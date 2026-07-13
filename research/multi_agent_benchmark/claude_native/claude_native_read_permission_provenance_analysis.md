# Claude Native Read Permission Provenance Analysis

## Status

```text
CLAUDE_NATIVE_READ_PERMISSION_PROVENANCE_ANALYSIS_COMPLETE
READ_PERMISSION_DENIAL_RUNTIME_CONFIRMED
READ_INVOCATION_HARDENING_REQUIRED
NO_NEW_LIVE_SESSIONS
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Scope

Only the authorized failed session was inspected:

```text
role:
CRITICAL_ARM_B

repeat:
4

raw_private_id:
8fa32b5a-0b12-48b3-80c9-be10ff07905a

stdout SHA-256:
207e29e682158555b5c769f108b7601be3edb4ddf0b5fcf34db23a1e51319c77
```

No new live sessions were run.

## Public Telemetry Before Raw Inspection

The public diagnostic result showed:

```text
returncode:
0

tools_observed:
[]

stderr:
empty
```

Therefore, before private raw inspection, the only proven public fact was:

```text
Claude returned a valid structured answer claiming that Read permission was denied.
```

## Private Raw Provenance

The private raw stdout was inspected without publishing the raw response or the
private path.

The raw SHA-256 matched the recorded value.

The raw response contains a top-level `permission_denials` metadata field with:

```text
tool_name:
Read

tool_use_id:
present

tool_input.file_path:
present, redacted from public artifacts
```

The raw response does not contain separate stream-style `tool_use` or
`tool_result` events, and it does not contain a runtime error event. The
permission-denial provenance is therefore provided by the Claude Code JSON
result metadata, not by streamed tool events.

## Classification

This is stronger than a model-only textual claim.

The authoritative classification is now:

```text
READ_PERMISSION_DENIAL_RUNTIME_CONFIRMED
READ_INVOCATION_HARDENING_REQUIRED
```

## Boundary

```text
raw private response:
NOT PUBLISHED

private file path:
NOT PUBLISHED

prompts:
FROZEN

cases:
FROZEN

schema:
FROZEN

comparator:
FROZEN

MVP code:
FROZEN

primary benchmark:
NOT AUTHORIZED
```

## Next Step

A separate authorization is required for read invocation hardening. The
candidate change remains a harness invocation change only:

```text
existing:
--tools Read,Glob,Grep
--permission-mode dontAsk

candidate addition:
--allowedTools Read,Glob,Grep
```

No readiness rerun or primary benchmark is authorized by this analysis.
