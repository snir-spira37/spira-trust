from __future__ import annotations

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_claude_native_primary_benchmark as primary  # noqa: E402


def test_primary_plan_has_180_sessions_and_frozen_order():
    plan = primary.build_primary_plan()

    assert len(plan) == 180
    assert plan[0]["repetition"] == 1
    assert plan[0]["case_id"] == "synthetic_clean_success"
    assert [plan[index]["arm"] for index in range(3)] == ["B", "A", "C"]
    assert plan[-1]["repetition"] == 5
    assert plan[-1]["case_id"] == "03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262"
    assert plan[-1]["arm"] == "C"


def test_primary_plan_covers_only_primary_cases():
    plan = primary.build_primary_plan()
    case_manifest = json.loads(primary.CASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    primary_case_ids = {case["case_id"] for case in case_manifest["cases"] if case["allocation"] == "primary"}

    assert {item["case_id"] for item in plan} == primary_case_ids
    assert all(item["arm"] in {"A", "B", "C"} for item in plan)


def test_plan_hash_is_stable():
    assert primary.plan_sha256(primary.build_primary_plan()) == primary.plan_sha256(primary.build_primary_plan())


def test_resume_manifest_strips_runtime_fields():
    plan = primary.build_primary_plan()
    item = {
        **plan[0],
        "status": "COMPLETED",
        "attempt_count": 1,
        "attempts": [{"attempt": 1}],
        "completed_at_utc": "2026-07-13T00:00:00Z",
        "result_recorded": True,
    }

    assert primary.strip_runtime_fields(item) == plan[0]


def test_infrastructure_failure_classification():
    assert primary.is_infrastructure_failure({"returncode": 1, "result_envelope_present": False})
    assert primary.is_infrastructure_failure(
        {
            "returncode": 0,
            "result_envelope_present": True,
            "structured_output_present": True,
            "usage": {"input_total_available": False},
        }
    )
    assert not primary.is_infrastructure_failure(
        {
            "returncode": 0,
            "result_envelope_present": True,
            "structured_output_present": True,
            "usage": {"input_total_available": True},
        }
    )


def test_usage_and_false_proceed_helpers_are_type_safe():
    assert not primary.usage_available({"usage": "bad"})
    assert not primary.false_proceed({"comparison": "bad"})
    assert primary.usage_available({"usage": {"input_total_available": True}})
    assert primary.false_proceed({"comparison": {"false_proceed": True}})


def test_arm_a_operational_pass_uses_action_gate_and_safety_floor():
    session = {
        "schema_valid": True,
        "workspace_mutated": False,
        "forbidden_tool_count": 0,
        "usage": {"input_total_available": True},
        "comparison": {
            "false_proceed": False,
            "checks": {
                "gate": True,
                "recommended_agent_action": True,
                "reason_codes": False,
                "not_claimed": False,
            },
        },
    }

    assert primary.arm_a_operational_pass(session)


def test_primary_runner_declares_checkpoint_files():
    assert primary.SESSION_MANIFEST_PATH.name == "claude_native_primary_session_manifest.json"
    assert primary.RESULTS_PATH.name == "claude_native_primary_results.json"
    assert primary.PRIVATE_MANIFEST_PATH.name == "claude_native_primary_raw_private_manifest.json"


def test_atomic_json_write_round_trips(tmp_path):
    path = tmp_path / "checkpoint.json"

    primary.atomic_json_write(path, {"b": 2, "a": 1})

    assert json.loads(path.read_text(encoding="utf-8")) == {"a": 1, "b": 2}
    assert not list(tmp_path.glob(".*.tmp"))
