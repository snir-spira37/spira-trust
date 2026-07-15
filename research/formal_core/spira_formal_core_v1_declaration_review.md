# SPIRA Formal Core V1 Declaration Review

## Status

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

PASSTHROUGH_ARCHITECTURE_PRESERVED

OLD_AGENT_BENCHMARK_RESULTS_PRESERVED

NO_EXISTING_RESULT_RECLASSIFICATION

FORMAL_SPECIFICATION_AUTHORIZATION_REQUIRED

FORMAL_IMPLEMENTATION_NOT_AUTHORIZED

LEAN_IMPLEMENTATION_NOT_AUTHORIZED

DOMAIN_ADAPTER_PROOF_NOT_AUTHORIZED

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Review Scope

This review evaluates:

```text
research/formal_core/spira_formal_core_v1_declaration_proposal.md
```

The review is limited to the proposed formal-methods direction and proof
boundary.

It does not review or authorize:

```text
Lean implementation

Python implementation changes

domain adapter changes

Gate A changes

passthrough envelope changes

benchmark runner changes

new live agent sessions

result reclassification

production or release claims
```

## 2. Decision

The declaration is accepted as the correct next direction for SPIRA.

The accepted direction is:

```text
do not attempt to prove the whole product first

prove a small deterministic shared decision core

force every domain to connect to that core through a typed-evidence contract
```

The central formal target is accepted:

```text
Core(E, P) = C
```

where:

```text
E = typed evidence
P = policy, version, and bounded context
C = authoritative SPIRA machine contract
```

## 3. Accepted Boundary

The typed-evidence boundary is accepted.

The proof boundary is:

```text
typed evidence
+
valid policy/version/context
->
authoritative SPIRA machine contract
```

The initial proof claim must not include raw input parsing.

This separation is essential:

```text
raw input
-> tested or untrusted adapter
-> typed-evidence boundary
-> formally verified SPIRA core
-> authoritative machine contract
-> untrusted agents and presentation
```

The core proof may later be combined with separately reviewed domain
conformance work, but adapter correctness is not part of Formal Core V1.

## 4. Accepted Core Contract Algebra Direction

The proposal correctly identifies the contract fields that must be represented
in the formal algebra:

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

The review accepts that explicit lists are semantic contract data, not
formatting details.

The future formal specification must preserve the distinctions:

```text
not_evaluated != pass

not_claimed != false

empty blocking_items != unknown blocking status
```

## 5. Accepted Seven Theorem Set

The proposed seven theorem families are accepted for specification.

They are:

```text
1. Determinism

2. Blocking claim prevents PROCEED

3. Required NOT_EVALUATED prevents silent PASS

4. Explicit contractual lists are preserved

5. Gate A preserves the complete domain contract

6. Model and presentation fields have zero decision authority

7. Parse/internal/validation errors fail closed
```

These theorem families are intentionally small, but they cover the core safety
invariants discovered through the prior MVP and agent-benchmark work.

The future theorem specification may refine names, predicates, and formal
preconditions, but it must not weaken these seven obligations without a
separate review.

## 6. Relationship to Passthrough Architecture

The declaration is consistent with the accepted machine-contract passthrough
architecture.

The accepted authority order remains:

```text
SPIRA machine contract
>
deterministic validator/evaluator
>
model explanation
>
model self-report or free-form agent suggestion
```

Formal Core V1 should prove the deterministic source of the authoritative
machine contract. It should not try to prove LLM behavior.

The accepted formal principle is:

```text
ModelOutput != DecisionAuthority
```

and more specifically:

```text
ExecutedAction must be derived from the authoritative machine contract,
not from model-generated explanation fields.
```

## 7. Domain Rollout Assessment

The recommended rollout order is accepted.

Domain 2 is the right first conformance target because the typed-evidence
language is compact:

```text
tests passed

tests failed

collection error

conflicting evidence

malformed evidence

required information unknown
```

The review accepts the proposed early Domain 2 shape:

```text
action = PROCEED
=>
failures = 0
and conflict = false
and requiredUnknown = empty
```

Domain 3 and Domain 1 should follow after the core algebra and Domain 2 proof
pattern are stable.

## 8. Trusted Computing Base Requirement

The trusted computing base ledger is required before implementation.

The next specification must distinguish at least:

```text
Lean kernel

formal definitions

proof scripts

Python mirror or implementation, if any

JSON serialization and canonicalization

domain adapters

test corpus

Python runtime

operating system

LLM providers

benchmark runners
```

Any future public claim must state:

```text
proven

trusted

tested

out of scope
```

as separate categories.

No claim may imply that raw file parsing, external tools, providers, or live
agent behavior have been formally proven unless those components receive
separate proof work.

## 9. Preservation of Existing Results

This review preserves all existing benchmark and readiness results.

It does not reclassify:

```text
old Claude strict-regeneration results

old Codex strict-regeneration results

old partial primary attempts

post-passthrough readiness results

post-preflight primary attempts
```

Those results remain evidence for the architectural lesson:

```text
language models are not deterministic contract serializers
```

Formal Core V1 addresses a different claim:

```text
given typed evidence and policy, the deterministic SPIRA core produces a safe
authoritative machine contract according to a formal specification
```

## 10. Required Next Document

The next document should be:

```text
research/formal_core/spira_formal_core_v1_specification_authorization.md
```

It should authorize specification work only.

It should allow:

```text
contract algebra specification

typed-evidence boundary specification

seven theorem statement specification

Lean 4 methodology specification

trusted computing base ledger

Domain 2 first-conformance plan
```

It should not authorize:

```text
Lean implementation

proof scripts

Python code changes

adapter changes

benchmark changes

new live sessions

production claims

release
```

## 11. Accepted Next Status

After this review, the authoritative status is:

```text
SPIRA_FORMAL_CORE_V1_DECLARATION_ACCEPTED

FORMAL_CORE_SPECIFICATION_AUTHORIZATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED

PYTHON_IMPLEMENTATION_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

AGENT_BENCHMARKS_PAUSED

NO_EXISTING_RESULT_RECLASSIFICATION

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 12. Summary

The declaration correctly reframes SPIRA's strongest proof path:

```text
prove the foundation,
not the whole house
```

The accepted proof boundary is the deterministic typed-evidence core. Domain
adapters, raw file formats, and LLM explanations remain outside the first proof
claim and must connect through explicit contracts, tests, conformance reviews,
or later proofs.

This is the right direction for a credible Formal Core V1.
