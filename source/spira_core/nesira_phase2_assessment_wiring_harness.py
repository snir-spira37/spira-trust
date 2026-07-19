from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from pathlib import Path
from typing import Any, Callable, Mapping

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_assessment_wiring import (
    DOMAINS,
    EXECUTION_MARKER,
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
    assess_phase2_wiring,
    compose_subresults,
)
from spira_core.nesira_phase2_authority_harness import _valid_bundle as _authority_bundle
from spira_core.nesira_phase2_identity_harness import _valid_bundle as _identity_bundle
from spira_core.nesira_phase2_isolation_attestation_adapter import ISOLATION_CAVEAT
from spira_core.nesira_phase2_isolation_attestation_harness import _valid_bundle as _attestation_bundle
from spira_core.nesira_phase2_signature_harness import _valid_bundle as _signature_bundle


ORACLE = Path("research") / "nesira_policy_profile" / "nesira_phase2_assessment_decision_table.json"
EXPECTED_CONTEXT = {
    "payload_class": "NESIRA_PHASE2_SIGNATURE_TEST_PAYLOAD",
    "subject": "legacy-db-primary",
    "candidate_id": "legacy-db-primary",
    "candidate_hash": "sha256:9d839fb63a0d19c728e3cfaea55e27f9e6f4a5506d65ecf38d5f3ea6fbf92d41",
    "environment": "prod-eu-1",
    "environment_id": "prod-eu-1",
    "purpose": "phase2-assessment-wiring-conformance",
    "action": "approve-nesira-assessment",
    "policy_version": "authority-policy-v1",
    "profile_id": "nesira-profile-v1",
    "profile_version": "1",
    "signer_identity": "spira://identity/signer-001",
}

REQUIRED_CASES = {
    "all_four_sufficient",
    "signature_insufficient",
    "identity_insufficient",
    "authority_insufficient",
    "attestation_insufficient",
    "signature_not_evaluated",
    "identity_not_evaluated",
    "authority_not_evaluated",
    "attestation_not_evaluated",
    "mixed_insufficient_and_not_evaluated",
    "malformed_adapter_result",
    "missing_caller_context",
    "cross_subject_mismatch",
}

FORBIDDEN_OUTPUT_KEYS = {
    "agent_" + "action",
    "combined_" + "verdict",
    "execute",
    "permission_to_" + "sev" + "er",
    "pro" + "ceed",
    "safe_to_" + "sev" + "er",
    "se" + "ver",
}


def run_assessment_wiring_harness(repo_root: Path, *, build_wheel: bool = True) -> dict[str, Any]:
    first = _run_once(repo_root, build_wheel=build_wheel)
    second = _run_once(repo_root, build_wheel=build_wheel)
    first["two_run_semantic_diff"] = int(canonical_json(_semantic_projection(first)) != canonical_json(_semantic_projection(second)))
    first["verdict"] = _verdict(first)
    return first


def _run_once(repo_root: Path, *, build_wheel: bool) -> dict[str, Any]:
    cases = _fixture_cases()
    fixture_results = [_run_case(case) for case in cases]
    fixture_results.append(_malformed_adapter_result_case())
    oracle = _oracle_metrics(repo_root)
    wheel = _check_public_wheel_exclusion(repo_root) if build_wheel else {"wheel_built": False}
    return {
        "schema": "SPIRA_NESIRA_PHASE2_ASSESSMENT_WIRING_HARNESS_RESULTS_V1",
        "fixture_results": fixture_results,
        "classification": _classification_metrics(fixture_results),
        "oracle_agreement": oracle,
        "public_wheel_exclusion": wheel,
    }


def _fixture_cases() -> list[dict[str, Any]]:
    base = _valid_request()

    def case(
        id_: str,
        expected: str,
        mutation: str | None = None,
        transform: Callable[[dict[str, Any]], None] | None = None,
    ) -> dict[str, Any]:
        current = deepcopy(base)
        if transform is not None:
            transform(current)
        return {
            "id": id_,
            "mutation": mutation,
            "request": current,
            "expected_composite_verdict": expected,
        }

    return [
        case("all_four_sufficient", VERDICT_SUFFICIENT),
        case("signature_insufficient", VERDICT_INSUFFICIENT, "signature_insufficient", _signature_insufficient),
        case("identity_insufficient", VERDICT_INSUFFICIENT, "identity_insufficient", _identity_insufficient),
        case("authority_insufficient", VERDICT_INSUFFICIENT, "authority_insufficient", _authority_insufficient),
        case("attestation_insufficient", VERDICT_INSUFFICIENT, "attestation_insufficient", _attestation_insufficient),
        case("signature_not_evaluated", VERDICT_NOT_EVALUATED, "signature_not_evaluated", lambda item: item.update({"signature_root": None})),
        case("identity_not_evaluated", VERDICT_NOT_EVALUATED, "identity_not_evaluated", lambda item: item.update({"identity_root": None})),
        case("authority_not_evaluated", VERDICT_NOT_EVALUATED, "authority_not_evaluated", lambda item: item.update({"authority_root": None})),
        case("attestation_not_evaluated", VERDICT_NOT_EVALUATED, "attestation_not_evaluated", lambda item: item.update({"attestation_root": None})),
        case("mixed_insufficient_and_not_evaluated", VERDICT_INSUFFICIENT, "mixed_insufficient_and_not_evaluated", _mixed_insufficient_and_not_evaluated),
        case("missing_caller_context", VERDICT_NOT_EVALUATED, "missing_caller_context", lambda item: item.pop("expected_context")),
        case("cross_subject_mismatch", VERDICT_INSUFFICIENT, "cross_subject_mismatch", _cross_subject_mismatch),
    ]


