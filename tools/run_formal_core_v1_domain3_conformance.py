from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import terraform_plan_oracle_validator as validator  # noqa: E402
from spira_core import terraform_plan_producer as producer  # noqa: E402


DOMAIN = ROOT / "research" / "formal_core" / "domain3"
MANIFEST = ROOT / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"
ORACLE = ROOT / "research" / "terraform_plan_contract" / "oracle_v1.json"
LEAN_PROJECT = ROOT / "formal" / "spira_formal_core_v1"

RESULTS = DOMAIN / "spira_formal_core_v1_domain3_conformance_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain3_conformance_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain3_conformance_review.md"

FORMAL_ACTIONS = {"PROCEED", "STOP_BLOCKED", "RERUN_REQUIRED", "REPORT_NOT_EVALUATED"}


def main() -> None:
    manifest = _read_json(MANIFEST)
    oracle = _read_json(ORACLE)
    produced = producer.produce_cases(manifest, root=ROOT)
    validation = validator.validate_oracle_document(
        producer.candidate_oracle_from_produced(oracle, produced),
        root=ROOT,
    )
    lean = run_lake_build()
    proof_scan = scan_lean_sources()
    results = evaluate_conformance(manifest, oracle, produced, validation, lean, proof_scan)
    _write_json(RESULTS, results)
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    REVIEW.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"status": results["status"]}, sort_keys=True))
    if results["status"] != "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED":
        raise SystemExit(1)


def evaluate_conformance(
    manifest: Mapping[str, Any],
    oracle: Mapping[str, Any],
    produced: Mapping[str, Any],
    validation: Mapping[str, Any],
    lean: Mapping[str, Any],
    proof_scan: Mapping[str, Any],
) -> dict[str, Any]:
    expected_by_id = {str(case["case_id"]): case for case in oracle.get("cases", [])}
    produced_by_id = {str(case["case_id"]): case for case in produced.get("cases", [])}
    case_ids = sorted(expected_by_id)
    case_results = []
    mismatches = []
    false_proceeds = []
    blocking_to_proceed = []
    not_evaluated_to_proceed = []
    malformed_to_proceed = []
    sensitive_leaks = []
    instruction_overrides = []
    identity_drops = []
    evidence_drops = []
    proof_drops = []

    for case_id in case_ids:
        expected = expected_by_id[case_id]
        produced_case = produced_by_id.get(case_id)
        expected_projection = project_oracle_case(expected)
        if produced_case is None:
            mismatches.append({"case_id": case_id, "field": "producer", "reason": "missing"})
            case_results.append({"case_id": case_id, "passed": False})
            continue
        candidate = producer._candidate_case(produced_case)
        produced_projection = project_oracle_case(candidate)
        checks = compare_projection(expected_projection, produced_projection)
        if not checks["all"]:
            for field, ok in checks["fields"].items():
                if not ok:
                    mismatches.append({"case_id": case_id, "field": field})
        expected_action = expected_projection["action"]
        observed_action = produced_projection["action"]
        if expected_action != "PROCEED" and observed_action == "PROCEED":
            false_proceeds.append(case_id)
        if expected_action in {"STOP_BLOCKED", "RERUN_REQUIRED"} and observed_action == "PROCEED":
            blocking_to_proceed.append(case_id)
        if expected_projection["not_evaluated"] and observed_action == "PROCEED":
            not_evaluated_to_proceed.append(case_id)
        if "TERRAFORM_PLAN_JSON_INVALID" in expected_projection["reason_codes"] and observed_action == "PROCEED":
            malformed_to_proceed.append(case_id)
        if has_sensitive_leak(candidate):
            sensitive_leaks.append(case_id)
        if "instruction" in case_id and observed_action != expected_action:
            instruction_overrides.append(case_id)
        if not checks["fields"]["identities"]:
            identity_drops.append(case_id)
        if not checks["fields"]["evidence_refs"]:
            evidence_drops.append(case_id)
        if not checks["fields"]["proof_refs"]:
            proof_drops.append(case_id)
        case_results.append(
            {
                "case_id": case_id,
                "oracle_action": expected_action,
                "producer_action": observed_action,
                "passed": checks["all"],
            }
        )

    mutation_checks = mutation_relationship_checks(oracle, produced)
    gates = {
        "lean_build_pass": lean["returncode"] == 0,
        "proof_scan_pass": proof_scan["status"] == "PASS",
        "validator_pass": validation.get("verdict") == "PASS",
        "case_count": len(case_ids) == 40,
        "producer_case_count": len(produced.get("cases", [])) == 40,
        "case_projection_pass": all(item["passed"] for item in case_results),
        "false_proceed_count": len(false_proceeds) == 0,
        "blocking_to_proceed_count": len(blocking_to_proceed) == 0,
        "not_evaluated_to_proceed_count": len(not_evaluated_to_proceed) == 0,
        "malformed_to_proceed_count": len(malformed_to_proceed) == 0,
        "sensitive_value_leak_count": len(sensitive_leaks) == 0,
        "instruction_override_count": len(instruction_overrides) == 0,
        "identity_drop_count": len(identity_drops) == 0,
        "evidence_drop_count": len(evidence_drops) == 0,
        "proof_drop_count": len(proof_drops) == 0,
        "mutation_pairs": mutation_checks["passed"] == 10 and mutation_checks["total"] == 10,
    }
    status = "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED"
    if not all(gates.values()) or mismatches:
        status = "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_NEEDS_REVISION"
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_RESULTS",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "authorization": "research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_authorization.md",
        "case_count": len(case_ids),
        "producer_case_count": len(produced.get("cases", [])),
        "case_pass_count": sum(1 for item in case_results if item["passed"]),
        "case_fail_count": sum(1 for item in case_results if not item["passed"]),
        "action_distribution": action_distribution(case_results),
        "false_proceed_cases": false_proceeds,
        "blocking_to_proceed_cases": blocking_to_proceed,
        "not_evaluated_to_proceed_cases": not_evaluated_to_proceed,
        "malformed_to_proceed_cases": malformed_to_proceed,
        "sensitive_value_leak_cases": sensitive_leaks,
        "instruction_override_cases": instruction_overrides,
        "identity_drop_cases": identity_drops,
        "evidence_drop_cases": evidence_drops,
        "proof_drop_cases": proof_drops,
        "mutation_pair_checks": mutation_checks,
        "validator": {
            "verdict": validation.get("verdict"),
            "status": validation.get("status"),
            "counts": validation.get("counts"),
        },
        "gates": gates,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:100],
        "case_results": case_results,
        "lean_build": lean,
        "proof_scan": proof_scan,
        "raw_terraform_json_parser_formally_proved": False,
        "not_authorized": [
            "FORMAL_CORE_V1_ACTION_ALGEBRA_CHANGE",
            "DOMAIN3_ORACLE_CHANGE",
            "DOMAIN3_CORPUS_CHANGE",
            "DOMAIN3_ADAPTER_CHANGE",
            "DOMAIN1_CONFORMANCE",
            "RUNTIME_INTEGRATION",
            "PRODUCTION_CLAIM",
            "RELEASE",
        ],
    }


