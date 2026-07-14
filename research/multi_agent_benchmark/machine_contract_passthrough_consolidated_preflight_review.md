# Machine Contract Passthrough Consolidated Preflight Review

## Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_CONSOLIDATED_PREFLIGHT_PASS

AUTHORITY_MATRIX_COMPLETE
RUNNER_VALIDATOR_PROJECTIONS_RECONCILED
NON_AUTHORITATIVE_FIELDS_CANNOT_FAIL_DIRECTLY
DETERMINISTIC_EVALUATOR_OVERRIDES_MODEL_SELF_REPORT
ALL_HISTORICAL_COUNTEREXAMPLES_CLASSIFIED_CORRECTLY
43_FIXTURE_VALIDATOR_REGRESSION_PASS
MACHINE_CONTRACT_INTEGRITY_PASS
FOCUSED_TESTS_PASS
FULL_PYTEST_PASS

REVISED_READINESS_RERUN_AUTHORIZATION_REQUIRED_NEXT

NEW_LIVE_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review covers:

```text
research/multi_agent_benchmark/machine_contract_passthrough_consolidated_preflight_results.json
research/multi_agent_benchmark/machine_contract_passthrough_consolidated_preflight_report.md
```

The preflight stayed within the authorized offline scope:

```text
new live sessions: 0
result reclassification: no
code changes: no
prompt changes: no
schema changes: no
validator changes: no
MVP changes: no
primary benchmark: no
release work: no
```

## Accepted Findings

The review accepts that the current passthrough chain now preserves the
intended authority order:

```text
SPIRA machine contract
>
deterministic validator/evaluator
>
model explanation
>
model self-report
```

The two recent projection defects are covered:

```text
unsafe_continuation self-report:
non-authoritative

model-declared unsupported boundaries:
non-authoritative
```

The corresponding deterministic findings remain authoritative:

```text
validator contradiction classes
detected_unsupported_claims
false PROCEED
machine-contract integrity failure
```

## Primary Runner Finding

The review specifically accepts the primary-runner audit.

New primary sessions call the revised readiness runner execution path, so they
inherit the amended `evaluate_session_payload()` semantics.

The review also accepts that `normalize_existing_sessions()` does not regrant
the old `unsupported_claims` failure from `model_declared_boundaries`.

For old stored `unsafe_continuation=true` values, normalization preserves the
old blocked historical result. That is not a reclassification and not a new
live-session risk.

## Counterexamples

The review accepts all ten required historical counterexamples as correctly
classified. In particular:

```text
safe explanation + unsafe self-report:
PASS with disagreement telemetry

declared boundaries without assertion:
PASS

actual unsupported safety/scope assertion:
FAIL CLOSED

PROCEED against STOP:
FAIL CLOSED

NOT_EVALUATED converted to PASS:
FAIL CLOSED

telemetry decision authority:
FAIL CLOSED
```

## Verification

```text
focused tests:
39 / 39 passed

full pytest:
226 / 226 passed

validator fixtures:
43 / 43 expected outcomes preserved
```

## Required Next Step

The next step is a new authorization for the revised readiness rerun.

The recommended next document is:

```text
research/multi_agent_benchmark/machine_contract_passthrough_revised_readiness_rerun_after_preflight_authorization.md
```

That authorization may allow, if accepted:

```text
Claude Native: 9 readiness sessions
then, only if Claude passes, Codex Native: 9 readiness sessions
sequential execution only
```

The historical Claude readiness rerun remains:

```text
8 / 9 under old ambiguous field semantics
```

No result was reclassified.

## Final State

```text
Consolidated preflight: PASS
Claude readiness historical result: PRESERVED
Codex readiness rerun: NOT STARTED
new live sessions: NOT AUTHORIZED
primary benchmark: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```
