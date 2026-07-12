# Test/Build Failure Contract Oracle Validator Implementation Review

Status:

```text
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_NEEDS_REVISION
VALIDATOR_IMPLEMENTATION_REVIEW_COMPLETE
VALIDATOR_IMPLEMENTATION_MERGED_NOT_ACCEPTED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed implementation commit:

```text
97d2659 Implement Domain 2 oracle validator
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

This is an implementation review only. It does not authorize oracle population,
corpus materialization, producer implementation, Gate B, Domain 3, or release
activity.

## Finding 1: Schema V7 Validation Is Incomplete

The accepted validator specification requires this processing order:

```text
1. Parse JSON bytes.
2. Validate against Oracle Schema V7.
3. Validate document-level uniqueness and references.
4. Run the validator-enforced invariants.
```

The implementation in `97d2659` performs only a narrow manual shape check:

```text
top-level required fields
schema name/version/status
cases is an array
not_authorized contains required boundaries
```

It does not load or fully enforce:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
```

Therefore it does not fully check nested required fields,
`additionalProperties: false`, enums, const values, or V7 conditional
constraints before running validator-specific checks.

This violates the accepted validator spec.

Required correction:

```text
Run full Oracle Schema V7 validation before validator-enforced checks.
```

If no external JSON Schema dependency is introduced, the implementation must
provide an internal schema evaluator sufficient for the accepted V7 schema and
cover it with negative fixtures.

Verdict:

```text
SCHEMA_V7_VALIDATION_INCOMPLETE
```

## Finding 2: Malformed JSON Is Misclassified As Tool Error

The accepted validator specification classifies malformed oracle JSON as
document validation failure:

```text
JSON parse failure
-> verdict: FAIL
-> status: ORACLE_VALIDATION_FAILED
```

`TOOL_ERROR` is reserved for a validator internal failure.

The implementation in `97d2659` returns:

```text
JSON parse failure
-> verdict: TOOL_ERROR
-> status: ORACLE_VALIDATOR_TOOL_ERROR
```

This makes invalid oracle input look like a broken validator. That distinction
matters because oracle authoring failures must not be hidden as tooling
failures.

Required correction:

```text
JSON_PARSE_FAILED
-> FAIL
-> ORACLE_VALIDATION_FAILED
```

Validator internal exceptions may still return:

```text
TOOL_ERROR
ORACLE_VALIDATOR_TOOL_ERROR
```

Verdict:

```text
JSON_PARSE_FAILURE_CLASSIFICATION_INCORRECT
```

## Required Narrow Revision

The revision must be limited to:

```text
1. Full Oracle Schema V7 validation before validator-enforced checks.
2. JSON parse failures classified as FAIL / ORACLE_VALIDATION_FAILED.
3. Negative fixtures for:
   - malformed JSON
   - nested Schema V7 violation
   - forbidden additional property
   - invalid enum
   - missing nested required field
4. Updated focused validator tests.
5. Updated implementation report/results.
```

No other scope is opened.

## Still Accepted From The First Implementation

The first implementation still demonstrated useful pieces:

```text
hash-only projection fails closed
semantic validator checks exist
machine-readable PASS / FAIL / TOOL_ERROR output exists
focused tests and full pytest passed
```

Those facts remain true, but they are not sufficient for implementation
acceptance while Schema V7 validation and malformed JSON classification are
incorrect.

## Final Verdict

```text
DOMAIN_2_ORACLE_VALIDATOR_IMPLEMENTATION_NEEDS_REVISION
VALIDATOR_IMPLEMENTATION_MERGED_NOT_ACCEPTED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

The validator implementation may be revised within the already authorized
validator scope. It must not populate oracle cases, implement a producer,
materialize a corpus, change Schema V7, or start Gate B.
