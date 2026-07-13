from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

from spira_core import terraform_plan_oracle_validator as validator
from spira_core import terraform_plan_producer as producer


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"
ORACLE = ROOT / "research" / "terraform_plan_contract" / "oracle_v1.json"
EVALUATOR = ROOT / "tools" / "evaluate_terraform_plan_producer.py"


def test_producer_matches_accepted_oracle_for_full_corpus():
    produced = producer.produce_cases(_manifest(), root=ROOT)
    candidate = producer.candidate_oracle_from_produced(_oracle(), produced)
    report = validator.validate_oracle_document(candidate, root=ROOT)

    assert len(produced["cases"]) == 40
    assert len(produced["mutation_relationships"]) == 10
    assert report["verdict"] == "PASS"
    assert candidate["cases"] == _oracle()["cases"]
    assert candidate["mutation_relationships"] == _oracle()["mutation_relationships"]


def test_no_changes_applyable_false_is_not_blocked():
    produced = {case["case_id"]: case for case in producer.produce_cases(_manifest(), root=ROOT)["cases"]}

    action = produced["syn_applyable_false_no_changes"]["produced_policy_action"]

    assert action["recommended_agent_action"] == "PROCEED"
    assert action["reason_codes"] == ["TERRAFORM_PLAN_NO_CHANGES"]


def test_replace_order_and_replace_paths_are_identity_bearing():
    produced = {case["case_id"]: case for case in producer.produce_cases(_manifest(), root=ROOT)["cases"]}

    delete_create = produced["auth_replace_delete_create"]["produced_claims"]
    create_delete = produced["auth_replace_create_delete"]["produced_claims"]
    base = produced["syn_replace_path_base"]["produced_explicit_lists"]["replace_paths"]
    mutated = produced["syn_replace_path_mutation"]["produced_explicit_lists"]["replace_paths"]

    assert _action_sequence(delete_create) == ["delete", "create"]
    assert _action_sequence(create_delete) == ["create", "delete"]
    assert base == ["/resource_changes/0/change/replace_paths/0"]
    assert mutated == ["/resource_changes/0/change/replace_paths/0", "/resource_changes/0/change/replace_paths/1"]


def test_unknown_and_sensitive_paths_are_not_evaluated_without_value_exposure():
    produced = {case["case_id"]: case for case in producer.produce_cases(_manifest(), root=ROOT)["cases"]}
    unknown = produced["syn_unknown_after_values"]
    sensitive = produced["syn_sensitive_paths"]

    assert unknown["produced_explicit_lists"]["unknown_paths"]
    assert sensitive["produced_explicit_lists"]["sensitive_paths"]
    assert all(
        claim["status"] == "NOT_EVALUATED"
        for claim in unknown["produced_claims"]
        if claim["claim_type"] == "PLANNED_VALUE_UNKNOWN"
    )
    assert all(
        claim["status"] == "NOT_EVALUATED"
        for claim in sensitive["produced_claims"]
        if claim["claim_type"] == "SENSITIVE_PATH_PRESENT"
    )
    assert not any("password" in json.dumps(claim).lower() for claim in sensitive["produced_claims"])


def test_instruction_like_values_do_not_override_policy():
    produced = {case["case_id"]: case for case in producer.produce_cases(_manifest(), root=ROOT)["cases"]}

    tag_action = produced["syn_instruction_text_tag"]["produced_policy_action"]
    description_action = produced["syn_instruction_text_description"]["produced_policy_action"]

    assert tag_action["recommended_agent_action"] == "STOP_BLOCKED"
    assert description_action["recommended_agent_action"] == "STOP_BLOCKED"


def test_order_only_mutation_preserves_claim_identity_but_not_contextual_identity():
    produced = producer.produce_cases(_manifest(), root=ROOT)
    relation = {item["pair_id"]: item for item in produced["mutation_relationships"]}["mutation_order_only"]

    assert relation["expected_claims_relation"] == "SAME"
    assert relation["expected_claims_root_relation"] == "SAME"
    assert relation["expected_unification_id_relation"] == "DIFFERENT"


