# Test/Build Failure Contract - Dual Identity Model Review

## Status

```text
DOMAIN_2_DUAL_IDENTITY_MODEL_NEEDS_REVISION
MODEL_REVIEW_COMPLETE
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
```

Reviewed document:

```text
research/test_build_failure_contract_dual_identity_model.md
```

Reviewed commit:

```text
50ba87f2d5cb3fb8b2a5f60d7b48736d3bafb794
```

## Review Scope

This review checks whether the locked Dual Identity Model V1 is ready to
support the next artifact:

```text
oracle schema update
```

It does not authorize:

```text
Domain 2 producer
pytest adapter
oracle population
corpus materialization
Gate B
release/version/tag/PyPI
```

## Accepted Elements

The review accepts the four corrections added by the Dual Identity Model V1.

### Timeout Disambiguation

The model correctly separates:

```text
per-test timeout
run-level timeout
```

This avoids treating a completed pytest run with one timed-out test as the same
semantic event as a pytest process that failed to complete because the run-level
timeout fired.

### Explicit Non-Passing Outcomes

The model correctly makes the following outcomes identity-bearing:

```text
SKIPPED
XFAILED
XPASSED_BLOCKING
XPASSED_NONBLOCKING
```

It also correctly requires counts to derive from explicit sorted unique lists.
A count without the corresponding list is invalid.

### Declared Deltas Only

The model correctly rejects vague labels such as:

```text
irrelevant log noise
cosmetic-only change
```

Each fixture pair must declare the exact delta class being tested. The result
then proves only that the declared mutation did not change the normalized
semantic result under the locked identity contract.

### Collection Determinism

The model correctly requires deterministic collection identity before emitting:

```text
scope_identity
result_identity
semantic equivalence claims
cache or reuse decisions
```

If collection membership or canonical test IDs change under the same pinned
scope, the model fails closed:

```text
scope_identity_status: NOT_EVALUATED
reason_code: TEST_COLLECTION_IDENTITY_NOT_DETERMINISTIC
```

## Blocking Finding

### Result Identity Currently Mixes Test Semantics With Policy Decision

The reviewed model defines `result_identity` as semantic, but includes:

```text
decision/action
reason codes
```

It also describes the identity question as:

```text
Did these normalized test/build facts produce this action?
```

This makes `result_identity` depend on policy and decision mapping.

Example:

```text
same normalized test result
+ different policy
-> different action
-> different result_identity
```

That is a valid identity model only if the intended identity is a combined
policy-result identity. It is not a clean semantic identity for the observed
test result itself.

## Required Revision

Before oracle schema work, the model must choose exactly one of the following.

### Option A - Policy-Independent Result Identity

`result_identity` identifies the normalized test result itself.

It includes:

```text
scope_identity
process_state
result_state
blocking_cases
nonblocking_cases
failure_classes
run_level_failures
```

It excludes:

```text
policy
decision semantics
stop
recommended_agent_action
reason_codes
```

Under this model:

```text
same normalized test result + different policy
-> same result_identity
-> action may change
-> run_identity / proof identity may change
```

This option preserves a clean separation between observed test-result semantics
and policy-derived action.

### Option B - Policy Result Identity

The model may intentionally identify the combination of:

```text
normalized test result
policy / decision semantics
action
reason codes
```

If this option is chosen, the field should not be called plain
`result_identity` without qualification. It should be renamed or explicitly
scoped, for example:

```text
policy_result_identity
```

Under this model:

```text
same normalized test result + different policy
-> different policy_result_identity
```

This option is valid only if the document states that the identity is for a
policy-mediated result, not for the test result alone.

## Non-Negotiable Guardrails

Any revision must preserve:

```text
run_identity remains contextual
unification_id semantics remain unchanged
scope_identity remains required before result identity
collection nondeterminism remains fail-closed
SKIPPED / XFAILED remain identity-bearing
timeout disambiguation remains explicit
declared-delta requirements remain mandatory
```

The revision must not silently authorize:

```text
producer implementation
oracle population
corpus materialization
Gate B
Domain 3
```

## Why This Blocks Oracle Work

The oracle schema must know what a stable identity is allowed to include.

If action and reason codes are included in `result_identity`, oracle fixtures
must expect result identity to change when policy changes.

If action and reason codes are excluded, oracle fixtures must expect the
semantic result identity to remain stable across policy changes, while the
proof/action identity changes elsewhere.

Both models can be valid. Mixing them would make fixture expectations
ambiguous.

## Required Next Artifact

The next artifact should be a revision of the identity model, not producer code:

```text
research/test_build_failure_contract_dual_identity_model_v2.md
```

The V2 document must end with one of:

```text
DOMAIN_2_POLICY_INDEPENDENT_RESULT_IDENTITY_LOCKED
DOMAIN_2_POLICY_RESULT_IDENTITY_LOCKED
DOMAIN_2_IDENTITY_MODEL_NEEDS_REVISION
```

Only after that document is reviewed and accepted may oracle schema work begin.

## Verdict

```text
DOMAIN_2_DUAL_IDENTITY_MODEL_NEEDS_REVISION
MODEL_REVIEW_COMPLETE
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
```

The four requested corrections are present and accepted.

The model is not yet accepted because `result_identity` must explicitly choose
whether it is policy-independent test-result identity or policy-mediated result
identity.
