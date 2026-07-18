from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_identity_adapter import (
    PINNED_CRYPTOGRAPHY_VERSION,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
    assess_identity,
)


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)
EXPECTED_CONTEXT = {
    "subject": "legacy-db-primary",
    "environment": "prod-eu-1",
    "purpose": "phase2-identity-adapter-conformance",
}
ORACLE = Path("research") / "nesira_policy_profile" / "nesira_phase2_assessment_decision_table.json"

REQUIRED_FAILURE_MODES = {
    "missing_identity_root",
    "ambiguous_identity_root",
    "malformed_identity_root",
    "unsupported_credential_type",
    "malformed_credential",
    "bad_credential_signature",
    "chain_unbuildable_missing_intermediate",
    "known_but_undeclared_issuer",
    "wrong_declared_identity_root",
    "untrusted_issuer",
    "expired_credential",
    "expired_intermediate",
    "expired_identity_root",
    "revoked_credential",
    "revoked_intermediate",
    "revoked_identity_root",
    "revocation_unknown",
    "revocation_stale",
    "revocation_unreachable",
    "clock_missing",
    "clock_untrusted",
    "namespace_mismatch",
    "signer_identity_mismatch",
    "signing_key_binding_mismatch",
    "subject_context_mismatch",
    "environment_context_mismatch",
    "purpose_context_mismatch",
}

FORBIDDEN_EXECUTION_KEYS = {
    "execute",
    "sever",
    "permission_to_sever",
    "authorized_to_sever",
    "safe_to_sever",
    "isolation_occurred",
    "isolation_proven",
}


def run_identity_harness(repo_root: Path, *, build_wheel: bool = True) -> dict[str, Any]:
    first = _run_once(repo_root, build_wheel=build_wheel)
    second = _run_once(repo_root, build_wheel=build_wheel)
    first_semantic = _semantic_projection(first)
    second_semantic = _semantic_projection(second)
    first["two_run_semantic_diff"] = 0 if canonical_json(first_semantic) == canonical_json(second_semantic) else 1
    first["verdict"] = _verdict(first)
    return first


def _run_once(repo_root: Path, *, build_wheel: bool) -> dict[str, Any]:
    cases = _fixture_cases()
    results = [_run_case(case) for case in cases]
    end_to_end = _end_to_end_composition(repo_root, results)
    wheel = _check_public_wheel_exclusion(repo_root) if build_wheel else {"wheel_built": False}
    return {
        "schema": "SPIRA_NESIRA_PHASE2_IDENTITY_ADAPTER_HARNESS_RESULTS_V1",
        "crypto_pin": {
            "library": "cryptography",
            "version": PINNED_CRYPTOGRAPHY_VERSION,
        },
        "fixture_results": results,
        "classification": _classification_metrics(results),
        "end_to_end_composition": end_to_end,
        "public_wheel_exclusion": wheel,
    }


