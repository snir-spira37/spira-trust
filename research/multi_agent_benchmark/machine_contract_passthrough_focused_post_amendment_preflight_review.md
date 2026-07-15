# Machine Contract Passthrough Focused Post-Amendment Preflight Review

## Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_FOCUSED_POST_AMENDMENT_PREFLIGHT_PASS

MODEL_SELF_REPORT_FIELDS_NON_AUTHORITATIVE_CONFIRMED
RUNNER_VALIDATOR_PROJECTIONS_RECONCILED
DETERMINISTIC_FAILURE_GATES_CONFIRMED
AUTHORIZED_ARTIFACT_PROVENANCE_GATE_CONFIRMED
SOURCE_AND_FROZEN_ASSET_MUTATION_GATE_CONFIRMED
HISTORICAL_COUNTEREXAMPLES_REPLAYED_WITHOUT_RECLASSIFICATION
VALIDATOR_43_FIXTURE_REGRESSION_PASS
FOCUSED_TESTS_PASS
FULL_PYTEST_PASS

POST_AMENDMENT_READINESS_RERUN_AUTHORIZATION_REQUIRED_NEXT

NO_NEW_LIVE_SESSIONS
NO_RESULT_RECLASSIFICATION
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review

The focused post-amendment preflight is accepted.

It verified the updated authority model after the self-report authority
amendment and did not modify code, prompts, schemas, validators, fixtures,
oracles, producers, the MVP implementation, cases, randomization, or historical
results.

## Accepted Findings

The following are accepted:

```text
model recommended_agent_action is telemetry only
model stop is telemetry only
model unsafe_continuation is telemetry only
model declared boundaries are telemetry only
model not_claimed_assertions are telemetry only
model evidence/proof self-report is telemetry only
```

Authoritative gates remain:

```text
machine-contract integrity
accepted validator verdict
deterministic explanation contradiction detection
deterministic unsafe-continuation detection
deterministic unsupported-claim detection
deterministic NOT_EVALUATED / not_claimed violation detection
deterministic fabricated evidence/proof detection
forbidden tool use
workspace mutation
unauthorized source/frozen-asset mutation
```

Authorized result, manifest, checkpoint, report, review, raw-private manifest,
agent-order, and combined-review artifacts are not repository mutation.

## Historical Results

The historical Claude post-preflight primary attempt remains unchanged:

```text
CLAUDE_NATIVE_PASSTHROUGH_REVISED_PRIMARY_NEEDS_REVISION
completed sessions: 7 / 180
```

The preflight provides counterfactual evidence that the runner now handles the
three analyzed findings correctly, but it does not convert the old run to pass
and does not authorize resuming from session 8.

## Validation

The validator regression passed:

```text
43 / 43 fixtures
14 / 14 contradiction classes
false accepts: 0
false rejects: 0
```

Focused tests passed:

```text
30 passed
```

Full pytest passed:

```text
234 passed
```

## Required Next Step

The next step is a separate post-amendment readiness rerun authorization.

That authorization should preserve:

```text
fresh sessions only
Claude first
Codex only if Claude passes
shared accepted evaluator
accepted validator
Envelope Schema V1
accepted MVP passthrough implementation
no primary benchmark
no result reclassification
```

No live readiness session, primary benchmark, holdout, carryover, DeepSeek
track, efficiency claim, release, version bump, tag, PyPI upload, or merge to
main is authorized by this review.
