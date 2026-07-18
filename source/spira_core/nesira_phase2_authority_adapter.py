from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from spira_core.nesira_phase2_signature_adapter import (
    FLOOR_ASSUMPTIONS,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
)


AUTHORITY_SUFFICIENT_ASSUMPTIONS = sorted(
    {
        *FLOOR_ASSUMPTIONS,
        "PT-AUTHORITY-01",
        "PT-AUTHORITY-02",
        "PT-REVOKE-01",
        "PT-REVOKE-02",
    }
)


@dataclass(frozen=True)
class AuthorityAdapterResult:
    sub_verdict: str
    declared_root_id: str | None
    declared_root_version: str | None
    assumption_ids: list[str]
    not_evaluated_items: list[str]
    blocking_items: list[str]
    evidence_references: list[str]
    reason_codes: list[str]
    dependency_boundary: dict[str, Any]
    execution_marker: str = "ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION"

    def as_dict(self) -> dict[str, Any]:
        return {
            "sub_verdict": self.sub_verdict,
            "declared_root_id": self.declared_root_id,
            "declared_root_version": self.declared_root_version,
            "assumption_ids": sorted(self.assumption_ids),
            "not_evaluated_items": list(self.not_evaluated_items),
            "blocking_items": list(self.blocking_items),
            "evidence_references": list(self.evidence_references),
            "reason_codes": list(self.reason_codes),
            "dependency_boundary": dict(self.dependency_boundary),
            "execution_marker": self.execution_marker,
        }


