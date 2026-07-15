# SPIRA Formal Core V1 Python/Lean Equivalence Protocol Review

## Status

```text
SPIRA_FORMAL_CORE_V1_PYTHON_LEAN_EQUIVALENCE_PROTOCOL_ACCEPTED

TYPED_EVIDENCE_EXCHANGE_BOUNDARY_ACCEPTED

FIELD_BY_FIELD_SEMANTIC_COMPARISON_ACCEPTED

EXPLICIT_LIST_EQUALITY_ACCEPTED

HASH_EQUALITY_NOT_SUFFICIENT_ACCEPTED

TRUSTED_BRIDGE_COMPONENTS_RECORDED

GENERIC_DIFFERENTIAL_HARNESS_AUTHORIZATION_REQUIRED_NEXT

NO_PYTHON_IMPLEMENTATION_AUTHORIZED_BY_THIS_PROTOCOL

NO_DOMAIN_CONFORMANCE_AUTHORIZED

NO_RUNTIME_INTEGRATION_AUTHORIZED

NO_PRODUCTION_CLAIM

NO_RELEASE
```

## 1. Review Scope

This review covers:

```text
research/formal_core/spira_formal_core_v1_python_lean_equivalence_protocol.md
```

It does not review or authorize a harness implementation.

## 2. Decision

The protocol is accepted.

The comparison boundary is correctly limited to canonical typed evidence:

```text
typed evidence -> Python core behavior
typed evidence -> Lean reference core
```

Raw parsers remain outside the comparison claim.

## 3. Equality Review

The review accepts the separation:

```text
formal semantic equality
canonical serialized equality
hash equality
```

Semantic equality is authoritative. Hash equality alone is not a proof of
semantic equality.

## 4. Field Mapping Review

The protocol requires field-by-field comparison of:

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

This is accepted.

## 5. Trusted Bridge Review

The bridge components are correctly recorded as trusted or tested, not proven:

```text
typed-evidence JSON parser
serializer
normalizer
Lean invocation wrapper
stdout/stderr parser
canonicalizer
hash implementation
```

The protocol does not overclaim Python correctness.

## 6. Required Next Authorization

The next document should be:

```text
research/formal_core/spira_formal_core_v1_differential_harness_authorization.md
```

It may authorize a generic research-only harness over canonical typed evidence
and formal test vectors.

It must not authorize production runtime integration or domain conformance.

## 7. Final Review Result

```text
SPIRA_FORMAL_CORE_V1_PYTHON_LEAN_EQUIVALENCE_PROTOCOL_ACCEPTED

GENERIC_DIFFERENTIAL_HARNESS_AUTHORIZATION_REQUIRED_NEXT
```
