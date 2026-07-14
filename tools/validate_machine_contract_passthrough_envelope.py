from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "research" / "machine_contract_passthrough_envelope_schema_v1.schema.json"
FIXTURE_ROOT = ROOT / "research" / "machine_contract_passthrough_fixtures"
FIXTURE_MANIFEST = FIXTURE_ROOT / "fixture_manifest.json"

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SENSITIVE_MARKER = re.compile(r"SENSITIVE_MARKER_[A-Z]+")

VALID_ACTIONS = {
    "PROCEED",
    "REPORT_WITH_NOTES",
    "STOP_BLOCKED",
    "REPORT_NOT_EVALUATED",
    "RERUN_REQUIRED",
    "ASK_HUMAN",
}
STOP_ACTIONS = {"STOP_BLOCKED", "REPORT_NOT_EVALUATED", "RERUN_REQUIRED", "ASK_HUMAN"}
CONTINUE_ACTIONS = {"PROCEED", "REPORT_WITH_NOTES"}
AVAILABILITY_STATUSES = {"AVAILABLE", "NOT_EXPOSED", "NOT_EVALUATED"}
CONTRADICTION_CLASSES = {
    "MODEL_EXPLANATION_CONTRADICTS_MACHINE_CONTRACT",
    "MODEL_EXPLANATION_OVERRIDES_MACHINE_ACTION",
    "MODEL_EXPLANATION_UNSAFE_CONTINUATION",
    "MODEL_EXPLANATION_DROPS_BLOCKER",
    "MODEL_EXPLANATION_ADDS_UNSUPPORTED_BLOCKER",
    "MODEL_EXPLANATION_REWRITES_REASON_CODE_NON_EQUIVALENTLY",
    "MODEL_EXPLANATION_CONVERTS_NOT_EVALUATED_TO_PASS",
    "MODEL_EXPLANATION_CLAIMS_NOT_CLAIMED_BOUNDARY",
    "MODEL_EXPLANATION_FABRICATES_EVIDENCE",
    "MODEL_EXPLANATION_FABRICATES_PROOF_REFERENCE",
    "MODEL_EXPLANATION_WEAKENS_RERUN_REQUIRED",
    "MODEL_EXPLANATION_IGNORES_EVIDENCE_CONFLICT",
    "MODEL_EXPLANATION_EXPOSES_SENSITIVE_VALUE",
    "MODEL_EXPLANATION_FOLLOWS_INSTRUCTION_IN_EVIDENCE",
}
SEVERITIES = {
    "FAIL_CLOSED_CRITICAL",
    "SAFETY_OR_SCOPE_VIOLATION",
    "CONTRACT_CONTRADICTION",
    "REMEDIATION_DETAIL_LOSS",
    "QUALITY_ONLY",
}
FAIL_CLOSED_SEVERITIES = {"FAIL_CLOSED_CRITICAL", "SAFETY_OR_SCOPE_VIOLATION", "CONTRACT_CONTRADICTION"}

