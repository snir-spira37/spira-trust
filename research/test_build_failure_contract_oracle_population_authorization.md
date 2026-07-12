# Test/Build Failure Contract Oracle Population Authorization

Status:

```text
DOMAIN_2_ORACLE_POPULATION_AUTHORIZED
ORACLE_POPULATION_AUTHORIZATION_ONLY
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Accepted prerequisites:

```text
Dual Identity Model V2: ACCEPTED
Oracle Schema V7: ACCEPTED
Oracle Validator Spec: ACCEPTED
Oracle Validator Implementation: ACCEPTED
Domain 2 Corpus: ACCEPTED
Public Run Materialization: ACCEPTED
```

Accepted corpus review:

```text
90bf925 Review Domain 2 public run materialization
DOMAIN_2_CORPUS_ACCEPTED
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_ACCEPTED
```

This document authorizes only Domain 2 oracle population for the frozen
38-case corpus. It does not authorize producer implementation, pytest adapter
implementation, Gate B, Domain 3, or any release activity.

## Purpose

The accepted corpus is a frozen evidence input set. It is not yet an oracle.

The next research object is an independently authored oracle that records the
expected answers for the 38 frozen cases:

```text
30 synthetic cases
8 materialized public run cases
6 declared mutation pairs
```

Oracle population means writing expected claims, identities, actions, explicit
lists, relationships and evidence locators against the already accepted corpus.
It must not use producer output.

## Authorized Work

This authorization permits only:

```text
oracle document creation
expected scope_identity authoring
expected result_identity authoring
expected result_identity_status authoring
expected run/result identity relationship authoring
expected policy/action binding authoring
expected typed claim authoring
expected explicit sorted unique list authoring
expected NOT_EVALUATED state authoring
expected evidence locator authoring
expected mutation relationship authoring
expected not-claimed boundary authoring
validator execution against the populated oracle
oracle population report creation
machine-readable oracle population results creation
privacy/path/secret scans
```

The oracle must be authored from frozen evidence only:

```text
synthetic console/JUnit/metadata evidence
public run materialization records
public console/JUnit/exit-code hashes
recorded dependency environments
frozen corpus manifest
declared mutation pairs
```

## Authorized Files

The oracle population step may add or edit only:

```text
research/test_build_failure_contract/oracle/
research/test_build_failure_contract/oracle_v1.json
research/test_build_failure_contract/oracle_population_report.md
research/test_build_failure_contract/oracle_population_results.json
tools/populate_test_build_failure_oracle.py
```

If another file is required, work must stop and a new authorization document
must be committed before changing it.

## Required Oracle Content

For every one of the 38 frozen cases, the oracle must include:

```text
case_id
expected_scope_identity
expected_result_identity
expected_result_identity_status
expected_run_identity_relationships, when applicable
expected_result_identity_relationships, when applicable
expected_policy_action
expected_typed_claims
expected_explicit_lists
expected_evidence_locators
expected_not_evaluated states, when applicable
expected_not_claimed boundaries
```

For the 6 declared mutation pairs, the oracle must include expected mutation
relationships. Relationships must be valid and symmetric when the accepted
validator requires symmetry.

Every list that functions as a set must be:

```text
sorted
unique
explicit
consistent with the identity projection
```

Count-only oracle answers are not sufficient when the contract requires the
underlying explicit list.

## Canonical Projection Requirement

Every emitted identity must include enough canonical projection bytes for the
accepted validator to recompute the identity hash.

The oracle must not use hash-only expected identities:

```text
scope_identity_sha256 without scope projection bytes
result_identity_sha256 without result projection bytes
collection_manifest_sha256 without canonical collection manifest bytes
```

Hash-only inputs must fail closed under the accepted validator:

```text
PROJECTION_BYTES_NOT_AVAILABLE
ORACLE_VALIDATION_FAILED
```

## Schema And Validator Gates

The populated oracle must satisfy:

```text
accepted schema: SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
accepted validator spec: cec74d1
accepted validator implementation final review: a4dcafe
validator schema-gate correction: 1da0059
```

Required gates:

```text
38 / 38 oracle cases populated
38 / 38 pass Schema V7
38 / 38 pass accepted validator
identity hashes recompute
scope identities recompute
result identities recompute
collection manifest hashes recompute
explicit lists match projections
related case references resolve
identity relationships are symmetric where required
mutation relationships are valid
NOT_EVALUATED cases fail closed
ACTION_STOP_CONSISTENCY holds
privacy/path/secret scans pass
producer output observed: false
```

## Independence Rules

Oracle authoring is not producer implementation.

The oracle must not be derived from:

```text
Domain 2 producer output
pytest adapter output
Gate B cache/status/rerun output
LLM interpretation of hidden evidence
case names alone
```

The oracle may use human-authored interpretation of the frozen evidence and the
accepted Domain 2 contracts.

For public cases, names such as:

```text
public_requests_clean
public_requests_assertion
public_flask_unicode_path
```

are not expected answers. The oracle must be authored from the materialized
console/JUnit/exit-code evidence and the recorded dependency environment.

The corpus field:

```text
producer_output_seen
```

must remain false for all cases during oracle population.

## Stop Conditions

Any of the following must stop oracle population:

```text
case count != 38
corpus case ID changed
mutation pair changed
missing evidence locator
missing canonical projection bytes for an emitted identity
identity hash does not recompute
Schema V7 validation failure
accepted validator failure
explicit list mismatch
relationship asymmetry
unresolved related_case_id
NOT_EVALUATED state paired with emitted identity hash
stop/action inconsistency
producer output observed
attempt to change corpus evidence to fit oracle answer
attempt to replace a case silently
private path or secret detected in publishable oracle artifact
```

Stop status:

```text
DOMAIN_2_ORACLE_POPULATION_INCOMPLETE
```

or, if the oracle contract itself must change:

```text
DOMAIN_2_ORACLE_NEEDS_REVISION
```

No expected answer may be completed by assumption. No threshold may be changed
after seeing validation failures.

## Required Results

The oracle population step must produce:

```text
research/test_build_failure_contract/oracle_v1.json
research/test_build_failure_contract/oracle_population_report.md
research/test_build_failure_contract/oracle_population_results.json
```

The results file must report:

```text
schema validation status
validator status
case count
populated case count
identity recomputation status
explicit-list validation status
mutation relationship validation status
NOT_EVALUATED validation status
privacy/path/secret scan status
producer output observed status
```

## Completion Statuses

Oracle population must end in exactly one of:

```text
DOMAIN_2_ORACLE_POPULATED
DOMAIN_2_ORACLE_POPULATION_INCOMPLETE
DOMAIN_2_ORACLE_NEEDS_REVISION
ORACLE_POPULATION_AUTHORIZATION_REVISION_REQUIRED
```

`DOMAIN_2_ORACLE_POPULATED` does not authorize producer implementation. It only
means the oracle has been populated and validated under this authorization.

After population, a separate oracle review is required before any producer
authorization can be considered.

## Not Authorized

This authorization does not permit:

```text
producer implementation
pytest adapter implementation
Gate B status/cache/rerun work
Domain 3 work
core changes
schema changes
validator changes
corpus case replacement
release/version/tag/PyPI publication
```

## Final Authorization

```text
DOMAIN_2_ORACLE_POPULATION_AUTHORIZED
ORACLE_POPULATION_AUTHORIZATION_ONLY
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```
