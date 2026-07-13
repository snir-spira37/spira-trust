from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

from spira_core import test_build_failure_oracle_validator as validator
from spira_core import test_build_failure_producer as producer


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "test_build_failure_contract" / "corpus_manifest_v1.json"
ORACLE = ROOT / "research" / "test_build_failure_contract" / "oracle_v1.json"
EVALUATOR = ROOT / "tools" / "evaluate_test_build_failure_producer.py"


def test_producer_matches_accepted_oracle_for_full_corpus():
    manifest = _manifest()
    oracle = _oracle()

    produced = producer.produce_cases(manifest, root=ROOT)
    candidate = _candidate_oracle(oracle, produced)
    report = validator.validate_oracle_document(candidate)

    assert len(produced) == 38
    assert report["verdict"] == "PASS"
    for expected, actual in zip(oracle["cases"], candidate["cases"]):
        assert actual["case_id"] == expected["case_id"]
        assert actual["expected_claims"] == expected["expected_claims"]
        assert actual["expected_policy_action"] == expected["expected_policy_action"]
        assert actual["expected_explicit_lists"] == expected["expected_explicit_lists"]
        assert actual["expected_identity_relationships"] == expected["expected_identity_relationships"]
        assert actual["expected_evidence_locators"] == expected["expected_evidence_locators"]


def test_conflicting_console_and_junit_requires_rerun():
    case = _case("synthetic_console_junit_conflict")

    output = producer.produce_case(case, root=ROOT)

    assert output["produced_result_identity"]["status"] == "NOT_EVALUATED"
    assert output["produced_policy_action"]["recommended_agent_action"] == "RERUN_REQUIRED"
    assert output["produced_policy_action"]["reason_codes"] == ["TEST_EVIDENCE_CONFLICT"]
    assert output["produced_source_sufficiency"]["console"] == "CONFLICTING"
    assert output["produced_source_sufficiency"]["junit"] == "CONFLICTING"


def test_public_withheld_outputs_fail_closed_without_semantic_identity():
    case = _case("public_requests_clean")

    output = producer.produce_case(case, root=ROOT)

    assert output["produced_result_identity"]["status"] == "NOT_EVALUATED"
    assert "result_identity_sha256" not in output["produced_result_identity"]
    assert output["produced_policy_action"]["recommended_agent_action"] == "REPORT_NOT_EVALUATED"
    assert output["produced_policy_action"]["reason_codes"] == ["PUBLIC_RUN_OUTPUT_WITHHELD"]
    assert output["produced_source_sufficiency"]["console"] == "NOT_EVALUATED"
    assert output["produced_source_sufficiency"]["junit"] == "NOT_EVALUATED"


def test_classification_does_not_use_case_kind_as_answer_key():
    case = copy.deepcopy(_case("synthetic_single_assertion_failure"))
    case["case_kind"] = "clean_successful_run"

    output = producer.produce_case(case, root=ROOT)

    assert output["produced_policy_action"]["recommended_agent_action"] == "STOP_BLOCKED"
    assert output["produced_policy_action"]["reason_codes"] == ["TEST_FAILURE"]
    assert output["produced_claims"][0]["status"] == "BLOCK"


def test_contextual_mutation_relationship_preserves_scope_and_result_identity():
    manifest = _manifest()
    produced = {case["case_id"]: case for case in producer.produce_cases(manifest, root=ROOT)}

    relation = produced["synthetic_single_assertion_failure"]["produced_identity_relationships"]
    by_related = {item["related_case_id"]: item for item in relation}

    assert by_related["synthetic_long_traceback"]["run_identity_relation"] == "DIFFERENT"
    assert by_related["synthetic_long_traceback"]["scope_identity_relation"] == "SAME"
    assert by_related["synthetic_long_traceback"]["result_identity_relation"] == "SAME"
    assert by_related["synthetic_multiple_failures"]["result_identity_relation"] == "DIFFERENT"


