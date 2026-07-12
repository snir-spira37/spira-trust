# Test/Build Failure Contract - Dual Identity Model V2

## Status

```text
DOMAIN_2_POLICY_INDEPENDENT_RESULT_IDENTITY_LOCKED
DUAL_IDENTITY_MODEL_V2_LOCKED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

This document revises:

```text
research/test_build_failure_contract_dual_identity_model.md
```

It responds to:

```text
research/test_build_failure_contract_dual_identity_model_review.md
```

The V1 model mixed observed test-result semantics with policy-derived action
inside `result_identity`. V2 chooses the review's Option A:

```text
Policy-Independent Result Identity
```

No producer, oracle population, corpus materialization, Gate B work, release,
version bump, tag, or PyPI publication is authorized by this document.

## Decision

Domain 2 uses two identities:

```text
run_identity
result_identity
```

`run_identity` remains contextual.

`result_identity` is policy-independent.

The existing contextual `unification_id` semantics remain unchanged.

## Run Identity

`run_identity` binds the exact evidence context:

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

It answers:

```text
Was this exact evidence context used?
```

Different contextual evidence must produce a different `run_identity` even when
the normalized test result is unchanged.

Examples:

```text
same semantic test result + different timestamp bytes
-> different run_identity

same semantic test result + different command fingerprint
-> different run_identity

same semantic test result + different policy/context roots
-> different run_identity
```

## Result Identity

`result_identity` identifies the normalized observed test result itself.

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

It excludes:

```text
policy
decision semantics
stop
recommended_agent_action
reason_codes
```

It answers:

```text
Did these normalized pytest-result facts recur?
```

Under this model:

```text
same normalized test result + different policy
-> same result_identity
-> action may change
-> run_identity / proof identity may change
```

This is the required separation:

```text
observed test result
!= policy-derived action
```

## Policy-Derived Action Is Bound Elsewhere

Policy-derived action remains bound by the existing SPIRA action and proof
contracts:

```text
stop
recommended_agent_action
reason_codes
decision semantics
unification_id
proof identity
```

Those values must not be smuggled into `result_identity`.

If a future design needs a combined identity for:

```text
normalized result + policy + action
```

it must introduce a separate, explicitly named, reviewed field such as:

```text
policy_result_identity
```

That field is not authorized by V2.

## Scope Identity Precondition

No `result_identity` may be emitted without a valid deterministic
`scope_identity`.

If scope identity cannot be established:

```text
scope_identity_status: NOT_EVALUATED
result_identity_status: NOT_EVALUATED
reason_code: TEST_COLLECTION_IDENTITY_NOT_DETERMINISTIC
```

In that case:

```text
no scope_identity is emitted
no result_identity is emitted
no semantic equivalence claim is allowed
no cache or reuse decision is allowed
```

## Timeout Semantics

Timeout semantics remain explicit and non-overlapping.

### Per-Test Timeout

```text
The pytest process completes and emits a complete result.
process_state remains COMPLETED.
The timed-out test appears in the case-result projection.
outcome is ERROR.
failure_class is TIMEOUT.
The canonical test ID is required.
```

### Run-Level Timeout

```text
The pytest process itself does not complete normally because the run-level
time limit is reached.
process_state is TIMEOUT.
result_state is ERROR.
run_level_failures contains TIMEOUT.
No individual test is identified as the timed-out case unless the evidence
explicitly and deterministically establishes that identity.
```

A run-level timeout may receive a `result_identity` only when:

```text
scope identity is established
the timeout event is conclusively established
the available evidence is sufficient for the closed gate result
no incomplete blocking-case set is represented as complete
```

Otherwise:

```text
result_identity_status: NOT_EVALUATED
reason_code: TEST_RESULT_EVIDENCE_INCOMPLETE
```

Required mutation behavior:

```text
individual failure -> per-test timeout
= semantic mutation
= result_identity must change

