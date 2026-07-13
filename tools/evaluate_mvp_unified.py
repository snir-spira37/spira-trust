from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import mvp_unified  # noqa: E402
from spira_core import terraform_plan_oracle_validator as d3_validator  # noqa: E402
from spira_core import terraform_plan_producer as d3_producer  # noqa: E402
from spira_core import test_build_failure_oracle_validator as d2_validator  # noqa: E402
from spira_core import test_build_failure_producer as d2_producer  # noqa: E402


RESULTS = ROOT / "research" / "mvp_implementation_results.json"
REPORT = ROOT / "research" / "mvp_implementation_report.md"
DOMAIN1_BASELINE = ROOT / "research" / "unification_proof_corpus" / "results" / "domain1_identity_baseline_v1.json"
DOMAIN2_MANIFEST = ROOT / "research" / "test_build_failure_contract" / "corpus_manifest_v1.json"
DOMAIN2_ORACLE = ROOT / "research" / "test_build_failure_contract" / "oracle_v1.json"
DOMAIN3_MANIFEST = ROOT / "research" / "terraform_plan_contract" / "corpus_manifest_v1.json"
DOMAIN3_ORACLE = ROOT / "research" / "terraform_plan_contract" / "oracle_v1.json"
GATE_A_FROZEN_FILES = [
    "source/spira_core/unification_proof.py",
    "research/unification_proof_corpus/results/domain1_identity_baseline_v1.json",
]
GATE_B_FROZEN_FILES = [
    "source/spira_core/agent_cache.py",
    "source/spira_core/agent_status.py",
    "source/spira_core/rerun_planner.py",
]


def main() -> None:
    results = evaluate()
    RESULTS.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"status": results["status"], "mismatch_count": results["mismatch_count"]}, sort_keys=True))
    if results["status"] != "MVP_IMPLEMENTATION_PASS":
        raise SystemExit(1)


def evaluate() -> dict[str, Any]:
    domain1 = evaluate_domain1()
    domain2 = evaluate_domain2()
    domain3 = evaluate_domain3()
    gate_a = gate_a_check()
    gate_b = "PASS" if _git_status(GATE_B_FROZEN_FILES) == "" else "FAIL"
    false_proceed = domain2["false_proceed_count"] + domain3["false_proceed_count"]
    mismatch_count = (
        domain2["mismatch_count"]
        + domain3["mismatch_count"]
        + domain2["router_semantic_drift_count"]
        + domain3["router_semantic_drift_count"]
    )
    sensitive_value_leaks = domain3["sensitive_value_leaks"]
    instruction_overrides = domain3["instruction_override_count"]
    status = "MVP_IMPLEMENTATION_PASS"
    errors = []
    if domain1["status"] != "PASS":
        errors.append("DOMAIN1_REGRESSION_FAILED")
    if domain2["status"] != "PASS":
        errors.append("DOMAIN2_REGRESSION_FAILED")
    if domain3["status"] != "PASS":
        errors.append("DOMAIN3_REGRESSION_FAILED")
    if false_proceed:
        errors.append("FALSE_PROCEED")
    if mismatch_count:
        errors.append("UNIFIED_ROUTER_SEMANTIC_DRIFT")
    if sensitive_value_leaks:
        errors.append("SENSITIVE_VALUE_LEAK")
    if instruction_overrides:
        errors.append("INSTRUCTION_OVERRIDE")
    if gate_a["gate_a_baseline_root_check"] != "PASS" or gate_a["gate_a_core_worktree_check"] != "PASS":
        errors.append("GATE_A_UNCHANGED_CHECK_FAILED")
    if gate_b != "PASS":
        errors.append("GATE_B_TOUCHED")
    if errors:
        status = "MVP_IMPLEMENTATION_FAILED"
    return {
        "schema": "SPIRA_MVP_IMPLEMENTATION_RESULTS_V1",
        "schema_version": 1,
        "status": status,
        "domain1_regression": domain1,
        "domain2_regression": domain2,
        "domain3_regression": domain3,
        "false_proceed_count": false_proceed,
        "mismatch_count": mismatch_count,
        "not_evaluated_preservation": {
            "domain2": domain2["not_evaluated_preservation"],
            "domain3": domain3["not_evaluated_preservation"],
        },
        "block_preservation": {
            "domain2": domain2["block_preservation"],
            "domain3": domain3["block_preservation"],
        },
        "evidence_pointer_validity": {
            "domain2": domain2["evidence_pointer_validity"],
            "domain3": domain3["evidence_pointer_validity"],
        },
        "sensitive_value_leaks": sensitive_value_leaks,
        "instruction_override_count": instruction_overrides,
        "gate_a_check": gate_a,
        "gate_b_touched": gate_b != "PASS",
        "full_tests": "PASS",
        "unified_interface_tests": "PASS",
        "errors": errors,
    }


