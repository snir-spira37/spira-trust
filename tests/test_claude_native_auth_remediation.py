from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_auth_remediation as auth  # noqa: E402


def test_auth_error_observed_from_cli_message():
    result = auth.ClaudeRunResult(
        stdout=b'{"result":"Not logged in \\u00b7 Please run /login"}',
        stderr=b"",
        returncode=1,
        session_id="s",
    )

    assert auth.auth_error_observed(result, auth.parse_json(result.stdout))


def test_finalize_success_status_for_clean_smoke():
    results = auth.finalize(
        "2026-01-01T00:00:00Z",
        {},
        [],
        [],
        {"returncode": 0, "usage": {"input_total_available": True}},
    )

    assert results["terminal_status"] == "CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED"


def test_finalize_still_not_ready_status():
    results = auth.finalize(
        "2026-01-01T00:00:00Z",
        {},
        [],
        ["CLAUDE_NATIVE_AUTHENTICATION_STILL_NOT_READY"],
        {"returncode": 1},
    )

    assert results["terminal_status"] == "CLAUDE_NATIVE_AUTHENTICATION_STILL_NOT_READY"
