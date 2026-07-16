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

from spira_core import test_build_failure_producer as producer  # noqa: E402


DOMAIN = ROOT / "research" / "formal_core" / "domain2"
MANIFEST = ROOT / "research" / "test_build_failure_contract" / "corpus_manifest_v1.json"
ORACLE = ROOT / "research" / "test_build_failure_contract" / "oracle_v1.json"
LEAN_PROJECT = ROOT / "formal" / "spira_formal_core_v1"

RESULTS = DOMAIN / "spira_formal_core_v1_domain2_conformance_rerun_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain2_conformance_rerun_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain2_conformance_rerun_review.md"

FORMAL_ACTIONS = {"PROCEED", "STOP_BLOCKED", "RERUN_REQUIRED", "REPORT_NOT_EVALUATED"}


def main() -> None:
    manifest = _read_json(MANIFEST)
    oracle = _read_json(ORACLE)
    produced = producer.produce_cases(manifest, root=ROOT)
    lean = run_lake_build()
    proof_scan = scan_lean_sources()
    results = evaluate_conformance(manifest, oracle, produced, lean, proof_scan)
    _write_json(RESULTS, results)
    REPORT.write_text(report_markdown(results), encoding="utf-8", newline="\n")
    REVIEW.write_text(review_markdown(results), encoding="utf-8", newline="\n")
    print(json.dumps({"status": results["status"]}, sort_keys=True))
    if results["status"] != "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED":
        raise SystemExit(1)


