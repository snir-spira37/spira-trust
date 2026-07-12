# Test/Build Failure Contract Oracle Validator Implementation Authorization

Status:

```text
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_AUTHORIZED
VALIDATOR_IMPLEMENTATION_AUTHORIZATION_ONLY
ORACLE_SCHEMA_V7_ACCEPTED
ORACLE_VALIDATOR_SPEC_ACCEPTED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Accepted schema:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
ORACLE_SCHEMA_V7_LOCKED
DOMAIN_2_ORACLE_SCHEMA_V7_ACCEPTED
```

Accepted validator specification:

```text
research/test_build_failure_contract_oracle_validator_spec.md
research/test_build_failure_contract_oracle_validator_spec_review.md
DOMAIN_2_ORACLE_VALIDATOR_SPEC_ACCEPTED
```

This document authorizes a narrow implementation of the Domain 2 oracle
validator and its focused tests. It does not authorize oracle case population,
Domain 2 producer implementation, corpus materialization, Gate B, Domain 3, or
release activity.

## Authorized Work

The authorized work is limited to:

```text
validator implementation for SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
positive validator fixtures
negative validator fixtures
machine-readable validation report output
focused validator tests
validator implementation report
```

The implementation must validate oracle documents against the accepted V7
schema and every validator-enforced invariant accepted in the validator spec.

The implementation must not infer missing oracle data from the workspace, run
pytest, create oracle cases, materialize a corpus, or implement a producer.

## Allowed Files

The implementation may add or edit only files required for the validator:

```text
source/spira_core/test_build_failure_oracle_validator.py
tests/test_test_build_failure_oracle_validator.py
tests/fixtures/test_build_failure_oracle_validator/
research/test_build_failure_contract_oracle_validator_implementation_report.md
research/test_build_failure_contract_oracle_validator_implementation_results.json
```

If implementation requires any file outside this list, work must stop and a new
authorization document must be committed before that file is changed.

The accepted schema and accepted spec may be read but must not be changed by
this authorization:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
research/test_build_failure_contract_oracle_validator_spec.md
research/test_build_failure_contract_oracle_validator_spec_review.md
```

## Forbidden Files And Areas

This authorization does not allow changes to:

```text
source/spira_core/unification_proof.py
source/spira_core agent action semantics
status/cache/rerun planner code
Domain 1 unification corpus tooling
Domain 1 identity baseline
Gate B code or documents
Domain 2 producer code
Domain 2 corpus files
oracle populated case files
release, version, tag, PyPI, or packaging metadata
```

No new action enum, claim status enum, decision semantics version, or
Unification Proof schema change is authorized.

## Required Validator Scope

The validator must implement all accepted checks from the validator spec:

```text
JSON Schema V7 validation
hash recomputation
scope canonicalization checks
case-id uniqueness
related-case referential integrity
relationship symmetry
explicit-list equivalence
action/stop consistency
semantic result invariants
declared-delta validation
fail-closed statuses
machine-readable output schema
```

The validator must distinguish:

```text
oracle validation failure
validator tool error
schema parse failure
```

It must not convert tool errors into oracle findings, and it must not hide
oracle validation failures as tool errors.

## Hash-Only Fail-Closed Requirement

The accepted spec review requires:

```text
hash only without canonical projection bytes
-> PROJECTION_BYTES_NOT_AVAILABLE
-> ORACLE_VALIDATION_FAILED
-> FAIL CLOSED
```

The implementation must include negative fixtures for:

```text
hash-only scope projection
hash-only result projection
```

A document that supplies only `scope_projection_sha256` or only an identity
hash without the canonical projection bytes needed for recomputation must fail.

The validator must recompute hashes from canonical bytes. It must never accept
a digest merely because it is a syntactically valid SHA-256 string.

## Required Positive Fixtures

Focused positive fixtures must cover at least:

```text
minimal passing oracle document
multiple cases with reciprocal identity relationships
EMITTED scope identity with full projection
EMITTED result identity with full projection
STOP_BLOCKED with stop:true
REPORT_WITH_NOTES with stop:false
NOT_EVALUATED scope implying NOT_EVALUATED result
policy-independent result identity separate from policy action
```

Positive fixtures must be hand-authored for validator behavior only. They are
not oracle population and must not be presented as corpus cases.

## Required Negative Fixtures

Every validator-enforced invariant must have at least one negative fixture.

Required negative fixtures include:

```text
hash-only scope projection
hash-only result projection
scope hash mismatch
result hash mismatch
collection manifest hash mismatch
duplicate case_id
missing related_case_id
asymmetric relationship
unsorted canonical arrays
duplicate set member
strict-list mismatch
invalid declared delta
stop:false with STOP_BLOCKED
stop:true with PROCEED
passed result with blocking cases
run timeout without TIMEOUT run-level failure
failure classes not derived from cases
ambiguous repository URL
shell command string instead of argv
dirty git revision represented as git_commit only
unknown active plugin
duplicate plugin identity
NOT_EVALUATED identity carrying hash
NOT_EVALUATED identity carrying projection
EMITTED identity with incomplete evidence
validator internal exception
```

Each negative fixture must assert the expected machine-readable `error_code`.

## Machine-Readable Report Requirement

The validator must emit one JSON object matching the accepted result contract:

```text
schema: SPIRA_DOMAIN2_ORACLE_VALIDATOR_RESULT
schema_version: 1
validator_spec: SPIRA_DOMAIN2_ORACLE_VALIDATOR_SPEC_V1
oracle_schema: SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
verdict: PASS / FAIL / TOOL_ERROR
status: ORACLE_VALIDATION_PASS / ORACLE_VALIDATION_FAILED /
        ORACLE_VALIDATOR_TOOL_ERROR
