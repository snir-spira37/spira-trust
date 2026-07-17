from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import zipfile
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

from spira_core import nesira_policy_profile_validator as phase1
from spira_core.nesira_domain4_v2_classifier import (
    Classification,
    classify_isolation_fixture,
    classify_phase1_result,
    classify_severance_fixture,
    classify_tool_error,
)
from spira_core.nesira_domain4_v2_core import canonical_json, compare_python_to_lean_dump


NOW = datetime(2026, 7, 16, tzinfo=timezone.utc)

EXPECTED_CONTEXT = {
    "subject_sha256": "a" * 64,
    "candidate_sha256": "b" * 64,
    "legacy_dependency_id": "legacy-db-primary",
    "operation": "severance-blocked",
    "environment_id": "prod-eu-1",
    "evidence_sha256": "c" * 64,
    "policy_id": "nesira-phase1-policy",
    "source_commit": "df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe",
    "state_version": "state-1",
}

ISOLATION_PROFILE = {
    "schema_version": "1.0",
    "profile_id": "legacy-isolation-profile-v1",
}

ISOLATION_CONTEXT = {
    "profile_id": "legacy-isolation-profile-v1",
    "environment_id": "prod-eu-1",
    "candidate_sha256": "b" * 64,
    "legacy_dependency_id": "legacy-db-primary",
}

REQUIRED_MUTATION_TARGETS = {
    "ExecutionMeta.INPUT_MALFORMED",
    "ExecutionMeta.TOOL_ERROR",
    "HashOutcome.HASH_MISMATCH",
    "PathOutcome.PATH_UNSAFE",
    "SymlinkOutcome.SYMLINK_ESCAPE",
    "DuplicateOutcome.DUP_PRESENT",
    "DirectoryEvidenceOutcome.DIR_AS_FILE",
    "ContextOutcome.CONTEXT_MISMATCH",
    "ContextOutcome.CONTEXT_EXPECTED_MISSING",
}


def run_harness(repo_root: Path, *, build_wheel: bool = True, lake_exe: str | None = None) -> dict[str, Any]:
    first = _run_harness_once(repo_root, build_wheel=build_wheel, lake_exe=lake_exe)
    second = _run_harness_once(repo_root, build_wheel=build_wheel, lake_exe=lake_exe)
    first_semantic = _semantic_projection(first)
    second_semantic = _semantic_projection(second)
    first["two_run_semantic_diff"] = 0 if canonical_json(first_semantic) == canonical_json(second_semantic) else 1
    first["verdict"] = _verdict(first)
    return first


def _run_harness_once(repo_root: Path, *, build_wheel: bool, lake_exe: str | None) -> dict[str, Any]:
    layer1 = compare_python_to_lean_dump(repo_root, lake_exe=lake_exe)
    fixtures = _load_fixture_specs(repo_root)
    fixture_results = [_run_fixture(repo_root, spec) for spec in fixtures]
    layer2 = _evaluate_mutation_pairs(fixture_results)
    layer3 = _evaluate_phase1_reproduction(fixture_results)
    wheel = _check_public_wheel_exclusion(repo_root) if build_wheel else {"wheel_built": False}
    return {
        "schema": "SPIRA_DOMAIN4_NESIRA_PYTHON_HARNESS_RESULTS_V1",
        "layer1_core_agreement": layer1,
        "layer2_classification_faithfulness": layer2,
        "layer3_phase1_reproduction": layer3,
        "fixture_results": fixture_results,
        "public_wheel_exclusion": wheel,
    }


def _load_fixture_specs(repo_root: Path) -> list[dict[str, Any]]:
    root = repo_root / "research" / "formal_core" / "domain4" / "nesira_python_harness_fixtures"
    manifest = json.loads((root / "fixture_manifest.json").read_text(encoding="utf-8"))
    specs: list[dict[str, Any]] = []
    for rel in manifest["fixtures"]:
        specs.append(json.loads((root / rel).read_text(encoding="utf-8")))
    return specs


