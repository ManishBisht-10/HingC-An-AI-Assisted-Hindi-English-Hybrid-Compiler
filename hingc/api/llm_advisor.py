from __future__ import annotations

import asyncio
import json
import os
import re
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Any, Iterable, Optional

from hingc.compiler.errors import CompilerError

HINGC_ADVISOR_SYSTEM_PROMPT = (
    "You are HingC Advisor - an expert in the HingC Hinglish programming language.\n"
    "A student wrote HingC code and got compiler errors. Your job is to:\n"
    "1. Explain each error in simple Hinglish (mix of Hindi and English), as if teaching a beginner.\n"
    "2. Show the exact incorrect line.\n"
    "3. Show the corrected HingC code for each error.\n"
    "4. Give an overall summary of what went wrong.\n"
    "5. If the code compiled successfully, review the generated C code and suggest any improvements.\n"
    "Be friendly, encouraging, and educational. Use a conversational tone."
)


@dataclass(frozen=True, slots=True)
class LLMErrorExplanation:
    error_id: str
    explanation: str
    fix_suggestion: str
    fixed_code_snippet: str


@dataclass(frozen=True, slots=True)
class LLMAdvice:
    error_explanations: list[LLMErrorExplanation] = field(default_factory=list)
    overall_summary: str = ""
    code_quality_tips: list[str] = field(default_factory=list)
    raw_response: str = ""


async def explain_errors(
    source_code: str,
    errors: list[CompilerError],
    generated_c: Optional[str],
) -> LLMAdvice:
    """
    Generate educational diagnostics for HingC compile results.

    This function is resilient by design: if no provider key is configured,
    if the network call fails, or if model output is malformed, it returns
    deterministic fallback advice built from compiler errors.
    """

    provider = os.getenv("LLM_PROVIDER", "ollama").strip().lower()
    default_model_by_provider = {
        "anthropic": "claude-sonnet-4-20250514",
        "openai": "gpt-4o",
        "ollama": "llama3.1:8b-instruct-q8_0",
        "llama": "llama3.1:8b-instruct-q8_0",
    }
    model = os.getenv("LLM_MODEL", default_model_by_provider.get(provider, "llama3.1:8b-instruct-q8_0")).strip()

    user_payload = _build_user_payload(source_code=source_code, errors=errors, generated_c=generated_c)

    raw_response = ""
    try:
        if provider == "openai":
            raw_response = await _call_openai(model=model, user_payload=user_payload)
        elif provider in {"ollama", "llama"}:
            raw_response = await _call_ollama(model=model, user_payload=user_payload)
        else:
            raw_response = await _call_anthropic(model=model, user_payload=user_payload)

        parsed = _parse_model_response(raw_response)
        normalized = _normalize_advice(parsed, raw_response=raw_response)
        normalized = _postprocess_advice(source_code=source_code, errors=errors, advice=normalized)
        if normalized.error_explanations or normalized.overall_summary or normalized.code_quality_tips:
            return normalized
    except Exception:
        # Fallback below; callers still get usable guidance even on API failures.
        pass

    return _fallback_advice(source_code=source_code, errors=errors, generated_c=generated_c, raw_response=raw_response)