def assess_authority(
    *,
    policy_source: Mapping[str, Any] | None,
    declared_root: Mapping[str, Any] | None,
    established_identity: Mapping[str, Any] | None,
    identity_sub_verdict: str,
    expected_context: Mapping[str, Any],
    now_utc: datetime | None,
) -> dict[str, Any]:
    if declared_root is None:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_DECLARED_ROOT_MISSING",
            "declared authority policy root missing",
        ).as_dict()
    if not isinstance(declared_root, Mapping):
        return _not_evaluated(
            None,
            "AUTHORITY_DECLARED_ROOT_MALFORMED",
            "declared authority policy root malformed",
        ).as_dict()
    if declared_root.get("ambiguous_authority_roots") is True:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_DECLARED_ROOT_AMBIGUOUS",
            "declared authority policy root ambiguous",
        ).as_dict()
    root_error = _root_shape_error(declared_root)
    if root_error is not None:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_DECLARED_ROOT_MALFORMED",
            "declared authority policy root malformed or unsupported",
            details=[root_error],
        ).as_dict()
    if _clock_unavailable(now_utc):
        return _not_evaluated(
            declared_root,
            "AUTHORITY_CLOCK_NOT_EVALUATED",
            "clock missing or untrusted",
            extra_assumptions=["PT-CLOCK-01"],
        ).as_dict()
    if identity_sub_verdict != VERDICT_SUFFICIENT:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_IDENTITY_NOT_EVALUATED",
            "identity sub-verdict is not sufficient",
        ).as_dict()
    identity_error = _identity_error(established_identity)
    if identity_error is not None:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_ESTABLISHED_IDENTITY_MISSING",
            "established signer identity missing or malformed",
            details=[identity_error],
        ).as_dict()
    if policy_source is None:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_POLICY_SOURCE_MISSING",
            "authority policy source missing or unreadable",
        ).as_dict()
    if not isinstance(policy_source, Mapping):
        return _not_evaluated(
            declared_root,
            "AUTHORITY_POLICY_SOURCE_MALFORMED",
            "authority policy source malformed",
        ).as_dict()

    evidence_reference = str(policy_source.get("evidence_id", "authority_policy"))
    policy_error = _policy_shape_error(policy_source)
    if policy_error is not None:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_POLICY_SOURCE_MALFORMED",
            "authority policy source malformed",
            details=[policy_error],
            evidence_references=[evidence_reference],
        ).as_dict()

    if policy_source.get("policy_type") not in declared_root["accepted_policy_types"]:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_POLICY_TYPE_UNSUPPORTED",
            "authority policy type unsupported by declared root",
            evidence_references=[evidence_reference],
        ).as_dict()

    root_mismatch = _policy_root_mismatch(policy_source, declared_root)
    if root_mismatch is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_POLICY_ROOT_MISMATCH",
            "authority policy root id/version mismatch",
            [root_mismatch],
            [evidence_reference],
        ).as_dict()

    context_error = _context_mismatch(policy_source, expected_context)
    if context_error is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_CONTEXT_MISMATCH",
            "authority policy context mismatch",
            [context_error],
            [evidence_reference],
        ).as_dict()

    scope_error = _scope_mismatch(policy_source, declared_root, expected_context)
    if scope_error is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_POLICY_SCOPE_MISMATCH",
            "authority policy scope mismatch",
            [scope_error],
            [evidence_reference],
        ).as_dict()

    version_error = _policy_version_error(policy_source, expected_context)
    if version_error is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_POLICY_VERSION_MISMATCH",
            "authority policy version mismatch or stale",
            [version_error],
            [evidence_reference],
        ).as_dict()

    temporal_error = _temporal_error(declared_root, policy_source, now_utc)
    if temporal_error is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_POLICY_TEMPORAL_INVALID",
            "authority policy source expired or not yet valid",
            [temporal_error],
            [evidence_reference],
        ).as_dict()

    revoked = _revoked_item(declared_root, policy_source)
    if revoked is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_POLICY_REVOKED",
            "authority policy root or source revoked",
            [revoked],
            [evidence_reference],
        ).as_dict()
    unknown_revocation = _unknown_revocation_item(declared_root, policy_source)
    if unknown_revocation is not None:
        return _not_evaluated(
            declared_root,
            "AUTHORITY_REVOCATION_NOT_EVALUATED",
            "revocation status unknown, stale, unreachable, missing, or inconclusive",
            extra_assumptions=["PT-REVOKE-03"],
            details=[unknown_revocation],
            evidence_references=[evidence_reference],
        ).as_dict()

    signer_identity = str(established_identity["signer_identity"])
    request = _request(expected_context, policy_source)
    deny_match = _matching_entry(policy_source["deny"], signer_identity, request)
    if deny_match is not None:
        return _insufficient(
            declared_root,
            "AUTHORITY_EXPLICIT_DENY",
            "signer identity explicitly denied by authority policy",
            [f"deny entry: {deny_match}"],
            [evidence_reference],
        ).as_dict()

    identity_present = _identity_present(policy_source, signer_identity)
    if not identity_present:
        return _insufficient(
            declared_root,
            "AUTHORITY_IDENTITY_ABSENT_FROM_POLICY",
            "signer identity absent from consultable authority policy",
            [signer_identity],
            [evidence_reference],
        ).as_dict()

    allow_match = _matching_entry(policy_source["allow"], signer_identity, request)
    if allow_match is None:
        return _insufficient(
            declared_root,
            "AUTHORITY_ACTION_NOT_ALLOWED",
            "signer identity present but action is not explicitly allowed",
            [signer_identity],
            [evidence_reference],
        ).as_dict()

    return AuthorityAdapterResult(
        sub_verdict=VERDICT_SUFFICIENT,
        declared_root_id=_root_id(declared_root),
        declared_root_version=_root_version(declared_root),
        assumption_ids=AUTHORITY_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[],
        evidence_references=[evidence_reference],
        reason_codes=["AUTHORITY_EXPLICIT_ALLOW_UNDER_DECLARED_ROOTS"],
        dependency_boundary=_dependency_boundary(),
    ).as_dict()


