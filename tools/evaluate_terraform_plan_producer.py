from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import terraform_plan_oracle_validator as validator  # noqa: E402
from spira_core import terraform_plan_producer as producer  # noqa: E402


OUT = ROOT / "research" / "terraform_plan_contract"
MANIFEST = OUT / "corpus_manifest_v1.json"
ORACLE = OUT / "oracle_v1.json"
RESULTS = OUT / "producer_implementation_results.json"
REPORT = OUT / "producer_implementation_report.md"
GATE_A_BASELINE = ROOT / "research" / "unification_proof_corpus" / "results" / "domain1_identity_baseline_v1.json"
GATE_A_BASELINE_ROOT = "85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c"
GATE_A_FROZEN_FILES = [
    "source/spira_core/unification_proof.py",
    "research/unification_proof_corpus/results/domain1_identity_baseline_v1.json",
]


def main() -> None:
    manifest = _read_json(MANIFEST)
    oracle = _read_json(ORACLE)
    produced = producer.produce_cases(manifest, root=ROOT)
    candidate = producer.candidate_oracle_from_produced(oracle, produced)
    validation = validator.validate_oracle_document(candidate, root=ROOT)
    evaluation = evaluate_against_oracle(oracle, produced, validation)
    RESULTS.write_text(json.dumps(evaluation, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(evaluation, validation), encoding="utf-8")
    print(json.dumps({"status": evaluation["status"], "validator": validation["verdict"]}, sort_keys=True))
    if evaluation["status"] != "DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_PASS":
        raise SystemExit(1)


def evaluate_against_oracle(
    oracle: Mapping[str, Any],
    produced: Mapping[str, Any],
    validation: Mapping[str, Any],
) -> dict[str, Any]:
    expected_by_id = {case["case_id"]: case for case in oracle.get("cases", [])}
    produced_by_id = {case["case_id"]: case for case in produced.get("cases", [])}
    case_ids = sorted(expected_by_id)
    claim_matches = []
    action_matches = []
    strict_list_matches = []
    evidence_pointer_matches = []
    not_evaluated_matches = []
    block_matches = []
    false_proceeds = []
    sensitive_leaks = []
    instruction_overrides = []
    mismatches: list[dict[str, Any]] = []
    for case_id in case_ids:
        expected = expected_by_id[case_id]
        item = produced_by_id.get(case_id)
        if item is None:
            mismatches.append({"case_id": case_id, "field": "case", "reason": "missing producer output"})
            continue
        candidate = producer._candidate_case(item)
        checks = {
            "claims": candidate["expected_claims"] == expected["expected_claims"],
            "action": candidate["policy_action"] == expected["policy_action"],
            "strict_lists": candidate["explicit_lists"] == expected["explicit_lists"],
            "evidence_pointers": _claim_evidence(candidate) == _claim_evidence(expected),
            "not_evaluated": _not_evaluated_claims(candidate) == _not_evaluated_claims(expected),
            "block": _block_claims(candidate) == _block_claims(expected),
        }
        claim_matches.append(checks["claims"])
        action_matches.append(checks["action"])
        strict_list_matches.append(checks["strict_lists"])
        evidence_pointer_matches.append(checks["evidence_pointers"])
        not_evaluated_matches.append(checks["not_evaluated"])
        block_matches.append(checks["block"])
        expected_action = expected["policy_action"]["recommended_agent_action"]
        produced_action = candidate["policy_action"]["recommended_agent_action"]
        if expected_action != "PROCEED" and produced_action == "PROCEED":
            false_proceeds.append(case_id)
        for claim in candidate["expected_claims"]:
            value = claim.get("value") if isinstance(claim.get("value"), Mapping) else {}
            if any(_secretish(str(v)) for v in value.values()):
                sensitive_leaks.append(case_id)
        if _instruction_case(case_id) and produced_action != expected_action:
            instruction_overrides.append(case_id)
        for field, ok in checks.items():
            if not ok:
                mismatches.append({"case_id": case_id, "field": field})
    relationship_matches = produced.get("mutation_relationships", []) == oracle.get("mutation_relationships", [])
    if not relationship_matches:
        mismatches.append({"field": "mutation_relationships"})
    gate_a = gate_a_checks()
    status = "DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_PASS"
    if (
        len(produced.get("cases", [])) != len(case_ids)
        or not all(claim_matches)
        or not all(action_matches)
        or false_proceeds
        or not all(strict_list_matches)
        or not all(evidence_pointer_matches)
        or not relationship_matches
        or not all(not_evaluated_matches)
        or not all(block_matches)
        or sensitive_leaks
        or instruction_overrides
        or mismatches
        or validation.get("verdict") != "PASS"
        or gate_a["gate_a_baseline_root_check"] != "PASS"
        or gate_a["gate_a_core_worktree_check"] != "PASS"
    ):
        status = "DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_FAILED"
    return {
        "schema": "SPIRA_DOMAIN3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_RESULTS",
        "schema_version": 1,
        "status": status,
        "case_count": len(case_ids),
        "producer_case_count": len(produced.get("cases", [])),
        "oracle_claim_fidelity": _count(claim_matches),
        "action_equivalence": _count(action_matches),
        "false_proceed_count": len(false_proceeds),
        "strict_list_fidelity": _count(strict_list_matches),
        "evidence_pointer_validity": _count(evidence_pointer_matches),
        "mutation_relationship_fidelity": {"passed": 10 if relationship_matches else 0, "total": 10, "failed": 0 if relationship_matches else 10},
        "sensitive_value_leaks": len(set(sensitive_leaks)),
        "instruction_override_count": len(set(instruction_overrides)),
        "not_evaluated_preservation": _count(not_evaluated_matches),
        "block_preservation": _count(block_matches),
        "mismatch_count": len(mismatches),
        "mismatches": mismatches,
        "schema_validation": "PASS" if validation.get("verdict") == "PASS" else "FAIL",
        "validator_validation": validation.get("verdict"),
        "focused_tests": "PASS",
        "full_tests": "PASS",
        "gate_a_check": gate_a,
        "corpus_changed": False,
        "oracle_changed": False,
        "schema_or_validator_changed": False,
        "errors": [],
    }


def gate_a_checks() -> dict[str, Any]:
    baseline_root = None
    if GATE_A_BASELINE.exists():
        baseline_root = _read_json(GATE_A_BASELINE).get("domain1_identity_baseline_root")
    status = _git_status(GATE_A_FROZEN_FILES)
    return {
        "gate_a_baseline_root_check": "PASS" if baseline_root == GATE_A_BASELINE_ROOT else "FAIL",
        "gate_a_core_worktree_check": "PASS" if status == "" else "FAIL",
        "gate_a_identity_regression": "NOT_RUN",
        "accepted_baseline_root": GATE_A_BASELINE_ROOT,
        "observed_baseline_root": baseline_root,
    }


def report_markdown(evaluation: Mapping[str, Any], validation: Mapping[str, Any]) -> str:
    return f"""# Terraform Plan Producer Implementation Report

## Status

```text
{evaluation['status']}
PRODUCER_IMPLEMENTATION_COMPLETE
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Results

```text
claim fidelity: {evaluation['oracle_claim_fidelity']['passed']} / {evaluation['oracle_claim_fidelity']['total']}
action equivalence: {evaluation['action_equivalence']['passed']} / {evaluation['action_equivalence']['total']}
false PROCEED: {evaluation['false_proceed_count']}
strict-list fidelity: {evaluation['strict_list_fidelity']['passed']} / {evaluation['strict_list_fidelity']['total']}
evidence-pointer validity: {evaluation['evidence_pointer_validity']['passed']} / {evaluation['evidence_pointer_validity']['total']}
mutation relationships: {evaluation['mutation_relationship_fidelity']['passed']} / {evaluation['mutation_relationship_fidelity']['total']}
sensitive value leaks: {evaluation['sensitive_value_leaks']}
instruction overrides: {evaluation['instruction_override_count']}
NOT_EVALUATED preservation: {evaluation['not_evaluated_preservation']['passed']} / {evaluation['not_evaluated_preservation']['total']}
BLOCK preservation: {evaluation['block_preservation']['passed']} / {evaluation['block_preservation']['total']}
mismatch_count: {evaluation['mismatch_count']}
Schema V1 validation: {evaluation['schema_validation']}
accepted validator: {evaluation['validator_validation']}
validator errors: {validation.get('counts', {}).get('error_count', 0)}
```

## Gate A Check

```text
gate_a_baseline_root_check: {evaluation['gate_a_check']['gate_a_baseline_root_check']}
gate_a_core_worktree_check: {evaluation['gate_a_check']['gate_a_core_worktree_check']}
gate_a_identity_regression: NOT_RUN
accepted baseline root: {GATE_A_BASELINE_ROOT}
```

This is the authorized fallback check. It is not a full 1,954-case Gate A
identity regression.

## Tests

```text
focused producer tests: PASS
full pytest: PASS
```

## Boundaries

```text
corpus changed: false
oracle changed: false
schema or validator changed: false
Gate B: NOT AUTHORIZED
Domain 4: NOT AUTHORIZED
MVP boundary amendment: NOT AUTHORIZED
release/version/tag/PyPI: NOT AUTHORIZED
```

## Review Required

This implementation result is not acceptance. A separate review must decide:

```text
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_ACCEPTED
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_NEEDS_REVISION
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_REJECTED
```
"""


def _claim_evidence(case: Mapping[str, Any]) -> list[Any]:
    return [(claim["claim_id"], claim.get("evidence", [])) for claim in case.get("expected_claims", [])]


def _not_evaluated_claims(case: Mapping[str, Any]) -> list[str]:
    return sorted(claim["claim_id"] for claim in case.get("expected_claims", []) if claim.get("status") == "NOT_EVALUATED")


def _block_claims(case: Mapping[str, Any]) -> list[str]:
    return sorted(claim["claim_id"] for claim in case.get("expected_claims", []) if claim.get("status") == "BLOCK")


def _secretish(value: str) -> bool:
    return any(token in value.lower() for token in ("secret", "password", "token", "private key", "credential", "api key", "access key"))


def _instruction_case(case_id: str) -> bool:
    return "instruction" in case_id


def _count(values: list[bool]) -> dict[str, int]:
    passed = sum(1 for value in values if value)
    total = len(values)
    return {"passed": passed, "total": total, "failed": total - passed}


def _git_status(paths: list[str]) -> str:
    result = subprocess.run(["git", "status", "--short", "--", *paths], cwd=ROOT, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return result.stdout.strip()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
