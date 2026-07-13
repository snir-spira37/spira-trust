from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

from spira_core import mvp_unified
from spira_core import terraform_plan_producer
from spira_core import test_build_failure_producer


ROOT = Path(__file__).resolve().parents[1]


def test_explicit_routing_wraps_pytest_without_semantic_drift():
    envelope = mvp_unified.route(domain="pytest_result", case_id="synthetic_clean_success", root=ROOT)
    manifest = _read_json(ROOT / "research" / "test_build_failure_contract" / "corpus_manifest_v1.json")
    direct = {
        item["case_id"]: item
        for item in test_build_failure_producer.produce_cases(manifest, root=ROOT)
    }["synthetic_clean_success"]

    assert envelope["domain"] == "pytest_result"
    assert envelope["producer_output"] == direct
    assert envelope["semantic_drift"] is False
    assert envelope["direct_contract_hash"] == mvp_unified.sha256_canonical(
        mvp_unified.producer_contract_projection("pytest_result", direct)
    )
    assert envelope["recommended_agent_action"] == direct["produced_policy_action"]["recommended_agent_action"]


def test_explicit_routing_wraps_terraform_without_semantic_drift():
    envelope = mvp_unified.route(domain="terraform_plan", case_id="auth_no_changes", root=ROOT)
    manifest = _read_json(ROOT / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json")
    direct = {
        item["case_id"]: item
        for item in terraform_plan_producer.produce_cases(manifest, root=ROOT)["cases"]
    }["auth_no_changes"]

    assert envelope["domain"] == "terraform_plan"
    assert envelope["producer_output"] == direct
    assert envelope["semantic_drift"] is False
    assert envelope["recommended_agent_action"] == "PROCEED"
    assert envelope["direct_contract_hash"] == mvp_unified.sha256_canonical(
        mvp_unified.producer_contract_projection("terraform_plan", direct)
    )


def test_domain1_baseline_summary_is_preserved():
    summary = mvp_unified.domain1_summary(root=ROOT)
    envelope = mvp_unified.route(domain="python_artifact", root=ROOT)

    assert summary["baseline_root_check"] == "PASS"
    assert summary["record_count"] == 1954
    assert envelope["domain"] == "python_artifact"
    assert envelope["direct_contract_hash"] == envelope["unified_contract_hash"]


def test_unambiguous_detection_and_ambiguous_input_fail_closed():
    assert (
        mvp_unified.resolve_domain(
            evidence_path=ROOT / "research" / "terraform_plan_contract" / "cases" / "auth_no_changes" / "plan.json"
        )
        == "terraform_plan"
    )
    with pytest.raises(mvp_unified.MvpUnifiedError, match="AMBIGUOUS_DOMAIN"):
        mvp_unified.resolve_domain(evidence_path=ROOT / "README.md")


def test_agent_contract_preserves_action_and_boundaries_without_full_output_duplication():
    envelope = mvp_unified.route(domain="terraform_plan", case_id="auth_create_only", root=ROOT)
    contract = mvp_unified.agent_contract(envelope)

    assert "producer_output" not in contract
    assert contract["recommended_agent_action"] == envelope["recommended_agent_action"]
    assert contract["reason_codes"] == envelope["reason_codes"]
    assert contract["not_evaluated"] == envelope["not_evaluated"]
    assert contract["producer_contract_hash"] == envelope["direct_contract_hash"]


def test_mvp_evaluator_passes_three_domain_regression():
    evaluator = _load_tool(ROOT / "tools" / "evaluate_mvp_unified.py")

    result = evaluator.evaluate()

    assert result["status"] == "MVP_IMPLEMENTATION_PASS"
    assert result["domain1_regression"]["baseline_root_check"] == "PASS"
    assert result["domain2_regression"]["oracle_claim_fidelity"] == {"passed": 38, "total": 38, "failed": 0}
    assert result["domain3_regression"]["oracle_claim_fidelity"] == {"passed": 40, "total": 40, "failed": 0}
    assert result["domain2_regression"]["router_semantic_drift_count"] == 0
    assert result["domain3_regression"]["router_semantic_drift_count"] == 0
    assert result["false_proceed_count"] == 0
    assert result["mismatch_count"] == 0


def test_mvp_benchmark_smoke_passes_without_efficiency_claim():
    benchmark = _load_tool(ROOT / "tools" / "benchmark_mvp_unified_agent.py")

    result = benchmark.run_smoke()

    assert result["status"] == "MVP_UNIFIED_REAL_AGENT_BENCHMARK_COMPLETED_WITHOUT_EFFICIENCY_CLAIM"
    assert result["session_count"] == 27
    assert result["efficiency_claim_authorized"] is False
    assert result["median_unified_overhead_ratio"] <= result["overhead_limit_ratio"]
    assert all(item["status"] == "PASS" for item in result["preservation_gates"])


def _load_tool(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))
