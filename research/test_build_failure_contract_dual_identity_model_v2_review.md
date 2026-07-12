# Test/Build Failure Contract - Dual Identity Model V2 Review

## Status

```text
DOMAIN_2_DUAL_IDENTITY_MODEL_V2_ACCEPTED
MODEL_V2_REVIEW_COMPLETE
ORACLE_SCHEMA_UPDATE_AUTHORIZED_NEXT
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed document:

```text
research/test_build_failure_contract_dual_identity_model_v2.md
```

Reviewed commit:

```text
cdc588ff995ba0dde476e64d64b2f10b184bbd21
```

## Review Scope

This review determines whether Dual Identity Model V2 resolves the blocking
finding from:

```text
research/test_build_failure_contract_dual_identity_model_review.md
```

It does not authorize:

```text
Domain 2 producer
pytest adapter
oracle population
corpus materialization
Gate B
Domain 3
release/version/tag/PyPI
```

## Decision Reviewed

V2 chooses:

```text
Policy-Independent Result Identity
```

This resolves the V1 ambiguity by separating:

```text
observed pytest result semantics
```

from:

```text
policy-derived action
```

## Accepted Identity Model

### Run Identity

`run_identity` remains contextual.

It binds the exact evidence context:

```text
source bytes
source hashes
command
environment
timestamps or declared run context
source revision
selection scope
collection manifest
policy/context roots
decision semantics
```

This remains aligned with the existing contextual `unification_id` model.

The review accepts:

```text
unification_id semantics unchanged
run_identity contextual
policy/context changes may change run_identity
```

### Result Identity

`result_identity` now identifies only the normalized observed pytest result.

It includes:

```text
scope_identity
process_state
result_state
blocking_cases
nonblocking_cases
failure_classes
run_level_failures
evidence completeness state
```

It explicitly excludes:

```text
policy
decision semantics
stop
recommended_agent_action
reason_codes
```

The review accepts this separation.

Required consequence:

```text
same normalized pytest result + different policy
-> same result_identity
-> action may change outside result_identity
-> run_identity / proof identity may change
```

## Preservation Of V1 Corrections

The review confirms that V2 preserves the corrections accepted in the V1
review.

### Timeout Semantics

V2 keeps per-test timeout and run-level timeout separate:

```text
per-test timeout -> process_state COMPLETED + case-level TIMEOUT
run-level timeout -> process_state TIMEOUT + run-level failure TIMEOUT
```

This is accepted.

### Explicit Non-Passing Outcomes

V2 keeps the following outcomes identity-bearing:

```text
SKIPPED
XFAILED
XPASSED_BLOCKING
XPASSED_NONBLOCKING
```

Counts remain derived from explicit sorted unique lists. A count without its
list remains invalid.

This is accepted.

### Declared Deltas Only

V2 preserves declared-delta fixture rules and rejects vague claims such as:

```text
irrelevant log noise
cosmetic-only change
```

This is accepted.

### Collection Determinism

V2 preserves deterministic collection as a precondition for:

```text
scope_identity
result_identity
semantic equivalence claims
cache or reuse decisions
```

When collection is not deterministic, V2 remains fail-closed:

```text
scope_identity_status: NOT_EVALUATED
result_identity_status: NOT_EVALUATED
reason_code: TEST_COLLECTION_IDENTITY_NOT_DETERMINISTIC
```

This is accepted.

## Oracle Implications

The oracle schema may now distinguish:

```text
run_identity expectations
result_identity expectations
policy/action expectations
```

The oracle must encode at least these identity consequences:

```text
same bytes + same scope + same result
-> same run_identity
-> same result_identity

declared contextual bytes change + same scope + same semantic result
-> different run_identity
-> same result_identity

same normalized result + different policy
-> same result_identity
-> action may differ outside result_identity

changed blocking outcome
-> different result_identity

FAIL -> SKIPPED
-> different result_identity

FAIL -> XFAILED
-> different result_identity

same collected set in different order
-> same scope_identity

different collected set under same pinned scope
-> scope NOT_EVALUATED
-> no result_identity
```

The oracle must not include action, stop, decision semantics, or reason codes
inside the expected `result_identity` projection.

## Remaining Boundaries

Accepted V2 does not authorize implementation.

Still not authorized:

```text
Domain 2 producer
pytest adapter
oracle population
corpus materialization
Gate B
Domain 3
release/version/tag/PyPI
```

The next authorized artifact is an oracle schema update only.

That artifact may define expected fields and review gates, but it must not
populate oracle cases from producer output and must not authorize producer code.

## Verdict

```text
DOMAIN_2_DUAL_IDENTITY_MODEL_V2_ACCEPTED
MODEL_V2_REVIEW_COMPLETE
ORACLE_SCHEMA_UPDATE_AUTHORIZED_NEXT
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Dual Identity Model V2 resolves the V1 blocking finding.

`result_identity` is now a policy-independent identity of the normalized pytest
result, while policy-derived action remains outside that identity and is bound
by the existing proof/action contracts.
