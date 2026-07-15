# SPIRA Formal Core V1 Specification Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_SPECIFICATION_AUTHORIZED

SPECIFICATION_PHASE_ONLY

CONTRACT_ALGEBRA_SPECIFICATION_AUTHORIZED

TYPED_EVIDENCE_BOUNDARY_SPECIFICATION_AUTHORIZED

POLICY_VERSION_CONTEXT_SPECIFICATION_AUTHORIZED

SEVEN_CORE_THEOREM_STATEMENTS_AUTHORIZED

FORMAL_PRECONDITIONS_AND_POSTCONDITIONS_REQUIRED

LEAN_4_METHODOLOGY_SPECIFICATION_AUTHORIZED

TRUSTED_COMPUTING_BASE_LEDGER_REQUIRED

CANONICALIZATION_AND_IDENTITY_ASSUMPTIONS_REQUIRED

DOMAIN_2_FIRST_CONFORMANCE_PLAN_AUTHORIZED

SPECIFICATION_REVIEW_REQUIRED

LEAN_IMPLEMENTATION_NOT_AUTHORIZED

LEAN_DEFINITIONS_NOT_AUTHORIZED

PROOF_SCRIPTS_NOT_AUTHORIZED

PYTHON_CODE_CHANGES_NOT_AUTHORIZED

DOMAIN_ADAPTER_CONFORMANCE_NOT_AUTHORIZED

GATE_A_CHANGES_NOT_AUTHORIZED

PASSTHROUGH_CHANGES_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Purpose

This document authorizes the specification phase for SPIRA Formal Core V1.

The accepted declaration review established the proof direction:

```text
Core(E, P) = C
```

where:

```text
E = typed evidence
P = policy, version, and bounded context
C = authoritative SPIRA machine contract
```

This authorization permits writing the formal specification documents needed
before any Lean implementation or proof scripts are created.

This phase must define exactly what the future proof will mean, what it will
not mean, and which assumptions will remain trusted, tested, or out of scope.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_DECLARATION_ACCEPTED

MINIMAL_SHARED_DECISION_CORE_ACCEPTED

TYPED_EVIDENCE_BOUNDARY_ACCEPTED

CONTRACT_ALGEBRA_FORMALIZATION_ACCEPTED

SEVEN_CORE_THEOREMS_ACCEPTED_FOR_SPECIFICATION

LEAN_4_REFERENCE_FORMALIZATION_ACCEPTED_AS_DIRECTION

PYTHON_ADAPTERS_OUTSIDE_INITIAL_PROOF_BOUNDARY_ACCEPTED

DOMAIN_CONFORMANCE_REQUIRED_SEPARATELY

TRUSTED_COMPUTING_BASE_LEDGER_REQUIRED
```

## 3. Authorized Deliverables

The following deliverables are authorized:

```text
research/formal_core/spira_formal_core_v1_contract_algebra_spec.md

research/formal_core/spira_formal_core_v1_theorem_spec.md

research/formal_core/spira_formal_core_v1_trusted_computing_base_ledger.md

research/formal_core/spira_formal_core_v1_domain2_conformance_plan.md

research/formal_core/spira_formal_core_v1_specification_review.md
```

The Domain 2 conformance plan may remain a plan only. It must not implement
adapter conformance, tests, Lean definitions, or Python code.

## 4. Contract Algebra Specification Scope

The contract algebra specification must define the abstract data needed for the
formal core.

It must cover at least:

```text
action

stop

reason_codes

blocking_items

not_evaluated

not_claimed

evidence references

proof references

domain identity

subject or case identity

policy identity

schema/version identity

producer identity

contract identity
```

It must preserve the accepted semantic distinctions:

```text
NOT_EVALUATED != PASS

not_claimed != false

empty blocking_items != unknown blocking status
```

It must specify whether each list is:

```text
ordered or unordered

deduplicated or multiplicity-preserving

canonicalized or compared structurally

required or optional

allowed to be empty or required to be non-empty
```

The specification must not silently treat explicit contract lists as display
formatting.

## 5. Typed-Evidence Boundary Specification Scope

The typed-evidence boundary specification must define the formal input layer
for the core.

It must distinguish:

```text
raw input

adapter output

typed evidence

policy/version/context

core contract output
```

It must state that adapter correctness is outside the first proof boundary.

The initial proof claim may only assume:

```text
valid typed evidence
+
valid policy/version/context
```

not:

```text
correct parsing of every raw artifact
```

The specification must include how malformed, incomplete, conflicting, or
version-incompatible typed evidence is represented or rejected.

## 6. Theorem Specification Scope

The theorem specification must turn the accepted seven theorem families into
precise statement drafts.

It must include:

```text
formal name

