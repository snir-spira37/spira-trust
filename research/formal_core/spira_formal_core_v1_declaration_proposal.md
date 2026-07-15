# SPIRA Formal Core V1 Declaration Proposal

## Status

```text
SPIRA_FORMAL_CORE_V1_DECLARATION_PROPOSED

MINIMAL_SHARED_DECISION_CORE_ONLY

TYPED_EVIDENCE_BOUNDARY_PROPOSED

CONTRACT_ALGEBRA_FORMALIZATION_PROPOSED

SEVEN_CORE_THEOREMS_PROPOSED

LEAN_4_REFERENCE_FORMALIZATION_PROPOSED

PYTHON_ADAPTERS_OUTSIDE_INITIAL_PROOF_BOUNDARY

DOMAIN_CONFORMANCE_REQUIRED_SEPARATELY

TRUSTED_COMPUTING_BASE_LEDGER_REQUIRED

PASSTHROUGH_ARCHITECTURE_PRESERVED

OLD_AGENT_BENCHMARK_RESULTS_PRESERVED

NO_EXISTING_RESULT_RECLASSIFICATION

NO_FORMAL_IMPLEMENTATION_AUTHORIZATION

NO_LEAN_IMPLEMENTATION_AUTHORIZATION

NO_DOMAIN_ADAPTER_PROOF_AUTHORIZATION

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Purpose

This proposal declares a new formal-methods direction for SPIRA.

The goal is not to prove the whole product, all parsers, all file formats, all
agent behavior, or all presentation logic.

The goal is to isolate and eventually prove a small deterministic core:

```text
Core(E, P) = C
```

where:

```text
E = typed evidence
P = policy, version, and bounded context
C = authoritative SPIRA machine contract
```

The intended proof target is the shared decision core that every domain must
connect to through a typed-evidence boundary.

This is a declaration proposal only. It does not authorize Lean code, Python
refactors, domain adapter changes, benchmark result changes, or production
claims.

## 2. Motivation

The accepted machine-contract passthrough architecture established the core
product principle:

```text
SPIRA machine contract:
authoritative

model explanation:
non-authoritative

agent or presentation suggestion:
non-authoritative
```

The live Claude and Codex investigations showed that language models are not
deterministic serializers of a contract they are asked to regenerate. The
accepted architecture therefore preserves the SPIRA contract mechanically and
uses deterministic validators and evaluators to detect contradictions.

That architecture creates the right boundary for formal work:

```text
raw input
-> tested or untrusted adapter
-> typed-evidence boundary
-> formally verified SPIRA core
-> authoritative machine contract
-> untrusted agents and presentation
```

Formal Core V1 should prove the foundation at the typed-evidence boundary,
while leaving raw parsers and live agents outside the initial trusted theorem
scope.

## 3. Proposed Formal Boundary

### 3.1 In Scope

Formal Core V1 proposes to prove properties of:

```text
typed evidence

policy/version/context inputs

contract algebra

decision action

stop state

reason_codes

blocking_items

not_evaluated

not_claimed

evidence references

proof binding

contract identity

Gate A preservation over complete domain contracts

model and presentation fields having zero decision authority

fail-closed behavior for validation and internal errors
```

### 3.2 Out of Scope

Formal Core V1 does not initially prove:

```text
filesystem behavior

ZIP or wheel parsing

JSON parser correctness

JUnit or pytest output extraction

Terraform CLI behavior

Terraform Plan JSON parsing

network behavior

operating system behavior

Claude, Codex, DeepSeek, or any LLM behavior

natural-language explanation quality

provider usage accounting

UI or report rendering

Python runtime correctness
```

Those components remain adapters, integrations, or presentation layers. They
may be tested, audited, fuzzed, or separately proven later, but they are not
part of the initial mathematical proof claim.

## 4. Core Contract Shape

Formal Core V1 should define a contract algebra sufficient to represent the
accepted SPIRA decision semantics:

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

The formal contract must preserve explicit lists as semantic data, not as
formatting artifacts.

The proof should treat absence of required evidence differently from evidence
that proves success:

```text
not_evaluated != pass

not_claimed != false

empty blocking_items != unknown blocking status
```

## 5. Typed-Evidence Boundary

Each domain must eventually expose a typed-evidence language that is smaller
than its raw input format.

The boundary separates:

```text
adapter responsibility:
raw input -> typed evidence

formal core responsibility:
typed evidence + policy -> machine contract
```

The first formal core does not prove that every adapter constructed the typed
evidence correctly. It proves that if the typed evidence satisfies the formal
language, the resulting SPIRA contract satisfies the core theorem set.

The intended claim is:

```text
valid typed claims
+
valid policy
->
correct SPIRA contract according to the formal core specification
```

not:

```text
all real-world files are parsed correctly
```

## 6. Seven Proposed Core Theorems

### 6.1 Determinism

For fixed typed evidence and fixed policy/version/context, the core returns the
same machine contract.

```text
Core(E, P) = C1
Core(E, P) = C2
=> C1 = C2
```

### 6.2 Blocking Claim Prevents PROCEED

If typed evidence contains an active blocking condition under the policy, the
resulting contract cannot authorize `PROCEED`.

```text
active_blocker(E, P)
=> Core(E, P).action != PROCEED
```

### 6.3 Required NOT_EVALUATED Prevents Silent PASS

If required information is unavailable, malformed, unknown, conflicting, or
outside the evaluated boundary, the result must preserve that uncertainty in
`not_evaluated` and must not silently convert it to success.

```text
required_unknown(E, P)
=> required_unknown_item in Core(E, P).not_evaluated
```

### 6.4 Explicit Contractual Lists Are Preserved

The core must preserve all semantically required explicit lists in the machine
contract:

```text
reason_codes

