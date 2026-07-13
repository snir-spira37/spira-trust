# Claude Native Usage Telemetry Invocation Repair Probe Review

## Status

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_ACCEPTED
OUTPUT_FORMAT_JSON_REPAIR_CONFIRMED
JSON_RESULT_ENVELOPE_RESTORED
USAGE_TELEMETRY_RESTORED
READ_PERMISSION_HARDENING_PRESERVED
FULL_TWENTY_SESSION_HARDENING_RERUN_AUTHORIZED_NEXT
READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
authorization:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_invocation_repair_authorization.md

results:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_invocation_repair_probe_results.json

report:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_invocation_repair_probe_report.md

raw manifest:
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_invocation_repair_probe_raw_private_manifest.json
```

## Scope Check

```text
authorized runner repair:
--output-format json

new live sessions:
6

primary benchmark sessions:
0

readiness rerun sessions:
0

prompts / cases / schema / comparator / model / MVP:
unchanged
```

## Results

```text
Read nonce:
3 / 3

Critical Arm B:
2 / 2

Matched Arm C:
1 / 1

JSON result envelope present:
6 / 6

structured_output present:
6 / 6

schema valid:
6 / 6

correct:
6 / 6

usage available:
6 / 6

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

## Findings

Restoring:

```text
--output-format json
```

restored the Claude Code JSON result envelope and usage telemetry while
preserving the earlier read-permission hardening.

The root-cause candidate from the static runner-delta analysis is confirmed for
the six authorized probes.

## Verdict

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_ACCEPTED
```

## Next Authorized State

This review does not authorize a 9-cell readiness rerun or primary benchmark.

The next document may authorize rerunning the full 20-session hardening
diagnostic with the repaired invocation:

```text
Read nonce:
5 / 5

Critical Arm B:
10 / 10

Matched Arm C:
5 / 5

usage:
20 / 20
```

Only after that review may a separate authorization consider a full 9-cell
readiness rerun.
