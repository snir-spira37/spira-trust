from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_usage_telemetry_invocation_repair_probe as probe  # noqa: E402


def test_probe_plan_is_three_benchmark_sessions():
    plan = probe.probe_plan()

    assert len(plan) == 3


def test_probe_plan_counts_authorized_cells_only():
    counts = {}
    for planned in probe.probe_plan():
        item = planned["item"]
        key = (planned["role"], item["domain"], item["case_id"], item["arm"])
        counts[key] = counts.get(key, 0) + 1

    assert counts == {
        ("CRITICAL_ARM_B", "pytest_result", "synthetic_clean_success", "B"): 2,
        ("MATCHED_ARM_C", "pytest_result", "synthetic_clean_success", "C"): 1,
    }


def test_usage_available_requires_numeric_input_and_output_tokens():
    assert probe.usage_available({"usage": {"input_total_available": True, "input_tokens": 1, "output_tokens": 2}})
    assert not probe.usage_available({"usage": {"input_total_available": True, "input_tokens": 1}})


def test_result_envelope_and_structured_output_checks():
    session = {"result_envelope_present": True, "structured_output_present": True}

    assert probe.result_envelope_present(session)
    assert probe.structured_output_present(session)
