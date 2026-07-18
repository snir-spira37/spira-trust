from __future__ import annotations

import base64
import binascii
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Mapping


PINNED_CRYPTOGRAPHY_VERSION = "49.0.0"
PINNED_CRYPTOGRAPHY_WHEEL_SHA256 = "e5dfc1e64de5677cec922ffa8da89c546d0415bf6efdf081842e5d44c84e1f0e"
PINNED_TRANSITIVE_DEPENDENCIES = {
    "cffi": {
        "version": "2.1.0",
        "wheel_sha256": "c97f080ea627e2863524c5af3836e2270b5f5dfff1f104392b959f8df0c5d384",
    },
    "pycparser": {
        "version": "3.0",
        "wheel_sha256": "b727414169a36b7d524c1c3e31839a521725078d7b2ff038656844266160a992",
    },
}

VERDICT_SUFFICIENT = "TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS"
VERDICT_INSUFFICIENT = "TRUST_INSUFFICIENT"
VERDICT_NOT_EVALUATED = "TRUST_NOT_EVALUATED"

FLOOR_ASSUMPTIONS = [
    "PT-CRYPTO-01",
    "PT-CLOCK-01",
    "PT-META-01",
    "PT-META-02",
    "PT-META-04",
]

SIGNATURE_SUFFICIENT_ASSUMPTIONS = sorted(
    {
        *FLOOR_ASSUMPTIONS,
        "PT-CRYPTO-02",
        "PT-CRYPTO-03",
        "PT-KEYLEGIT-01",
        "PT-KEYLEGIT-02",
        "PT-REVOKE-01",
        "PT-REVOKE-02",
    }
)


@dataclass(frozen=True)
class SignatureAdapterResult:
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


def assess_signature(
    *,
    payload: bytes,
    signature_evidence: Mapping[str, Any],
    declared_root: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    now_utc: datetime | None,
) -> dict[str, Any]:
    dependency_error = _cryptography_dependency_error()
    if dependency_error is not None:
        return _not_evaluated(
            declared_root,
            "SIGNATURE_CRYPTOGRAPHY_DEPENDENCY_UNAVAILABLE",
            "cryptography dependency unavailable or not pinned",
            extra_assumptions=["PT-CRYPTO-01"],
            details=[dependency_error],
        ).as_dict()

    if not isinstance(payload, bytes):
        return _not_evaluated(
            declared_root,
            "SIGNATURE_PAYLOAD_MALFORMED",
            "payload is not bytes",
        ).as_dict()
    if not isinstance(signature_evidence, Mapping):
        return _not_evaluated(
            declared_root,
            "SIGNATURE_EVIDENCE_MALFORMED",
            "signature evidence malformed",
        ).as_dict()
    if declared_root is None:
        return _not_evaluated(
            declared_root,
            "SIGNATURE_DECLARED_ROOT_MISSING",
            "declared signing root missing",
        ).as_dict()
    root_error = _root_shape_error(declared_root)
    if root_error is not None:
        return _not_evaluated(
            declared_root,
            "SIGNATURE_DECLARED_ROOT_MALFORMED",
            "declared signing root malformed or unsupported",
            details=[root_error],
        ).as_dict()
    if _clock_unavailable(now_utc):
        return _not_evaluated(
            declared_root,
            "SIGNATURE_CLOCK_NOT_EVALUATED",
            "clock missing or untrusted",
            extra_assumptions=["PT-CLOCK-01"],
        ).as_dict()

    root_id = str(declared_root["trust_root_id"])
    root_version = str(declared_root["version"])
    evidence_reference = str(signature_evidence.get("evidence_id", "signature_evidence"))

    context_error = _context_mismatch(signature_evidence, expected_context)
    if context_error is not None:
        return _insufficient(
            declared_root,
            "SIGNATURE_CONTEXT_MISMATCH",
            "signature evidence context mismatch",
            [context_error],
            [evidence_reference],
        ).as_dict()

    scope_error = _scope_mismatch(signature_evidence, declared_root)
    if scope_error is not None:
        return _insufficient(
            declared_root,
            "SIGNATURE_ROOT_SCOPE_MISMATCH",
            "signature evidence outside declared signing root scope",
            [scope_error],
            [evidence_reference],
        ).as_dict()

    algorithm = signature_evidence.get("algorithm")
    if algorithm != "Ed25519" or algorithm not in declared_root.get("accepted_algorithms", []):
        return _not_evaluated(
            declared_root,
            "SIGNATURE_ALGORITHM_UNSUPPORTED",
            "signature algorithm unsupported by declared root",
            evidence_references=[evidence_reference],
        ).as_dict()

    if str(signature_evidence.get("key_id", "")) != str(declared_root["key_id"]):
        return _insufficient(
            declared_root,
            "SIGNATURE_DECLARED_ROOT_MISMATCH",
            "signature key does not match declared signing root",
            ["wrong declared signing root"],
            [evidence_reference],
        ).as_dict()

    temporal_error = _temporal_error(declared_root, now_utc)
    if temporal_error is not None:
        return _insufficient(
            declared_root,
            "SIGNATURE_DECLARED_ROOT_EXPIRED",
            "declared signing root expired or not yet valid",
            [temporal_error],
            [evidence_reference],
        ).as_dict()

    revocation_status = _revocation_status(declared_root)
    if revocation_status == "REVOKED":
        return _insufficient(
            declared_root,
            "SIGNATURE_DECLARED_ROOT_REVOKED",
            "declared signing root revoked",
            ["declared signing root revoked"],
            [evidence_reference],
        ).as_dict()
    if revocation_status != "GOOD_FRESH":
        return _not_evaluated(
            declared_root,
            "SIGNATURE_REVOCATION_NOT_EVALUATED",
            "revocation status unknown, stale, unreachable, or inconclusive",
            extra_assumptions=["PT-REVOKE-03"],
            evidence_references=[evidence_reference],
        ).as_dict()

    signature_bytes = _decode_signature(signature_evidence.get("signature_b64"))
    if signature_bytes is None:
        return _not_evaluated(
            declared_root,
            "SIGNATURE_BYTES_MALFORMED",
            "signature bytes malformed",
            evidence_references=[evidence_reference],
        ).as_dict()

    public_key = _load_public_key(declared_root["public_key_pem"])
    if public_key is None:
        return _not_evaluated(
            declared_root,
            "SIGNATURE_PUBLIC_KEY_MALFORMED",
            "declared public key malformed",
            evidence_references=[evidence_reference],
        ).as_dict()

    try:
        public_key.verify(signature_bytes, payload)
    except _invalid_signature_type():
        return _insufficient(
            declared_root,
            "SIGNATURE_INVALID",
            "signature verification failed",
            ["invalid signature"],
            [evidence_reference],
        ).as_dict()

    return SignatureAdapterResult(
        sub_verdict=VERDICT_SUFFICIENT,
        declared_root_id=root_id,
        declared_root_version=root_version,
        assumption_ids=SIGNATURE_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[],
        evidence_references=[evidence_reference],
        reason_codes=["SIGNATURE_VERIFIED_UNDER_DECLARED_ROOTS"],
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
        "key_id",
        "public_key_pem",
        "accepted_algorithms",
        "payload_class",
        "subject_scope",
        "environment_scope",
        "purpose_scope",
        "action_scope",
        "valid_from",
        "valid_until",
        "revocation",
    }
    missing = sorted(name for name in required if name not in root)
    if missing:
        return "missing fields: " + ",".join(missing)
    if root.get("trust_root_kind") != "SIGNING_KEY":
        return "trust_root_kind is not SIGNING_KEY"
    if not isinstance(root.get("accepted_algorithms"), list):
        return "accepted_algorithms is not a list"
    return None