def _build_user_payload(source_code: str, errors: list[CompilerError], generated_c: Optional[str]) -> str:
    structured_errors = _serialize_errors(errors)
    payload = {
        "source_code": source_code,
        "errors": structured_errors,
        "generated_c": generated_c,
        "instructions": (
            "Return JSON only with keys: error_explanations, overall_summary, code_quality_tips. "
            "error_explanations must be a list of objects with keys: "
            "error_id, explanation, fix_suggestion, fixed_code_snippet."
        ),
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def _serialize_errors(errors: Iterable[CompilerError]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for idx, err in enumerate(errors, start=1):
        result.append(
            {
                "error_id": f"E{idx}",
                "phase": err.phase,
                "line": err.line,
                "column": err.column,
                "message": err.message,
            }
        )
    return result


async def _call_anthropic(model: str, user_payload: str) -> str:
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not configured")

    body = {
        "model": model,
        "max_tokens": 1600,
        "temperature": 0.2,
        "system": HINGC_ADVISOR_SYSTEM_PROMPT,
        "messages": [
            {
                "role": "user",
                "content": user_payload,
            }
        ],
    }
    req = urllib.request.Request(
        url="https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    response_data = await asyncio.to_thread(_urlopen_json, req)
    parts = response_data.get("content") or []
    text_chunks = [part.get("text", "") for part in parts if isinstance(part, dict)]
    return "\n".join(chunk for chunk in text_chunks if chunk).strip()


async def _call_openai(model: str, user_payload: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    body = {
        "model": model,
        "temperature": 0.2,
        "response_format": {"type": "json_object"},
        "messages": [
            {"role": "system", "content": HINGC_ADVISOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_payload},
        ],
    }
    req = urllib.request.Request(
        url="https://api.openai.com/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "content-type": "application/json",
        },
        method="POST",
    )

    response_data = await asyncio.to_thread(_urlopen_json, req)
    choices = response_data.get("choices") or []
    if not choices:
        return ""
    msg = choices[0].get("message") or {}
    return str(msg.get("content") or "").strip()


async def _call_ollama(model: str, user_payload: str) -> str:
    base_url = os.getenv("LLAMA_API_URL", os.getenv("OLLAMA_API_URL", "http://localhost:11434")).strip()
    if not base_url:
        raise RuntimeError("LLAMA_API_URL/OLLAMA_API_URL is not configured")

    endpoint = f"{base_url.rstrip('/')}/api/chat"
    body = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {
            "temperature": 0.2,
        },
        "messages": [
            {"role": "system", "content": HINGC_ADVISOR_SYSTEM_PROMPT},
            {"role": "user", "content": user_payload},
        ],
    }

    req = urllib.request.Request(
        url=endpoint,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "content-type": "application/json",
        },
        method="POST",
    )

    response_data = await asyncio.to_thread(_urlopen_json, req)
    msg = response_data.get("message") or {}
    return str(msg.get("content") or "").strip()


def _urlopen_json(req: urllib.request.Request) -> dict[str, Any]:
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        detail = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"LLM HTTP error {e.code}: {detail}") from e


def _parse_model_response(raw_response: str) -> dict[str, Any]:
    if not raw_response.strip():
        return {}

    # Try strict JSON first.
    try:
        parsed = json.loads(raw_response)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    # Try extracting JSON object from markdown blocks or mixed text.
    start = raw_response.find("{")
    end = raw_response.rfind("}")
    if start != -1 and end != -1 and end > start:
        snippet = raw_response[start : end + 1]
        try:
            parsed = json.loads(snippet)
            if isinstance(parsed, dict):
                return parsed
        except json.JSONDecodeError:
            return {}
    return {}


def _normalize_advice(parsed: dict[str, Any], raw_response: str) -> LLMAdvice:
    exps: list[LLMErrorExplanation] = []
    for item in parsed.get("error_explanations") or []:
        if not isinstance(item, dict):
            continue
        exps.append(
            LLMErrorExplanation(
                error_id=str(item.get("error_id") or ""),
                explanation=str(item.get("explanation") or ""),
                fix_suggestion=str(item.get("fix_suggestion") or ""),
                fixed_code_snippet=str(item.get("fixed_code_snippet") or ""),
            )
        )

    tips_raw = parsed.get("code_quality_tips") or []
    tips = [str(tip) for tip in tips_raw if str(tip).strip()]

    return LLMAdvice(
        error_explanations=exps,
        overall_summary=str(parsed.get("overall_summary") or "").strip(),
        code_quality_tips=tips,
        raw_response=raw_response,
    )


