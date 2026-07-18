from __future__ import annotations

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
from spira_core.nesira_phase2_authority_adapter import (
    VERDICT_INSUFFICIENT,
    VERDICT_NOT_EVALUATED,
    VERDICT_SUFFICIENT,
    assess_authority,
)


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)
EXPECTED_CONTEXT = {
    "subject": "legacy-db-primary",
    "environment": "prod-eu-1",
    "purpose": "phase2-authority-adapter-conformance",
    "action": "approve-nesira-assessment",
    "policy_version": "authority-policy-v1",
}
ORACLE = Path("research") / "nesira_policy_profile" / "nesira_phase2_assessment_decision_table.json"

REQUIRED_FAILURE_MODES = {
    "missing_authority_policy_root",
    "ambiguous_authority_policy_root",
    "malformed_authority_policy_root",
    "policy_source_missing",
    "policy_source_malformed",
    "unsupported_policy_type",
    "established_identity_missing",
    "identity_sub_verdict_not_sufficient",
    "explicit_deny",
    "identity_absent_from_policy",
    "action_not_allowed",
    "subject_context_mismatch",
    "environment_context_mismatch",
    "purpose_context_mismatch",
    "policy_version_mismatch",
    "policy_root_mismatch",
    "policy_version_stale",
    "policy_expired",
    "policy_not_yet_valid",
    "policy_revoked",
    "revocation_unknown",
    "revocation_stale",
    "revocation_unreachable",
    "clock_missing",
    "clock_untrusted",
}

FORBIDDEN_OUTPUT_KEYS = {
    "execute",
    "sever",
    "permission_to_sever",
    "authorized_to_sever",
    "safe_to_sever",
    "isolation_occurred",
    "isolation_proven",
    "identity_verified",
    "signature_verified",
}


