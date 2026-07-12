# Test/Build Failure Contract - Dual Identity Model V1

## Status

```text
DOMAIN_2_DUAL_IDENTITY_MODEL_V1_LOCKED
NO_PRODUCER_IMPLEMENTATION_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

This document resolves the Domain 2 identity-model question as a versioned
design artifact.

It does not silently amend:

```text
research/test_build_failure_contract_methodology.md
research/test_build_failure_contract_identity_model_question.md
```

The methodology remains historically locked. This document adds a separate
identity model that must be reviewed before any Domain 2 producer, oracle
population, or corpus materialization begins.

## Identity Model Decision

Domain 2 uses a dual identity model:

```text
run_identity
result_identity
```

### Run Identity

`run_identity` is contextual.

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

It answers:

```text
Was this exact evidence context used to produce this action?
```

This is aligned with the existing contextual `unification_id` model. The
meaning of `unification_id` is not changed by this document.

### Result Identity

`result_identity` is semantic.

It binds only the normalized, policy-relevant test result facts admitted by this
contract:

```text
scope identity
process state
result state
blocking cases
nonblocking cases
run-level failures
decision/action
reason codes
```

It answers:

```text
Did these normalized test/build facts produce this action?
```

`result_identity` is a separate identity. It must not be implemented by
changing the meaning of `unification_id`.

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

## Amendment 1 - Distinguish Per-Test Timeout From Run-Level Timeout

Timeout semantics are explicit and non-overlapping.

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

## Amendment 2 - Preserve Explicit Non-Passing Outcomes

The V1 semantic projection must not silently discard `SKIPPED` or `XFAILED`.

The case-result representation is split into two explicit lists:

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
skip, xfail, or xpass is acceptable under a future project policy.

## Amendment 3 - Replace Unqualified Noise With Declared Deltas

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

## Amendment 4 - Collection Identity Determinism

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

The oracle must now cover at least:

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
```

## Not Authorized

This document does not authorize:

```text
Domain 2 producer
pytest adapter
oracle population
corpus materialization
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
identity-model document review
oracle schema update
fixture-pair and corpus lock
separate review
separate producer authorization
```

No producer code may begin before the separate producer authorization.

## Final Status

```text
Domain 2 identity model:
DUAL IDENTITY MODEL V1

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
