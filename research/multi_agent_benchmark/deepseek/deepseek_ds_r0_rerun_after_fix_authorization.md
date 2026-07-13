# DeepSeek DS-R0 Rerun After Fix Authorization

## Status

```text
DS_R0_RERUN_AFTER_FIX_AUTHORIZED
TECHNICAL_PROBES_ONLY
READINESS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
MVP_CODE_FROZEN
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

```text
runner fix review:
DS_R0_RUNNER_FIX_ACCEPTED
STRUCTURED_OUTPUT_SCHEMA_TRANSPORT_FIXED
SCHEMA_TRANSPORT_INLINE_CANONICAL_JSON
SCHEMA_SEMANTICS_UNCHANGED
```

## Scope

This authorization permits one fresh DS-R0 technical-probe rerun from the
beginning:

```text
P1 model resolution
P2 Claude init/tool inventory
P3 structured output
P4 read-only tools
P5 write/web/subagent denial
P6/P7 session isolation
P8 usage accounting
```

The rerun may update only:

```text
research/multi_agent_benchmark/deepseek/ds_r0_results.json
research/multi_agent_benchmark/deepseek/ds_r0_report.md
research/multi_agent_benchmark/deepseek/ds_r0_raw_private_manifest.json
```

## Required Boundaries

```text
benchmark cases sent:
0

readiness sessions:
0

primary/holdout/carryover sessions:
0
```

The rerun must not change:

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

## Success Gate

The positive terminal status is:

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
forbidden tool calls: 0
repository mutations: 0
workspace mutations: 0
benchmark cases sent: 0
readiness sessions: 0
```

## Blocked Gate

If any probe fails:

```text
DS_R0_TECHNICAL_PROBES_BLOCKED
```

Do not weaken probes, alter prompts, alter cases, or start readiness.

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
research/multi_agent_benchmark/deepseek/deepseek_ds_r0_after_fix_review.md
```

Only an accepted passing DS-R0 review may open the nine live readiness sessions.
