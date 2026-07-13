# Terraform Plan Oracle Validator Implementation Authorization

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_AUTHORIZED
VALIDATOR_IMPLEMENTATION_AUTHORIZATION_ONLY
ORACLE_SCHEMA_V1_ACCEPTED
ORACLE_VALIDATOR_SPEC_ACCEPTED
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
CORPUS_CHANGES_NOT_AUTHORIZED
SCHEMA_OR_SPEC_CHANGES_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows:

```text
Terraform corpus:
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED

Oracle schema:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED

Oracle validator specification:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED
```

The accepted corpus manifest remains:

```text
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

## Authorized Work

Only the following work is authorized:

```text
1. Terraform Plan oracle validator implementation.
2. Focused positive validator fixtures.
3. Focused negative validator fixtures.
4. Machine-readable validation results.
5. Validator implementation report.
6. Focused validator tests.
7. Full test-suite execution.
```

The validator may validate future oracle documents against:

```text
research/terraform_plan_contract/oracle_schema_v1.schema.json
research/terraform_plan_contract/oracle_validator_spec.md
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/cases/
```

It may not create oracle expected answers.

## Allowed Files

Implementation may touch only files required for the validator:

```text
source/spira_core/terraform_plan_oracle_validator.py
tests/test_terraform_plan_oracle_validator.py
tools/validate_terraform_plan_oracle.py
research/terraform_plan_contract/validator_fixtures/
research/terraform_plan_contract/oracle_validator_implementation_report.md
research/terraform_plan_contract/oracle_validator_implementation_results.json
```

If implementation requires any file outside this list, work must stop and a new
authorization must be written before changing that file.

## Forbidden Changes

This authorization does not allow:

```text
oracle population
oracle expected answers
producer implementation
pytest or Terraform producer adapter
corpus modification
case replacement
case addition
case deletion
Oracle Schema V1 modification
validator specification modification
Gate A refactor
Gate B cache/reuse/status work
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```

## Required Validator Behavior

The implementation must follow the accepted specification and enforce:

```text
full Oracle Schema V1 validation
canonical hash recomputation
case/reference integrity
relationship symmetry
strict-list equivalence
resource action-sequence validation
replace_paths consistency
unknown-path representation
sensitive-value absence
optional provenance states
action/stop consistency
machine-readable PASS / FAIL / TOOL_ERROR output
```

Malformed oracle JSON must return:

```text
verdict: FAIL
status: ORACLE_VALIDATION_FAILED
error_code: JSON_PARSE_FAILED
```

It must not return `TOOL_ERROR`.

`TOOL_ERROR` is reserved for internal validator failures.

## Hash-Only Fail-Closed Rule

The implementation must not accept a digest merely because it is a valid
SHA-256 string.

If canonical bytes required for recomputation are missing, validation must fail:

```text
error_code: CANONICAL_BYTES_NOT_AVAILABLE
verdict: FAIL
status: ORACLE_VALIDATION_FAILED
```

## Required Positive Fixtures

Focused positive fixtures must cover at least:

```text
valid minimal no-change case
valid create/update/delete case
valid replacement case preserving action sequence order
valid unknown_paths case
valid sensitive_paths NOT_EVALUATED case
valid optional provenance states
valid mutation relationship set
```

Positive fixtures may be small and focused, but they must use the same schema,
canonicalization, and validator path as the final oracle validation path.

## Required Negative Fixtures

The implementation must include negative fixtures for:

```text
malformed JSON oracle document
Schema V1 nested required-field violation
forbidden additional property
invalid enum
missing accepted corpus case
extra non-corpus case
case file hash mismatch
subject hash mismatch
context hash mismatch
unification_id mismatch
hash-only identity without canonical bytes
unresolvable evidence locator
duplicate claim_id
non-canonical explicit list
replace_paths mismatch
unknown_paths mismatch
sensitive value exposed as ordinary string
BOUND provenance without recomputable bytes
invalid stop/action pair
mutation pair references missing case
mutation relation mismatch
producer output observed
```

Each negative fixture must fail with the expected validation error and must not
be reported as `TOOL_ERROR`.

## Machine-Readable Results

The implementation must produce:

```text
research/terraform_plan_contract/oracle_validator_implementation_results.json
```

with:

```text
schema: SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_RESULTS
schema_version: 1
status:
  DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_PASS
  DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_INCOMPLETE
  VALIDATOR_SPEC_REVISION_REQUIRED
  IMPLEMENTATION_AUTHORIZATION_REVISION_REQUIRED
accepted_schema: Oracle Schema V1
accepted_spec: oracle_validator_spec.md
positive_fixtures_total
positive_fixtures_passed
negative_fixtures_total
negative_fixtures_expected_failures
focused_tests
full_tests
oracle_population_performed: false
producer_output_observed: false
errors
```

## Implementation Report

The implementation report must be:

```text
research/terraform_plan_contract/oracle_validator_implementation_report.md
```

It must document:

```text
authorization chain
implemented checks
fixtures and expected outcomes
focused test command and result
full test command and result
machine-readable results path
privacy/path/secret scan result
confirmation that oracle population was not performed
confirmation that producer implementation was not performed
```

## Acceptance Gates

The implementation may be reported as pass only if all gates pass:

```text
focused validator tests: PASS
all positive fixtures: PASS
all negative fixtures: expected failures
hash-only fixtures: FAIL CLOSED
malformed JSON fixtures: FAIL / ORACLE_VALIDATION_FAILED
machine-readable result validation: PASS
privacy/path/secret scan: PASS
full pytest suite: PASS
oracle population performed: false
producer output observed: false
corpus/schema/spec unchanged
```

The only successful implementation status is:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_PASS
```

## Stop Conditions

The implementation must stop with a non-pass status if any of these occur:

```text
Oracle Schema V1 is insufficient for validator implementation
validator spec is ambiguous or impossible to implement
required canonical bytes cannot be derived under the locked contract
negative fixture cannot be represented without changing schema/spec
corpus artifact must be changed
oracle expected answers are needed
producer output is observed
Gate B behavior is needed
```

Allowed terminal non-pass statuses:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_INCOMPLETE
VALIDATOR_SPEC_REVISION_REQUIRED
IMPLEMENTATION_AUTHORIZATION_REVISION_REQUIRED
```

## Post-Implementation Review Requirement

Even if the implementation reports:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_PASS
```

the validator is not accepted until a separate review records one of:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_NEEDS_REVISION
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_REJECTED
```

Oracle population remains blocked until the validator implementation is
accepted by that separate review.

## Non-Authorization

This document does not authorize:

```text
oracle population
producer implementation
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```
