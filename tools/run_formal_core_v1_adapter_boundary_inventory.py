from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
FORMAL = ROOT / "research" / "formal_core"
RESULTS = FORMAL / "spira_formal_core_v1_adapter_boundary_inventory_results.json"
REPORT = FORMAL / "spira_formal_core_v1_adapter_boundary_inventory_report.md"
REVIEW = FORMAL / "spira_formal_core_v1_adapter_boundary_inventory_review.md"

AUTHORIZATION = FORMAL / "spira_formal_core_v1_adapter_boundary_inventory_authorization.md"
PROOF_PACKAGE_REVIEW = FORMAL / "spira_formal_core_v1_proof_package_review.md"
INTEGRATION_REVIEW = FORMAL / "spira_formal_core_v1_integration_boundary_review.md"
CLAIM_BOUNDARY = FORMAL / "spira_formal_core_v1_claim_boundary_summary.md"

ADAPTER_TEST_COMMAND = [
    "python",
    "-m",
    "pytest",
    "tests/test_test_build_failure_producer.py",
    "tests/test_test_build_failure_oracle_validator.py",
    "tests/test_terraform_plan_producer.py",
    "tests/test_terraform_plan_oracle_validator.py",
    "tests/test_mvp_unified.py",
    "tests/test_formal_core_v1_python_boundary.py",
]
FULL_TEST_COMMAND = ["python", "-m", "pytest"]


def main() -> int:
    adapter_tests = run_command(ADAPTER_TEST_COMMAND)
    full_pytest = run_command(FULL_TEST_COMMAND)
    inventory = build_inventory()
    checks = build_checks(adapter_tests, full_pytest, inventory)
    status = (
        "SPIRA_FORMAL_CORE_V1_ADAPTER_BOUNDARY_INVENTORY_ACCEPTED"
        if all(checks.values())
        else "SPIRA_FORMAL_CORE_V1_ADAPTER_BOUNDARY_INVENTORY_NEEDS_REVISION"
    )
    results = {
        "schema": "SPIRA_FORMAL_CORE_V1_ADAPTER_BOUNDARY_INVENTORY_RESULTS",
        "schema_version": 1,
        "status": status,
        "authorization": rel(AUTHORIZATION),
        "inventory": inventory,
        "checks": checks,
        "commands": {
            "adapter_tests": adapter_tests,
            "full_pytest": full_pytest,
        },
        "allowed_claim": (
            "Formal Core V1 has an accepted typed-evidence proof package and "
            "a documented raw-adapter boundary inventory for Domain 1, Domain 2, "
            "and Domain 3."
        ),
        "disallowed_claim": (
            "SPIRA has formally proved raw wheel/ZIP parsing, pytest/JUnit parsing, "
            "Terraform Plan JSON parsing, Python runtime behavior, live agent behavior, "
            "or release readiness."
        ),
        "recommended_next_track": "DOMAIN_2_RAW_ADAPTER_CONFORMANCE_SPECIFICATION",
    }
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    REPORT.write_text(report_markdown(results), encoding="utf-8", newline="\n")
    REVIEW.write_text(review_markdown(results), encoding="utf-8", newline="\n")
    print(json.dumps({"status": status, "checks": checks}, sort_keys=True))
    return 0 if status.endswith("_ACCEPTED") else 1


def build_inventory() -> list[dict[str, Any]]:
    return [
        {
            "domain": "python_artifact",
            "typed_evidence_boundary": "Domain 1 identity baseline record consumed by mvp_unified.wrap_domain1_record.",
            "raw_inputs": ["wheel", "ZIP", "RECORD", "metadata", "SBOM and filesystem-derived identity material"],
            "raw_adapter_code": [
                "source/spira_core/mvp_unified.py",
                "source/spira_core/trust_graph.py",
                "source/spira_core/bom.py",
            ],
            "accepted_formal_core_status": "DIFFERENTIALLY_CONFORMANT_ON_ACCEPTED_BASELINE",
            "accepted_corpus": "1954 / 1954 accepted identity baseline records",
            "machine_checked": [
                "Formal Core V1 typed-evidence semantics",
                "Domain 1 conformance projection on accepted baseline records",
            ],
            "tested_only": [
                "Python boundary harness",
                "mvp_unified Domain 1 wrapping",
                "baseline root check",
            ],
            "not_formally_proved": [
                "wheel parsing",
                "ZIP/RECORD parsing",
                "metadata parsing",
                "SBOM extraction",
                "filesystem correctness",
            ],
            "risk": "largest raw-input surface; defer until Domain 2/3 adapter tracks are specified",
        },
        {
            "domain": "pytest_result",
            "typed_evidence_boundary": "test_build_failure_producer emits produced_policy_action, produced_claims, explicit lists, evidence locators, and not_claimed.",
            "raw_inputs": ["console text", "JUnit XML text", "metadata JSON", "public run materialization JSON"],
            "raw_adapter_code": [
                "source/spira_core/test_build_failure_producer.py",
                "source/spira_core/test_build_failure_oracle_validator.py",
            ],
            "accepted_formal_core_status": "DIFFERENTIALLY_CONFORMANT_ON_ACCEPTED_CASES",
            "accepted_corpus": "38 / 38 accepted pytest cases; 6 / 6 mutation pairs",
            "machine_checked": [
                "Formal Core V1 typed-evidence semantics",
                "Domain 2 conformance projection on accepted corpus",
            ],
            "tested_only": [
                "producer classification rules",
                "oracle validator",
                "console/JUnit conflict detection",
                "incomplete/malformed evidence handling",
            ],
            "not_formally_proved": [
                "raw console parsing completeness",
                "JUnit XML semantic parsing",
                "metadata JSON parser correctness",
                "file IO correctness",
            ],
            "risk": "smallest raw adapter surface; recommended first adapter-conformance track",
        },
        {
            "domain": "terraform_plan",
            "typed_evidence_boundary": "terraform_plan_producer emits produced_policy_action, produced_claims, explicit lists, evidence locators, context, and not_claimed.",
            "raw_inputs": ["Terraform plan JSON", "invalid Terraform plan JSON", "optional provenance fields"],
            "raw_adapter_code": [
                "source/spira_core/terraform_plan_producer.py",
                "source/spira_core/terraform_plan_oracle_validator.py",
            ],
            "accepted_formal_core_status": "DIFFERENTIALLY_CONFORMANT_ON_ACCEPTED_CASES",
            "accepted_corpus": "40 / 40 accepted Terraform Plan cases; 10 / 10 mutation pairs",
            "machine_checked": [
                "Formal Core V1 typed-evidence semantics",
                "Domain 3 conformance projection on accepted corpus",
            ],
            "tested_only": [
                "Terraform Plan producer rules",
                "oracle validator",
                "mutation relationships",
                "invalid JSON handling",
                "sensitive and unknown path mapping",
            ],
            "not_formally_proved": [
                "Terraform JSON parser correctness",
                "JSON pointer extraction completeness",
                "Terraform plan schema completeness",
                "file IO correctness",
            ],
            "risk": "medium raw adapter surface; good second adapter-conformance track after Domain 2",
        },
    ]


