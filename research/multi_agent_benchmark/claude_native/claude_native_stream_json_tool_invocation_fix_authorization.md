# Claude Native Stream-JSON Tool Invocation Fix Authorization

## Status

```text
CLAUDE_NATIVE_STREAM_JSON_TOOL_INVOCATION_FIX_AUTHORIZED
P4_P5_INVOCATION_FIX_ONLY
CHEAP_MODEL_PIN_HAIKU_PRESERVED
CLAUDE_NATIVE_C0_RERUN_AUTHORIZED_AFTER_FIX
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The model identity revision allowed C0 to reach P4:

```text
C0-P1 authentication/model identity:
PASS

C0-P2 init/tool inventory:
PASS

C0-P3 structured output:
PASS

C0-P4 read-only tool execution:
BLOCKED
```

The observed P4 stderr was a Claude Code invocation requirement:

```text
When using --print, --output-format=stream-json requires --verbose
```

P2 already used `--verbose`. P4 and P5 did not.

## Authorized Fix

Allowed change:

```text
add --verbose to C0-P4 read-only tool probe
add --verbose to C0-P5 denial/isolation probe
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

## Required Validation

```text
focused C0 tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```

## Next Required Artifact

After the rerun:

```text
research/multi_agent_benchmark/claude_native/claude_native_c0_final_review.md
```

Only if C0 passes and the review accepts the result may a later document
authorize the nine Claude native readiness sessions.
