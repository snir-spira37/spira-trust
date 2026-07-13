# Claude Native C0 Rerun Authorization

## Status

```text
CLAUDE_NATIVE_C0_RERUN_AUTHORIZED
C0_TECHNICAL_PROBES_ONLY
CHEAP_MODEL_PIN_HAIKU
READINESS_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

The Claude native auth invocation fix was accepted:

```text
CLAUDE_NATIVE_AUTH_INVOCATION_FIX_ACCEPTED
CLAUDE_NATIVE_AUTHENTICATION_REMEDIATED
CLAUDE_NATIVE_MODEL_IDENTITY_SMOKE_PASS
CLAUDE_NATIVE_USAGE_ACCOUNTING_SMOKE_AVAILABLE
CHEAP_MODEL_PIN_ACCEPTED_AS_HAIKU
```

The prior C0 blocked result is preserved:

```text
prior C0:
CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED

blocker:
CLAUDE_NATIVE_AUTHENTICATION_NOT_READY
```

This rerun is a new technical-probe execution after auth remediation.

## Scope

This authorization permits only a fresh Claude native C0 technical-probe rerun
from P1 using:

```text
requested model:
haiku

Claude Code version:
2.1.206

Claude Code binary SHA-256:
d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2

invocation:
no --bare
existing Claude Code login auth store
fresh session IDs
--no-session-persistence
synthetic temporary files only
```

## Required Sequence

```text
C0-P1 Anthropic authentication and model identity
C0-P2 Claude Code init and tool inventory
C0-P3 structured JSON output with inline canonical schema
C0-P4 Read / Glob / Grep execution in a synthetic read-only workspace
C0-P5 write, web, shell-write, and subagent denial
C0-P6 fresh session isolation
C0-P7 usage accounting extraction
```

## Required Pass Gates

The rerun may pass only if all hold:

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

## Allowed Files

```text
research/multi_agent_benchmark/claude_native/claude_native_c0_results.json
research/multi_agent_benchmark/claude_native/claude_native_c0_report.md
research/multi_agent_benchmark/claude_native/claude_native_c0_raw_private_manifest.json
```

The existing runner and tests may be used. A change to the runner or tests is
not authorized by this document.

## Forbidden

This authorization forbids:

```text
sending benchmark cases to the model
starting readiness sessions
starting primary / holdout / carryover benchmark sessions
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing output schema
changing MVP code
changing producers
changing Gate A
changing thresholds
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Required Validation

After rerun:

```text
focused C0 tests
JSON validation
benchmark asset validator
secret/private-path scan
frozen asset diff check
full pytest
```

## Terminal Statuses

The rerun must end with exactly one of:

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

After the rerun:

```text
research/multi_agent_benchmark/claude_native/claude_native_c0_rerun_review.md
```

Only if the rerun is accepted as:

```text
CLAUDE_NATIVE_C0_TECHNICAL_PROBES_PASS
```

may a later artifact consider authorizing the nine Claude native readiness
sessions.
