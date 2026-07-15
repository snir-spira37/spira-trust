from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_formal_core_v1_domain2_raw_adapter_conformance.py"


def test_domain2_raw_adapter_fixture_projection_matches_clean_success_expected():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain2/raw_adapter_fixtures/clean_success/clean_success_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert projected == fixture["expected_typed_evidence"]


def test_domain2_raw_adapter_fixture_projection_detects_metadata_identity_mismatch():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain2/raw_adapter_fixtures/clean_success/clean_success_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["raw_inputs"]["metadata_json"]["fixture_id"] = "different"

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert projected["evidence_validity"] == "conflicting"
    assert {"kind": "reason", "value": "TEST_IDENTITY_CONFLICT"} in projected["typed_claims"]


def test_domain2_raw_adapter_conformance_all_fixtures_pass():
    runner = _load_runner()
    manifest = runner.read_json(runner.MANIFEST)
    rows = [runner.evaluate_fixture(entry) for entry in manifest["entries"]]
    counts = runner.summarize(rows)

    assert counts == {
        "fixture_count": 26,
        "fixture_hash_mismatch_count": 0,
        "typed_evidence_mismatch_count": 0,
        "contract_mismatch_count": 0,
        "false_proceed_count": 0,
        "blocking_item_loss_count": 0,
        "not_evaluated_loss_count": 0,
        "not_claimed_loss_count": 0,
        "evidence_proof_identity_loss_count": 0,
    }


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_formal_core_v1_domain2_raw_adapter_conformance", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
