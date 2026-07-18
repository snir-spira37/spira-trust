from __future__ import annotations

import tomllib
import zipfile
from pathlib import Path

from spira_core import nesira_phase2_signature_adapter as adapter
from spira_core.nesira_phase2_signature_harness import run_signature_harness


ROOT = Path(__file__).resolve().parents[1]


def test_signature_adapter_harness_accepts_authorized_corpus():
    results = run_signature_harness(ROOT, build_wheel=False)

    assert results["verdict"] == "NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED"
    assert results["classification"]["required_signature_failure_modes_without_fixture"] == 0
    assert results["classification"]["required_signature_failure_modes_without_mutation_pair"] == 0
    assert results["classification"]["sub_verdict_mismatches"] == 0
    assert results["classification"]["unexpected_sufficient_verdicts"] == 0
    assert results["classification"]["missing_root_mapped_to_insufficient"] == 0
    assert results["classification"]["wrong_root_mapped_to_not_evaluated"] == 0
    assert results["classification"]["soft_pass_revocation_unknown"] == 0
    assert results["classification"]["soft_pass_clock_failure"] == 0
    assert results["classification"]["default_trust_paths"] == 0
    assert results["classification"]["adapter_outputs_with_execution_semantics"] == 0
    assert results["end_to_end_composition"]["composition_mismatches"] == 0
    assert results["two_run_semantic_diff"] == 0


def test_signature_adapter_maps_missing_root_and_wrong_root_distinctly():
    results = run_signature_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}

    assert by_id["missing_declared_root"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["missing_declared_root"]["reason_codes"] == ["SIGNATURE_DECLARED_ROOT_MISSING"]
    assert by_id["wrong_declared_root"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["wrong_declared_root"]["reason_codes"] == ["SIGNATURE_DECLARED_ROOT_MISMATCH"]


def test_signature_adapter_fails_closed_for_revocation_clock_and_default_trust():
    results = run_signature_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}

    assert by_id["revocation_unknown"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert "PT-REVOKE-03" in by_id["revocation_unknown"]["assumption_ids"]
    assert by_id["clock_missing"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["clock_untrusted"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["missing_declared_root"]["actual_sub_verdict"] != adapter.VERDICT_SUFFICIENT


def test_signature_adapter_sufficient_carries_required_assumptions_and_pin():
    results = run_signature_harness(ROOT, build_wheel=False)
    valid = {item["id"]: item for item in results["fixture_results"]}["valid_signature_declared_root_fresh_revocation"]

    assert valid["actual_sub_verdict"] == adapter.VERDICT_SUFFICIENT
    for assumption in [
        "PT-CRYPTO-01",
        "PT-CRYPTO-02",
        "PT-CRYPTO-03",
        "PT-KEYLEGIT-01",
        "PT-KEYLEGIT-02",
        "PT-REVOKE-01",
        "PT-REVOKE-02",
        "PT-CLOCK-01",
        "PT-META-01",
        "PT-META-02",
        "PT-META-04",
    ]:
        assert assumption in valid["assumption_ids"]
    assert results["crypto_pin"]["version"] == adapter.PINNED_CRYPTOGRAPHY_VERSION


def test_signature_adapter_routes_through_composition_oracle():
    results = run_signature_harness(ROOT, build_wheel=False)
    rows = {row["signature_sub"]: row for row in results["end_to_end_composition"]["rows"]}

    assert rows[adapter.VERDICT_SUFFICIENT]["actual_composite"] == adapter.VERDICT_NOT_EVALUATED
    assert rows[adapter.VERDICT_NOT_EVALUATED]["actual_composite"] == adapter.VERDICT_NOT_EVALUATED
    assert rows[adapter.VERDICT_INSUFFICIENT]["actual_composite"] == adapter.VERDICT_INSUFFICIENT


def test_signature_adapter_and_crypto_dependency_are_excluded_from_public_wheel():
    results = run_signature_harness(ROOT, build_wheel=True)
    wheel = results["public_wheel_exclusion"]

    assert wheel["wheel_exclusion_failures"] == 0
    assert wheel["adapter_entries"] == []
    assert wheel["cryptography_entries"] == []
    assert wheel["metadata_mentions_cryptography"] is False


def test_project_core_dependencies_remain_empty_and_extra_is_pinned():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "requirements" / "nesira_adapters_win_amd64_cp312.txt").read_text(encoding="utf-8")

    assert pyproject["project"]["dependencies"] == []
    assert "optional-dependencies" not in pyproject["project"]
    assert f"cryptography=={adapter.PINNED_CRYPTOGRAPHY_VERSION}" in requirements
    assert adapter.PINNED_CRYPTOGRAPHY_WHEEL_SHA256 in requirements


def test_signature_adapter_module_not_in_public_builder_allowlist():
    builder = (ROOT / "tools" / "build_spira_trust_public.py").read_text(encoding="utf-8")

    assert "spira_core/nesira_phase2_signature_adapter.py" not in builder
    assert "spira_core/nesira_phase2_signature_harness.py" not in builder


def test_public_wheel_metadata_does_not_include_cryptography(tmp_path):
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
        metadata_name = next(name for name in zf.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert "Requires-Dist: cryptography" not in metadata
    assert "Provides-Extra: nesira-adapters" not in metadata
