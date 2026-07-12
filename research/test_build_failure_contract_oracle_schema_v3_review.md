# Test/Build Failure Contract - Oracle Schema V3 Review

## Status

```text
DOMAIN_2_ORACLE_SCHEMA_V3_NEEDS_REVISION
ORACLE_SCHEMA_V3_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed schema:

```text
research/test_build_failure_contract_oracle_schema_v3.schema.json
```

Reviewed commit:

```text
c6fedeb5518af3402bead222ccff6174fdac84cb
```

## Review Scope

This review checks whether Oracle Schema V3 is ready to support oracle case
authoring.

It does not authorize:

```text
oracle population
fixture generation
corpus materialization
producer implementation
validator implementation
Gate B
release/version/tag/PyPI
```

## Accepted Fixes From V3

Oracle Schema V3 correctly addresses the gaps found in the V2 review.

### Scope Identity Contract

V3 adds:

```text
scope_identity_sha256
scope_projection
scope_projection_sha256
```

and requires emitted scope identity to contain:

```text
scope_identity_sha256
collection_manifest_sha256
canonical_collected_test_ids
scope_projection or scope_projection_sha256
```

This is accepted as a structural improvement.

### Emitted Result Identity Eligibility

V3 restricts emitted `result_identity` projections to:

```text
evidence_completeness == COMPLETE
process_state != NOT_EVALUATED
result_state not in NOT_EVALUATED / CONFLICTING / UNSUPPORTED
```

This is accepted.

### One-Way Action Stop Consistency

V3 enforces:

```text
stop: false
-> recommended_agent_action in PROCEED / REPORT_WITH_NOTES
```

This closes the most dangerous direction where a non-stopping oracle action
could still report a blocking action. The improvement is accepted, but the
rule remains incomplete as described below.

## Blocking Finding 1 - Identity Hash Recomputation Is Not Fully Specified

V3 adds identity digests and projections, but the validator requirements do not
yet require recomputation of every digest from its canonical projection.

Currently required:

```text
RESULT_SCOPE_IDENTITY_HASH_MATCHES_EXPECTED_SCOPE
```

Still missing:

```text
SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION
RESULT_IDENTITY_HASH_MATCHES_RESULT_PROJECTION
COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST
```

Without these invariants, an oracle case can contain syntactically valid hashes
that are not derived from the projections they purport to identify.

Required revision:

```text
validator_enforced_before_oracle_population must include:
  SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION
  RESULT_IDENTITY_HASH_MATCHES_RESULT_PROJECTION
  COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST
```

If any of these can be enforced directly by schema, V4 may classify them as
schema-enforced. Otherwise they must be validator-enforced before oracle
population.

## Blocking Finding 2 - Explicit Lists Are Duplicated Without Equivalence Invariant

The schema has explicit case lists in two places:

```text
expected_result_identity.projection.blocking_cases
expected_result_identity.projection.nonblocking_cases
```

and:

```text
expected_explicit_lists.blocking_cases
expected_explicit_lists.nonblocking_cases
```

But V3 does not require these lists to be identical.

This weakens the strict-list invariant that motivated the Domain 2 model:

```text
counts and summaries must derive from explicit sorted unique lists
```

Required revision:

```text
validator_enforced_before_oracle_population must include:
  RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS
```

The invariant must compare canonical list content exactly:

```text
projection.blocking_cases == expected_explicit_lists.blocking_cases
projection.nonblocking_cases == expected_explicit_lists.nonblocking_cases
```

If `expected_result_identity.status == NOT_EVALUATED`, then the invariant must
define whether `expected_explicit_lists` must be empty or may contain only
separately justified evidence lists. That choice must be explicit before oracle
population.

## Blocking Finding 3 - ACTION_STOP_CONSISTENCY Is Only One-Way

V3 enforces:

```text
stop: false
-> PROCEED or REPORT_WITH_NOTES
```

But it does not explicitly reject:

```text
stop: true + PROCEED
stop: true + REPORT_WITH_NOTES
```

This leaves the action contract asymmetric.

Required revision:

```text
stop: true
-> recommended_agent_action not in PROCEED / REPORT_WITH_NOTES
```

Equivalently:

```text
stop: true
-> recommended_agent_action in STOP_BLOCKED / RERUN_REQUIRED / REPORT_NOT_EVALUATED
```

This may be schema-enforced directly and should remain part of:

```text
ACTION_STOP_CONSISTENCY
```

## Required Next Artifact

The next artifact should be a schema revision:

```text
research/test_build_failure_contract_oracle_schema_v4.schema.json
```

It must at minimum:

```text
1. Require recomputation checks for scope, result, and collection manifest hashes.
2. Require explicit-list equivalence between result projection and expected lists.
3. Make ACTION_STOP_CONSISTENCY bidirectional.
4. Keep oracle population blocked.
5. Keep validator implementation blocked unless separately authorized.
```

## Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V3_NEEDS_REVISION
ORACLE_SCHEMA_V3_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle Schema V3 is a strong improvement, but it is not accepted until hash
recomputation, strict-list equivalence, and bidirectional action/stop
consistency are locked.
