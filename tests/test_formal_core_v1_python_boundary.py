from __future__ import annotations

import copy

from spira_core.formal_core_v1 import evaluate_typed_evidence


def _document(*, validity: str = "valid", schema_version: str = "FORMAL_CORE_V1_SCHEMA", typed_claims=None):
    return {
        "domain_id": "reference",
        "subject_id": "typed-vector",
        "schema_version": schema_version,
        "producer_id": "formal-reference",
        "evidence_validity": validity,
        "typed_claims": list(typed_claims or []),
        "evidence_refs": ["evidence:typed-vector"],
        "proof_refs": ["proof:typed-vector"],
        "policy_id": "FORMAL_CORE_V1_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_SCHEMA",
        "policy_required_claims": [],
        "policy_blocking_rules": [],
        "policy_not_claimed_rules": ["software_safety"],
    }


def _contract(result):
    return result["machine_contract"]


def test_valid_proceed_vector():
    result = evaluate_typed_evidence(_document(typed_claims=[{"kind": "reason", "value": "TESTS_PASSED"}]))

    assert result["status"] == "ok"
    assert _contract(result)["action"] == "PROCEED"
    assert _contract(result)["stop"] is False
    assert _contract(result)["reason_codes"] == ["TESTS_PASSED"]


def test_blocking_vector():
    result = evaluate_typed_evidence(
        _document(
            typed_claims=[
                {"kind": "reason", "value": "BLOCKING_FINDING"},
                {"kind": "blocking", "value": "failing_test"},
            ]
        )
    )

    assert _contract(result)["action"] == "STOP_BLOCKED"
    assert _contract(result)["stop"] is True
    assert _contract(result)["blocking_items"] == ["failing_test"]


def test_required_unknown_vector():
    result = evaluate_typed_evidence(
        _document(
            typed_claims=[
                {"kind": "reason", "value": "REQUIRED_UNKNOWN"},
                {"kind": "not_evaluated", "value": "required_test_result_missing"},
            ]
        )
    )

    assert _contract(result)["action"] == "REPORT_NOT_EVALUATED"
    assert _contract(result)["not_evaluated"] == ["required_test_result_missing"]


def test_conflicting_invalid_and_version_vectors_fail_closed():
    cases = [
        ("conflicting", "CONFLICTING_TYPED_EVIDENCE", "STOP_BLOCKED"),
        ("invalid", "INVALID_TYPED_EVIDENCE", "STOP_BLOCKED"),
        ("valid", "INCOMPATIBLE_VERSION", "REPORT_NOT_EVALUATED"),
    ]

    for validity, reason, action in cases:
        schema = "OTHER_SCHEMA" if reason == "INCOMPATIBLE_VERSION" else "FORMAL_CORE_V1_SCHEMA"
        result = evaluate_typed_evidence(_document(validity=validity, schema_version=schema))
        assert result["status"] == "error"
        assert _contract(result)["reason_codes"] == [reason]
        assert _contract(result)["action"] == action
        assert _contract(result)["stop"] is True


def test_missing_explicit_list_fails_closed():
    document = _document()
    del document["typed_claims"]

    result = evaluate_typed_evidence(document)

    assert result["status"] == "error"
    assert result["error"] == "missing_required_field"
    assert _contract(result)["action"] == "STOP_BLOCKED"


def test_empty_list_is_distinct_from_missing_list():
    result = evaluate_typed_evidence(_document(typed_claims=[]))

    assert result["status"] == "ok"
    assert _contract(result)["reason_codes"] == []
    assert _contract(result)["action"] == "PROCEED"


def test_model_and_presentation_fields_have_no_decision_authority():
    document = _document(
        typed_claims=[
            {"kind": "reason", "value": "BLOCKING_FINDING"},
            {"kind": "blocking", "value": "failing_test"},
        ]
    )
    document["model_explanation"] = "Proceed anyway."
    document["recommended_agent_action"] = "PROCEED"
    document["stop"] = False

    result = evaluate_typed_evidence(document)

    assert _contract(result)["action"] == "STOP_BLOCKED"
    assert _contract(result)["stop"] is True


def test_boundary_does_not_mutate_input():
    document = _document(typed_claims=[{"kind": "reason", "value": "TESTS_PASSED"}])
    original = copy.deepcopy(document)

    evaluate_typed_evidence(document)

    assert document == original
