# Test/Build Failure Contract Oracle Final Review

Status:

```text
DOMAIN_2_ORACLE_ACCEPTED
ORACLE_FINAL_REVIEW_COMPLETE
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
PYTEST_ADAPTER_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed revision:

```text
2efe227 Revise Domain 2 oracle
DOMAIN_2_ORACLE_REVISED
```

Accepted prior gates:

```text
Dual Identity Model V2: ACCEPTED
Oracle Schema V7: ACCEPTED
Oracle Validator Spec: ACCEPTED
Oracle Validator Implementation: ACCEPTED
Domain 2 corpus: ACCEPTED
Oracle population: COMPLETE, mechanically valid, semantically revised
```

This review evaluates whether the revised Domain 2 oracle is acceptable as the
expected-answer set for the frozen 38-case Test/Build Failure Contract corpus.
It does not authorize producer implementation, pytest adapter implementation,
Gate B, Domain 3, schema changes, corpus changes, or release activity.

## Review Inputs

Reviewed files:

```text
research/test_build_failure_contract/oracle_v1.json
research/test_build_failure_contract/oracle_population_report.md
research/test_build_failure_contract/oracle_population_results.json
tools/populate_test_build_failure_oracle.py
```

Frozen inputs preserved:

```text
Corpus case count: 38
Synthetic cases: 30
Public materialized cases: 8
Mutation pairs: 6
Schema: SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
Decision semantics: SPIRA_DECISION_SEMANTICS_V2
Producer output observed: false
```

Mechanical validation:

```text
Schema V7: PASS
Accepted validator: PASS
Validator errors: 0
Relationship count: 12
Declared delta count: 6
```

## Finding 1: Classification Source

Verdict:

```text
CLOSED
```

The revised population tool no longer uses `case_kind` as the answer key for
classification. Expected answers are derived from frozen evidence available in
the corpus:

```text
console evidence
JUnit XML evidence
exit-code evidence
metadata evidence
public_run_materialization records
declared mutation pairs
```

The public cases with withheld raw console/JUnit outputs are handled
fail-closed:

```text
expected_result_identity.status: NOT_EVALUATED
recommended_agent_action: REPORT_NOT_EVALUATED
reason_codes: ["PUBLIC_RUN_OUTPUT_WITHHELD"]
```

This is correct. The oracle does not infer semantic test results from public
case names such as `requests_clean`, nor from exit code alone when the raw
console/JUnit evidence is not available in the committed corpus.

## Finding 2: Evidence Conflict Decision

Verdict:

```text
CLOSED
```

The conflict case is now mapped according to the locked decision table:

```text
case_id: synthetic_console_junit_conflict
expected_result_identity.status: NOT_EVALUATED
recommended_agent_action: RERUN_REQUIRED
reason_codes: ["TEST_EVIDENCE_CONFLICT"]
```

The rejected mapping is no longer used for this case:

```text
STOP_BLOCKED + TEST_FAILURE
```

This preserves the fail-closed posture for contradictory evidence. A
console/JUnit disagreement is not treated as an ordinary package test failure.

## Finding 3: Identity Relationships

Verdict:

```text
CLOSED
```

The revised oracle no longer marks every mutation relationship as fully
different. The six mutation pairs now follow the accepted dual-identity model.

Factual mutations:

```text
run_identity_relation: DIFFERENT
scope_identity_relation: SAME
result_identity_relation: DIFFERENT
```

Contextual or cosmetic declared deltas:

```text
TRACEBACK_FORMATTING_CHANGED
TEMP_PATH_CHANGED
UNRELATED_STDOUT_ADDED

run_identity_relation: DIFFERENT
scope_identity_relation: SAME
result_identity_relation: SAME
```

This correctly separates exact contextual run identity from normalized
policy-independent result identity. It also preserves declared deltas instead
of using an unbounded "noise" category.

## Finding 4: Sufficiency And Collection

Verdict:

```text
CLOSED
```

The revised oracle sets `expected_source_sufficiency` per source and per case.
It distinguishes:

```text
ANSWERED
NOT_APPLICABLE
NOT_EVALUATED
CONFLICTING
```

The reviewed edge cases are handled as follows:

```text
truncated console / incomplete evidence
-> TEST_RESULT_EVIDENCE_INCOMPLETE

malformed or insufficient JUnit evidence
-> TEST_RESULT_EVIDENCE_INCOMPLETE

console/JUnit contradiction
-> CONFLICTING source sufficiency
-> RERUN_REQUIRED

public raw outputs withheld
-> console/JUnit NOT_EVALUATED
-> result_identity NOT_EVALUATED
```

Collection determinism is evaluated from explicit scope inputs and available
evidence rather than being used as an unexamined answer-key shortcut. For the
accepted corpus, emitted scopes remain deterministic under Schema V7.

## Validation Evidence

The revised oracle reports:

```text
DOMAIN_2_ORACLE_REVISED
38 / 38 cases
Schema V7: PASS
Accepted validator: PASS
identity recomputation: PASS
explicit list validation: PASS
mutation relationship validation: PASS
NOT_EVALUATED validation: PASS
validator errors: 0
producer_output_observed: false
```

The validator result is necessary but not sufficient for acceptance. This
review separately confirms that the four semantic review findings were
addressed without changing the corpus, Schema V7, validator, or producer
boundary.

## Acceptance Boundary

Accepted:

```text
The Domain 2 oracle is accepted as the expected-answer set for the frozen
38-case Test/Build Failure Contract corpus.
```

Not claimed:

```text
The future producer is correct.
The pytest adapter exists.
The public withheld raw outputs have semantic result identities.
Gate B reuse/cache behavior is authorized.
Domain 3 is authorized.
The oracle proves software safety.
```

This acceptance authorizes only a future discussion of producer implementation
authorization. It does not itself authorize implementation.

## Final Verdict

```text
DOMAIN_2_ORACLE_ACCEPTED
ORACLE_FINAL_REVIEW_COMPLETE
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
PYTEST_ADAPTER_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```