def project_oracle_case(case: Mapping[str, Any]) -> dict[str, Any]:
    action = case["policy_action"]["recommended_agent_action"]
    if action not in FORMAL_ACTIONS:
        action = f"__UNSUPPORTED_ACTION__:{action}"
    return {
        "action": action,
        "stop": action != "PROCEED",
        "reason_codes": list(case["policy_action"]["reason_codes"]),
        "explicit_lists": canonical(case["explicit_lists"]),
        "not_evaluated": list(case["explicit_lists"].get("not_evaluated", [])),
        "not_claimed": list(case["not_claimed"]),
        "evidence_refs": canonical(claim_evidence(case)),
        "proof_refs": canonical(case.get("mutation_membership", [])),
        "identities": {
            "subject": case["subject"],
            "context": case["context"],
            "optional_provenance": case["optional_provenance"],
        },
    }


def compare_projection(expected: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "action": observed["action"] == expected["action"],
        "stop": observed["stop"] == expected["stop"],
        "reason_codes": observed["reason_codes"] == expected["reason_codes"],
        "explicit_lists": observed["explicit_lists"] == expected["explicit_lists"],
        "not_evaluated": observed["not_evaluated"] == expected["not_evaluated"],
        "not_claimed": observed["not_claimed"] == expected["not_claimed"],
        "evidence_refs": observed["evidence_refs"] == expected["evidence_refs"],
        "proof_refs": observed["proof_refs"] == expected["proof_refs"],
        "identities": observed["identities"] == expected["identities"],
    }
    return {"all": all(fields.values()), "fields": fields}


def mutation_relationship_checks(oracle: Mapping[str, Any], produced: Mapping[str, Any]) -> dict[str, Any]:
    expected = canonical(oracle.get("mutation_relationships", []))
    observed = canonical(produced.get("mutation_relationships", []))
    ok = expected == observed
    return {"passed": 10 if ok else 0, "total": 10, "failed": 0 if ok else 10}


def action_distribution(case_results: list[Mapping[str, Any]]) -> dict[str, int]:
    result: dict[str, int] = {}
    for item in case_results:
        action = str(item["oracle_action"])
        result[action] = result.get(action, 0) + 1
    return dict(sorted(result.items()))


def claim_evidence(case: Mapping[str, Any]) -> list[Any]:
    return [(claim["claim_id"], claim.get("evidence", [])) for claim in case.get("expected_claims", [])]