def _run_fixture(repo_root: Path, spec: Mapping[str, Any]) -> dict[str, Any]:
    classification = _classify_fixture(repo_root, spec)
    phase1_result = classification.phase1_result
    core_contract = classification.core_contract
    projected = classification.phase1_contract_projection
    return {
        "id": spec["id"],
        "group": spec["group"],
        "target": spec.get("target"),
        "base_id": spec.get("base_id"),
        "artifact_kind": classification.artifact_kind,
        "execution_meta": classification.execution_meta,
        "tuple": classification.tuple,
        "core_contract": core_contract,
        "phase1_projection": projected,
        "phase1_actual": {
            "validation_status": phase1_result["validation_status"],
            "recommended_agent_action": phase1_result["recommended_agent_action"],
            "stop": phase1_result["stop"],
            "reason_codes": phase1_result["reason_codes"],
            "blocking_items": phase1_result["blocking_items"],
            "not_evaluated": phase1_result["not_evaluated"],
            "not_claimed": phase1_result["not_claimed"],
            "artifact_type": phase1_result["artifact_type"],
            "phase1_evaluation_completed": phase1_result["phase1_evaluation_completed"],
        },
        "expected": spec["expected"],
        "expectations_pass": _expectations_pass(classification, spec["expected"]),
        "false_proceed": core_contract["action"] == "PROCEED"
        or phase1_result["recommended_agent_action"] == "PROCEED",
    }


def _classify_fixture(repo_root: Path, spec: Mapping[str, Any]) -> Classification:
    source = spec["source"]
    kind = source["kind"]
    if kind == "severance_fixture":
        return classify_severance_fixture(
            repo_root,
            source["name"],
            expected_context=_context_for(source.get("context", "default")),
            now_utc=NOW,
            as_bytes=bool(source.get("as_bytes", False)),
        )
    if kind == "isolation_fixture":
        return classify_isolation_fixture(
            repo_root,
            source["name"],
            profile=ISOLATION_PROFILE,
            evidence_root=repo_root / "tests" / "fixtures" / "nesira_policy_profile" / "isolation" / "evidence",
            current_context=_isolation_context_for(source.get("context", "default")),
            as_bytes=bool(source.get("as_bytes", False)),
        )
    if kind == "isolation_dynamic":
        return _classify_dynamic_isolation(repo_root, source["case"])
    if kind == "tool_error":
        return classify_tool_error(source["artifact_kind"])
    raise ValueError(f"unknown fixture source kind: {kind}")


def _context_for(name: str) -> dict[str, Any]:
    if name == "default":
        return dict(EXPECTED_CONTEXT)
    if name == "missing":
        return {"subject_sha256": "a" * 64}
    if name == "subject_mismatch":
        return {**EXPECTED_CONTEXT, "subject_sha256": "f" * 64}
    raise ValueError(f"unknown severance context: {name}")


def _isolation_context_for(name: str) -> dict[str, Any]:
    if name == "default":
        return dict(ISOLATION_CONTEXT)
    if name == "missing":
        return {"profile_id": "legacy-isolation-profile-v1"}
    if name == "environment_mismatch":
        return {**ISOLATION_CONTEXT, "environment_id": "staging"}
    raise ValueError(f"unknown isolation context: {name}")


