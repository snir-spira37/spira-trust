# SPIRA Formal Core V1 Specification Review

## Status

```text
SPIRA_FORMAL_CORE_V1_SPECIFICATION_ACCEPTED

CONTRACT_ALGEBRA_SPECIFICATION_ACCEPTED

TYPED_EVIDENCE_BOUNDARY_SPECIFICATION_ACCEPTED

SEVEN_CORE_THEOREM_STATEMENTS_ACCEPTED

TRUSTED_COMPUTING_BASE_LEDGER_ACCEPTED

CANONICALIZATION_AND_IDENTITY_ASSUMPTIONS_RECORDED

DOMAIN_2_FIRST_CONFORMANCE_PLAN_ACCEPTED

LEAN_IMPLEMENTATION_AUTHORIZATION_REQUIRED_NEXT

LEAN_DEFINITIONS_NOT_AUTHORIZED_BY_THIS_REVIEW

PROOF_SCRIPTS_NOT_AUTHORIZED_BY_THIS_REVIEW

PYTHON_CODE_CHANGES_NOT_AUTHORIZED

DOMAIN_ADAPTER_CONFORMANCE_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Review Scope

This review covers the specification deliverables authorized by:

```text
research/formal_core/spira_formal_core_v1_specification_authorization.md
```

The reviewed deliverables are:

```text
spira_formal_core_v1_contract_algebra_spec.md
spira_formal_core_v1_theorem_spec.md
spira_formal_core_v1_trusted_computing_base_ledger.md
spira_formal_core_v1_domain2_conformance_plan.md
```

## 2. Decision

The specification phase is accepted.

The documents define a sufficiently precise Formal Core V1 target for the next
authorization stage.

The accepted scope remains narrow:

```text
typed evidence
+
policy/version/context
->
authoritative machine contract
```

Raw parsers, domain adapters, Python runtime behavior, and LLM behavior remain
outside the initial proof boundary.

## 3. Contract Algebra Review

The contract algebra specification is accepted.

It covers the required authoritative fields:

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

It correctly treats explicit lists as semantic contract data and preserves:

```text
NOT_EVALUATED != PASS
not_claimed != false
empty blocking_items != unknown blocking status
```

The review accepts the choice of ordered, required, structurally compared
explicit lists for V1.

## 4. Theorem Specification Review

The seven theorem families are accepted for implementation authorization:

```text
1. Determinism
2. Blocking claim prevents PROCEED
3. Required NOT_EVALUATED prevents silent PASS
4. Explicit contractual lists are preserved
5. Gate A preserves the complete domain contract
6. Model and presentation fields have zero decision authority
7. Parse/internal/validation errors fail closed
```

The statements remain drafts until encoded in Lean, but the obligations are
clear enough to proceed to a Lean implementation authorization.

No theorem family was removed or weakened.

## 5. Trusted Computing Base Review

The TCB ledger is accepted.

It correctly separates:

```text
PROVEN_TARGET
TRUSTED_ASSUMPTION
TESTED_ONLY
FUTURE_CONFORMANCE_REQUIRED
OUT_OF_SCOPE
```

The review especially accepts that the following are not part of the initial
proof claim:

```text
raw wheel/ZIP parsing
pytest/JUnit parsing
Terraform JSON parsing
canonical JSON implementation
Python runtime
LLM providers
benchmark runners
```

This prevents overclaiming.

## 6. Canonicalization and Identity Review

The specification records that Formal Core V1 may use structural identity
internally.

External byte-level identity mechanisms remain outside the initial proof unless
separately authorized:

```text
canonical JSON
SHA-256 implementation
serialized contract bytes
adapter-produced reference hashes
```

This is accepted.

## 7. Domain 2 Plan Review

The Domain 2 first-conformance plan is accepted as a plan only.

Domain 2 is the right first target because bounded pytest evidence has a compact
typed-evidence vocabulary.

The proposed core obligation is accepted:

```text
action = PROCEED
=>
failed_test_count = 0
and error_count = 0
and conflict_present = false
and malformed_result = false
and required_unknown = []
```

Domain 2 conformance implementation remains blocked until separately
authorized.

## 8. Required Next Authorization

The next document should be:

```text
research/formal_core/spira_formal_core_v1_lean_implementation_authorization.md
```

It may authorize:

```text
Lean project scaffolding
formal algebra definitions
core function definitions
seven theorem statements
proof scripts for the seven theorem families
Lean test/build instructions
implementation report
implementation review
```

It must keep blocked:

```text
Python code changes
domain adapter changes
Domain 2 conformance implementation
Gate A Python changes
benchmark changes
live sessions
production claims
release
```

## 9. Final Review Status

```text
FORMAL_CORE_DECLARATION:
ACCEPTED

FORMAL_CORE_SPECIFICATION:
ACCEPTED

LEAN IMPLEMENTATION:
AUTHORIZATION REQUIRED NEXT

PYTHON CHANGES:
BLOCKED

DOMAIN CONFORMANCE:
BLOCKED

AGENT BENCHMARKS:
PAUSED

PRODUCTION CLAIM:
BLOCKED

RELEASE:
BLOCKED
```
