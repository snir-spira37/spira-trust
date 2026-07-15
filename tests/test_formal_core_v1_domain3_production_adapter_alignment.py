from __future__ import annotations

import importlib.util
from pathlib import Path

from spira_core import terraform_plan_oracle_validator as validator
from spira_core import terraform_plan_producer as producer


ROOT = Path(__file__).resolve().parents[1]
RUNNER_PATH = ROOT / "tools" / "run_formal_core_v1_domain3_production_adapter_alignment.py"


def test_domain3_production_adapter_source_status_is_clean():
    runner = _load_runner()

    assert runner.git_status(runner.PRODUCER_PATHS) == ""


def test_domain3_production_adapter_produces_accepted_case_count():
    runner = _load_runner()
    manifest = runner.read_json(runner.MANIFEST)

    produced = producer.produce_cases(manifest, root=ROOT)

    assert len(produced["cases"]) == 40
    assert len(produced["mutation_relationships"]) == 10


def test_domain3_production_adapter_alignment_core_gates_pass_without_cli_write():
    runner = _load_runner()
    conformance = runner.load_domain3_conformance_module()
    raw_harness = runner.load_raw_adapter_harness_module()
    manifest = runner.read_json(runner.MANIFEST)
    oracle = runner.read_json(runner.ORACLE)
    produced = producer.produce_cases(manifest, root=ROOT)
    validation = validator.validate_oracle_document(producer.candidate_oracle_from_produced(oracle, produced), root=ROOT)
    lean = {"returncode": 0}
    proof_scan = {"status": "PASS", "matches": []}

    production = conformance.evaluate_conformance(manifest, oracle, produced, validation, lean, proof_scan)
    fixture_rows = [raw_harness.evaluate_fixture(entry) for entry in runner.read_json(raw_harness.MANIFEST)["entries"]]
    fixture_counts = raw_harness.summarize(fixture_rows)

    assert production["status"] == "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED"
    assert production["case_pass_count"] == 40
    assert production["mutation_pair_checks"]["passed"] == 10
    assert fixture_counts["fixture_count"] == 31
    assert fixture_counts["contract_mismatch_count"] == 0


def _load_runner():
    spec = importlib.util.spec_from_file_location("run_formal_core_v1_domain3_production_adapter_alignment", RUNNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module
