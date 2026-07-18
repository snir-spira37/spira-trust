from __future__ import annotations

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


IDENTITY_SUFFICIENT_ASSUMPTIONS = sorted(
    {
        *FLOOR_ASSUMPTIONS,
        "PT-CRYPTO-02",
        "PT-IDENTITY-01",
        "PT-IDENTITY-02",
        "PT-REVOKE-01",
        "PT-REVOKE-02",
        "PT-META-03",
    }
)


@dataclass(frozen=True)
class IdentityAdapterResult:
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


def assess_identity(
    *,
    credential_evidence: Mapping[str, Any],
    declared_root: Mapping[str, Any] | None,
    expected_context: Mapping[str, Any],
    now_utc: datetime | None,
) -> dict[str, Any]:
    dependency_error = _cryptography_dependency_error()
    if dependency_error is not None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_CRYPTOGRAPHY_DEPENDENCY_UNAVAILABLE",
            "cryptography dependency unavailable or not pinned",
            extra_assumptions=["PT-CRYPTO-01"],
            details=[dependency_error],
        ).as_dict()

    if not isinstance(credential_evidence, Mapping):
        return _not_evaluated(
            declared_root,
            "IDENTITY_CREDENTIAL_MALFORMED",
            "identity credential evidence malformed",
        ).as_dict()
    if declared_root is None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_DECLARED_ROOT_MISSING",
            "declared identity root missing",
        ).as_dict()
    if not isinstance(declared_root, Mapping):
        return _not_evaluated(
            None,
            "IDENTITY_DECLARED_ROOT_MALFORMED",
            "declared identity root malformed",
        ).as_dict()
    if declared_root.get("ambiguous_identity_roots") is True:
        return _not_evaluated(
            declared_root,
            "IDENTITY_DECLARED_ROOT_AMBIGUOUS",
            "declared identity root ambiguous",
        ).as_dict()
    root_error = _root_shape_error(declared_root)
    if root_error is not None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_DECLARED_ROOT_MALFORMED",
            "declared identity root malformed or unsupported",
            details=[root_error],
        ).as_dict()
    if _clock_unavailable(now_utc):
        return _not_evaluated(
            declared_root,
            "IDENTITY_CLOCK_NOT_EVALUATED",
            "clock missing or untrusted",
            extra_assumptions=["PT-CLOCK-01"],
        ).as_dict()

    evidence_reference = str(credential_evidence.get("evidence_id", "identity_credential"))
    root_id = str(declared_root["trust_root_id"])
    root_version = str(declared_root["version"])

    if credential_evidence.get("credential_type") not in declared_root.get("accepted_credential_types", []):
        return _not_evaluated(
            declared_root,
            "IDENTITY_CREDENTIAL_TYPE_UNSUPPORTED",
            "identity credential type unsupported by declared root",
            evidence_references=[evidence_reference],
        ).as_dict()

    root_cert = _load_certificate(declared_root["root_cert_pem"])
    if root_cert is None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_DECLARED_ROOT_CERT_MALFORMED",
            "declared identity root certificate malformed",
            evidence_references=[evidence_reference],
        ).as_dict()
    leaf_cert = _load_certificate(credential_evidence.get("leaf_cert_pem"))
    if leaf_cert is None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_CREDENTIAL_MALFORMED",
            "identity credential certificate malformed",
            evidence_references=[evidence_reference],
        ).as_dict()
    intermediates = _load_certificate_list(credential_evidence.get("intermediate_certs_pem"))
    if intermediates is None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_INTERMEDIATE_CERT_MALFORMED",
            "identity intermediate certificate malformed",
            evidence_references=[evidence_reference],
        ).as_dict()

    context_error = _context_mismatch(credential_evidence, expected_context)
    if context_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_CONTEXT_MISMATCH",
            "identity credential context mismatch",
            [context_error],
            [evidence_reference],
        ).as_dict()
    namespace_error = _namespace_mismatch(credential_evidence, declared_root)
    if namespace_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_NAMESPACE_MISMATCH",
            "identity namespace mismatch",
            [namespace_error],
            [evidence_reference],
        ).as_dict()
    signer_error = _signer_identity_mismatch(credential_evidence, declared_root)
    if signer_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_SIGNER_MISMATCH",
            "identity signer mismatch",
            [signer_error],
            [evidence_reference],
        ).as_dict()
    binding_error = _signing_key_binding_mismatch(credential_evidence, declared_root)
    if binding_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_SIGNING_KEY_BINDING_MISMATCH",
            "identity credential does not bind expected signing key/root",
            [binding_error],
            [evidence_reference],
        ).as_dict()
    explicit_root_error = _explicit_root_mismatch(credential_evidence, declared_root)
    if explicit_root_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_DECLARED_ROOT_MISMATCH",
            "identity credential root does not match declared identity root",
            [explicit_root_error],
            [evidence_reference],
        ).as_dict()
    issuer_error = _issuer_mismatch(credential_evidence, declared_root)
    if issuer_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_UNTRUSTED_ISSUER",
            "identity issuer is not trusted under declared root policy",
            [issuer_error],
            [evidence_reference],
        ).as_dict()

    temporal_error = _temporal_error(declared_root, now_utc)
    if temporal_error is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_DECLARED_ROOT_EXPIRED",
            "declared identity root expired or not yet valid",
            [temporal_error],
            [evidence_reference],
        ).as_dict()

    revoked = _revoked_item(declared_root, credential_evidence)
    if revoked is not None:
        return _insufficient(
            declared_root,
            "IDENTITY_REVOCATION_REJECTED",
            "identity credential, intermediate, or root revoked",
            [revoked],
            [evidence_reference],
        ).as_dict()
    unknown_revocation = _unknown_revocation_item(declared_root, credential_evidence)
    if unknown_revocation is not None:
        return _not_evaluated(
            declared_root,
            "IDENTITY_REVOCATION_NOT_EVALUATED",
            "revocation status unknown, stale, unreachable, missing, or inconclusive",
            extra_assumptions=["PT-REVOKE-03"],
            details=[unknown_revocation],
            evidence_references=[evidence_reference],
        ).as_dict()

    chain_error = _verify_declared_chain(root_cert, leaf_cert, intermediates, now_utc)
    if chain_error is not None:
        if _chain_error_is_invalid_signature(chain_error):
            return _insufficient(
                declared_root,
                "IDENTITY_CREDENTIAL_SIGNATURE_INVALID",
                "identity credential certificate signature verification failed",
                [chain_error],
                [evidence_reference],
            ).as_dict()
        if _chain_error_is_expired(chain_error):
            return _insufficient(
                declared_root,
                "IDENTITY_CERTIFICATE_EXPIRED",
                "identity credential, intermediate, or root expired or not yet valid",
                [chain_error],
                [evidence_reference],
            ).as_dict()
        known_undeclared = _verifies_under_known_undeclared_root(credential_evidence, leaf_cert, intermediates, now_utc)
        if known_undeclared:
            return _insufficient(
                declared_root,
                "IDENTITY_KNOWN_UNDECLARED_ISSUER",
                "identity credential chains to a known but undeclared issuer/root",
                [chain_error],
                [evidence_reference],
            ).as_dict()
        return _not_evaluated(
            declared_root,
            "IDENTITY_CHAIN_NOT_EVALUATED",
            "identity certificate chain cannot be built from supplied evidence",
            details=[chain_error],
            evidence_references=[evidence_reference],
        ).as_dict()

    return IdentityAdapterResult(
        sub_verdict=VERDICT_SUFFICIENT,
        declared_root_id=root_id,
        declared_root_version=root_version,
        assumption_ids=IDENTITY_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[],
        evidence_references=[evidence_reference],
        reason_codes=["IDENTITY_BOUND_UNDER_DECLARED_ROOTS"],
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
        "root_cert_pem",
        "accepted_credential_types",
        "identity_namespace",
        "signer_identity_scope",
        "bound_signing_key_scope",
        "accepted_issuer_ids",
        "subject_scope",
        "environment_scope",
        "purpose_scope",
        "valid_from",
        "valid_until",
        "revocation",
    }
    missing = sorted(name for name in required if name not in root)
    if missing:
        return "missing fields: " + ",".join(missing)
    if root.get("trust_root_kind") != "IDENTITY_BINDING_CA":
        return "trust_root_kind is not IDENTITY_BINDING_CA"
    for field in (
        "accepted_credential_types",
        "signer_identity_scope",
        "bound_signing_key_scope",
        "accepted_issuer_ids",
        "subject_scope",
        "environment_scope",
        "purpose_scope",
    ):
        if not isinstance(root.get(field), list):
            return f"{field} is not a list"
    return None


