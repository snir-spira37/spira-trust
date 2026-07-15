from __future__ import annotations

import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_formal_core_v1_domain3_raw_adapter_conformance.py"


def test_domain3_raw_adapter_fixture_projection_matches_no_change_expected():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain3/raw_adapter_fixtures/no_change/no_change_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert projected == fixture["expected_typed_evidence"]


def test_domain3_raw_adapter_fixture_projection_preserves_replace_paths():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain3/raw_adapter_fixtures/replace_path/replace_path_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)
    lists = runner.projected_lists(projected)

    assert lists["replace_paths"] == fixture["expected_replace_paths"]


def test_domain3_raw_adapter_fixture_projection_detects_manifest_identity_mismatch():
    runner = _load_runner()
    fixture_path = ROOT / "research/formal_core/domain3/raw_adapter_fixtures/no_change/no_change_01.json"
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    fixture["raw_inputs"]["manifest"]["fixture_id"] = "different"

    projected = runner.project_raw_fixture_to_typed_evidence(fixture)

    assert projected["evidence_validity"] == "internal_failure"
    assert {"kind": "reason", "value": "INTERNAL_ADAPTER_FAILURE"} in projected["typed_claims"]


def test_domain3_raw_adapter_conformance_all_fixtures_pass():
    runner = _load_runner()
    manifest = runner.read_json(runner.MANIFEST)
    rows = [runner.evaluate_fixture(entry) for entry in manifest["entries"]]
    counts = runner.summarize(rows)

    assert counts == {
        "fixture_count": 31,
        "fixture_hash_mismatch_count": 0,
        "typed_evidence_mismatch_count": 0,
        "contract_mismatch_count": 0,
        "false_proceed_count": 0,
        "blocking_item_loss_count": 0,
        "not_evaluated_loss_count": 0,
        "not_claimed_loss_count": 0,
        "evidence_proof_identity_loss_count": 0,
        "resource_action_loss_count": 0,
        "replace_path_loss_count": 0,
        "unknown_path_loss_count": 0,
        "sensitive_path_loss_count": 0,
    }


def test_domain3_raw_adapter_command_summary_is_deterministic():
    runner = _load_runner()
    output = "\n".join(
        [
            "============================= test session starts =============================",
            "collected 4 items",
            "tests/test_example.py .... [100%]",
            "============================== 4 passed in 0.13s ==============================",
        ]
    )

    summary = runner.command_output_summary(output)

    assert summary == {
        "collected": 4,
        "summary": "============================== 4 passed in <duration> ==============================",
        "line_count": 4,
        "has_output": True,
    }


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_formal_core_v1_domain3_raw_adapter_conformance", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
