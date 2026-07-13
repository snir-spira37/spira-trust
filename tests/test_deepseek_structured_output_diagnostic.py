from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_deepseek_structured_output_diagnostic as diagnostic  # noqa: E402


def test_stderr_category_detects_cli_option_error():
    assert diagnostic.categorize_stderr(b"error: unknown option '--json-schema'") == "CLI_OPTION_ERROR"


def test_contains_json_object_detects_nested_event_text():
    assert diagnostic.contains_json_object({"result": '{"probe_status":"PASS"}'})


def test_finalize_detects_invocation_defect_when_json_without_schema_works():
    results = diagnostic.finalize(
        "2026-01-01T00:00:00Z",
        [{"name": "json_without_schema", "returncode": 0, "json_object_found": True, "safe_stderr_category": "EMPTY"}],
        [],
        [],
    )

    assert results["terminal_status"] == "STRUCTURED_OUTPUT_INVOCATION_DEFECT_FOUND"


def test_finalize_detects_unsupported_when_all_probes_fail():
    results = diagnostic.finalize(
        "2026-01-01T00:00:00Z",
        [{"name": "json_with_schema", "returncode": 1, "json_object_found": False, "safe_stderr_category": "JSON_SCHEMA_ERROR"}],
        [],
        [],
    )

    assert results["terminal_status"] == "STRUCTURED_OUTPUT_UNSUPPORTED_OR_UNRELIABLE"
