# Claude Native Primary Benchmark Report

## Status

```text
CLAUDE_NATIVE_PRIMARY_BENCHMARK_INFRASTRUCTURE_BLOCKED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
session count:
180

completed sessions:
122

next session index:
123

schema valid:
122 / 122

JSON result envelope:
122 / 122

structured_output:
122 / 122

usage available:
122 / 122

strict fidelity:
77 / 122

Arm B strict fidelity:
40

Arm C strict fidelity:
34

Arm A operational pass:
27

false PROCEED:
7

workspace mutations:
0

forbidden tool calls:
0

persistent infrastructure failures:
0
```

## Resume State

```text
manifest:
research/multi_agent_benchmark/claude_native/claude_native_primary_session_manifest.json

plan_sha256:
570f41baf38065242acdae1bc145aff3b97893a116d9c059c1dadc0609aa739c

completed_session_count:
122

next_session_index:
123
```

If interrupted, rerun the primary runner with `--resume`. The runner skips only
sessions marked `COMPLETED` in the manifest and resumes at `next_session_index`.

## Boundary

```text
Holdout:
NOT_STARTED

Carryover:
NOT_STARTED

Codex / DeepSeek tracks:
NOT_STARTED

Efficiency claim:
NOT_AUTHORIZED

Release / version / tag / PyPI:
NOT_AUTHORIZED
```
