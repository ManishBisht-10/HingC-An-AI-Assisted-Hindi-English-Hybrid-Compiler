import asyncio

from hingc.api.llm_advisor import (
    HINGC_ADVISOR_SYSTEM_PROMPT,
    _build_user_payload,
    _parse_model_response,
    advice_to_dict,
    explain_errors,
)
from hingc.compiler.errors import ParseError, SemanticError
from hingc.compiler.errors import LexerError


def test_system_prompt_contains_required_roles():
    assert "HingC Advisor" in HINGC_ADVISOR_SYSTEM_PROMPT
    assert "simple Hinglish" in HINGC_ADVISOR_SYSTEM_PROMPT
    assert "corrected HingC code" in HINGC_ADVISOR_SYSTEM_PROMPT


def test_user_payload_contains_structured_errors():
    err = ParseError("Expected expression", line=3, column=8)
    payload = _build_user_payload(source_code="shuru\nabc\nkhatam\n", errors=[err], generated_c=None)

    assert '"error_id": "E1"' in payload
    assert '"phase": "parser"' in payload
    assert '"line": 3' in payload


def test_parse_model_response_extracts_embedded_json():
    raw = "Some text\n```json\n{\"overall_summary\":\"ok\",\"code_quality_tips\":[]}\n```"
    parsed = _parse_model_response(raw)
    assert parsed["overall_summary"] == "ok"


