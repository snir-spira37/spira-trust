# SPIRA Formal Core V1 Theorem Specification

## Status

```text
SPIRA_FORMAL_CORE_V1_THEOREM_STATEMENTS_SPECIFIED

SPECIFICATION_ONLY

SEVEN_THEOREM_FAMILIES_PRESERVED

NO_LEAN_DEFINITIONS

NO_PROOF_SCRIPTS

NO_PRODUCTION_CLAIM
```

## 1. Purpose

This document specifies the theorem statements that a future Lean 4
formalization should prove for SPIRA Formal Core V1.

The statements are still specification drafts. They are not Lean definitions or
proof scripts.

## 2. Shared Notation

The intended core shape is:

```text
Core(E, P) = C
```

where:

```text
E = typed evidence
P = policy/version/context
C = authoritative machine contract
```

Predicates used below:

```text
ValidEvidence(E)
ValidPolicy(P)
ActiveBlocker(E, P)
RequiredUnknown(E, P, item)
RequiredExplicitListItem(E, P, field, item)
InvalidCoreInput(E, P)
Preserves(a, b, field)
NonAuthoritative(x)
```

The final Lean version may rename these predicates, but must preserve their
obligations.

## 3. Theorem 1: Determinism

### Informal Meaning

For the same typed evidence and same policy/context, the core returns the same
contract.

### Preconditions

```text
ValidEvidence(E)
ValidPolicy(P)
```

### Statement Draft

```text
Core(E, P) = C1
Core(E, P) = C2
=> C1 = C2
```

### Postcondition

All authoritative fields are equal:

```text
action
stop
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
identity fields
```

## 4. Theorem 2: Blocking Claim Prevents PROCEED

### Informal Meaning

If a policy-active blocker exists, the core cannot return `PROCEED`.

### Preconditions

```text
ValidEvidence(E)
ValidPolicy(P)
ActiveBlocker(E, P)
Core(E, P) = C
```

### Statement Draft

```text
C.action != PROCEED
and C.stop = true
```

### Required Preservation

The active blocker must be represented in:

```text
C.blocking_items
```

or, if the blocker cannot be concretely identified, a fail-closed reason must
be represented in:

```text
C.reason_codes
```

## 5. Theorem 3: Required NOT_EVALUATED Prevents Silent PASS

### Informal Meaning

Required unknown, malformed, unavailable, conflicting, or out-of-bound evidence
must not silently become a pass.

### Preconditions

```text
ValidPolicy(P)
RequiredUnknown(E, P, item)
Core(E, P) = C
```

### Statement Draft

```text
item in C.not_evaluated
and C.action != PROCEED
```

If a policy later allows `PROCEED` with a known non-critical unknown, that policy
must encode the item as non-required. Formal Core V1 does not allow silent
conversion of required unknowns to success.

## 6. Theorem 4: Explicit Contractual Lists Are Preserved

### Informal Meaning

Every semantically required explicit list item must appear in the authoritative
machine contract.

### Preconditions

```text
ValidEvidence(E)
ValidPolicy(P)
RequiredExplicitListItem(E, P, field, item)
Core(E, P) = C
```

### Statement Draft

```text
item in C.field
```

where `field` may be:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
```

### Exclusion

Model-generated restatement of a list is not a preservation mechanism.

## 7. Theorem 5: Gate A Preserves Complete Domain Contract

### Informal Meaning

Gate A may wrap a domain contract, but it cannot weaken or rewrite it.

### Preconditions

```text
DomainContract = C
GateA(C) = U
```

### Statement Draft

```text
Preserves(U, C, action)
Preserves(U, C, stop)
Preserves(U, C, reason_codes)
Preserves(U, C, blocking_items)
Preserves(U, C, not_evaluated)
Preserves(U, C, not_claimed)
Preserves(U, C, evidence_refs)
Preserves(U, C, proof_refs)
```

The future Lean statement may use a single structural preservation relation.

## 8. Theorem 6: Model and Presentation Fields Have Zero Decision Authority

### Informal Meaning

Model explanations, model self-reports, UI text, reports, and agent suggestions
cannot alter the authoritative decision.

### Preconditions

```text
Core(E, P) = C
NonAuthoritative(M)
```

### Statement Draft

```text
AuthoritativeAction(C, M) = C.action
AuthoritativeStop(C, M) = C.stop
```

and:

```text
M cannot modify C.reason_codes
M cannot modify C.blocking_items
M cannot modify C.not_evaluated
M cannot modify C.not_claimed
M cannot modify C.evidence_refs
M cannot modify C.proof_refs
```

### Design Implication

The accepted passthrough rule is:

```text
ModelOutput != DecisionAuthority
```

## 9. Theorem 7: Parse/Internal/Validation Errors Fail Closed

### Informal Meaning

Invalid typed evidence, invalid policy, version mismatch, identity mismatch, or
internal validation error cannot produce `PROCEED`.

### Preconditions

```text
InvalidCoreInput(E, P)
Core(E, P) = C
```

### Statement Draft

```text
C.action != PROCEED
and C.stop = true
```

The contract must preserve a fail-closed reason in:

```text
C.reason_codes
```

and, when applicable:

```text
C.not_evaluated
```

## 10. Lean Methodology Notes

The future Lean implementation should prefer:

```text
total core functions

explicit error constructors

opaque identity types at first

small domain-independent predicates

separate domain conformance modules

no axioms unless separately reviewed
```

This document does not create those modules.

## 11. Review Gate

The theorem statements are acceptable for Formal Core V1 only if the
specification review confirms:

```text
no theorem family was removed

no theorem family was weakened

preconditions are explicit

postconditions are explicit

out-of-scope assumptions are recorded in the TCB ledger
```
