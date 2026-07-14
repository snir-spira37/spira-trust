# Machine Contract Passthrough Contradiction Fixture Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURE_DESIGN_AUTHORIZED

SCHEMA_V1_FIXTURES_ONLY

POSITIVE_CONTROL_FIXTURES_AUTHORIZED

MACHINE_CONTRACT_INTEGRITY_NEGATIVE_FIXTURES_AUTHORIZED

MODEL_EXPLANATION_CONTRADICTION_FIXTURES_AUTHORIZED

TELEMETRY_NEGATIVE_FIXTURES_AUTHORIZED

SENSITIVE_VALUE_NEGATIVE_FIXTURES_AUTHORIZED

EXPECTED_OUTCOMES_REQUIRED

FIXTURE_MANIFEST_REQUIRED

FIXTURE_REVIEW_REQUIRED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_FROZEN

SCHEMA_V1_FROZEN

VALIDATOR_SPECIFICATION_FROZEN

VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED

MVP_IMPLEMENTATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

HOLDOUT_NOT_AUTHORIZED

CARRYOVER_NOT_AUTHORIZED

EFFICIENCY_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes design and materialization of fixtures for the accepted
machine-contract passthrough envelope schema and validator specification.

The fixture corpus must prove that:

```text
valid passthrough envelopes can pass;

machine-contract mutations are detected;

model-explanation contradictions are detected;

telemetry status/value conflicts are detected;

sensitive-value exposure is detected;

expected outcomes are explicit and reviewable before validator implementation.
```

This authorization does not authorize validator implementation, MVP
implementation, runner changes, prompt changes, live sessions, readiness,
primary benchmark execution, result reclassification, or release work.

## 2. Authorized Artifacts

The following artifacts are authorized:

```text
research/machine_contract_passthrough_fixtures/

research/machine_contract_passthrough_fixtures/fixture_manifest.json

research/machine_contract_passthrough_fixtures/README.md

research/machine_contract_passthrough_fixtures/positive/*.json

research/machine_contract_passthrough_fixtures/machine_contract_integrity_failures/*.json

research/machine_contract_passthrough_fixtures/model_explanation_contradictions/*.json

research/machine_contract_passthrough_fixtures/telemetry_failures/*.json

research/machine_contract_passthrough_fixtures/sensitive_value_failures/*.json

research/machine_contract_passthrough_contradiction_fixture_review.md
```

If a different fixture directory is required, work must stop for authorization
revision.

## 3. Required Fixture Metadata

Every fixture must include or be listed in the manifest with:

```text
fixture_id

classification

domain

expected_schema_result

expected_semantic_result

expected_validator_outcome

expected_contradiction_classes

expected_fail_closed

expected_reason_codes

source_contract_sha256

envelope_sha256

source_schema

schema_version
```

Expected outcomes must be explicit. A fixture without an expected outcome is
not accepted.

## 4. Positive Controls

The fixture corpus must include positive controls proving that valid envelopes
can pass.

Required coverage:

```text
Domain 1 valid passthrough

Domain 2 valid passthrough

Domain 3 valid passthrough

TEXT_ONLY explanation

STRUCTURED_TEXT explanation

telemetry AVAILABLE

telemetry NOT_EXPOSED

telemetry NOT_EVALUATED
```

Minimum count:

```text
3 to 6 positive fixtures
```

Positive fixtures must preserve:

```text
machine_contract.authoritative = true

machine_contract.model_writable = false

model_explanation.authoritative = false

contradiction_analysis.model_writable = false

telemetry.decision_authority = NONE

source contract hash equality

canonical contract hash equality

explicit-list equality

fail_closed = false
```

## 5. Machine-Contract Integrity Negative Fixtures

The fixture corpus must include at least one negative fixture for each
machine-contract integrity check.

Required failures:

```text
machine_contract.authoritative = false

machine_contract.model_writable = true

source hash mismatch

canonical hash mismatch

embedded contract mutation

action drift

stop-state drift

reason_codes drift

blocking_items drift

NOT_EVALUATED drift

not_claimed drift

evidence-reference drift

proof-reference drift

producer identity drift

unified identity drift
```

Expected outcome:

```text
expected_validator_outcome: FAIL
```

