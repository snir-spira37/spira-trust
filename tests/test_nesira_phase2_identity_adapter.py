from __future__ import annotations

import tomllib
import zipfile
from pathlib import Path

from spira_core import nesira_phase2_identity_adapter as adapter
from spira_core.nesira_phase2_identity_harness import run_identity_harness


ROOT = Path(__file__).resolve().parents[1]


def test_identity_adapter_harness_accepts_authorized_corpus():
    results = run_identity_harness(ROOT, build_wheel=False)

    assert results["verdict"] == "NESIRA_PHASE2_IDENTITY_ADAPTER_ACCEPTED"
    assert results["classification"]["required_identity_failure_modes_without_fixture"] == 0
    assert results["classification"]["required_identity_failure_modes_without_mutation_pair"] == 0
    assert results["classification"]["sub_verdict_mismatches"] == 0
    assert results["classification"]["unexpected_sufficient_verdicts"] == 0
    assert results["classification"]["missing_root_mapped_to_insufficient"] == 0
    assert results["classification"]["wrong_root_mapped_to_not_evaluated"] == 0
    assert results["classification"]["chain_unbuildable_mapped_to_insufficient"] == 0
    assert results["classification"]["known_untrusted_issuer_mapped_to_not_evaluated"] == 0
    assert results["classification"]["soft_pass_revocation_unknown"] == 0
    assert results["classification"]["soft_pass_clock_failure"] == 0
    assert results["classification"]["default_trust_paths"] == 0
    assert results["classification"]["adapter_outputs_with_authority_semantics"] == 0
    assert results["classification"]["adapter_outputs_with_execution_semantics"] == 0
    assert results["end_to_end_composition"]["composition_mismatches"] == 0
    assert results["two_run_semantic_diff"] == 0


def test_identity_adapter_maps_root_and_chain_distinctions():
    results = run_identity_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}

    assert by_id["missing_identity_root"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["missing_identity_root"]["reason_codes"] == ["IDENTITY_DECLARED_ROOT_MISSING"]
    assert by_id["wrong_declared_identity_root"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["wrong_declared_identity_root"]["reason_codes"] == ["IDENTITY_DECLARED_ROOT_MISMATCH"]
    assert by_id["chain_unbuildable_missing_intermediate"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["chain_unbuildable_missing_intermediate"]["reason_codes"] == ["IDENTITY_CHAIN_NOT_EVALUATED"]
    assert by_id["known_but_undeclared_issuer"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["known_but_undeclared_issuer"]["reason_codes"] == ["IDENTITY_KNOWN_UNDECLARED_ISSUER"]


def test_identity_adapter_fails_closed_for_revocation_clock_and_default_trust():
    results = run_identity_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}

    assert by_id["revocation_unknown"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert "PT-REVOKE-03" in by_id["revocation_unknown"]["assumption_ids"]
    assert by_id["clock_missing"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["clock_untrusted"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["missing_identity_root"]["actual_sub_verdict"] != adapter.VERDICT_SUFFICIENT


def test_identity_adapter_sufficient_carries_required_assumptions_and_pin():
    results = run_identity_harness(ROOT, build_wheel=False)
    valid = {item["id"]: item for item in results["fixture_results"]}["valid_identity_binding"]

    assert valid["actual_sub_verdict"] == adapter.VERDICT_SUFFICIENT
    for assumption in [
        "PT-CRYPTO-01",
        "PT-CRYPTO-02",
        "PT-IDENTITY-01",
        "PT-IDENTITY-02",
        "PT-REVOKE-01",
        "PT-REVOKE-02",
        "PT-CLOCK-01",
        "PT-META-01",
        "PT-META-02",
        "PT-META-03",
        "PT-META-04",
    ]:
        assert assumption in valid["assumption_ids"]
    assert results["crypto_pin"]["version"] == adapter.PINNED_CRYPTOGRAPHY_VERSION


def test_identity_adapter_routes_through_composition_oracle():
    results = run_identity_harness(ROOT, build_wheel=False)
    rows = {row["identity_sub"]: row for row in results["end_to_end_composition"]["rows"]}

    assert rows[adapter.VERDICT_SUFFICIENT]["actual_composite"] == adapter.VERDICT_NOT_EVALUATED
    assert rows[adapter.VERDICT_NOT_EVALUATED]["actual_composite"] == adapter.VERDICT_NOT_EVALUATED
    assert rows[adapter.VERDICT_INSUFFICIENT]["actual_composite"] == adapter.VERDICT_INSUFFICIENT


def test_identity_adapter_and_crypto_dependency_are_excluded_from_public_wheel():
    results = run_identity_harness(ROOT, build_wheel=True)
    wheel = results["public_wheel_exclusion"]

    assert wheel["wheel_exclusion_failures"] == 0
    assert wheel["adapter_entries"] == []
    assert wheel["cryptography_entries"] == []
    assert wheel["metadata_mentions_cryptography"] is False


def test_project_core_dependencies_remain_empty_and_identity_adapter_uses_existing_pin():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "requirements" / "nesira_adapters_win_amd64_cp312.txt").read_text(encoding="utf-8")

    assert pyproject["project"]["dependencies"] == []
    assert "optional-dependencies" not in pyproject["project"]
    assert f"cryptography=={adapter.PINNED_CRYPTOGRAPHY_VERSION}" in requirements
    assert adapter.PINNED_CRYPTOGRAPHY_WHEEL_SHA256 in requirements


def test_identity_adapter_module_not_in_public_builder_allowlist():
    builder = (ROOT / "tools" / "build_spira_trust_public.py").read_text(encoding="utf-8")

    assert "spira_core/nesira_phase2_identity_adapter.py" not in builder
    assert "spira_core/nesira_phase2_identity_harness.py" not in builder


def test_identity_adapter_uses_cryptography_x509_verification_not_manual_chain_logic():
    source = (ROOT / "source" / "spira_core" / "nesira_phase2_identity_adapter.py").read_text(encoding="utf-8")

    assert "cryptography.x509.verification" in source
    assert "PolicyBuilder" in source
    assert "Store([" in source
    assert "default_store" not in source
    assert "load_default" not in source
    assert "public_key().verify(" not in source
    assert "load_pem_public_key" not in source


def test_public_wheel_metadata_does_not_include_identity_adapter_or_cryptography(tmp_path):
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

    assert all("nesira_phase2_identity" not in name for name in names)
    assert "Requires-Dist: cryptography" not in metadata
    assert "Provides-Extra: nesira-adapters" not in metadata
