from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


FORMAL_CORE_V1_CONTRACT_ID = "FORMAL_CORE_V1_CONTRACT"

ACTION_PROCEED = "PROCEED"
ACTION_STOP_BLOCKED = "STOP_BLOCKED"
ACTION_RERUN_REQUIRED = "RERUN_REQUIRED"
ACTION_REPORT_NOT_EVALUATED = "REPORT_NOT_EVALUATED"

VALIDITY_VALID = "valid"
VALIDITY_INVALID = "invalid"
VALIDITY_INCOMPLETE = "incomplete"
VALIDITY_CONFLICTING = "conflicting"
VALIDITY_VERSION_INCOMPATIBLE = "version_incompatible"
VALIDITY_INTERNAL_FAILURE = "internal_failure"

REQUIRED_FIELDS = (
    "domain_id",
    "subject_id",
    "schema_version",
    "producer_id",
    "evidence_validity",
    "typed_claims",
    "evidence_refs",
    "proof_refs",
    "policy_id",
    "policy_schema_version",
    "policy_required_claims",
    "policy_blocking_rules",
    "policy_not_claimed_rules",
)

VALIDITIES = {
    VALIDITY_VALID,
    VALIDITY_INVALID,
    VALIDITY_INCOMPLETE,
    VALIDITY_CONFLICTING,
    VALIDITY_VERSION_INCOMPATIBLE,
    VALIDITY_INTERNAL_FAILURE,
}


@dataclass(frozen=True)
class CoreFailure:
    error: str
    action: str
    reason_code: str
    not_evaluated: tuple[str, ...] = ()


FAILURES: dict[str, CoreFailure] = {
    "MISSING_REQUIRED_FIELD": CoreFailure(
        error="missing_required_field",
        action=ACTION_STOP_BLOCKED,
        reason_code="MISSING_REQUIRED_FIELD",
    ),
    "INVALID_TYPED_EVIDENCE": CoreFailure(
        error="invalid_typed_evidence",
        action=ACTION_STOP_BLOCKED,
        reason_code="INVALID_TYPED_EVIDENCE",
    ),
    "INCOMPLETE_TYPED_EVIDENCE": CoreFailure(
        error="incomplete_typed_evidence",
        action=ACTION_REPORT_NOT_EVALUATED,
        reason_code="INCOMPLETE_TYPED_EVIDENCE",
        not_evaluated=("required information unavailable",),
    ),
    "CONFLICTING_TYPED_EVIDENCE": CoreFailure(
        error="conflicting_typed_evidence",
        action=ACTION_STOP_BLOCKED,
        reason_code="CONFLICTING_TYPED_EVIDENCE",
    ),
    "INCOMPATIBLE_VERSION": CoreFailure(
        error="incompatible_version",
        action=ACTION_REPORT_NOT_EVALUATED,
        reason_code="INCOMPATIBLE_VERSION",
        not_evaluated=("schema version incompatible",),
    ),
    "INTERNAL_VALIDATION_FAILURE": CoreFailure(
        error="internal_validation_failure",
        action=ACTION_STOP_BLOCKED,
        reason_code="INTERNAL_VALIDATION_FAILURE",
    ),
}


