# Claude Code Harness Remediation Review

## Status

```text
CLAUDE_CODE_HARNESS_REMEDIATION_ACCEPTED
CLAUDE_CODE_VERSION_CONFIRMED
CLAUDE_CODE_BINARY_IDENTITY_CONFIRMED
CLAUDE_CODE_REQUIRED_FLAGS_CONFIRMED
CLAUDE_CODE_HARNESS_READY_FOR_DS_R0
DS_R0_RERUN_AUTHORIZATION_REQUIRED_NEXT
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
authorization:
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_authorization.md

discovery results:
research/multi_agent_benchmark/deepseek/claude_code_harness_discovery_results.json

discovery report:
research/multi_agent_benchmark/deepseek/claude_code_harness_discovery_report.md

remediation results:
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_results.json

remediation report:
research/multi_agent_benchmark/deepseek/claude_code_harness_remediation_report.md
```

## Review Question

```text
Did the authorized Claude Code harness discovery/remediation close the
CLAUDE_EXECUTABLE_NOT_FOUND blocker sufficiently to allow a future DS-R0 rerun
authorization, without starting readiness or benchmark execution?
```

## Verdict

```text
CLAUDE_CODE_HARNESS_REMEDIATION_ACCEPTED
```

The remediation is accepted.

The Claude Code harness is ready for a future DS-R0 rerun authorization.

This review does not itself authorize the rerun.

## Confirmed Facts

```text
installation method:
winget install Anthropic.ClaudeCode

installed package:
Anthropic.ClaudeCode

version:
2.1.206

binary sha256:
d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2

raw binary path recorded:
false

path handling:
direct binary invocation or process-local PATH only
```

The already-running PowerShell session did not see the new `claude` alias
immediately after installation. That is not treated as a blocker. The benchmark
runner should use either the exact resolved binary or a process-local PATH
addition, rather than depending on a shell alias refresh.

## Required Flags

The remediation report confirms that `claude --help` exposed the DS-R0-required
flag surfaces:

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

Therefore:

```text
CLAUDE_CODE_REQUIRED_FLAGS_CONFIRMED
```

## Harness Smoke

The authorized non-scored harness smoke passed:

```text
HARNESS_LAUNCH_SMOKE_PASS
```

Recorded smoke facts:

```text
model:
deepseek-v4-pro

usage accounting:
available

web_search_requests:
0

web_fetch_requests:
0

permission_denials:
0

benchmark cases sent:
0

readiness sessions started:
0
```

The smoke was not a benchmark case and must not be counted as readiness,
primary, holdout, or carryover execution.

## Model Identity Boundary

The smoke continued to use the accepted DeepSeek model identity:

```text
deepseek-v4-pro
```

The smoke response reported a context window value, but this does not reopen
the `[1m]` claim. The benchmark still does not claim an independently verified
one-million-token context capability.

## Frozen Assets

The remediation did not change:

```text
18 benchmark cases
54 Arm A/B/C frozen inputs
prompt templates
output schema
randomization
MVP code
producer semantics
Gate A behavior
correctness thresholds
overhead threshold
```

## Still Not Authorized

```text
DS-R0 rerun
9 live readiness sessions
primary benchmark
holdout benchmark
carryover benchmark
MVP changes
producer changes
case or prompt changes
efficiency claim
merge to main
release/version/tag/PyPI
```

## Next Required Artifact

The next artifact must be a narrow DS-R0 rerun authorization:

```text
research/multi_agent_benchmark/deepseek/deepseek_ds_r0_rerun_authorization.md
```

It should authorize only:

```text
fresh DS-R0 execution from P1
direct invocation of the pinned Claude Code binary or process-local PATH setup
technical probes only
no benchmark cases
no readiness sessions
no efficiency claim
```

## Required DS-R0 Rerun Sequence

The rerun must start from the beginning:

```text
P1 model resolution
P2 Claude system/init and tool inventory
structured output
read-only tools
write/web/subagent denial
session isolation
usage accounting
```

Only if that future rerun returns:

```text
DS_R0_TECHNICAL_PROBES_PASS
```

may a separate review consider authorizing the nine live readiness sessions.
