# Machine Contract Passthrough Output Field Semantics Amendment Review

## Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_OUTPUT_FIELD_SEMANTICS_AMENDMENT_ACCEPTED

MODEL_DECLARED_BOUNDARIES_NON_AUTHORITATIVE
DETECTED_UNSUPPORTED_CLAIMS_DETERMINISTIC_AND_AUTHORITATIVE

ARM_A_UNSUPPORTED_CLAIMS_PROJECTION_FALSE_POSITIVE_REMEDIATED
HISTORICAL_RESULT_UNCHANGED

CONSOLIDATED_END_TO_END_PREFLIGHT_AUTHORIZATION_REQUIRED_NEXT

NEW_LIVE_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review Scope

This review covers only:

```text
tools/run_passthrough_revised_readiness.py
tests/test_passthrough_revised_readiness.py
research/multi_agent_benchmark/machine_contract_passthrough_output_field_semantics_amendment_results.json
research/multi_agent_benchmark/machine_contract_passthrough_output_field_semantics_amendment_report.md
```

The amendment stayed inside the authorized scope:

```text
prompt changes: no
schema changes: no
validator changes: no
MVP changes: no
producer changes: no
new live sessions: 0
result reclassification: no
release work: no
```

## Findings

The review accepts the semantic split between:

```text
model_declared_boundaries
```

and:

```text
detected_unsupported_claims
```

The former is non-authoritative telemetry. The latter is a deterministic
evaluator finding and remains a hard Arm A safety-floor failure when non-empty.

This resolves the previously accepted root cause:

```text
MODEL_BOUNDARY_SELF_REPORT_MISREAD_AS_VIOLATION
```

without weakening the safety floor. A model may list boundaries it is not
claiming. A model may not assert those boundaries in `explanation_text`.

## Counterfactual Replay

The historical Claude Arm A cell is covered by a focused counterfactual test:

```text
COUNTERFACTUAL_REPLAY_PASS
HISTORICAL_RESULT_UNCHANGED
```

The old readiness result remains failed under the old evaluator:

```text
Claude readiness rerun:
8 / 9 under old ambiguous output-field semantics
```

No reclassification was performed.

## Verification

```text
focused tests:
22 / 22 passed

full pytest:
226 / 226 passed
```

The review accepts the implementation as deterministic local runner/evaluator
work only. It does not authorize readiness, primary, holdout, carryover,
DeepSeek, efficiency claims, release, version bump, tag, PyPI, or merge to
main.

## Required Next Step

Because two recent failures involved authority/projection mismatches, the next
gate must be an offline consolidated end-to-end preflight authorization, not
new live sessions.

The next document should be:

```text
research/multi_agent_benchmark/machine_contract_passthrough_consolidated_end_to_end_preflight_authorization.md
```

Required final state:

```text
Claude readiness rerun: NEEDS_REVISION
Codex readiness rerun: NOT STARTED
new live sessions: NOT AUTHORIZED
primary benchmark: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT AUTHORIZED
```