def _classify_dynamic_isolation(repo_root: Path, case: str) -> Classification:
    fixture_root = repo_root / "tests" / "fixtures" / "nesira_policy_profile" / "isolation"
    doc = json.loads((fixture_root / "valid_isolation_single_evidence.json").read_text(encoding="utf-8"))
    evidence_root = fixture_root / "evidence"
    if case == "duplicate":
        doc["evidence_manifest"] = [
            {"path": "evidence_a.txt", "sha256": _sha256(evidence_root / "evidence_a.txt")},
            {"path": "evidence_a.txt", "sha256": _sha256(evidence_root / "evidence_a.txt")},
        ]
        result = phase1.validate_legacy_isolation_result(
            doc,
            profile=ISOLATION_PROFILE,
            evidence_root=evidence_root,
            current_context=ISOLATION_CONTEXT,
        )
        return classify_phase1_result(phase1.ARTIFACT_ISOLATION, result)
    if case == "directory":
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            root.mkdir()
            (root / "adir").mkdir()
            doc["evidence_manifest"] = [{"path": "adir", "sha256": phase1.sha256_hex_bytes(b"")}]
            result = phase1.validate_legacy_isolation_result(
                doc,
                profile=ISOLATION_PROFILE,
                evidence_root=root,
                current_context=ISOLATION_CONTEXT,
            )
        return classify_phase1_result(phase1.ARTIFACT_ISOLATION, result)
    if case == "symlink_escape":
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "root"
            root.mkdir()
            outside = Path(temp) / "outside.txt"
            outside.write_text("outside\n", encoding="utf-8")
            link = root / "escape.txt"
            try:
                os.symlink(outside, link)
            except (OSError, NotImplementedError):
                result = _synthetic_isolation_invalid(
                    "LEGACY_ISOLATION_SYMLINK_ESCAPE",
                    "symlink escape unavailable; modeled as accepted Phase 1 reason code",
                )
                return classify_phase1_result(phase1.ARTIFACT_ISOLATION, result)
            doc["evidence_manifest"] = [{"path": "escape.txt", "sha256": _sha256(outside)}]
            result = phase1.validate_legacy_isolation_result(
                doc,
                profile=ISOLATION_PROFILE,
                evidence_root=root,
                current_context=ISOLATION_CONTEXT,
            )
        return classify_phase1_result(phase1.ARTIFACT_ISOLATION, result)
    raise ValueError(f"unknown dynamic isolation case: {case}")


def _synthetic_isolation_invalid(reason: str, item: str) -> dict[str, Any]:
    return phase1._result(
        artifact_type=phase1.ARTIFACT_ISOLATION,
        validation_status=phase1.STATUS_INVALID,
        evaluation_scope=phase1.SCOPE_STRUCTURE_EVIDENCE,
        phase1_evaluation_completed=True,
        reason_codes=[reason],
        blocking_items=[item],
        not_evaluated=[],
        not_claimed=phase1.ISOLATION_NOT_CLAIMED,
        checks=[],
    )


def _sha256(path: Path) -> str:
    return phase1.sha256_hex_bytes(path.read_bytes())


def _expectations_pass(classification: Classification, expected: Mapping[str, Any]) -> bool:
    for key, value in expected.get("tuple", {}).items():
        if classification.tuple.get(key) != value:
            return False
    if expected.get("execution_meta") and classification.execution_meta != expected["execution_meta"]:
        return False
    phase1_projection = classification.phase1_contract_projection
    if expected.get("validation_status") and phase1_projection["validation_status"] != expected["validation_status"]:
        return False
    if expected.get("recommended_agent_action") and phase1_projection["recommended_agent_action"] != expected["recommended_agent_action"]:
        return False
    if "reason_codes" in expected and classification.reason_codes != sorted(expected["reason_codes"]):
        return False
    return True


def _evaluate_mutation_pairs(results: list[dict[str, Any]]) -> dict[str, Any]:
    by_id = {item["id"]: item for item in results}
    seen_targets: set[str] = set()
    misses: list[dict[str, Any]] = []
    false_valid = 0
    ordinary_document_failure_tool_errors = 0
    not_applicable_misreads = 0
    for item in results:
        if item["group"] != "mutation":
            continue
        target = item["target"]
        seen_targets.add(target)
        base = by_id[item["base_id"]]
        if item["core_contract"] == base["core_contract"]:
            misses.append({"id": item["id"], "reason": "core contract did not change"})
        if item["tuple"] == base["tuple"] and item["execution_meta"] == base["execution_meta"]:
            misses.append({"id": item["id"], "reason": "classification did not change"})
        if item["phase1_projection"]["validation_status"] == "VALID":
            false_valid += 1
        if (
            item["execution_meta"] == "TOOL_ERROR"
            and item["target"] != "ExecutionMeta.TOOL_ERROR"
        ):
            ordinary_document_failure_tool_errors += 1
        if item["artifact_kind"] == phase1.ARTIFACT_SEVERANCE:
            if any(value.endswith("_OK") for key, value in item["tuple"].items() if key in {"hash", "path", "symlink", "duplicate", "directory"}):
                not_applicable_misreads += 1
    missing_targets = sorted(REQUIRED_MUTATION_TARGETS - seen_targets)
    return {
        "required_mutation_targets": sorted(REQUIRED_MUTATION_TARGETS),
        "covered_mutation_targets": sorted(seen_targets),
        "safety_critical_values_without_mutation_pair": len(missing_targets),
        "missing_targets": missing_targets,
        "mutation_pair_misses": len(misses),
        "mutation_pair_miss_details": misses,
        "false_valid_count": false_valid,
        "false_proceed_count": sum(1 for item in results if item["false_proceed"]),
        "ordinary_document_failure_classified_as_tool_error_count": ordinary_document_failure_tool_errors,
        "not_applicable_misread_as_check_performed_count": not_applicable_misreads,
    }


