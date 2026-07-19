from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from spira_core.nesira_phase2_authority_adapter import assess_authority
from spira_core.nesira_phase2_identity_adapter import assess_identity
from spira_core.nesira_phase2_isolation_attestation_adapter import assess_isolation_attestation
from spira_core.nesira_phase2_signature_adapter import (
    FLOOR_ASSUMPTIONS,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
    assess_signature,
)


EXECUTION_MARKER = "ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION"
VERDICT_VALUES = {VERDICT_SUFFICIENT, VERDICT_INSUFFICIENT, VERDICT_NOT_EVALUATED}
DOMAINS = ("signature", "identity", "authority", "isolation")
FORBIDDEN_OUTPUT_KEYS = {
    "agent_" + "action",
    "combined_" + "verdict",
    "execute",
    "pro" + "ceed",
    "se" + "ver",
}


@dataclass(frozen=True)
class AssessmentWiringResult:
    verdict: str
    per_domain_breakdown: dict[str, str]
    sub_assessments: dict[str, dict[str, Any]]
    trust_roots_used: list[str]
    assumptions: list[str]
    checked_facts: list[str]
    gaps: list[str]
    not_evaluated_items: list[str]
    blocking_items: list[str]
    evidence_references: list[str]
    reason_codes: list[str]
    execution_marker: str = EXECUTION_MARKER

    def as_dict(self) -> dict[str, Any]:
        return {
            "verdict": self.verdict,
            "per_domain_breakdown": dict(self.per_domain_breakdown),
            "sub_assessments": {name: dict(value) for name, value in self.sub_assessments.items()},
            "trust_roots_used": list(self.trust_roots_used),
            "assumptions": list(self.assumptions),
            "checked_facts": list(self.checked_facts),
            "gaps": list(self.gaps),
            "not_evaluated_items": list(self.not_evaluated_items),
            "blocking_items": list(self.blocking_items),
            "evidence_references": list(self.evidence_references),
            "reason_codes": list(self.reason_codes),
            "execution_marker": self.execution_marker,
        }


def assess_phase2_wiring(request: Mapping[str, Any]) -> dict[str, Any]:
    expected_context = request.get("expected_context") if isinstance(request, Mapping) else None
    now_utc = request.get("now_utc") if isinstance(request, Mapping) else None
    if not isinstance(expected_context, Mapping):
        subresults = {
            domain: _malformed_sub_result(domain, "ASSESSMENT_WIRING_CALLER_CONTEXT_MALFORMED")
            for domain in DOMAINS
        }
        return compose_subresults(subresults).as_dict()

    shared_context = expected_context
    signature = _call_adapter(
        "signature",
        lambda: assess_signature(
            payload=request.get("signature_payload"),
            signature_evidence=request.get("signature_evidence"),
            declared_root=request.get("signature_root"),
            expected_context=shared_context,
            now_utc=_now(now_utc),
        ),
    )
    identity = _call_adapter(
        "identity",
        lambda: assess_identity(
            credential_evidence=request.get("identity_credential"),
            declared_root=request.get("identity_root"),
            expected_context=shared_context,
            now_utc=_now(now_utc),
        ),
    )
    authority = _call_adapter(
        "authority",
        lambda: assess_authority(
            policy_source=request.get("authority_policy_source"),
            declared_root=request.get("authority_root"),
            established_identity=_established_identity(shared_context),
            identity_sub_verdict=identity["sub_verdict"],
            expected_context=shared_context,
            now_utc=_now(now_utc),
        ),
    )
    isolation = _call_adapter(
        "isolation",
        lambda: assess_isolation_attestation(
            attestation_evidence=request.get("attestation_evidence"),
            declared_root=request.get("attestation_root"),
            expected_context=shared_context,
            now_utc=_now(now_utc),
        ),
    )
    return compose_subresults(
        {
            "signature": signature,
            "identity": identity,
            "authority": authority,
            "isolation": isolation,
        }
    ).as_dict()


def compose_subresults(subresults: Mapping[str, Mapping[str, Any]]) -> AssessmentWiringResult:
    sanitized = {domain: _sanitize_sub_result(domain, subresults.get(domain)) for domain in DOMAINS}
    breakdown = {domain: sanitized[domain]["sub_verdict"] for domain in DOMAINS}
    verdict = _compose_verdict(breakdown)
    return AssessmentWiringResult(
        verdict=verdict,
        per_domain_breakdown=breakdown,
        sub_assessments={domain: dict(sanitized[domain]) for domain in DOMAINS},
        trust_roots_used=_trust_roots_used(sanitized),
        assumptions=_assumptions(sanitized),
        checked_facts=_combined_items(sanitized, "reason_codes", evaluated_only=True),
        gaps=_combined_items(sanitized, "not_evaluated_items"),
        not_evaluated_items=_combined_items(sanitized, "not_evaluated_items"),
        blocking_items=_combined_items(sanitized, "blocking_items"),
        evidence_references=_combined_items(sanitized, "evidence_references"),
        reason_codes=_combined_items(sanitized, "reason_codes"),
    )