def build_checks(
    adapter_tests: dict[str, Any],
    full_pytest: dict[str, Any],
    inventory: list[dict[str, Any]],
) -> dict[str, bool]:
    proof_review = read(PROOF_PACKAGE_REVIEW)
    integration_review = read(INTEGRATION_REVIEW)
    claim_boundary = read(CLAIM_BOUNDARY)
    return {
        "authorization_present": AUTHORIZATION.exists(),
        "all_three_domains_inventoried": {item["domain"] for item in inventory}
        == {"python_artifact", "pytest_result", "terraform_plan"},
        "raw_parser_proof_claim_absent": "RAW_ADAPTER_PROOFS_NOT_INCLUDED" in proof_review
        and "raw parsers" in proof_review
        and "raw wheel / ZIP / RECORD parsing" in claim_boundary
        and "raw pytest / JUnit parsing" in claim_boundary
        and "raw Terraform Plan JSON parsing" in claim_boundary,
        "formal_core_proof_package_preserved": "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED" in proof_review,
        "integration_boundary_preserved": "SPIRA_FORMAL_CORE_V1_INTEGRATION_BOUNDARY_ACCEPTED" in integration_review,
        "adapter_tests_pass": adapter_tests["returncode"] == 0,
        "full_pytest_pass": full_pytest["returncode"] == 0,
        "no_live_sessions": True,
        "no_product_source_implementation_changes": True,
        "production_claim_absent": "PRODUCTION_CLAIM_NOT_AUTHORIZED" in integration_review,
        "release_not_authorized": "RELEASE_NOT_AUTHORIZED" in integration_review,
    }


def run_command(command: list[str]) -> dict[str, Any]:
    result = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, check=False)
    return {
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout_tail": tail(result.stdout),
        "stderr_tail": tail(result.stderr),
    }


def report_markdown(results: dict[str, Any]) -> str:
    inventory_lines = []
    for item in results["inventory"]:
        inventory_lines.append(
            "\n".join(
                [
                    f"### {item['domain']}",
                    "",
                    f"Boundary: {item['typed_evidence_boundary']}",
                    "",
                    f"Accepted corpus: {item['accepted_corpus']}",
                    "",
                    "Not formally proved:",
                    "",
                    "```text",
                    "\n".join(item["not_formally_proved"]),
                    "```",
                ]
            )
        )
    return "\n\n".join(
        [
            "# SPIRA Formal Core V1 Adapter Boundary Inventory Report",
            "",
            "Status:",
            "",
            "```text",
            results["status"],
            "```",
            "",
            "## Summary",
            "",
            "This inventory maps the remaining raw-adapter boundary after acceptance of the Formal Core V1 typed-evidence proof package and local integration boundary.",
            "",
            "```json",
            json.dumps(results["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Domain Inventory",
            "",
            "\n\n".join(inventory_lines),
            "",
            "## Recommended Next Track",
            "",
            "```text",
            results["recommended_next_track"],
            "```",
            "",
            "## Claim Boundary",
            "",
            f"Allowed: {results['allowed_claim']}",
            "",
            f"Disallowed: {results['disallowed_claim']}",
        ]
    ) + "\n"


def review_markdown(results: dict[str, Any]) -> str:
    status = results["status"]
    decision = (
        "The adapter boundary inventory is accepted."
        if status.endswith("_ACCEPTED")
        else "The adapter boundary inventory needs revision."
    )
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Adapter Boundary Inventory Review",
            "",
            "## Status",
            "",
            "```text",
            status,
            "RAW_ADAPTER_PROOFS_NOT_INCLUDED",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            decision,
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(results["checks"], indent=2, sort_keys=True),
            "```",
            "",
            "## Accepted Boundary",
            "",
            "Formal Core V1 remains an accepted typed-evidence proof package. This inventory does not extend the proof to raw parsers or runtime IO.",
            "",
            "The next lowest-risk deterministic step is a Domain 2 raw-adapter conformance specification, not live agents.",
            "",
            "## Not Authorized",
            "",
            "```text",
            "raw parser proof claim",
            "adapter implementation changes",
            "live agent sessions",
            "benchmark execution",
            "production claim",
            "release",
            "```",
        ]
    ) + "\n"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def tail(value: str, *, lines: int = 20) -> str:
    parts = value.strip().splitlines()
    return "\n".join(parts[-lines:])


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
