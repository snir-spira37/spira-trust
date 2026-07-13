from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_readiness as readiness  # noqa: E402


def test_strip_code_fence_json():
    assert readiness.strip_code_fence("```json\n{\"gate\":\"PROCEED\"}\n```") == '{"gate":"PROCEED"}'


def test_validate_output_schema_rejects_extra_property():
    schema = {
        "properties": {"gate": {"enum": ["PROCEED", "STOP"]}, "recommended_agent_action": {"enum": ["PROCEED"]}},
        "required": ["gate", "recommended_agent_action"],
    }

    errors = readiness.validate_output_schema({"gate": "PROCEED", "recommended_agent_action": "PROCEED", "extra": 1}, schema)

    assert any(error.startswith("ADDITIONAL_PROPERTIES") for error in errors)


def test_compare_to_expected_detects_false_proceed():
    expected = {
        "expected_action": {"recommended_agent_action": "STOP_BLOCKED", "stop": True},
        "expected_stop_state": True,
        "expected_reason_codes": ["X"],
        "expected_not_evaluated": [],
        "expected_blocking_list": [],
        "expected_not_claimed": [],
    }
    output = {
        "gate": "PROCEED",
        "recommended_agent_action": "PROCEED",
        "reason_codes": ["X"],
        "not_evaluated": [],
        "blocking_items": [],
        "not_claimed": [],
    }

    comparison = readiness.compare_to_expected(output, expected)

    assert not comparison["pass"]
    assert comparison["false_proceed"]


def test_readiness_inputs_are_nine():
    assert len(readiness.readiness_inputs()) == 9


def test_claude_transport_schema_removes_only_draft_uri():
    schema = {"$schema": "https://json-schema.org/draft/2020-12/schema", "type": "object", "required": ["gate"]}

    transported = readiness.claude_transport_schema(schema)

    assert "$schema" not in transported
    assert readiness.schema_transport_semantics_unchanged(schema, transported)