informal meaning

preconditions

postconditions

failure mode

fields involved

trusted assumptions

known exclusions

future Lean statement sketch
```

The seven theorem families are:

```text
1. Determinism

2. Blocking claim prevents PROCEED

3. Required NOT_EVALUATED prevents silent PASS

4. Explicit contractual lists are preserved

5. Gate A preserves the complete domain contract

6. Model and presentation fields have zero decision authority

7. Parse/internal/validation errors fail closed
```

The specification phase may refine predicate names and preconditions, but it
must not weaken these seven obligations.

## 7. Lean 4 Methodology Specification Scope

The Lean methodology specification must remain methodological.

It may specify:

```text
Lean 4 as the intended proof assistant

expected module layout

definition/proof separation

use of total functions or explicit error types

avoidance of axioms unless separately authorized

notation policy

proof review expectations

reproducibility expectations
```

It must not create:

```text
.lean files

Lean definitions

proof scripts

Lake project files

extraction or code-generation hooks
```

## 8. Trusted Computing Base Ledger Scope

The trusted computing base ledger must classify components as:

```text
PROVEN_TARGET

TRUSTED_ASSUMPTION

TESTED_ONLY

OUT_OF_SCOPE

FUTURE_CONFORMANCE_REQUIRED
```

It must include at least:

```text
Lean kernel

formal definitions

proof scripts

JSON serialization and canonicalization

typed-evidence construction

Domain 1 adapter

Domain 2 adapter

Domain 3 adapter

Gate A implementation

passthrough envelope implementation

validator implementation

Python runtime

operating system

LLM providers

benchmark runners
```

It must define how future claims should avoid collapsing proven, trusted,
tested, and out-of-scope components.

## 9. Canonicalization and Identity Assumptions

The specification deliverables must explicitly address canonicalization and
identity assumptions.

They must cover:

```text
contract identity

policy identity

schema/version identity

evidence reference identity

proof reference identity

hash binding

canonical JSON, if used outside the formal core

structural equality versus byte equality

list equality semantics
```

If a future proof assumes canonical equality, the assumption must be recorded
in the trusted computing base ledger unless the canonicalizer itself becomes a
separate proof target.

## 10. Domain 2 First-Conformance Plan

The Domain 2 plan must define how bounded local pytest result evidence will be
the first domain to connect to the formal core.

It should cover a compact typed-evidence vocabulary such as:

```text
tests passed

tests failed

collection error

conflicting evidence

malformed evidence

required information unknown
```

It should draft at least one conformance obligation of the form:

```text
action = PROCEED
=>
failures = 0
and conflict = false
and requiredUnknown = empty
```

This plan must not implement the conformance proof or change the Domain 2
adapter.

## 11. Required Review

The final deliverable for this phase must be:

```text
research/formal_core/spira_formal_core_v1_specification_review.md
```

The review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_SPECIFICATION_ACCEPTED

SPIRA_FORMAL_CORE_V1_SPECIFICATION_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_SPECIFICATION_REJECTED
```

If accepted, it may recommend a later implementation authorization. It must
not itself authorize Lean implementation or proof scripts.

## 12. Explicit Non-Authorization

This document does not authorize:

```text
Lean definitions

Lean proof scripts

Lake project creation

Python code changes

source/spira_core changes

tools changes

test changes

domain adapter changes

Gate A changes

passthrough envelope changes

validator changes

benchmark runner changes

new live sessions

result reclassification

production claim

release
```

## 13. Success Criteria

This phase succeeds only if the specification review confirms:

```text
contract algebra is sufficiently precise

typed-evidence boundary is explicit

seven theorem statements are specified without weakening

preconditions and postconditions are documented

Lean methodology is defined without implementation

trusted computing base ledger is complete enough for V1

canonicalization and identity assumptions are recorded

Domain 2 first-conformance plan is concrete but non-implementing

old agent benchmark results remain preserved

no production claim is made
```

## 14. Current Authoritative Status

```text
FORMAL_CORE_DECLARATION:
ACCEPTED

FORMAL_CORE_SPECIFICATION:
AUTHORIZED NEXT

LEAN IMPLEMENTATION:
BLOCKED

PROOF SCRIPTS:
BLOCKED

PYTHON CHANGES:
BLOCKED

DOMAIN CONFORMANCE:
BLOCKED

AGENT BENCHMARKS:
PAUSED

RELEASE:
BLOCKED
```
