from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_codex_native_readiness as readiness  # noqa: E402
import run_codex_native_readiness_reliability_diagnostic as diagnostic  # noqa: E402


def test_readiness_inputs_are_nine():
    assert len(readiness.readiness_inputs()) == 9


def test_codex_transport_schema_removes_provider_unsupported_keywords():
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "example",
        "type": "object",
        "properties": {
            "items": {
                "type": "array",
                "uniqueItems": True,
                "items": {"type": "string"},
            }
        },
    }

    transported = readiness.codex_transport_schema(schema)

    assert "$schema" not in transported
    assert "title" not in transported
    assert "uniqueItems" not in transported["properties"]["items"]
    assert transported["properties"]["items"]["items"] == {"type": "string"}


def test_extract_agent_output_from_codex_jsonl_events():
    events = [
        {"type": "thread.started", "thread_id": "t1"},
        {"type": "turn.started"},
        {"type": "item.completed", "item": {"type": "agent_message", "text": '{"gate":"PROCEED"}'}},
        {"type": "turn.completed", "usage": {"input_tokens": 1}},
    ]

    assert readiness.extract_agent_output(events) == {"gate": "PROCEED"}


def test_extract_usage_requires_turn_completed_usage():
    events = [
        {
            "type": "turn.completed",
            "usage": {
                "input_tokens": 10,
                "cached_input_tokens": 3,
                "output_tokens": 4,
                "reasoning_output_tokens": 2,
            },
        }
    ]

    usage = readiness.extract_usage(events)

    assert usage["input_tokens"] == 10
    assert usage["cached_input_tokens"] == 3
    assert usage["output_tokens"] == 4
    assert usage["reasoning_output_tokens"] == 2
    assert usage["input_total_available"]
    assert usage["usage_source"] == "turn.completed.usage"


def test_command_classification_allows_read_only_get_content():
    command = '"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe" -Command "Get-Content -Raw .\\frozen_input.json"'

    assert readiness.classify_command(command) == "READ_ONLY"


def test_command_classification_forbids_write_marker():
    command = 'powershell -Command "Set-Content -Path x -Value y"'

    assert readiness.classify_command(command) == "FORBIDDEN"


def test_readiness_errors_detect_usage_missing():
    session = {
        "ready": True,
        "comparison": {"false_proceed": False},
        "workspace_mutated": False,
        "forbidden_tool_count": 0,
        "usage": {"input_total_available": False},
        "result_envelope_present": True,
        "structured_output_present": True,
        "schema_valid": True,
    }

    assert "CODEX_NATIVE_READINESS_USAGE_NOT_AVAILABLE" in readiness.readiness_errors([session] * 9)


def test_arm_a_metadata_mismatch_is_not_readiness_revision_when_operationally_safe():
    arm_a = {
        "arm": "A",
        "ready": False,
        "comparison": {
            "false_proceed": False,
            "checks": {
                "gate": True,
                "recommended_agent_action": True,
                "reason_codes": False,
                "blocking_items": False,
            },
        },
        "workspace_mutated": False,
        "forbidden_tool_count": 0,
        "usage": {"input_total_available": True},
        "result_envelope_present": True,
        "structured_output_present": True,
        "schema_valid": True,
    }
    arm_b = {**arm_a, "arm": "B", "ready": True, "comparison": {"false_proceed": False, "checks": {}, "pass": True}}
    arm_c = {**arm_b, "arm": "C"}

    assert "CODEX_NATIVE_READINESS_NEEDS_REVISION" not in readiness.readiness_errors([arm_a] * 3 + [arm_b] * 3 + [arm_c] * 3)


def test_diagnostic_enriches_missing_contract_metadata():
    expected = {
        "expected_reason_codes": ["TESTS_PASSED"],
        "expected_not_claimed": ["producer_correctness", "software_safety"],
    }
    session = {
        "agent_output": {
            "reason_codes": [],
            "not_claimed": [],
        },
        "comparison": {
            "pass": False,
            "checks": {
                "recommended_agent_action": True,
                "gate": True,
                "blocking_items": True,
                "not_evaluated": True,
            },
        },
        "result_envelope_present": True,
        "structured_output_present": True,
        "usage": {"input_total_available": True},
    }

    enriched = diagnostic.enrich_diagnostic_session(session, expected)

    assert enriched["missing_reason_codes"] == ["TESTS_PASSED"]
    assert enriched["missing_not_claimed"] == ["producer_correctness", "software_safety"]
    assert enriched["action_preserved"]
    assert enriched["stop_state_preserved"]
