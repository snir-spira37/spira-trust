# Claude Native Readiness Schema Transport Fix Authorization

## Status

```text
CLAUDE_NATIVE_READINESS_SCHEMA_TRANSPORT_FIX_AUTHORIZED
READINESS_TRANSPORT_FIX_ONLY
NINE_READINESS_SESSIONS_RERUN_AUTHORIZED_AFTER_FIX
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorized Fix

Allowed change:

```text
derive a Claude transport schema from agent_output.schema.json
remove only the top-level $schema field from the transported copy
verify semantic fields remain unchanged
rerun exactly the 9 Claude native readiness sessions
```

Allowed files:

```text
tools/run_claude_native_readiness.py
tests/test_claude_native_readiness.py
research/multi_agent_benchmark/claude_native/claude_native_readiness_results.json
research/multi_agent_benchmark/claude_native/claude_native_readiness_report.md
research/multi_agent_benchmark/claude_native/claude_native_readiness_raw_private_manifest.json
```

## Forbidden

```text
changing agent_output.schema.json
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing MVP code
changing producers
changing thresholds
primary / holdout / carryover execution
efficiency claims
release / version / tag / PyPI
```

## Required Validation

```text
focused readiness tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```
