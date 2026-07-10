# SPIRA Live API Benchmark v2

Date: 2026-07-10

This is a regression rerun of `bench/results/live_v1/` after adding
`SPIRA_DECISION_SEMANTICS_V2` to the embedded `SPIRA_AGENT_ACTION_V1` contract.

The benchmark used the same two wheels and the same prompt shape as live v1.
Evidence was injected into the DeepSeek Chat API prompt. This is an API
file-ingestion benchmark, not a full autonomous agent tool-use benchmark.

## What Changed Since v1

The action contract now distinguishes:

- raw `graph_verdict`
- `combined_verdict`
- `action_verdict`

The agent action is derived from `combined_verdict` when present, falling back
to the raw graph verdict only if no combined verdict exists.

This closes the semantic gap where a raw `GRAPH_OK` could produce `PROCEED`
even when another evaluated layer made the combined verdict
`GRAPH_OK_WITH_NOTES`.

## Results

Average prompt-token usage:

| Case | Full evidence | Decision only | Agent summary |
|---|---:|---:|---:|
| `median_minijinja` | 15,033 | 2,093 | 1,221 |
| `p90_nutpie` | 40,305 | 2,112 | 1,234 |

Prompt-token ratios:

| Case | Full evidence vs summary | Decision only vs summary |
|---|---:|---:|
| `median_minijinja` | 12.31x | 1.71x |
| `p90_nutpie` | 32.66x | 1.71x |

Correctness:

| Arm | Gate decision correctness | Exact action preservation |
|---|---:|---:|
| Full evidence | 0/6 | 0/6 |
| Decision only | 6/6 | 0/6 |
| Agent summary | 6/6 | 6/6 |

## Interpretation

The new action contract is larger than live v1, so the prompt-token reduction
against `spira-decision.json` moved from about 2.1x to about 1.7x. The
correctness result held: the summary path preserved both `STOP` and
`REPORT_NOT_EVALUATED` in 6/6 runs.

The broad-evidence path still converted `GRAPH_OK_WITH_NOTES` into `PROCEED` in
6/6 runs, confirming that the issue is not missing evidence but missing
deterministic action semantics.

## Not Claimed

- No physical energy or CO2 measurement.
- No full autonomous coding-agent tool-use measurement.
- No claim that DeepSeek behavior generalizes to every model.
- No claim that SPIRA makes packages safe.