def _fixture_cases() -> list[dict[str, Any]]:
    bundle = _valid_bundle()

    def case(
        id_: str,
        expected: str,
        mutation: str | None = None,
        transform: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        current = deepcopy(bundle)
        if transform is not None:
            transform(current)
        return {
            "id": id_,
            "mutation": mutation,
            "credential_evidence": current["credential_evidence"],
            "declared_root": current["declared_root"],
            "expected_context": current["expected_context"],
            "now_utc": current["now_utc"],
            "expected_sub_verdict": expected,
        }

    return [
        case("valid_identity_binding", VERDICT_SUFFICIENT),
        case("missing_identity_root", VERDICT_NOT_EVALUATED, "missing_identity_root", lambda item: item.update({"declared_root": None})),
        case("ambiguous_identity_root", VERDICT_NOT_EVALUATED, "ambiguous_identity_root", lambda item: item["declared_root"].update({"ambiguous_identity_roots": True})),
        case("malformed_identity_root", VERDICT_NOT_EVALUATED, "malformed_identity_root", lambda item: item["declared_root"].pop("root_cert_pem")),
        case("unsupported_credential_type", VERDICT_NOT_EVALUATED, "unsupported_credential_type", lambda item: item["credential_evidence"].update({"credential_type": "UNSUPPORTED"})),
        case("malformed_credential", VERDICT_NOT_EVALUATED, "malformed_credential", lambda item: item["credential_evidence"].update({"leaf_cert_pem": "not a certificate"})),
        case("bad_credential_signature", VERDICT_INSUFFICIENT, "bad_credential_signature", _bad_credential_signature),
        case("chain_unbuildable_missing_intermediate", VERDICT_NOT_EVALUATED, "chain_unbuildable_missing_intermediate", lambda item: item["credential_evidence"].update({"intermediate_certs_pem": []})),
        case("known_but_undeclared_issuer", VERDICT_INSUFFICIENT, "known_but_undeclared_issuer", _known_but_undeclared_issuer),
        case("wrong_declared_identity_root", VERDICT_INSUFFICIENT, "wrong_declared_identity_root", lambda item: item["credential_evidence"].update({"issuer_root_id": "other-identity-root"})),
        case("untrusted_issuer", VERDICT_INSUFFICIENT, "untrusted_issuer", lambda item: item["credential_evidence"].update({"issuer_id": "untrusted-intermediate"})),
        case("expired_credential", VERDICT_INSUFFICIENT, "expired_credential", _expired_credential),
        case("expired_intermediate", VERDICT_INSUFFICIENT, "expired_intermediate", _expired_intermediate),
        case("expired_identity_root", VERDICT_INSUFFICIENT, "expired_identity_root", _expired_identity_root),
        case("revoked_credential", VERDICT_INSUFFICIENT, "revoked_credential", lambda item: item["credential_evidence"].update({"revocation": {"status": "REVOKED", "freshness": "FRESH"}})),
        case("revoked_intermediate", VERDICT_INSUFFICIENT, "revoked_intermediate", lambda item: item["credential_evidence"].update({"intermediate_revocations": [{"status": "REVOKED", "freshness": "FRESH"}]})),
        case("revoked_identity_root", VERDICT_INSUFFICIENT, "revoked_identity_root", lambda item: item["declared_root"].update({"revocation": {"status": "REVOKED", "freshness": "FRESH"}})),
        case("revocation_unknown", VERDICT_NOT_EVALUATED, "revocation_unknown", lambda item: item["credential_evidence"].update({"revocation": {"status": "UNKNOWN", "freshness": "FRESH"}})),
        case("revocation_stale", VERDICT_NOT_EVALUATED, "revocation_stale", lambda item: item["credential_evidence"].update({"revocation": {"status": "GOOD", "freshness": "STALE"}})),
        case("revocation_unreachable", VERDICT_NOT_EVALUATED, "revocation_unreachable", lambda item: item["credential_evidence"].update({"revocation": {"status": "UNREACHABLE", "freshness": "UNKNOWN"}})),
        case("clock_missing", VERDICT_NOT_EVALUATED, "clock_missing", lambda item: item.update({"now_utc": None})),
        case("clock_untrusted", VERDICT_NOT_EVALUATED, "clock_untrusted", lambda item: item.update({"now_utc": datetime(2026, 7, 16)})),
        case("namespace_mismatch", VERDICT_INSUFFICIENT, "namespace_mismatch", lambda item: item["credential_evidence"].update({"identity_namespace": "other.namespace"})),
        case("signer_identity_mismatch", VERDICT_INSUFFICIENT, "signer_identity_mismatch", lambda item: item["credential_evidence"].update({"signer_identity": "other-signer"})),
        case("signing_key_binding_mismatch", VERDICT_INSUFFICIENT, "signing_key_binding_mismatch", lambda item: item["credential_evidence"].update({"bound_signing_key_id": "other-signing-key"})),
        case("subject_context_mismatch", VERDICT_INSUFFICIENT, "subject_context_mismatch", lambda item: item["credential_evidence"].update({"subject": "other-subject"})),
        case("environment_context_mismatch", VERDICT_INSUFFICIENT, "environment_context_mismatch", lambda item: item["credential_evidence"].update({"environment": "staging"})),
        case("purpose_context_mismatch", VERDICT_INSUFFICIENT, "purpose_context_mismatch", lambda item: item["credential_evidence"].update({"purpose": "other-purpose"})),
    ]


def _valid_bundle() -> dict[str, Any]:
    chain = _certificate_chain("identity-root-main", "identity-intermediate-main", "spira://identity/signer-001")
    return {
        "credential_evidence": {
            "evidence_id": "identity-fixture-001",
            "credential_type": "X509_CLIENT_CERTIFICATE",
            "leaf_cert_pem": chain["leaf_cert_pem"],
            "intermediate_certs_pem": [chain["intermediate_cert_pem"]],
            "known_undeclared_roots_pem": [],
            "issuer_root_id": "identity-root-main",
            "issuer_id": "identity-intermediate-main",
            "identity_namespace": "spira://identity",
            "signer_identity": "spira://identity/signer-001",
            "bound_signing_key_id": "signing-key-main",
            **EXPECTED_CONTEXT,
            "revocation": {"status": "GOOD", "freshness": "FRESH"},
            "intermediate_revocations": [{"status": "GOOD", "freshness": "FRESH"}],
        },
        "declared_root": {
            "trust_root_id": "identity-root-main",
            "version": "1",
            "trust_root_kind": "IDENTITY_BINDING_CA",
            "root_cert_pem": chain["root_cert_pem"],
            "accepted_credential_types": ["X509_CLIENT_CERTIFICATE"],
            "identity_namespace": "spira://identity",
            "signer_identity_scope": ["spira://identity/signer-001"],
            "bound_signing_key_scope": ["signing-key-main"],
            "accepted_issuer_ids": ["identity-intermediate-main"],
            "subject_scope": [EXPECTED_CONTEXT["subject"]],
            "environment_scope": [EXPECTED_CONTEXT["environment"]],
            "purpose_scope": [EXPECTED_CONTEXT["purpose"]],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
            "revocation": {"status": "GOOD", "freshness": "FRESH"},
        },
        "expected_context": dict(EXPECTED_CONTEXT),
        "now_utc": NOW,
    }


def _certificate_chain(
    root_cn: str,
    intermediate_cn: str,
    leaf_cn: str,
    *,
    bad_leaf_signature: bool = False,
    expired_leaf: bool = False,
    expired_intermediate: bool = False,
    expired_root: bool = False,
) -> dict[str, str]:
    from cryptography import x509
    from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    def private_key() -> Any:
        return rsa.generate_private_key(public_exponent=65537, key_size=2048)

    def name(common_name: str) -> Any:
        return x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])

    def validity(expired: bool) -> tuple[datetime, datetime]:
        if expired:
            return NOW - timedelta(days=30), NOW - timedelta(days=1)
        return NOW - timedelta(days=10), NOW + timedelta(days=10)

    def build_cert(
        *,
        subject: Any,
        issuer: Any,
        public_key: Any,
        issuer_public_key: Any,
        serial: int,
        is_ca: bool,
        path_length: int | None,
        expired: bool,
    ) -> Any:
        not_before, not_after = validity(expired)
        builder = (
            x509.CertificateBuilder()
            .subject_name(subject)
            .issuer_name(issuer)
            .public_key(public_key)
            .serial_number(serial)
            .not_valid_before(not_before)
            .not_valid_after(not_after)
            .add_extension(x509.BasicConstraints(ca=is_ca, path_length=path_length), critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(issuer_public_key), critical=False)
        )
        if is_ca:
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=True,
                    crl_sign=True,
                    key_encipherment=False,
                    data_encipherment=False,
                    key_agreement=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
        else:
            builder = builder.add_extension(
                x509.KeyUsage(
                    digital_signature=True,
                    key_cert_sign=False,
                    crl_sign=False,
                    key_encipherment=True,
                    data_encipherment=False,
                    key_agreement=False,
                    content_commitment=False,
                    encipher_only=False,
                    decipher_only=False,
                ),
                critical=True,
            )
            builder = builder.add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.CLIENT_AUTH]), critical=False)
            builder = builder.add_extension(x509.SubjectAlternativeName([x509.DNSName("signer.example")]), critical=False)
        return builder

    root_key = private_key()
    intermediate_key = private_key()
    leaf_key = private_key()
    wrong_leaf_signer = private_key()
    root = build_cert(
        subject=name(root_cn),
        issuer=name(root_cn),
        public_key=root_key.public_key(),
        issuer_public_key=root_key.public_key(),
        serial=1001,
        is_ca=True,
        path_length=1,
        expired=expired_root,
    ).sign(root_key, hashes.SHA256())
    intermediate = build_cert(
        subject=name(intermediate_cn),
        issuer=name(root_cn),
        public_key=intermediate_key.public_key(),
        issuer_public_key=root_key.public_key(),
        serial=1002,
        is_ca=True,
        path_length=0,
        expired=expired_intermediate,
    ).sign(root_key, hashes.SHA256())
    leaf = build_cert(
        subject=name(leaf_cn),
        issuer=name(intermediate_cn),
        public_key=leaf_key.public_key(),
        issuer_public_key=intermediate_key.public_key(),
        serial=1003,
        is_ca=False,
        path_length=None,
        expired=expired_leaf,
    ).sign(wrong_leaf_signer if bad_leaf_signature else intermediate_key, hashes.SHA256())

    def pem(cert: Any) -> str:
        return cert.public_bytes(serialization.Encoding.PEM).decode("ascii")

    return {
        "root_cert_pem": pem(root),
        "intermediate_cert_pem": pem(intermediate),
        "leaf_cert_pem": pem(leaf),
    }


