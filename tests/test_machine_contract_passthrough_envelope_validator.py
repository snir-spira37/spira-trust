from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import validate_machine_contract_passthrough_envelope as validator  # noqa: E402


FIXTURES = ROOT / "research" / "machine_contract_passthrough_fixtures"
MANIFEST = FIXTURES / "fixture_manifest.json"


def test_full_fixture_manifest_passes_acceptance_gates():
    report = validator.evaluate_fixture_manifest(MANIFEST)

    assert report["verdict"] == "PASS", report["errors"]
    assert report["status"] == "MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_PASS"
    assert report["counts"]["fixture_count"] == 43
    assert report["counts"]["positive_pass_count"] == 6
    assert report["counts"]["negative_rejected_count"] == 37
    assert report["counts"]["false_accepts"] == 0
    assert report["counts"]["false_rejects"] == 0
    assert report["counts"]["fixture_mutations"] == 0
    assert report["counts"]["contradiction_classes_detected_count"] == 14
    assert report["counts"]["deterministic_repeated_evaluation"] is True
    assert report["counts"]["schema_manifest_hash_validation"] == "PASS"
    assert report["errors"] == []
    assert "LIVE_SESSIONS" in report["not_authorized"]


def test_fixture_evaluation_matches_manifest_for_every_fixture():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    for fixture in manifest["fixtures"]:
        report = validator.validate_envelope_file(ROOT / fixture["path"], manifest_fixture=fixture)

        assert report["verdict"] == fixture["expected_validator_outcome"], fixture["fixture_id"]
        assert report["schema_result"] == fixture["expected_schema_result"], fixture["fixture_id"]
        assert report["summary"]["contradiction_classes_detected"] == sorted(
            fixture["expected_contradiction_classes"]
        ), fixture["fixture_id"]
        assert report["summary"]["fail_closed"] == fixture["expected_fail_closed"], fixture["fixture_id"]


def test_schema_authority_violation_fails_closed_as_validation_failure():
    fixture = _fixture("machine_contract_integrity_failures", "machine_authoritative_false")

    report = validator.validate_envelope_file(fixture)

    assert report["verdict"] == "FAIL"
    assert report["schema_result"] == "FAIL"
    assert "SCHEMA_V1_VALIDATION_FAILED" in _error_codes(report)


def test_hash_and_field_drift_fail_semantically_not_as_tool_error():
    source_hash = validator.validate_envelope_file(_fixture("machine_contract_integrity_failures", "source_hash_mismatch"))
    action_drift = validator.validate_envelope_file(_fixture("machine_contract_integrity_failures", "action_drift"))

    assert source_hash["verdict"] == "FAIL"
    assert source_hash["schema_result"] == "PASS"
    assert "SOURCE_CONTRACT_HASH_MISMATCH" in _error_codes(source_hash)
    assert action_drift["verdict"] == "FAIL"
    assert "ACTION_DRIFT" in _error_codes(action_drift)


def test_contradiction_classes_are_detected_and_fail_closed():
    report = validator.validate_envelope_file(
        _fixture("model_explanation_contradictions", "model_explanation_converts_not_evaluated_to_pass")
    )

    assert report["verdict"] == "FAIL"
    assert report["summary"]["contradiction_classes_detected"] == [
        "MODEL_EXPLANATION_CONVERTS_NOT_EVALUATED_TO_PASS"
    ]
    assert report["summary"]["fail_closed"] is True


def test_telemetry_and_sensitive_value_failures_are_rejected():
    telemetry = validator.validate_envelope_file(_fixture("telemetry_failures", "telemetry_usage_not_evaluated_with_numeric"))
    sensitive = validator.validate_envelope_file(_fixture("sensitive_value_failures", "sensitive_marker_in_model_explanation"))

    assert telemetry["verdict"] == "FAIL"
    assert "TELEMETRY_USAGE_STATUS_VALUE_CONFLICT" in _error_codes(telemetry)
    assert sensitive["verdict"] == "FAIL"
    assert "SENSITIVE_VALUE_EXPOSED" in _error_codes(sensitive)


def test_json_parse_failure_is_fail_not_tool_error(tmp_path):
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{", encoding="utf-8")

    report = validator.validate_envelope_file(invalid)

    assert report["verdict"] == "FAIL"
    assert report["status"] == "ENVELOPE_VALIDATION_FAILED"
    assert _error_codes(report) == {"JSON_PARSE_FAILED"}


def test_internal_exception_is_tool_error(monkeypatch):
    def boom(_document):
        raise RuntimeError("boom")

    monkeypatch.setattr(validator, "validate_envelope_document", boom)

    report = validator.validate_envelope_file(FIXTURES / "positive" / "positive_domain1_text_available.json")

    assert report["verdict"] == "TOOL_ERROR"
    assert report["status"] == "ENVELOPE_VALIDATOR_TOOL_ERROR"
    assert "ENVELOPE_VALIDATOR_EXCEPTION" in _error_codes(report)


def test_validator_does_not_mutate_fixture_documents():
    fixture = FIXTURES / "positive" / "positive_domain2_structured_not_exposed.json"
    before = json.loads(fixture.read_text(encoding="utf-8"))
    frozen = copy.deepcopy(before)

    report = validator.validate_envelope_file(fixture)
    after = json.loads(fixture.read_text(encoding="utf-8"))

    assert report["verdict"] == "PASS"
    assert before == frozen
    assert after == frozen


def _fixture(directory: str, name: str) -> Path:
    return FIXTURES / directory / f"{name}.json"


def _error_codes(report: dict) -> set[str]:
    return {check["error_code"] for check in report["checks"] if check["result"] in {"FAIL", "TOOL_ERROR"}}
