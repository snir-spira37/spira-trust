# Claude Native Primary Benchmark Report

## Status

```text
CLAUDE_NATIVE_PRIMARY_BENCHMARK_COMPLETE
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
session count:
180

completed sessions:
180

next session index:
None

schema valid:
180 / 180

JSON result envelope:
180 / 180

structured_output:
180 / 180

usage available:
180 / 180

strict fidelity:
112 / 180

Arm B strict fidelity:
57

Arm C strict fidelity:
51

Arm A operational pass:
39

false PROCEED:
9

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
180

next_session_index:
None
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
