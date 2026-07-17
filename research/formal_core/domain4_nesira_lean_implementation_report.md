# SPIRA Domain 4 / Nesira Lean Implementation Report

## Summary

```text
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_ACCEPTED
```

Domain 4 / Nesira has been translated into the existing
`formal/spira_formal_core_v1` Lean package as a faithful Lean-only
implementation of the accepted paper chain:

```text
flag schema V2
decision table V2
conformance harness V2 specification boundary
NOT_PROVEN ledger
```

No Python, fixtures, harness implementation, Phase 2 trust layer, product
integration, public claim, or release behavior was implemented.

## Files Changed

Created:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Meta.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Proofs.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Main.lean
research/formal_core/domain4_nesira_lean_implementation_results.json
research/formal_core/domain4_nesira_lean_implementation_report.md
research/formal_core/domain4_nesira_lean_implementation_review.md
```

Updated only for imports:

```text
formal/spira_formal_core_v1/SpiraFormalCore.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/All.lean
```

## What Was Implemented

The Lean implementation defines:

```text
ExecutionMeta
ArtifactKind
9 V2 outcome enum types
OutcomeTuple
Policy
Phase1Action without PROCEED
ValidationStatus
MachineContract
status/action projection
NesiraCoreV2
Domain4 theorem families
Domain4 dump over the finite core space
```

The finite core-space size is:

```text
2 artifact kinds * 3 execution meta values * 3^9 outcome tuples = 118098
```

The Lean dump count was evaluated:

```text
actualDumpLineCount: 118098
expectedDumpLineCount: 118098
```

An independent local checker compared the Lean dump against the frozen
decision-table V2 ordering:

```text
dump rows checked: 118098
dump/spec disagreements: 0
```

## Proof Results

Required theorem families:

```text
tool_error_stops: PROVED
input_malformed_rerun: PROVED
schema_structural_violation_not_valid: PROVED
hash_mismatch_not_valid: PROVED_WITH_PRECEDENCE_PRECONDITIONS
unsafe_path_not_valid: PROVED_WITH_PRECEDENCE_PRECONDITIONS
missing_evidence_not_evaluated: PROVED_WITH_PRECEDENCE_PRECONDITIONS
context_expected_missing_not_evaluated: PROVED_WITH_PRECEDENCE_PRECONDITIONS
phase1_no_proceed: TYPE_LEVEL_PROVED_BY_ABSENCE_OF_CONSTRUCTOR
core_deterministic: PROVED
stop_true: PROVED
```

The row theorems that target later evidence checks include the required
precedence preconditions. This is necessary because the first-match table may
stop before hash/evidence checks if schema, context, or path outcomes fail
first.

## Build And Hygiene

Command:

```text
lake build
```

Result:

```text
returncode: 0
jobs: 41
status: PASS
```

Proof hygiene scan over the Formal Core Lean package:

```text
sorry: 0
admit: 0
custom axiom: 0
sorryAx: 0
native_decide: 0
unsafe: 0
opaque: 0
implemented_by: 0
extern: 0
```

## Axiom Inventory

`#print axioms` results:

```text
tool_error_stops: [propext]
input_malformed_rerun: [propext]
schema_structural_violation_not_valid: [propext]
hash_mismatch_not_valid: [propext]
unsafe_path_not_valid: [propext]
missing_evidence_not_evaluated: [propext]
context_expected_missing_not_evaluated: [propext]
core_deterministic: []
stop_true: [propext]
```

No `sorryAx`, custom axiom, or unapproved axiom was found.

## Regression

The existing Formal Core package still builds:

```text
Domain 1: PASS
Domain 2: PASS
Domain 3: PASS
generic core proofs: PASS
```

This is evidenced by the successful full `lake build` of the existing package
with Domain4 imported.

## Boundary

Still not implemented or claimed:

```text
Python raw -> enum classifier
PythonCore
Python/Lean exhaustive conformance harness
fixtures or mutation pairs
reason-code fidelity harness
Phase 2 signer trust
signer authority
actual isolation execution
permission to sever
combined verdict integration
CLI / wheel exposure
public capability claim
release
```

## Next Step

The next stage requires a separate authorization:

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_AUTHORIZATION_REQUIRED
```

That later stage should implement PythonCore / classifier / fixtures / harness
and run the full 118098-tuple PythonCore == LeanCore agreement plus mutation
pairs and reason-code fidelity.
