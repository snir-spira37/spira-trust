# DeepSeek DS-R0 Rerun Authorization

## Status

```text
DS_R0_RERUN_AUTHORIZED
TECHNICAL_PROBES_ONLY
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

```text
model identity amendment review:
DEEPSEEK_MODEL_IDENTITY_AMENDMENT_ACCEPTED

Claude Code harness remediation review:
CLAUDE_CODE_HARNESS_REMEDIATION_ACCEPTED
CLAUDE_CODE_HARNESS_READY_FOR_DS_R0

accepted model identity:
deepseek-v4-pro

accepted Claude Code version:
2.1.206

accepted Claude Code binary sha256:
d5072b25b9a20bffb24625d36129a05ed2be4d2eb7e35625aad6aa35596892c2
```

## Scope

This authorization permits one fresh DS-R0 technical-probe rerun only.

The rerun must start from the beginning:

```text
P1 direct provider model resolution
P2 Claude system/init and tool inventory
P3 structured output
P4 read-only tool availability
P5 write/web/subagent denial
P6/P7 session isolation
P8 usage accounting
```

The rerun may use:

```text
direct invocation of the pinned Claude Code binary
```

or:

```text
process-local PATH addition for the resolved WinGet package directory
```

The rerun must not depend on persistent shell alias refresh.

## Allowed Files

The rerun may update only:

```text
research/multi_agent_benchmark/deepseek/ds_r0_results.json
research/multi_agent_benchmark/deepseek/ds_r0_report.md
research/multi_agent_benchmark/deepseek/ds_r0_raw_private_manifest.json
```

If a code change is required to invoke the pinned Claude Code binary or to use a
process-local PATH addition, stop and create a separate narrow implementation
authorization before changing code.

## Required Boundaries

```text
benchmark cases sent to model:
0

readiness sessions:
0

primary sessions:
0

holdout sessions:
0

carryover sessions:
0
```

The rerun must not modify:

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
DeepSeek model identity
Claude Code version or binary
```

## Success Gate

The only positive terminal status is:

```text
DS_R0_TECHNICAL_PROBES_PASS
```

It requires:

```text
model identity confirmed
Claude Code harness ready
structured JSON output ready
tool isolation ready
write/web/subagent denial verified
session isolation ready
usage accounting ready
cache decomposition reported
forbidden tool calls: 0
repository mutations: 0
workspace mutations: 0
benchmark cases sent: 0
readiness sessions: 0
```

## Blocked / Failure Gate

If any probe fails, the result must be:

```text
DS_R0_TECHNICAL_PROBES_BLOCKED
```

The blocked result must be reported factually. Do not weaken tool isolation,
skip probes, change the output schema, change prompts, or start readiness.

## Required Validation

After the rerun:

```text
focused DS-R0 tests
benchmark asset validator
JSON validation
secret/private-path scan
full pytest
frozen asset diff check
```

## Next Required Artifact

After the rerun, a separate review is required:

```text
research/multi_agent_benchmark/deepseek/deepseek_ds_r0_rerun_review.md
```

Possible verdicts:

```text
DS_R0_RERUN_ACCEPTED
DS_R0_RERUN_NEEDS_REVISION
DS_R0_RERUN_REJECTED
```

Only if DS-R0 is accepted may the process consider authorizing the nine live
readiness sessions.
