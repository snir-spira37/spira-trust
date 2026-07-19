from __future__ import annotations

import base64
import binascii
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping

from spira_core.nesira_phase2_signature_adapter import (
    FLOOR_ASSUMPTIONS,
    PINNED_CRYPTOGRAPHY_VERSION,
    PINNED_CRYPTOGRAPHY_WHEEL_SHA256,
    PINNED_TRANSITIVE_DEPENDENCIES,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
)


ISOLATION_CAVEAT = "PT-ISOLATION-01"

ATTESTATION_FLOOR_ASSUMPTIONS = sorted({*FLOOR_ASSUMPTIONS, ISOLATION_CAVEAT})

ATTESTATION_SUFFICIENT_ASSUMPTIONS = sorted(
    {
        *ATTESTATION_FLOOR_ASSUMPTIONS,
        "PT-CRYPTO-02",
        "PT-CRYPTO-03",
        "PT-ISOLATION-02",
        "PT-ISOLATION-03",
        "PT-REVOKE-01",
        "PT-REVOKE-02",
    }
)


@dataclass(frozen=True)
class AttestationAdapterResult:
    sub_verdict: str
    declared_root_id: str | None
    declared_root_version: str | None
    assumption_ids: list[str]
    not_evaluated_items: list[str]
    blocking_items: list[str]
    evidence_references: list[str]
    reason_codes: list[str]
    crypto_dependency: dict[str, Any]
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
            "crypto_dependency": dict(self.crypto_dependency),
            "execution_marker": self.execution_marker,
        }


def assess_isolation_attestation(
    *,
    attestation_evidence: Mapping[str, Any] | None,
    declared_root: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    now_utc: datetime | None,
) -> dict[str, Any]:
    dependency_error = _cryptography_dependency_error()
    if dependency_error is not None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_CRYPTOGRAPHY_DEPENDENCY_UNAVAILABLE",
            "cryptography dependency unavailable or not pinned",
            extra_assumptions=["PT-CRYPTO-01"],
            details=[dependency_error],
        ).as_dict()
    if declared_root is None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_DECLARED_AUTHORITY_MISSING",
            "declared attestation authority missing",
        ).as_dict()
    if not isinstance(declared_root, Mapping):
        return _not_evaluated(
            None,
            "ATTESTATION_DECLARED_AUTHORITY_MALFORMED",
            "declared attestation authority malformed",
        ).as_dict()
    if declared_root.get("ambiguous_attestation_authorities") is True:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_DECLARED_AUTHORITY_AMBIGUOUS",
            "declared attestation authority ambiguous",
        ).as_dict()
    root_error = _root_shape_error(declared_root)
    if root_error is not None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_DECLARED_AUTHORITY_MALFORMED",
            "declared attestation authority malformed or unsupported",
            details=[root_error],
        ).as_dict()
    if _clock_unavailable(now_utc):
        return _not_evaluated(
            declared_root,
            "ATTESTATION_CLOCK_NOT_EVALUATED",
            "clock missing or untrusted",
            extra_assumptions=["PT-CLOCK-01"],
        ).as_dict()
    if attestation_evidence is None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_EVIDENCE_MISSING",
            "attestation evidence missing or unreadable",
        ).as_dict()
    if not isinstance(attestation_evidence, Mapping):
        return _not_evaluated(
            declared_root,
            "ATTESTATION_EVIDENCE_MALFORMED",
            "attestation evidence malformed",
        ).as_dict()

    evidence_reference = str(attestation_evidence.get("evidence_id", "attestation_evidence"))
    evidence_error = _evidence_shape_error(attestation_evidence)
    if evidence_error is not None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_EVIDENCE_MALFORMED",
            "attestation evidence malformed",
            details=[evidence_error],
            evidence_references=[evidence_reference],
        ).as_dict()

    attestation_type = attestation_evidence.get("attestation_type")
    if attestation_type not in declared_root["accepted_attestation_types"]:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_TYPE_UNSUPPORTED",
            "attestation type unsupported by declared authority",
            evidence_references=[evidence_reference],
        ).as_dict()

    algorithm = attestation_evidence.get("algorithm")
    if algorithm != "Ed25519" or algorithm not in declared_root["accepted_algorithms"]:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_ALGORITHM_UNSUPPORTED",
            "attestation algorithm unsupported by declared authority",
            evidence_references=[evidence_reference],
        ).as_dict()

    authority_mismatch = _authority_mismatch(attestation_evidence, declared_root)
    if authority_mismatch is not None:
        return _insufficient(
            declared_root,
            "ATTESTATION_DECLARED_AUTHORITY_MISMATCH",
            "attestation authority does not match declared root",
            [authority_mismatch],
            [evidence_reference],
        ).as_dict()

    scope_error = _scope_mismatch(attestation_evidence, declared_root, expected_context)
    if scope_error is not None:
        return _insufficient(
            declared_root,
            "ATTESTATION_DECLARED_AUTHORITY_SCOPE_MISMATCH",
            "attestation outside declared authority scope",
            [scope_error],
            [evidence_reference],
        ).as_dict()

    claim_error = _claim_mismatch(attestation_evidence, expected_context)
    if claim_error is not None:
        return _insufficient(
            declared_root,
            "ATTESTATION_CLAIMS_MISMATCH",
            "attestation claims do not bind expected profile",
            [claim_error],
            [evidence_reference],
        ).as_dict()

    temporal_error = _temporal_error(declared_root, attestation_evidence, now_utc)
    if temporal_error is not None:
        return _insufficient(
            declared_root,
            "ATTESTATION_TEMPORAL_INVALID",
            "attestation or declared authority expired or not yet valid",
            [temporal_error],
            [evidence_reference],
        ).as_dict()

    revoked = _revoked_item(declared_root, attestation_evidence)
    if revoked is not None:
        return _insufficient(
            declared_root,
            "ATTESTATION_REVOKED",
            "attestation authority or attestation revoked",
            [revoked],
            [evidence_reference],
        ).as_dict()
    unknown_revocation = _unknown_revocation_item(declared_root, attestation_evidence)
    if unknown_revocation is not None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_REVOCATION_NOT_EVALUATED",
            "revocation status unknown, stale, unreachable, missing, or inconclusive",
            extra_assumptions=["PT-REVOKE-03"],
            details=[unknown_revocation],
            evidence_references=[evidence_reference],
        ).as_dict()

    public_key = _load_public_key(declared_root["public_key_pem"])
    if public_key is None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_DECLARED_PUBLIC_KEY_MALFORMED",
            "declared attestation public key malformed",
            evidence_references=[evidence_reference],
        ).as_dict()
    signature_bytes = _decode_signature(attestation_evidence.get("signature_b64"))
    if signature_bytes is None:
        return _not_evaluated(
            declared_root,
            "ATTESTATION_SIGNATURE_BYTES_MALFORMED",
            "attestation signature bytes malformed",
            evidence_references=[evidence_reference],
        ).as_dict()

    payload_bytes = _payload_bytes(attestation_evidence["attestation_payload"])
    try:
        public_key.verify(signature_bytes, payload_bytes)
    except _invalid_signature_type():
        return _insufficient(
            declared_root,
            "ATTESTATION_SIGNATURE_INVALID",
            "attestation signature verification failed",
            ["invalid attestation signature"],
            [evidence_reference],
        ).as_dict()

    return AttestationAdapterResult(
        sub_verdict=VERDICT_SUFFICIENT,
        declared_root_id=_root_id(declared_root),
        declared_root_version=_root_version(declared_root),
        assumption_ids=ATTESTATION_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[],
        evidence_references=[evidence_reference],
        reason_codes=["ATTESTATION_VERIFIED_UNDER_DECLARED_AUTHORITY"],
        crypto_dependency=_crypto_dependency(),
    ).as_dict()


