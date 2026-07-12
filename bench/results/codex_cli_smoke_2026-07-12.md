# Codex CLI Smoke - 2026-07-12

## Status

```text
CODEX_CLI_SMOKE_PASS_WITH_EXPLICIT_LOCAL_BINARY
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

`Get-Command` and `where.exe` first found Codex under the WindowsApps package path:

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

Further diagnosis found a local Codex binary under the per-user OpenAI Codex
bin directory:

```text
%LOCALAPPDATA%\OpenAI\Codex\bin\ea1c60319a1dcb19\codex.exe
```

Running that binary directly succeeded:

```text
codex-cli 0.142.5
```

The smoke was then rerun with:

```powershell
$smokeDir = Join-Path $env:TEMP "spira-codex-smoke"
$codex = Join-Path $env:LOCALAPPDATA "OpenAI\Codex\bin\ea1c60319a1dcb19\codex.exe"

& $codex exec --json --skip-git-repo-check --sandbox read-only --cd $smokeDir `
  --output-last-message codex_smoke_last.txt `
  "Reply with exactly CODEX_SMOKE_OK. Do not inspect, create, edit, or delete files." `
  > codex_smoke_skip_git.jsonl
```

Result:

```text
exit code: 0
final output: CODEX_SMOKE_OK
JSONL written: yes
turn.completed usage present: yes
input_tokens: 12508
cached_input_tokens: 10112
output_tokens: 9
reasoning_output_tokens: 0
```

The JSONL output was written by PowerShell redirection as UTF-16. Parsers for
the benchmark harness must either capture stdout directly from the process or
read the file with the correct encoding.

## Decision

The Codex real-agent benchmark is authorized from this smoke when using the
explicit local Codex binary path above, or another path that passes the same
smoke.

No 18-session benchmark was run during the smoke.

No DeepSeek fallback was run or relabeled as Codex.

## Next Step

Run the locked benchmark protocol using the smoke-passed Codex CLI path:

```text
bench/codex_real_agent_protocol.md
```

If the WindowsApps alias is preferred later, fix PATH/permissions first and
rerun this smoke before using it for measurements.
