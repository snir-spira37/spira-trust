from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_deepseek_read_tool_diagnostic as diagnostic  # noqa: E402


def test_tool_call_extraction_nested_event():
    event = {"message": {"content": [{"type": "tool_use", "name": "Read"}]}}

    assert diagnostic.tool_calls_from_value(event) == {"Read"}


def test_permission_stderr_category():
    assert diagnostic.categorize_stderr(b"tool permission not allowed") == "TOOL_PERMISSION_ERROR"


def test_finalize_configuration_defect_when_some_tool_probe_works():
    results = diagnostic.finalize(
        "2026-01-01T00:00:00Z",
        [{"name": "read", "returncode": 0, "tool_calls_observed": ["Read"], "safe_stderr_category": "EMPTY", "workspace_mutated": False}],
        [],
        [],
    )

    assert results["terminal_status"] == "READ_TOOL_CONFIGURATION_DEFECT_FOUND"


def test_finalize_compatibility_not_ready_when_no_probe_works():
    results = diagnostic.finalize(
        "2026-01-01T00:00:00Z",
        [{"name": "read", "returncode": 1, "tool_calls_observed": [], "safe_stderr_category": "EMPTY", "workspace_mutated": False}],
        [],
        [],
    )

    assert results["terminal_status"] == "DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY"