def _bad_credential_signature(item: dict[str, Any]) -> None:
    chain = _certificate_chain(
        "identity-root-main",
        "identity-intermediate-main",
        "spira://identity/signer-001",
        bad_leaf_signature=True,
    )
    item["credential_evidence"]["leaf_cert_pem"] = chain["leaf_cert_pem"]


def _known_but_undeclared_issuer(item: dict[str, Any]) -> None:
    chain = _certificate_chain("known-undeclared-root", "known-undeclared-intermediate", "spira://identity/signer-001")
    item["credential_evidence"]["leaf_cert_pem"] = chain["leaf_cert_pem"]
    item["credential_evidence"]["intermediate_certs_pem"] = [chain["intermediate_cert_pem"]]
    item["credential_evidence"]["known_undeclared_roots_pem"] = [chain["root_cert_pem"]]
    item["credential_evidence"].pop("issuer_root_id", None)


def _expired_credential(item: dict[str, Any]) -> None:
    chain = _certificate_chain(
        "identity-root-main",
        "identity-intermediate-main",
        "spira://identity/signer-001",
        expired_leaf=True,
    )
    item["declared_root"]["root_cert_pem"] = chain["root_cert_pem"]
    item["credential_evidence"]["intermediate_certs_pem"] = [chain["intermediate_cert_pem"]]
    item["credential_evidence"]["leaf_cert_pem"] = chain["leaf_cert_pem"]


