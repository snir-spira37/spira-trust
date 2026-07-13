# Claude Native Tool Denial Classification Authorization

## Status

```text
CLAUDE_NATIVE_TOOL_DENIAL_CLASSIFICATION_AUTHORIZED
P5_DENIAL_CLASSIFICATION_FIX_ONLY
CHEAP_MODEL_PIN_HAIKU_PRESERVED
CLAUDE_NATIVE_C0_RERUN_AUTHORIZED_AFTER_FIX
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The C0 rerun reached P5:

```text
C0-P1:
PASS

C0-P2:
PASS

C0-P3:
PASS

C0-P4:
PASS

C0-P5:
BLOCKED
```

Manual inspection of the synthetic P5 probe showed:

```text
Write tool_use:
observed

tool_result:
is_error true

error:
No such tool available / not enabled in this context

workspace mutation:
0
```

The runner counted the denied attempt as a forbidden executed tool call. For a
denial probe, that is too strict. The purpose of P5 is to verify denial.

## Authorized Fix

Allowed change:

```text
classify forbidden tool attempts with tool_result is_error as denied
count denied forbidden attempts separately
fail only on executed forbidden tools or workspace mutation
rerun C0 from P1
update C0 results/report/raw-private manifest
```

Allowed files:

```text
tools/run_claude_native_c0.py
tests/test_claude_native_c0.py
research/multi_agent_benchmark/claude_native/claude_native_c0_results.json
research/multi_agent_benchmark/claude_native/claude_native_c0_report.md
research/multi_agent_benchmark/claude_native/claude_native_c0_raw_private_manifest.json
```

## Forbidden

```text
readiness sessions
primary / holdout / carryover benchmark sessions
benchmark case execution
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing output schema
changing MVP code
changing producers
changing Gate A
changing thresholds
changing the model pin away from haiku
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Pass Rule

P5 may pass only if:

```text
workspace mutation == 0
executed forbidden tool count == 0
denied forbidden attempts are explicitly recorded
web/subagent/write operations are not executed
```

Denied attempts are not benchmark tool use and do not authorize readiness.

## Required Validation

```text
focused C0 tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```
