from __future__ import annotations

import asyncio
import json
import os
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

    provider = os.getenv("LLM_PROVIDER", "anthropic").strip().lower()
    model = os.getenv(
        "LLM_MODEL",
        "claude-sonnet-4-20250514" if provider == "anthropic" else "gpt-4o",
    ).strip()

    user_payload = _build_user_payload(source_code=source_code, errors=errors, generated_c=generated_c)

    raw_response = ""
    try:
        if provider == "openai":
            raw_response = await _call_openai(model=model, user_payload=user_payload)
        else:
            raw_response = await _call_anthropic(model=model, user_payload=user_payload)

        parsed = _parse_model_response(raw_response)
        normalized = _normalize_advice(parsed, raw_response=raw_response)
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
        line_text = lines[err.line - 1] if 1 <= err.line <= len(lines) else ""
        explanations.append(
            LLMErrorExplanation(
                error_id=f"E{idx}",
                explanation=(
                    f"Line {err.line} par issue hai: {err.message}. "
                    "Compiler ko yeh statement expected HingC syntax/type rules ke mutabik nahi mila."
                ),
                fix_suggestion=(
                    "Line ko language rules ke hisaab se rewrite karo, especially keyword order, "
                    "variable declaration/type, aur expression syntax check karo."
                ),
                fixed_code_snippet=line_text,
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


def advice_to_dict(advice: LLMAdvice) -> dict[str, Any]:
    return {
        "error_explanations": [asdict(item) for item in advice.error_explanations],
        "overall_summary": advice.overall_summary,
        "code_quality_tips": list(advice.code_quality_tips),
        "raw_response": advice.raw_response,
    }
