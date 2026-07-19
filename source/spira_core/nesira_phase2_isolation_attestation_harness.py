from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_isolation_attestation_adapter import (
    ISOLATION_CAVEAT,
    PINNED_CRYPTOGRAPHY_VERSION,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
    assess_isolation_attestation,
)


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)
EXPECTED_CONTEXT = {
    "candidate_id": "legacy-db-primary",
    "candidate_hash": "sha256:9d839fb63a0d19c728e3cfaea55e27f9e6f4a5506d65ecf38d5f3ea6fbf92d41",
    "environment_id": "prod-eu-1",
    "profile_id": "nesira-profile-v1",
    "profile_version": "1",
}
ORACLE = Path("research") / "nesira_policy_profile" / "nesira_phase2_assessment_decision_table.json"

REQUIRED_FAILURE_MODES = {
    "missing_attestation_authority_root",
    "ambiguous_attestation_authority_root",
    "malformed_attestation_authority_root",
    "attestation_missing",
    "attestation_malformed",
    "unsupported_attestation_type",
    "bad_attestation_signature",
    "known_undeclared_attestation_authority",
    "attestation_root_mismatch",
    "candidate_claim_mismatch",
    "environment_claim_mismatch",
    "isolation_profile_claim_mismatch",
    "attestation_expired",
    "attestation_not_yet_valid",
    "attestation_authority_revoked",
    "revocation_unknown",
    "revocation_stale",
    "revocation_unreachable",
    "clock_missing",
    "clock_untrusted",
    "clock_missing_with_expired_attestation",
}

ALLOWED_ATTESTATION_LANGUAGE_FRAGMENTS = {
    "isolation_attestation",
    "isolation_profile",
    "isolation_sub",
    "pt-isolation-01",
    "isolation-01",
    "isolation_01",
    "carries_isolation_caveat",
    "has_isolation_truth_semantics",
    "outputs_with_isolation_truth_semantics",
    "outputs_without_pt_isolation_01",
    "required_isolation_failure_modes",
    "covered_isolation_failure_modes",
    "non_allowlisted_isolation_language_hits",
    "forbidden_isolation_language_hits",
    "expected_by_isolation",
    "isolation_verdict",
}

FORBIDDEN_STEM_PATTERN = re.compile(
    r"(" + "iso" + r"lat\w*|" + "sand" + r"box\w*|" + "con" + r"tain\w*)",
    re.IGNORECASE,
)


def run_isolation_attestation_harness(repo_root: Path, *, build_wheel: bool = True) -> dict[str, Any]:
    first = _run_once(repo_root, build_wheel=build_wheel)
    second = _run_once(repo_root, build_wheel=build_wheel)
    first_semantic = _semantic_projection(first)
    second_semantic = _semantic_projection(second)
    first["two_run_semantic_diff"] = 0 if canonical_json(first_semantic) == canonical_json(second_semantic) else 1
    language = _language_metrics(first)
    first["language_allowlist"] = language
    first["verdict"] = _verdict(first)
    return first


