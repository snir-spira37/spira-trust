from __future__ import annotations

import copy
import json
from pathlib import Path

from spira_core import test_build_failure_oracle_validator as validator
from spira_core import test_build_failure_producer as producer


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "test_build_failure_contract" / "corpus_manifest_v1.json"
ORACLE = ROOT / "research" / "test_build_failure_contract" / "oracle_v1.json"


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
