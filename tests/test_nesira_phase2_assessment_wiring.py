from __future__ import annotations

import tomllib
import zipfile
from pathlib import Path

from spira_core import nesira_phase2_assessment_wiring as wiring
from spira_core.nesira_phase2_assessment_wiring_harness import run_assessment_wiring_harness


ROOT = Path(__file__).resolve().parents[1]


def test_assessment_wiring_harness_accepts_authorized_corpus():
    results = run_assessment_wiring_harness(ROOT, build_wheel=False)

    assert results["verdict"] == "NESIRA_PHASE2_ASSESSMENT_WIRING_ACCEPTED"
    assert results["classification"]["required_wiring_cases_without_fixture"] == 0
    assert results["classification"]["composite_verdict_mismatches"] == 0
    assert results["classification"]["outputs_missing_floor"] == 0
    assert results["classification"]["sufficient_outputs_missing_pt_isolation_01"] == 0
    assert results["classification"]["outputs_with_forbidden_semantics"] == 0
    assert results["oracle_agreement"]["wiring_rows_checked"] == 81
    assert results["oracle_agreement"]["wiring_oracle_disagreements"] == 0
    assert results["oracle_agreement"]["oracle_required_assumption_failures"] == 0
    assert results["two_run_semantic_diff"] == 0


def test_cross_subject_mismatch_is_not_sufficient():
    results = run_assessment_wiring_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}
    case = by_id["cross_subject_mismatch"]

    assert case["actual_composite_verdict"] != wiring.VERDICT_SUFFICIENT
    assert case["actual_composite_verdict"] == wiring.VERDICT_INSUFFICIENT
    assert results["classification"]["cross_subject_mismatch_produced_sufficient"] == 0
    assert results["classification"]["cross_subject_mismatch_not_sufficient"] == 1


def test_assessment_wiring_respects_strict_and_oracle_rows():
    results = run_assessment_wiring_harness(ROOT, build_wheel=False)
    oracle = results["oracle_agreement"]

    assert oracle["oracle_rows"] == 81
    assert oracle["unique_oracle_keys"] == 81
    assert oracle["duplicate_oracle_keys"] == 0
    assert oracle["wiring_oracle_disagreements"] == 0


def test_insufficient_dominates_not_evaluated():
    results = run_assessment_wiring_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}
    case = by_id["mixed_insufficient_and_not_evaluated"]

    assert case["actual_composite_verdict"] == wiring.VERDICT_INSUFFICIENT
    assert case["per_domain_breakdown"]["signature"] == wiring.VERDICT_INSUFFICIENT
    assert case["per_domain_breakdown"]["identity"] == wiring.VERDICT_NOT_EVALUATED


def test_sufficient_assessment_carries_full_boundary_markers():
    results = run_assessment_wiring_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}
    case = by_id["all_four_sufficient"]

    assert case["actual_composite_verdict"] == wiring.VERDICT_SUFFICIENT
    assert case["execution_marker"] == wiring.EXECUTION_MARKER
    assert "PT-ISOLATION-01" in case["assumptions"]
    assert case["carries_floor"] is True
    assert case["trust_roots_used"] == [
        "attestation-root-main@1",
        "authority-root-main@1",
        "identity-root-main@1",
        "signing-root-main@1",
    ]


def test_malformed_adapter_result_fails_closed():
    malformed = {
        "signature": {
            "sub_verdict": "TRUST_MAGIC",
            "execution_marker": wiring.EXECUTION_MARKER,
            "assumption_ids": [],
        },
        "identity": _sub(wiring.VERDICT_SUFFICIENT),
        "authority": _sub(wiring.VERDICT_SUFFICIENT),
        "isolation": _sub(wiring.VERDICT_SUFFICIENT, isolation=True),
    }
    result = wiring.compose_subresults(malformed).as_dict()

    assert result["per_domain_breakdown"]["signature"] == wiring.VERDICT_NOT_EVALUATED
    assert result["verdict"] == wiring.VERDICT_NOT_EVALUATED
    assert "signature:ASSESSMENT_WIRING_SUB_RESULT_MALFORMED" in result["reason_codes"]


