from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_formal_core_v1_domain1_raw_adapter_conformance.py"


def test_domain1_raw_adapter_fixture_projection_matches_baseline_expected():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain1/raw_adapter_fixtures/accepted_identity_baseline/accepted_identity_baseline_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert projected == fixture["expected_typed_evidence"]


def test_domain1_raw_adapter_fixture_projection_preserves_identity_fields():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain1/raw_adapter_fixtures/artifact_hash_mismatch/artifact_hash_mismatch_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert runner.identity_from_projected(projected) == fixture["expected_identity_fields"]


def test_domain1_raw_adapter_fixture_projection_detects_manifest_identity_mismatch():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain1/raw_adapter_fixtures/accepted_identity_baseline/accepted_identity_baseline_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["raw_inputs"]["manifest"]["fixture_id"] = "different"

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert projected["evidence_validity"] == "internal_failure"
    assert {"kind": "reason", "value": "INTERNAL_ADAPTER_FAILURE"} in projected["typed_claims"]


def test_domain1_raw_adapter_conformance_all_fixtures_pass():
    runner = _load_runner()
    manifest = runner.read_json(runner.MANIFEST)
    rows = [runner.evaluate_fixture(entry) for entry in manifest["entries"]]
    counts = runner.summarize(rows)

    assert counts == {
        "fixture_count": 33,
        "fixture_hash_mismatch_count": 0,
        "typed_evidence_mismatch_count": 0,
        "contract_mismatch_count": 0,
        "false_proceed_count": 0,
        "blocking_item_loss_count": 0,
        "not_evaluated_loss_count": 0,
        "not_claimed_loss_count": 0,
        "evidence_proof_identity_loss_count": 0,
        "identity_hash_loss_count": 0,
        "unification_id_loss_count": 0,
    }


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_formal_core_v1_domain1_raw_adapter_conformance", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