def _fallback_advice(
    source_code: str,
    errors: list[CompilerError],
    generated_c: Optional[str],
    raw_response: str,
) -> LLMAdvice:
    lines = source_code.splitlines()
    explanations: list[LLMErrorExplanation] = []

    for idx, err in enumerate(errors, start=1):
        resolved_line, line_text = _resolve_error_line_and_text(lines=lines, err=err)
        explanation, fix_suggestion, fixed_code = _build_targeted_fallback(
            err=err,
            line_text=line_text,
            line_no=resolved_line,
        )
        fixed_code = _ensure_distinct_fix(original_line=line_text, proposed_fixed_line=fixed_code)
        explanations.append(
            LLMErrorExplanation(
                error_id=f"E{idx}",
                explanation=explanation,
                fix_suggestion=_compose_detailed_fix_advice(base_advice=fix_suggestion, line_no=resolved_line, fixed_line=fixed_code),
                fixed_code_snippet=fixed_code,
            )
        )

    if errors:
        overall = (
            "Code compile nahi hua kyunki syntax/semantic errors aaye. "
            "Pehle listed lines ko fix karke dubara compile karo."
        )
    else:
        overall = "Code successfully compile hua. Output aur generated C dono sahi direction me hain."

    tips: list[str] = []
    if generated_c:
        tips.extend(
            [
                "Generated C me consistent indentation rakho taaki debugging easy ho.",
                "User input handle karte time scanf return value check karna safe hota hai.",
            ]
        )

    return LLMAdvice(
        error_explanations=explanations,
        overall_summary=overall,
        code_quality_tips=tips,
        raw_response=raw_response,
    )


