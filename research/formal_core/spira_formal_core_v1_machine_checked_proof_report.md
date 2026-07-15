# SPIRA Formal Core V1 Machine-Checked Proof Report

## Status

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_COMPLETE

SEVEN_THEOREM_FAMILIES_PROVED_7_OF_7

LAKE_BUILD_PASS

NO_SORRY_ADMIT_OR_CUSTOM_AXIOM

NO_SORRYAX

APPROVED_BUILTIN_AXIOM_PROPEXT_RECORDED

DEFINITION_DRIFT_0

THEOREM_STATEMENT_DRIFT_0

PYTHON_CHANGES_0

DOMAIN_ADAPTER_CHANGES_0
```

## 1. Scope

This report covers only the seven-theorem proof phase authorized by:

```text
research/formal_core/spira_formal_core_v1_seven_theorem_proof_authorization.md
```

It does not cover:

```text
Python/Lean equivalence
Domain 1/2/3 conformance
executable reference vectors
runtime integration
production claims
release
```

## 2. Proof Files

```text
SpiraFormalCore/Proofs/Determinism.lean
SpiraFormalCore/Proofs/Blocking.lean
SpiraFormalCore/Proofs/NotEvaluated.lean
SpiraFormalCore/Proofs/ExplicitLists.lean
SpiraFormalCore/Proofs/GateA.lean
SpiraFormalCore/Proofs/ModelNonAuthority.lean
SpiraFormalCore/Proofs/FailClosed.lean
SpiraFormalCore/Proofs/All.lean
```

## 3. Theorem Families

```text
T1 Determinism:
PASS

T2 Blocking evidence prevents PROCEED:
PASS

T3 Required NOT_EVALUATED prevents silent PASS:
PASS

T4 Explicit contractual lists are preserved:
PASS

T5 Gate A preserves the complete domain contract:
PASS

T6 Model and presentation fields have zero decision authority:
PASS

T7 Invalid/internal/validation errors fail closed:
PASS
```

## 4. Build Result

Command:

```text
lake build
```

Result:

```text
PASS
Build completed successfully (21 jobs).
```

## 5. Proof Hygiene

Forbidden-token scan over Lean source:

```text
rg -n "\b(sorry|admit|axiom|sorryAx|opaque|unsafe)\b" formal/spira_formal_core_v1 -g "*.lean"
```

Result:

```text
PASS
```

No `sorry`, `admit`, custom `axiom`, `sorryAx`, `opaque`, or `unsafe` token was
present in Lean source.

## 6. Axiom Inventory

The `#print axioms` inventory produced:

```text
no custom axioms
no sorryAx
```

Some proofs depend on Lean's built-in:

```text
propext
```

This is recorded as an approved built-in logical axiom for this phase.

The following theorems do not depend on any axioms:

```text
assembleContract_preserves_reasonCodes
assembleContract_preserves_blockingItems
assembleContract_preserves_notEvaluated
assembleContract_preserves_notClaimed
assembleContract_preserves_evidenceRefs
assembleContract_preserves_proofRefs
gateA_project_preserves_contract
executedAction_model_non_authority
passthrough_preserves_machine_action
```

The following theorems depend on approved built-in `propext`:

```text
core_extensional_determinism
blocking_decideAction_not_proceed
required_unknown_decideAction_not_proceed
failClosedAction_not_proceed
assembleFailClosedContract_stop_true
```

## 7. Non-Changes

This proof phase did not modify:

```text
Python code
Domain adapters
benchmark runners
historical benchmark results
corpora
oracles
```

The only definition-file update was importing the authorized proof aggregation
module from `SpiraFormalCore.lean`.

## 8. Result

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_READY_FOR_REVIEW
```

The next phase, if accepted, requires a separate executable reference
authorization.