def test_evaluator_passes_for_full_corpus():
    evaluator = _evaluator()
    oracle = _oracle()
    produced = producer.produce_cases(_manifest(), root=ROOT)
    validation = validator.validate_oracle_document(producer.candidate_oracle_from_produced(oracle, produced), root=ROOT)

    result = evaluator.evaluate_against_oracle(oracle, produced, validation)

    assert result["status"] == "DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_PASS"
    assert result["mismatch_count"] == 0
    assert result["oracle_claim_fidelity"] == {"passed": 40, "total": 40, "failed": 0}
    assert result["mutation_relationship_fidelity"] == {"passed": 10, "total": 10, "failed": 0}


def test_evaluator_negative_gates_fail():
    fixtures = [
        _claim_mismatch,
        _action_mismatch,
        _false_proceed,
        _strict_list_mismatch,
        _evidence_pointer_mismatch,
        _mutation_relationship_mismatch,
        _sensitive_value_leak,
        _instruction_override,
        _not_evaluated_dropped,
        _block_dropped,
    ]
    for mutate in fixtures:
        evaluator = _evaluator()
        oracle = _oracle()
        produced = producer.produce_cases(_manifest(), root=ROOT)
        mutate(produced)
        validation = validator.validate_oracle_document(producer.candidate_oracle_from_produced(oracle, produced), root=ROOT)

        result = evaluator.evaluate_against_oracle(oracle, produced, validation)

        assert result["status"] == "DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_FAILED"
        assert result["mismatch_count"] > 0 or result["false_proceed_count"] > 0 or result["sensitive_value_leaks"] > 0


def _action_sequence(claims: list[dict]) -> list[str]:
    for claim in claims:
        if claim["claim_type"] == "TERRAFORM_RESOURCE_ACTION_SEQUENCE":
            return claim["value"]["action_sequence"]
    raise AssertionError("missing action sequence")


def _manifest() -> dict:
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def _oracle() -> dict:
    return json.loads(ORACLE.read_text(encoding="utf-8"))


def _evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_terraform_plan_producer", EVALUATOR)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _first_case(produced: dict) -> dict:
    return produced["cases"][0]


def _case(produced: dict, case_id: str) -> dict:
    for item in produced["cases"]:
        if item["case_id"] == case_id:
            return item
    raise AssertionError(case_id)


def _claim_mismatch(produced: dict) -> None:
    _first_case(produced)["produced_claims"][0]["value"] = {"string": "mutated"}


def _action_mismatch(produced: dict) -> None:
    _first_case(produced)["produced_policy_action"]["reason_codes"] = ["TERRAFORM_PLAN_CHANGES_PRESENT"]


def _false_proceed(produced: dict) -> None:
    item = _case(produced, "auth_create_only")
    item["produced_policy_action"] = {
        "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
        "stop": False,
        "recommended_agent_action": "PROCEED",
        "reason_codes": ["TERRAFORM_PLAN_NO_CHANGES"],
    }


def _strict_list_mismatch(produced: dict) -> None:
    _case(produced, "auth_create_only")["produced_explicit_lists"]["create_resources"] = []


def _evidence_pointer_mismatch(produced: dict) -> None:
    _first_case(produced)["produced_claims"][0]["evidence"][0]["json_pointer"] = "/wrong"


def _mutation_relationship_mismatch(produced: dict) -> None:
    produced["mutation_relationships"][0]["expected_claims_relation"] = "SAME"


def _sensitive_value_leak(produced: dict) -> None:
    _first_case(produced)["produced_claims"][0]["value"] = {"string": "password=leak"}


def _instruction_override(produced: dict) -> None:
    _case(produced, "syn_instruction_text_tag")["produced_policy_action"]["recommended_agent_action"] = "PROCEED"


def _not_evaluated_dropped(produced: dict) -> None:
    item = _case(produced, "syn_unknown_after_values")
    for claim in item["produced_claims"]:
        if claim["claim_type"] == "PLANNED_VALUE_UNKNOWN":
            claim["status"] = "PASS"
            return
    raise AssertionError("missing unknown claim")


def _block_dropped(produced: dict) -> None:
    item = _case(produced, "syn_errored_true")
    for claim in item["produced_claims"]:
        if claim["claim_type"] == "TERRAFORM_PLAN_ERRORED":
            claim["status"] = "PASS"
            return
    raise AssertionError("missing errored claim")