def _cryptography_dependency_error() -> str | None:
    try:
        import cryptography
    except Exception as exc:
        return f"import failed: {type(exc).__name__}"
    if cryptography.__version__ != PINNED_CRYPTOGRAPHY_VERSION:
        return f"version mismatch: {cryptography.__version__}"
    return None


def _crypto_dependency() -> dict[str, Any]:
    return {
        "name": "cryptography",
        "version": PINNED_CRYPTOGRAPHY_VERSION,
        "wheel_sha256": PINNED_CRYPTOGRAPHY_WHEEL_SHA256,
        "transitive_dependencies": PINNED_TRANSITIVE_DEPENDENCIES,
    }


def _root_shape_error(root: Mapping[str, Any]) -> str | None:
    required = {
        "trust_root_id",
        "version",
        "trust_root_kind",
        "authority_id",
        "public_key_pem",
        "accepted_algorithms",
        "accepted_attestation_types",
        "candidate_scope",
        "environment_scope",
        "profile_scope",
        "valid_from",
        "valid_until",
        "revocation",
    }
    missing = sorted(name for name in required if name not in root)
    if missing:
        return "missing fields: " + ",".join(missing)
    if root.get("trust_root_kind") != "ATTESTATION_AUTHORITY":
        return "trust_root_kind is not ATTESTATION_AUTHORITY"
    for field in ("accepted_algorithms", "accepted_attestation_types", "candidate_scope", "environment_scope", "profile_scope"):
        if not isinstance(root.get(field), list):
            return f"{field} is not a list"
    return None


def _evidence_shape_error(evidence: Mapping[str, Any]) -> str | None:
    required = {
        "evidence_id",
        "attestation_type",
        "authority_id",
        "authority_root_id",
        "authority_root_version",
        "algorithm",
        "signature_b64",
        "attestation_payload",
        "valid_from",
        "valid_until",
        "revocation",
    }
    missing = sorted(name for name in required if name not in evidence)
    if missing:
        return "missing fields: " + ",".join(missing)
    if not isinstance(evidence.get("attestation_payload"), Mapping):
        return "attestation_payload is not a mapping"
    return None