def _root_shape_error(root: Mapping[str, Any]) -> str | None:
    required = {
        "trust_root_id",
        "version",
        "trust_root_kind",
        "accepted_policy_types",
        "subject_scope",
        "environment_scope",
        "purpose_scope",
        "action_scope",
        "policy_version_scope",
        "valid_from",
        "valid_until",
        "revocation",
    }
    missing = sorted(name for name in required if name not in root)
    if missing:
        return "missing fields: " + ",".join(missing)
    if root.get("trust_root_kind") != "AUTHORITY_POLICY_SOURCE":
        return "trust_root_kind is not AUTHORITY_POLICY_SOURCE"
    for field in (
        "accepted_policy_types",
        "subject_scope",
        "environment_scope",
        "purpose_scope",
        "action_scope",
        "policy_version_scope",
    ):
        if not isinstance(root.get(field), list):
            return f"{field} is not a list"
    return None


def _policy_shape_error(policy: Mapping[str, Any]) -> str | None:
    required = {
        "authority_root_id",
        "authority_root_version",
        "policy_type",
        "policy_id",
        "policy_version",
        "subject",
        "environment",
        "purpose",
        "action",
        "valid_from",
        "valid_until",
        "revocation",
        "allow",
        "deny",
    }
    missing = sorted(name for name in required if name not in policy)
    if missing:
        return "missing fields: " + ",".join(missing)
    if not isinstance(policy.get("allow"), list):
        return "allow is not a list"
    if not isinstance(policy.get("deny"), list):
        return "deny is not a list"
    return None


def _identity_error(identity: Mapping[str, Any] | None) -> str | None:
    if not isinstance(identity, Mapping):
        return "established identity is not a mapping"
    value = identity.get("signer_identity")
    if not isinstance(value, str) or not value:
        return "signer_identity missing"
    return None


def _clock_unavailable(now_utc: datetime | None) -> bool:
    if now_utc is None:
        return True
    return now_utc.tzinfo is None or now_utc.utcoffset() is None


