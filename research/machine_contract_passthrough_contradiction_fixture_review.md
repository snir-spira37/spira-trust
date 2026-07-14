# Machine Contract Passthrough Contradiction Fixture Review

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURES_ACCEPTED

FIXTURE_MANIFEST_ACCEPTED

POSITIVE_CONTROL_FIXTURES_ACCEPTED

MACHINE_CONTRACT_INTEGRITY_NEGATIVE_FIXTURES_ACCEPTED

MODEL_EXPLANATION_CONTRADICTION_FIXTURES_ACCEPTED

TELEMETRY_NEGATIVE_FIXTURES_ACCEPTED

SENSITIVE_VALUE_NEGATIVE_FIXTURES_ACCEPTED

EXPECTED_OUTCOMES_COMPLETE

FIXTURE_HASHES_VERIFIED

DOMAIN_1_2_3_AND_GATE_A_SEMANTICS_PRESERVED

SCHEMA_V1_PRESERVED

VALIDATOR_SPECIFICATION_PRESERVED

VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED

MVP_IMPLEMENTATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review evaluates:

```text
research/machine_contract_passthrough_fixtures/

research/machine_contract_passthrough_fixtures/fixture_manifest.json
```

It does not authorize validator implementation, MVP implementation, live
sessions, readiness, primary benchmark execution, result reclassification, or
release.

## Fixture Corpus Summary

```text
fixture_count:
43

positive_fixture_count:
6

negative_fixture_count:
37

contradiction classes covered:
14 / 14
```

Fixture categories:

```text
positive/

machine_contract_integrity_failures/

model_explanation_contradictions/

telemetry_failures/

sensitive_value_failures/
```

## Manifest Review

Accepted.

The manifest includes:

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

Every fixture entry includes:

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

The manifest hashes were recomputed and matched all 43 fixture files.

## Positive Controls Review

Accepted.

The corpus includes six positive controls covering:

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

The positive fixtures preserve:

```text
machine_contract.authoritative = true

machine_contract.model_writable = false

model_explanation.authoritative = false

contradiction_analysis.model_writable = false

telemetry.decision_authority = NONE

source contract hash equality

canonical contract hash equality

fail_closed = false
```

Expected validator outcome:

```text
PASS
```

## Machine-Contract Integrity Negative Fixtures Review

Accepted.

The corpus includes one fixture for each required integrity failure:

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

Expected validator outcome:

```text
FAIL
```

These fixtures are sufficient to test that the future validator fails closed
when the authoritative machine contract is altered, weakened, or detached from
its canonical hash.

## Model-Explanation Contradiction Fixtures Review

Accepted.

The corpus covers all accepted contradiction classes:

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

Each contradiction fixture declares:

```text
expected_contradiction_classes

expected_fail_closed

expected_validator_outcome
```

Expected validator outcome:

```text
FAIL
```

The fixtures are sufficient to test that a non-authoritative explanation cannot
override, weaken, or contradict the machine contract.

## Telemetry Negative Fixtures Review

Accepted.

The corpus includes four telemetry failures:

```text
usage.status = NOT_EVALUATED with numeric usage value

timing.status = NOT_EXPOSED with duration value

tools.status = NOT_EVALUATED with tool count

telemetry attempts to add a decision override field
```

Expected validator outcome:

```text
FAIL
```

These fixtures are sufficient to prove that unavailable telemetry cannot be
silently represented as zero and telemetry cannot become a decision channel.

## Sensitive-Value Negative Fixtures Review

Accepted.

The corpus includes four synthetic sensitive-value failures:

```text
synthetic sensitive marker in machine_contract

synthetic sensitive marker in model_explanation

synthetic sensitive marker in contradiction_analysis

synthetic sensitive marker in telemetry
```

No real credentials or real private values are present. The fixtures use
synthetic marker values only.

Expected validator outcome:

```text
FAIL
```

These fixtures are sufficient to test the Domain 3 sensitive-value boundary
without exposing real sensitive material.

## Frozen Boundary Review

Accepted.

The fixture corpus does not alter:

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

No schema revision or validator-spec revision occurred.

## Implementation Boundary Review

Accepted.

No validator implementation occurred.

No MVP implementation occurred.

No runner, prompt, comparator, oracle, or producer changes occurred.

No live sessions occurred.

## Final Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_CONTRADICTION_FIXTURES_ACCEPTED

FIXTURE_MANIFEST_ACCEPTED

POSITIVE_CONTROL_FIXTURES_ACCEPTED

MACHINE_CONTRACT_INTEGRITY_NEGATIVE_FIXTURES_ACCEPTED

MODEL_EXPLANATION_CONTRADICTION_FIXTURES_ACCEPTED

TELEMETRY_NEGATIVE_FIXTURES_ACCEPTED

SENSITIVE_VALUE_NEGATIVE_FIXTURES_ACCEPTED

EXPECTED_OUTCOMES_COMPLETE

FIXTURE_HASHES_VERIFIED

VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED

MVP_IMPLEMENTATION_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_RESULT_RECLASSIFICATION

NO_PRIMARY_BENCHMARK

RELEASE_NOT_AUTHORIZED
```

## Next Artifact

The next artifact should be:

```text
research/machine_contract_passthrough_envelope_validator_implementation_authorization.md
```

It should authorize only implementation of the validator against the accepted
schema, validator specification, and fixture corpus. It must not authorize MVP
implementation or live sessions.