completed result -> run-level timeout
= process-state mutation
= result_identity must change
```

## Explicit Non-Passing Outcomes

The semantic projection must not silently discard:

```text
SKIPPED
XFAILED
```

Case results are represented with:

```json
{
  "blocking_cases": [],
  "nonblocking_cases": []
}
```

### Blocking Cases

Permitted observed outcomes:

```text
FAILED
ERROR
XPASSED_BLOCKING
```

`XPASSED_BLOCKING` may be used only when pytest explicitly classifies the
unexpected pass as a failing result under the captured run configuration.

### Nonblocking Cases

Permitted observed outcomes:

```text
SKIPPED
XFAILED
XPASSED_NONBLOCKING
```

Every entry must contain:

```text
canonical test_id
observed outcome
explicit reason category when deterministically available
```

Free-text skip or xfail reasons do not enter the identity.

Passing tests remain omitted from the semantic projection.

Required rules:

```text
FAIL -> SKIPPED
= result_identity changes

FAIL -> XFAILED
= result_identity changes

SKIPPED -> XFAILED
= result_identity changes

SKIPPED test disappears from the collected set
= scope_identity changes

same skipped/xfailed identities in different report order
= result_identity remains stable
```

Counts, when exposed, are derived only from the corresponding explicit sorted
unique lists:

```text
failed_count == len(failed IDs)
error_count == len(error IDs)
skipped_count == len(skipped IDs)
xfailed_count == len(xfailed IDs)
xpassed_count == len(xpassed IDs)
```

A count without its required explicit list is invalid.

This model records observed test-result semantics. It does not decide whether a
skip, xfail, or xpass is acceptable under project policy.

## Declared Deltas Only

Unqualified phrases such as the following must not appear in mutation
requirements unless the exact mutation is declared:

```text
irrelevant log noise
cosmetic-only change
```

Every paired Quadrant B or Quadrant D fixture must contain:

```json
{
  "pair_id": "...",
  "base_case_id": "...",
  "mutated_case_id": "...",
  "declared_input_deltas": [
    {
      "source": "console",
      "delta_type": "TIMESTAMP_CHANGED",
      "description": "Only the displayed run timestamp differs"
    }
  ],
  "expected_run_identity_relation": "DIFFERENT",
  "expected_result_identity_relation": "SAME"
}
```

Permitted predeclared delta classes may include:

```text
TIMESTAMP_CHANGED
DURATION_CHANGED
PID_CHANGED
ANSI_FORMATTING_CHANGED
WHITESPACE_CHANGED
TEMP_PATH_CHANGED
TRACEBACK_FORMATTING_CHANGED
CONSOLE_ORDER_CHANGED
UNRELATED_STDOUT_ADDED
UNRELATED_STDERR_ADDED
```

Each delta class must define precisely which semantic fields it is forbidden to
change.

Required principle:

```text
The experiment does not prove that "noise" is irrelevant.

It proves that the specifically declared mutations did not change the
normalized semantic result under the locked identity contract.
```

A pair containing an undeclared delta is invalid for identity evaluation.

If a declared cosmetic mutation changes a semantic projection field:

```text
IDENTITY_FIXTURE_CLASSIFICATION_ERROR
```

The case is reviewed. The oracle is not silently rewritten.

## Collection Identity Determinism

The collected-test-set identity must be independently proven deterministic
within the pinned scope.

Canonical collection manifest:

```text
schema
schema_version
project identity
source revision
normalized selection command
sorted unique canonical collected test IDs
Python version contract
pytest version
relevant plugin contract
collection-contract version
```

Collection ordering is not identity-bearing.

The collected IDs are normalized under the locked canonical test-ID rules,
sorted, and deduplicated before hashing.

Required collection digest:

```text
collection_manifest_sha256 =
SHA256(
  "SPIRA_PYTEST_COLLECTION_MANIFEST_V1\0"
  + UTF8(canonical_json(collection_manifest))
)
```

### Determinism Gate

For designated corpus cases, collection must be repeated under the same pinned
scope.

Expected:

```text
same canonical collected-test set
same collection_manifest_sha256
```

A different raw ordering with the same canonical set is permitted.

Any unexplained difference in membership or canonical test identity produces:

```text
scope_identity_status: NOT_EVALUATED
reason_code: TEST_COLLECTION_IDENTITY_NOT_DETERMINISTIC
```

When collection identity is not deterministic:

```text
no scope_identity is emitted
no result_identity is emitted
no semantic equivalence claim is allowed
no cache or reuse decision is allowed
```

The producer must not stabilize collection heuristically by:

```text
dropping parameter values
removing unstable IDs
matching tests by similarity
ignoring missing or added tests
rewriting plugin-generated identities
```

The frozen corpus must include:

```text
dynamic parameterized IDs
plugin-dependent collection
collection-order variation
collection-membership instability
duplicate collected IDs
Unicode collected IDs
Windows/Linux path normalization
```

Required distinction:

```text
same members, different order
-> deterministic collection
-> same scope_identity