def evaluate_typed_evidence(document: Mapping[str, Any]) -> dict[str, Any]:
    """Evaluate canonical typed evidence using Formal Core V1 Python semantics.

    This is a research boundary for differential comparison with Lean. It does
    not parse raw artifacts, call models, or integrate with production runtime
    paths.
    """

    missing = [field for field in REQUIRED_FIELDS if field not in document]
    if missing:
        return _fail_closed(document, FAILURES["MISSING_REQUIRED_FIELD"], details={"missing_fields": missing})

    list_error = _first_list_shape_error(document)
    if list_error:
        return _fail_closed(document, FAILURES["MISSING_REQUIRED_FIELD"], details=list_error)

    validity = str(document["evidence_validity"])
    if validity not in VALIDITIES:
        return _fail_closed(
            document,
            FAILURES["INVALID_TYPED_EVIDENCE"],
            details={"invalid_evidence_validity": validity},
        )

    if validity == VALIDITY_INVALID:
        return _fail_closed(document, FAILURES["INVALID_TYPED_EVIDENCE"])
    if validity == VALIDITY_INCOMPLETE:
        return _fail_closed(document, FAILURES["INCOMPLETE_TYPED_EVIDENCE"])
    if validity == VALIDITY_CONFLICTING:
        return _fail_closed(document, FAILURES["CONFLICTING_TYPED_EVIDENCE"])
    if validity == VALIDITY_VERSION_INCOMPATIBLE:
        return _fail_closed(document, FAILURES["INCOMPATIBLE_VERSION"])
    if validity == VALIDITY_INTERNAL_FAILURE:
        return _fail_closed(document, FAILURES["INTERNAL_VALIDATION_FAILURE"])
    if str(document["schema_version"]) != str(document["policy_schema_version"]):
        return _fail_closed(document, FAILURES["INCOMPATIBLE_VERSION"])

    typed_claims = list(document["typed_claims"])
    reason_codes = _claims_of_kind(typed_claims, "reason")
    blocking_items = _claims_of_kind(typed_claims, "blocking")
    not_evaluated = _claims_of_kind(typed_claims, "not_evaluated")
    not_claimed = _claims_of_kind(typed_claims, "not_claimed")
    evidence_refs = list(document["evidence_refs"]) + _claims_of_kind(typed_claims, "evidence_ref")
    proof_refs = list(document["proof_refs"]) + _claims_of_kind(typed_claims, "proof_ref")
    action = _decide_action(blocking_items=blocking_items, not_evaluated=not_evaluated)

    return {
        "status": "ok",
        "error": None,
        "machine_contract": _contract(
            document,
            action=action,
            reason_codes=reason_codes,
            blocking_items=blocking_items,
            not_evaluated=not_evaluated,
            not_claimed=not_claimed,
            evidence_refs=evidence_refs,
            proof_refs=proof_refs,
        ),
    }


def _first_list_shape_error(document: Mapping[str, Any]) -> dict[str, Any] | None:
    for field in (
        "typed_claims",
        "evidence_refs",
        "proof_refs",
        "policy_required_claims",
        "policy_blocking_rules",
        "policy_not_claimed_rules",
    ):
        if not isinstance(document.get(field), list):
            return {"field": field, "expected": "list"}
    return None


def _claims_of_kind(claims: list[Any], kind: str) -> list[str]:
    values: list[str] = []
    for claim in claims:
        if isinstance(claim, Mapping) and claim.get("kind") == kind and "value" in claim:
            values.append(str(claim["value"]))
    return values


def _decide_action(*, blocking_items: list[str], not_evaluated: list[str]) -> str:
    if blocking_items:
        return ACTION_STOP_BLOCKED
    if not_evaluated:
        return ACTION_REPORT_NOT_EVALUATED
    return ACTION_PROCEED


def _fail_closed(
    document: Mapping[str, Any],
    failure: CoreFailure,
    *,
    details: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status": "error",
        "error": failure.error,
        "details": dict(details or {}),
        "machine_contract": _contract(
            document,
            action=failure.action,
            reason_codes=[failure.reason_code],
            blocking_items=[],
            not_evaluated=list(failure.not_evaluated),
            not_claimed=_list_or_empty(document.get("policy_not_claimed_rules")),
            evidence_refs=_list_or_empty(document.get("evidence_refs")),
            proof_refs=_list_or_empty(document.get("proof_refs")),
        ),
    }


def _contract(
    document: Mapping[str, Any],
    *,
    action: str,
    reason_codes: list[str],
    blocking_items: list[str],
    not_evaluated: list[str],
    not_claimed: list[str],
    evidence_refs: list[str],
    proof_refs: list[str],
) -> dict[str, Any]:
    return {
        "domain_id": str(document.get("domain_id", "__missing__")),
        "subject_id": str(document.get("subject_id", "__missing__")),
        "policy_id": str(document.get("policy_id", "__missing__")),
        "schema_version": str(document.get("policy_schema_version", document.get("schema_version", "__missing__"))),
        "producer_id": str(document.get("producer_id", "__missing__")),
        "contract_id": FORMAL_CORE_V1_CONTRACT_ID,
        "action": action,
        "stop": action != ACTION_PROCEED,
        "reason_codes": list(reason_codes),
        "blocking_items": list(blocking_items),
        "not_evaluated": list(not_evaluated),
        "not_claimed": list(not_claimed),
        "evidence_refs": list(evidence_refs),
        "proof_refs": list(proof_refs),
    }


def _list_or_empty(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