def _build_targeted_fallback(err: CompilerError, line_text: str, line_no: int | None = None) -> tuple[str, str, str]:
    msg = err.message
    msg_lower = msg.lower()
    clean_line = line_text.strip()
    line_col = getattr(err, "column", 1)
    display_line = line_no or err.line

    # semantic: undeclared variable
    invalid_char = re.search(r"Invalid character: '([^']+)'", msg)
    if invalid_char:
        ch = invalid_char.group(1)
        fixed_line = line_text.replace(ch, "").strip()
        if not fixed_line:
            fixed_line = "(remove this line)"
        return (
            f"Line {display_line} par invalid character '{ch}' mila, jo HingC syntax ka part nahi hai.",
            "Invalid symbol hatao aur valid HingC statement likho.",
            fixed_line,
        )

    expected_token = re.search(r"Expected token ([A-Z_]+), got ([A-Z_]+)\((.+)\)", msg)
    if expected_token:
        expected, got, _ = expected_token.groups()
        fixed_line = _fix_expected_token_line(clean_line, expected, got, line_col)
        return (
            f"Line {display_line} par parser ko token {expected} chahiye tha, lekin {got} mila.",
            f"Syntax ko adjust karke missing token {expected} add karo ya current token order sahi karo.",
            fixed_line,
        )

    expected_keyword = re.search(r"Expected keyword '([^']+)'", msg)
    if expected_keyword:
        kw = expected_keyword.group(1)
        return (
            f"Line {display_line} par required keyword '{kw}' missing hai.",
            f"Program structure complete karne ke liye '{kw}' add karo.",
            kw,
        )

    if "unexpected token rbrace" in msg_lower and "in statement" in msg_lower:
        return (
            f"Line {display_line} par extra '}}' mila jo yahan valid statement nahi hai.",
            "Agar block yahin close nahi ho raha to extra '}' hatao.",
            "(remove this line)",
        )

    if "expected 'sthiti' or 'warna_default' in switch" in msg_lower:
        fixed = _fix_switch_case_line(clean_line)
        return (
            f"Line {display_line} par switch ke andar 'sthiti' ya 'warna_default' expected tha.",
            "Switch branch ko 'sthiti <value>:' ya 'warna_default:' format me likho.",
            fixed,
        )

    # semantic: undeclared variable
    undeclared = re.search(r"Undeclared variable '([^']+)'", msg)
    if undeclared:
        name = undeclared.group(1)
        return (
            f"Line {display_line} par variable '{name}' use ho raha hai, lekin pehle declare nahi hua.",
            "Use se pehle variable declare karo. Quick fix: declaration line add karo aur phir assignment/use rakho.",
            f"rakho poora {name} = 0",
        )

    # semantic: type mismatch on assignment
    mismatch = re.search(r"Type mismatch: cannot assign ([^ ]+) to ([^ ]+) variable '([^']+)'", msg)
    if mismatch:
        source_t, target_t, name = mismatch.groups()
        return (
            f"Line {display_line} par type mismatch hai: value type {source_t} hai, variable '{name}' ka type {target_t} hai.",
            "Variable type aur assigned value type same rakho. Ya to declaration ka type badlo, ya compatible value do.",
            _type_mismatch_fix_line(target_type=target_t, source_type=source_t, var_name=name, current_line=clean_line),
        )

    # semantic: loop-control misuse
    if "break (toro) used outside of a loop" in msg_lower:
        return (
            f"Line {display_line} par 'toro' sirf loop ke andar valid hota hai.",
            "'toro' hatao ya is statement ko 'jabtak'/'karo' loop ke andar move karo.",
            "jabtak (1) {\n  toro\n}",
        )
    if "continue (agla) used outside of a loop" in msg_lower:
        return (
            f"Line {display_line} par 'agla' sirf loop ke andar valid hota hai.",
            "'agla' hatao ya is statement ko loop body ke andar rakho.",
            "jabtak (1) {\n  agla\n}",
        )

    # semantic: function issues
    undefined_fn = re.search(r"Call to undefined function '([^']+)'", msg)
    if undefined_fn:
        fn = undefined_fn.group(1)
        return (
            f"Function '{fn}' ko call kiya gaya hai, lekin uska declaration/definition nahi mila.",
            "Function ko pehle define karo, ya call name ko existing function name se match karo.",
            f"kaam poora {fn}() {{\n  wapas 0\n}}",
        )

    wrong_args = re.search(r"Function '([^']+)' called with wrong number of arguments", msg)
    if wrong_args:
        fn = wrong_args.group(1)
        return (
            f"Function '{fn}' ko galat number of arguments ke saath call kiya gaya hai.",
            "Call site par argument count function declaration ke equal rakho.",
            f"{fn}(/* required args here */)",
        )

    # parser-style errors
    if "expected expression" in msg_lower:
        if re.fullmatch(r"[@#$%^&*]+", clean_line):
            fixed_line = "rakho poora x = 1"
        elif re.search(r"[+\-*/%><=!&|]\s*\)", clean_line):
            # Common beginner typo: incomplete condition like agar (x >) {
            fixed_line = re.sub(r"([+\-*/%><=!&|])\s*\)", r"\1 0)", clean_line)
        elif clean_line.endswith(("+", "-", "*", "/", "%", ">", "<", "==", "!=", "&&", "||")):
            fixed_line = f"{clean_line} 1"
        else:
            fixed_line = "rakho poora x = 1"
        return (
            f"Line {display_line} par expression incomplete hai ya missing hai.",
            "Operator ke dono side valid expression do, ya incomplete token hatao.",
            fixed_line,
        )

    if "division by zero" in msg_lower:
        return (
            f"Line {display_line} par denominator zero hai, isliye runtime/semantic error aayega.",
            "Division se pehle denominator ko zero-check karo.",
            "agar (b != 0) {\n  rakho poora ans = a / b\n}",
        )

    # default fallback for uncommon errors
    return (
        f"Line {display_line} par issue hai: {msg}",
        "Is line ko error message ke according exact syntax/type rule follow karte hue rewrite karo.",
        _generic_line_repair(clean_line, line_col),
    )