different members or canonical IDs under the same pinned scope
-> nondeterministic collection
-> scope NOT_EVALUATED
```

## Updated Mutation Matrix Requirements

The oracle must cover at least:

```text
1. Identical bytes, identical scope, identical result
   -> same run_identity
   -> same result_identity

2. Different declared contextual bytes, identical scope and semantic result
   -> different run_identity
   -> same result_identity

3. Changed blocking outcome
   -> different run_identity
   -> different result_identity

4. FAIL -> SKIPPED
   -> different result_identity

5. FAIL -> XFAILED
   -> different result_identity

6. Per-test timeout
   -> blocking case TIMEOUT
   -> process_state COMPLETED

7. Run-level timeout
   -> process_state TIMEOUT
   -> run-level failure TIMEOUT

8. Same collected set in different order
   -> same scope_identity

9. Different collected set under the same pinned scope
   -> scope NOT_EVALUATED

10. Scope revision or selection mutation
    -> different scope_identity
    -> different result_identity

11. Same normalized result under different policy
    -> same result_identity
    -> action may differ outside result_identity
```

## Updated Acceptance Gates

```text
100% correct distinction between per-test and run-level timeout
100% preservation of explicit SKIPPED and XFAILED identity lists
100% declared-delta coverage for Quadrant B and D pairs
0 undeclared-delta pairs accepted
100% collection-order invariance
100% detection of collection-membership nondeterminism
0 result_identity values emitted without a valid deterministic scope_identity
100% exclusion of policy/action/reason_codes from result_identity
100% stability of result_identity across policy-only changes
```

## Not Authorized

This document does not authorize:

```text
Domain 2 producer
pytest adapter
oracle population
corpus materialization
semantic identity implementation
policy_result_identity field
Gate B
Domain 3
release/version/tag/PyPI
```

It also does not authorize changing:

```text
unification_id semantics
agent action enum
claim status enum
SPIRA_DECISION_SEMANTICS_V2
Gate A proof assembler
Domain 1 identity baseline
```

## Required Next Steps

After this document is committed, the order remains:

```text
dual identity model V2 review
oracle schema update
fixture-pair and corpus lock
separate review
separate producer authorization
```

No producer code may begin before the separate producer authorization.

## Final Status

```text
Domain 2 identity model:
DUAL IDENTITY MODEL V2

Result identity:
POLICY-INDEPENDENT

Policy-derived action:
BOUND OUTSIDE RESULT_IDENTITY

Timeout semantics:
EXPLICITLY DISAMBIGUATED

Skipped and xfailed outcomes:
IDENTITY-BEARING AND EXPLICIT

Cosmetic mutation claims:
DECLARED-DELTAS ONLY

Collection identity:
DETERMINISM REQUIRED

Gate B:
NOT AUTHORIZED

Domain 2 producer:
NOT AUTHORIZED

Oracle population:
NOT AUTHORIZED

Corpus materialization:
NOT AUTHORIZED
```