def _valid_request() -> dict[str, Any]:
    signature = _signature_bundle()
    identity = _identity_bundle()
    authority = _authority_bundle()
    attestation = _attestation_bundle()
    _align_signature(signature)
    _align_identity(identity)
    _align_authority(authority)
    return {
        "expected_context": dict(EXPECTED_CONTEXT),
        "signature_payload": signature["payload"],
        "signature_evidence": signature["signature_evidence"],
        "signature_root": signature["declared_root"],
        "identity_credential": identity["credential_evidence"],
        "identity_root": identity["declared_root"],
        "authority_policy_source": authority["policy_source"],
        "authority_root": authority["declared_root"],
        "attestation_evidence": attestation["attestation_evidence"],
        "attestation_root": attestation["declared_root"],
        "now_utc": signature["now_utc"],
    }


def _align_signature(bundle: dict[str, Any]) -> None:
    for target in (bundle["signature_evidence"],):
        target.update(
            {
                "subject": EXPECTED_CONTEXT["subject"],
                "environment": EXPECTED_CONTEXT["environment"],
                "purpose": EXPECTED_CONTEXT["purpose"],
                "action": EXPECTED_CONTEXT["action"],
            }
        )
    bundle["declared_root"].update(
        {
            "subject_scope": [EXPECTED_CONTEXT["subject"]],
            "environment_scope": [EXPECTED_CONTEXT["environment"]],
            "purpose_scope": [EXPECTED_CONTEXT["purpose"]],
            "action_scope": [EXPECTED_CONTEXT["action"]],
        }
    )


def _align_identity(bundle: dict[str, Any]) -> None:
    bundle["credential_evidence"].update(
        {
            "subject": EXPECTED_CONTEXT["subject"],
            "environment": EXPECTED_CONTEXT["environment"],
            "purpose": EXPECTED_CONTEXT["purpose"],
        }
    )
    bundle["declared_root"].update(
        {
            "subject_scope": [EXPECTED_CONTEXT["subject"]],
            "environment_scope": [EXPECTED_CONTEXT["environment"]],
            "purpose_scope": [EXPECTED_CONTEXT["purpose"]],
        }
    )


def _align_authority(bundle: dict[str, Any]) -> None:
    allow = {
        "entry_id": "allow-001",
        "signer_identity": EXPECTED_CONTEXT["signer_identity"],
        "subject": EXPECTED_CONTEXT["subject"],
        "environment": EXPECTED_CONTEXT["environment"],
        "purpose": EXPECTED_CONTEXT["purpose"],
        "action": EXPECTED_CONTEXT["action"],
        "policy_version": EXPECTED_CONTEXT["policy_version"],
    }
    bundle["policy_source"].update(
        {
            "subject": EXPECTED_CONTEXT["subject"],
            "environment": EXPECTED_CONTEXT["environment"],
            "purpose": EXPECTED_CONTEXT["purpose"],
            "action": EXPECTED_CONTEXT["action"],
            "policy_version": EXPECTED_CONTEXT["policy_version"],
            "allow": [allow],
            "deny": [],
        }
    )
    bundle["declared_root"].update(
        {
            "subject_scope": [EXPECTED_CONTEXT["subject"]],
            "environment_scope": [EXPECTED_CONTEXT["environment"]],
            "purpose_scope": [EXPECTED_CONTEXT["purpose"]],
            "action_scope": [EXPECTED_CONTEXT["action"]],
            "policy_version_scope": [EXPECTED_CONTEXT["policy_version"]],
        }
    )


def _signature_insufficient(item: dict[str, Any]) -> None:
    item["signature_root"]["subject_scope"] = ["other-subject"]


def _identity_insufficient(item: dict[str, Any]) -> None:
    item["identity_credential"]["subject"] = "other-subject"


