# SPIRA Formal Core V1 Python/Lean Equivalence Protocol

## Status

```text
SPIRA_FORMAL_CORE_V1_PYTHON_LEAN_EQUIVALENCE_PROTOCOL_PROPOSED

PROTOCOL_ONLY

NO_PYTHON_IMPLEMENTATION_AUTHORIZATION

NO_DIFFERENTIAL_HARNESS_IMPLEMENTATION_AUTHORIZATION

NO_DOMAIN_CONFORMANCE_AUTHORIZATION

NO_RUNTIME_INTEGRATION_AUTHORIZATION

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Purpose

This protocol defines how a later research-only differential harness should
compare accepted Python behavior with the executable Lean Formal Core V1.

It does not authorize writing the harness or changing Python.

The permitted future claim shape is:

```text
The existing Python behavior is differentially equivalent to the executable
Lean reference core on the evaluated corpus.
```

It is not a proof of Python correctness.

## 2. Comparison Boundary

The comparison boundary is typed evidence only:

```text
canonical typed evidence
-> Python core behavior

canonical typed evidence
-> Lean reference core
```

The protocol does not compare raw input parsing.

Out of scope:

```text
wheel/ZIP parsing
pytest/JUnit parsing
Terraform JSON parsing
LLM behavior
runtime bridge integration
production deployment
```

## 3. Exchange Representation

The future harness must define a canonical typed-evidence exchange
representation containing:

```text
domain_id
subject_id
schema_version
producer_id
evidence_validity
typed_claims
evidence_refs
proof_refs
policy_id
policy_schema_version
policy_required_claims
policy_blocking_rules
policy_not_claimed_rules
```

The representation must distinguish:

```text
missing field
empty list
known unknown
not evaluated
invalid evidence
version incompatibility
```

## 4. Field Mapping

The future harness must compare every semantic contract field:

```text
action
stop
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
domain_id
subject_id
policy_id
schema_version
producer_id
contract_id
```

No field may be compared only by a hash when semantic equality is available.

## 5. Equality Layers

The protocol distinguishes:

```text
formal semantic equality
canonical serialized equality
hash equality
```

Rules:

```text
semantic equality is authoritative for differential comparison

canonical serialized equality is supporting evidence

hash equality alone is insufficient
```

## 6. Explicit List Equality

Explicit lists are compared as:

```text
ordered
required
structural
empty list distinct from missing field
```

A future comparator must fail closed on:

```text
missing list
reordered list
extra item
missing item
item substitution
type mismatch
```

unless a separate global amendment changes list semantics.

## 7. Action and Error Mapping

Action mapping:

```text
Python PROCEED <-> Lean Action.PROCEED
Python STOP_BLOCKED <-> Lean Action.STOP_BLOCKED
Python RERUN_REQUIRED <-> Lean Action.RERUN_REQUIRED
Python REPORT_NOT_EVALUATED <-> Lean Action.REPORT_NOT_EVALUATED
```

Error mapping:

```text
invalid typed evidence -> non-PROCEED fail-closed result
incomplete typed evidence -> non-PROCEED fail-closed result
conflicting typed evidence -> non-PROCEED fail-closed result
version incompatibility -> non-PROCEED fail-closed result
internal validation failure -> non-PROCEED fail-closed result
```

The exact action may be compared when specified; otherwise the minimum gate is:

```text
error result.action != PROCEED
```

## 8. Manifests

The future harness must record:

```text
typed evidence input hash
policy/context hash
Python source commit
Lean source commit
Lean toolchain
Python output hash
Lean output hash
normalized semantic contract hash
comparison result
```

## 9. Trusted Bridge Components

The bridge remains outside the current proof boundary.

The TCB ledger must record:

```text
typed-evidence JSON parser
typed-evidence JSON serializer
Python normalization code
Lean invocation wrapper
stdout/stderr parser
canonicalization implementation
hash implementation
```

These components are trusted or tested unless separately proved.

## 10. Stop Conditions

The future differential harness must stop on:

```text
semantic field mismatch
list mismatch
identity mismatch
missing field
non-deterministic repeat
Lean execution failure
Python execution failure
bridge parse failure
hash/semantic disagreement
```

Mismatches must be preserved. They must not be repaired by changing oracle,
corpus, Lean definitions, or Python behavior inside the same phase.

## 11. Required Future Authorization

The next implementation document should be:

```text
research/formal_core/spira_formal_core_v1_differential_harness_authorization.md
```

It may authorize a research-only generic differential harness.

It must not authorize:

```text
production Python integration
Domain conformance claims
release
```
