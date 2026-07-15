from __future__ import annotations

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "research" / "formal_core" / "external_reproduction_package"


def test_external_reproduction_package_required_files_exist():
    required = {
        "README_TASK.txt",
        "FORMAL_CLAIMS_AND_BOUNDARIES.md",
        "expected_results.json",
        "artifact_manifest.json",
        "SHA256SUMS",
        "verify_all.ps1",
        "verify_all.sh",
        "proof_and_axiom_inventory.json",
        "toolchain_lock.json",
        "COLD_EXTERNAL_REVIEW_TASK.md",
    }

    assert {path.name for path in PACKAGE.iterdir() if path.is_file()} >= required


def test_external_reproduction_package_manifest_hashes_match():
    manifest = _json("artifact_manifest.json")

    assert manifest["source_artifact_count"] > 100
    for item in manifest["source_artifacts"]:
        path = ROOT / item["path"]
        assert path.exists(), item["path"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == item["sha256"]


def test_external_reproduction_package_expected_statuses_are_present():
    expected = _json("expected_results.json")

    assert expected["all_domain_alignment"]["status"] == "SPIRA_FORMAL_CORE_V1_ALL_DOMAIN_ADAPTER_ALIGNMENT_ACCEPTED"
    assert expected["domain1"]["raw_fixture_conformance"]["fixture_count"] == 33
    assert expected["domain2"]["raw_fixture_conformance"]["fixture_count"] == 26
    assert expected["domain3"]["raw_fixture_conformance"]["fixture_count"] == 31


def test_external_reproduction_package_proof_inventory_has_no_forbidden_tokens():
    inventory = _json("proof_and_axiom_inventory.json")

    assert inventory["lean_file_count"] > 0
    assert inventory["no_forbidden_tokens"] is True
    assert inventory["forbidden_token_matches"] == []


def test_external_reproduction_verify_scripts_do_not_run_live_agents():
    combined = (PACKAGE / "verify_all.ps1").read_text(encoding="utf-8").lower()
    combined += "\n" + (PACKAGE / "verify_all.sh").read_text(encoding="utf-8").lower()

    assert "claude" not in combined
    assert "deepseek" not in combined
    assert "codex primary" not in combined


def _json(name: str):
    return json.loads((PACKAGE / name).read_text(encoding="utf-8"))