def _policy_root_mismatch(policy: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    if str(policy["authority_root_id"]) != str(root["trust_root_id"]):
        return "policy authority root id differs from declared root"
    if str(policy["authority_root_version"]) != str(root["version"]):
        return "policy authority root version differs from declared root"
    return None


def _context_mismatch(policy: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    for field in ("subject", "environment", "purpose", "action"):
        if field not in expected:
            return f"expected context missing {field}"
        if policy.get(field) != expected[field]:
            return f"{field} mismatch"
    return None


def _scope_mismatch(policy: Mapping[str, Any], root: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    scope_fields = {
        "subject": "subject_scope",
        "environment": "environment_scope",
        "purpose": "purpose_scope",
        "action": "action_scope",
        "policy_version": "policy_version_scope",
    }
    for context_field, root_field in scope_fields.items():
        value = policy.get(context_field, expected.get(context_field))
        allowed = root.get(root_field)
        if value not in allowed:
            return f"{context_field} out of declared authority root scope"
    return None


def _policy_version_error(policy: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    expected_version = expected.get("policy_version")
    if expected_version is None:
        return "expected policy version missing"
    if policy.get("policy_version") != expected_version:
        return "policy version mismatch"
    return None


def _temporal_error(root: Mapping[str, Any], policy: Mapping[str, Any], now_utc: datetime | None) -> str | None:
    assert now_utc is not None
    for label, item in (("declared authority root", root), ("authority policy source", policy)):
        valid_from = _parse_utc(item["valid_from"])
        valid_until = _parse_utc(item["valid_until"])
        if valid_from is None or valid_until is None:
            return f"{label} validity window malformed"
        if now_utc < valid_from:
            return f"{label} not yet valid"
        if now_utc > valid_until:
            return f"{label} expired"
    return None


def _revoked_item(root: Mapping[str, Any], policy: Mapping[str, Any]) -> str | None:
    for label, revocation in _revocation_items(root, policy):
        if _revocation_status(revocation) == "REVOKED":
            return f"{label} revoked"
    return None


def _unknown_revocation_item(root: Mapping[str, Any], policy: Mapping[str, Any]) -> str | None:
    for label, revocation in _revocation_items(root, policy):
        if _revocation_status(revocation) != "GOOD_FRESH":
            return f"{label} revocation not fresh-good"
    return None


def _revocation_items(root: Mapping[str, Any], policy: Mapping[str, Any]) -> list[tuple[str, Any]]:
    return [
        ("declared authority root", root.get("revocation")),
        ("authority policy source", policy.get("revocation")),
    ]


def _revocation_status(revocation: Any) -> str:
    if not isinstance(revocation, Mapping):
        return "UNKNOWN"
    status = str(revocation.get("status", "UNKNOWN")).upper()
    freshness = str(revocation.get("freshness", "UNKNOWN")).upper()
    if status == "REVOKED":
        return "REVOKED"
    if status == "GOOD" and freshness == "FRESH":
        return "GOOD_FRESH"
    return "UNKNOWN"


def _request(expected: Mapping[str, Any], policy: Mapping[str, Any]) -> dict[str, str]:
    return {
        "subject": str(expected["subject"]),
        "environment": str(expected["environment"]),
        "purpose": str(expected["purpose"]),
        "action": str(expected["action"]),
        "policy_version": str(policy["policy_version"]),
    }


def _identity_present(policy: Mapping[str, Any], signer_identity: str) -> bool:
    entries = list(policy["allow"]) + list(policy["deny"])
    return any(isinstance(entry, Mapping) and entry.get("signer_identity") == signer_identity for entry in entries)


def _matching_entry(entries: list[Any], signer_identity: str, request: Mapping[str, str]) -> str | None:
    for index, entry in enumerate(entries):
        if not isinstance(entry, Mapping):
            continue
        if entry.get("signer_identity") != signer_identity:
            continue
        if all(entry.get(field) == request[field] for field in ("subject", "environment", "purpose", "action", "policy_version")):
            return str(entry.get("entry_id", f"entry-{index}"))
    return None


def _parse_utc(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        return None
    return parsed.astimezone(timezone.utc)


def _root_id(root: Mapping[str, Any] | None) -> str | None:
    if not isinstance(root, Mapping):
        return None
    value = root.get("trust_root_id")
    return str(value) if value is not None else None


def _root_version(root: Mapping[str, Any] | None) -> str | None:
    if not isinstance(root, Mapping):
        return None
    value = root.get("version")
    return str(value) if value is not None else None


def _dependency_boundary() -> dict[str, Any]:
    return {
        "new_dependencies": [],
        "crypto_verification_performed": False,
        "identity_verification_performed": False,
    }


def _not_evaluated(
    root: Mapping[str, Any] | None,
    reason: str,
    item: str,
    *,
    extra_assumptions: list[str] | None = None,
    details: list[str] | None = None,
    evidence_references: list[str] | None = None,
) -> AuthorityAdapterResult:
    not_evaluated = [item]
    if details:
        not_evaluated.extend(details)
    return AuthorityAdapterResult(
        sub_verdict=VERDICT_NOT_EVALUATED,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=sorted({*FLOOR_ASSUMPTIONS, *(extra_assumptions or [])}),
        not_evaluated_items=not_evaluated,
        blocking_items=[],
        evidence_references=evidence_references or [],
        reason_codes=[reason],
        dependency_boundary=_dependency_boundary(),
    )


def _insufficient(
    root: Mapping[str, Any],
    reason: str,
    item: str,
    blocking_items: list[str],
    evidence_references: list[str],
) -> AuthorityAdapterResult:
    return AuthorityAdapterResult(
        sub_verdict=VERDICT_INSUFFICIENT,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=AUTHORITY_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[item, *blocking_items],
        evidence_references=evidence_references,
        reason_codes=[reason],
        dependency_boundary=_dependency_boundary(),
    )
