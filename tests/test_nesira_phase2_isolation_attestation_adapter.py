from __future__ import annotations

import tomllib
import zipfile
from pathlib import Path

from spira_core import nesira_phase2_isolation_attestation_adapter as adapter
from spira_core.nesira_phase2_isolation_attestation_harness import (
    run_isolation_attestation_harness,
)


ROOT = Path(__file__).resolve().parents[1]


def test_isolation_attestation_harness_accepts_authorized_corpus():
    results = run_isolation_attestation_harness(ROOT, build_wheel=False)

    assert results["verdict"] == "NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_ACCEPTED"
    assert results["classification"]["required_isolation_failure_modes_without_fixture"] == 0
    assert results["classification"]["required_isolation_failure_modes_without_mutation_pair"] == 0
    assert results["classification"]["sub_verdict_mismatches"] == 0
    assert results["classification"]["unexpected_sufficient_verdicts"] == 0
    assert results["classification"]["missing_root_mapped_to_insufficient"] == 0
    assert results["classification"]["known_undeclared_authority_mapped_to_not_evaluated"] == 0
    assert results["classification"]["claims_mismatch_mapped_to_not_evaluated"] == 0
    assert results["classification"]["clock_failure_mapped_to_temporal_invalid"] == 0
    assert results["classification"]["soft_pass_revocation_unknown"] == 0
    assert results["classification"]["soft_pass_clock_failure"] == 0
    assert results["classification"]["outputs_without_pt_isolation_01"] == 0
    assert results["classification"]["outputs_with_execution_semantics"] == 0
    assert results["classification"]["outputs_with_isolation_truth_semantics"] == 0
    assert results["language_allowlist"]["forbidden_isolation_language_hits"] == 0
    assert results["language_allowlist"]["non_allowlisted_isolation_language_hits"] == 0
    assert results["end_to_end_composition"]["composition_mismatches"] == 0
    assert results["end_to_end_composition"]["composite_caveat_mismatches"] == 0
    assert results["two_run_semantic_diff"] == 0