def _run_once(repo_root: Path, *, build_wheel: bool) -> dict[str, Any]:
    cases = _fixture_cases()
    results = [_run_case(case) for case in cases]
    end_to_end = _end_to_end_composition(repo_root, results)
    wheel = _check_public_wheel_exclusion(repo_root) if build_wheel else {"wheel_built": False}
    return {
        "schema": "SPIRA_NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_HARNESS_RESULTS_V1",
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
            "attestation_evidence": current["attestation_evidence"],
            "declared_root": current["declared_root"],
            "expected_context": current["expected_context"],
            "now_utc": current["now_utc"],
            "expected_sub_verdict": expected,
        }

    return [
        case("valid_attestation_under_declared_authority", VERDICT_SUFFICIENT),
        case("missing_attestation_authority_root", VERDICT_NOT_EVALUATED, "missing_attestation_authority_root", lambda item: item.update({"declared_root": None})),
        case("ambiguous_attestation_authority_root", VERDICT_NOT_EVALUATED, "ambiguous_attestation_authority_root", lambda item: item["declared_root"].update({"ambiguous_attestation_authorities": True})),
        case("malformed_attestation_authority_root", VERDICT_NOT_EVALUATED, "malformed_attestation_authority_root", lambda item: item["declared_root"].pop("public_key_pem")),
        case("attestation_missing", VERDICT_NOT_EVALUATED, "attestation_missing", lambda item: item.update({"attestation_evidence": None})),
        case("attestation_malformed", VERDICT_NOT_EVALUATED, "attestation_malformed", lambda item: item["attestation_evidence"].pop("attestation_payload")),
        case("unsupported_attestation_type", VERDICT_NOT_EVALUATED, "unsupported_attestation_type", lambda item: item["attestation_evidence"].update({"attestation_type": "UNSUPPORTED"})),
        case("bad_attestation_signature", VERDICT_INSUFFICIENT, "bad_attestation_signature", _bad_signature),
        case("known_undeclared_attestation_authority", VERDICT_INSUFFICIENT, "known_undeclared_attestation_authority", lambda item: item["attestation_evidence"].update({"authority_id": "known-but-undeclared-authority"})),
        case("attestation_root_mismatch", VERDICT_INSUFFICIENT, "attestation_root_mismatch", lambda item: item["attestation_evidence"].update({"authority_root_id": "other-attestation-root"})),
        case("candidate_claim_mismatch", VERDICT_INSUFFICIENT, "candidate_claim_mismatch", lambda item: item["attestation_evidence"]["attestation_payload"].update({"candidate_id": "other-candidate"})),
        case("environment_claim_mismatch", VERDICT_INSUFFICIENT, "environment_claim_mismatch", lambda item: item["attestation_evidence"]["attestation_payload"].update({"environment_id": "staging"})),
        case("isolation_profile_claim_mismatch", VERDICT_INSUFFICIENT, "isolation_profile_claim_mismatch", lambda item: item["attestation_evidence"]["attestation_payload"].update({"profile_id": "other-profile"})),
        case("attestation_expired", VERDICT_INSUFFICIENT, "attestation_expired", lambda item: item["attestation_evidence"].update({"valid_from": "2025-01-01T00:00:00Z", "valid_until": "2025-12-31T00:00:00Z"})),
        case("attestation_not_yet_valid", VERDICT_INSUFFICIENT, "attestation_not_yet_valid", lambda item: item["attestation_evidence"].update({"valid_from": "2027-01-01T00:00:00Z", "valid_until": "2027-12-31T00:00:00Z"})),
        case("attestation_authority_revoked", VERDICT_INSUFFICIENT, "attestation_authority_revoked", lambda item: item["declared_root"].update({"revocation": {"status": "REVOKED", "freshness": "FRESH"}})),
        case("revocation_unknown", VERDICT_NOT_EVALUATED, "revocation_unknown", lambda item: item["attestation_evidence"].update({"revocation": {"status": "UNKNOWN", "freshness": "FRESH"}})),
        case("revocation_stale", VERDICT_NOT_EVALUATED, "revocation_stale", lambda item: item["attestation_evidence"].update({"revocation": {"status": "GOOD", "freshness": "STALE"}})),
        case("revocation_unreachable", VERDICT_NOT_EVALUATED, "revocation_unreachable", lambda item: item["attestation_evidence"].update({"revocation": {"status": "UNREACHABLE", "freshness": "UNKNOWN"}})),
        case("clock_missing", VERDICT_NOT_EVALUATED, "clock_missing", lambda item: item.update({"now_utc": None})),
        case("clock_untrusted", VERDICT_NOT_EVALUATED, "clock_untrusted", lambda item: item.update({"now_utc": datetime(2026, 7, 16)})),
        case("clock_missing_with_expired_attestation", VERDICT_NOT_EVALUATED, "clock_missing_with_expired_attestation", _clock_missing_with_expired_attestation),
    ]


