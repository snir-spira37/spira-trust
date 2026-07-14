# Machine Contract Passthrough Envelope Validator Implementation Report

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_PASS

DETERMINISTIC_VALIDATOR_IMPLEMENTED

SCHEMA_V1_FROZEN

VALIDATOR_SPECIFICATION_FROZEN

FORTY_THREE_FIXTURES_FROZEN

FIXTURE_MANIFEST_FROZEN

EXPECTED_OUTCOMES_FROZEN

MVP_INTEGRATION_NOT_PERFORMED

RUNNER_CHANGES_NOT_PERFORMED

PROMPT_CHANGES_NOT_PERFORMED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

RELEASE_NOT_AUTHORIZED
```

## 1. Scope

This implementation report covers only the deterministic validator authorized by:

```text
research/machine_contract_passthrough_envelope_validator_implementation_authorization.md
```

The implementation added:

```text
tools/validate_machine_contract_passthrough_envelope.py

tests/test_machine_contract_passthrough_envelope_validator.py

research/machine_contract_passthrough_envelope_validator_implementation_results.json
```

This report does not authorize MVP integration, runner changes, prompt changes,
live sessions, revised readiness, primary benchmark execution, result
reclassification, or release work.

## 2. Frozen Inputs Evaluated

The validator evaluated the frozen fixture manifest:

```text
research/machine_contract_passthrough_fixtures/fixture_manifest.json
```

It used the accepted Schema V1 and validator specification:

```text
research/machine_contract_passthrough_envelope_schema_v1.schema.json

research/machine_contract_passthrough_envelope_validator_spec.md
```

No fixture file, expected outcome, schema, or specification file was modified.

## 3. Validator Behavior Implemented

The validator returns:

```text
PASS
FAIL
TOOL_ERROR
```

It keeps `FAIL` separate from `TOOL_ERROR`.

Implemented checks include:

```text
JSON parse
Schema V1 structural constants and authority boundaries
embedded-and-hash-bound machine contract representation
canonical JSON hash recomputation
source contract hash equality
explicit field preservation against embedded_contract
action / stop consistency
reason_codes / blocking_items / NOT_EVALUATED / not_claimed preservation
evidence and proof reference identity preservation
producer and unified wrapper identity preservation
contradiction class detection
fail-closed contradiction consistency
telemetry availability-status consistency
sensitive marker absence across all envelope sections
fixture manifest expectation binding
deterministic repeated evaluation
fixture file hash verification
```

The implementation uses deterministic canonical JSON:

```text
sort_keys = true
separators = "," and ":"
UTF-8 bytes
arrays preserved in order
strings preserved exactly
```

## 4. Fixture Evaluation Results

Machine-readable results:

```text
research/machine_contract_passthrough_envelope_validator_implementation_results.json
```

Observed counts:

```text
fixture_count: 43
positive_fixture_count: 6
negative_fixture_count: 37
positive_pass_count: 6
negative_rejected_count: 37
false_accepts: 0
false_rejects: 0
fixture_mutations: 0
contradiction_classes_detected_count: 14
deterministic_repeated_evaluation: true
schema_manifest_hash_validation: PASS
errors: 0
```

Acceptance gates:

```text
6 / 6 positive fixtures PASS

37 / 37 negative fixtures rejected

14 / 14 contradiction classes detected

false accepts: 0

false rejects: 0

fixture mutations: 0

deterministic repeated evaluation: 100%

schema / manifest / hash validation: PASS
```

## 5. Negative Fixture Coverage

The implementation rejected all frozen negative fixture classes:

```text
15 / 15 machine-contract integrity failures

14 / 14 model-explanation contradiction fixtures

4 / 4 telemetry failures

4 / 4 sensitive-value failures
```

The validator detects all accepted contradiction classes:

```text
MODEL_EXPLANATION_CONTRADICTS_MACHINE_CONTRACT
MODEL_EXPLANATION_OVERRIDES_MACHINE_ACTION
MODEL_EXPLANATION_UNSAFE_CONTINUATION
MODEL_EXPLANATION_DROPS_BLOCKER
MODEL_EXPLANATION_ADDS_UNSUPPORTED_BLOCKER
MODEL_EXPLANATION_REWRITES_REASON_CODE_NON_EQUIVALENTLY
MODEL_EXPLANATION_CONVERTS_NOT_EVALUATED_TO_PASS
MODEL_EXPLANATION_CLAIMS_NOT_CLAIMED_BOUNDARY
MODEL_EXPLANATION_FABRICATES_EVIDENCE
MODEL_EXPLANATION_FABRICATES_PROOF_REFERENCE
MODEL_EXPLANATION_WEAKENS_RERUN_REQUIRED
MODEL_EXPLANATION_IGNORES_EVIDENCE_CONFLICT
MODEL_EXPLANATION_EXPOSES_SENSITIVE_VALUE
MODEL_EXPLANATION_FOLLOWS_INSTRUCTION_IN_EVIDENCE
```

## 6. Focused Tests

Focused validator tests:

```text
tests/test_machine_contract_passthrough_envelope_validator.py

9 passed
```

The tests cover:

```text
full 43-fixture manifest evaluation
per-fixture expected outcome matching
schema authority failure
hash mismatch and action drift
contradiction detection and fail-closed reporting
telemetry value/status conflict rejection
sensitive marker rejection
JSON parse failure as FAIL
internal exception as TOOL_ERROR
no fixture mutation during validation
```

## 7. Non-Authorization Preserved

This implementation did not perform and does not authorize:

```text
MVP integration
mvp_unified.py changes
runner changes
prompt changes
schema changes
fixture changes
Claude / Codex / DeepSeek sessions
revised readiness
primary benchmark
holdout
carryover
result reclassification
efficiency claim
merge to main
release / version / tag / PyPI
```

## 8. Completion Statement

The deterministic validator implementation satisfies the accepted Schema V1,
validator specification, frozen 43-fixture corpus, fixture manifest, and expected
outcomes within the authorized implementation scope.

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_PASS
```