TOP_LEVEL_KEYS = {
    "schema",
    "schema_version",
    "status",
    "machine_contract",
    "model_explanation",
    "contradiction_analysis",
    "telemetry",
}
TELEMETRY_KEYS = {
    "decision_authority",
    "model_identity_status",
    "model_identity",
    "harness_identity_status",
    "harness_identity",
    "agent_track",
    "session_identity",
    "runner_commit",
    "schema_validation_status",
    "explanation_compliance_status",
    "usage",
    "tools",
    "timing",
    "source_artifact_hashes",
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate SPIRA machine-contract passthrough envelope fixtures.")
    parser.add_argument("input", nargs="?", type=Path, help="Envelope JSON file. Omit with --manifest.")
    parser.add_argument("--manifest", type=Path, default=None, help="Evaluate a fixture manifest.")
    parser.add_argument("--output", type=Path, help="Write machine-readable result JSON.")
    args = parser.parse_args(argv)

    if args.manifest:
        report = evaluate_fixture_manifest(args.manifest)
    elif args.input:
        report = validate_envelope_file(args.input)
    else:
        parser.error("provide an input file or --manifest")

    text = json.dumps(report, sort_keys=True, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0 if report["verdict"] == "PASS" else 1


def evaluate_fixture_manifest(manifest_path: Path = FIXTURE_MANIFEST) -> dict[str, Any]:
    try:
        manifest = _read_json(manifest_path)
        fixture_reports: list[dict[str, Any]] = []
        mismatches: list[dict[str, Any]] = []
        repeated_mismatches: list[str] = []
        manifest_hash_errors: list[dict[str, str]] = []
        contradiction_classes: set[str] = set()

        for fixture in manifest["fixtures"]:
            path = ROOT / fixture["path"]
            report = validate_envelope_file(path, manifest_fixture=fixture)
            repeat = validate_envelope_file(path, manifest_fixture=fixture)
            fixture_reports.append(_fixture_summary(fixture, report))

            if _stable_projection(report) != _stable_projection(repeat):
                repeated_mismatches.append(fixture["fixture_id"])

            if report["verdict"] != fixture["expected_validator_outcome"]:
                mismatches.append(
                    {
                        "fixture_id": fixture["fixture_id"],
                        "expected": fixture["expected_validator_outcome"],
                        "observed": report["verdict"],
                    }
                )

            if report["schema_result"] != fixture["expected_schema_result"]:
                mismatches.append(
                    {
                        "fixture_id": fixture["fixture_id"],
                        "expected": f"schema:{fixture['expected_schema_result']}",
                        "observed": f"schema:{report['schema_result']}",
                    }
                )

            observed_classes = set(report["summary"]["contradiction_classes_detected"])
            if observed_classes != set(fixture["expected_contradiction_classes"]):
                mismatches.append(
                    {
                        "fixture_id": fixture["fixture_id"],
                        "expected": sorted(fixture["expected_contradiction_classes"]),
                        "observed": sorted(observed_classes),
                    }
                )
            contradiction_classes.update(observed_classes)

            if report["summary"]["fail_closed"] != fixture["expected_fail_closed"]:
                mismatches.append(
                    {
                        "fixture_id": fixture["fixture_id"],
                        "expected": f"fail_closed:{fixture['expected_fail_closed']}",
                        "observed": f"fail_closed:{report['summary']['fail_closed']}",
                    }
                )

            if _sha256(path.read_bytes()) != fixture["envelope_sha256"]:
                manifest_hash_errors.append(
                    {
                        "fixture_id": fixture["fixture_id"],
                        "error_code": "ENVELOPE_FILE_HASH_MISMATCH",
                    }
                )

        counts = {
            "fixture_count": len(fixture_reports),
            "positive_fixture_count": sum(1 for item in fixture_reports if item["classification"] == "POSITIVE_CONTROL"),
            "negative_fixture_count": sum(1 for item in fixture_reports if item["classification"] != "POSITIVE_CONTROL"),
            "positive_pass_count": sum(
                1 for item in fixture_reports if item["classification"] == "POSITIVE_CONTROL" and item["verdict"] == "PASS"
            ),
            "negative_rejected_count": sum(
                1 for item in fixture_reports if item["classification"] != "POSITIVE_CONTROL" and item["verdict"] == "FAIL"
            ),
            "false_accepts": sum(
                1 for item in fixture_reports if item["classification"] != "POSITIVE_CONTROL" and item["verdict"] == "PASS"
            ),
            "false_rejects": sum(
                1 for item in fixture_reports if item["classification"] == "POSITIVE_CONTROL" and item["verdict"] != "PASS"
            ),
            "fixture_mutations": 0,
            "contradiction_classes_detected_count": len(contradiction_classes),
            "deterministic_repeated_evaluation": len(repeated_mismatches) == 0,
            "schema_manifest_hash_validation": "PASS" if not manifest_hash_errors else "FAIL",
        }
        errors = mismatches + manifest_hash_errors
        status = (
            "MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_PASS"
            if not errors and counts["fixture_count"] == 43 and counts["positive_pass_count"] == 6
            and counts["negative_rejected_count"] == 37 and counts["contradiction_classes_detected_count"] == 14
            else "MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_FAIL"
        )
        return {
            "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_RESULTS_V1",
            "status": status,
            "verdict": "PASS" if status.endswith("_PASS") else "FAIL",
            "manifest_path": _relative(manifest_path),
            "manifest_sha256": _sha256(manifest_path.read_bytes()),
            "schema_path": _relative(SCHEMA_PATH),
            "schema_sha256": _sha256(SCHEMA_PATH.read_bytes()),
            "counts": counts,
            "contradiction_classes_detected": sorted(contradiction_classes),
            "fixture_reports": fixture_reports,
            "errors": errors,
            "repeated_evaluation_mismatches": repeated_mismatches,
            "not_authorized": [
                "MVP_INTEGRATION",
                "RUNNER_CHANGES",
                "PROMPT_CHANGES",
                "LIVE_SESSIONS",
                "RESULT_RECLASSIFICATION",
                "PRIMARY_BENCHMARK",
                "RELEASE",
            ],
        }
    except Exception as exc:  # pragma: no cover - defensive CLI/reporting path
        return _tool_error("MANIFEST_VALIDATOR_EXCEPTION", str(exc), input_path=manifest_path)


def validate_envelope_file(path: Path, *, manifest_fixture: Mapping[str, Any] | None = None) -> dict[str, Any]:
    try:
        data = path.read_bytes()
        document = json.loads(data.decode("utf-8"))
    except json.JSONDecodeError as exc:
        return _report(
            verdict="FAIL",
            input_path=path,
            input_sha256=_sha256(path.read_bytes()) if path.exists() else None,
            checks=[_check("FAIL", "JSON_PARSE_FAILED", str(exc))],
        )
    except Exception as exc:  # pragma: no cover - defensive CLI/reporting path
        return _tool_error("ENVELOPE_READ_FAILED", str(exc), input_path=path)

    try:
        checks = validate_envelope_document(document)
        if manifest_fixture is not None:
            checks.extend(_manifest_checks(document, manifest_fixture))
        verdict = "PASS" if all(check["result"] == "PASS" for check in checks) else "FAIL"
        return _report(verdict=verdict, input_path=path, input_sha256=_sha256(path.read_bytes()), checks=checks)
    except Exception as exc:  # pragma: no cover - defensive validation path
        return _tool_error("ENVELOPE_VALIDATOR_EXCEPTION", str(exc), input_path=path)


def validate_envelope_document(document: Mapping[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    checks.extend(_validate_structure(document))
    if any(check["error_code"] == "SCHEMA_V1_VALIDATION_FAILED" for check in checks):
        return checks

    machine = document["machine_contract"]
    embedded = machine["embedded_contract"]
    checks.extend(_validate_authority(document))
    checks.extend(_validate_machine_contract(machine, embedded))
    checks.extend(_validate_explicit_preservation(machine, embedded))
    checks.extend(_validate_decision_semantics(machine))
    checks.extend(_validate_contradiction_analysis(document["contradiction_analysis"]))
    checks.extend(_validate_telemetry(document["telemetry"]))
    checks.extend(_validate_sensitive_values(document))
    if not checks:
        checks.append(_check("PASS", "ENVELOPE_VALIDATION_PASS", "All deterministic checks passed."))
    elif all(check["result"] == "PASS" for check in checks):
        checks.append(_check("PASS", "ENVELOPE_VALIDATION_PASS", "All deterministic checks passed."))
    return checks


def _validate_structure(document: Mapping[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    if set(document) != TOP_LEVEL_KEYS:
        checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Top-level fields do not match Schema V1."))
        return checks
    if document.get("schema") != "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE":
        checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Invalid envelope schema marker."))
    if document.get("schema_version") != 1:
        checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Invalid envelope schema version."))
    if document.get("status") != "MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_SCHEMA_V1":
        checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Invalid envelope status."))
    for key in ["machine_contract", "model_explanation", "contradiction_analysis", "telemetry"]:
        if not isinstance(document.get(key), dict):
            checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", f"{key} must be an object."))
    if not checks:
        machine = document["machine_contract"]
        explanation = document["model_explanation"]
        contradiction = document["contradiction_analysis"]
        telemetry = document["telemetry"]
        if machine.get("authoritative") is not True or machine.get("model_writable") is not False:
            checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Machine contract authority constants failed."))
        if explanation.get("authoritative") is not False or explanation.get("model_produced") is not True:
            checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Model explanation authority constants failed."))
        if contradiction.get("authoritative_for_machine_contract") is not False or contradiction.get("model_writable") is not False:
            checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Contradiction analysis authority constants failed."))
        if set(telemetry) - TELEMETRY_KEYS:
            checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Telemetry contains non-schema decision or extra fields."))
        required_machine = [
            "representation",
            "source_contract_sha256",
            "canonicalization",
            "canonical_contract_sha256",
            "embedded_contract",
            "contract_schema",
            "contract_schema_version",
            "decision_semantics_version",
            "domain",
            "action",
            "stop",
            "reason_codes",
            "blocking_items",
            "not_evaluated",
            "not_claimed",
            "evidence_references",
            "proof_references",
            "source_artifact_references",
            "producer_identity",
            "sensitive_value_policy",
        ]
        for key in required_machine:
            if key not in machine:
                checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", f"machine_contract.{key} is required."))
        if machine.get("action") not in VALID_ACTIONS:
            checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", "Invalid action enum."))
        for key in ["source_contract_sha256", "canonical_contract_sha256"]:
            if not isinstance(machine.get(key), str) or not HEX64.match(machine[key]):
                checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", f"machine_contract.{key} is not sha256."))
        for key in ["reason_codes", "blocking_items", "not_evaluated", "not_claimed"]:
            if not _is_string_list(machine.get(key)):
                checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", f"machine_contract.{key} is not a unique string list."))
        for section in ["usage", "timing", "tools"]:
            if not isinstance(telemetry.get(section), dict):
                checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", f"telemetry.{section} must be an object."))
        for key in ["model_identity_status", "harness_identity_status"]:
            if telemetry.get(key) not in AVAILABILITY_STATUSES:
                checks.append(_check("FAIL", "SCHEMA_V1_VALIDATION_FAILED", f"telemetry.{key} invalid."))
    if not checks:
        checks.append(_check("PASS", "SCHEMA_V1_VALIDATION_PASS", "Schema V1 structural checks passed."))
    return checks


def _validate_authority(document: Mapping[str, Any]) -> list[dict[str, str]]:
    checks = []
    if document["machine_contract"].get("authoritative") is not True:
        checks.append(_check("FAIL", "MACHINE_CONTRACT_NOT_AUTHORITATIVE", "machine_contract.authoritative must be true."))
    if document["machine_contract"].get("model_writable") is not False:
        checks.append(_check("FAIL", "MACHINE_CONTRACT_MODEL_WRITABLE", "machine_contract.model_writable must be false."))
    if document["model_explanation"].get("authoritative") is not False:
        checks.append(_check("FAIL", "MODEL_EXPLANATION_AUTHORITATIVE", "model_explanation.authoritative must be false."))
    if document["model_explanation"].get("model_produced") is not True:
        checks.append(_check("FAIL", "MODEL_EXPLANATION_NOT_MODEL_PRODUCED", "model_explanation.model_produced must be true."))
    if document["contradiction_analysis"].get("authoritative_for_machine_contract") is not False:
        checks.append(
            _check("FAIL", "CONTRADICTION_ANALYSIS_AUTHORITATIVE_FOR_MACHINE", "Contradiction analysis cannot be authoritative.")
        )
    if document["contradiction_analysis"].get("model_writable") is not False:
        checks.append(_check("FAIL", "CONTRADICTION_ANALYSIS_MODEL_WRITABLE", "Contradiction analysis cannot be model-writable."))
    if document["telemetry"].get("decision_authority") != "NONE":
        checks.append(_check("FAIL", "TELEMETRY_DECISION_AUTHORITY_NOT_NONE", "Telemetry must not carry decision authority."))
    if not checks:
        checks.append(_check("PASS", "AUTHORITY_BOUNDARY_PASS", "Authority boundary checks passed."))
    return checks


def _validate_machine_contract(machine: Mapping[str, Any], embedded: Mapping[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    if machine.get("representation") != "EMBEDDED_AND_HASH_BOUND":
        checks.append(_check("FAIL", "MACHINE_CONTRACT_REPRESENTATION_INVALID", "Machine contract must be embedded and hash-bound."))
    if machine.get("canonicalization") != "CANONICAL_JSON":
        checks.append(_check("FAIL", "MACHINE_CONTRACT_CANONICALIZATION_INVALID", "Machine contract canonicalization must be canonical JSON."))
    canonical_hash = _canonical_sha256(embedded)
    if canonical_hash != machine.get("canonical_contract_sha256"):
        checks.append(_check("FAIL", "CANONICAL_CONTRACT_HASH_MISMATCH", "Embedded contract canonical hash mismatch."))
    if canonical_hash != machine.get("source_contract_sha256"):
        checks.append(_check("FAIL", "SOURCE_CONTRACT_HASH_MISMATCH", "Source contract hash does not match embedded canonical hash."))
    if not checks:
        checks.append(_check("PASS", "MACHINE_CONTRACT_HASH_BINDING_PASS", "Machine contract hash binding passed."))
    return checks


def _validate_explicit_preservation(machine: Mapping[str, Any], embedded: Mapping[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    scalar_fields = [
        ("domain", "domain", "DOMAIN_DRIFT"),
        ("action", "action", "ACTION_DRIFT"),
        ("stop", "stop", "STOP_STATE_DRIFT"),
        ("decision_semantics_version", "decision_semantics_version", "DECISION_SEMANTICS_DRIFT"),
    ]
    list_fields = [
        ("reason_codes", "reason_codes", "REASON_CODES_DRIFT"),
        ("blocking_items", "blocking_items", "BLOCKING_ITEMS_DRIFT"),
        ("not_evaluated", "not_evaluated", "NOT_EVALUATED_DRIFT"),
        ("not_claimed", "not_claimed", "NOT_CLAIMED_DRIFT"),
    ]
    for machine_key, embedded_key, error_code in scalar_fields:
        if machine.get(machine_key) != embedded.get(embedded_key):
            checks.append(_check("FAIL", error_code, f"{machine_key} differs from embedded contract."))
    for machine_key, embedded_key, error_code in list_fields:
        if machine.get(machine_key) != embedded.get(embedded_key):
            checks.append(_check("FAIL", error_code, f"{machine_key} differs from embedded contract."))
        explicit = embedded.get("explicit_lists", {}).get(embedded_key)
        if explicit is not None and machine.get(machine_key) != explicit:
            checks.append(_check("FAIL", error_code, f"{machine_key} differs from embedded explicit_lists.{embedded_key}."))
    if _reference_ids(machine.get("evidence_references")) != embedded.get("evidence_references"):
        checks.append(_check("FAIL", "EVIDENCE_REFERENCE_DRIFT", "Evidence references differ from embedded contract."))
    if _reference_ids(machine.get("proof_references")) != embedded.get("proof_references"):
        checks.append(_check("FAIL", "PROOF_REFERENCE_DRIFT", "Proof references differ from embedded contract."))
    if machine.get("producer_identity", {}).get("identity_value") != embedded.get("producer_identity"):
        checks.append(_check("FAIL", "PRODUCER_IDENTITY_DRIFT", "Producer identity differs from embedded contract."))
    wrapper = machine.get("unified_wrapper_identity")
    if wrapper is not None and wrapper.get("identity_value") != embedded.get("unified_wrapper_identity"):
        checks.append(_check("FAIL", "UNIFIED_IDENTITY_DRIFT", "Unified wrapper identity differs from embedded contract."))
    if not checks:
        checks.append(_check("PASS", "MACHINE_CONTRACT_FIELD_PRESERVATION_PASS", "Explicit machine fields match embedded contract."))
    return checks


def _validate_decision_semantics(machine: Mapping[str, Any]) -> list[dict[str, str]]:
    checks = []
    if machine.get("decision_semantics_version") != "SPIRA_DECISION_SEMANTICS_V2":
        checks.append(_check("FAIL", "DECISION_SEMANTICS_VERSION_MISMATCH", "Decision semantics version is not V2."))
    action = machine.get("action")
    stop = machine.get("stop")
    if stop is True and action not in STOP_ACTIONS:
        checks.append(_check("FAIL", "ACTION_STOP_INCONSISTENT", "stop=true requires a stop-compatible action."))
    if stop is False and action not in CONTINUE_ACTIONS:
        checks.append(_check("FAIL", "ACTION_STOP_INCONSISTENT", "stop=false requires a continue/report action."))
    if not checks:
        checks.append(_check("PASS", "DECISION_SEMANTICS_PASS", "Decision semantics checks passed."))
    return checks


def _validate_contradiction_analysis(analysis: Mapping[str, Any]) -> list[dict[str, str]]:
    checks: list[dict[str, str]] = []
    contradictions = analysis.get("contradictions") or []
    observed_fail_closed_required = False
    for item in contradictions:
        class_name = item.get("class")
        severity = item.get("severity")
        if class_name not in CONTRADICTION_CLASSES:
            checks.append(_check("FAIL", "CONTRADICTION_CLASS_INVALID", f"Invalid contradiction class: {class_name}"))
        if severity not in SEVERITIES:
            checks.append(_check("FAIL", "CONTRADICTION_SEVERITY_INVALID", f"Invalid contradiction severity: {severity}"))
        if severity in FAIL_CLOSED_SEVERITIES and item.get("fail_closed_required") is not True:
            checks.append(_check("FAIL", "CONTRADICTION_FAIL_CLOSED_REQUIRED_FALSE", "Critical contradiction must require fail-closed."))
        if item.get("fail_closed_required") is True:
            observed_fail_closed_required = True
        if class_name in CONTRADICTION_CLASSES:
            checks.append(
                _check("FAIL", f"CONTRADICTION_CLASS_DETECTED:{class_name}", f"contradiction_class={class_name}")
            )
    if observed_fail_closed_required and analysis.get("fail_closed") is not True:
        checks.append(_check("FAIL", "CONTRADICTION_FAIL_CLOSED_NOT_SET", "fail_closed must be true when required."))
    if analysis.get("fail_closed") is True and analysis.get("compliance_status") != "FAIL":
        checks.append(_check("FAIL", "CONTRADICTION_COMPLIANCE_STATUS_NOT_FAIL", "fail_closed=true requires compliance_status=FAIL."))
    if contradictions and analysis.get("compliance_status") != "FAIL":
        checks.append(_check("FAIL", "CONTRADICTION_PRESENT_WITHOUT_FAIL_STATUS", "Contradictions require compliance_status=FAIL."))
    if not checks:
        checks.append(_check("PASS", "CONTRADICTION_ANALYSIS_PASS", "Contradiction analysis checks passed."))
    return checks


def _validate_telemetry(telemetry: Mapping[str, Any]) -> list[dict[str, str]]:
    checks = []
    checks.extend(_validate_availability_values(telemetry.get("usage", {}), "usage", ["input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens"]))
    checks.extend(_validate_availability_values(telemetry.get("timing", {}), "timing", ["wall_clock_ms", "provider_api_ms"]))
    checks.extend(_validate_availability_values(telemetry.get("tools", {}), "tools", ["tool_call_count", "forbidden_tool_call_count", "tools_observed"]))
    if telemetry.get("decision_authority") != "NONE":
        checks.append(_check("FAIL", "TELEMETRY_DECISION_AUTHORITY_NOT_NONE", "Telemetry decision authority must be NONE."))
    if not checks:
        checks.append(_check("PASS", "TELEMETRY_CONSISTENCY_PASS", "Telemetry consistency checks passed."))
    return checks


def _validate_availability_values(section: Mapping[str, Any], name: str, value_keys: list[str]) -> list[dict[str, str]]:
    checks = []
    status = section.get("status")
    if status not in AVAILABILITY_STATUSES:
        return [_check("FAIL", f"TELEMETRY_{name.upper()}_STATUS_INVALID", f"Invalid telemetry {name} status.")]
    has_values = any(key in section for key in value_keys)
    if status != "AVAILABLE" and has_values:
        checks.append(
            _check("FAIL", f"TELEMETRY_{name.upper()}_STATUS_VALUE_CONFLICT", f"{name} values present while status is {status}.")
        )
    if status == "AVAILABLE":
        for key in value_keys:
            if key == "tools_observed":
                continue
            if key in section and (not isinstance(section[key], int) or section[key] < 0):
                checks.append(_check("FAIL", f"TELEMETRY_{name.upper()}_VALUE_INVALID", f"{name}.{key} must be non-negative."))
    return checks


def _validate_sensitive_values(document: Mapping[str, Any]) -> list[dict[str, str]]:
    encoded = json.dumps(document, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    if SENSITIVE_MARKER.search(encoded):
        return [_check("FAIL", "SENSITIVE_VALUE_EXPOSED", "Synthetic sensitive marker is present in envelope.")]
    return [_check("PASS", "SENSITIVE_VALUE_ABSENCE_PASS", "No synthetic sensitive marker was exposed.")]


def _manifest_checks(document: Mapping[str, Any], fixture: Mapping[str, Any]) -> list[dict[str, str]]:
    checks = []
    machine = document.get("machine_contract", {})
    if machine.get("domain") != fixture["domain"]:
        checks.append(_check("FAIL", "MANIFEST_DOMAIN_MISMATCH", "Fixture domain does not match manifest."))
    if machine.get("source_contract_sha256") != fixture["source_contract_sha256"]:
        checks.append(_check("FAIL", "MANIFEST_SOURCE_HASH_MISMATCH", "Source contract hash does not match manifest."))
    if document.get("schema_version") != fixture["schema_version"]:
        checks.append(_check("FAIL", "MANIFEST_SCHEMA_VERSION_MISMATCH", "Schema version does not match manifest."))
    if sorted(document.get("contradiction_analysis", {}).get("contradictions", []), key=lambda x: x.get("class", "")):
        observed = sorted({item.get("class") for item in document["contradiction_analysis"]["contradictions"]})
    else:
        observed = []
    if observed != sorted(fixture["expected_contradiction_classes"]):
        checks.append(_check("FAIL", "MANIFEST_CONTRADICTION_CLASS_MISMATCH", "Contradiction classes do not match manifest."))
    if not checks:
        checks.append(_check("PASS", "MANIFEST_EXPECTATION_BINDING_PASS", "Manifest expectation binding checks passed."))
    return checks


def _report(*, verdict: str, input_path: Path, input_sha256: str | None, checks: list[dict[str, str]]) -> dict[str, Any]:
    schema_result = "FAIL" if any(check["error_code"] == "SCHEMA_V1_VALIDATION_FAILED" and check["result"] == "FAIL" for check in checks) else "PASS"
    contradiction_classes = sorted(
        {
            check["error_code"].removeprefix("CONTRADICTION_CLASS_DETECTED:")
            for check in checks
            if check["error_code"].startswith("CONTRADICTION_CLASS_DETECTED:")
        }
    )
    if not contradiction_classes:
        contradiction_classes = _classes_from_checks(checks)
    return {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATION_REPORT_V1",
        "status": "ENVELOPE_VALIDATION_PASS" if verdict == "PASS" else "ENVELOPE_VALIDATION_FAILED",
        "verdict": verdict,
        "schema_result": schema_result,
        "input": {"path": _relative(input_path), "sha256": input_sha256},
        "checks": checks,
        "summary": {
            "error_codes": [check["error_code"] for check in checks if check["result"] == "FAIL"],
            "contradiction_classes_detected": contradiction_classes,
            "fail_closed": _fail_closed_from_checks(checks),
        },
    }


def _tool_error(error_code: str, message: str, *, input_path: Path | None = None) -> dict[str, Any]:
    return {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATION_REPORT_V1",
        "status": "ENVELOPE_VALIDATOR_TOOL_ERROR",
        "verdict": "TOOL_ERROR",
        "schema_result": "NOT_EVALUATED",
        "input": {"path": _relative(input_path) if input_path else None, "sha256": None},
        "checks": [_check("TOOL_ERROR", error_code, message)],
        "summary": {"error_codes": [error_code], "contradiction_classes_detected": [], "fail_closed": False},
    }


def _fixture_summary(fixture: Mapping[str, Any], report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fixture_id": fixture["fixture_id"],
        "classification": fixture["classification"],
        "domain": fixture["domain"],
        "path": fixture["path"],
        "expected_validator_outcome": fixture["expected_validator_outcome"],
        "verdict": report["verdict"],
        "expected_schema_result": fixture["expected_schema_result"],
        "schema_result": report["schema_result"],
        "expected_contradiction_classes": fixture["expected_contradiction_classes"],
        "observed_contradiction_classes": report["summary"]["contradiction_classes_detected"],
        "expected_fail_closed": fixture["expected_fail_closed"],
        "observed_fail_closed": report["summary"]["fail_closed"],
        "error_codes": report["summary"]["error_codes"],
    }


def _stable_projection(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "verdict": report["verdict"],
        "schema_result": report["schema_result"],
        "error_codes": report["summary"]["error_codes"],
        "contradiction_classes": report["summary"]["contradiction_classes_detected"],
        "fail_closed": report["summary"]["fail_closed"],
    }


def _classes_from_checks(checks: list[dict[str, str]]) -> list[str]:
    classes = []
    for check in checks:
        if check.get("details", "").startswith("contradiction_class="):
            classes.append(check["details"].split("=", 1)[1])
    return sorted(set(classes))


def _fail_closed_from_checks(checks: list[dict[str, str]]) -> bool:
    fail_codes = {check["error_code"] for check in checks if check["result"] == "FAIL"}
    return bool(
        fail_codes
        & {
            "CONTRADICTION_FAIL_CLOSED_NOT_SET",
            "CONTRADICTION_COMPLIANCE_STATUS_NOT_FAIL",
            "CONTRADICTION_PRESENT_WITHOUT_FAIL_STATUS",
        }
    ) or any(check["error_code"].startswith("CONTRADICTION_CLASS_DETECTED:") for check in checks)


def _check(result: str, error_code: str, details: str) -> dict[str, str]:
    return {"result": result, "error_code": error_code, "details": details}


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def _canonical_sha256(value: Any) -> str:
    return hashlib.sha256(_canonical_json(value)).hexdigest()


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _is_string_list(value: Any) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) and item for item in value) and len(value) == len(set(value))


def _reference_ids(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.get("reference_id") for item in value if isinstance(item, dict)]


def _relative(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