def _authority_insufficient(item: dict[str, Any]) -> None:
    item["authority_policy_source"]["allow"] = []


def _attestation_insufficient(item: dict[str, Any]) -> None:
    item["attestation_evidence"]["attestation_payload"]["candidate_id"] = "other-candidate"


def _mixed_insufficient_and_not_evaluated(item: dict[str, Any]) -> None:
    _signature_insufficient(item)
    item["identity_root"] = None


def _cross_subject_mismatch(item: dict[str, Any]) -> None:
    item["signature_evidence"]["subject"] = "candidate-from-signature"
    item["identity_credential"]["subject"] = "candidate-from-identity"
    item["attestation_evidence"]["attestation_payload"]["candidate_id"] = "candidate-from-attestation"


def _run_case(case: Mapping[str, Any]) -> dict[str, Any]:
    result = assess_phase2_wiring(case["request"])
    expected = case["expected_composite_verdict"]
    return _case_result(
        id_=str(case["id"]),
        mutation=case["mutation"],
        expected=expected,
        result=result,
    )


def _malformed_adapter_result_case() -> dict[str, Any]:
    result = compose_subresults(
        {
            "signature": {"sub_verdict": "TRUST_MAGIC", "execution_marker": EXECUTION_MARKER, "assumption_ids": []},
            "identity": _synthetic_sub_result("identity", VERDICT_SUFFICIENT),
            "authority": _synthetic_sub_result("authority", VERDICT_SUFFICIENT),
            "isolation": _synthetic_sub_result("isolation", VERDICT_SUFFICIENT),
        }
    ).as_dict()
    return _case_result(
        id_="malformed_adapter_result",
        mutation="malformed_adapter_result",
        expected=VERDICT_NOT_EVALUATED,
        result=result,
    )


def _case_result(
    *,
    id_: str,
    mutation: str | None,
    expected: str,
    result: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "id": id_,
        "mutation": mutation,
        "expected_composite_verdict": expected,
        "actual_composite_verdict": result["verdict"],
        "composite_verdict_matches": result["verdict"] == expected,
        "per_domain_breakdown": result["per_domain_breakdown"],
        "assumptions": result["assumptions"],
        "trust_roots_used": result["trust_roots_used"],
        "reason_codes": result["reason_codes"],
        "not_evaluated_items": result["not_evaluated_items"],
        "blocking_items": result["blocking_items"],
        "execution_marker": result["execution_marker"],
        "has_forbidden_output_semantics": _has_forbidden_output_semantics(result),
        "carries_floor": all(item in result["assumptions"] for item in _floor()),
        "carries_pt_isolation_01": ISOLATION_CAVEAT in result["assumptions"],
    }


def _classification_metrics(results: list[dict[str, Any]]) -> dict[str, Any]:
    covered = {item["mutation"] for item in results if item["mutation"]}
    missing = sorted(REQUIRED_CASES - {item["id"] for item in results})
    mismatches = [item for item in results if not item["composite_verdict_matches"]]
    by_id = {item["id"]: item for item in results}
    return {
        "required_wiring_cases": sorted(REQUIRED_CASES),
        "covered_wiring_cases": sorted(item["id"] for item in results),
        "required_wiring_cases_without_fixture": len(missing),
        "missing_cases": missing,
        "composite_verdict_mismatches": len(mismatches),
        "mismatch_ids": [item["id"] for item in mismatches],
        "cross_subject_mismatch_produced_sufficient": int(by_id["cross_subject_mismatch"]["actual_composite_verdict"] == VERDICT_SUFFICIENT),
        "cross_subject_mismatch_not_sufficient": int(by_id["cross_subject_mismatch"]["actual_composite_verdict"] != VERDICT_SUFFICIENT),
        "outputs_missing_floor": sum(1 for item in results if not item["carries_floor"]),
        "sufficient_outputs_missing_pt_isolation_01": sum(
            1
            for item in results
            if item["actual_composite_verdict"] == VERDICT_SUFFICIENT and not item["carries_pt_isolation_01"]
        ),
        "outputs_with_forbidden_semantics": sum(1 for item in results if item["has_forbidden_output_semantics"]),
    }


