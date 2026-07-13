# Claude Native Readiness Blocked Review

## Status

```text
CLAUDE_NATIVE_READINESS_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
READINESS_SESSIONS_EXECUTED_9_OF_9
SCHEMA_TRANSPORT_DEFECT_CONFIRMED
CLAUDE_JSON_SCHEMA_DRAFT_URI_NOT_SUPPORTED_IN_CLI_TRANSPORT
READINESS_SCHEMA_TRANSPORT_FIX_REQUIRED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
readiness commit:
8b54423

results:
research/multi_agent_benchmark/claude_native/claude_native_readiness_results.json

report:
research/multi_agent_benchmark/claude_native/claude_native_readiness_report.md
```

## Verdict

```text
CLAUDE_NATIVE_READINESS_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
```

The readiness result is accepted as a factual blocked run.

All 9 authorized readiness sessions were started, but all failed before agent
output because Claude Code rejected the transported schema.

## Blocking Finding

Synthetic diagnosis confirmed the invocation defect:

```text
--json-schema with the frozen schema object:
FAIL

error:
no schema with key or ref "https://json-schema.org/draft/2020-12/schema"
```

The frozen schema file is valid for repository validation, but Claude Code's
`--json-schema` transport does not accept the `$schema` draft URI in this
context.

## Boundary Preserved

```text
primary benchmark:
NOT STARTED

holdout / carryover:
NOT STARTED

MVP code:
UNCHANGED

frozen schema file:
UNCHANGED

efficiency claim:
NOT AUTHORIZED
```

## Next Required Fix

The next fix must be narrow:

```text
derive a transport schema from the frozen output schema
remove only $schema from the transported copy
preserve required/additionalProperties/enums/properties
record schema_transport_semantics_changed = false
rerun the same 9 readiness sessions
```
