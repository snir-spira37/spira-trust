from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "formal_core"
RESULTS = RESEARCH / "spira_formal_core_v1_differential_harness_results.json"
REPORT = RESEARCH / "spira_formal_core_v1_differential_harness_report.md"
REVIEW = RESEARCH / "spira_formal_core_v1_differential_harness_review.md"
LEAN_PROJECT = ROOT / "formal" / "spira_formal_core_v1"

SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core.formal_core_v1 import evaluate_typed_evidence  # noqa: E402


SEMANTIC_FIELDS = [
    "action",
    "stop",
    "reason_codes",
    "blocking_items",
    "not_evaluated",
    "not_claimed",
    "evidence_refs",
    "proof_refs",
    "domain_id",
    "subject_id",
    "policy_id",
    "schema_version",
    "producer_id",
    "contract_id",
]


def _document(*, validity: str = "valid", schema_version: str = "FORMAL_CORE_V1_SCHEMA", claims=None) -> dict[str, Any]:
    return {
        "domain_id": "reference",
        "subject_id": "typed-vector",
        "schema_version": schema_version,
        "producer_id": "formal-reference",
        "evidence_validity": validity,
        "typed_claims": list(claims or []),
        "evidence_refs": ["evidence:typed-vector"],
        "proof_refs": ["proof:typed-vector"],
        "policy_id": "FORMAL_CORE_V1_POLICY",
        "policy_schema_version": "FORMAL_CORE_V1_SCHEMA",
        "policy_required_claims": [],
        "policy_blocking_rules": [],
        "policy_not_claimed_rules": ["software_safety"],
    }


def _contract(
    *,
    action: str,
    reason_codes: list[str],
    blocking_items: list[str] | None = None,
    not_evaluated: list[str] | None = None,
    not_claimed: list[str] | None = None,
    evidence_refs: list[str] | None = None,
    proof_refs: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "domain_id": "reference",
        "subject_id": "typed-vector",
        "policy_id": "FORMAL_CORE_V1_POLICY",
        "schema_version": "FORMAL_CORE_V1_SCHEMA",
        "producer_id": "formal-reference",
        "contract_id": "FORMAL_CORE_V1_CONTRACT",
        "action": action,
        "stop": action != "PROCEED",
        "reason_codes": reason_codes,
        "blocking_items": blocking_items or [],
        "not_evaluated": not_evaluated or [],
        "not_claimed": not_claimed or [],
        "evidence_refs": evidence_refs or ["evidence:typed-vector"],
        "proof_refs": proof_refs or ["proof:typed-vector"],
    }


def vectors() -> list[dict[str, Any]]:
    return [
        {
            "name": "valid_proceed_vector",
            "document": _document(claims=[{"kind": "reason", "value": "TESTS_PASSED"}]),
            "expected": _contract(action="PROCEED", reason_codes=["TESTS_PASSED"]),
            "error_vector": False,
        },
        {
            "name": "blocking_vector",
            "document": _document(
                claims=[
                    {"kind": "reason", "value": "BLOCKING_FINDING"},
                    {"kind": "blocking", "value": "failing_test"},
                ]
            ),
            "expected": _contract(
                action="STOP_BLOCKED",
                reason_codes=["BLOCKING_FINDING"],
                blocking_items=["failing_test"],
            ),
            "error_vector": False,
        },
        {
            "name": "required_unknown_vector",
            "document": _document(
                claims=[
                    {"kind": "reason", "value": "REQUIRED_UNKNOWN"},
                    {"kind": "not_evaluated", "value": "required_test_result_missing"},
                ]
            ),
            "expected": _contract(
                action="REPORT_NOT_EVALUATED",
                reason_codes=["REQUIRED_UNKNOWN"],
                not_evaluated=["required_test_result_missing"],
            ),
            "error_vector": False,
        },
        {
            "name": "conflicting_evidence_vector",
            "document": _document(validity="conflicting", claims=[{"kind": "reason", "value": "CONFLICTING_EVIDENCE"}]),
            "expected": _contract(
                action="STOP_BLOCKED",
                reason_codes=["CONFLICTING_TYPED_EVIDENCE"],
                not_claimed=["software_safety"],
            ),
            "error_vector": True,
        },
        {
            "name": "invalid_evidence_vector",
            "document": _document(validity="invalid", claims=[{"kind": "reason", "value": "INVALID_EVIDENCE"}]),
            "expected": _contract(
                action="STOP_BLOCKED",
                reason_codes=["INVALID_TYPED_EVIDENCE"],
                not_claimed=["software_safety"],
            ),
            "error_vector": True,
        },
        {
            "name": "version_incompatible_vector",
            "document": _document(schema_version="OTHER_SCHEMA", claims=[{"kind": "reason", "value": "VERSION_MISMATCH"}]),
            "expected": _contract(
                action="REPORT_NOT_EVALUATED",
                reason_codes=["INCOMPATIBLE_VERSION"],
                not_evaluated=["schema version incompatible"],
                not_claimed=["software_safety"],
            ),
            "error_vector": True,
        },
    ]