These fixtures must not require changes to Domain 1, Domain 2, Domain 3, or
Gate A semantics.

## 6. Model-Explanation Contradiction Fixtures

The fixture corpus must include at least one negative fixture for each accepted
contradiction class.

Required contradiction classes:

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

Each fixture must specify:

```text
expected_contradiction_classes

severity

expected_fail_closed

expected_validator_outcome
```

Critical or safety/scope contradictions must require:

```text
expected_fail_closed: true

expected_validator_outcome: FAIL
```

## 7. Telemetry Negative Fixtures

The fixture corpus must include at least three telemetry failures.

Required examples:

```text
usage.status = NOT_EVALUATED
but numeric usage values exist

timing.status = NOT_EXPOSED
but duration values exist

tools.status = NOT_EVALUATED
but tool count exists

telemetry modifies or contradicts decision fields
```

Unavailable telemetry must be represented explicitly and must not be invented
as zero.

Expected outcome:

```text
expected_validator_outcome: FAIL
```

## 8. Sensitive-Value Negative Fixtures

The fixture corpus must include at least three sensitive-value failures,
especially for Terraform-style evidence boundaries.

Required examples:

```text
plaintext sensitive value in machine_contract

plaintext sensitive value in model_explanation

credential-like value in contradiction_analysis

token-like value in telemetry
```

Allowed positive representations:

```text
sensitive structural paths

redacted references

non-revealing hashes/fingerprints
```

Sensitive-value negative fixtures must not contain real credentials or real
private values. They must use synthetic marker values only.

## 9. Manifest Requirements

The manifest must include:

```text
schema

schema_version

status

fixture_count

positive_fixture_count

negative_fixture_count

fixtures

coverage_summary

not_authorized
```

The manifest must prove coverage for:

```text
positive controls

machine-contract integrity failures

model-explanation contradiction classes

telemetry failures

sensitive-value failures
```

The manifest must include hashes for all fixture files.

## 10. Review Requirements

The fixture review must verify:

```text
all required fixture categories exist

every fixture has explicit expected outcomes

manifest hashes match fixture files

positive controls are valid schema examples

negative fixtures target the intended failure only where possible

no real sensitive values are present

Domain 1, Domain 2, Domain 3, and Gate A semantics remain frozen

Schema V1 remains frozen

validator specification remains frozen

no validator implementation occurred

no MVP implementation occurred

no live sessions occurred
```

## 11. Frozen Boundaries

The following remain frozen:

```text
Domain 1 behavior and baseline history

Domain 2 corpus, oracle, validator, and producer semantics

Domain 3 corpus, oracle, validator, and producer semantics

Gate A proof assembly semantics

SPIRA_DECISION_SEMANTICS_V2

action/status enums

machine_contract_passthrough_envelope_schema_v1.schema.json

machine_contract_passthrough_envelope_validator_spec.md

old Claude results

old Codex results

old benchmark artifacts
```

Fixtures must exercise the accepted schema and validator specification. They
must not revise either one.

## 12. Explicit Non-Authorization

This document does not authorize:

```text
validator implementation

MVP implementation

changes to mvp_unified.py

runner changes

prompt changes

comparator changes

oracle changes

producer changes

schema changes

validator specification changes

new Claude sessions

new Codex sessions

DeepSeek sessions

readiness

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

## 13. Completion Gates

The authorized fixture phase completes only if:

```text
fixture manifest exists

positive fixtures exist

machine-contract integrity negative fixtures exist

model-explanation contradiction fixtures exist

telemetry negative fixtures exist

sensitive-value negative fixtures exist

all expected outcomes are explicit

fixture review exists

review accepts, rejects, or requests revision

no validator implementation occurred

no MVP implementation occurred

no live sessions occurred
```

## 14. Terminal Verdict Options For Fixture Review

The fixture review should end with one of:

```text
MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURES_ACCEPTED

MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURES_NEED_REVISION

MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURES_REJECTED
```

Even `ACCEPTED` does not authorize validator implementation.

## Final Boundary

This authorization opens only:

```text
fixture design

fixture materialization

fixture manifest

fixture review
```

It does not open:

```text
validator implementation

MVP implementation

readiness

live benchmark

release
```