blocking_items

not_evaluated

not_claimed

evidence references

proof references
```

The theorem should rule out silent loss, replacement, or model-side
regeneration of these lists.

### 6.5 Gate A Preserves the Complete Domain Contract

Gate A may assemble, wrap, and expose a domain contract, but it must not weaken
or rewrite the complete domain decision contract.

```text
DomainContract(D) = C
GateA(C) = U
=> U preserves C.action, C.stop, C.reason_codes, C.blocking_items,
   C.not_evaluated, C.not_claimed, C.evidence references, and C.proof binding
```

### 6.6 Model and Presentation Fields Have Zero Decision Authority

Any field produced by a model, agent, UI, report, or explanation channel must
not alter the authoritative machine contract.

```text
Core(E, P) = C
presentation_or_model_output = M
=> authoritative_action(C, M) = C.action
```

This theorem aligns the formal core with the accepted passthrough architecture:

```text
ModelOutput != DecisionAuthority
```

### 6.7 Parse, Validation, and Internal Errors Fail Closed

When the core receives invalid typed evidence, invalid policy, version
mismatch, inconsistent internal state, or proof-binding failure, it must return
a non-proceeding fail-closed result.

```text
invalid_core_input(E, P)
=> Core(E, P).action != PROCEED
```

and the resulting contract must preserve the reason for non-proceeding rather
than silently omitting it.

## 7. Domain Rollout Strategy

Formal Core V1 should start with the smallest domain language that provides
meaningful coverage.

The recommended first domain is Domain 2, bounded local pytest result evidence,
because its typed-evidence space is compact:

```text
tests passed

tests failed

collection error

conflicting evidence

malformed evidence

required information unknown
```

An early Domain 2 theorem can target:

```text
action = PROCEED
=>
failures = 0
and conflict = false
and requiredUnknown = empty
```

After the core algebra and proof pattern are stable, Domain 3 and Domain 1 can
conform to the same core rather than defining separate decision theories.

## 8. Trusted Computing Base Ledger

Any future formalization must maintain a trusted computing base ledger.

The ledger should distinguish:

```text
Lean kernel

formal definitions

extracted or mirrored Python implementation, if any

JSON serialization and canonicalization

domain adapters

test corpus

Python runtime

operating system

LLM providers

benchmark runners
```

The proof claim must explicitly state which parts are proven, which parts are
trusted, and which parts are only tested.

No public claim may collapse these categories.

## 9. Relationship to Existing Results

This proposal preserves all prior benchmark and readiness results.

It does not reclassify:

```text
old Claude strict-regeneration results

old Codex strict-regeneration results

old partial primary attempts

post-passthrough readiness results

post-preflight primary attempts
```

Those results remain evidence for the architecture decision:

```text
language models are not 100% deterministic contract serializers
```

Formal Core V1 addresses a different question:

```text
given typed evidence and policy, does the deterministic SPIRA core produce a
safe authoritative machine contract according to the formal specification?
```

## 10. Proposed Authorization Sequence

This declaration proposes the following sequence:

```text
1. Formal Core V1 declaration proposal

2. Declaration review

3. Contract algebra and theorem specification

4. Lean 4 methodology and trusted-base lock

5. Generic core implementation in Lean

6. Seven machine-checked proofs

7. Differential equivalence against the existing Python core

8. Domain 2 conformance

9. Domain 3 conformance

10. Domain 1 conformance

11. Gate A / passthrough proof package

12. External reproduction package
```

Each step requires its own authorization or review before implementation.

## 11. Non-Authorization

This proposal does not authorize:

```text
Lean implementation

Python implementation changes

adapter changes

Domain 1, 2, or 3 producer changes

Gate A changes

passthrough envelope changes

validator changes

benchmark runner changes

new live sessions

result reclassification

production claim

release
```

## 12. Proposed Review Outcome

If accepted, the next review should be able to conclude:

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

NO_EXISTING_RESULT_RECLASSIFICATION

FORMAL_IMPLEMENTATION_AUTHORIZATION_REQUIRED

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 13. Intended Future Claim

If the future proof program succeeds, the valid claim should be narrow:

```text
Given typed evidence satisfying the formal evidence language and a valid policy,
the SPIRA Formal Core V1 has been machine-checked in Lean as deterministic,
fail-closed, uncertainty-preserving, explicit-list-preserving, and unable to
return PROCEED when a blocking condition is present.
```

After separate domain conformance work, a stronger claim may be possible:

```text
Domains 1-3 map their supported input languages to the typed-evidence boundary
according to separately reviewed conformance specifications.
```

No claim should imply that all raw files, tools, providers, agents, or operating
environments have been formally proven.
