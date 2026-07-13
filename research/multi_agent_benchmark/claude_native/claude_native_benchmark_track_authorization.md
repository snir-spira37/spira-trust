# Claude Native Benchmark Track Authorization

## Status

```text
CLAUDE_NATIVE_BENCHMARK_TRACK_AUTHORIZED
CLAUDE_NATIVE_TECHNICAL_PROBES_AUTHORIZED_NEXT
READINESS_SESSIONS_NOT_YET_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
DEEPSEEK_VIA_CLAUDE_CODE_TRACK_BLOCKED_WITH_BOUNDS
CODEX_NATIVE_TRACK_NOT_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The locked multi-agent benchmark protocol includes a Claude native track:

```text
agent_id:
CLAUDE_CODE_NATIVE

harness:
Claude Code

backend:
Anthropic

output:
stream-json or json
```

The DeepSeek-via-Claude-Code track is blocked before benchmark execution:

```text
DeepSeek model identity:
PASS

Claude Code harness:
PASS

structured output:
PASS

read-only tool execution:
BLOCKED
```

The next methodological question is whether the same Claude Code harness passes
the technical gates with its native Anthropic backend.

## Scope

This authorization opens only the Claude native technical-probe track.

It does not authorize readiness sessions or primary benchmark execution.

## Frozen Inputs

The following remain frozen:

```text
18 benchmark cases
54 frozen Arm A/B/C inputs
prompt templates
agent output schema
randomization
MVP code
Domain 1 producer behavior
Domain 2 producer behavior
Domain 3 producer behavior
Gate A semantics
action enum
claim-status enum
thresholds
```

No benchmark case may be sent during technical probes.

## Required Model and Harness Pinning

Before any scored session, the Claude native track must record:

```text
Claude Code executable path or process-local PATH strategy
Claude Code version
Claude Code binary SHA-256
requested Anthropic model ID
resolved or response-reported model ID, if available
Anthropic endpoint identity
usage accounting source
permission mode
tool allowlist
session isolation settings
```

The already pinned Claude Code installation may be reused:

```text
Claude Code version:
2.1.206

Claude Code binary SHA-256:
d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2
```

If the binary path, version, or hash differs, the track must stop and record a
new harness identity result.

## Authorized Technical Probes

The next run may execute only non-scored technical probes using synthetic
temporary files:

```text
C0-P1 Anthropic authentication and model identity
C0-P2 Claude Code init and tool inventory
C0-P3 structured JSON output with the frozen output schema
C0-P4 Read / Glob / Grep tool execution in a temporary read-only workspace
C0-P5 write, web, shell-write, and subagent denial
C0-P6 fresh session isolation
C0-P7 usage accounting extraction
```

The probes may use:

```text
inline canonical JSON schema transport
process-local PATH or direct Claude binary invocation
synthetic temporary files
safe stdout/stderr metadata
machine-readable results and report
```

## Required C0 Pass Gates

The Claude native technical probes pass only if all of the following hold:

```text
model identity confirmed
no model fallback
Claude Code version and binary identity confirmed
structured JSON output valid
output schema enforced
Read tool call observed and successful
Glob tool call observed and successful
Grep tool call observed and successful
write operations denied
web access denied
subagents disabled or denied
workspace mutation: 0
fresh session isolation confirmed
exact usage accounting available
benchmark cases sent: 0
readiness sessions started: 0
```

If exact usage counters cannot be recovered:

```text
CLAUDE_USAGE_ACCOUNTING_NOT_READY
```

If read-only tools do not execute:

```text
CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY
```

## Allowed Files

The technical-probe implementation may add or update only Claude native
benchmark-track artifacts:

```text
tools/run_claude_native_c0.py
tests/test_claude_native_c0.py
research/multi_agent_benchmark/claude_native/claude_native_c0_results.json
research/multi_agent_benchmark/claude_native/claude_native_c0_report.md
research/multi_agent_benchmark/claude_native/claude_native_c0_raw_private_manifest.json
```

Raw stdout/stderr must remain outside the repository.

Any need to change shared benchmark assets, prompts, cases, MVP code, producers,
or existing DeepSeek artifacts requires a separate authorization.

## Forbidden

This authorization forbids:

```text
sending benchmark cases to the model
starting the 9 readiness sessions
starting primary / holdout / carryover benchmark sessions
changing the MVP
changing producers
changing Gate A
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing output schema
changing randomization
weakening correctness thresholds
making efficiency claims
merge to main
release / version / tag / PyPI
```

Network access is permitted only to the Anthropic model endpoint required for
the technical probes.

## Required Validation

After C0 execution:

```text
focused C0 tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```

## Terminal Statuses

The C0 technical probes must end with exactly one of:

```text
CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS
CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED
CLAUDE_NATIVE_STRUCTURED_OUTPUT_NOT_READY
CLAUDE_NATIVE_READ_ONLY_TOOLS_NOT_READY
CLAUDE_NATIVE_USAGE_ACCOUNTING_NOT_READY
CLAUDE_NATIVE_TOOL_ISOLATION_FAILED
CLAUDE_NATIVE_C0_INCOMPLETE
CLAUDE_NATIVE_TRACK_AUTHORIZATION_REVISION_REQUIRED
```

## Next Required Artifact

After C0 execution:

```text
research/multi_agent_benchmark/claude_native/claude_native_c0_review.md
```

Only if C0 is accepted with:

```text
CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS
```

may a later review consider authorizing the nine Claude native readiness
sessions.
