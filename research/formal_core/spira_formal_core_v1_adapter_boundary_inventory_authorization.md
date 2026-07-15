# SPIRA Formal Core V1 Adapter Boundary Inventory Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_ADAPTER_BOUNDARY_INVENTORY_AUTHORIZED
```

## Purpose

This authorization opens an offline inventory of the raw-adapter boundary that remains outside the accepted Formal Core V1 proof package.

The goal is to identify, for each accepted domain, where raw input becomes typed evidence and what must be proven, tested, or kept trusted in later work.

## Scope

Authorized:

```text
EXISTING_CODE_AND_ARTIFACTS_ONLY
RAW_TO_TYPED_EVIDENCE_BOUNDARY_INVENTORY
DOMAIN_1_2_3_ADAPTER_RESPONSIBILITY_MAPPING
TRUSTED_TESTED_PROVEN_OUT_OF_SCOPE_CLASSIFICATION
EXISTING_ADAPTER_TEST_EXECUTION
FULL_PYTEST_EXECUTION
INVENTORY_RESULTS_REPORT_AND_REVIEW
```

Authorized files:

```text
tools/run_formal_core_v1_adapter_boundary_inventory.py
research/formal_core/spira_formal_core_v1_adapter_boundary_inventory_results.json
research/formal_core/spira_formal_core_v1_adapter_boundary_inventory_report.md
research/formal_core/spira_formal_core_v1_adapter_boundary_inventory_review.md
```

## Boundaries

Not authorized:

```text
RAW_PARSER_IMPLEMENTATION_CHANGE
DOMAIN_ADAPTER_IMPLEMENTATION_CHANGE
FORMAL_CORE_LEAN_CHANGE
PYTHON_CORE_SEMANTICS_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
NEW_LEAN_PROOFS
RAW_PARSER_PROOF_CLAIM
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
PRODUCTION_CLAIM
RELEASE
```

## Required Questions

The inventory must answer:

```text
1. What is the current typed-evidence boundary for each domain?
2. Which code reads or interprets raw input before the Formal Core boundary?
3. Which obligations are already machine-checked?
4. Which obligations are tested only?
5. Which obligations remain trusted or out of scope?
6. Which domain is the lowest-risk next adapter-conformance track?
7. What claim is allowed after this inventory?
8. What claim remains disallowed?
```

## Acceptance Gates

Acceptance requires:

```text
all three domains inventoried
raw parser proof claim absent
Formal Core proof package preserved
integration boundary preserved
existing adapter tests pass
full pytest pass
no product/source implementation changes
no live sessions
```

Successful completion may support only an adapter-boundary inventory claim. It must not upgrade the Formal Core V1 proof claim to include raw parser correctness.
