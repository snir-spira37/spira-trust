# Machine Contract Passthrough Model Self-Report Authority Amendment Review

## Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_MODEL_SELF_REPORT_AUTHORITY_AMENDMENT_ACCEPTED

MODEL_ACTION_SELF_REPORT_NON_AUTHORITATIVE
MODEL_STOP_SELF_REPORT_NON_AUTHORITATIVE
MODEL_SAFETY_SELF_REPORT_NON_AUTHORITATIVE
MODEL_DECLARED_BOUNDARIES_NON_AUTHORITATIVE

MACHINE_CONTRACT_ACTION_AUTHORITATIVE
MACHINE_CONTRACT_STOP_STATE_AUTHORITATIVE
ACCEPTED_VALIDATOR_VERDICT_AUTHORITATIVE
DETERMINISTIC_EXPLANATION_EVALUATION_AUTHORITATIVE

AUTHORIZED_ARTIFACT_WRITES_EXCLUDED_FROM_REPOSITORY_MUTATION_GATE
UNAUTHORIZED_SOURCE_OR_FROZEN_ASSET_MUTATION_REMAINS_FAIL_CLOSED

HISTORICAL_RESULTS_PRESERVED
NO_RESULT_RECLASSIFICATION
NO_NEW_LIVE_SESSIONS

FOCUSED_POST_AMENDMENT_CONSOLIDATED_PREFLIGHT_AUTHORIZATION_REQUIRED_NEXT

CLAUDE_PRIMARY_RESUME_NOT_AUTHORIZED
CODEX_PRIMARY_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review

The amendment is accepted as a narrow runner/evaluator correction.

The implementation stayed within the authorized file set:

```text
tools/run_passthrough_revised_readiness.py
tools/run_passthrough_revised_primary_benchmark.py
tests/test_passthrough_revised_readiness.py
tests/test_passthrough_revised_primary_benchmark.py
```

The implementation created only the authorized results, report, and review
artifacts for this amendment.

## Authority Boundary

The reviewed implementation enforces the intended separation:

```text
machine contract and deterministic validator/evaluator:
authoritative

model-generated action, stop, safety, declared-boundary, and evidence
self-report fields:
non-authoritative telemetry
```

Model self-report disagreements are recorded and counted, but they do not
directly produce hard failure codes when the explanation text and authoritative
machine contract pass.

## Repository Mutation Gate

The primary runner now distinguishes authorized benchmark output writes from
unauthorized repository mutation.

Accepted behavior:

```text
authorized result/manifest/checkpoint/report/review writes:
not repository mutation

source, prompt, schema, validator, fixture, oracle, producer, MVP, frozen
asset, or historical-result mutation:
still visible to the mutation gate
```

## Test Review

Focused tests passed:

```text
30 passed
```

Full pytest passed:

```text
234 passed
```

The tests cover all required counterexamples, including both historical Claude
post-preflight primary non-pass sessions and the authorized-artifact mutation
finding.

## Preserved History

The old Claude post-preflight primary attempt remains historical:

```text
CLAUDE_NATIVE_PASSTHROUGH_REVISED_PRIMARY_NEEDS_REVISION
completed sessions: 7 / 180
```

This amendment does not resume it, complete it, or convert it to pass.

## Required Next Step

Before any new live session, a focused post-amendment consolidated preflight
authorization is required.

That preflight should verify:

```text
all model self-report fields are non-authoritative in readiness and primary
deterministic text analysis remains fail-closed
validator failures remain fail-closed
authorized artifact writes are excluded from mutation failures
source/frozen-asset writes remain mutation failures
historical counterexamples replay as expected without reclassification
```

No readiness rerun, primary benchmark, efficiency claim, release, version bump,
tag, PyPI upload, or merge to main is authorized by this review.
