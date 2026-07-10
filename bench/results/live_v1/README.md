# SPIRA Live API Benchmark v1

Date: 2026-07-10

This directory records the first live token-usage benchmark for SPIRA agent summaries.

The benchmark used the DeepSeek Chat API and provider-reported token usage. The API key is not stored here, and no secret material is included in the results.

## What This Measures

This is an API file-ingestion benchmark:

- Evidence was injected into the prompt.
- The model was asked to answer a narrow artifact-gate question: `PROCEED` or `STOP`.
- Token counts are provider-reported prompt/completion/total tokens.

This is not a full autonomous agent tool-use benchmark. It does not measure a coding agent deciding which files to open with tools.

## Cases

Two real PyPI wheels from the PEP 770 survey were used:

- `median_minijinja`: median-sized embedded SBOM case.
- `p90_nutpie`: p90-sized embedded SBOM case.

Both cases had `agent_summary.json` with:

- `stop: true`
- `recommended_agent_action: REPORT_NOT_EVALUATED`
- `combined_verdict: GRAPH_OK_WITH_NOTES`

## Arms

- `a_full_evidence`: broad SPIRA evidence injected, excluding `agent_summary.json`.
- `a_decision_only`: minimal legacy baseline using `spira-decision.json`.
- `b_agent_summary`: `agent_summary.json` only.

Each arm ran 3 repeats per case.

## Results

Average prompt-token usage:

| Case | Full evidence | Decision only | Agent summary |
|---|---:|---:|---:|
| `median_minijinja` | 15,109 | 2,092 | 981 |
| `p90_nutpie` | 40,338 | 2,115 | 987 |

Prompt-token ratios:

| Case | Full evidence vs summary | Decision only vs summary |
|---|---:|---:|
| `median_minijinja` | 15.4x | 2.13x |
| `p90_nutpie` | 40.87x | 2.14x |

Correctness:

| Arm | Gate decision correctness | Exact action preservation |
|---|---:|---:|
| Full evidence | 0/6 | 0/6 |
| Decision only | 6/6 | 0/6 |
| Agent summary | 6/6 | 6/6 |

The full-evidence failures were not caused by missing facts. The model saw the `not_evaluated` layers, but inferred that `GRAPH_OK_WITH_NOTES`, `exit_code: 0`, and no blockers meant `PROCEED`.

## Control

A small control run injected the same full evidence but added a strict prompt rule:

> If `not_evaluated` is a non-empty list, answer `STOP`.

The model then corrected both full-evidence cases to `STOP`, but still used 15,124 and 40,353 prompt tokens and did not preserve `recommended_agent_action: REPORT_NOT_EVALUATED` exactly.

This isolates the main finding: the value of `agent_summary.json` is not only size. It carries the deterministic `stop` and `recommended_agent_action` mapping that otherwise has to be reconstructed in every prompt or inferred by the model.

## Publication-Safe Claim

In live DeepSeek API runs with evidence injected into the prompt, `agent_summary.json` used 2.1x fewer prompt tokens than the minimal `spira-decision.json` baseline and 15x-41x fewer than broad evidence injection. More importantly, the summary path returned the intended `STOP / REPORT_NOT_EVALUATED` decision in 6/6 runs, while the broad evidence path converted `GRAPH_OK_WITH_NOTES` into `PROCEED` in 6/6 runs unless the prompt manually encoded the missing stop rule.

## Not Claimed

- No physical energy or CO2 measurement.
- No full autonomous coding-agent tool-use measurement.
- No claim that more context always makes models wrong.
- No claim that DeepSeek behavior generalizes to every model.
- No claim that SPIRA makes packages safe.

## Files

- `deepseek_api_benchmark_results.json`: complete benchmark rows and model responses.
- `deepseek_api_benchmark_runs.csv`: compact run table.
- `deepseek_api_benchmark_summary.md`: generated summary table.
- `strict_not_evaluated_control.json`: control run with explicit `not_evaluated => STOP` rule.
- `full_evidence_error_analysis.md`: interpretation of the full-evidence failures and control.
- `selection_and_expected_results.json`: selected cases and expected gate fields.
- `run_deepseek_api_benchmark.py`: runner used for the measurement.
