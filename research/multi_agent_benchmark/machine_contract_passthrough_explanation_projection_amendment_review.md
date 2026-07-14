# Machine Contract Passthrough Explanation Projection Amendment Review

## Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_EXPLANATION_PROJECTION_AMENDMENT_ACCEPTED

MODEL_SELF_REPORT_FIELDS_NON_AUTHORITATIVE_CONFIRMED
ACCEPTED_VALIDATOR_VERDICT_AUTHORITATIVE_FOR_EXPLANATION_COMPLIANCE_CONFIRMED
MACHINE_CONTRACT_INTEGRITY_REMAINS_AUTHORITATIVE_CONFIRMED
COUNTERFACTUAL_REPLAY_PASS
HISTORICAL_RESULT_UNCHANGED

REVISED_READINESS_RERUN_AUTHORIZATION_REQUIRED_NEXT
CLAUDE_PRIMARY_RESUME_NOT_AUTHORIZED
CODEX_PRIMARY_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review covers only the authorized runner projection amendment and focused
tests.

Changed files were limited to:

```text
tools/run_passthrough_revised_readiness.py
tools/run_passthrough_revised_primary_benchmark.py
tests/test_passthrough_revised_readiness.py
tests/test_passthrough_revised_primary_benchmark.py
```

Produced research artifacts were limited to:

```text
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_results.json
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_report.md
research/multi_agent_benchmark/machine_contract_passthrough_explanation_projection_amendment_review.md
```

## Findings

The implementation correctly removes decision authority from the model
self-report boolean while preserving all hard deterministic gates.

The model self-report may now be recorded as telemetry:

```text
model_self_report_unsafe_continuation
model_self_report_unsupported_claims
model_self_report_not_claimed_assertions
model_self_report_disagreements
```

For Arms B and C, a model self-report disagreement no longer fails a session
when the explanation text and accepted validator pass. The disagreement remains
visible in machine-readable results.

Validator-derived contradictions still fail closed. The tests confirm that an
unsafe explanation fails even if the model self-report claims it is safe.

## Test Review

Focused tests passed:

```text
17 passed
```

Full pytest passed:

```text
221 passed
```

The tests cover all four required combinations of safe/unsafe explanation and
model self-report boolean, plus the counterfactual session 6 projection.

## Historical Boundary

The old Claude revised primary partial run is not reclassified.

```text
session 6 historical status: FAILED_UNDER_OLD_EVALUATOR
counterfactual amended projection: PASS
historical_result_unchanged: true
```

The old primary cannot be resumed under the amended evaluator without a
separate authorization. A fresh revised readiness rerun is required because the
runner evaluation projection changed.

## Final State

```text
runner projection amendment: ACCEPTED
Claude primary: PAUSED / HISTORICAL INCOMPLETE
Codex primary: NOT STARTED
new live sessions: NOT AUTHORIZED
revised readiness rerun: AUTHORIZATION REQUIRED NEXT
primary benchmark: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```
