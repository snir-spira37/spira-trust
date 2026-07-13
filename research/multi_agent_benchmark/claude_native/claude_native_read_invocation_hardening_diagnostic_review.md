# Claude Native Read Invocation Hardening Diagnostic Review

## Status

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_NEEDS_REVISION
READ_INVOCATION_HARDENING_DIAGNOSTIC_REVIEW_COMPLETE
READ_GLOB_GREP_PERMISSION_CONFIGURATION_SUPPORTED
READ_PERMISSION_DENIALS_ZERO
USAGE_ACCOUNTING_NOT_AVAILABLE_UNDER_HARDENED_JSON_INVOCATION
FULL_NINE_CELL_READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
authorization:
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_authorization.md

results:
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_results.json

report:
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_report.md

raw manifest:
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_raw_private_manifest.json
```

## Scope Check

```text
diagnostic sessions:
20 / 20

primary benchmark sessions:
0

readiness rerun sessions:
0

prompts / cases / schema / comparator / model / MVP:
unchanged
```

## Results

```text
Read nonce confirmed:
5 / 5

Critical Arm B exact:
10 / 10

Matched Arm C exact:
5 / 5

schema valid:
20 / 20

permission denials:
0

false PROCEED:
0

workspace mutations:
0

repository mutations:
0

forbidden tool calls:
0
```

The hardening candidate is strongly supported:

```text
--allowedTools Read,Glob,Grep
```

eliminated the previously confirmed Read permission denial across the 20
authorized diagnostic sessions.

## Blocking Finding

The diagnostic does not pass because usage accounting was not available:

```text
usage available:
0 / 20
```

Private inspection of one diagnostic raw stdout confirmed the output was a bare
structured JSON object rather than the Claude Code result envelope containing
usage metadata.

This is a telemetry/harness compatibility blocker, not a SPIRA correctness
failure and not a Read permission failure.

## Verdict

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_DIAGNOSTIC_NEEDS_REVISION
```

The read invocation hardening is not accepted yet because all acceptance
conditions included usage availability.

## Next State

A separate authorization is required to diagnose usage telemetry under the
hardened invocation. The most likely narrow diagnostic is to compare:

```text
--output-format json
--output-format stream-json
```

under the same hardened tool permission configuration, without changing
prompts, cases, schema, comparator, model, or MVP code.

Until then:

```text
full nine-cell readiness rerun:
NOT AUTHORIZED

primary benchmark:
NOT AUTHORIZED

efficiency claim:
NOT AUTHORIZED

release:
NOT AUTHORIZED
```
