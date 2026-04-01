import asyncio

from hingc.api.llm_advisor import (
    HINGC_ADVISOR_SYSTEM_PROMPT,
    _build_user_payload,
    _parse_model_response,
    advice_to_dict,
    explain_errors,
)
from hingc.compiler.errors import ParseError


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
