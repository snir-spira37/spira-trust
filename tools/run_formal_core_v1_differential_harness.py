from __future__ import annotations

import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
RESEARCH = ROOT / "research" / "formal_core"
RESULTS = RESEARCH / "spira_formal_core_v1_differential_harness_results.json"
REPORT = RESEARCH / "spira_formal_core_v1_differential_harness_report.md"
REVIEW = RESEARCH / "spira_formal_core_v1_differential_harness_review.md"


EXPECTED_ENTRYPOINTS = [
    "source/spira_core/formal_core_v1.py",
    "source/spira_core/formal_core.py",
]

KNOWN_DOMAIN_SPECIFIC_CANDIDATES = [
    "source/spira_core/mvp_unified.py",
    "source/spira_core/test_build_failure_producer.py",
    "source/spira_core/terraform_plan_producer.py",
    "source/spira_core/agent_summary.py",
]


def _rel_exists(path: str) -> bool:
    return (ROOT / path).exists()


def build_results() -> dict[str, Any]:
    accepted_entrypoints = [path for path in EXPECTED_ENTRYPOINTS if _rel_exists(path)]
    domain_specific_candidates = [path for path in KNOWN_DOMAIN_SPECIFIC_CANDIDATES if _rel_exists(path)]
    status = (
        "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED"
        if accepted_entrypoints
        else "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION"
    )
    blocker = None if accepted_entrypoints else "PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED"
    return {
        "status": status,
        "phase": "generic_differential_harness",
        "accepted_python_typed_evidence_entrypoint": bool(accepted_entrypoints),
        "accepted_entrypoints": accepted_entrypoints,
        "domain_specific_candidates_not_accepted_as_generic_entrypoint": domain_specific_candidates,
        "blocker": blocker,
        "lean_reference_available": _rel_exists("formal/spira_formal_core_v1/SpiraFormalCore/Reference.lean"),
        "formal_vectors_available": _rel_exists("formal/spira_formal_core_v1/SpiraFormalCore/TestVectors.lean"),
        "comparison_executed": False,
        "comparison_executed_reason": "blocked before comparison because no accepted Python typed-evidence entrypoint exists"
        if blocker
        else "accepted entrypoint available",
        "python_source_changes": 0,
        "domain_adapter_changes": 0,
        "benchmark_changes": 0,
        "result_reclassification": 0,
    }


def write_outputs(results: dict[str, Any]) -> None:
    RESULTS.write_text(json.dumps(results, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    REPORT.write_text(
        "\n".join(
            [
                "# SPIRA Formal Core V1 Differential Harness Report",
                "",
                "## Status",
                "",
                "```text",
                str(results["status"]),
                str(results["blocker"] or "NO_BLOCKER"),
                "```",
                "",
                "## Result",
                "",
                "The generic differential comparison did not execute.",
                "",
                "Reason:",
                "",
                "```text",
                str(results["comparison_executed_reason"]),
                "```",
                "",
                "## Discovery",
                "",
                "Accepted Python typed-evidence entrypoints:",
                "",
                "```json",
                json.dumps(results["accepted_entrypoints"], indent=2),
                "```",
                "",
                "Domain-specific candidates observed but not accepted as generic typed-evidence entrypoints:",
                "",
                "```json",
                json.dumps(
                    results["domain_specific_candidates_not_accepted_as_generic_entrypoint"],
                    indent=2,
                ),
                "```",
                "",
                "## Boundary",
                "",
                "No Python source, domain adapter, benchmark, corpus, oracle, or historical result was modified.",
                "",
            ]
        ),
        encoding="utf-8",
    )
    REVIEW.write_text(
        "\n".join(
            [
                "# SPIRA Formal Core V1 Differential Harness Review",
                "",
                "## Status",
                "",
                "```text",
                str(results["status"]),
                str(results["blocker"] or "NO_BLOCKER"),
                "DOMAIN_CONFORMANCE_NOT_AUTHORIZED",
                "RUNTIME_INTEGRATION_NOT_AUTHORIZED",
                "PRODUCTION_CLAIM_NOT_AUTHORIZED",
                "RELEASE_NOT_AUTHORIZED",
                "```",
                "",
                "## Decision",
                "",
                "The differential harness phase needs revision before semantic comparison can run.",
                "",
                "The Lean executable reference exists, but the repository does not yet expose an accepted Python",
                "typed-evidence entrypoint matching the Formal Core V1 protocol.",
                "",
                "Creating a new Python decision core inside this phase would violate the protocol. The correct",
                "next step is a separate authorization to define or expose a Python typed-evidence boundary,",
                "or to amend the differential harness scope.",
                "",
                "## Preserved Boundaries",
                "",
                "```text",
                "Python source changes: 0",
                "domain adapter changes: 0",
                "benchmark changes: 0",
                "result reclassification: 0",
                "```",
                "",
                "## Required Next Step",
                "",
                "```text",
                "SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_AUTHORIZATION_REQUIRED",
                "```",
                "",
            ]
        ),
        encoding="utf-8",
    )


def main() -> int:
    results = build_results()
    write_outputs(results)
    return 0 if results["accepted_python_typed_evidence_entrypoint"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