def _clock_unavailable(now_utc: datetime | None) -> bool:
    if now_utc is None:
        return True
    return now_utc.tzinfo is None or now_utc.utcoffset() is None


def _context_mismatch(evidence: Mapping[str, Any], expected: Mapping[str, Any]) -> str | None:
    for field in ("subject", "environment", "purpose"):
        if field not in expected:
            return f"expected context missing {field}"
        if evidence.get(field) != expected[field]:
            return f"{field} mismatch"
    return None


def _namespace_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    if evidence.get("identity_namespace") != root.get("identity_namespace"):
        return "identity namespace mismatch"
    return None


def _signer_identity_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    signer = evidence.get("signer_identity")
    allowed = root.get("signer_identity_scope")
    if signer not in allowed:
        return "signer identity outside declared identity root scope"
    cert_signer = _certificate_common_name(evidence.get("leaf_cert_pem"))
    if cert_signer is None:
        return "signer identity missing from certificate subject"
    if cert_signer != signer:
        return "certificate subject does not match signer identity"
    return None


def _signing_key_binding_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    key_id = evidence.get("bound_signing_key_id")
    allowed = root.get("bound_signing_key_scope")
    if key_id not in allowed:
        return "bound signing key/root outside declared identity scope"
    return None


def _explicit_root_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    issuer_root = evidence.get("issuer_root_id")
    if issuer_root is None:
        return None
    if str(issuer_root) != str(root["trust_root_id"]):
        return "credential issuer root id differs from declared identity root"
    return None


