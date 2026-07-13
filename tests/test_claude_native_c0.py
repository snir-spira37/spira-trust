from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_c0 as c0  # noqa: E402


def test_terminal_pass_requires_all_core_probes_ready():
    probes = {
        "C0-P1": {"ready": True},
        "C0-P2": {"ready": True},
        "C0-P3": {"ready": True},
        "C0-P4": {"ready": True},
        "C0-P5": {"ready": True},
        "C0-P7": {"ready": True},
        "session_isolation_summary": {"ready": True},
    }

    assert c0.terminal_status([], probes) == "CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS"


def test_authentication_error_maps_to_model_identity_gate():
    assert c0.terminal_status(["CLAUDE_NATIVE_AUTHENTICATION_NOT_READY"], {}) == "CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED"


def test_tool_call_extraction_finds_nested_read_call():
    event = {"message": {"content": [{"type": "tool_use", "name": "Read"}]}}

    assert c0.tool_calls_from_value(event) == {"Read"}


def test_forbidden_tools_match_lowercase_and_mcp_prefix():
    assert c0.forbidden_tools_present(["Read", "Bash", "mcp__server__tool"]) == {"Bash", "mcp__server__tool"}


def test_auth_error_observed_from_json_result():
    result = c0.ClaudeRunResult(
        stdout=b'{"result":"Not logged in \\u00b7 Please run /login"}',
        stderr=b"",
        returncode=1,
        session_id="s",
    )
    parsed = c0.parse_json_bytes(result.stdout)

    assert c0.auth_error_observed(result, parsed)


def test_claude_native_model_identity_rule_accepts_haiku_without_reported_model_when_usage_available():
    result = c0.ClaudeRunResult(stdout=b'{"result":"ok"}', stderr=b"", returncode=0, session_id="s")

    rule = c0.claude_native_model_identity_rule(
        result=result,
        parsed=c0.parse_json_bytes(result.stdout),
        reported_model=None,
        usage={"input_total_available": True},
    )

    assert rule["ready"]


def test_claude_native_model_identity_rule_rejects_contradicting_reported_model():
    result = c0.ClaudeRunResult(stdout=b'{"result":"ok"}', stderr=b"", returncode=0, session_id="s")

    rule = c0.claude_native_model_identity_rule(
        result=result,
        parsed=c0.parse_json_bytes(result.stdout),
        reported_model="deepseek-v4-pro",
        usage={"input_total_available": True},
    )

    assert not rule["ready"]
    assert rule["reported_model_contradicts_request"]


def test_forbidden_tool_denial_summary_treats_not_enabled_result_as_denied():
    events = [
        {"message": {"content": [{"type": "tool_use", "name": "Write"}]}},
        {
            "message": {
                "content": [
                    {
                        "type": "tool_result",
                        "is_error": True,
                        "content": "No such tool available: Write. Write exists but is not enabled in this context.",
                    }
                ]
            }
        },
    ]

    summary = c0.forbidden_tool_denial_summary(events)

    assert summary["forbidden_tool_attempt_count"] == 1
    assert summary["denied_forbidden_tool_attempt_count"] == 1
    assert summary["executed_forbidden_tool_count"] == 0
