# DeepSeek Read Tool Diagnostic Authorization

## Status

```text
DEEPSEEK_READ_TOOL_DIAGNOSTIC_AUTHORIZED
P4_TECHNICAL_DIAGNOSTIC_ONLY
NO_BENCHMARK_CASES_AUTHORIZED
DS_R0_RERUN_NOT_AUTHORIZED
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

```text
read-tool blocked review:
DS_R0_READ_TOOL_BLOCKED_RESULT_ACCEPTED_AS_FACTUAL
MODEL_IDENTITY_CONFIRMED
CLAUDE_CODE_HARNESS_CONFIRMED
STRUCTURED_OUTPUT_CONFIRMED
READ_ONLY_TOOL_EXECUTION_NOT_READY
READ_TOOL_DIAGNOSTIC_AUTHORIZATION_REQUIRED
```

## Purpose

The diagnostic may investigate why DS-R0 P4 failed:

```text
probe:
DS-R0-P4

blocker:
DEEPSEEK_READ_TOOL_NOT_READY

returncode:
1

stdout bytes:
0

workspace mutation:
0

forbidden tool calls:
0
```

## Allowed Probes

The diagnostic may run only unscored technical probes using synthetic temporary
files, not benchmark cases.

Allowed probes:

```text
stream-json capture including stderr/error events
Read-only probe
Glob-only probe
Grep-only probe
tool use without --json-schema
tool use with inline schema
relative path versus absolute path inside a temporary workspace
--tools syntax and actual system/init inventory
permission-mode effect on tool calls
```

## Allowed Files

```text
tools/run_deepseek_read_tool_diagnostic.py
tests/test_deepseek_read_tool_diagnostic.py
research/multi_agent_benchmark/deepseek/read_tool_diagnostic_results.json
research/multi_agent_benchmark/deepseek/read_tool_diagnostic_report.md
research/multi_agent_benchmark/deepseek/read_tool_diagnostic_raw_private_manifest.json
```

Raw stdout/stderr must remain outside the repository.

## Required Safe Metadata

The diagnostic must capture:

```text
exit code
timeout status
stdout byte size and SHA-256
stderr byte size and SHA-256
safe stderr category
tool-call names observed
server tool use counts
workspace mutation status
usage availability
```

Do not record:

```text
API keys
authorization headers
raw private paths
raw full stdout/stderr
benchmark evidence
```

## Forbidden

The diagnostic must not:

```text
change DS-R0 runner behavior
change tool requirements
weaken tool isolation
change benchmark cases
change prompts
change frozen Arm A/B/C inputs
change MVP code
start DS-R0 rerun
start readiness sessions
start primary/holdout/carryover sessions
make efficiency claims
merge to main
release/version/tag/PyPI
```

## Terminal Statuses

The diagnostic must end with exactly one of:

```text
READ_TOOL_INVOCATION_DEFECT_FOUND
READ_TOOL_CONFIGURATION_DEFECT_FOUND
DEEPSEEK_CLAUDE_TOOL_CALL_COMPATIBILITY_NOT_READY
READ_TOOL_DIAGNOSTIC_INCOMPLETE
READ_TOOL_DIAGNOSTIC_AUTHORIZATION_REVISION_REQUIRED
```

## Required Validation

After diagnostic execution:

```text
focused diagnostic tests
benchmark asset validator
JSON validation
secret/private-path scan
full pytest
frozen asset diff check
```

## Next Required Artifact

After the diagnostic:

```text
research/multi_agent_benchmark/deepseek/deepseek_read_tool_diagnostic_review.md
```

Only a future accepted diagnostic review may decide whether a narrow runner
fix, a protocol amendment, or DeepSeek-via-Claude-Code track blockage is the
correct next step.