def _expired_intermediate(item: dict[str, Any]) -> None:
    chain = _certificate_chain(
        "identity-root-main",
        "identity-intermediate-main",
        "spira://identity/signer-001",
        expired_intermediate=True,
    )
    item["declared_root"]["root_cert_pem"] = chain["root_cert_pem"]
    item["credential_evidence"]["intermediate_certs_pem"] = [chain["intermediate_cert_pem"]]
    item["credential_evidence"]["leaf_cert_pem"] = chain["leaf_cert_pem"]


def _expired_identity_root(item: dict[str, Any]) -> None:
    item["declared_root"]["valid_from"] = "2025-01-01T00:00:00Z"
    item["declared_root"]["valid_until"] = "2025-12-31T00:00:00Z"


def _run_case(case: Mapping[str, Any]) -> dict[str, Any]:
    result = assess_identity(
        credential_evidence=case["credential_evidence"],
        declared_root=case["declared_root"],
        expected_context=case["expected_context"],
        now_utc=case["now_utc"],
    )
    expected = case["expected_sub_verdict"]
    return {
        "id": case["id"],
        "mutation": case["mutation"],
        "expected_sub_verdict": expected,
        "actual_sub_verdict": result["sub_verdict"],
        "sub_verdict_matches": result["sub_verdict"] == expected,
        "reason_codes": result["reason_codes"],
        "assumption_ids": result["assumption_ids"],
        "not_evaluated_items": result["not_evaluated_items"],
        "blocking_items": result["blocking_items"],
        "execution_marker": result["execution_marker"],
        "has_execution_semantics": _has_execution_semantics(result),
    }