def _clock_unavailable(now_utc: datetime | None) -> bool:
    if now_utc is None:
        return True
    return now_utc.tzinfo is None or now_utc.utcoffset() is None


def _authority_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    if str(evidence.get("authority_root_id")) != str(root.get("trust_root_id")):
        return "attestation authority root id differs from declared root"
    if str(evidence.get("authority_root_version")) != str(root.get("version")):
        return "attestation authority root version differs from declared root"
    if str(evidence.get("authority_id")) != str(root.get("authority_id")):
        return "attestation authority id differs from declared root"
    return None


def _scope_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    payload = evidence["attestation_payload"]
    checks = {
        "candidate": ("candidate_id", "candidate_scope"),
        "environment": ("environment_id", "environment_scope"),
        "profile": ("profile_id", "profile_scope"),
    }
    for label, (payload_field, root_field) in checks.items():
        expected_value = expected.get(payload_field)
        if expected_value is None:
            return f"expected context missing {payload_field}"
        allowed = root.get(root_field)
        if payload.get(payload_field) not in allowed or expected_value not in allowed:
            return f"{label} out of declared authority scope"
    return None


def _claim_mismatch(evidence: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    payload = evidence["attestation_payload"]
    for field in ("candidate_id", "candidate_hash", "environment_id", "profile_id", "profile_version"):
        if field not in expected:
            return f"expected context missing {field}"
        if payload.get(field) != expected[field]:
            return f"{field} claim mismatch"
    return None


def _temporal_error(root: Mapping[str, Any], evidence: Mapping[str, Any], now_utc: datetime | None) -> str | None:
    assert now_utc is not None
    for label, item in (("declared authority", root), ("attestation", evidence)):
        valid_from = _parse_utc(item["valid_from"])
        valid_until = _parse_utc(item["valid_until"])
        if valid_from is None or valid_until is None:
            return f"{label} validity window malformed"
        if now_utc < valid_from:
            return f"{label} not yet valid"
        if now_utc > valid_until:
            return f"{label} expired"
    return None


def _revoked_item(root: Mapping[str, Any], evidence: Mapping[str, Any]) -> str | None:
    for label, item in (("declared attestation authority", root), ("attestation", evidence)):
        revocation = item.get("revocation")
        if isinstance(revocation, Mapping) and str(revocation.get("status", "")).upper() == "REVOKED":
            return f"{label} revoked"
    return None


def _unknown_revocation_item(root: Mapping[str, Any], evidence: Mapping[str, Any]) -> str | None:
    for label, item in (("declared attestation authority", root), ("attestation", evidence)):
        if _revocation_status(item) != "GOOD_FRESH":
            return f"{label} revocation not fresh-good"
    return None


def _revocation_status(item: Mapping[str, Any]) -> str:
    revocation = item.get("revocation")
    if not isinstance(revocation, Mapping):
        return "UNKNOWN"
    status = str(revocation.get("status", "UNKNOWN")).upper()
    freshness = str(revocation.get("freshness", "UNKNOWN")).upper()
    if status == "REVOKED":
        return "REVOKED"
    if status == "GOOD" and freshness == "FRESH":
        return "GOOD_FRESH"
    return "UNKNOWN"


def _decode_signature(value: Any) -> bytes | None:
    if not isinstance(value, str):
        return None
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error):
        return None


def _payload_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _load_public_key(public_key_pem: Any) -> Any | None:
    if not isinstance(public_key_pem, str):
        return None
    try:
        from cryptography.hazmat.primitives import serialization
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

        public_key = serialization.load_pem_public_key(public_key_pem.encode("ascii"))
        if not isinstance(public_key, Ed25519PublicKey):
            return None
        return public_key
    except Exception:
        return None


def _invalid_signature_type() -> type[Exception]:
    from cryptography.exceptions import InvalidSignature

    return InvalidSignature


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


def _not_evaluated(
    root: Mapping[str, Any] | None,
    reason: str,
    item: str,
    *,
    extra_assumptions: list[str] | None = None,
    details: list[str] | None = None,
    evidence_references: list[str] | None = None,
) -> AttestationAdapterResult:
    not_evaluated = [item]
    if details:
        not_evaluated.extend(details)
    return AttestationAdapterResult(
        sub_verdict=VERDICT_NOT_EVALUATED,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=sorted({*ATTESTATION_FLOOR_ASSUMPTIONS, *(extra_assumptions or [])}),
        not_evaluated_items=not_evaluated,
        blocking_items=[],
        evidence_references=evidence_references or [],
        reason_codes=[reason],
        crypto_dependency=_crypto_dependency(),
    )


def _insufficient(
    root: Mapping[str, Any],
    reason: str,
    item: str,
    blocking_items: list[str],
    evidence_references: list[str],
) -> AttestationAdapterResult:
    return AttestationAdapterResult(
        sub_verdict=VERDICT_INSUFFICIENT,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=ATTESTATION_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[item, *blocking_items],
        evidence_references=evidence_references,
        reason_codes=[reason],
        crypto_dependency=_crypto_dependency(),
    )
