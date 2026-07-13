# Claude Native Usage Telemetry Runner Delta Analysis Authorization

## Status

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_RUNNER_DELTA_ANALYSIS_AUTHORIZED
EXISTING_RUNNER_AND_RESULTS_ANALYSIS_ONLY
NO_NEW_LIVE_SESSIONS

READ_PERMISSION_HARDENING_RESULTS_PRESERVED
PROMPTS_FROZEN
CASES_FROZEN
SCHEMA_FROZEN
COMPARATOR_FROZEN
MODEL_FROZEN
MVP_CODE_FROZEN

READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Analysis Question

Determine whether the loss of Claude Code usage metadata was caused by an
invocation delta between:

```text
tools/run_claude_native_readiness.py
```

and:

```text
tools/run_claude_native_read_invocation_hardening_diagnostic.py
```

## Required Comparison

Compare the complete Claude Code argv of both runners, including:

```text
--print
--no-session-persistence
--session-id
--model
--permission-mode
--output-format
--tools
--allowedTools
--disallowedTools
--strict-mcp-config
--no-chrome
--disable-slash-commands
--max-turns
--json-schema
```

## Required Findings

If the code comparison confirms the omission, the analysis must record:

```text
HARDENED_RUNNER_OUTPUT_FORMAT_JSON_OMITTED
BARE_STRUCTURED_JSON_OUTPUT_EXPLAINED_BY_DEFAULT_OUTPUT_MODE_CANDIDATE
USAGE_TELEMETRY_FAILURE_NOT_ATTRIBUTED_TO_ALLOWED_TOOLS
USAGE_TELEMETRY_INVOCATION_REPAIR_REQUIRED
```

The analysis must distinguish:

```text
proven:
--output-format json was omitted

strongly supported:
the omission explains bare structured JSON and missing usage envelope

not yet proven:
restoring the flag will restore usage in the hardened invocation
```

## Authorized Artifacts

```text
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_runner_delta_analysis.json
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_runner_delta_analysis.md
research/multi_agent_benchmark/claude_native/claude_native_usage_telemetry_runner_delta_analysis_review.md
```

No private raw response or private filesystem path may be published.

## Next Authorization Boundary

If accepted, the next authorization may permit exactly one runner change:

```text
add:
--output-format json
```

while preserving:

```text
--permission-mode dontAsk
--tools Read,Glob,Grep
--allowedTools Read,Glob,Grep
--disallowedTools Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*
```

No other invocation, prompt, case, schema, comparator, model, producer, or MVP
change is authorized.
