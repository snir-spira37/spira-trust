# Test/Build Failure Contract Oracle Revision Authorization

Status:

```text
DOMAIN_2_ORACLE_REVISION_AUTHORIZED
ORACLE_REVISION_ONLY
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Accepted oracle review:

```text
9f90a4b Review Domain 2 oracle population
DOMAIN_2_ORACLE_NEEDS_REVISION
ORACLE_REVIEW_COMPLETE
```

Preserved mechanical population result:

```text
DOMAIN_2_ORACLE_POPULATED
Schema V7: PASS
Accepted validator: PASS
38 / 38 cases populated
```

This document authorizes only a narrow semantic revision of the populated
oracle. It does not authorize producer implementation, pytest adapter
implementation, Gate B, Domain 3, corpus replacement, schema changes,
validator changes, or release activity.

## Purpose

The populated oracle is structurally valid and passed the accepted validator,
but the oracle review found that it is not yet semantically acceptable as the
expected-answer set for a future producer benchmark.

The purpose of this revision is to fix only the four review findings:

```text
ORACLE_CLASSIFICATION_SOURCE_RISK
EVIDENCE_CONFLICT_DECISION_MISMATCH
IDENTITY_RELATIONSHIP_MISMATCH
SUFFICIENCY_AND_COLLECTION_ASSUMED
```

## Authorized Files

The revision may edit only:

```text
research/test_build_failure_contract/oracle_v1.json
research/test_build_failure_contract/oracle_population_report.md
research/test_build_failure_contract/oracle_population_results.json
tools/populate_test_build_failure_oracle.py
```

The revision may add a versioned revised oracle only if needed for clarity:

```text
research/test_build_failure_contract/oracle_v2.json
```

If a file outside this list is required, work must stop and a new
authorization document must be committed before changing it.

## Finding 1: Classification Source

Authorized correction:

```text
expected answers must be derived from frozen evidence
case names must not determine expected answers
case_kind must not act as a hidden answer key
exit code may be used only as evidence
```

Permitted evidence sources:

```text
console evidence
JUnit XML evidence
exit-code evidence
metadata evidence
public_run_materialization records
frozen corpus manifest
declared mutation pairs
```

The revised oracle population logic must document, per case or by explicit
rule, how expected answers are derived from evidence rather than from corpus
labels that encode the intended result.

## Finding 2: Evidence Conflict Decision

Authorized correction:

```text
synthetic_console_junit_conflict
-> recommended_agent_action: RERUN_REQUIRED
-> reason_codes: ["TEST_EVIDENCE_CONFLICT"]
```

The revised oracle must not classify console/JUnit contradiction as an ordinary
test failure:

```text
STOP_BLOCKED + TEST_FAILURE
```

is not acceptable for that conflict case.

If the accepted identity model requires the result identity to be
`NOT_EVALUATED` for this conflict, the revision may set it so, provided Schema
V7 and the accepted validator pass.

## Finding 3: Identity Relationships

Authorized correction:

```text
derive SAME / DIFFERENT per declared mutation pair
do not default all run/scope/result identities to DIFFERENT
```

For contextual or cosmetic declared deltas:

```text
TRACEBACK_FORMATTING_CHANGED
TEMP_PATH_CHANGED
UNRELATED_STDOUT_ADDED
```

the revision must evaluate whether:

```text
run_identity_relation: DIFFERENT
scope_identity_relation: SAME or DIFFERENT, based on scope evidence
result_identity_relation: SAME when normalized result semantics are unchanged
```

If a declared mutation changes semantic result facts, the oracle must record
`result_identity_relation: DIFFERENT` and justify that difference from the
evidence or declared mutation.

## Finding 4: Sufficiency And Collection

Authorized correction:

```text
set expected_source_sufficiency per source and per case
derive collection_deterministic from explicit evidence
do not default all sources to ANSWERED
do not default all collection identities to deterministic
```

Allowed source sufficiency values:

```text
ANSWERED
NOT_APPLICABLE
NOT_EVALUATED
CONFLICTING
```

The revision must handle at least:

```text
truncated console evidence
malformed JUnit evidence
incomplete JUnit evidence
console/JUnit conflict evidence
withheld public raw outputs represented by hashes
non-derivable rerun target evidence
```

If collection determinism cannot be established for a case, the oracle must
fail closed under the accepted Schema V7 and validator behavior.

## Required Validation

The revision must rerun:

```text
Schema V7 validation
accepted oracle validator
identity hash recomputation
scope identity recomputation
result identity recomputation
collection manifest hash recomputation
explicit-list validation
mutation relationship validation
NOT_EVALUATED validation
ACTION_STOP_CONSISTENCY validation
JSON validation
privacy/path/secret scans
full pytest suite
```

Required successful result:

```text
38 / 38 oracle cases present
Schema V7: PASS
Accepted validator: PASS
validator errors: 0
producer_output_observed: false
```

## Stop Conditions

Any of the following must stop the revision:

```text
case count changes
corpus case IDs change
corpus evidence changes
mutation pairs change
Schema V7 validation fails
accepted validator fails
identity hash does not recompute
explicit list mismatch remains
console/JUnit conflict remains STOP_BLOCKED + TEST_FAILURE
contextual/cosmetic mutation pairs remain blanket DIFFERENT without evidence
source sufficiency remains blanket ANSWERED without evidence
collection_deterministic remains blanket true without evidence
producer output observed
need to change Schema V7
need to change accepted validator
need to change corpus
```

Stop status:

```text
DOMAIN_2_ORACLE_REVISION_INCOMPLETE
```

or:

```text
DOMAIN_2_ORACLE_REVISION_FAILED
```

If the authorization itself proves insufficient, the required result is:

```text
ORACLE_REVISION_AUTHORIZATION_REVISION_REQUIRED
```

## Completion Statuses

The revision must end in exactly one of:

```text
DOMAIN_2_ORACLE_REVISED
DOMAIN_2_ORACLE_REVISION_INCOMPLETE
DOMAIN_2_ORACLE_REVISION_FAILED
ORACLE_REVISION_AUTHORIZATION_REVISION_REQUIRED
```

`DOMAIN_2_ORACLE_REVISED` is not semantic oracle acceptance. It means only that
the revised oracle has been produced and passed the required mechanical gates.

After revision, a separate final oracle review is required before any producer
authorization can be considered.

## Not Authorized

This authorization does not permit:

```text
corpus modification
case replacement
case addition
Schema V7 changes
validator changes
producer implementation
pytest adapter implementation
Gate B status/cache/rerun work
Domain 3 work
release/version/tag/PyPI publication
oracle changes based on producer output
```

## Final Authorization

```text
DOMAIN_2_ORACLE_REVISION_AUTHORIZED
ORACLE_REVISION_ONLY
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```
