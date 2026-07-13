# Claude Native Session Nonce Schema Fix Authorization

## Status

```text
CLAUDE_NATIVE_SESSION_NONCE_SCHEMA_FIX_AUTHORIZED
P6_SESSION_PROBE_FIX_ONLY
CHEAP_MODEL_PIN_HAIKU_PRESERVED
CLAUDE_NATIVE_C0_RERUN_AUTHORIZED_AFTER_FIX
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The latest C0 rerun passed all gates except session isolation:

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
PASS

C0-P7:
PASS

C0-P6:
nonce not present
```

Both session probes had distinct session IDs and usage accounting, but the
model did not echo the nonce in free-form JSON output.

## Authorized Fix

Allowed change:

```text
use inline canonical JSON schema for C0-P6 session nonce probes
require the exact nonce with a schema const
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
