from __future__ import annotations

import base64
import json
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_signature_adapter import (
    PINNED_CRYPTOGRAPHY_VERSION,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
    assess_signature,
)


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)
PAYLOAD = b'{"payload":"nesira phase2 signature adapter fixture"}'
EXPECTED_CONTEXT = {
    "payload_class": "NESIRA_PHASE2_SIGNATURE_TEST_PAYLOAD",
    "subject": "legacy-db-primary",
    "environment": "prod-eu-1",
    "purpose": "phase2-signature-adapter-conformance",
    "action": "assess-signature",
}
ORACLE = Path("research") / "nesira_policy_profile" / "nesira_phase2_assessment_decision_table.json"

REQUIRED_FAILURE_MODES = {
    "bad_signature",
    "wrong_declared_root",
    "missing_declared_root",
    "malformed_declared_root",
    "expired_declared_root",
    "revoked_declared_root",
    "revocation_unknown",
    "revocation_stale",
    "revocation_unreachable",
    "clock_missing",
    "clock_untrusted",
    "payload_malformed",
    "signature_malformed",
    "payload_class_out_of_scope",
    "subject_scope_mismatch",
    "environment_scope_mismatch",
    "purpose_scope_mismatch",
    "action_scope_mismatch",
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


def run_signature_harness(repo_root: Path, *, build_wheel: bool = True) -> dict[str, Any]:
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
        "schema": "SPIRA_NESIRA_PHASE2_SIGNATURE_ADAPTER_HARNESS_RESULTS_V1",
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
            "payload": current["payload"],
            "signature_evidence": current["signature_evidence"],
            "declared_root": current["declared_root"],
            "expected_context": current["expected_context"],
            "now_utc": current["now_utc"],
            "expected_sub_verdict": expected,
        }

    return [
        case("valid_signature_declared_root_fresh_revocation", VERDICT_SUFFICIENT),
        case("bad_signature", VERDICT_INSUFFICIENT, "bad_signature", _bad_signature),
        case("wrong_declared_root", VERDICT_INSUFFICIENT, "wrong_declared_root", _wrong_declared_root),
        case("missing_declared_root", VERDICT_NOT_EVALUATED, "missing_declared_root", lambda item: item.update({"declared_root": None})),
        case("malformed_declared_root", VERDICT_NOT_EVALUATED, "malformed_declared_root", lambda item: item["declared_root"].pop("public_key_pem")),
        case("expired_declared_root", VERDICT_INSUFFICIENT, "expired_declared_root", _expired_root),
        case("revoked_declared_root", VERDICT_INSUFFICIENT, "revoked_declared_root", lambda item: item["declared_root"].update({"revocation": {"status": "REVOKED", "freshness": "FRESH"}})),
        case("revocation_unknown", VERDICT_NOT_EVALUATED, "revocation_unknown", lambda item: item["declared_root"].update({"revocation": {"status": "UNKNOWN", "freshness": "FRESH"}})),
        case("revocation_stale", VERDICT_NOT_EVALUATED, "revocation_stale", lambda item: item["declared_root"].update({"revocation": {"status": "GOOD", "freshness": "STALE"}})),
        case("revocation_unreachable", VERDICT_NOT_EVALUATED, "revocation_unreachable", lambda item: item["declared_root"].update({"revocation": {"status": "UNREACHABLE", "freshness": "UNKNOWN"}})),
        case("clock_missing", VERDICT_NOT_EVALUATED, "clock_missing", lambda item: item.update({"now_utc": None})),
        case("clock_untrusted", VERDICT_NOT_EVALUATED, "clock_untrusted", lambda item: item.update({"now_utc": datetime(2026, 7, 16)})),
        case("payload_malformed", VERDICT_NOT_EVALUATED, "payload_malformed", lambda item: item.update({"payload": "not bytes"})),
        case("signature_malformed", VERDICT_NOT_EVALUATED, "signature_malformed", lambda item: item["signature_evidence"].update({"signature_b64": "not-base64!"})),
        case("payload_class_out_of_scope", VERDICT_INSUFFICIENT, "payload_class_out_of_scope", lambda item: item["declared_root"].update({"payload_class": "OTHER"})),
        case("subject_scope_mismatch", VERDICT_INSUFFICIENT, "subject_scope_mismatch", lambda item: item["declared_root"].update({"subject_scope": ["other-subject"]})),
        case("environment_scope_mismatch", VERDICT_INSUFFICIENT, "environment_scope_mismatch", lambda item: item["declared_root"].update({"environment_scope": ["staging"]})),
        case("purpose_scope_mismatch", VERDICT_INSUFFICIENT, "purpose_scope_mismatch", lambda item: item["declared_root"].update({"purpose_scope": ["other-purpose"]})),
        case("action_scope_mismatch", VERDICT_INSUFFICIENT, "action_scope_mismatch", lambda item: item["declared_root"].update({"action_scope": ["other-action"]})),
    ]


