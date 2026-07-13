# Claude Native Read Invocation Hardening Authorization

## Status

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_AUTHORIZED
READ_INVOCATION_HARDENING_DIAGNOSTIC_ONLY
UNSCORED_DIAGNOSTIC_SESSIONS_ONLY
MODEL_FROZEN
PROMPTS_FROZEN
CASES_FROZEN
SCHEMA_FROZEN
COMPARATOR_FROZEN
MVP_CODE_FROZEN
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Basis

The accepted provenance review records:

```text
READ_PERMISSION_DENIAL_RUNTIME_CONFIRMED
READ_INVOCATION_HARDENING_REQUIRED
```

The supported root-cause candidate is:

```text
Read was available through --tools,
but was not pre-approved through --allowedTools
under --permission-mode dontAsk.
```

The effectiveness of this candidate fix is not yet proven.

## Authorized Invocation Change

The diagnostic may change only the Claude Code invocation:

```text
existing:
--permission-mode dontAsk
--tools Read,Glob,Grep
--disallowedTools Bash,Edit,Write,NotebookEdit,WebSearch,WebFetch,Agent,Task,mcp__*

candidate addition:
--allowedTools Read,Glob,Grep
```

The local Claude Code 2.1.206 help output confirms:

```text
--allowedTools, --allowed-tools <tools...>
Comma or space-separated list of tool names to allow
```

The diagnostic will use:

```text
--allowedTools Read,Glob,Grep
```

## Authorized Sessions

Exactly 20 unscored sessions are authorized:

```text
Read nonce technical probes:
5

Critical Arm B:
pytest_result synthetic_clean_success arm B
10

Matched Arm C:
pytest_result synthetic_clean_success arm C
5
```

## Acceptance Conditions

```text
Read nonce confirmed:
5 / 5

Arm B exact:
10 / 10

Arm C exact:
5 / 5

schema valid:
20 / 20

usage available:
20 / 20

permission denials:
0

false PROCEED:
0

workspace mutations:
0

repository mutations:
0

forbidden tool calls:
0
```

If all conditions pass, a review may conclude:

```text
CLAUDE_NATIVE_READ_INVOCATION_HARDENING_ACCEPTED
READ_GLOB_GREP_PERMISSION_CONFIGURATION_CONFIRMED
CRITICAL_ARM_B_EXACT_10_OF_10
MATCHED_ARM_C_EXACT_5_OF_5
FULL_NINE_CELL_READINESS_RERUN_JUSTIFIED
```

That still does not authorize primary benchmark execution.

## Authorized Files

```text
tools/run_claude_native_read_invocation_hardening_diagnostic.py
tests/test_claude_native_read_invocation_hardening_diagnostic.py
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_results.json
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_report.md
research/multi_agent_benchmark/claude_native/claude_native_read_invocation_hardening_diagnostic_raw_private_manifest.json
```

## Forbidden

```text
primary benchmark execution
holdout execution
carryover execution
readiness rerun
prompt changes
case changes
schema changes
comparator changes
model changes
MVP code changes
producer changes
threshold changes
publishing raw private responses
publishing private raw paths
efficiency claim
release / version / tag / PyPI
```