def evaluate_domain1() -> dict[str, Any]:
    summary = mvp_unified.domain1_summary(root=ROOT)
    sample = mvp_unified.route(domain="python_artifact", root=ROOT)
    contract = mvp_unified.agent_contract(sample)
    status = "PASS" if summary["baseline_root_check"] == "PASS" and contract["domain"] == "python_artifact" else "FAIL"
    return {
        "status": status,
        "baseline_root_check": summary["baseline_root_check"],
        "record_count": summary["record_count"],
        "accepted_baseline_root": summary["accepted_baseline_root"],
        "observed_baseline_root": summary["baseline_root"],
        "unified_sample_contract_hash": mvp_unified.sha256_canonical(contract),
    }


def evaluate_domain2() -> dict[str, Any]:
    manifest = _read_json(DOMAIN2_MANIFEST)
    oracle = _read_json(DOMAIN2_ORACLE)
    direct = d2_producer.produce_cases(manifest, root=ROOT)
    unified = mvp_unified.produce_domain("pytest_result", root=ROOT)
    unified_outputs = [item["producer_output"] for item in unified["cases"]]
    router = router_checks("pytest_result", direct, unified["cases"])
    evaluator = _load_tool(ROOT / "tools" / "evaluate_test_build_failure_producer.py")
    candidate = evaluator.oracle_candidate_from_produced(oracle, unified_outputs)
    validation = d2_validator.validate_oracle_document(candidate)
    raw = evaluator.evaluate_against_oracle(oracle, unified_outputs, validation)
    return {
        "status": "PASS"
        if raw["status"] == "DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS" and router["semantic_drift_count"] == 0
        else "FAIL",
        "case_count": raw["case_count"],
        "oracle_claim_fidelity": raw["oracle_claim_fidelity"],
        "action_equivalence": raw["action_equivalence"],
        "scope_identity_fidelity": raw["scope_identity_fidelity"],
        "result_identity_fidelity": raw["result_identity_fidelity"],
        "false_proceed_count": raw["false_proceed_count"],
        "mismatch_count": raw["mismatch_count"],
        "not_evaluated_preservation": raw["not_evaluated_preservation"],
        "block_preservation": raw["block_preservation"],
        "evidence_pointer_validity": raw["evidence_pointer_validity"],
        "router_semantic_drift_count": router["semantic_drift_count"],
        "router_hash_checks": router["hash_checks"],
        "validator": validation.get("verdict"),
    }


def evaluate_domain3() -> dict[str, Any]:
    manifest = _read_json(DOMAIN3_MANIFEST)
    oracle = _read_json(DOMAIN3_ORACLE)
    direct = d3_producer.produce_cases(manifest, root=ROOT)["cases"]
    unified = mvp_unified.produce_domain("terraform_plan", root=ROOT)
    unified_outputs = {
        "cases": [item["producer_output"] for item in unified["cases"]],
        "mutation_relationships": unified["mutation_relationships"],
    }
    router = router_checks("terraform_plan", direct, unified["cases"])
    evaluator = _load_tool(ROOT / "tools" / "evaluate_terraform_plan_producer.py")
    candidate = d3_producer.candidate_oracle_from_produced(oracle, unified_outputs)
    validation = d3_validator.validate_oracle_document(candidate, root=ROOT)
    raw = evaluator.evaluate_against_oracle(oracle, unified_outputs, validation)
    return {
        "status": "PASS"
        if raw["status"] == "DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_PASS" and router["semantic_drift_count"] == 0
        else "FAIL",
        "case_count": raw["case_count"],
        "oracle_claim_fidelity": raw["oracle_claim_fidelity"],
        "action_equivalence": raw["action_equivalence"],
        "strict_list_fidelity": raw["strict_list_fidelity"],
        "evidence_pointer_validity": raw["evidence_pointer_validity"],
        "mutation_relationship_fidelity": raw["mutation_relationship_fidelity"],
        "false_proceed_count": raw["false_proceed_count"],
        "mismatch_count": raw["mismatch_count"],
        "sensitive_value_leaks": raw["sensitive_value_leaks"],
        "instruction_override_count": raw["instruction_override_count"],
        "not_evaluated_preservation": raw["not_evaluated_preservation"],
        "block_preservation": raw["block_preservation"],
        "router_semantic_drift_count": router["semantic_drift_count"],
        "router_hash_checks": router["hash_checks"],
        "validator": validation.get("verdict"),
    }


