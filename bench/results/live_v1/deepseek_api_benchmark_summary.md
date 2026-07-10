# DeepSeek API Benchmark Summary

Created: 2026-07-10T13:52:43.754063Z
Model: `deepseek-v4-flash`

This is an API file-ingestion benchmark, not a full autonomous agent tool-use benchmark.

## Average Tokens

| Case | Arm | Runs | Avg prompt | Avg completion | Avg total | Correct runs | Exact action runs |
|---|---:|---:|---:|---:|---:|---:|---:|
| median_minijinja | a_full_evidence | 3 | 15109 | 253.33 | 15362.33 | 0 | 0 |
| median_minijinja | a_decision_only | 3 | 2092 | 191 | 2283 | 3 | 0 |
| median_minijinja | b_agent_summary | 3 | 981 | 155.67 | 1136.67 | 3 | 3 |
| p90_nutpie | a_full_evidence | 3 | 40338 | 256.67 | 40594.67 | 0 | 0 |
| p90_nutpie | a_decision_only | 3 | 2115 | 167 | 2282 | 3 | 0 |
| p90_nutpie | b_agent_summary | 3 | 987 | 164 | 1151 | 3 | 3 |

## Prompt Token Ratios

- `median_minijinja/a_full_evidence_vs_b_agent_summary_prompt_tokens`: 15.4x
- `median_minijinja/a_decision_only_vs_b_agent_summary_prompt_tokens`: 2.13x
- `p90_nutpie/a_full_evidence_vs_b_agent_summary_prompt_tokens`: 40.87x
- `p90_nutpie/a_decision_only_vs_b_agent_summary_prompt_tokens`: 2.14x

## Not Claimed

- No physical energy / CO2 measurement.
- No full autonomous tool-use agent measurement.
- Correctness means the parsed JSON answered STOP, preserved a non-empty not_evaluated list, preserved GRAPH_OK_WITH_NOTES, and did not claim safety.
- `exact_action_runs` in the JSON summary separately counts responses that preserved `recommended_agent_action: REPORT_NOT_EVALUATED` exactly.
