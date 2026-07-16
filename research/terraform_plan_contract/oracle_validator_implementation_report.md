# Terraform Plan Oracle Validator Implementation Report

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_PASS
VALIDATOR_IMPLEMENTATION_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Authorization Chain

```text
corpus:
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED

schema:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED

validator spec:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED

implementation authorization:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_AUTHORIZED
```

The accepted corpus manifest remains:

```text
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

## Implemented Files

```text
source/spira_core/terraform_plan_oracle_validator.py
tools/validate_terraform_plan_oracle.py
tests/test_terraform_plan_oracle_validator.py
research/terraform_plan_contract/validator_fixtures/README.md
research/terraform_plan_contract/oracle_validator_implementation_results.json
research/terraform_plan_contract/oracle_validator_implementation_report.md
```

## Implemented Checks

The validator implements:

```text
Schema V1 validation
canonical hash recomputation
case/reference integrity
relationship symmetry by relation recomputation
strict-list equivalence
resource action-sequence validation
replace_paths consistency
unknown-path representation
sensitive-value absence
optional provenance states
action/stop consistency
machine-readable PASS / FAIL / TOOL_ERROR output
```

Malformed oracle JSON is classified as:

```text
FAIL
ORACLE_VALIDATION_FAILED
JSON_PARSE_FAILED
```

Internal validator exceptions are classified separately as:

```text
TOOL_ERROR
ORACLE_VALIDATOR_TOOL_ERROR
ORACLE_VALIDATOR_EXCEPTION
```

Hash-only inputs without recomputable canonical bytes fail closed. In the
focused fixture suite this is represented by BOUND provenance that provides only
a fingerprint without the canonical bytes needed for recomputation.

## Positive Fixtures

Focused positive fixtures cover:

```text
valid 40-case corpus-bound oracle fixture
machine-readable bytes input
resource action facts
replacement path facts
unknown path facts
sensitive structural path facts
optional provenance states
mutation relationship set
```

Result:

```text
positive fixtures: 3 / 3 PASS
```

## Negative Fixtures

Focused negative fixtures cover:

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

Result:

```text
negative fixtures: 22 / 22 expected failures
```

## Test Results

Focused validator tests:

```text
command:
pytest tests\test_terraform_plan_oracle_validator.py -q

result:
7 passed
```

Full suite:

```text
command:
$env:PYTHONPATH='source;.'; pytest -q

result:
101 passed
```

The explicit `PYTHONPATH=source;.` is required by the existing
`tests/test_previous_version_gate.py` import of the repository-local `corpus`
package. Without the repository root on `PYTHONPATH`, pytest collection fails
before validator tests are reached.

## Privacy / Path / Secret Scan

Command:

```text
rg -n "<USER_HOME>|BEGIN PRIVATE KEY|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]+|xox[baprs]-|-----BEGIN" \
  source/spira_core/terraform_plan_oracle_validator.py \
  tests/test_terraform_plan_oracle_validator.py \
  tools/validate_terraform_plan_oracle.py \
  research/terraform_plan_contract/validator_fixtures/README.md
```

Result:

```text
PASS
```

The test suite intentionally includes a synthetic sensitive-value string in a
negative fixture to prove fail-closed behavior. It is not a secret.

## Boundaries Preserved

```text
oracle population performed: false
producer output observed: false
corpus changed: false
Oracle Schema V1 changed: false
validator spec changed: false
Gate B touched: false
Domain 4 touched: false
release/version/tag/PyPI touched: false
```

## Machine-Readable Results

```text
research/terraform_plan_contract/oracle_validator_implementation_results.json
```

## Post-Implementation Review Required

This report is not acceptance. A separate implementation review is still
required before oracle population can be considered.

Allowed review verdicts:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_NEEDS_REVISION
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_REJECTED
```
