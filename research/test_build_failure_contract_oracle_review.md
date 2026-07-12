# Test/Build Failure Contract Oracle Review

Status:

```text
DOMAIN_2_ORACLE_NEEDS_REVISION
ORACLE_REVIEW_COMPLETE
DOMAIN_2_ORACLE_POPULATED_PRESERVED
ORACLE_VALIDATION_PASS_PRESERVED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed oracle population commit:

```text
498c4f7 Populate Domain 2 oracle
```

Population status under the mechanical gates:

```text
DOMAIN_2_ORACLE_POPULATED
38 / 38 cases populated
Schema V7: PASS
Accepted validator: PASS
identity recomputation: PASS
explicit lists: PASS
relationships: 12
declared deltas: 6
validator errors: 0
producer_output_observed: false
```

This review preserves the formal success of the population step. The finding is
not that Schema V7 or the accepted validator failed. The finding is that the
oracle is not yet semantically accepted as the expected truth set for a future
producer benchmark.

## Review Question

The review asks whether the populated expected answers are justified by the
frozen evidence and the locked methodology.

It does not ask whether the JSON is well formed. That was already checked by
Schema V7 and the validator.

## Verdict

```text
DOMAIN_2_ORACLE_NEEDS_REVISION
```

The oracle is mechanically consistent but needs a semantic revision before it
can be accepted as the expected-answer set for Domain 2.

## Finding 1: Oracle Classification Source Risk

```text
ORACLE_CLASSIFICATION_SOURCE_RISK
```

The population tool classifies cases primarily from:

```text
case_kind
exit_code
```

The `case_kind` field is useful corpus metadata, but it must not become a
hidden expected-answer channel. A future producer will be evaluated against the
oracle, so the oracle must be authorable from frozen evidence rather than from
a label that already encodes the intended result.

Examples of classification inputs in the population tool include:

```text
kind = case["case_kind"]
exit_code = int(case.get("exit_code", 0))
```

This is not automatically invalid, but the oracle review cannot accept it
without an explicit evidence derivation showing that each expected answer is
grounded in console/JUnit/exit-code evidence and not merely in the case label.

Required revision:

```text
expected answers must be derived from evidence fields
case_kind may be used only as review metadata
any use of case_kind as an oracle hint must be removed or justified per case
```

## Finding 2: Evidence Conflict Decision Mismatch

```text
EVIDENCE_CONFLICT_DECISION_MISMATCH
```

The locked methodology defines conflicting test evidence as a rerun-required
condition:

```text
recommended_agent_action: RERUN_REQUIRED
reason_codes:
  - TEST_EVIDENCE_CONFLICT
```

The populated oracle currently classifies the synthetic console/JUnit conflict
as:

```text
recommended_agent_action: STOP_BLOCKED
reason_codes:
  - TEST_FAILURE
```

This is a direct mismatch with the locked decision table. A console/JUnit
conflict is not merely a failing test; it is an evidence integrity problem that
requires rerun or regeneration.

Required revision:

```text
synthetic_console_junit_conflict
-> RERUN_REQUIRED
-> TEST_EVIDENCE_CONFLICT
```

The expected result identity may also need to represent the conflict as
not-evaluated or rerun-required according to the accepted identity model and
validator constraints.

## Finding 3: Identity Relationship Mismatch

```text
IDENTITY_RELATIONSHIP_MISMATCH
```

The population tool assigns all declared mutation pairs:

```text
run_identity_relation: DIFFERENT
scope_identity_relation: DIFFERENT
result_identity_relation: DIFFERENT
```

This is too broad for declared contextual or cosmetic deltas.

For mutation pairs such as:

```text
TRACEBACK_FORMATTING_CHANGED
TEMP_PATH_CHANGED
UNRELATED_STDOUT_ADDED
```

the contextual run identity may change, but the semantic result identity should
not automatically change. If the collected test scope is unchanged, the
`scope_identity` should also remain `SAME`.

The dual identity model was introduced exactly to avoid treating contextual
input drift as semantic result drift.

Required revision:

```text
derive identity relationships per mutation pair
do not default contextual/cosmetic deltas to result_identity: DIFFERENT
use result_identity: SAME when normalized result semantics are unchanged
use scope_identity: SAME when collection scope is unchanged
```

If a pair truly changes the semantic result, the oracle must explain that
change from the evidence and declared mutation, not from a blanket default.

## Finding 4: Sufficiency And Collection Assumed

```text
SUFFICIENCY_AND_COLLECTION_ASSUMED
```

The populated oracle currently sets:

```text
expected_source_sufficiency: ANSWERED
collection_deterministic: true
```

for every case.

The methodology requires source sufficiency to distinguish:

```text
ANSWERED
NOT_APPLICABLE
NOT_EVALUATED
CONFLICTING
```

and the identity model requires collection determinism to be established, not
assumed by default.

This matters especially for:

```text
truncated console evidence
malformed or incomplete JUnit evidence
console/JUnit conflict evidence
withheld public raw outputs represented only by hashes
non-derivable rerun target evidence
```

Required revision:

```text
set source sufficiency per source and per case
mark conflicting sources as CONFLICTING
mark irrelevant sources as NOT_APPLICABLE
mark insufficient sources as NOT_EVALUATED
justify collection_deterministic per case from the corpus evidence
```

If collection cannot be determined for a case, the oracle must fail closed
instead of emitting a scope identity.

## Preserved Success

This review explicitly preserves:

```text
DOMAIN_2_ORACLE_POPULATED
Schema V7 validation: PASS
Accepted validator: PASS
identity recomputation: PASS
explicit lists: PASS
mutation relationship validation: PASS under current oracle contents
```

The revision is required because validator pass is not the same as semantic
oracle acceptance.

## Required Revision Scope

The next revision must be limited to the oracle and its population logic:

```text
fix expected answers
fix conflict decision/action mapping
fix identity relationships
fix source sufficiency states
fix collection determinism states
rerun Schema V7 validation
rerun accepted validator
update oracle_population_report.md
update oracle_population_results.json
```

The revision must not:

```text
change the corpus
replace cases
change Schema V7
change the accepted validator
use producer output
build a producer
build a pytest adapter
start Gate B
```

## Still Not Authorized

```text
producer implementation
pytest adapter implementation
Gate B status/cache/rerun work
Domain 3 work
corpus replacement
schema changes
validator changes
release/version/tag/PyPI publication
```

## Final Verdict

```text
DOMAIN_2_ORACLE_NEEDS_REVISION
ORACLE_REVIEW_COMPLETE
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```