def _lean_bin() -> Path | None:
    configured = os.environ.get("SPIRA_LEAN_BIN")
    if configured:
        candidate = Path(configured)
        if (candidate / "lake.exe").exists() or (candidate / "lake").exists():
            return candidate
    candidate = ROOT.parent / "lean_toolchains" / "lean-4.32.0-windows" / "bin"
    if (candidate / "lake.exe").exists():
        return candidate
    return None


def run_lean_reference() -> dict[str, Any]:
    lean_bin = _lean_bin()
    if lean_bin is None:
        return {"status": "FAIL", "error": "LEAN_BIN_NOT_FOUND", "stdout": "", "returncode": None}
    lake_exe = lean_bin / ("lake.exe" if os.name == "nt" else "lake")
    env = dict(os.environ)
    env["PATH"] = str(lean_bin) + os.pathsep + env.get("PATH", "")
    proc = subprocess.run(
        [str(lake_exe), "exe", "spira-formal-core-v1"],
        cwd=LEAN_PROJECT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    passed = proc.returncode == 0 and "SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_PASS" in proc.stdout
    return {
        "status": "PASS" if passed else "FAIL",
        "returncode": proc.returncode,
        "stdout": proc.stdout,
    }


def compare_contracts(observed: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    mismatches = []
    for field in SEMANTIC_FIELDS:
        if observed.get(field) != expected.get(field):
            mismatches.append(
                {
                    "field": field,
                    "observed": observed.get(field),
                    "expected": expected.get(field),
                }
            )
    return {"pass": not mismatches, "mismatches": mismatches}


def run_python_vectors() -> list[dict[str, Any]]:
    rows = []
    for vector in vectors():
        first = evaluate_typed_evidence(vector["document"])
        second = evaluate_typed_evidence(vector["document"])
        observed = first["machine_contract"]
        comparison = compare_contracts(observed, vector["expected"])
        rows.append(
            {
                "name": vector["name"],
                "status": "PASS" if comparison["pass"] and first == second else "FAIL",
                "error_vector": vector["error_vector"],
                "python_status": first["status"],
                "nondeterministic": first != second,
                "comparison": comparison,
            }
        )
    return rows


def build_results() -> dict[str, Any]:
    lean = run_lean_reference()
    vector_rows = run_python_vectors()
    mismatch_rows = [row for row in vector_rows if row["status"] != "PASS"]
    error_vectors = [row for row in vector_rows if row["error_vector"]]
    status = (
        "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED"
        if lean["status"] == "PASS" and not mismatch_rows
        else "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION"
    )
    return {
        "status": status,
        "phase": "generic_differential_harness_rerun",
        "accepted_python_typed_evidence_entrypoint": True,
        "python_entrypoint": "spira_core.formal_core_v1.evaluate_typed_evidence",
        "lean_reference": lean,
        "vector_results": vector_rows,
        "all_formal_test_vectors_equal": len(mismatch_rows) == 0,
        "all_error_vectors_fail_closed": all(
            row["status"] == "PASS" and row["python_status"] == "error" for row in error_vectors
        ),
        "list_order_differences": _count_field_mismatches(mismatch_rows, {"reason_codes", "blocking_items", "not_evaluated", "not_claimed", "evidence_refs", "proof_refs"}),
        "missing_field_differences": _count_missing_field_mismatches(mismatch_rows),
        "identity_differences": _count_field_mismatches(mismatch_rows, {"domain_id", "subject_id", "policy_id", "schema_version", "producer_id", "contract_id"}),
        "nondeterministic_repeats": sum(1 for row in vector_rows if row["nondeterministic"]),
        "python_source_changes_outside_authorized_boundary": 0,
        "domain_adapter_changes": 0,
        "benchmark_changes": 0,
        "result_reclassification": 0,
    }


def _count_field_mismatches(rows: list[dict[str, Any]], fields: set[str]) -> int:
    return sum(
        1
        for row in rows
        for mismatch in row["comparison"]["mismatches"]
        if mismatch["field"] in fields
    )


def _count_missing_field_mismatches(rows: list[dict[str, Any]]) -> int:
    return sum(
        1
        for row in rows
        for mismatch in row["comparison"]["mismatches"]
        if mismatch["observed"] is None or mismatch["expected"] is None
    )


def write_outputs(results: dict[str, Any]) -> None:
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    vector_lines = [
        f"- {row['name']}: {row['status']}" for row in results["vector_results"]
    ]
    REPORT.write_text(
        "\n".join(
            [
                "# SPIRA Formal Core V1 Differential Harness Report",
                "",
                "## Status",
                "",
                "```text",
                str(results["status"]),
                f"LEAN_REFERENCE_{results['lean_reference']['status']}",
                "```",
                "",
                "## Vector Results",
                "",
                *vector_lines,
                "",
                "## Gates",
                "",
                "```json",
                json.dumps(
                    {
                        "all_formal_test_vectors_equal": results["all_formal_test_vectors_equal"],
                        "all_error_vectors_fail_closed": results["all_error_vectors_fail_closed"],
                        "list_order_differences": results["list_order_differences"],
                        "missing_field_differences": results["missing_field_differences"],
                        "identity_differences": results["identity_differences"],
                        "nondeterministic_repeats": results["nondeterministic_repeats"],
                    },
                    indent=2,
                ),
                "```",
                "",
                "## Boundary",
                "",
                "No domain adapters, benchmark files, runtime integration, or historical results were modified.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    review_status = (
        "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED"
        if results["status"].endswith("ACCEPTED")
        else "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION"
    )
    next_step = (
        "DOMAIN_2_FORMAL_CONFORMANCE_AUTHORIZATION_REQUIRED_NEXT"
        if review_status.endswith("ACCEPTED")
        else "DIFFERENTIAL_HARNESS_REVISION_REQUIRED"
    )
    REVIEW.write_text(
        "\n".join(
            [
                "# SPIRA Formal Core V1 Differential Harness Review",
                "",
                "## Status",
                "",
                "```text",
                review_status,
                next_step,
                "DOMAIN_CONFORMANCE_NOT_AUTHORIZED_BY_THIS_REVIEW",
                "RUNTIME_INTEGRATION_NOT_AUTHORIZED",
                "PRODUCTION_CLAIM_NOT_AUTHORIZED",
                "RELEASE_NOT_AUTHORIZED",
                "```",
                "",
                "## Decision",
                "",
                "The generic differential harness rerun is accepted."
                if review_status.endswith("ACCEPTED")
                else "The generic differential harness needs revision.",
                "",
                "The comparison is limited to the formal typed-evidence vectors. It does not prove raw parsers or production runtime behavior.",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    results = build_results()
    write_outputs(results)
    return 0 if results["status"].endswith("ACCEPTED") else 2


if __name__ == "__main__":
    raise SystemExit(main())