def test_execution_looking_adapter_result_fails_closed():
    malformed = {
        "signature": dict(_sub(wiring.VERDICT_SUFFICIENT), **{"pro" + "ceed": True}),
        "identity": _sub(wiring.VERDICT_SUFFICIENT),
        "authority": _sub(wiring.VERDICT_SUFFICIENT),
        "isolation": _sub(wiring.VERDICT_SUFFICIENT, isolation=True),
    }
    result = wiring.compose_subresults(malformed).as_dict()

    assert result["per_domain_breakdown"]["signature"] == wiring.VERDICT_NOT_EVALUATED
    assert result["verdict"] == wiring.VERDICT_NOT_EVALUATED


def test_missing_caller_context_fails_closed():
    results = run_assessment_wiring_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}
    case = by_id["missing_caller_context"]

    assert case["actual_composite_verdict"] == wiring.VERDICT_NOT_EVALUATED
    assert set(case["per_domain_breakdown"].values()) == {wiring.VERDICT_NOT_EVALUATED}


def test_assessment_wiring_runtime_is_in_public_wheel_but_harness_is_excluded(tmp_path):
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    wheel_path = Path(result.stdout.splitlines()[0])
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert "spira_core/nesira_phase2_assessment_wiring.py" in names
    assert "spira_core/nesira_phase2_assessment_wiring_harness.py" not in names
    assert all("_harness.py" not in name for name in names)
    assert "Provides-Extra: nesira-assessment" in metadata
    assert "Requires-Dist: cryptography==49.0.0; extra == 'nesira-assessment'" in metadata


def test_project_dependencies_remain_empty_and_requirements_unchanged_for_wiring():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "requirements" / "nesira_adapters_win_amd64_cp312.txt").read_text(encoding="utf-8")

    assert pyproject["project"]["dependencies"] == []
    assert pyproject["project"]["optional-dependencies"] == {"nesira-assessment": ["cryptography==49.0.0"]}
    assert "assessment-wiring" not in requirements.lower()


def test_assessment_wiring_runtime_in_public_builder_allowlist_but_harness_excluded():
    builder = (ROOT / "tools" / "build_spira_trust_public.py").read_text(encoding="utf-8")

    assert "spira_core/nesira_phase2_assessment_wiring.py" in builder
    assert "spira_core/nesira_phase2_assessment_wiring_harness.py" not in builder


def test_public_wheel_metadata_exposes_crypto_only_as_optional_extra(tmp_path):
    import subprocess
    import sys

    result = subprocess.run(
        [sys.executable, "tools/build_spira_trust_public.py", str(tmp_path / "wheel_build")],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )
    wheel_path = Path(result.stdout.splitlines()[0])
    with zipfile.ZipFile(wheel_path) as zf:
        names = zf.namelist()
        metadata_name = next(name for name in names if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert all("_harness.py" not in name for name in names)
    assert "Provides-Extra: nesira-assessment" in metadata
    assert "Requires-Dist: cryptography==49.0.0; extra == 'nesira-assessment'" in metadata
    assert "Requires-Dist: cryptography==49.0.0\n" not in metadata


def _sub(verdict: str, *, isolation: bool = False) -> dict[str, object]:
    assumptions = ["PT-CRYPTO-01", "PT-CLOCK-01", "PT-META-01", "PT-META-02", "PT-META-04"]
    if isolation:
        assumptions.append("PT-ISOLATION-01")
    return {
        "sub_verdict": verdict,
        "declared_root_id": "root",
        "declared_root_version": "1",
        "assumption_ids": assumptions,
        "not_evaluated_items": [],
        "blocking_items": [],
        "evidence_references": [],
        "reason_codes": ["TEST_REASON"],
        "execution_marker": wiring.EXECUTION_MARKER,
    }
