# Claude Native Read Invocation Hardening Rerun Authorization

## Status

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_RERUN_AUTHORIZED
FULL_TWENTY_SESSION_HARDENING_RERUN_ONLY
REPAIRED_JSON_OUTPUT_INVOCATION_REQUIRED
MODEL_FROZEN
PROMPTS_FROZEN
CASES_FROZEN
SCHEMA_FROZEN
COMPARATOR_FROZEN
MVP_CODE_FROZEN
READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The accepted usage telemetry repair probe records:

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_ACCEPTED
OUTPUT_FORMAT_JSON_REPAIR_CONFIRMED
JSON_RESULT_ENVELOPE_RESTORED
USAGE_TELEMETRY_RESTORED
READ_PERMISSION_HARDENING_PRESERVED
```

The next gate is a full rerun of the previously authorized 20-session hardening
diagnostic using the repaired invocation.

## Required Invocation

The runner must use:

```text
--permission-mode dontAsk
--output-format json
--tools Read,Glob,Grep
--allowedTools Read,Glob,Grep
--disallowedTools Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*
--json-schema <unchanged inline canonical schema>
```

## Authorized Sessions

Exactly 20 unscored diagnostic sessions are authorized:

```text
Read nonce technical probes:
5

Critical Arm B:
pytest_result synthetic_clean_success arm B
10

Matched Arm C:
pytest_result synthetic_clean_success arm C
5
```

## Acceptance Conditions

```text
Read nonce confirmed:
5 / 5

Critical Arm B exact:
10 / 10

Matched Arm C exact:
5 / 5

JSON result envelope present:
20 / 20

structured_output present:
20 / 20

schema valid:
20 / 20

usage available:
20 / 20

permission denials:
0

false PROCEED:
0

workspace mutations:
0

repository mutations:
0

forbidden tools:
0
```

## Authorized Files

```text
tools/run_claude_native_read_invocation_hardening_diagnostic.py
tests/test_claude_native_read_invocation_hardening_diagnostic.py
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_results.json
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_report.md
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_raw_private_manifest.json
```

## Forbidden

```text
primary benchmark execution
holdout execution
carryover execution
9-cell readiness rerun
prompt changes
case changes
schema changes
comparator changes
model changes
MVP code changes
producer changes
threshold changes
publishing raw private responses
publishing private raw paths
efficiency claim
release / version / tag / PyPI
```

## Next Boundary

If the 20-session hardening rerun is accepted, a later authorization may permit
a full 9-cell Claude native readiness rerun.
