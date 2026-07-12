from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import test_build_failure_oracle_validator as validator  # noqa: E402
from spira_core import test_build_failure_producer as producer  # noqa: E402


OUT = ROOT / "research" / "test_build_failure_contract"
MANIFEST = OUT / "corpus_manifest_v1.json"
ORACLE = OUT / "oracle_v1.json"
REPORT = OUT / "producer_implementation_report.md"
RESULTS = OUT / "producer_implementation_results.json"


def main() -> None:
    manifest = _read_json(MANIFEST)
    oracle = _read_json(ORACLE)
    produced = producer.produce_cases(manifest, root=ROOT)
    candidate = oracle_candidate_from_produced(oracle, produced)
    validation = validator.validate_oracle_document(candidate)
    evaluation = evaluate_against_oracle(oracle, produced, validation)
    _write_json(RESULTS, evaluation)
    REPORT.write_text(report_markdown(evaluation, validation), encoding="utf-8")
    print(json.dumps({"status": evaluation["status"], "validator": validation["verdict"]}, sort_keys=True))
    if evaluation["status"] != "DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS":
        raise SystemExit(1)


def oracle_candidate_from_produced(oracle: Mapping[str, Any], produced_cases: list[Mapping[str, Any]]) -> dict[str, Any]:
    candidate = {key: value for key, value in oracle.items() if key != "cases"}
    candidate["cases"] = [candidate_case(item) for item in produced_cases]
    return candidate


def candidate_case(produced: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "case_id": produced["case_id"],
        "case_schema_version": produced["case_schema_version"],
        "review_class": "AUTHOR_REVIEW",
        "review_status": "REVIEWED",
        "input_manifest_sha256": produced["input_manifest_sha256"],
        "input_sources": produced["input_sources"],
        "supported_input": produced["supported_input"],
        "expected_source_sufficiency": produced["produced_source_sufficiency"],
        "expected_scope_identity": produced["produced_scope_identity"],
        "expected_result_identity": produced["produced_result_identity"],
        "expected_policy_action": produced["produced_policy_action"],
        "expected_identity_relationships": produced["produced_identity_relationships"],
        "expected_claims": produced["produced_claims"],
        "expected_explicit_lists": produced["produced_explicit_lists"],
        "expected_not_evaluated": produced["produced_not_evaluated"],
        "expected_not_claimed": produced["produced_not_claimed"],
        "expected_evidence_locators": produced["produced_evidence_locators"],
    }


