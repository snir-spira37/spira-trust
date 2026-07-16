from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_read_invocation_hardening_diagnostic as hardening  # noqa: E402


def test_benchmark_plan_is_exactly_fifteen_sessions():
    plan = hardening.benchmark_plan()

    assert len(plan) == 15


def test_benchmark_plan_counts_authorized_cells_only():
    counts = {}
    for planned in hardening.benchmark_plan():
        item = planned["item"]
        key = (planned["role"], item["domain"], item["case_id"], item["arm"])
        counts[key] = counts.get(key, 0) + 1

    assert counts == {
        ("CRITICAL_ARM_B", "pytest_result", "synthetic_clean_success", "B"): 10,
        ("MATCHED_ARM_C", "pytest_result", "synthetic_clean_success", "C"): 5,
    }


def test_raw_permission_denial_present_from_metadata():
    assert hardening.raw_permission_denial_present({"permission_denials": [{"tool_name": "Read"}]})


def test_sanitize_value_redacts_windows_paths():
    synthetic_user_path = "C:" + "\\Users\\example\\AppData\\Local\\Temp\\file.txt"
    value = {"blocking_items": [f"Permission denied: {synthetic_user_path}"]}

    sanitized = hardening.sanitize_value(value)

    assert "example" not in sanitized["blocking_items"][0]
    assert "<REDACTED_LOCAL_PATH>" in sanitized["blocking_items"][0]


def test_hardened_runner_source_has_single_json_output_format():
    source = Path(hardening.__file__).read_text(encoding="utf-8")

    assert source.count('"--output-format"') == 1
    assert '"json"' in source
    assert '"stream-json"' not in source
    assert '"--json-schema"' in source
    assert '"--allowedTools"' in source
    assert '"--permission-mode"' in source
    assert '"dontAsk"' in source


def test_result_envelope_and_structured_output_detection():
    parsed = {"type": "result", "structured_output": {"gate": "PROCEED"}}

    assert hardening.result_envelope_present(parsed)
    assert hardening.structured_output_present(parsed)