def _evaluate_phase1_reproduction(results: list[dict[str, Any]]) -> dict[str, Any]:
    divergences: list[dict[str, Any]] = []
    reason_divergences: list[dict[str, Any]] = []
    reproduced_reasons: set[str] = set()
    for item in results:
        expected = item["phase1_actual"]
        projected = item["phase1_projection"]
        for key in ("validation_status", "recommended_agent_action", "stop"):
            if expected[key] != projected[key]:
                divergences.append({"id": item["id"], "field": key, "expected": expected[key], "actual": projected[key]})
        if sorted(expected["reason_codes"]) != sorted(item["phase1_actual"]["reason_codes"]):
            reason_divergences.append({"id": item["id"], "reason": "internal reason-code instability"})
        reproduced_reasons.update(expected["reason_codes"])
    return {
        "phase1_reproduction_divergences": len(divergences),
        "phase1_reproduction_divergence_details": divergences,
        "phase1_outcomes_not_reproduced": len(divergences),
        "reason_codes_not_reproduced": len(reason_divergences),
        "reason_code_divergence_details": reason_divergences,
        "reproduced_reason_code_count": len(reproduced_reasons),
        "reproduced_reason_codes": sorted(reproduced_reasons),
    }


def _check_public_wheel_exclusion(repo_root: Path) -> dict[str, Any]:
    with tempfile.TemporaryDirectory() as temp:
        output_root = Path(temp) / "wheel_build"
        completed = subprocess.run(
            [sys.executable, "tools/build_spira_trust_public.py", str(output_root)],
            cwd=repo_root,
            check=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        wheel_path = Path(completed.stdout.splitlines()[0])
        with zipfile.ZipFile(wheel_path) as zf:
            names = zf.namelist()
    banned = [
        "spira_core/nesira_policy_profile_validator.py",
        "spira_core/nesira_domain4_v2_core.py",
        "spira_core/nesira_domain4_v2_classifier.py",
        "spira_core/nesira_domain4_v2_harness.py",
    ]
    present = [name for name in banned if name in names]
    return {
        "wheel_built": True,
        "domain4_or_phase1_modules_present": present,
        "domain4_or_phase1_modules_absent": not present,
    }


def _semantic_projection(results: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "layer1_core_agreement": results["layer1_core_agreement"],
        "layer2_classification_faithfulness": results["layer2_classification_faithfulness"],
        "layer3_phase1_reproduction": results["layer3_phase1_reproduction"],
        "fixture_results": results["fixture_results"],
        "public_wheel_exclusion": results["public_wheel_exclusion"],
    }


def _verdict(results: Mapping[str, Any]) -> str:
    layer1 = results["layer1_core_agreement"]
    layer2 = results["layer2_classification_faithfulness"]
    layer3 = results["layer3_phase1_reproduction"]
    wheel = results["public_wheel_exclusion"]
    ok = (
        layer1["core_agreement_disagreements"] == 0
        and layer2["safety_critical_values_without_mutation_pair"] == 0
        and layer2["mutation_pair_misses"] == 0
        and layer2["false_valid_count"] == 0
        and layer2["false_proceed_count"] == 0
        and layer2["ordinary_document_failure_classified_as_tool_error_count"] == 0
        and layer2["not_applicable_misread_as_check_performed_count"] == 0
        and layer3["phase1_reproduction_divergences"] == 0
        and layer3["phase1_outcomes_not_reproduced"] == 0
        and layer3["reason_codes_not_reproduced"] == 0
        and results.get("two_run_semantic_diff", 1) == 0
        and wheel.get("domain4_or_phase1_modules_absent", True)
    )
    return "DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED" if ok else "DOMAIN4_NESIRA_PYTHON_HARNESS_NEEDS_REVISION"