def _fix_expected_token_line(clean_line: str, expected: str, got: str, column: int) -> str:
    if not clean_line:
        return "rakho poora temp = 0"

    if expected == "RPAREN":
        if "{" in clean_line and ")" not in clean_line:
            return clean_line.replace("{", ") {", 1).replace(")  {", ") {", 1)
        if "(" in clean_line and ")" not in clean_line:
            return f"{clean_line})"
        return _insert_at_col(clean_line, column, ")")

    if expected == "LPAREN":
        m = re.match(r"^(\s*(?:agar|jabtak|likho|lo|chunao|karo)\b)\s+(.+)$", clean_line)
        if m:
            return f"{m.group(1)}({m.group(2)})"
        return _insert_at_col(clean_line, column, "(")

    if expected == "SEMICOLON":
        return _insert_at_col(clean_line, column, " ; ")

    if expected == "LBRACE":
        return f"{clean_line} {{"

    if expected == "RBRACE":
        return "}"

    if expected == "ASSIGN":
        m = re.match(r"^(\s*[A-Za-z_][A-Za-z0-9_]*)\s+(.+)$", clean_line)
        if m:
            return f"{m.group(1)} = {m.group(2)}"
        return _insert_at_col(clean_line, column, " = ")

    if expected == "COLON":
        return f"{clean_line}:"

    if expected == "COMMA":
        return _insert_at_col(clean_line, column, ", ")

    if expected == "KEYWORD":
        if clean_line.strip().startswith("kaam "):
            # kaam xyz f(...) -> kaam poora f(...)
            return re.sub(r"^(\s*kaam\s+)\w+", r"\1poora", clean_line, count=1)
        return _insert_at_col(clean_line, column, "poora ")

    if expected == "IDENTIFIER":
        return _insert_at_col(clean_line, column, "x")

    return _generic_line_repair(clean_line, column)


def _fix_switch_case_line(clean_line: str) -> str:
    # foo 1: ... -> sthiti 1: ...
    m = re.match(r"^(\s*)\w+\s+(.+)$", clean_line)
    if m and ":" in clean_line:
        return f"{m.group(1)}sthiti {m.group(2)}"
    if clean_line:
        return "sthiti 1: "
    return "sthiti 1:"


def _generic_line_repair(clean_line: str, column: int) -> str:
    if not clean_line:
        return "rakho poora temp = 0"

    if clean_line.endswith("="):
        return f"{clean_line} 0"

    if re.search(r"[+\-*/%><=!&|]\s*\)", clean_line):
        return re.sub(r"([+\-*/%><=!&|])\s*\)", r"\1 0)", clean_line)

    if clean_line.endswith(("+", "-", "*", "/", "%", ">", "<", "==", "!=", "&&", "||")):
        return f"{clean_line} 0"

    return _insert_at_col(clean_line, column, " 0")


def _insert_at_col(line: str, column: int, text: str) -> str:
    idx = max(0, min(len(line), int(column) - 1))
    return f"{line[:idx]}{text}{line[idx:]}"


def _type_mismatch_fix_line(target_type: str, source_type: str, var_name: str, current_line: str) -> str:
    # String assigned to int/float style mismatch is common for beginners.
    if source_type == "shabd" and target_type in {"poora", "dasha"}:
        return f"rakho shabd {var_name} = \"text\""
    if source_type in {"poora", "dasha"} and target_type == "shabd":
        return f"rakho shabd {var_name} = \"123\""

    if current_line:
        return current_line
    return f"rakho {target_type} {var_name} = /* compatible value */"


def _ensure_distinct_fix(original_line: str, proposed_fixed_line: str) -> str:
    original = original_line.strip()
    proposed = proposed_fixed_line.strip()
    if proposed and proposed != original:
        return proposed_fixed_line

    if not original:
        return "rakho poora temp = 0"

    # Last-resort safe fallback that differs from the original broken line.
    return "rakho poora temp = 0"


def advice_to_dict(advice: LLMAdvice) -> dict[str, Any]:
    return {
        "error_explanations": [asdict(item) for item in advice.error_explanations],
        "overall_summary": advice.overall_summary,
        "code_quality_tips": list(advice.code_quality_tips),
        "raw_response": advice.raw_response,
    }