def _call_adapter(domain: str, func: Any) -> dict[str, Any]:
    try:
        return _sanitize_sub_result(domain, func())
    except Exception:
        return _malformed_sub_result(domain, "ASSESSMENT_WIRING_ADAPTER_EXCEPTION")


def _sanitize_sub_result(domain: str, result: Any) -> dict[str, Any]:
    if not isinstance(result, Mapping):
        return _malformed_sub_result(domain, "ASSESSMENT_WIRING_SUB_RESULT_MALFORMED")
    verdict = result.get("sub_verdict")
    if verdict not in VERDICT_VALUES:
        return _malformed_sub_result(domain, "ASSESSMENT_WIRING_SUB_RESULT_MALFORMED")
    if result.get("execution_marker") != EXECUTION_MARKER:
        return _malformed_sub_result(domain, "ASSESSMENT_WIRING_SUB_RESULT_MALFORMED")
    if _has_forbidden_semantics(result):
        return _malformed_sub_result(domain, "ASSESSMENT_WIRING_SUB_RESULT_MALFORMED")
    if not isinstance(result.get("assumption_ids"), list):
        return _malformed_sub_result(domain, "ASSESSMENT_WIRING_SUB_RESULT_MALFORMED")
    return {
        "sub_verdict": verdict,
        "declared_root_id": result.get("declared_root_id"),
        "declared_root_version": result.get("declared_root_version"),
        "assumption_ids": sorted(str(item) for item in result.get("assumption_ids", [])),
        "not_evaluated_items": _list_of_str(result.get("not_evaluated_items")),
        "blocking_items": _list_of_str(result.get("blocking_items")),
        "evidence_references": _list_of_str(result.get("evidence_references")),
        "reason_codes": _list_of_str(result.get("reason_codes")),
        "execution_marker": EXECUTION_MARKER,
    }


def _malformed_sub_result(domain: str, reason: str) -> dict[str, Any]:
    return {
        "sub_verdict": VERDICT_NOT_EVALUATED,
        "declared_root_id": None,
        "declared_root_version": None,
        "assumption_ids": list(FLOOR_ASSUMPTIONS),
        "not_evaluated_items": [f"{domain} sub-result malformed"],
        "blocking_items": [],
        "evidence_references": [],
        "reason_codes": [reason],
        "execution_marker": EXECUTION_MARKER,
    }


def _compose_verdict(breakdown: Mapping[str, str]) -> str:
    values = [breakdown[domain] for domain in DOMAINS]
    if all(value == VERDICT_SUFFICIENT for value in values):
        return VERDICT_SUFFICIENT
    if any(value == VERDICT_INSUFFICIENT for value in values):
        return VERDICT_INSUFFICIENT
    return VERDICT_NOT_EVALUATED


def _assumptions(subresults: Mapping[str, Mapping[str, Any]]) -> list[str]:
    values = set(FLOOR_ASSUMPTIONS)
    for domain in DOMAINS:
        result = subresults[domain]
        if result["sub_verdict"] != VERDICT_NOT_EVALUATED:
            values.update(str(item) for item in result.get("assumption_ids", []))
    return sorted(values)


def _trust_roots_used(subresults: Mapping[str, Mapping[str, Any]]) -> list[str]:
    roots = set()
    for result in subresults.values():
        root_id = result.get("declared_root_id")
        root_version = result.get("declared_root_version")
        if root_id is not None and root_version is not None:
            roots.add(f"{root_id}@{root_version}")
    return sorted(roots)


def _combined_items(
    subresults: Mapping[str, Mapping[str, Any]],
    key: str,
    *,
    evaluated_only: bool = False,
) -> list[str]:
    items: list[str] = []
    for domain in DOMAINS:
        result = subresults[domain]
        if evaluated_only and result["sub_verdict"] == VERDICT_NOT_EVALUATED:
            continue
        for item in result.get(key, []):
            items.append(f"{domain}:{item}")
    return sorted(items)


def _established_identity(expected_context: Mapping[str, Any]) -> dict[str, str] | None:
    value = expected_context.get("signer_identity")
    if not isinstance(value, str) or not value:
        return None
    return {"signer_identity": value}


def _now(value: Any) -> datetime | None:
    return value if isinstance(value, datetime) else None


def _list_of_str(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def _has_forbidden_semantics(result: Mapping[str, Any]) -> bool:
    stack: list[Any] = [result]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, value in current.items():
                if str(key).lower() in FORBIDDEN_OUTPUT_KEYS:
                    return True
                stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)
    return False
