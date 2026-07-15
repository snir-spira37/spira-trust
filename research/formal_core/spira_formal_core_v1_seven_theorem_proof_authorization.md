# SPIRA Formal Core V1 Seven-Theorem Proof Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_SEVEN_THEOREM_PROOF_AUTHORIZED

PROOF_PHASE_ONLY

LEAN_TOOLCHAIN_FROZEN

LAKE_PROJECT_FROZEN

CORE_DEFINITIONS_FROZEN

ACCEPTED_THEOREM_STATEMENTS_FROZEN

TRUSTED_COMPUTING_BASE_LEDGER_FROZEN

SEVEN_THEOREM_FAMILIES_AUTHORIZED

AUXILIARY_LEMMAS_AUTHORIZED

AXIOM_INVENTORY_REQUIRED

PROOF_RESULTS_AUTHORIZED

PROOF_REPORT_AUTHORIZED

PROOF_REVIEW_REQUIRED

DEFINITION_CHANGES_NOT_AUTHORIZED

THEOREM_STATEMENT_WEAKENING_NOT_AUTHORIZED

PYTHON_CODE_CHANGES_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes machine-checked Lean proofs for the seven accepted
SPIRA Formal Core V1 theorem families.

It follows the accepted Lean definition phase:

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_ACCEPTED
```

This authorization does not permit changing the definitions to make proofs
easier. If a proof cannot be completed against the accepted definitions and
theorem obligations, the phase must stop with `NEEDS_REVISION`.

## 2. Frozen Baseline

```text
formal branch:
codex/formal-core-v1-lean

accepted definition commit:
a49c80f

Lean toolchain:
leanprover/lean4:v4.32.0

Lean version:
4.32.0

Lake version:
5.0.0-src+8c9756b
```

The accepted definition files under:

```text
formal/spira_formal_core_v1/SpiraFormalCore/
```

are frozen for this proof phase unless a separate amendment is created and
accepted.

## 3. Authorized Proof Files

This phase may create:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/Determinism.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/Blocking.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/NotEvaluated.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/ExplicitLists.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/GateA.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/ModelNonAuthority.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/FailClosed.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/All.lean
```

It may update:

```text
formal/spira_formal_core_v1/SpiraFormalCore.lean
```

only to import the authorized proof aggregation module.

Required research outputs:

```text
research/formal_core/spira_formal_core_v1_proof_inventory.json
research/formal_core/spira_formal_core_v1_machine_checked_proof_results.json
research/formal_core/spira_formal_core_v1_machine_checked_proof_report.md
research/formal_core/spira_formal_core_v1_machine_checked_proof_review.md
```

## 4. Authorized Theorem Families

### T1 - Determinism

For identical typed evidence and identical policy context:

```text
E1 = E2 and P1 = P2
->
core E1 P1 = core E2 P2
```

### T2 - Blocking evidence prevents PROCEED

If the derived blocking list is non-empty, the decided action is not
`PROCEED`.

```text
blockingItems.isEmpty = false
->
decideAction blockingItems notEvaluated != Action.PROCEED
```

### T3 - Required NOT_EVALUATED prevents silent PASS

If the derived not-evaluated list is non-empty and no blocking item takes
precedence, the decided action is not `PROCEED`.

```text
blockingItems.isEmpty = true
and notEvaluated.isEmpty = false
->
decideAction blockingItems notEvaluated != Action.PROCEED
```

### T4 - Explicit contractual lists are preserved

`assembleContract` preserves the explicit lists it receives:

```text
reasonCodes
blockingItems
notEvaluated
notClaimed
evidenceRefs
proofRefs
```

### T5 - Gate A preserves the complete domain contract

```text
projectDomainContract (gateAWrap C) = C
```

### T6 - Model and presentation fields have zero decision authority

```text
executedAction machineContract modelExplanation = machineContract.action
```

and the passthrough envelope preserves the machine contract action.

### T7 - Invalid/internal/validation errors fail closed

For every `CoreError`, the fail-closed action is not `PROCEED`.

```text
failClosedAction error != Action.PROCEED
```

The proof may also show that assembled fail-closed contracts have:

```text
stop = true
```

## 5. Proof Hygiene

The proof phase must contain:

```text
no sorry
no admit
no custom axiom
no sorryAx
no opaque used to hide an unproved obligation
no unsafe decision core
```

Theorem statements must not be weakened to obtain a pass.

Auxiliary lemmas are allowed only when they preserve the accepted theorem
obligations.

## 6. Axiom Inventory

For every final theorem, the report must record:

```text
#print axioms theoremName
```

The accepted result must contain no:

```text
sorryAx
custom axiom
unreviewed imported axiom
```

Any built-in logical axioms reported by Lean must be listed in the proof
inventory and reconciled with the trusted computing base ledger.

## 7. Acceptance Gates

This phase can be accepted only if:

```text
seven theorem families proved: 7 / 7

lake build: PASS

proof files with sorry/admit: 0

custom axioms: 0

unapproved axioms: 0

definition drift: 0

theorem-statement drift: 0

Python changes: 0

domain adapter changes: 0
```

Required accepted status:

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED
```

## 8. Stop Conditions

Stop immediately if:

```text
a theorem cannot be proved as stated

a definition change is required

an accepted theorem obligation must be weakened

an unapproved axiom is required

sorry/admit would be required

the TCB ledger must expand without amendment

Python behavior must be changed
```

## 9. Non-Authorization

This document does not authorize:

```text
Python/Lean equivalence protocol

executable reference vectors

Domain 2 conformance

Domain 3 conformance

Domain 1 conformance

runtime integration

benchmark execution

merge to main

release/version/tag/PyPI
```