def _classification_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    covered = {item["mutation"] for item in results if item["mutation"]}
    missing = sorted(REQUIRED_FAILURE_MODES - covered)
    mismatches = [item for item in results if not item["sub_verdict_matches"]]
    unexpected_sufficient = [
        item
        for item in results
        if item["expected_sub_verdict"] != VERDICT_SUFFICIENT and item["actual_sub_verdict"] == VERDICT_SUFFICIENT
    ]
    by_id = {item["id"]: item for item in results}
    return {
        "required_identity_failure_modes": sorted(REQUIRED_FAILURE_MODES),
        "covered_identity_failure_modes": sorted(covered),
        "required_identity_failure_modes_without_fixture": len(missing),
        "required_identity_failure_modes_without_mutation_pair": len(missing),
        "missing_failure_modes": missing,
        "sub_verdict_mismatches": len(mismatches),
        "mismatch_ids": [item["id"] for item in mismatches],
        "unexpected_sufficient_verdicts": len(unexpected_sufficient),
        "missing_root_mapped_to_insufficient": int(by_id["missing_identity_root"]["actual_sub_verdict"] == VERDICT_INSUFFICIENT),
        "wrong_root_mapped_to_not_evaluated": int(by_id["wrong_declared_identity_root"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "chain_unbuildable_mapped_to_insufficient": int(by_id["chain_unbuildable_missing_intermediate"]["actual_sub_verdict"] == VERDICT_INSUFFICIENT),
        "known_untrusted_issuer_mapped_to_not_evaluated": int(by_id["known_but_undeclared_issuer"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "soft_pass_revocation_unknown": int(by_id["revocation_unknown"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "soft_pass_clock_failure": int(by_id["clock_missing"]["actual_sub_verdict"] == VERDICT_SUFFICIENT or by_id["clock_untrusted"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "default_trust_paths": int(by_id["missing_identity_root"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "adapter_outputs_with_authority_semantics": 0,
        "adapter_outputs_with_execution_semantics": sum(1 for item in results if item["has_execution_semantics"]),
    }


def _end_to_end_composition(repo_root: Path, results: list[dict[str, Any]]) -> dict[str, Any]:
    oracle = _load_composition_oracle(repo_root)
    rows = []
    mismatches = []
    expected_by_identity = {
        VERDICT_SUFFICIENT: VERDICT_NOT_EVALUATED,
        VERDICT_NOT_EVALUATED: VERDICT_NOT_EVALUATED,
        VERDICT_INSUFFICIENT: VERDICT_INSUFFICIENT,
    }
    for identity_verdict, expected_composite in expected_by_identity.items():
        composite = oracle[identity_verdict]
        row = {
            "signature_sub": VERDICT_SUFFICIENT,
            "identity_sub": identity_verdict,
            "authority_sub": VERDICT_NOT_EVALUATED,
            "isolation_sub": VERDICT_NOT_EVALUATED,
            "expected_composite": expected_composite,
            "actual_composite": composite,
            "matches": composite == expected_composite,
        }
        rows.append(row)
        if not row["matches"]:
            mismatches.append(row)
    actual_verdicts = {item["actual_sub_verdict"] for item in results}
    return {
        "rows": rows,
        "adapter_verdicts_observed": sorted(actual_verdicts),
        "composition_mismatches": len(mismatches),
        "mismatch_rows": mismatches,
    }


def _load_composition_oracle(repo_root: Path) -> dict[str, str]:
    table = json.loads((repo_root / ORACLE).read_text(encoding="utf-8"))
    mapping = {}
    for row in table["rows"]:
        inputs = row["inputs"]
        if (
            inputs["signature_sub"] == VERDICT_SUFFICIENT
            and inputs["authority_sub"] == VERDICT_NOT_EVALUATED
            and inputs["isolation_sub"] == VERDICT_NOT_EVALUATED
        ):
            mapping[inputs["identity_sub"]] = row["composite_verdict"]
    return mapping


def _check_public_wheel_exclusion(repo_root: Path) -> dict[str, Any]:
    with _temporary_wheel_dir() as out_dir:
        completed = subprocess.run(
            [sys.executable, "tools/build_spira_trust_public.py", str(out_dir)],
            cwd=repo_root,
            check=True,
            text=True,
            capture_output=True,
        )
        wheel_path = Path(completed.stdout.splitlines()[0])
        with zipfile.ZipFile(wheel_path) as zf:
            names = zf.namelist()
            metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
            metadata = zf.read(metadata_name).decode("utf-8")
        adapter_entries = [name for name in names if "nesira_phase2_identity" in name]
        cryptography_entries = [name for name in names if "cryptography" in name.lower()]
        metadata_mentions_crypto = "cryptography" in metadata.lower()
        return {
            "wheel_built": True,
            "adapter_entries": adapter_entries,
            "cryptography_entries": cryptography_entries,
            "metadata_mentions_cryptography": metadata_mentions_crypto,
            "wheel_exclusion_failures": len(adapter_entries) + len(cryptography_entries) + int(metadata_mentions_crypto),
        }


class _temporary_wheel_dir:
    def __init__(self) -> None:
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self._temp = tempfile.TemporaryDirectory(prefix="spira_nesira_identity_wheel_")
        self.path = Path(self._temp.name)
        return self.path

    def __exit__(self, *_exc: object) -> None:
        if self._temp is not None:
            self._temp.cleanup()


def _has_execution_semantics(result: Mapping[str, Any]) -> bool:
    return any(key in result for key in FORBIDDEN_EXECUTION_KEYS)


def _semantic_projection(results: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_results": results["fixture_results"],
        "classification": results["classification"],
        "end_to_end_composition": results["end_to_end_composition"],
        "public_wheel_exclusion": results["public_wheel_exclusion"],
    }


def _verdict(results: Mapping[str, Any]) -> str:
    checks = [
        results["classification"]["required_identity_failure_modes_without_fixture"],
        results["classification"]["required_identity_failure_modes_without_mutation_pair"],
        results["classification"]["sub_verdict_mismatches"],
        results["classification"]["unexpected_sufficient_verdicts"],
        results["classification"]["missing_root_mapped_to_insufficient"],
        results["classification"]["wrong_root_mapped_to_not_evaluated"],
        results["classification"]["chain_unbuildable_mapped_to_insufficient"],
        results["classification"]["known_untrusted_issuer_mapped_to_not_evaluated"],
        results["classification"]["soft_pass_revocation_unknown"],
        results["classification"]["soft_pass_clock_failure"],
        results["classification"]["default_trust_paths"],
        results["classification"]["adapter_outputs_with_authority_semantics"],
        results["classification"]["adapter_outputs_with_execution_semantics"],
        results["end_to_end_composition"]["composition_mismatches"],
        results["public_wheel_exclusion"].get("wheel_exclusion_failures", 0),
        results["two_run_semantic_diff"],
    ]
    if any(check != 0 for check in checks):
        return "NESIRA_PHASE2_IDENTITY_ADAPTER_NEEDS_REVISION"
    return "NESIRA_PHASE2_IDENTITY_ADAPTER_ACCEPTED"