def evaluate_conformance(
    manifest: Mapping[str, Any],
    oracle: Mapping[str, Any],
    produced: list[Mapping[str, Any]],
    lean: Mapping[str, Any],
    proof_scan: Mapping[str, Any],
) -> dict[str, Any]:
    expected_by_id = {str(case["case_id"]): case for case in oracle.get("cases", [])}
    produced_by_id = {str(case["case_id"]): case for case in produced}
    case_ids = sorted(expected_by_id)
    case_results = []
    mismatches = []
    note_cases = []
    test_notes_drops = []
    blocking_to_proceed = []
    not_evaluated_to_proceed = []
    malformed_to_proceed = []
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
        produced_projection = project_produced_case(produced_case)
        raw_action = expected["expected_policy_action"]["recommended_agent_action"]
        if raw_action == "REPORT_WITH_NOTES":
            note_cases.append(case_id)
            if expected_projection["action"] != "PROCEED":
                mismatches.append({"case_id": case_id, "field": "note_projection"})
            if "TEST_NOTES" not in expected_projection["reason_codes"]:
                test_notes_drops.append(case_id)
        if raw_action not in {"PROCEED", "REPORT_WITH_NOTES"} and expected_projection["action"] == "PROCEED":
            blocking_to_proceed.append(case_id)
        if expected.get("expected_not_evaluated") and expected_projection["action"] == "PROCEED":
            not_evaluated_to_proceed.append(case_id)
        if any("MALFORMED" in str(code) for code in expected_projection["reason_codes"]) and expected_projection["action"] == "PROCEED":
            malformed_to_proceed.append(case_id)

        checks = compare_projection(expected_projection, produced_projection)
        if not checks["all"]:
            for field, ok in checks["fields"].items():
                if not ok:
                    mismatches.append({"case_id": case_id, "field": field})
        if not checks["fields"]["identities"]:
            identity_drops.append(case_id)
        if not checks["fields"]["evidence_refs"]:
            evidence_drops.append(case_id)
        if not checks["fields"]["proof_refs"]:
            proof_drops.append(case_id)
        case_results.append(
            {
                "case_id": case_id,
                "oracle_action": raw_action,
                "formal_action": expected_projection["action"],
                "producer_formal_action": produced_projection["action"],
                "passed": checks["all"],
            }
        )

    mutation_pairs = manifest.get("mutation_pairs", [])
    mutation_pair_checks = evaluate_mutation_pairs(mutation_pairs, expected_by_id, produced_by_id)
    gates = {
        "lean_build_pass": lean["returncode"] == 0,
        "proof_scan_pass": proof_scan["status"] == "PASS",
        "case_count": len(case_ids) == 38,
        "producer_case_count": len(produced) == 38,
        "case_projection_pass": all(item["passed"] for item in case_results),
        "report_with_notes_count": len(note_cases) == 2,
        "report_with_notes_projected_to_proceed": all(
            item["formal_action"] == "PROCEED"
            for item in case_results
            if item["oracle_action"] == "REPORT_WITH_NOTES"
        ),
        "test_notes_preserved": not test_notes_drops,
        "blocking_to_proceed_count": len(blocking_to_proceed) == 0,
        "not_evaluated_to_proceed_count": len(not_evaluated_to_proceed) == 0,
        "malformed_to_proceed_count": len(malformed_to_proceed) == 0,
        "identity_drop_count": len(identity_drops) == 0,
        "evidence_drop_count": len(evidence_drops) == 0,
        "proof_drop_count": len(proof_drops) == 0,
        "mutation_pairs": mutation_pair_checks["passed"] == 6 and mutation_pair_checks["total"] == 6,
    }
    status = "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED"
    if not all(gates.values()) or mismatches:
        status = "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_NEEDS_REVISION"

    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_RERUN_RESULTS",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "authorization": "research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_rerun_authorization.md",
        "mapping_amendment_review": "research/formal_core/domain2/spira_formal_core_v1_domain2_action_mapping_amendment_review.md",
        "case_count": len(case_ids),
        "producer_case_count": len(produced),
        "case_pass_count": sum(1 for item in case_results if item["passed"]),
        "case_fail_count": sum(1 for item in case_results if not item["passed"]),
        "report_with_notes_cases": note_cases,
        "report_with_notes_case_count": len(note_cases),
        "test_notes_drops": test_notes_drops,
        "blocking_to_proceed_cases": blocking_to_proceed,
        "not_evaluated_to_proceed_cases": not_evaluated_to_proceed,
        "malformed_to_proceed_cases": malformed_to_proceed,
        "identity_drop_cases": identity_drops,
        "evidence_drop_cases": evidence_drops,
        "proof_drop_cases": proof_drops,
        "mutation_pair_checks": mutation_pair_checks,
        "gates": gates,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:100],
        "case_results": case_results,
        "lean_build": lean,
        "proof_scan": proof_scan,
        "raw_pytest_junit_parser_formally_proved": False,
        "not_authorized": [
            "FORMAL_CORE_V1_ACTION_ALGEBRA_CHANGE",
            "DOMAIN2_ORACLE_CHANGE",
            "DOMAIN2_CORPUS_CHANGE",
            "DOMAIN2_ADAPTER_CHANGE",
            "DOMAIN1_CONFORMANCE",
            "DOMAIN3_CONFORMANCE",
            "RUNTIME_INTEGRATION",
            "PRODUCTION_CLAIM",
            "RELEASE",
        ],
    }


def project_oracle_case(case: Mapping[str, Any]) -> dict[str, Any]:
    action = case["expected_policy_action"]["recommended_agent_action"]
    reason_codes = list(case["expected_policy_action"]["reason_codes"])
    projected_action = project_action(
        action=action,
        reason_codes=reason_codes,
        blocking_items=case["expected_explicit_lists"]["blocking_cases"],
        not_evaluated=case["expected_not_evaluated"],
    )
    return {
        "action": projected_action,
        "stop": projected_action != "PROCEED",
        "reason_codes": reason_codes,
        "blocking_items": _canonical_items(case["expected_explicit_lists"]["blocking_cases"]),
        "not_evaluated": list(case["expected_not_evaluated"]),
        "not_claimed": list(case["expected_not_claimed"]),
        "evidence_refs": _canonical_items(case["expected_evidence_locators"]),
        "proof_refs": _canonical_items(case["expected_identity_relationships"]),
        "identities": identity_projection(case),
    }


