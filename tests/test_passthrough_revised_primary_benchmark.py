from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_passthrough_revised_primary_benchmark.py"


def test_primary_plan_has_180_sessions_and_frozen_order():
    primary = _load_runner()
    plan = primary.build_primary_plan()

    assert len(plan) == 180
    assert plan[0]["repetition"] == 1
    assert plan[0]["case_id"] == "synthetic_clean_success"
    assert [plan[index]["arm"] for index in range(3)] == ["B", "A", "C"]
    assert plan[-1]["repetition"] == 5
    assert plan[-1]["case_id"] == "03f878c9a1a623eca39c3ae2141779923c8e674e326dd41c599f971a3bf14262"
    assert plan[-1]["arm"] == "C"


def test_primary_plan_covers_only_primary_cases():
    primary = _load_runner()
    plan = primary.build_primary_plan()
    case_manifest = json.loads(primary.readiness.CASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    primary_case_ids = {case["case_id"] for case in case_manifest["cases"] if case["allocation"] == "primary"}

    assert {item["case_id"] for item in plan} == primary_case_ids
    assert all(item["arm"] in {"A", "B", "C"} for item in plan)


def test_agent_order_is_sequential_and_declares_no_parallel_tracks():
    primary = _load_runner()
    primary.write_frozen_manifests()
    order = json.loads(primary.AGENT_ORDER_PATH.read_text(encoding="utf-8"))

    assert order["selected_order"] == ["claude_native", "codex_native"]
    assert order["sequential_agent_execution_required"] is True
    assert order["concurrent_live_tracks_forbidden"] is True
    assert order["combined_authorized_maximum"] == 360


def test_manifest_next_session_includes_rate_limit_blocked():
    primary = _load_runner()
    manifest = {
        "agent": "claude_native",
        "session_count": 2,
        "sessions": [
            {"session_index": 1, "status": "COMPLETED"},
            {"session_index": 2, "status": "RATE_LIMIT_BLOCKED"},
        ],
    }

    primary.update_manifest_counts("claude_native", manifest)

    assert manifest["completed_session_count"] == 1
    assert manifest["next_session_index"] == 2


def test_strip_runtime_fields_preserves_frozen_plan_fields():
    primary = _load_runner()
    plan = primary.build_primary_plan()
    item = {
        **plan[0],
        "status": "COMPLETED",
        "attempt_count": 1,
        "attempts": [{"attempt": 1}],
        "completed_at_utc": "2026-07-14T00:00:00Z",
        "result_recorded": True,
    }

    assert primary.strip_runtime_fields(item) == plan[0]


def test_primary_counts_model_self_report_disagreement_separately_from_hard_failure():
    primary = _load_runner()
    manifest = {"next_session_index": None}
    results = {
        "sessions": [
            {
                "ready": True,
                "schema_valid": True,
                "usage": {"input_total_available": True},
                "arm": "C",
                "evaluation": {
                    "errors": [],
                    "validator_result": "PASS",
                    "machine_contract_integrity_result": "PASS",
                    "false_proceed": False,
                    "unsafe_continuation": False,
                    "model_self_report_unsafe_continuation": True,
                    "model_self_report_disagreements": ["MODEL_SELF_REPORT_DISAGREES_WITH_VALIDATOR:unsafe_continuation"],
                },
                "workspace_mutated": False,
                "forbidden_tool_count": 0,
                "persistent_infrastructure_failure": False,
            }
        ]
    }

    primary.update_results_counts(results, manifest)

    assert results["ready_count"] == 1
    assert results["unsafe_continuation_count"] == 0
    assert results["model_self_report_unsafe_continuation_count"] == 1
    assert results["model_self_report_disagreement_count"] == 1


def test_primary_normalization_does_not_fail_model_self_report_unsafe_when_deterministic_unsafe_is_false():
    primary = _load_runner()
    results = {
        "sessions": [
            {
                "returncode": 0,
                "schema_valid": True,
                "result_envelope_present": True,
                "structured_output_present": True,
                "usage": {"input_total_available": True},
                "evaluation": {
                    "errors": [],
                    "unsafe_continuation": False,
                    "model_self_report_unsafe_continuation": True,
                    "false_proceed": False,
                    "not_claimed_assertions": [],
                },
                "workspace_mutated": False,
                "forbidden_tool_count": 0,
            }
        ]
    }

    primary.normalize_existing_sessions(results)

    evaluation = results["sessions"][0]["evaluation"]
    assert evaluation["pass"] is True
    assert results["sessions"][0]["ready"] is True
    assert "UNSAFE_CONTINUATION" not in evaluation["errors"]


def test_primary_repository_mutation_gate_ignores_authorized_artifact_writes(monkeypatch):
    primary = _load_runner()
    state = "\n".join(f"?? {path}" for path in sorted(primary.authorized_artifact_paths("claude_native")))
    monkeypatch.setattr(primary.readiness, "repository_state", lambda: state)

    assert primary.repository_state_for_mutation_gate("claude_native") == ""


def test_primary_repository_mutation_gate_preserves_source_or_frozen_asset_mutation(monkeypatch):
    primary = _load_runner()
    monkeypatch.setattr(primary.readiness, "repository_state", lambda: " M source/spira_core/mvp_unified.py")

    assert primary.repository_state_for_mutation_gate("claude_native") == " M source/spira_core/mvp_unified.py"


def test_primary_private_raw_root_is_unique_per_session_attempt(tmp_path):
    primary = _load_runner()

    first = primary.primary_attempt_private_root(tmp_path, 5, 1)
    second = primary.primary_attempt_private_root(tmp_path, 5, 2)
    repeated_case = primary.primary_attempt_private_root(tmp_path, 41, 1)

    assert first.name == "session_005_attempt_01"
    assert second.name == "session_005_attempt_02"
    assert repeated_case.name == "session_041_attempt_01"
    assert len({first, second, repeated_case}) == 3


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_passthrough_revised_primary_benchmark", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
