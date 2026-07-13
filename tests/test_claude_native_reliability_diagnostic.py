from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_reliability_diagnostic as diagnostic  # noqa: E402


def test_diagnostic_plan_is_exactly_thirty_sessions():
    plan = diagnostic.diagnostic_plan()

    assert len(plan) == 30


def test_diagnostic_plan_counts_authorized_cells_only():
    counts = {}
    for planned in diagnostic.diagnostic_plan():
        item = planned["item"]
        key = (planned["role"], item["domain"], item["case_id"], item["arm"])
        counts[key] = counts.get(key, 0) + 1

    assert counts == {
        ("CRITICAL_ARM_B", "pytest_result", "synthetic_clean_success", "B"): 10,
        ("FAILED_ARM_A_PYTEST", "pytest_result", "synthetic_clean_success", "A"): 5,
        (
            "FAILED_ARM_A_PYTHON_ARTIFACT",
            "python_artifact",
            "0006ef4f580f536bdea2368b85005c6598cf0c1aea729e3c373414c625ecebd4",
            "A",
        ): 5,
        ("FAILED_ARM_A_TERRAFORM", "terraform_plan", "auth_no_changes", "A"): 5,
        ("MATCHED_ARM_C_CONTROL", "pytest_result", "synthetic_clean_success", "C"): 5,
    }


def test_summarize_by_cell_counts_output_not_object():
    sessions = [
        {
            "diagnostic_role": "CRITICAL_ARM_B",
            "domain": "pytest_result",
            "case_id": "synthetic_clean_success",
            "arm": "B",
            "returncode": 1,
            "output_found": False,
            "schema_valid": False,
            "comparison": {"pass": False, "errors": ["OUTPUT_NOT_OBJECT"], "false_proceed": False},
        }
    ]

    summary = diagnostic.summarize_by_cell(sessions)

    assert summary[0]["output_not_object_count"] == 1
    assert summary[0]["correct_count"] == 0


def test_tool_permission_denial_observed_from_reason_code():
    session = {
        "agent_output": {
            "reason_codes": ["MISSING_PERMISSIONS"],
            "blocking_items": ["Permission denied for Read tool"],
        }
    }

    assert diagnostic.tool_permission_denial_observed(session)