def _clock_unavailable(now_utc: datetime | None) -> bool:
    if now_utc is None:
        return True
    return now_utc.tzinfo is None or now_utc.utcoffset() is None


def _context_mismatch(evidence: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    for field in ("payload_class", "subject", "environment", "purpose", "action"):
        if field not in expected:
            return f"expected context missing {field}"
        if evidence.get(field) != expected[field]:
            return f"{field} mismatch"
    return None


def _scope_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    if evidence.get("payload_class") != root.get("payload_class"):
        return "payload class out of scope"
    scope_fields = {
        "subject": "subject_scope",
        "environment": "environment_scope",
        "purpose": "purpose_scope",
        "action": "action_scope",
    }
    for evidence_field, root_field in scope_fields.items():
        allowed = root.get(root_field)
        if not isinstance(allowed, list) or evidence.get(evidence_field) not in allowed:
            return f"{evidence_field} out of scope"
    return None


def _temporal_error(root: Mapping[str, Any], now_utc: datetime | None) -> str | None:
    assert now_utc is not None
    valid_from = _parse_utc(root["valid_from"])
    valid_until = _parse_utc(root["valid_until"])
    if valid_from is None or valid_until is None:
        return "validity window malformed"
    if now_utc < valid_from:
        return "declared signing root not yet valid"
    if now_utc > valid_until:
        return "declared signing root expired"
    return None


def _revocation_status(root: Mapping[str, Any]) -> str:
    revocation = root.get("revocation")
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
) -> SignatureAdapterResult:
    not_evaluated = [item]
    if details:
        not_evaluated.extend(details)
    return SignatureAdapterResult(
        sub_verdict=VERDICT_NOT_EVALUATED,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=sorted({*FLOOR_ASSUMPTIONS, *(extra_assumptions or [])}),
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
) -> SignatureAdapterResult:
    return SignatureAdapterResult(
        sub_verdict=VERDICT_INSUFFICIENT,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=SIGNATURE_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[item, *blocking_items],
        evidence_references=evidence_references,
        reason_codes=[reason],
        crypto_dependency=_crypto_dependency(),
    )