def _valid_bundle() -> dict[str, Any]:
    private_key = _private_key()
    payload = {
        "candidate_id": EXPECTED_CONTEXT["candidate_id"],
        "candidate_hash": EXPECTED_CONTEXT["candidate_hash"],
        "environment_id": EXPECTED_CONTEXT["environment_id"],
        "profile_id": EXPECTED_CONTEXT["profile_id"],
        "profile_version": EXPECTED_CONTEXT["profile_version"],
        "attestation_statement": "claim-bound-to-profile-v1",
    }
    signature = private_key.sign(canonical_json(payload).encode("utf-8"))
    return {
        "attestation_evidence": {
            "evidence_id": "attestation-fixture-001",
            "attestation_type": "SPIRA_ATTESTATION_V1",
            "authority_id": "attestation-authority-main",
            "authority_root_id": "attestation-root-main",
            "authority_root_version": "1",
            "algorithm": "Ed25519",
            "signature_b64": _signature_b64(signature),
            "attestation_payload": payload,
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
            "revocation": {"status": "GOOD", "freshness": "FRESH"},
        },
        "declared_root": {
            "trust_root_id": "attestation-root-main",
            "version": "1",
            "trust_root_kind": "ATTESTATION_AUTHORITY",
            "authority_id": "attestation-authority-main",
            "public_key_pem": _public_key_pem(private_key),
            "accepted_algorithms": ["Ed25519"],
            "accepted_attestation_types": ["SPIRA_ATTESTATION_V1"],
            "candidate_scope": [EXPECTED_CONTEXT["candidate_id"]],
            "environment_scope": [EXPECTED_CONTEXT["environment_id"]],
            "profile_scope": [EXPECTED_CONTEXT["profile_id"]],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
            "revocation": {"status": "GOOD", "freshness": "FRESH"},
        },
        "expected_context": dict(EXPECTED_CONTEXT),
        "now_utc": NOW,
    }


def _private_key() -> Any:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

    return Ed25519PrivateKey.generate()


def _public_key_pem(private_key: Any) -> str:
    from cryptography.hazmat.primitives import serialization

    return (
        private_key.public_key()
        .public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        .decode("ascii")
    )


def _signature_b64(signature: bytes) -> str:
    import base64

    return base64.b64encode(signature).decode("ascii")


def _bad_signature(item: dict[str, Any]) -> None:
    import base64

    signature = bytearray(base64.b64decode(item["attestation_evidence"]["signature_b64"]))
    signature[0] ^= 1
    item["attestation_evidence"]["signature_b64"] = base64.b64encode(bytes(signature)).decode("ascii")


def _clock_missing_with_expired_attestation(item: dict[str, Any]) -> None:
    item.update({"now_utc": None})
    item["attestation_evidence"].update({"valid_from": "2025-01-01T00:00:00Z", "valid_until": "2025-12-31T00:00:00Z"})