def run_authority_harness(repo_root: Path, *, build_wheel: bool = True) -> dict[str, Any]:
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
        "schema": "SPIRA_NESIRA_PHASE2_AUTHORITY_ADAPTER_HARNESS_RESULTS_V1",
        "fixture_results": results,
        "classification": _classification_metrics(results),
        "end_to_end_composition": end_to_end,
        "public_wheel_exclusion": wheel,
        "dependency_boundary": {
            "new_dependencies": [],
            "pyproject_change_required": False,
        },
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
            "policy_source": current["policy_source"],
            "declared_root": current["declared_root"],
            "established_identity": current["established_identity"],
            "identity_sub_verdict": current["identity_sub_verdict"],
            "expected_context": current["expected_context"],
            "now_utc": current["now_utc"],
            "expected_sub_verdict": expected,
        }

    return [
        case("valid_explicit_allow", VERDICT_SUFFICIENT),
        case("missing_authority_policy_root", VERDICT_NOT_EVALUATED, "missing_authority_policy_root", lambda item: item.update({"declared_root": None})),
        case("ambiguous_authority_policy_root", VERDICT_NOT_EVALUATED, "ambiguous_authority_policy_root", lambda item: item["declared_root"].update({"ambiguous_authority_roots": True})),
        case("malformed_authority_policy_root", VERDICT_NOT_EVALUATED, "malformed_authority_policy_root", lambda item: item["declared_root"].pop("trust_root_kind")),
        case("policy_source_missing", VERDICT_NOT_EVALUATED, "policy_source_missing", lambda item: item.update({"policy_source": None})),
        case("policy_source_malformed", VERDICT_NOT_EVALUATED, "policy_source_malformed", lambda item: item["policy_source"].pop("allow")),
        case("unsupported_policy_type", VERDICT_NOT_EVALUATED, "unsupported_policy_type", lambda item: item["policy_source"].update({"policy_type": "UNSUPPORTED"})),
        case("established_identity_missing", VERDICT_NOT_EVALUATED, "established_identity_missing", lambda item: item.update({"established_identity": None})),
        case("identity_sub_verdict_not_sufficient", VERDICT_NOT_EVALUATED, "identity_sub_verdict_not_sufficient", lambda item: item.update({"identity_sub_verdict": VERDICT_NOT_EVALUATED})),
        case("explicit_deny", VERDICT_INSUFFICIENT, "explicit_deny", _explicit_deny),
        case("identity_absent_from_policy", VERDICT_INSUFFICIENT, "identity_absent_from_policy", _identity_absent_from_policy),
        case("action_not_allowed", VERDICT_INSUFFICIENT, "action_not_allowed", _action_not_allowed),
        case("subject_context_mismatch", VERDICT_INSUFFICIENT, "subject_context_mismatch", lambda item: item["policy_source"].update({"subject": "other-subject"})),
        case("environment_context_mismatch", VERDICT_INSUFFICIENT, "environment_context_mismatch", lambda item: item["policy_source"].update({"environment": "staging"})),
        case("purpose_context_mismatch", VERDICT_INSUFFICIENT, "purpose_context_mismatch", lambda item: item["policy_source"].update({"purpose": "other-purpose"})),
        case("policy_version_mismatch", VERDICT_INSUFFICIENT, "policy_version_mismatch", lambda item: item["policy_source"].update({"policy_version": "authority-policy-v2"})),
        case("policy_root_mismatch", VERDICT_INSUFFICIENT, "policy_root_mismatch", lambda item: item["policy_source"].update({"authority_root_id": "other-authority-root"})),
        case("policy_version_stale", VERDICT_INSUFFICIENT, "policy_version_stale", lambda item: item["declared_root"].update({"policy_version_scope": ["authority-policy-v2"]})),
        case("policy_expired", VERDICT_INSUFFICIENT, "policy_expired", lambda item: item["policy_source"].update({"valid_from": "2025-01-01T00:00:00Z", "valid_until": "2025-12-31T00:00:00Z"})),
        case("policy_not_yet_valid", VERDICT_INSUFFICIENT, "policy_not_yet_valid", lambda item: item["policy_source"].update({"valid_from": "2027-01-01T00:00:00Z", "valid_until": "2027-12-31T00:00:00Z"})),
        case("policy_revoked", VERDICT_INSUFFICIENT, "policy_revoked", lambda item: item["policy_source"].update({"revocation": {"status": "REVOKED", "freshness": "FRESH"}})),
        case("revocation_unknown", VERDICT_NOT_EVALUATED, "revocation_unknown", lambda item: item["policy_source"].update({"revocation": {"status": "UNKNOWN", "freshness": "FRESH"}})),
        case("revocation_stale", VERDICT_NOT_EVALUATED, "revocation_stale", lambda item: item["policy_source"].update({"revocation": {"status": "GOOD", "freshness": "STALE"}})),
        case("revocation_unreachable", VERDICT_NOT_EVALUATED, "revocation_unreachable", lambda item: item["policy_source"].update({"revocation": {"status": "UNREACHABLE", "freshness": "UNKNOWN"}})),
        case("clock_missing", VERDICT_NOT_EVALUATED, "clock_missing", lambda item: item.update({"now_utc": None})),
        case("clock_untrusted", VERDICT_NOT_EVALUATED, "clock_untrusted", lambda item: item.update({"now_utc": datetime(2026, 7, 16)})),
    ]