def test_scope_identity_mismatch_fails_evaluation():
    evaluator = _evaluator()
    oracle = _oracle()
    produced = producer.produce_cases(_manifest(), root=ROOT)
    produced[0] = copy.deepcopy(produced[0])
    produced[0]["produced_scope_identity"] = copy.deepcopy(produced[0]["produced_scope_identity"])
    produced[0]["produced_scope_identity"]["scope_identity_sha256"] = "0" * 64

    result = evaluator.evaluate_against_oracle(oracle, produced, _validator_pass())

    assert result["status"] == "DOMAIN_2_PRODUCER_IMPLEMENTATION_FAILED"
    assert result["scope_identity_fidelity"]["failed"] == 1
    assert result["mismatch_count"] > 0


def test_result_identity_mismatch_fails_evaluation():
    evaluator = _evaluator()
    oracle = _oracle()
    produced = producer.produce_cases(_manifest(), root=ROOT)
    produced[8] = copy.deepcopy(produced[8])
    produced[8]["produced_result_identity"] = copy.deepcopy(produced[8]["produced_result_identity"])
    if produced[8]["produced_result_identity"]["status"] == "EMITTED":
        produced[8]["produced_result_identity"]["result_identity_sha256"] = "0" * 64
    else:
        produced[8]["produced_result_identity"]["reason_codes"] = ["MUTATED"]

    result = evaluator.evaluate_against_oracle(oracle, produced, _validator_pass())

    assert result["status"] == "DOMAIN_2_PRODUCER_IMPLEMENTATION_FAILED"
    assert result["result_identity_fidelity"]["failed"] == 1
    assert result["mismatch_count"] > 0


def test_mismatch_count_blocks_pass_even_when_other_gates_are_green(monkeypatch):
    evaluator = _evaluator()
    oracle = _oracle()
    produced = producer.produce_cases(_manifest(), root=ROOT)
    produced[0] = copy.deepcopy(produced[0])
    produced[0]["produced_scope_identity"] = copy.deepcopy(produced[0]["produced_scope_identity"])
    produced[0]["produced_scope_identity"]["scope_identity_sha256"] = "0" * 64

    monkeypatch.setattr(evaluator, "_count", lambda *, all_values: {"passed": len(all_values), "total": len(all_values), "failed": 0})
    result = evaluator.evaluate_against_oracle(oracle, produced, _validator_pass())

    assert result["mismatch_count"] > 0
    assert result["status"] == "DOMAIN_2_PRODUCER_IMPLEMENTATION_FAILED"


def _manifest():
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _oracle():
    return json.loads(ORACLE.read_text(encoding="utf-8"))


def _case(case_id: str):
    for item in _manifest()["cases"]:
        if item["case_id"] == case_id:
            return item
    raise AssertionError(case_id)


def _candidate_oracle(oracle: dict, produced: list[dict]) -> dict:
    candidate = {key: value for key, value in oracle.items() if key != "cases"}
    candidate["cases"] = [
        {
            "case_id": item["case_id"],
            "case_schema_version": item["case_schema_version"],
            "review_class": "AUTHOR_REVIEW",
            "review_status": "REVIEWED",
            "input_manifest_sha256": item["input_manifest_sha256"],
            "input_sources": item["input_sources"],
            "supported_input": item["supported_input"],
            "expected_source_sufficiency": item["produced_source_sufficiency"],
            "expected_scope_identity": item["produced_scope_identity"],
            "expected_result_identity": item["produced_result_identity"],
            "expected_policy_action": item["produced_policy_action"],
            "expected_identity_relationships": item["produced_identity_relationships"],
            "expected_claims": item["produced_claims"],
            "expected_explicit_lists": item["produced_explicit_lists"],
            "expected_not_evaluated": item["produced_not_evaluated"],
            "expected_not_claimed": item["produced_not_claimed"],
            "expected_evidence_locators": item["produced_evidence_locators"],
        }
        for item in produced
    ]
    return candidate


def _evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_test_build_failure_producer", EVALUATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _validator_pass():
    return {
        "verdict": "PASS",
        "status": "ORACLE_VALIDATION_PASS",
        "counts": {
            "case_count": 38,
            "relationship_count": 12,
            "declared_delta_count": 6,
            "error_count": 0,
            "warning_count": 0,
        },
    }