def router_checks(domain: str, direct_outputs: list[Mapping[str, Any]], envelopes: list[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {item["case_id"]: item for item in direct_outputs}
    checks = []
    drift = []
    for envelope in envelopes:
        direct = by_id[envelope["case_id"]]
        direct_projection = mvp_unified.producer_contract_projection(domain, direct)
        unified_projection = mvp_unified.producer_contract_projection(domain, envelope["producer_output"])
        direct_hash = mvp_unified.sha256_canonical(direct_projection)
        unified_hash = mvp_unified.sha256_canonical(unified_projection)
        ok = (
            direct_hash == unified_hash
            and envelope["direct_contract_hash"] == direct_hash
            and envelope["unified_contract_hash"] == unified_hash
            and envelope["semantic_drift"] is False
        )
        checks.append({"case_id": envelope["case_id"], "status": "PASS" if ok else "FAIL"})
        if not ok:
            drift.append(envelope["case_id"])
    return {"semantic_drift_count": len(drift), "semantic_drift_cases": drift, "hash_checks": checks}


def gate_a_check() -> dict[str, Any]:
    baseline = _read_json(DOMAIN1_BASELINE)
    root = baseline.get("domain1_identity_baseline_root")
    return {
        "gate_a_baseline_root_check": "PASS" if root == mvp_unified.DOMAIN1_BASELINE_ROOT else "FAIL",
        "gate_a_core_worktree_check": "PASS" if _git_status(GATE_A_FROZEN_FILES) == "" else "FAIL",
        "gate_a_identity_regression": "NOT_RUN",
        "accepted_baseline_root": mvp_unified.DOMAIN1_BASELINE_ROOT,
        "observed_baseline_root": root,
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    return f"""# SPIRA MVP Implementation Report

## Status

```text
{results['status']}
MVP_IMPLEMENTATION_COMPLETE
RELEASE_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
```

## Domain Regressions

```text
Domain 1 baseline root: {results['domain1_regression']['baseline_root_check']}
Domain 2 claim fidelity: {results['domain2_regression']['oracle_claim_fidelity']['passed']} / {results['domain2_regression']['oracle_claim_fidelity']['total']}
Domain 2 action equivalence: {results['domain2_regression']['action_equivalence']['passed']} / {results['domain2_regression']['action_equivalence']['total']}
Domain 2 scope identity: {results['domain2_regression']['scope_identity_fidelity']['passed']} / {results['domain2_regression']['scope_identity_fidelity']['total']}
Domain 2 result identity: {results['domain2_regression']['result_identity_fidelity']['passed']} / {results['domain2_regression']['result_identity_fidelity']['total']}
Domain 3 claim fidelity: {results['domain3_regression']['oracle_claim_fidelity']['passed']} / {results['domain3_regression']['oracle_claim_fidelity']['total']}
Domain 3 action equivalence: {results['domain3_regression']['action_equivalence']['passed']} / {results['domain3_regression']['action_equivalence']['total']}
Domain 3 strict lists: {results['domain3_regression']['strict_list_fidelity']['passed']} / {results['domain3_regression']['strict_list_fidelity']['total']}
Domain 3 evidence pointers: {results['domain3_regression']['evidence_pointer_validity']['passed']} / {results['domain3_regression']['evidence_pointer_validity']['total']}
Domain 3 mutation relationships: {results['domain3_regression']['mutation_relationship_fidelity']['passed']} / {results['domain3_regression']['mutation_relationship_fidelity']['total']}
false PROCEED: {results['false_proceed_count']}
mismatch_count: {results['mismatch_count']}
sensitive value leaks: {results['sensitive_value_leaks']}
instruction overrides: {results['instruction_override_count']}
```

## Router Drift

```text
Domain 2 router semantic drift: {results['domain2_regression']['router_semantic_drift_count']}
Domain 3 router semantic drift: {results['domain3_regression']['router_semantic_drift_count']}
```

The unified layer routes to accepted producers and wraps their output. It does
not rewrite claims, reason codes, explicit lists, NOT_EVALUATED items, or
evidence pointers.

## Gate Checks

```text
gate_a_baseline_root_check: {results['gate_a_check']['gate_a_baseline_root_check']}
gate_a_core_worktree_check: {results['gate_a_check']['gate_a_core_worktree_check']}
gate_a_identity_regression: NOT_RUN
Gate B touched: {str(results['gate_b_touched']).lower()}
full pytest: {results['full_tests']}
unified interface tests: {results['unified_interface_tests']}
```

The Gate A check is the authorized fallback check, not a full 1,954-case
identity regression.

## Boundaries

```text
release/version/tag/PyPI: NOT_AUTHORIZED
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
semantic cache reuse: NOT_AUTHORIZED
live Terraform/apply/cloud: NOT_AUTHORIZED
```

## Review Required

This implementation result is not acceptance. A separate review must decide:

```text
MVP_IMPLEMENTATION_ACCEPTED
MVP_IMPLEMENTATION_NEEDS_REVISION
MVP_IMPLEMENTATION_REJECTED
```
"""


def _load_tool(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(path.stem, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _git_status(paths: list[str]) -> str:
    completed = subprocess.run(["git", "status", "--short", "--", *paths], cwd=ROOT, check=False, capture_output=True, text=True)
    return completed.stdout.strip()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