def _oracle_metrics(repo_root: Path) -> dict[str, Any]:
    table = json.loads((repo_root / ORACLE).read_text(encoding="utf-8"))
    rows = table["rows"]
    keys = set()
    disagreements = []
    missing_required_assumptions = []
    for row in rows:
        inputs = row["inputs"]
        key = tuple(inputs[f"{domain}_sub"] for domain in DOMAINS)
        keys.add(key)
        subresults = {
            domain: _synthetic_sub_result(domain, inputs[f"{domain}_sub"])
            for domain in DOMAINS
        }
        actual = compose_subresults(subresults).as_dict()
        if actual["verdict"] != row["composite_verdict"]:
            disagreements.append(row["row_id"])
        required = set(row["required_explicit_assumption_ids"])
        if not required.issubset(set(actual["assumptions"])):
            missing_required_assumptions.append(row["row_id"])
    return {
        "oracle_rows": len(rows),
        "unique_oracle_keys": len(keys),
        "expected_oracle_rows": 81,
        "duplicate_oracle_keys": len(rows) - len(keys),
        "wiring_rows_checked": len(rows),
        "wiring_oracle_disagreements": len(disagreements),
        "disagreement_rows": disagreements,
        "oracle_required_assumption_failures": len(missing_required_assumptions),
        "oracle_required_assumption_failure_rows": missing_required_assumptions,
    }


def _synthetic_sub_result(domain: str, verdict: str) -> dict[str, Any]:
    assumptions = list(_floor())
    if verdict != VERDICT_NOT_EVALUATED:
        assumptions.extend([f"PT-{domain.upper()}-FIXTURE"])
    if domain == "isolation" and verdict != VERDICT_NOT_EVALUATED:
        assumptions.append(ISOLATION_CAVEAT)
    return {
        "sub_verdict": verdict,
        "declared_root_id": f"{domain}-root",
        "declared_root_version": "1",
        "assumption_ids": sorted(set(assumptions)),
        "not_evaluated_items": [] if verdict != VERDICT_NOT_EVALUATED else [f"{domain} not evaluated"],
        "blocking_items": [] if verdict != VERDICT_INSUFFICIENT else [f"{domain} insufficient"],
        "evidence_references": [f"{domain}-evidence"] if verdict != VERDICT_NOT_EVALUATED else [],
        "reason_codes": [f"{domain.upper()}_{verdict}"],
        "execution_marker": EXECUTION_MARKER,
    }


def _floor() -> list[str]:
    from spira_core.nesira_phase2_signature_adapter import FLOOR_ASSUMPTIONS

    return list(FLOOR_ASSUMPTIONS)


def _check_public_wheel_exclusion(repo_root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp:
        out_dir = Path(tmp)
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
    blocked_fragments = [
        "nesira_phase2_assessment_wiring",
        "nesira_phase2_signature",
        "nesira_phase2_identity",
        "nesira_phase2_authority",
        "nesira_phase2_isolation_attestation",
    ]
    blocked_entries = [name for name in names if any(fragment in name for fragment in blocked_fragments)]
    cryptography_entries = [name for name in names if "cryptography" in name.lower()]
    dependency_headers = [
        line
        for line in metadata.splitlines()
        if line.startswith("Requires-Dist:") or line.startswith("Provides-Extra:")
    ]
    return {
        "wheel_built": True,
        "blocked_entries": blocked_entries,
        "cryptography_entries": cryptography_entries,
        "metadata_dependency_headers": dependency_headers,
        "metadata_mentions_new_dependency": "cryptography" in metadata.lower(),
        "wheel_exclusion_failures": len(blocked_entries) + len(cryptography_entries) + len(dependency_headers),
    }


def _has_forbidden_output_semantics(value: Any) -> bool:
    stack = [value]
    while stack:
        current = stack.pop()
        if isinstance(current, Mapping):
            for key, nested in current.items():
                if str(key).lower() in FORBIDDEN_OUTPUT_KEYS:
                    return True
                stack.append(nested)
        elif isinstance(current, list):
            stack.extend(current)
    return False


def _semantic_projection(results: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_results": results["fixture_results"],
        "classification": results["classification"],
        "oracle_agreement": results["oracle_agreement"],
        "public_wheel_exclusion": results["public_wheel_exclusion"],
    }


def _verdict(results: Mapping[str, Any]) -> str:
    failures = [
        results["classification"]["required_wiring_cases_without_fixture"],
        results["classification"]["composite_verdict_mismatches"],
        results["classification"]["cross_subject_mismatch_produced_sufficient"],
        results["classification"]["outputs_missing_floor"],
        results["classification"]["sufficient_outputs_missing_pt_isolation_01"],
        results["classification"]["outputs_with_forbidden_semantics"],
        results["oracle_agreement"]["duplicate_oracle_keys"],
        results["oracle_agreement"]["wiring_oracle_disagreements"],
        results["oracle_agreement"]["oracle_required_assumption_failures"],
        results["public_wheel_exclusion"].get("wheel_exclusion_failures", 0),
        results.get("two_run_semantic_diff", 1),
    ]
    if any(failures):
        return "NESIRA_PHASE2_ASSESSMENT_WIRING_NEEDS_REVISION"
    return "NESIRA_PHASE2_ASSESSMENT_WIRING_ACCEPTED"