def _valid_bundle() -> dict[str, Any]:
    private_key = _private_key()
    signature = private_key.sign(PAYLOAD)
    return {
        "payload": PAYLOAD,
        "signature_evidence": {
            "evidence_id": "signature-fixture-001",
            "signature_b64": base64.b64encode(signature).decode("ascii"),
            "algorithm": "Ed25519",
            "key_id": "signing-key-main",
            **EXPECTED_CONTEXT,
        },
        "declared_root": {
            "trust_root_id": "signing-root-main",
            "version": "1",
            "trust_root_kind": "SIGNING_KEY",
            "key_id": "signing-key-main",
            "public_key_pem": _public_key_pem(private_key),
            "accepted_algorithms": ["Ed25519"],
            "payload_class": EXPECTED_CONTEXT["payload_class"],
            "subject_scope": [EXPECTED_CONTEXT["subject"]],
            "environment_scope": [EXPECTED_CONTEXT["environment"]],
            "purpose_scope": [EXPECTED_CONTEXT["purpose"]],
            "action_scope": [EXPECTED_CONTEXT["action"]],
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


def _bad_signature(item: dict[str, Any]) -> None:
    signature = bytearray(base64.b64decode(item["signature_evidence"]["signature_b64"]))
    signature[0] ^= 1
    item["signature_evidence"]["signature_b64"] = base64.b64encode(bytes(signature)).decode("ascii")


def _wrong_declared_root(item: dict[str, Any]) -> None:
    item["declared_root"]["key_id"] = "different-declared-key"


def _expired_root(item: dict[str, Any]) -> None:
    item["declared_root"]["valid_from"] = "2025-01-01T00:00:00Z"
    item["declared_root"]["valid_until"] = "2025-12-31T00:00:00Z"


def _run_case(case: Mapping[str, Any]) -> dict[str, Any]:
    result = assess_signature(
        payload=case["payload"],
        signature_evidence=case["signature_evidence"],
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
        item for item in results
        if item["expected_sub_verdict"] != VERDICT_SUFFICIENT and item["actual_sub_verdict"] == VERDICT_SUFFICIENT
    ]
    by_id = {item["id"]: item for item in results}
    return {
        "required_signature_failure_modes": sorted(REQUIRED_FAILURE_MODES),
        "covered_signature_failure_modes": sorted(covered),
        "required_signature_failure_modes_without_fixture": len(missing),
        "required_signature_failure_modes_without_mutation_pair": len(missing),
        "missing_failure_modes": missing,
        "sub_verdict_mismatches": len(mismatches),
        "mismatch_ids": [item["id"] for item in mismatches],
        "unexpected_sufficient_verdicts": len(unexpected_sufficient),
        "missing_root_mapped_to_insufficient": int(by_id["missing_declared_root"]["actual_sub_verdict"] == VERDICT_INSUFFICIENT),
        "wrong_root_mapped_to_not_evaluated": int(by_id["wrong_declared_root"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "soft_pass_revocation_unknown": int(by_id["revocation_unknown"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "soft_pass_clock_failure": int(by_id["clock_missing"]["actual_sub_verdict"] == VERDICT_SUFFICIENT or by_id["clock_untrusted"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "default_trust_paths": int(by_id["missing_declared_root"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "adapter_outputs_with_execution_semantics": sum(1 for item in results if item["has_execution_semantics"]),
    }


def _end_to_end_composition(repo_root: Path, results: list[dict[str, Any]]) -> dict[str, Any]:
    oracle = _load_composition_oracle(repo_root)
    rows = []
    mismatches = []
    expected_by_signature = {
        VERDICT_SUFFICIENT: VERDICT_NOT_EVALUATED,
        VERDICT_NOT_EVALUATED: VERDICT_NOT_EVALUATED,
        VERDICT_INSUFFICIENT: VERDICT_INSUFFICIENT,
    }
    for signature_verdict, expected_composite in expected_by_signature.items():
        composite = oracle[signature_verdict]
        row = {
            "signature_sub": signature_verdict,
            "identity_sub": VERDICT_NOT_EVALUATED,
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
            inputs["identity_sub"] == VERDICT_NOT_EVALUATED
            and inputs["authority_sub"] == VERDICT_NOT_EVALUATED
            and inputs["isolation_sub"] == VERDICT_NOT_EVALUATED
        ):
            mapping[inputs["signature_sub"]] = row["composite_verdict"]
    return mapping


def _check_public_wheel_exclusion(repo_root: Path) -> dict[str, Any]:
    with _temporary_wheel_dir(repo_root) as out_dir:
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
        adapter_entries = [name for name in names if "nesira_phase2_signature" in name]
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
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self._temp = tempfile.TemporaryDirectory(prefix="spira_nesira_signature_wheel_")
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
        results["classification"]["required_signature_failure_modes_without_fixture"],
        results["classification"]["required_signature_failure_modes_without_mutation_pair"],
        results["classification"]["sub_verdict_mismatches"],
        results["classification"]["unexpected_sufficient_verdicts"],
        results["classification"]["missing_root_mapped_to_insufficient"],
        results["classification"]["wrong_root_mapped_to_not_evaluated"],
        results["classification"]["soft_pass_revocation_unknown"],
        results["classification"]["soft_pass_clock_failure"],
        results["classification"]["default_trust_paths"],
        results["classification"]["adapter_outputs_with_execution_semantics"],
        results["end_to_end_composition"]["composition_mismatches"],
        results["public_wheel_exclusion"].get("wheel_exclusion_failures", 0),
        results["two_run_semantic_diff"],
    ]
    if any(check != 0 for check in checks):
        return "NESIRA_PHASE2_SIGNATURE_ADAPTER_NEEDS_REVISION"
    return "NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED"
