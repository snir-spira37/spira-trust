# Codex CLI Smoke - 2026-07-12

## Status

```text
CODEX_CLI_SMOKE_BLOCKED_ACCESS_DENIED
```

## Purpose

This smoke checks whether the Codex real-agent benchmark may run as a Codex CLI
tool-use benchmark.

The protocol is locked in:

```text
bench/codex_real_agent_protocol.md
```

## Commands Tried

```powershell
Get-Command codex -ErrorAction SilentlyContinue
codex --version
where.exe codex
```

## Observed Result

`Get-Command` and `where.exe` found Codex under the WindowsApps package path:

```text
C:\Program Files\WindowsApps\OpenAI.Codex_26.623.19656.0_x64__2p2nqsd0c76g0\app\resources\codex.exe
```

Running:

```text
codex --version
```

failed from the current PowerShell environment with:

```text
Access is denied
```

## Decision

The Codex real-agent benchmark is not authorized from this smoke.

No 18-session benchmark was run.

No DeepSeek fallback was run or relabeled as Codex.

## Next Step

Fix or confirm a runnable Codex CLI path/session mode, then rerun the smoke:

```text
codex --version
minimal clean session
new transcript/JSONL written
usage counters present
tool calls visible
```

Only after this passes may `bench/codex_real_agent_protocol.md` move from
pending smoke to executable benchmark.