def _issuer_mismatch(evidence: Mapping[str, Any], root: Mapping[str, Any]) -> str | None:
    issuers = root.get("accepted_issuer_ids")
    if evidence.get("issuer_id") not in issuers:
        return "identity issuer not accepted by declared root policy"
    return None


def _temporal_error(root: Mapping[str, Any], now_utc: datetime | None) -> str | None:
    assert now_utc is not None
    valid_from = _parse_utc(root["valid_from"])
    valid_until = _parse_utc(root["valid_until"])
    if valid_from is None or valid_until is None:
        return "validity window malformed"
    if now_utc < valid_from:
        return "declared identity root not yet valid"
    if now_utc > valid_until:
        return "declared identity root expired"
    return None


def _revoked_item(root: Mapping[str, Any], evidence: Mapping[str, Any]) -> str | None:
    for label, revocation in _revocation_items(root, evidence):
        if _revocation_status(revocation) == "REVOKED":
            return f"{label} revoked"
    return None


def _unknown_revocation_item(root: Mapping[str, Any], evidence: Mapping[str, Any]) -> str | None:
    for label, revocation in _revocation_items(root, evidence):
        if _revocation_status(revocation) != "GOOD_FRESH":
            return f"{label} revocation not fresh-good"
    return None


def _revocation_items(root: Mapping[str, Any], evidence: Mapping[str, Any]) -> list[tuple[str, Any]]:
    items = [
        ("declared identity root", root.get("revocation")),
        ("identity credential", evidence.get("revocation")),
    ]
    intermediates = evidence.get("intermediate_revocations", [])
    if isinstance(intermediates, list):
        for index, revocation in enumerate(intermediates):
            items.append((f"intermediate {index}", revocation))
    else:
        items.append(("intermediate revocation list", None))
    return items


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


def _verify_declared_chain(root_cert: Any, leaf_cert: Any, intermediates: list[Any], now_utc: datetime | None) -> str | None:
    assert now_utc is not None
    try:
        from cryptography.x509.verification import PolicyBuilder, Store

        verifier = PolicyBuilder().store(Store([root_cert])).time(now_utc).build_client_verifier()
        verifier.verify(leaf_cert, intermediates)
        return None
    except Exception as exc:
        return str(exc)


def _verifies_under_known_undeclared_root(
    evidence: Mapping[str, Any],
    leaf_cert: Any,
    intermediates: list[Any],
    now_utc: datetime | None,
) -> bool:
    assert now_utc is not None
    roots = _load_certificate_list(evidence.get("known_undeclared_roots_pem", []))
    if not roots:
        return False
    try:
        from cryptography.x509.verification import PolicyBuilder, Store

        for root in roots:
            try:
                PolicyBuilder().store(Store([root])).time(now_utc).build_client_verifier().verify(leaf_cert, intermediates)
                return True
            except Exception:
                continue
    except Exception:
        return False
    return False


def _chain_error_is_invalid_signature(error: str) -> bool:
    return "signature does not match" in error.lower()


def _chain_error_is_expired(error: str) -> bool:
    lowered = error.lower()
    return "not valid at validation time" in lowered or "expired" in lowered


def _load_certificate(value: Any) -> Any | None:
    if not isinstance(value, str):
        return None
    try:
        from cryptography import x509

        return x509.load_pem_x509_certificate(value.encode("ascii"))
    except Exception:
        return None


def _load_certificate_list(value: Any) -> list[Any] | None:
    if not isinstance(value, list):
        return None
    certs = []
    for item in value:
        cert = _load_certificate(item)
        if cert is None:
            return None
        certs.append(cert)
    return certs


def _certificate_common_name(leaf_cert_pem: Any) -> str | None:
    cert = _load_certificate(leaf_cert_pem)
    if cert is None:
        return None
    try:
        from cryptography.x509.oid import NameOID

        values = cert.subject.get_attributes_for_oid(NameOID.COMMON_NAME)
    except Exception:
        return None
    if len(values) != 1:
        return None
    return str(values[0].value)


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
) -> IdentityAdapterResult:
    not_evaluated = [item]
    if details:
        not_evaluated.extend(details)
    return IdentityAdapterResult(
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
) -> IdentityAdapterResult:
    return IdentityAdapterResult(
        sub_verdict=VERDICT_INSUFFICIENT,
        declared_root_id=_root_id(root),
        declared_root_version=_root_version(root),
        assumption_ids=IDENTITY_SUFFICIENT_ASSUMPTIONS,
        not_evaluated_items=[],
        blocking_items=[item, *blocking_items],
        evidence_references=evidence_references,
        reason_codes=[reason],
        crypto_dependency=_crypto_dependency(),
    )