def project_produced_case(case: Mapping[str, Any]) -> dict[str, Any]:
    action = case["produced_policy_action"]["recommended_agent_action"]
    reason_codes = list(case["produced_policy_action"]["reason_codes"])
    projected_action = project_action(
        action=action,
        reason_codes=reason_codes,
        blocking_items=case["produced_explicit_lists"]["blocking_cases"],
        not_evaluated=case["produced_not_evaluated"],
    )
    return {
        "action": projected_action,
        "stop": projected_action != "PROCEED",
        "reason_codes": reason_codes,
        "blocking_items": _canonical_items(case["produced_explicit_lists"]["blocking_cases"]),
        "not_evaluated": list(case["produced_not_evaluated"]),
        "not_claimed": list(case["produced_not_claimed"]),
        "evidence_refs": _canonical_items(case["produced_evidence_locators"]),
        "proof_refs": _canonical_items(case["produced_identity_relationships"]),
        "identities": identity_projection(case, produced=True),
    }


def project_action(
    *,
    action: str,
    reason_codes: list[str],
    blocking_items: list[Any],
    not_evaluated: list[str],
) -> str:
    if action == "REPORT_WITH_NOTES":
        if "TEST_NOTES" not in reason_codes or blocking_items or not_evaluated:
            return "__INVALID_REPORT_WITH_NOTES_MAPPING__"
        return "PROCEED"
    if action in FORMAL_ACTIONS:
        return action
    return f"__UNSUPPORTED_ACTION__:{action}"


def compare_projection(expected: Mapping[str, Any], observed: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "action": observed["action"] == expected["action"],
        "stop": observed["stop"] == expected["stop"],
        "reason_codes": observed["reason_codes"] == expected["reason_codes"],
        "blocking_items": observed["blocking_items"] == expected["blocking_items"],
        "not_evaluated": observed["not_evaluated"] == expected["not_evaluated"],
        "not_claimed": observed["not_claimed"] == expected["not_claimed"],
        "evidence_refs": observed["evidence_refs"] == expected["evidence_refs"],
        "proof_refs": observed["proof_refs"] == expected["proof_refs"],
        "identities": observed["identities"] == expected["identities"],
    }
    return {"all": all(fields.values()), "fields": fields}


def evaluate_mutation_pairs(
    pairs: list[Mapping[str, Any]],
    expected_by_id: Mapping[str, Mapping[str, Any]],
    produced_by_id: Mapping[str, Mapping[str, Any]],
) -> dict[str, Any]:
    checks = []
    for pair in pairs:
        left = str(pair["source_case_id"])
        right = str(pair["mutated_case_id"])
        ok = left in expected_by_id and right in expected_by_id and left in produced_by_id and right in produced_by_id
        if ok:
            expected_left = project_oracle_case(expected_by_id[left])
            expected_right = project_oracle_case(expected_by_id[right])
            produced_left = project_produced_case(produced_by_id[left])
            produced_right = project_produced_case(produced_by_id[right])
            ok = (
                expected_left["proof_refs"] == produced_left["proof_refs"]
                and expected_right["proof_refs"] == produced_right["proof_refs"]
            )
        checks.append({"source_case_id": left, "mutated_case_id": right, "passed": ok})
    return {
        "passed": sum(1 for item in checks if item["passed"]),
        "total": len(checks),
        "failed": sum(1 for item in checks if not item["passed"]),
        "checks": checks,
    }


def identity_projection(case: Mapping[str, Any], *, produced: bool = False) -> dict[str, Any]:
    prefix = "produced" if produced else "expected"
    return {
        "scope_identity": case[f"{prefix}_scope_identity"],
        "result_identity": case[f"{prefix}_result_identity"],
        "relationships": case[f"{prefix}_identity_relationships"],
    }


