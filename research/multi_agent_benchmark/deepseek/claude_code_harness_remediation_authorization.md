# Claude Code Harness Remediation Authorization

## Status

```text
CLAUDE_CODE_HARNESS_REMEDIATION_AUTHORIZED
PHASE_A_DISCOVERY_AUTHORIZED
PHASE_B_REMEDIATION_CONDITIONALLY_AUTHORIZED_ONLY_IF_DISCOVERY_PROVES_NEEDED
DS_R0_RERUN_NOT_YET_AUTHORIZED
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This authorization follows the accepted DS-R0 rerun blocked review:

```text
DS_R0_RERUN_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
MODEL_IDENTITY_CONFIRMED
DEEPSEEK_USAGE_ACCOUNTING_AVAILABLE
CLAUDE_CODE_HARNESS_NOT_READY
CLAUDE_EXECUTABLE_DISCOVERY_OR_REMEDIATION_REQUIRED
```

The only established blocker is:

```text
No `claude` executable was found in the current PATH / command environment.
```

This authorization is limited to discovering and, only if necessary, remediating
the Claude Code harness availability needed for DS-R0 technical probes.

It does not authorize readiness sessions, scored benchmark sessions, MVP code
changes, or release work.

## Preserved History

```text
DS-R0 Run 1:
BLOCKED — requested model identity deepseek-v4-pro[1m] normalized

Model identity amendment:
ACCEPTED — provider-confirmed model ID pinned as deepseek-v4-pro

DS-R0 Run 2:
MODEL IDENTITY PASS
USAGE ACCOUNTING AVAILABLE
BLOCKED — claude executable not found in current environment
```

No prior result may be deleted or rewritten.

## Phase A — Discovery Only

Phase A is authorized immediately.

Allowed discovery operations:

```text
locate an existing claude executable
inspect current PATH visibility
inspect npm global prefix and package root
inspect common npm launcher locations
inspect launcher type and version
verify resolved executable path
record executable hash/version safely
verify required Claude Code flags by help/version output when possible
run harness launch smoke only if it sends no benchmark cases
```

Examples of allowed read-only discovery commands:

```powershell
Get-Command claude -All -ErrorAction SilentlyContinue
where.exe claude
npm prefix -g
npm root -g
Get-ChildItem "$env:APPDATA\npm" -Filter "claude*" -ErrorAction SilentlyContinue
claude --version
claude --help
```

Phase A must not:

```text
modify PATH permanently
install packages
upgrade packages
remove packages
send benchmark cases to a model
start DS-R0 rerun
start readiness sessions
start primary/holdout/carryover benchmark sessions
```

## Phase B — Conditional Remediation

Phase B is authorized only if Phase A proves one of the following:

```text
CLAUDE_EXECUTABLE_NOT_INSTALLED
CLAUDE_EXECUTABLE_FOUND_BUT_NOT_PATH_VISIBLE
CLAUDE_LAUNCHER_AMBIGUOUS
CLAUDE_CODE_VERSION_NOT_READY
CLAUDE_REQUIRED_FLAGS_UNAVAILABLE
```

If remediation is needed, it must be the narrowest action that resolves the
observed blocker.

Allowed Phase B remediation:

```text
temporarily expose an existing launcher to the current process PATH
record the exact executable path used by the harness
install Claude Code only if no usable executable is discovered
use a pinned installation method where available
avoid unrelated package updates
verify post-install executable path
verify post-install version
record executable hash when a stable local launcher file exists
verify required CLI flags
run no benchmark cases
run no scored readiness sessions
```

Phase B must not:

```text
change benchmark cases
change prompts
change frozen Arm A/B/C inputs
change output schema
change randomization
change MVP code
change producers
change DeepSeek model identity
change correctness or overhead thresholds
merge to main
release/version/tag/PyPI
```

## Required Flag Verification

Discovery/remediation must check whether the harness supports the DS-R0
required surfaces:

```text
--print
--model
--output-format
--max-turns
--permission-mode
--tools
--disallowedTools
--strict-mcp-config
--no-session-persistence
--session-id
```

If a required flag is unavailable or renamed, the result must be recorded as:

```text
CLAUDE_REQUIRED_FLAGS_UNAVAILABLE
```

and DS-R0 rerun remains blocked until a separate review decides whether a
protocol amendment is needed.

## Allowed Output Artifacts

The discovery/remediation cell may create:

```text
research/multi_agent_benchmark/deepseek/claude_code_harness_discovery_results.json
research/multi_agent_benchmark/deepseek/claude_code_harness_discovery_report.md
```

If remediation/install occurs, it may also create:

```text
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_results.json
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_report.md
```

No raw private paths or secrets may be recorded. If local paths are needed for
audit, they must be sanitized or represented by hashes and safe metadata.

## Success Gate

The successful terminal status is:

```text
CLAUDE_CODE_HARNESS_READY_FOR_DS_R0
```

It requires:

```text
CLAUDE_EXECUTABLE_DISCOVERED
CLAUDE_CODE_VERSION_CONFIRMED
REQUIRED_FLAGS_AVAILABLE
HARNESS_LAUNCH_SMOKE_PASS
NO_BENCHMARK_CASES_SENT
NO_READINESS_SESSIONS_STARTED
NO_PRIMARY_BENCHMARK_STARTED
```

Only after this status is reviewed may a fresh DS-R0 rerun be authorized.

## Failure / Blocked Gates

Possible terminal statuses:

```text
CLAUDE_EXECUTABLE_NOT_INSTALLED
CLAUDE_EXECUTABLE_FOUND_BUT_NOT_PATH_VISIBLE
CLAUDE_CODE_VERSION_NOT_READY
CLAUDE_REQUIRED_FLAGS_UNAVAILABLE
CLAUDE_LAUNCHER_AMBIGUOUS
CLAUDE_CODE_HARNESS_REMEDIATION_INCOMPLETE
CLAUDE_CODE_HARNESS_REMEDIATION_AUTHORIZATION_REVISION_REQUIRED
```

Any blocked result must be recorded factually and must not be bypassed by
starting readiness sessions.

## Still Not Authorized

```text
DS-R0 live rerun
9 live readiness sessions
primary benchmark
holdout benchmark
carryover benchmark
MVP changes
producer changes
case or prompt changes
efficiency claims
merge to main
release/version/tag/PyPI
```

## Next Step

The next allowed action is Phase A discovery only.

If Phase A succeeds without remediation, produce the discovery report/results
and request review.

If Phase A proves remediation is needed, execute only the narrow Phase B action
allowed above, then produce remediation report/results and request review.

In all cases, DS-R0 rerun remains blocked until a separate review accepts that
the Claude Code harness is ready.
