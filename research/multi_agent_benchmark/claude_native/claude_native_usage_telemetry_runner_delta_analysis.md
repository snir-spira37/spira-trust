# Claude Native Usage Telemetry Runner Delta Analysis

## Status

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_RUNNER_DELTA_ANALYSIS_COMPLETE
HARDENED_RUNNER_OUTPUT_FORMAT_JSON_OMITTED
USAGE_TELEMETRY_ROOT_CAUSE_CANDIDATE_IDENTIFIED
READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Question

Determine whether the loss of usage telemetry in the hardened diagnostic was
caused by a runner invocation delta rather than by `--allowedTools` itself or a
general Claude Code telemetry failure.

## Compared Runners

```text
baseline readiness runner:
tools/run_claude_native_readiness.py

hardened diagnostic runner:
tools/run_claude_native_read_invocation_hardening_diagnostic.py
```

## Static Invocation Delta

The baseline readiness runner includes:

```text
--permission-mode
dontAsk

--output-format
json

--tools
Read,Glob,Grep

--json-schema
<inline canonical schema>
```

The hardened diagnostic runner includes:

```text
--permission-mode
dontAsk

--tools
Read,Glob,Grep

--allowedTools
Read,Glob,Grep

--json-schema
<inline canonical schema>
```

but omits:

```text
--output-format
json
```

## Findings

```text
HARDENED_RUNNER_OUTPUT_FORMAT_JSON_OMITTED
BARE_STRUCTURED_JSON_OUTPUT_EXPLAINED_BY_DEFAULT_OUTPUT_MODE_CANDIDATE
USAGE_TELEMETRY_FAILURE_NOT_ATTRIBUTED_TO_ALLOWED_TOOLS
USAGE_TELEMETRY_INVOCATION_REPAIR_REQUIRED
```

## Evidence From Prior Results

The hardened diagnostic preserved the important correctness and permission
results:

```text
schema valid:
20 / 20

correct:
20 / 20

permission denials:
0

usage available:
0 / 20
```

Private inspection during the hardening review observed bare structured JSON
without the Claude Code result envelope. The static delta explains why: the
hardened runner did not request `--output-format json`.

## Methodological Distinction

Proven:

```text
--output-format json was omitted from the hardened runner
```

Strongly supported:

```text
the omission explains bare structured JSON and missing usage envelope
usage telemetry failure is not currently attributable to --allowedTools
```

Not yet proven:

```text
restoring --output-format json will restore usage under the hardened invocation
```

## Boundary

```text
new live sessions:
0

prompts / cases / schema / comparator / model / MVP:
unchanged

readiness rerun:
NOT AUTHORIZED

primary benchmark:
NOT AUTHORIZED

efficiency claim:
NOT AUTHORIZED
```

## Next Candidate Authorization

The next authorization may permit exactly one runner change:

```python
"--output-format",
"json",
```

while preserving:

```text
--permission-mode dontAsk
--tools Read,Glob,Grep
--allowedTools Read,Glob,Grep
--disallowedTools Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*
--json-schema <unchanged inline canonical schema>
```

The first diagnostic after repair should be a small 6-session telemetry probe:

```text
Read nonce:
3

Critical Arm B:
2

Matched Arm C:
1
```

`stream-json` remains a separate fallback path and is not the next authorized
repair candidate.
