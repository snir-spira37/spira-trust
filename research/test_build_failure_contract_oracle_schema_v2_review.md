# Test/Build Failure Contract - Oracle Schema V2 Review

## Status

```text
DOMAIN_2_ORACLE_SCHEMA_V2_NEEDS_REVISION
ORACLE_SCHEMA_V2_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed schema:

```text
research/test_build_failure_contract_oracle_schema_v2.schema.json
```

Reviewed commit:

```text
7839758435430b02b506da9fe2ec70c6936733a2
```

## Review Scope

This review checks whether Oracle Schema V2 is ready to support oracle case
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

## Accepted Fixes From V2

Oracle Schema V2 correctly closes the two fail-closed holes found in V1.

### NOT_EVALUATED Result Identity

V2 rejects:

```text
result_identity.status == NOT_EVALUATED
+ result_identity_sha256
```

and:

```text
result_identity.status == NOT_EVALUATED
+ projection
```

This is accepted.

### NOT_EVALUATED Scope Identity

V2 rejects:

```text
scope_identity.status == NOT_EVALUATED
+ collection_manifest_sha256
```

and:

```text
scope_identity.status == NOT_EVALUATED
+ canonical_collected_test_ids
```

V2 also enforces:

```text
scope_identity.status == NOT_EVALUATED
-> result_identity.status == NOT_EVALUATED
```

This is accepted.

### Policy Action Semantics Version

V2 requires:

```text
expected_policy_action.decision_semantics_version
```

and constrains it to:

```text
SPIRA_DECISION_SEMANTICS_V2
```

This is accepted.

### Validator-Required Rules

V2 explicitly classifies the following as validator-enforced before oracle
population:

```text
RELATED_CASE_ID_EXISTS
IDENTITY_RELATIONSHIP_SYMMETRY
CANONICAL_ARRAY_SORTING
CASE_ID_UNIQUENESS
DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY
```

This classification is accepted as long as oracle population remains blocked
until such a validator is separately authorized and reviewed.

## Blocking Finding 1 - Scope Identity Has No Own Digest Or Projection

`expected_scope_identity` currently includes:

```text
status
collection_deterministic
collection_manifest_sha256
canonical_collected_test_ids
reason_codes
```

but it does not include:

```text
scope_identity_sha256
scope_projection
scope_projection_sha256
```

At the same time, `result_identity_projection` requires:

```text
scope_identity_sha256
```

This creates an oracle consistency gap. A case can state the scope hash inside
the result projection without providing a corresponding expected scope identity
digest or projection to compare against.

Required revision:

```text
expected_scope_identity.status == EMITTED
-> scope_identity_sha256 required
-> either scope_projection or scope_projection_sha256 required
```

At minimum, schema V3 must define how:

```text
expected_result_identity.projection.scope_identity_sha256
```

is checked against:

```text
expected_scope_identity
```

If JSON Schema cannot enforce the cross-field equality, the equality check must
be declared as validator-enforced before oracle population.

## Blocking Finding 2 - EMITTED Result Identity Can Still Represent Incomplete Or Invalid Evidence

When:

```text
expected_result_identity.status == EMITTED
```

V2 requires:

```text
result_identity_sha256
projection
```

but it does not require the projection to be semantically identity-eligible.

The schema still permits:

```text
evidence_completeness: INCOMPLETE
```

or:

```text
evidence_completeness: CONFLICTING
```

or:

```text
evidence_completeness: UNSUPPORTED
```

It also permits:

```text
process_state: NOT_EVALUATED
result_state: NOT_EVALUATED
result_state: CONFLICTING
result_state: UNSUPPORTED
```

inside an emitted result identity projection.

This contradicts the identity model requirement that no `result_identity` is
emitted when the result cannot be evaluated from sufficient deterministic
evidence.

Required revision:

```text
result_identity.status == EMITTED
-> projection.evidence_completeness == COMPLETE
-> projection.process_state != NOT_EVALUATED
-> projection.result_state not in NOT_EVALUATED / CONFLICTING / UNSUPPORTED
```

If an unsupported, conflicting, incomplete, or not-evaluated input is observed,
the case may still have policy action such as:

```text
RERUN_REQUIRED
REPORT_NOT_EVALUATED
STOP_BLOCKED
```

but it must not emit `result_identity`.

## Additional Required Validator Invariant

V2 should also classify action consistency as validator-enforced or schema
enforced.

At minimum, before oracle population a validator must reject contradictions
such as:

```text
stop: false
recommended_agent_action: STOP_BLOCKED
```

and:

```text
stop: false
recommended_agent_action: RERUN_REQUIRED
```

The exact rule may be documented as:

```text
ACTION_STOP_CONSISTENCY
```

This is not a producer feature. It is an oracle-validity invariant.

## Required Next Artifact

The next artifact should be a schema revision:

```text
research/test_build_failure_contract_oracle_schema_v3.schema.json
```

It must at minimum:

```text
1. Add scope_identity_sha256 and a scope projection/hash contract.
2. Define how result projection scope_identity_sha256 is checked.
3. Require EMITTED result_identity to use COMPLETE evidence.
4. Reject NOT_EVALUATED / CONFLICTING / UNSUPPORTED result states for emitted result_identity.
5. Classify ACTION_STOP_CONSISTENCY as schema-enforced or validator-enforced.
6. Keep oracle population blocked.
```

## Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V2_NEEDS_REVISION
ORACLE_SCHEMA_V2_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle Schema V2 fixes the V1 fail-closed holes, but it is not accepted until
scope identity has a verifiable identity contract and emitted result identities
are restricted to complete, evaluable result projections.
