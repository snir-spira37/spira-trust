# Machine Contract Passthrough Envelope Validator Implementation Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_AUTHORIZED

SCHEMA_V1_FROZEN

VALIDATOR_SPECIFICATION_FROZEN

FORTY_THREE_FIXTURES_FROZEN

FIXTURE_MANIFEST_FROZEN

EXPECTED_OUTCOMES_FROZEN

DETERMINISTIC_VALIDATOR_IMPLEMENTATION_ONLY

VALIDATOR_TESTS_AUTHORIZED

FIXTURE_EVALUATION_AUTHORIZED

MVP_INTEGRATION_NOT_AUTHORIZED

RUNNER_CHANGES_NOT_AUTHORIZED

PROMPT_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes implementation of a deterministic validator for the
accepted Machine Contract Passthrough Envelope Schema V1.

The validator must evaluate the accepted 43-fixture corpus and produce
machine-readable results and a report.

This authorization does not authorize MVP integration, runner changes, prompt
changes, live sessions, revised readiness, primary benchmark execution, result
reclassification, or release work.

## 2. Frozen Inputs

The following are frozen:

```text
research/machine_contract_passthrough_envelope_schema_v1.schema.json

research/machine_contract_passthrough_envelope_validator_spec.md

research/machine_contract_passthrough_fixtures/

research/machine_contract_passthrough_fixtures/fixture_manifest.json

research/machine_contract_passthrough_contradiction_fixture_review.md
```

The implementation must not modify:

```text
Schema V1

validator specification

fixture files

fixture manifest

expected outcomes

Domain 1, Domain 2, or Domain 3 semantics

Gate A semantics

old Claude or Codex results
```

## 3. Authorized Files

The following implementation artifacts are authorized:

```text
tools/validate_machine_contract_passthrough_envelope.py

tests/test_machine_contract_passthrough_envelope_validator.py

research/machine_contract_passthrough_envelope_validator_implementation_results.json

research/machine_contract_passthrough_envelope_validator_implementation_report.md

research/machine_contract_passthrough_envelope_validator_implementation_review.md
```

If another implementation file is required, work must stop for authorization
revision.

## 4. Required Validator Capabilities

The validator must check:

```text
JSON parsing

Schema V1 validation

required section presence

authority boundary flags

canonical JSON hash recomputation

source hash equality

embedded contract hash equality

action equality

stop-state equality

reason_codes equality

blocking_items equality

NOT_EVALUATED equality

not_claimed equality

evidence reference equality

proof reference equality

producer identity equality

unified wrapper identity equality

contradiction class validity

critical contradiction implies fail_closed = true

critical contradiction implies compliance_status = FAIL

telemetry status/value consistency

telemetry cannot alter decision fields

sensitive-value absence
```

## 5. Canonical JSON Requirement

The validator must recompute canonical JSON for `embedded_contract`.

Required canonicalization:

```text
UTF-8
object keys sorted lexicographically
no insignificant whitespace
arrays preserved in order
strings preserved exactly
```

It must compare:

```text
sha256(canonical_json(embedded_contract))
```

against:

```text
machine_contract.canonical_contract_sha256
```

and compare that canonical hash to the expected manifest/source contract hash
where applicable.

Any mismatch must return:

```text
FAIL
```

## 6. Expected Validator Outcomes

The validator must return one of:

```text
PASS

FAIL

TOOL_ERROR
```

Rules:

```text
PASS:
schema and semantic checks pass

FAIL:
fixture is parseable but violates schema or semantic rules

TOOL_ERROR:
validator cannot complete because of an internal runtime/tool error
```

`FAIL` must not be collapsed into `TOOL_ERROR`.

## 7. Fixture Evaluation Gates

The implementation can be accepted only if:

```text
positive fixtures:
6 / 6 PASS

negative fixtures:
37 / 37 rejected correctly

contradiction classes:
14 / 14 detected correctly

false accepts:
0

false rejects:
0

fixture mutations:
0

deterministic repeated evaluation:
100%

schema validation:
PASS

manifest hash validation:
PASS
```

## 8. Sensitive-Value Handling

The validator must detect synthetic sensitive markers in:

```text
machine_contract

model_explanation

contradiction_analysis

telemetry
```

The accepted fixture corpus uses synthetic markers only. The validator must not
require or expose real sensitive values.

Any sensitive-value exposure fixture must return:

```text
FAIL
```

and:

```text
fail_closed = true
```

where the fixture expects fail-closed behavior.

## 9. Telemetry Handling

The validator must distinguish:

```text
AVAILABLE

NOT_EXPOSED

NOT_EVALUATED
```

It must reject:

```text
usage.status = NOT_EVALUATED with numeric usage values

timing.status = NOT_EXPOSED with duration values

tools.status = NOT_EVALUATED with tool counts

telemetry fields that attempt to alter or contradict decision fields
```

Unavailable telemetry must not be treated as zero.

## 10. Report Requirements

The implementation must produce:

```text
research/machine_contract_passthrough_envelope_validator_implementation_results.json

research/machine_contract_passthrough_envelope_validator_implementation_report.md
```

The results must include:

```text
schema

schema_version

status

fixture_count

pass_count

fail_count

tool_error_count

positive_pass_count

negative_rejected_count

false_accept_count

false_reject_count

contradiction_classes_detected

fixture_hash_mismatches

fixture_mutations_detected

deterministic_repeated_evaluation

not_authorized
```

The report must summarize the fixture results and explicitly preserve the
remaining authorization boundaries.

## 11. Review Requirements

The implementation review must verify:

```text
implementation stayed within authorized files

Schema V1 remained frozen

validator specification remained frozen

43 fixtures remained frozen

fixture manifest remained frozen

expected outcomes remained frozen

6 / 6 positive fixtures passed

37 / 37 negative fixtures failed as expected

14 / 14 contradiction classes were detected

false accepts = 0

false rejects = 0

fixture mutations = 0

repeated evaluation deterministic = 100%

focused tests passed

full pytest passed

no MVP integration occurred

no runner changes occurred

no prompt changes occurred

no live sessions occurred
```

## 12. Explicit Non-Authorization

This document does not authorize:

```text
MVP implementation

integration into mvp_unified.py

runner changes

prompt changes

comparator changes outside the validator

oracle changes

producer changes

schema changes

validator specification changes

fixture changes

new Claude sessions

new Codex sessions

DeepSeek sessions

revised readiness

primary benchmark

holdout

carryover

result reclassification

efficiency claim

merge to main

release

version bump

tag

PyPI publication
```

## 13. Terminal Verdict Options For Implementation Review

The implementation review should end with one of:

```text
MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_NEEDS_REVISION

MACHINE_CONTRACT_PASSTHROUGH_ENVELOPE_VALIDATOR_IMPLEMENTATION_REJECTED
```

Even `ACCEPTED` does not authorize MVP implementation.

## Final Boundary

This authorization opens only:

```text
deterministic envelope validator implementation

validator tests

fixture evaluation

implementation results/report

implementation review
```

It does not open:

```text
MVP integration

readiness

live benchmark

release
```