def _valid_bundle() -> dict[str, Any]:
    allow_entry = {
        "entry_id": "allow-001",
        "signer_identity": "spira://identity/signer-001",
        "subject": EXPECTED_CONTEXT["subject"],
        "environment": EXPECTED_CONTEXT["environment"],
        "purpose": EXPECTED_CONTEXT["purpose"],
        "action": EXPECTED_CONTEXT["action"],
        "policy_version": EXPECTED_CONTEXT["policy_version"],
    }
    return {
        "policy_source": {
            "evidence_id": "authority-policy-fixture-001",
            "authority_root_id": "authority-root-main",
            "authority_root_version": "1",
            "policy_type": "SPIRA_AUTHORITY_POLICY_V1",
            "policy_id": "authority-policy-main",
            "policy_version": EXPECTED_CONTEXT["policy_version"],
            "subject": EXPECTED_CONTEXT["subject"],
            "environment": EXPECTED_CONTEXT["environment"],
            "purpose": EXPECTED_CONTEXT["purpose"],
            "action": EXPECTED_CONTEXT["action"],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
            "revocation": {"status": "GOOD", "freshness": "FRESH"},
            "allow": [allow_entry],
            "deny": [],
        },
        "declared_root": {
            "trust_root_id": "authority-root-main",
            "version": "1",
            "trust_root_kind": "AUTHORITY_POLICY_SOURCE",
            "accepted_policy_types": ["SPIRA_AUTHORITY_POLICY_V1"],
            "subject_scope": [EXPECTED_CONTEXT["subject"]],
            "environment_scope": [EXPECTED_CONTEXT["environment"]],
            "purpose_scope": [EXPECTED_CONTEXT["purpose"]],
            "action_scope": [EXPECTED_CONTEXT["action"]],
            "policy_version_scope": [EXPECTED_CONTEXT["policy_version"]],
            "valid_from": "2026-01-01T00:00:00Z",
            "valid_until": "2026-12-31T00:00:00Z",
            "revocation": {"status": "GOOD", "freshness": "FRESH"},
        },
        "established_identity": {"signer_identity": "spira://identity/signer-001"},
        "identity_sub_verdict": VERDICT_SUFFICIENT,
        "expected_context": dict(EXPECTED_CONTEXT),
        "now_utc": NOW,
    }


def _explicit_deny(item: dict[str, Any]) -> None:
    item["policy_source"]["deny"] = [dict(item["policy_source"]["allow"][0], entry_id="deny-001")]


def _identity_absent_from_policy(item: dict[str, Any]) -> None:
    item["policy_source"]["allow"] = [
        dict(item["policy_source"]["allow"][0], entry_id="allow-other-identity", signer_identity="spira://identity/other")
    ]


def _action_not_allowed(item: dict[str, Any]) -> None:
    item["policy_source"]["allow"] = [
        dict(item["policy_source"]["allow"][0], entry_id="allow-other-action", action="different-action")
    ]


