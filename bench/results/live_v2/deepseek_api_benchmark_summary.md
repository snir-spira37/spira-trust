# DeepSeek API Benchmark Summary

Created: 2026-07-10T14:48:27.427543Z
Model: `deepseek-v4-flash`

This is an API file-ingestion benchmark, not a full autonomous agent tool-use benchmark.

## Average Tokens

| Case | Arm | Runs | Avg prompt | Avg completion | Avg total | Correct runs | Exact action runs |
|---|---:|---:|---:|---:|---:|---:|---:|
| median_minijinja | a_full_evidence | 3 | 15033 | 220.33 | 15253.33 | 0 | 0 |
| median_minijinja | a_decision_only | 3 | 2093 | 173.67 | 2266.67 | 3 | 0 |
| median_minijinja | b_agent_summary | 3 | 1221 | 151 | 1372 | 3 | 3 |
| p90_nutpie | a_full_evidence | 3 | 40305 | 242.33 | 40547.33 | 0 | 0 |
| p90_nutpie | a_decision_only | 3 | 2112 | 156 | 2268 | 3 | 0 |
| p90_nutpie | b_agent_summary | 3 | 1234 | 156 | 1390 | 3 | 3 |

## Prompt Token Ratios

- `median_minijinja/a_full_evidence_vs_b_agent_summary_prompt_tokens`: 12.31x
- `median_minijinja/a_decision_only_vs_b_agent_summary_prompt_tokens`: 1.71x
- `p90_nutpie/a_full_evidence_vs_b_agent_summary_prompt_tokens`: 32.66x
- `p90_nutpie/a_decision_only_vs_b_agent_summary_prompt_tokens`: 1.71x

## Not Claimed

- No physical energy / CO2 measurement.
- No full autonomous tool-use agent measurement.
- Correctness means the parsed JSON answered STOP, preserved a non-empty not_evaluated list, preserved GRAPH_OK_WITH_NOTES, and did not claim safety.
- `exact_action_runs` in the JSON summary separately counts responses that preserved `recommended_agent_action: REPORT_NOT_EVALUATED` exactly.
