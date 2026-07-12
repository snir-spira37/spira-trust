# Test/Build Failure Contract Oracle Validator Implementation Report

Status:

```text
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_PASS
VALIDATOR_IMPLEMENTATION_COMPLETE
SCHEMA_V7_VALIDATION_AND_JSON_PARSE_CLASSIFICATION_FIXED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Authorization:

```text
research/test_build_failure_contract_oracle_validator_implementation_authorization.md
```

Accepted schema:

```text
SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
```

Accepted validator spec:

```text
research/test_build_failure_contract_oracle_validator_spec.md
research/test_build_failure_contract_oracle_validator_spec_review.md
```

## Implemented Scope

The implementation adds a narrow Domain 2 oracle validator:

```text
source/spira_core/test_build_failure_oracle_validator.py
```

The validator accepts oracle JSON bytes, files, or already-parsed documents and
returns a machine-readable validation result:

```text
SPIRA_DOMAIN2_ORACLE_VALIDATOR_RESULT
```

It implements:

```text
full Oracle Schema V7 validation with an internal V7 schema evaluator
scope/result/collection hash recomputation
scope canonicalization checks
case-id uniqueness
related-case referential integrity
relationship symmetry
explicit-list equivalence
action/stop consistency
semantic result invariants
declared-delta validation
fail-closed statuses
machine-readable PASS / FAIL / TOOL_ERROR output
```

No producer, oracle population, corpus materialization, Gate B, Domain 3, or
release work was performed.

## Fixture Coverage

Focused validator tests use a canonical positive oracle fixture factory and
apply one targeted mutation per negative fixture. The fixture manifest is:

```text
tests/fixtures/test_build_failure_oracle_validator/fixture_manifest.json
```

Positive fixture coverage:

```text
minimal passing oracle document
machine-readable bytes input
multiple cases with symmetric relationships
NOT_EVALUATED scope implies NOT_EVALUATED result
REPORT_WITH_NOTES with stop:false
```

Negative fixture coverage includes:

```text
malformed JSON
nested Schema V7 violation
forbidden additional property
invalid enum
missing nested required field
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
stop/action contradictions
passed result with blocking cases
run timeout without TIMEOUT run-level failure
failure classes not derived from cases
ambiguous repository URL
shell command string instead of argv
dirty revision represented as git_commit only
unknown active plugin
duplicate plugin identity
NOT_EVALUATED identity carrying hash
NOT_EVALUATED identity carrying projection
EMITTED identity with incomplete evidence
validator internal exception
```

The implementation review at `15ed353` found two gaps in the first
implementation:

```text
Schema V7 validation was incomplete.
Malformed JSON was classified as TOOL_ERROR.
```

This revision closes both:

```text
Oracle Schema V7 is validated before validator-enforced invariants.
Malformed JSON returns FAIL / ORACLE_VALIDATION_FAILED.
Validator internal exceptions remain TOOL_ERROR / ORACLE_VALIDATOR_TOOL_ERROR.
```

## Hash-Only Gate

The critical fail-closed rule passed:

```text
hash only without canonical projection bytes
-> PROJECTION_BYTES_NOT_AVAILABLE
-> ORACLE_VALIDATION_FAILED
-> FAIL CLOSED
```

The validator never accepts an identity digest merely because it looks like a
SHA-256 string. It requires canonical projection bytes and recomputes the
identity hash.

## Test Results

Focused validator tests:

```text
python -m pytest tests/test_test_build_failure_oracle_validator.py -q
8 passed
```

Full suite:

```text
python -m pytest -q
86 passed
```

## Notes

This implementation is intentionally not wired into packaging or CLI release
surfaces. Version bump, public wheel inclusion, release tags and PyPI
publication were not authorized in this step.

The validator is a prerequisite for future oracle population authorization,
but it does not itself authorize oracle population.