def test_explain_errors_fallback_without_keys(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    err = ParseError("Expected expression", line=2, column=1)
    advice = asyncio.run(explain_errors("shuru\n@\nkhatam\n", [err], None))

    data = advice_to_dict(advice)
    assert data["overall_summary"]
    assert len(data["error_explanations"]) == 1
    assert data["error_explanations"][0]["error_id"] == "E1"


def test_explain_errors_uses_ollama_provider(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLAMA_API_URL", "http://localhost:11434")
    monkeypatch.setenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0")

    def fake_urlopen_json(req):
        assert req.full_url.endswith("/api/chat")
        return {
            "message": {
                "content": (
                    '{"error_explanations":[{"error_id":"E1","explanation":"x","fix_suggestion":"y",'
                    '"fixed_code_snippet":"z"}],"overall_summary":"ok","code_quality_tips":["tip"]}'
                )
            }
        }

    monkeypatch.setattr("hingc.api.llm_advisor._urlopen_json", fake_urlopen_json)

    err = ParseError("Expected expression", line=2, column=1)
    advice = asyncio.run(explain_errors("shuru\n@\nkhatam\n", [err], None))
    data = advice_to_dict(advice)

    assert data["overall_summary"] == "ok"
    assert len(data["error_explanations"]) == 1
    assert data["code_quality_tips"] == ["tip"]


def test_fallback_advice_generates_distinct_targeted_fixes(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    errs = [
        SemanticError("Undeclared variable 'x'", line=2, column=1),
        SemanticError("Break (toro) used outside of a loop", line=3, column=1),
    ]

    code = "shuru\nx = 5\ntoro\nkhatam\n"
    advice = asyncio.run(explain_errors(code, errs, None))
    data = advice_to_dict(advice)

    assert len(data["error_explanations"]) == 2
    first = data["error_explanations"][0]
    second = data["error_explanations"][1]

    assert "declare" in first["fix_suggestion"].lower()
    assert "loop" in second["fix_suggestion"].lower()
    assert first["fixed_code_snippet"] != second["fixed_code_snippet"]


def test_fallback_does_not_echo_same_broken_line(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    broken = "@"
    err = ParseError("Expected expression", line=2, column=1)
    advice = asyncio.run(explain_errors(f"shuru\n{broken}\nkhatam\n", [err], None))
    data = advice_to_dict(advice)

    fixed = data["error_explanations"][0]["fixed_code_snippet"].strip()
    assert fixed
    assert fixed != broken


def test_model_output_is_postprocessed_when_fix_is_generic(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLAMA_API_URL", "http://localhost:11434")
    monkeypatch.setenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0")

    def fake_urlopen_json(req):
        assert req.full_url.endswith("/api/chat")
        return {
            "message": {
                "content": (
                    '{"error_explanations":[{"error_id":"E1","explanation":"x","'
                    'fix_suggestion":"Is line ko error message ke according exact syntax/type rule follow karte hue rewrite karo.",'
                    '"fixed_code_snippet":"@"}],"overall_summary":"ok","code_quality_tips":[]}'
                )
            }
        }

    monkeypatch.setattr("hingc.api.llm_advisor._urlopen_json", fake_urlopen_json)

    err = ParseError("Expected expression", line=2, column=1)
    advice = asyncio.run(explain_errors("shuru\n@\nkhatam\n", [err], None))
    data = advice_to_dict(advice)
    item = data["error_explanations"][0]

    assert item["fixed_code_snippet"] != "@"
    assert "rewrite" not in item["fix_suggestion"].lower()


def test_model_output_with_symbol_only_fix_is_replaced(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLAMA_API_URL", "http://localhost:11434")
    monkeypatch.setenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0")

    def fake_urlopen_json(req):
        assert req.full_url.endswith("/api/chat")
        return {
            "message": {
                "content": (
                    '{"error_explanations":[{"error_id":"E1","explanation":"x","'
                    'fix_suggestion":"rewrite this line",'
                    '"fixed_code_snippet":"@"}],"overall_summary":"ok","code_quality_tips":[]}'
                )
            }
        }

    monkeypatch.setattr("hingc.api.llm_advisor._urlopen_json", fake_urlopen_json)

    err = ParseError("Expected expression", line=2, column=1)
    advice = asyncio.run(explain_errors("shuru\n@\nkhatam\n", [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert item["fixed_code_snippet"] != "@"
    assert item["fixed_code_snippet"].strip()


def test_invalid_character_gets_specific_targeted_fix(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    monkeypatch.setenv("LLAMA_API_URL", "http://localhost:11434")
    monkeypatch.setenv("LLM_MODEL", "llama3.1:8b-instruct-q8_0")

    def fake_urlopen_json(req):
        assert req.full_url.endswith("/api/chat")
        return {
            "message": {
                "content": (
                    '{"error_explanations":[{"error_id":"E1","explanation":"x","'
                    'fix_suggestion":"rewrite this line",'
                    '"fixed_code_snippet":"@"}],"overall_summary":"ok","code_quality_tips":[]}'
                )
            }
        }

    monkeypatch.setattr("hingc.api.llm_advisor._urlopen_json", fake_urlopen_json)

    err = LexerError("Invalid character: '@'", line=2, column=1)
    advice = asyncio.run(explain_errors("shuru\n@\nkhatam\n", [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert "invalid" in item["fix_suggestion"].lower() or "symbol" in item["fix_suggestion"].lower()
    assert item["fixed_code_snippet"] == "(remove this line)"


def test_expected_rparen_fix_uses_incorrect_line_context(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\nagar (x > 0 {\nlikho(\"x\")\n}\nkhatam\n"
    err = ParseError("Expected token RPAREN, got LBRACE('{')", line=2, column=13)
    advice = asyncio.run(explain_errors(src, [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert item["fixed_code_snippet"] == "agar (x > 0 ) {"


def test_expected_lparen_fix_wraps_arguments(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\nlikho \"x\"\nkhatam\n"
    err = ParseError("Expected token LPAREN, got STRING_LITERAL('x')", line=2, column=7)
    advice = asyncio.run(explain_errors(src, [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert item["fixed_code_snippet"] == 'likho("x")'


def test_lexer_invalid_character_inside_line_is_removed(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\nrakho poora @x = 1\nkhatam\n"
    err = LexerError("Invalid character: '@'", line=2, column=13)
    advice = asyncio.run(explain_errors(src, [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert item["fixed_code_snippet"] == "rakho poora x = 1"


def test_unexpected_rbrace_gets_remove_line_fix(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\n}\nkhatam\n"
    err = ParseError("Unexpected token RBRACE('}') in statement", line=2, column=1)
    advice = asyncio.run(explain_errors(src, [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert item["fixed_code_snippet"] == "(remove this line)"


def test_invalid_character_only_line_gets_remove_line_fix(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\n@\nkhatam\n"
    err = LexerError("Invalid character: '@'", line=2, column=1)
    advice = asyncio.run(explain_errors(src, [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert item["fixed_code_snippet"] == "(remove this line)"


def test_fix_suggestion_contains_line_specific_custom_fix(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\nlikho \"x\"\nkhatam\n"
    err = ParseError("Expected token LPAREN, got STRING_LITERAL('x')", line=2, column=7)
    advice = asyncio.run(explain_errors(src, [err], None))
    item = advice_to_dict(advice)["error_explanations"][0]

    assert "custom fix for line 2" in item["fix_suggestion"].lower()
    assert 'likho("x")' in item["fix_suggestion"]


def test_multi_semantic_errors_get_individual_line_specific_advice(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.setenv("LLM_PROVIDER", "anthropic")

    src = "shuru\nx = 5\ntoro\nrakho poora y = \"hi\"\nkhatam\n"
    errs = [
        SemanticError("Undeclared variable 'x'", line=1, column=1),
        SemanticError("Break (toro) used outside of a loop", line=1, column=1),
        SemanticError("Type mismatch: cannot assign shabd to poora variable 'y'", line=1, column=1),
    ]

    advice = asyncio.run(explain_errors(src, errs, None))
    items = advice_to_dict(advice)["error_explanations"]

    assert len(items) == 3
    assert "custom fix for line 2" in items[0]["fix_suggestion"].lower()
    assert "custom fix for line 3" in items[1]["fix_suggestion"].lower()
    assert "custom fix for line 4" in items[2]["fix_suggestion"].lower()
