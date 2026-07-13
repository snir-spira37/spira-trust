# Claude Native C0 Technical Probes Report

## Status

```text
CLAUDE_NATIVE_MODEL_IDENTITY_NOT_CONFIRMED
BENCHMARK_CASES_NOT_EXECUTED
READINESS_SESSIONS_NOT_STARTED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Identity

```text
track: Claude native through Claude Code
requested model: sonnet
Claude Code version: 2.1.206 (Claude Code)
Claude Code binary sha256: d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2
```

## Probe Summary

```text
probe count: 1
structured output ready: False
read-only tools ready: False
tool isolation ready: False
usage accounting ready: False
workspace mutations: 0
forbidden tool calls: 0
benchmark cases sent: 0
readiness sessions: 0
```

## Probes

- C0-P1: ready=False rc=1 errors=['CLAUDE_NATIVE_AUTHENTICATION_NOT_READY']

## Blockers

- CLAUDE_NATIVE_AUTHENTICATION_NOT_READY

## Boundary

```text
No benchmark cases were sent.
No readiness, primary, holdout, or carryover benchmark was started.
No efficiency claim is authorized.
No release/version/tag/PyPI action is authorized.
```