def _postprocess_advice(source_code: str, errors: list[CompilerError], advice: LLMAdvice) -> LLMAdvice:
    if not errors:
        return advice

    lines = source_code.splitlines()
    by_id = {item.error_id: item for item in advice.error_explanations}
    improved: list[LLMErrorExplanation] = []

    for idx, err in enumerate(errors, start=1):
        error_id = f"E{idx}"
        existing = by_id.get(error_id)
        if existing is None and idx - 1 < len(advice.error_explanations):
            existing = advice.error_explanations[idx - 1]

        resolved_line, line_text = _resolve_error_line_and_text(lines=lines, err=err)
        fallback_expl, fallback_fix, fallback_code = _build_targeted_fallback(
            err=err,
            line_text=line_text,
            line_no=resolved_line,
        )
        fallback_code = _ensure_distinct_fix(original_line=line_text, proposed_fixed_line=fallback_code)

        if existing is None:
            improved.append(
                LLMErrorExplanation(
                    error_id=error_id,
                    explanation=fallback_expl,
                    fix_suggestion=_compose_detailed_fix_advice(base_advice=fallback_fix, line_no=resolved_line, fixed_line=fallback_code),
                    fixed_code_snippet=fallback_code,
                )
            )
            continue

        explanation = existing.explanation.strip() or fallback_expl
        # Use deterministic compiler-rule-based fix output for reliability.
        fix_suggestion = _compose_detailed_fix_advice(base_advice=fallback_fix, line_no=err.line, fixed_line=fallback_code)
        fixed_code = fallback_code

        improved.append(
            LLMErrorExplanation(
                error_id=error_id,
                explanation=explanation,
                fix_suggestion=fix_suggestion,
                fixed_code_snippet=fixed_code,
            )
        )

    return LLMAdvice(
        error_explanations=improved,
        overall_summary=advice.overall_summary,
        code_quality_tips=advice.code_quality_tips,
        raw_response=advice.raw_response,
    )


def _is_generic_fix_suggestion(text: str) -> bool:
    lowered = text.strip().lower()
    if not lowered:
        return True

    generic_markers = [
        "rewrite",
        "according to error message",
        "error message ke according",
        "language rules",
        "syntax/type rule",
        "check syntax",
    ]
    return any(marker in lowered for marker in generic_markers)


def _looks_invalid_fix_line(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return True
    # Single token made of punctuation/symbols is not a useful fixed code snippet.
    if re.fullmatch(r"[^\w\s]+", stripped):
        return True
    return False


def _compose_detailed_fix_advice(base_advice: str, line_no: int, fixed_line: str) -> str:
    snippet = fixed_line.strip() or "(remove this line)"
    return (
        f"{base_advice} "
        f"Custom fix for line {line_no}: {snippet}"
    )


def _resolve_error_line_and_text(lines: list[str], err: CompilerError) -> tuple[int, str]:
    # If compiler already has a strong line reference, trust it.
    if 1 <= err.line <= len(lines) and err.line != 1:
        return err.line, lines[err.line - 1]

    msg = err.message

    # Semantic errors in this codebase frequently carry line=1; infer likely line.
    var_match = re.search(r"variable '([^']+)'", msg)
    if var_match:
        name = var_match.group(1)
        for idx, line in enumerate(lines, start=1):
            if re.search(rf"\b{re.escape(name)}\b", line):
                if "Undeclared variable" in msg and re.search(rf"\brakho\b.*\b{re.escape(name)}\b", line):
                    continue
                return idx, line

    if "Break (toro)" in msg:
        for idx, line in enumerate(lines, start=1):
            if "toro" in line:
                return idx, line

    if "Continue (agla)" in msg:
        for idx, line in enumerate(lines, start=1):
            if "agla" in line:
                return idx, line

    invalid_char = re.search(r"Invalid character: '([^']+)'", msg)
    if invalid_char:
        ch = invalid_char.group(1)
        for idx, line in enumerate(lines, start=1):
            if ch in line:
                return idx, line

    if 1 <= err.line <= len(lines):
        return err.line, lines[err.line - 1]

    return 1, lines[0] if lines else ""