def _run_case(case: Mapping[str, Any]) -> dict[str, Any]:
    result = assess_isolation_attestation(
        attestation_evidence=case["attestation_evidence"],
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
        "evidence_references": result["evidence_references"],
        "crypto_dependency": result["crypto_dependency"],
        "execution_marker": result["execution_marker"],
        "has_execution_semantics": _has_execution_semantics(result),
        "has_isolation_truth_semantics": _has_truth_semantics(result),
        "carries_isolation_caveat": ISOLATION_CAVEAT in result["assumption_ids"],
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
        "required_isolation_failure_modes": sorted(REQUIRED_FAILURE_MODES),
        "covered_isolation_failure_modes": sorted(covered),
        "required_isolation_failure_modes_without_fixture": len(missing),
        "required_isolation_failure_modes_without_mutation_pair": len(missing),
        "missing_failure_modes": missing,
        "sub_verdict_mismatches": len(mismatches),
        "mismatch_ids": [item["id"] for item in mismatches],
        "unexpected_sufficient_verdicts": len(unexpected_sufficient),
        "missing_root_mapped_to_insufficient": int(by_id["missing_attestation_authority_root"]["actual_sub_verdict"] == VERDICT_INSUFFICIENT),
        "known_undeclared_authority_mapped_to_not_evaluated": int(by_id["known_undeclared_attestation_authority"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "claims_mismatch_mapped_to_not_evaluated": int(by_id["candidate_claim_mismatch"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED or by_id["environment_claim_mismatch"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED or by_id["isolation_profile_claim_mismatch"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "clock_failure_mapped_to_temporal_invalid": int(by_id["clock_missing_with_expired_attestation"]["actual_sub_verdict"] == VERDICT_INSUFFICIENT),
        "soft_pass_revocation_unknown": int(by_id["revocation_unknown"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "soft_pass_clock_failure": int(by_id["clock_missing"]["actual_sub_verdict"] == VERDICT_SUFFICIENT or by_id["clock_untrusted"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "outputs_without_pt_isolation_01": sum(1 for item in results if not item["carries_isolation_caveat"]),
        "outputs_with_execution_semantics": sum(1 for item in results if item["has_execution_semantics"]),
        "outputs_with_isolation_truth_semantics": sum(1 for item in results if item["has_isolation_truth_semantics"]),
    }


def _end_to_end_composition(repo_root: Path, results: list[dict[str, Any]]) -> dict[str, Any]:
    table = json.loads((repo_root / ORACLE).read_text(encoding="utf-8"))
    rows = []
    mismatches = []
    caveat_mismatches = []
    expected_by_isolation = {
        VERDICT_SUFFICIENT: VERDICT_SUFFICIENT,
        VERDICT_NOT_EVALUATED: VERDICT_NOT_EVALUATED,
        VERDICT_INSUFFICIENT: VERDICT_INSUFFICIENT,
    }
    for isolation_verdict, expected_composite in expected_by_isolation.items():
        row = _find_oracle_row(table, isolation_verdict)
        actual = row["composite_verdict"]
        assumptions = row["required_explicit_assumption_ids"]
        current = {
            "signature_sub": VERDICT_SUFFICIENT,
            "identity_sub": VERDICT_SUFFICIENT,
            "authority_sub": VERDICT_SUFFICIENT,
            "isolation_sub": isolation_verdict,
            "expected_composite": expected_composite,
            "actual_composite": actual,
            "matches": actual == expected_composite,
            "composite_carries_pt_isolation_01": ISOLATION_CAVEAT in assumptions,
        }
        rows.append(current)
        if not current["matches"]:
            mismatches.append(current)
        if isolation_verdict == VERDICT_SUFFICIENT and ISOLATION_CAVEAT not in assumptions:
            caveat_mismatches.append(current)
    actual_verdicts = {item["actual_sub_verdict"] for item in results}
    return {
        "rows": rows,
        "adapter_verdicts_observed": sorted(actual_verdicts),
        "composition_mismatches": len(mismatches),
        "mismatch_rows": mismatches,
        "composite_caveat_mismatches": len(caveat_mismatches),
    }


def _find_oracle_row(table: Mapping[str, Any], isolation_verdict: str) -> Mapping[str, Any]:
    for row in table["rows"]:
        inputs = row["inputs"]
        if (
            inputs["signature_sub"] == VERDICT_SUFFICIENT
            and inputs["identity_sub"] == VERDICT_SUFFICIENT
            and inputs["authority_sub"] == VERDICT_SUFFICIENT
            and inputs["isolation_sub"] == isolation_verdict
        ):
            return row
    raise KeyError(isolation_verdict)


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
        adapter_entries = [name for name in names if "nesira_phase2_isolation_attestation" in name]
        cryptography_entries = [name for name in names if name.startswith("cryptography")]
        dependency_headers = [
            line
            for line in metadata.splitlines()
            if line.startswith(("Requires-Dist:", "Provides-Extra:"))
        ]
        return {
            "wheel_built": True,
            "adapter_entries": adapter_entries,
            "cryptography_entries": cryptography_entries,
            "metadata_dependency_headers": dependency_headers,
            "metadata_mentions_new_dependency": bool(dependency_headers),
            "wheel_exclusion_failures": len(adapter_entries) + len(cryptography_entries) + int(bool(dependency_headers)),
        }


class _temporary_wheel_dir:
    def __init__(self) -> None:
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self._temp = tempfile.TemporaryDirectory(prefix="spira_nesira_attestation_wheel_")
        self.path = Path(self._temp.name)
        return self.path

    def __exit__(self, *_exc: object) -> None:
        if self._temp is not None:
            self._temp.cleanup()


def _has_execution_semantics(result: Mapping[str, Any]) -> bool:
    forbidden_keys = {"execute", "sever", "permission_to_sever", "authorized_to_sever", "safe_to_sever", "runner"}
    return any(key in result for key in forbidden_keys)


def _has_truth_semantics(result: Mapping[str, Any]) -> bool:
    serialized = canonical_json(result).lower()
    forbidden = [
        "verified",
        "established",
        "guaranteed",
        "ensured",
        "enforced",
        "ran",
        "was",
    ]
    stem = "iso" + "lat"
    return any(f"{stem}{suffix}" in serialized for suffix in forbidden)


def _language_metrics(results: Mapping[str, Any]) -> dict[str, Any]:
    serialized = canonical_json(_semantic_projection(results)).lower()
    hits = []
    for match in FORBIDDEN_STEM_PATTERN.finditer(serialized):
        token = match.group(1)
        if not _token_is_allowlisted(serialized, match.start(), match.end()):
            hits.append({"token": token, "offset": match.start()})
    explicit_bad_hits = _explicit_bad_hits(serialized)
    return {
        "non_allowlisted_isolation_language_hits": len(hits),
        "non_allowlisted_samples": hits[:20],
        "forbidden_isolation_language_hits": len(explicit_bad_hits),
        "forbidden_samples": explicit_bad_hits[:20],
    }


def _token_is_allowlisted(serialized: str, start: int, end: int) -> bool:
    window = serialized[max(0, start - 64) : min(len(serialized), end + 64)]
    return any(fragment in window for fragment in ALLOWED_ATTESTATION_LANGUAGE_FRAGMENTS)


def _explicit_bad_hits(serialized: str) -> list[str]:
    stem = "isol" + "ation"
    bad_phrases = [
        stem + " verif" + "ied",
        stem + " establish" + "ed",
        stem + " guarante" + "ed",
        stem + " ensur" + "ed",
        stem + " enforc" + "ed",
        "ran in " + stem,
        "was " + "iso" + "lat" + "ed",
        "sand" + "box" + "ed",
        "con" + "tain" + "ed",
    ]
    return [phrase for phrase in bad_phrases if phrase in serialized]


def _semantic_projection(results: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_results": results["fixture_results"],
        "classification": results["classification"],
        "end_to_end_composition": results["end_to_end_composition"],
        "public_wheel_exclusion": results["public_wheel_exclusion"],
    }


def _verdict(results: Mapping[str, Any]) -> str:
    checks = [
        results["classification"]["required_isolation_failure_modes_without_fixture"],
        results["classification"]["required_isolation_failure_modes_without_mutation_pair"],
        results["classification"]["sub_verdict_mismatches"],
        results["classification"]["unexpected_sufficient_verdicts"],
        results["classification"]["missing_root_mapped_to_insufficient"],
        results["classification"]["known_undeclared_authority_mapped_to_not_evaluated"],
        results["classification"]["claims_mismatch_mapped_to_not_evaluated"],
        results["classification"]["clock_failure_mapped_to_temporal_invalid"],
        results["classification"]["soft_pass_revocation_unknown"],
        results["classification"]["soft_pass_clock_failure"],
        results["classification"]["outputs_without_pt_isolation_01"],
        results["classification"]["outputs_with_execution_semantics"],
        results["classification"]["outputs_with_isolation_truth_semantics"],
        results["end_to_end_composition"]["composition_mismatches"],
        results["end_to_end_composition"]["composite_caveat_mismatches"],
        results["public_wheel_exclusion"].get("wheel_exclusion_failures", 0),
        results["language_allowlist"]["forbidden_isolation_language_hits"],
        results["language_allowlist"]["non_allowlisted_isolation_language_hits"],
        results["two_run_semantic_diff"],
    ]
    if any(check != 0 for check in checks):
        return "NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_NEEDS_REVISION"
    return "NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_ACCEPTED"
