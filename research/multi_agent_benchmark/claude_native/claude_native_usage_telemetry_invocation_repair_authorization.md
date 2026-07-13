# Claude Native Usage Telemetry Invocation Repair Authorization

## Status

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_AUTHORIZED
OUTPUT_FORMAT_JSON_REPAIR_ONLY
SIX_UNSCORED_TELEMETRY_PROBES_AUTHORIZED
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

The accepted runner-delta review records:

```text
HARDENED_RUNNER_OUTPUT_FORMAT_JSON_OMITTED
USAGE_TELEMETRY_INVOCATION_REPAIR_REQUIRED
```

The previous 20-session hardening diagnostic remains preserved:

```text
correctness evidence:
PRESERVED

Read permission hardening:
SUPPORTED

permission denials:
0

telemetry evidence:
NOT EVALUATED / UNAVAILABLE for those 20 sessions
```

## Authorized Repair

Exactly one runner invocation change is authorized:

```python
"--output-format",
"json",
```

The repair must preserve:

```text
--permission-mode dontAsk
--tools Read,Glob,Grep
--allowedTools Read,Glob,Grep
--disallowedTools Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*
--json-schema <unchanged inline canonical schema>
```

## Required Static Checks

Focused tests must verify:

```text
--output-format appears exactly once
its value is json
--json-schema remains present
--allowedTools remains present
--permission-mode remains dontAsk
stream-json is absent
```

The delta must remain:

```text
before repair:
--output-format absent

after repair:
--output-format json present

all other relevant invocation elements:
unchanged
```

## Authorized Probes

After repair, exactly 6 unscored telemetry probes are authorized:

```text
Read nonce:
3

Critical Arm B:
2

Matched Arm C:
1
```

## Acceptance Conditions

```text
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

forbidden tools:
0
```

Usage available means:

```text
usage object present
input tokens present and numeric
output tokens present and numeric
values non-negative
usage belongs to the same session/result envelope as the structured output
model identity present or explicitly resolved from the same response
```

Cache and cost fields may be:

```text
AVAILABLE
or
NOT_EXPOSED
```

## Forbidden

```text
stream-json fallback
primary benchmark execution
holdout execution
carryover execution
full 20-session hardening rerun
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

If the 6 probes pass, a later authorization may rerun the full 20-session
hardening diagnostic.

If usage does not return, a separate JSON-vs-stream-json telemetry diagnostic
may be considered.
