# SPIRA Terraform Agent Action Gate Public Demo

## What SPIRA Does

SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.

## What This Demo Shows

This package shows the current Domain 3 Terraform Plan path only. It demonstrates how existing Terraform plan JSON fixtures are converted into typed evidence and then into a machine-readable SPIRA contract.

The three demonstrated outcomes are:

- `STOP_BLOCKED`
- `REPORT_NOT_EVALUATED`
- `RERUN_REQUIRED`

## Audience

This package is for external technical reviewers, platform engineers, AI-agent infrastructure teams, security engineers, and infrastructure owners who want to inspect the current evidence-to-contract behavior without knowing the full project history.

## Prerequisites

- Python 3.12+
- A repository checkout pinned to `19c0e996a79187c444bcbba76f3f4a907e003ae1` or a later package-build commit that preserves the same demo artifacts
- `pytest` installed for the optional Python test checks
- Lean/Lake only if the reviewer wants to independently run the formal package. Lean reproduction may be reported as PASS only when the reviewer actually runs `lake build` successfully in their own environment.

## How To Run

Use the existing Domain 3 research/conformance harness from the repository root:

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

There is no existing public command named `spira evaluate ...` in this demo.

Full reproduction steps are in `REPRODUCE_DEMO.md`.

## Result Interpretation

- `STOP_BLOCKED`: supported evidence shows a resource change that requires review.
- `REPORT_NOT_EVALUATED`: required evidence is incomplete, so SPIRA does not silently treat it as pass.
- `RERUN_REQUIRED`: invalid Terraform plan JSON must be regenerated; invalid JSON must not receive a soft PASS.

## What Is Proved And What Is Empirical

The formal core has Lean proofs for bounded decision properties, including that blockers and required non-evaluation do not become `PROCEED` inside the formal model, and that model explanation fields do not own the machine action.

This demo empirically reproduces the three Domain 3 Terraform Plan paths, focused Python tests, full Python tests, and package integrity checks. It does not claim end-to-end mathematical proof of Terraform parsing or all adapters.

## Formal Package Lean Reproduction

The builder later reproduced the formal package locally with Lean 4.32.0 / Lake 5.0.0 and `lake build` completed successfully. This is builder-side evidence only, not independent external certification.

External reviewers should independently run `lake build` before marking Lean reproduction as PASS. If Lean/Lake are unavailable in the review environment, record `NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT`.

## What SPIRA Does Not Claim Here

SPIRA currently gates supported artifact-backed actions. SPIRA does not yet gate arbitrary tool calls, arbitrary MCP actions, arbitrary database/API operations, or universal runtime agent behavior.

SPIRA is not a replacement for OPA, Sentinel, HCP Terraform, Spacelift, IAM, or MCP gateways.

## Full Review Instructions

See `COLD_DEMO_REVIEW_TASK.md` for the cold-review checklist and `CLAIMS_AND_BOUNDARIES.md` for exact public claim boundaries.