def evaluate_against_oracle(
    oracle: Mapping[str, Any],
    produced_cases: list[Mapping[str, Any]],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    expected_by_id = {case["case_id"]: case for case in oracle.get("cases", [])}
    produced_by_id = {case["case_id"]: case for case in produced_cases}
    case_ids = sorted(expected_by_id)
    claim_matches = []
    action_matches = []
    strict_list_matches = []
    evidence_pointer_matches = []
    relationship_matches = []
    not_evaluated_matches = []
    block_matches = []
    false_proceeds = []
    mismatches: list[dict[str, Any]] = []
    for case_id in case_ids:
        expected = expected_by_id[case_id]
        produced = produced_by_id.get(case_id)
        if produced is None:
            mismatches.append({"case_id": case_id, "field": "case", "reason": "missing producer output"})
            continue
        checks = {
            "claims": produced["produced_claims"] == expected["expected_claims"],
            "action": produced["produced_policy_action"] == expected["expected_policy_action"],
            "strict_lists": produced["produced_explicit_lists"] == expected["expected_explicit_lists"],
            "evidence_pointers": produced["produced_evidence_locators"] == expected["expected_evidence_locators"],
            "relationships": produced["produced_identity_relationships"] == expected["expected_identity_relationships"],
            "not_evaluated": produced["produced_not_evaluated"] == expected["expected_not_evaluated"],
            "block": _claim_statuses(produced["produced_claims"]) == _claim_statuses(expected["expected_claims"]),
            "scope_identity": produced["produced_scope_identity"] == expected["expected_scope_identity"],
            "result_identity": produced["produced_result_identity"] == expected["expected_result_identity"],
        }
        claim_matches.append(checks["claims"])
        action_matches.append(checks["action"])
        strict_list_matches.append(checks["strict_lists"])
        evidence_pointer_matches.append(checks["evidence_pointers"])
        relationship_matches.append(checks["relationships"])
        not_evaluated_matches.append(checks["not_evaluated"])
        block_matches.append(checks["block"])
        expected_action = expected["expected_policy_action"]["recommended_agent_action"]
        produced_action = produced["produced_policy_action"]["recommended_agent_action"]
        if expected_action != "PROCEED" and produced_action == "PROCEED":
            false_proceeds.append(case_id)
        for field, ok in checks.items():
            if not ok:
                mismatches.append({"case_id": case_id, "field": field})
    gate_a_check = gate_a_unchanged()
    status = "DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS"
    if (
        len(produced_cases) != len(case_ids)
        or not all(claim_matches)
        or not all(action_matches)
        or false_proceeds
        or not all(strict_list_matches)
        or not all(evidence_pointer_matches)
        or not all(relationship_matches)
        or not all(not_evaluated_matches)
        or not all(block_matches)
        or validation.get("verdict") != "PASS"
        or gate_a_check != "PASS"
    ):
        status = "DOMAIN_2_PRODUCER_IMPLEMENTATION_FAILED"
    return {
        "schema": "SPIRA_DOMAIN2_PRODUCER_IMPLEMENTATION_RESULTS",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "authorization": "research/test_build_failure_contract_producer_implementation_authorization.md",
        "producer_module": "source/spira_core/test_build_failure_producer.py",
        "case_count": len(case_ids),
        "producer_case_count": len(produced_cases),
        "oracle_claim_fidelity": _count(all_values=claim_matches),
        "action_equivalence": _count(all_values=action_matches),
        "false_proceed_count": len(false_proceeds),
        "false_proceed_cases": false_proceeds,
        "strict_list_fidelity": _count(all_values=strict_list_matches),
        "evidence_pointer_validity": _count(all_values=evidence_pointer_matches),
        "identity_relationship_preservation": _count(all_values=relationship_matches),
        "not_evaluated_preservation": _count(all_values=not_evaluated_matches),
        "block_preservation": _count(all_values=block_matches),
        "schema_v7_validation": "PASS" if validation.get("verdict") == "PASS" else "FAIL",
        "accepted_validator_verdict": validation.get("verdict"),
        "accepted_validator_status": validation.get("status"),
        "accepted_validator_counts": validation.get("counts"),
        "gate_a_identity_unchanged": gate_a_check,
        "producer_output_observed": True,
        "oracle_authoring_producer_output_observed": False,
        "not_authorized": [
            "CORPUS_MODIFICATION",
            "ORACLE_MODIFICATION",
            "SCHEMA_V7_MODIFICATION",
            "VALIDATOR_MODIFICATION",
            "GATE_A_REFACTOR",
            "GATE_B",
            "DOMAIN_3",
            "RELEASE_VERSION_TAG_PYPI",
        ],
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:50],
    }


def gate_a_unchanged() -> str:
    files = [
        "source/spira_core/unification_proof.py",
        "research/unification_proof_corpus/results/domain1_identity_baseline_v1.json",
    ]
    try:
        completed = subprocess.run(
            ["git", "status", "--short", "--", *files],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "UNKNOWN"
    return "PASS" if completed.returncode == 0 and not completed.stdout.strip() else "FAIL"


def report_markdown(results: Mapping[str, Any], validation: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Test/Build Failure Contract Producer Implementation Report",
            "",
            "Status:",
            "",
            "```text",
            str(results["status"]),
            "GATE_B_NOT_AUTHORIZED",
            "DOMAIN_3_NOT_AUTHORIZED",
            "```",
            "",
            "Acceptance gates:",
            "",
            "```json",
            json.dumps(
                {
                    "case_count": results["case_count"],
                    "oracle_claim_fidelity": results["oracle_claim_fidelity"],
                    "action_equivalence": results["action_equivalence"],
                    "false_proceed_count": results["false_proceed_count"],
                    "strict_list_fidelity": results["strict_list_fidelity"],
                    "evidence_pointer_validity": results["evidence_pointer_validity"],
                    "identity_relationship_preservation": results["identity_relationship_preservation"],
                    "not_evaluated_preservation": results["not_evaluated_preservation"],
                    "block_preservation": results["block_preservation"],
                    "gate_a_identity_unchanged": results["gate_a_identity_unchanged"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Validator:",
            "",
            "```json",
            json.dumps(
                {
                    "verdict": validation.get("verdict"),
                    "status": validation.get("status"),
                    "counts": validation.get("counts"),
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "This report does not authorize Gate B, Domain 3, release activity, or changes to the accepted corpus/oracle/schema/validator.",
            "",
        ]
    )


def _claim_statuses(claims: list[Mapping[str, Any]]) -> list[str]:
    return sorted(str(claim.get("status")) for claim in claims)


def _count(*, all_values: list[bool]) -> dict[str, int]:
    passed = sum(1 for item in all_values if item)
    return {
        "passed": passed,
        "total": len(all_values),
        "failed": len(all_values) - passed,
    }


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