checks: per-check machine-readable results
not_authorized: closed execution boundary
```

The report must not include secrets or absolute private paths. Paths must be
relative, redacted, or explicitly safe for publication.

## Required Test Gates

Before the implementation can be accepted, all of the following must pass:

```text
focused validator tests: PASS
all required positive fixtures: PASS
all required negative fixtures: PASS with expected error codes
hash-only fixtures: FAIL CLOSED
machine-readable report validation: PASS
privacy/path/secret scan for validator outputs: PASS
full pytest suite: PASS
```

The implementation report must include:

```text
fixture count
positive fixture count
negative fixture count
required invariant coverage table
hash-only fail-closed result
machine-readable report example
test command outputs
not_authorized boundary
```

## Merge Conditions

Validator implementation may be merged only if:

```text
all required validator invariants are implemented
each invariant has at least one negative fixture
hash-only projection fixtures fail closed
focused validator tests pass
full pytest suite passes
implementation report is committed
machine-readable result examples are committed or referenced
no unauthorized files are changed
oracle population remains absent
producer implementation remains absent
corpus materialization remains absent
Gate B remains untouched
```

If any required invariant is missing, the result is:

```text
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_INCOMPLETE
```

If the implementation cannot preserve the accepted spec without changing V7,
the result is:

```text
VALIDATOR_SPEC_REVISION_REQUIRED
```

If unauthorized scope is needed, the result is:

```text
IMPLEMENTATION_AUTHORIZATION_REVISION_REQUIRED
```

## Explicitly Not Authorized

The following remain blocked:

```text
oracle population
oracle corpus materialization
Domain 2 producer implementation
pytest adapter implementation
running pytest to produce oracle cases
changing Oracle Schema V7
changing the accepted validator spec
changing the policy-independent result identity model
changing Unification Proof core
Gate B status/cache/rerun work
Domain 3
release, version bump, tag, PyPI publication
```

## Next Allowed Step

After this authorization is committed, the next allowed engineering step is:

```text
implement the Domain 2 oracle validator within the allowed scope
add focused validator fixtures and tests
produce the validator implementation report
```

The validator implementation must end in one of:

```text
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_PASS
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_INCOMPLETE
VALIDATOR_SPEC_REVISION_REQUIRED
IMPLEMENTATION_AUTHORIZATION_REVISION_REQUIRED
```

Even if the validator implementation passes, oracle population still requires
a separate authorization artifact.