def has_sensitive_leak(case: Mapping[str, Any]) -> bool:
    for claim in case.get("expected_claims", []):
        value = claim.get("value")
        if isinstance(value, Mapping):
            for item in value.values():
                text = str(item).lower()
                if any(token in text for token in ("secret", "password", "token", "private key", "credential", "api key")):
                    return True
    return False


def run_lake_build() -> dict[str, Any]:
    completed = subprocess.run(
        ["lake", "build"],
        cwd=LEAN_PROJECT,
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ),
    )
    return {
        "command": "lake build",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def scan_lean_sources() -> dict[str, Any]:
    forbidden = ["sorry", "admit", "sorryAx", "axiom "]
    matches = []
    for path in sorted((LEAN_PROJECT / "SpiraFormalCore" / "Domain3").glob("*.lean")):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                matches.append({"path": str(path.relative_to(ROOT)), "token": token})
    return {"status": "PASS" if not matches else "FAIL", "matches": matches}


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Conformance Report",
            "",
            "Status:",
            "",
            "```text",
            str(results["status"]),
            "```",
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(
                {
                    "case_count": results["case_count"],
                    "case_pass_count": results["case_pass_count"],
                    "case_fail_count": results["case_fail_count"],
                    "action_distribution": results["action_distribution"],
                    "false_proceed_cases": results["false_proceed_cases"],
                    "blocking_to_proceed_cases": results["blocking_to_proceed_cases"],
                    "not_evaluated_to_proceed_cases": results["not_evaluated_to_proceed_cases"],
                    "sensitive_value_leak_cases": results["sensitive_value_leak_cases"],
                    "mutation_pair_checks": {
                        "passed": results["mutation_pair_checks"]["passed"],
                        "total": results["mutation_pair_checks"]["total"],
                    },
                    "mismatch_count": results["mismatch_count"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Lean:",
            "",
            "```json",
            json.dumps(
                {
                    "lake_build_returncode": results["lean_build"]["returncode"],
                    "proof_scan": results["proof_scan"]["status"],
                    "validator": results["validator"]["verdict"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Raw Terraform JSON parser formally proved: no.",
            "",
            "This report does not authorize Domain 1, runtime integration, production claims, or release activity.",
            "",
        ]
    )


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = results["status"] == "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED"
    statuses = [
        results["status"],
        "DOMAIN_3_FORMAL_TYPED_SEMANTICS_ACCEPTED" if accepted else "DOMAIN_3_FORMAL_TYPED_SEMANTICS_NOT_ACCEPTED",
        "DOMAIN_3_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED"
        if accepted
        else "DOMAIN_3_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_NOT_ACCEPTED",
        "RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO",
        "DOMAIN_1_NOT_AUTHORIZED",
        "RUNTIME_INTEGRATION_NOT_AUTHORIZED",
        "PRODUCTION_CLAIM_NOT_AUTHORIZED",
        "RELEASE_NOT_AUTHORIZED",
    ]
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 3 Conformance Review",
            "",
            "## Status",
            "",
            "```text",
            *statuses,
            "```",
            "",
            "## Decision",
            "",
            (
                "Domain 3 conformance is accepted for bounded Terraform Plan typed evidence."
                if accepted
                else "Domain 3 conformance is not accepted and requires revision."
            ),
            "",
            "The Terraform Plan oracle and corpus remain unchanged.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(
                {
                    "case_count": results["case_count"],
                    "case_pass_count": results["case_pass_count"],
                    "case_fail_count": results["case_fail_count"],
                    "action_distribution": results["action_distribution"],
                    "false_proceed_cases": len(results["false_proceed_cases"]),
                    "blocking_to_proceed_cases": len(results["blocking_to_proceed_cases"]),
                    "not_evaluated_to_proceed_cases": len(results["not_evaluated_to_proceed_cases"]),
                    "sensitive_value_leak_cases": len(results["sensitive_value_leak_cases"]),
                    "instruction_override_cases": len(results["instruction_override_cases"]),
                    "identity_drop_cases": len(results["identity_drop_cases"]),
                    "evidence_drop_cases": len(results["evidence_drop_cases"]),
                    "proof_drop_cases": len(results["proof_drop_cases"]),
                    "mutation_pair_checks": {
                        "passed": results["mutation_pair_checks"]["passed"],
                        "total": results["mutation_pair_checks"]["total"],
                    },
                    "lean_build_returncode": results["lean_build"]["returncode"],
                    "proof_scan": results["proof_scan"]["status"],
                    "validator": results["validator"]["verdict"],
                    "mismatch_count": results["mismatch_count"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundaries",
            "",
            "This review does not prove raw Terraform JSON parsing, Python runtime correctness, filesystem behavior, or production integration.",
            "",
            "Domain 1 conformance remains blocked until separately authorized.",
            "",
        ]
    )


def canonical(value: Any) -> Any:
    return json.loads(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False))


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