def test_isolation_attestation_maps_required_verdict_distinctions():
    results = run_isolation_attestation_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}

    assert by_id["missing_attestation_authority_root"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["missing_attestation_authority_root"]["reason_codes"] == ["ATTESTATION_DECLARED_AUTHORITY_MISSING"]
    assert by_id["known_undeclared_attestation_authority"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["known_undeclared_attestation_authority"]["reason_codes"] == ["ATTESTATION_DECLARED_AUTHORITY_MISMATCH"]
    assert by_id["bad_attestation_signature"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["candidate_claim_mismatch"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["environment_claim_mismatch"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["isolation_profile_claim_mismatch"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT


def test_isolation_attestation_clock_precedes_temporal_classification():
    results = run_isolation_attestation_harness(ROOT, build_wheel=False)
    by_id = {item["id"]: item for item in results["fixture_results"]}

    assert by_id["attestation_expired"]["actual_sub_verdict"] == adapter.VERDICT_INSUFFICIENT
    assert by_id["clock_missing"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["clock_untrusted"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["clock_missing_with_expired_attestation"]["actual_sub_verdict"] == adapter.VERDICT_NOT_EVALUATED
    assert by_id["clock_missing_with_expired_attestation"]["reason_codes"] == ["ATTESTATION_CLOCK_NOT_EVALUATED"]


def test_isolation_attestation_carries_caveat_on_every_sub_verdict():
    results = run_isolation_attestation_harness(ROOT, build_wheel=False)

    for item in results["fixture_results"]:
        assert adapter.ISOLATION_CAVEAT in item["assumption_ids"]
    valid = {item["id"]: item for item in results["fixture_results"]}["valid_attestation_under_declared_authority"]
    assert valid["actual_sub_verdict"] == adapter.VERDICT_SUFFICIENT
    assert adapter.ISOLATION_CAVEAT in valid["assumption_ids"]


def test_isolation_attestation_routes_through_composition_and_preserves_caveat():
    results = run_isolation_attestation_harness(ROOT, build_wheel=False)
    rows = {row["isolation_sub"]: row for row in results["end_to_end_composition"]["rows"]}

    assert rows[adapter.VERDICT_SUFFICIENT]["actual_composite"] == adapter.VERDICT_SUFFICIENT
    assert rows[adapter.VERDICT_SUFFICIENT]["composite_carries_pt_isolation_01"] is True
    assert rows[adapter.VERDICT_NOT_EVALUATED]["actual_composite"] == adapter.VERDICT_NOT_EVALUATED
    assert rows[adapter.VERDICT_INSUFFICIENT]["actual_composite"] == adapter.VERDICT_INSUFFICIENT


def test_isolation_attestation_language_allowlist_is_enforced_on_outputs():
    results = run_isolation_attestation_harness(ROOT, build_wheel=False)

    assert results["language_allowlist"]["forbidden_samples"] == []
    assert results["language_allowlist"]["non_allowlisted_samples"] == []


def test_isolation_attestation_adapter_does_not_run_or_observe():
    source = (ROOT / "source" / "spira_core" / "nesira_phase2_isolation_attestation_adapter.py").read_text(encoding="utf-8")

    forbidden = [
        "subprocess",
        "psutil",
        "socket",
        "os.walk",
        "pathlib",
        "permission_to_sever",
        "authorized_to_sever",
        "safe_to_sever",
    ]
    bad_words = [
        "occur" + "red",
        "happen" + "ed",
        "confirm" + "ed",
        "prov" + "en",
        "establish" + "ed",
        "guarante" + "ed",
        "ensur" + "ed",
        "enforc" + "ed",
        "sand" + "box" + "ed",
        "con" + "tain" + "ed",
    ]
    for token in forbidden:
        assert token not in source
    lowered = source.lower()
    for word in bad_words:
        assert word not in lowered


def test_isolation_attestation_binds_against_external_expected_context():
    source = (ROOT / "source" / "spira_core" / "nesira_phase2_isolation_attestation_adapter.py").read_text(encoding="utf-8")

    assert "expected_context" in source
    assert "payload.get(field) != expected[field]" in source
    assert "expected context missing" in source


def test_isolation_attestation_adapter_and_crypto_dependency_are_excluded_from_public_wheel():
    results = run_isolation_attestation_harness(ROOT, build_wheel=True)
    wheel = results["public_wheel_exclusion"]

    assert wheel["wheel_exclusion_failures"] == 0
    assert wheel["adapter_entries"] == []
    assert wheel["cryptography_entries"] == []
    assert wheel["metadata_mentions_new_dependency"] is False


def test_project_dependencies_remain_empty_and_crypto_pin_reused():
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    requirements = (ROOT / "requirements" / "nesira_adapters_win_amd64_cp312.txt").read_text(encoding="utf-8")

    assert pyproject["project"]["dependencies"] == []
    assert "optional-dependencies" not in pyproject["project"]
    assert f"cryptography=={adapter.PINNED_CRYPTOGRAPHY_VERSION}" in requirements
    assert "isolation-attestation" not in requirements.lower()


def test_isolation_attestation_adapter_module_not_in_public_builder_allowlist():
    builder = (ROOT / "tools" / "build_spira_trust_public.py").read_text(encoding="utf-8")

    assert "spira_core/nesira_phase2_isolation_attestation_adapter.py" not in builder
    assert "spira_core/nesira_phase2_isolation_attestation_harness.py" not in builder


def test_public_wheel_metadata_does_not_include_isolation_attestation_adapter_or_new_dependency(tmp_path):
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
        metadata_name = next(name for name in zf.namelist() if name.endswith(".dist-info/METADATA"))
        metadata = zf.read(metadata_name).decode("utf-8")

    assert all("nesira_phase2_isolation_attestation" not in name for name in names)
    assert "Requires-Dist:" not in metadata
    assert "Provides-Extra:" not in metadata