def run_lake_build() -> dict[str, Any]:
    env = dict(os.environ)
    completed = subprocess.run(
        ["lake", "build"],
        cwd=LEAN_PROJECT,
        check=False,
        capture_output=True,
        text=True,
        env=env,
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
    for path in sorted((LEAN_PROJECT / "SpiraFormalCore" / "Domain2").glob("*.lean")):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                matches.append({"path": str(path.relative_to(ROOT)), "token": token})
    return {"status": "PASS" if not matches else "FAIL", "matches": matches}


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 2 Conformance Rerun Report",
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
                    "report_with_notes_cases": results["report_with_notes_cases"],
                    "test_notes_drops": results["test_notes_drops"],
                    "blocking_to_proceed_cases": results["blocking_to_proceed_cases"],
                    "not_evaluated_to_proceed_cases": results["not_evaluated_to_proceed_cases"],
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
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Raw pytest/JUnit parser formally proved: no.",
            "",
            "This report does not authorize Domain 1, Domain 3, runtime integration, production claims, or release activity.",
            "",
        ]
    )


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = results["status"] == "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED"
    statuses = [
        results["status"],
        "DOMAIN_2_FORMAL_TYPED_SEMANTICS_ACCEPTED" if accepted else "DOMAIN_2_FORMAL_TYPED_SEMANTICS_NOT_ACCEPTED",
        "DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED"
        if accepted
        else "DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_NOT_ACCEPTED",
        "DOMAIN_2_REPORT_WITH_NOTES_MAPPING_ACCEPTED_IN_CONFORMANCE"
        if accepted
        else "DOMAIN_2_REPORT_WITH_NOTES_MAPPING_NOT_ACCEPTED_IN_CONFORMANCE",
        "RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO",
        "DOMAIN_3_NOT_AUTHORIZED",
        "DOMAIN_1_NOT_AUTHORIZED",
        "RUNTIME_INTEGRATION_NOT_AUTHORIZED",
        "PRODUCTION_CLAIM_NOT_AUTHORIZED",
        "RELEASE_NOT_AUTHORIZED",
    ]
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 2 Conformance Rerun Review",
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
                "Domain 2 conformance is accepted under the reviewed action mapping."
                if accepted
                else "Domain 2 conformance is not accepted and requires revision."
            ),
            "",
            "The accepted `REPORT_WITH_NOTES` projection is:",
            "",
            "```text",
            "REPORT_WITH_NOTES -> PROCEED + TEST_NOTES",
            "```",
            "",
            "The Domain 2 oracle and corpus remain unchanged. The previous negative conformance result remains preserved.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(
                {
                    "case_count": results["case_count"],
                    "case_pass_count": results["case_pass_count"],
                    "case_fail_count": results["case_fail_count"],
                    "report_with_notes_case_count": results["report_with_notes_case_count"],
                    "test_notes_drops": len(results["test_notes_drops"]),
                    "blocking_to_proceed_cases": len(results["blocking_to_proceed_cases"]),
                    "not_evaluated_to_proceed_cases": len(results["not_evaluated_to_proceed_cases"]),
                    "identity_drop_cases": len(results["identity_drop_cases"]),
                    "evidence_drop_cases": len(results["evidence_drop_cases"]),
                    "proof_drop_cases": len(results["proof_drop_cases"]),
                    "mutation_pair_checks": {
                        "passed": results["mutation_pair_checks"]["passed"],
                        "total": results["mutation_pair_checks"]["total"],
                    },
                    "lean_build_returncode": results["lean_build"]["returncode"],
                    "proof_scan": results["proof_scan"]["status"],
                    "mismatch_count": results["mismatch_count"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundaries",
            "",
            "This review does not prove raw pytest/JUnit parsing, Python runtime correctness, filesystem behavior, or production integration.",
            "",
            "Domain 3 and Domain 1 conformance remain blocked until separately authorized.",
            "",
        ]
    )


def _canonical_items(items: list[Any]) -> list[str]:
    return [json.dumps(item, sort_keys=True, separators=(",", ":"), ensure_ascii=False) for item in items]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    main()
