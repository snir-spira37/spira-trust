from __future__ import annotations

import json

import pytest

from spira_core.rerun_planner import build_rerun_plan
from spira_core.trust_cli import main


def test_rerun_planner_allows_unchanged_exact_context(tmp_path, capsys):
    context = _context()
    plan = build_rerun_plan(context, context)

    assert plan["schema"] == "SPIRA_AGENT_RERUN_PLAN_V1"
    assert plan["rerun_required"] is False
    assert plan["stop"] is False
    assert plan["recommended_agent_action"] == "REUSE_PRIOR_ACTION"
    assert plan["reason_codes"] == []
    assert plan["reuse"] == ["prior_agent_action_contract"]
    assert len(json.dumps(plan, separators=(",", ":")).encode("utf-8")) < 2 * 1024

    current = tmp_path / "current.json"
    previous = tmp_path / "previous.json"
    current.write_text(json.dumps(context), encoding="utf-8")
    previous.write_text(json.dumps(context), encoding="utf-8")
    assert main(["plan-rerun", "--current-context", str(current), "--previous-context", str(previous), "--format", "json"]) == 0
    cli_plan = json.loads(capsys.readouterr().out)
    assert cli_plan["recommended_agent_action"] == "REUSE_PRIOR_ACTION"


@pytest.mark.parametrize(
    ("field", "value", "reason", "rerun_step"),
    [
        ("artifact_sha256", "b" * 64, "ARTIFACT_CHANGED", "verification"),
        ("command_fingerprint", "c" * 64, "COMMAND_CONTEXT_CHANGED", "verification"),
        ("policy_sha256", "d" * 64, "POLICY_CHANGED", "policy_checks"),
        ("strict_closure", True, "STRICT_CLOSURE_CHANGED", "graph_closure"),
        ("lockfile_sha256", "e" * 64, "LOCKFILE_CHANGED", "lockfile_cross_check"),
        ("baseline_sha256", "f" * 64, "BASELINE_CHANGED", "baseline_drift"),
        ("wheelhouse_sha256", "1" * 64, "WHEELHOUSE_CHANGED", "graph_closure"),
        ("target_environment_sha256", "2" * 64, "TARGET_ENVIRONMENT_CHANGED", "target_environment_checks"),
        ("verify_embedded_sboms", True, "SBOM_VERIFICATION_MODE_CHANGED", "pep770_sbom_consistency"),
        ("attestation_sha256", "3" * 64, "ATTESTATION_CONTEXT_CHANGED", "pep740_offline_attestations"),
        ("attestation_trust_root_sha256", "4" * 64, "ATTESTATION_CONTEXT_CHANGED", "pep740_offline_attestations"),
        ("decision_semantics_version", "SPIRA_DECISION_SEMANTICS_TEST", "DECISION_SEMANTICS_CHANGED", "agent_action_contract"),
        ("tool_version", "different", "TOOL_VERSION_CHANGED", "verification"),
    ],
)
def test_rerun_planner_mutation_matrix_fails_closed(field, value, reason, rerun_step):
    previous = _context()
    current = {**previous, field: value}
    plan = build_rerun_plan(current, previous)

    assert plan["rerun_required"] is True
    assert plan["stop"] is True
    assert plan["recommended_agent_action"] == "RERUN_REQUIRED"
    assert reason in plan["reason_codes"]
    assert rerun_step in plan["rerun"]


@pytest.mark.parametrize(
    ("field", "reason"),
    [
        ("context_ambiguous", "CONTEXT_AMBIGUOUS"),
        ("result_conflict", "EXACT_CONTEXT_RESULT_CONFLICT"),
    ],
)
def test_rerun_planner_state_conflicts_fail_closed(field, reason):
    previous = _context()
    current = {**previous, field: True}
    plan = build_rerun_plan(current, previous)

    assert plan["rerun_required"] is True
    assert plan["recommended_agent_action"] == "RERUN_REQUIRED"
    assert reason in plan["reason_codes"]


def test_rerun_planner_unknown_missing_and_unsupported_contexts_fail_closed():
    previous = _context()
    missing = dict(previous)
    del missing["lockfile_sha256"]
    unknown = {**previous, "artifact_sha256": None}
    unsupported = {**previous, "unsupported_context": True}

    for current, reason in [
        (missing, "CURRENT_MISSING_CONTEXT_FIELDS"),
        (unknown, "CURRENT_UNKNOWN_ARTIFACT_SHA256"),
        (unsupported, "CURRENT_UNSUPPORTED_CONTEXT"),
    ]:
        plan = build_rerun_plan(current, previous)
        assert plan["rerun_required"] is True
        assert plan["stop"] is True
        assert plan["recommended_agent_action"] == "RERUN_REQUIRED"
        assert reason in plan["reason_codes"]


def test_rerun_planner_cli_corrupted_context_fails_closed(tmp_path, capsys):
    current = tmp_path / "current.json"
    previous = tmp_path / "previous.json"
    current.write_text("{not-json", encoding="utf-8")
    previous.write_text(json.dumps(_context()), encoding="utf-8")

    assert main(["plan-rerun", "--current-context", str(current), "--previous-context", str(previous), "--format", "json"]) == 2
    plan = json.loads(capsys.readouterr().out)
    assert plan["rerun_required"] is True
    assert plan["recommended_agent_action"] == "RERUN_REQUIRED"
    assert "CURRENT_UNSUPPORTED_CONTEXT" in plan["reason_codes"]


def _context():
    return {
        "artifact_sha256": "a" * 64,
        "command_fingerprint": "b" * 64,
        "policy_sha256": None,
        "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
        "tool_version": "source-tree",
        "strict_closure": False,
        "lockfile_sha256": None,
        "baseline_sha256": None,
        "wheelhouse_sha256": "c" * 64,
        "target_environment_sha256": None,
        "verify_embedded_sboms": False,
        "attestation_sha256": None,
        "attestation_trust_root_sha256": None,
        "context_ambiguous": False,
        "result_conflict": False,
    }
