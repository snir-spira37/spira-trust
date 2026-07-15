# SPIRA Formal Core V2 End-to-End Theorem Plan

## Status

```text
SPIRA_FORMAL_CORE_V2_END_TO_END_THEOREM_PLAN_PROPOSED

MATHEMATICAL_STRENGTHENING_ONLY

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED
BENCHMARK_OR_AGENT_WORK_NOT_AUTHORIZED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

Formal Core V2 should convert the useful V1 helper-level executable specification into a stronger end-to-end theorem package over:

```text
core : TypedEvidence -> PolicyContext -> CoreResult
```

The goal is to prove the main SPIRA invariants directly about `core(e, p)`, not only about helper functions used by `core`.

## Non-Goals

This plan does not authorize:

```text
Lean definition changes
Lean proof scripts
Python implementation changes
domain adapter changes
parser proof claims
new benchmark sessions
production claims
release work
```

## V2 Theorem Targets

### 1. End-To-End Blocking Prevents PROCEED

Target shape:

```text
valid(e, p)
and blocking claim or policy blocker is present
->
(core e p).action != PROCEED
and (core e p).stop = true
and blocker is present in (core e p).contract.blockingItems
```

This closes the gap where V1 proves the property for `decideAction` but not directly for `core`.

### 2. End-To-End NOT_EVALUATED Prevents Silent PROCEED

Target shape:

```text
valid(e, p)
and required unknown/not-evaluated evidence is present
and no higher-priority blocking condition is present
->
(core e p).action = REPORT_NOT_EVALUATED
or (core e p).action != PROCEED
and the unknown item is present in (core e p).contract.notEvaluated
```

This is the highest-value theorem family because it formalizes that uncertainty is preserved as a first-class contract outcome.

### 3. End-To-End Explicit List Soundness

For each explicit list:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence references
proof references
```

prove:

```text
every emitted item is justified by typed evidence or policy
```

### 4. End-To-End Explicit List Completeness

For each required typed evidence or policy item, prove:

```text
every required item appears in the corresponding machine-contract list
```

This is the missing dual of the V1 preservation theorems.

### 5. Domain FormalAction Equals Core Path

For each domain wrapper, prove a Lean theorem connecting the domain-specific action function to the generic core:

```text
DomainN.formalAction evidence
=
(DomainN.evaluate evidence).action
```

or, if the domain wrapper intentionally bypasses `core`, make that bypass explicit and justify it.

Domain 2 is the first priority because the external mathematical review identified a duplicated decision path:

```text
evaluate evidence
formalAction evidence
```

### 6. Policy Either Drives Decisions Or Is Removed

For each `PolicyContext` field, Formal Core V2 must choose one of two paths:

```text
active:
the field participates in core semantics and has theorems

ledger-only:
the field is explicitly documented as identity/provenance only
```

Dead policy fields should not imply mathematical authority.

### 7. Non-Authority Of Model And Presentation Fields

Replace mostly structural non-authority claims with an end-to-end theorem shape:

```text
changing only model explanation, model self-report, presentation,
telemetry, or non-authoritative fields
does not change executed action, stop state, or machine contract identity
```

This is the mathematically stronger form of the passthrough architecture.

### 8. Fail-Closed Core Path

Prove not only that `failClosedAction error != PROCEED`, but that every validation/internal/parse-boundary error path through `core` returns:

```text
action != PROCEED
stop = true
fail-closed reason code preserved
```

## Suggested Order

```text
1. V2 theorem specification review
2. Policy-field authority classification
3. End-to-end core theorem authorization
4. Domain 2 action-path equivalence first
5. Blocking and NOT_EVALUATED end-to-end theorems
6. Explicit-list soundness/completeness
7. Domain 3 equivalence
8. Domain 1 equivalence
9. Updated proof inventory and reproduction package
10. New external mathematical review
```

## Acceptance Criteria For V2

V2 should not be accepted merely because all Lean files build.

Acceptance requires:

```text
end-to-end core theorems exist
helper-only theorem families are no longer the main claim
policy fields are active or explicitly ledger-only
domain formalAction/evaluate equivalence is proven or intentionally removed
derive-list soundness and completeness are covered
no sorry/admit/axiom/unsafe escape hatches
reproduction package passes from cold checkout or ZIP
```

## Expected Claim If V2 Succeeds

Only after these theorems exist should the project consider the stronger wording:

```text
SPIRA has a formally verified deterministic decision core over typed evidence,
with end-to-end proofs that blocking and unknown evidence cannot silently
produce PROCEED and that explicit contract lists are sound and complete with
respect to the formal typed-evidence and policy algebra.
```

Until then, the V1 wording remains bounded.