def _run_case(case: Mapping[str, Any]) -> dict[str, Any]:
    result = assess_authority(
        policy_source=case["policy_source"],
        declared_root=case["declared_root"],
        established_identity=case["established_identity"],
        identity_sub_verdict=case["identity_sub_verdict"],
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
        "dependency_boundary": result["dependency_boundary"],
        "execution_marker": result["execution_marker"],
        "has_forbidden_output_semantics": _has_forbidden_output_semantics(result),
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
        "required_authority_failure_modes": sorted(REQUIRED_FAILURE_MODES),
        "covered_authority_failure_modes": sorted(covered),
        "required_authority_failure_modes_without_fixture": len(missing),
        "required_authority_failure_modes_without_mutation_pair": len(missing),
        "missing_failure_modes": missing,
        "sub_verdict_mismatches": len(mismatches),
        "mismatch_ids": [item["id"] for item in mismatches],
        "unexpected_sufficient_verdicts": len(unexpected_sufficient),
        "missing_policy_root_mapped_to_insufficient": int(by_id["missing_authority_policy_root"]["actual_sub_verdict"] == VERDICT_INSUFFICIENT),
        "identity_absent_mapped_to_not_evaluated": int(by_id["identity_absent_from_policy"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "explicit_deny_mapped_to_not_evaluated": int(by_id["explicit_deny"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "action_not_allowed_mapped_to_not_evaluated": int(by_id["action_not_allowed"]["actual_sub_verdict"] == VERDICT_NOT_EVALUATED),
        "default_allow_paths": int(by_id["identity_absent_from_policy"]["actual_sub_verdict"] == VERDICT_SUFFICIENT or by_id["action_not_allowed"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "soft_pass_revocation_unknown": int(by_id["revocation_unknown"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "soft_pass_clock_failure": int(by_id["clock_missing"]["actual_sub_verdict"] == VERDICT_SUFFICIENT or by_id["clock_untrusted"]["actual_sub_verdict"] == VERDICT_SUFFICIENT),
        "authority_outputs_with_identity_verification_semantics": sum(1 for item in results if item["dependency_boundary"].get("identity_verification_performed") is True),
        "authority_outputs_with_execution_semantics": sum(1 for item in results if item["has_forbidden_output_semantics"]),
    }


def _end_to_end_composition(repo_root: Path, results: list[dict[str, Any]]) -> dict[str, Any]:
    oracle = _load_composition_oracle(repo_root)
    rows = []
    mismatches = []
    expected_by_authority = {
        VERDICT_SUFFICIENT: VERDICT_NOT_EVALUATED,
        VERDICT_NOT_EVALUATED: VERDICT_NOT_EVALUATED,
        VERDICT_INSUFFICIENT: VERDICT_INSUFFICIENT,
    }
    for authority_verdict, expected_composite in expected_by_authority.items():
        composite = oracle[authority_verdict]
        row = {
            "signature_sub": VERDICT_SUFFICIENT,
            "identity_sub": VERDICT_SUFFICIENT,
            "authority_sub": authority_verdict,
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
            and inputs["identity_sub"] == VERDICT_SUFFICIENT
            and inputs["isolation_sub"] == VERDICT_NOT_EVALUATED
        ):
            mapping[inputs["authority_sub"]] = row["composite_verdict"]
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
        adapter_entries = [name for name in names if "nesira_phase2_authority" in name]
        dependency_headers = [
            line
            for line in metadata.splitlines()
            if line.startswith(("Requires-Dist:", "Provides-Extra:"))
        ]
        return {
            "wheel_built": True,
            "adapter_entries": adapter_entries,
            "metadata_dependency_headers": dependency_headers,
            "metadata_mentions_new_dependency": bool(dependency_headers),
            "wheel_exclusion_failures": len(adapter_entries) + int(bool(dependency_headers)),
        }


class _temporary_wheel_dir:
    def __init__(self) -> None:
        self._temp: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> Path:
        self._temp = tempfile.TemporaryDirectory(prefix="spira_nesira_authority_wheel_")
        self.path = Path(self._temp.name)
        return self.path

    def __exit__(self, *_exc: object) -> None:
        if self._temp is not None:
            self._temp.cleanup()


def _has_forbidden_output_semantics(result: Mapping[str, Any]) -> bool:
    return any(key in result for key in FORBIDDEN_OUTPUT_KEYS)


def _semantic_projection(results: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_results": results["fixture_results"],
        "classification": results["classification"],
        "end_to_end_composition": results["end_to_end_composition"],
        "public_wheel_exclusion": results["public_wheel_exclusion"],
        "dependency_boundary": results["dependency_boundary"],
    }


def _verdict(results: Mapping[str, Any]) -> str:
    checks = [
        results["classification"]["required_authority_failure_modes_without_fixture"],
        results["classification"]["required_authority_failure_modes_without_mutation_pair"],
        results["classification"]["sub_verdict_mismatches"],
        results["classification"]["unexpected_sufficient_verdicts"],
        results["classification"]["missing_policy_root_mapped_to_insufficient"],
        results["classification"]["identity_absent_mapped_to_not_evaluated"],
        results["classification"]["explicit_deny_mapped_to_not_evaluated"],
        results["classification"]["action_not_allowed_mapped_to_not_evaluated"],
        results["classification"]["default_allow_paths"],
        results["classification"]["soft_pass_revocation_unknown"],
        results["classification"]["soft_pass_clock_failure"],
        results["classification"]["authority_outputs_with_identity_verification_semantics"],
        results["classification"]["authority_outputs_with_execution_semantics"],
        results["end_to_end_composition"]["composition_mismatches"],
        results["public_wheel_exclusion"].get("wheel_exclusion_failures", 0),
        results["two_run_semantic_diff"],
    ]
    if any(check != 0 for check in checks):
        return "NESIRA_PHASE2_AUTHORITY_ADAPTER_NEEDS_REVISION"
    return "NESIRA_PHASE2_AUTHORITY_ADAPTER_ACCEPTED"
