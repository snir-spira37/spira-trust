# DeepSeek via Claude Code Track Closeout

## Status

```text
DEEPSEEK_VIA_CLAUDE_CODE_TRACK_BLOCKED_WITH_BOUNDS
CLAUDE_CODE_TOOL_CALL_COMPATIBILITY_NOT_READY_FOR_DEEPSEEK_BACKEND
BENCHMARK_CASES_NOT_EXECUTED
DEEPSEEK_DECISION_CORRECTNESS_NOT_EVALUATED
DEEPSEEK_EFFICIENCY_NOT_EVALUATED
ALTERNATIVE_DIRECT_HARNESS_REQUIRES_NEW_AUTHORIZATION
CLAUDE_NATIVE_TRACK_AUTHORIZATION_ALLOWED_NEXT
CODEX_NATIVE_TRACK_NOT_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This closeout records the terminal state of the current DeepSeek track:

```text
agent_id:
DEEPSEEK_VIA_CLAUDE_CODE

harness:
Claude Code

backend:
DeepSeek Anthropic-compatible API

model identity:
deepseek-v4-pro
```

The track evaluated DeepSeek only as a backend inside the pinned Claude Code
harness. It did not evaluate DeepSeek as a standalone model or as a native
agent system.

## Run History

```text
Run 1:
BLOCKED - model identity normalization

Amendment:
provider-confirmed model identity pinned as deepseek-v4-pro

Run 2:
MODEL IDENTITY PASS
BLOCKED - Claude executable unavailable in the current environment

Remediation:
Claude Code installed and pinned

Run 3:
MODEL IDENTITY PASS
CLAUDE HARNESS PASS
BLOCKED - schema file-path transport

Diagnostic:
inline JSON schema confirmed

Runner fix:
schema_transport = INLINE_CANONICAL_JSON
schema_semantics_changed = false

Run 4:
P1 model identity PASS
P2 Claude init / tool inventory PASS
P3 structured output PASS
P4 read-only tool execution BLOCKED

P4 diagnostic:
Read / Glob / Grep invocation and configuration probes exhausted
no observable read-only tool calls
```

No prior blocked result is erased. Each run closed one technical question and
exposed the next gate.

## Confirmed Capabilities

```text
DeepSeek API authentication:
PASS

provider-confirmed model identity:
deepseek-v4-pro

usage accounting:
AVAILABLE

Claude Code executable:
INSTALLED AND PINNED

Claude Code launch:
PASS

Claude Code init / tool inventory:
PASS

structured JSON output:
PASS

inline JSON Schema:
PASS
```

These facts remain valid within the tested environment.

## Terminal Blocker

```text
P4 read-only tool execution:
BLOCKED

terminal finding:
DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY
```

The diagnostic did not produce observable `Read`, `Glob`, or `Grep` calls in
the current DeepSeek-via-Claude-Code harness.

The accepted conclusion is bounded:

```text
DeepSeek via Claude Code is not ready for this benchmark track because the
current pinned combination did not satisfy the read-only tool-call gate.
```

## What This Does Not Claim

This closeout does not claim:

```text
DeepSeek is a weak model
DeepSeek cannot use tools in any harness
DeepSeek cannot evaluate SPIRA evidence
DeepSeek cannot be benchmarked with a direct harness
SPIRA MVP failed
Claude Code native tool use failed
```

The benchmark cases were not sent to DeepSeek. Therefore:

```text
DeepSeek decision correctness:
NOT_EVALUATED

DeepSeek efficiency:
NOT_EVALUATED
```

## Isolation Preserved

```text
benchmark cases sent:
0

readiness sessions:
0

primary / holdout / carryover sessions:
0

workspace mutation:
0

forbidden tool calls:
0

MVP code changes:
0

prompt / case / schema changes:
0
```

The track failed closed before any scored benchmark cell.

## Methodological Consequence

The blocked track demonstrates that an Anthropic-compatible backend is not
automatically equivalent to a native Claude Code agent for benchmark purposes.

The multi-agent benchmark remains valid, but the DeepSeek-via-Claude-Code track
cannot proceed to readiness or primary execution under the current pinned
configuration.

## Allowed Next Direction

The next clean comparison is the native Claude Code track:

```text
Claude native through Claude Code
```

That track can test whether the same installed Claude Code harness passes the
read-only tool gate with its native Anthropic backend.

## Separate Future Work

A DeepSeek direct track may be proposed later, but it is a different benchmark
system:

```text
DeepSeek via SPIRA direct benchmark harness
```

Such a track would require a new proposal and authorization covering:

```text
Read / Glob / Grep equivalents
read-only workspace isolation
fresh sessions
tool-call logging
files-opened accounting
provider usage accounting
strict JSON validation
conformance against the frozen multi-agent benchmark contract
```

It must not be represented as the same-harness Claude Code comparison.

## Not Authorized

This closeout does not authorize:

```text
DeepSeek readiness sessions
DeepSeek primary / holdout / carryover benchmark sessions
DeepSeek direct harness implementation
weakening read-only tool requirements
removing tool isolation
changing benchmark cases
changing prompts
changing frozen Arm inputs
changing MVP code
changing producers
making efficiency claims
merge to main
release / version / tag / PyPI
```

## Final State

```text
DeepSeek via Claude Code:
BLOCKED WITH BOUNDS

benchmark cases:
NOT EXECUTED

decision correctness:
NOT_EVALUATED

efficiency:
NOT_EVALUATED

next recommended track:
CLAUDE_NATIVE
```
