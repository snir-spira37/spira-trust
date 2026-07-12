# Codex Real-Agent Benchmark V1

Created: 2026-07-12T06:42:20.610287Z
Codex: `codex-cli 0.142.5`

This is a Codex CLI real-agent tool-use benchmark. It is not the DeepSeek file-ingestion benchmark.

## Average Usage

| Case | Arm | Runs | Gate/action valid | Compact NE valid | Strict list valid | Avg input | Avg cached input | Avg fresh input | Avg output | Avg tools | Avg file-read estimate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `median_minijinja` | `A_raw_discovery` | 3 | 3 | 3 | 3 | 93208 | 73984 | 19224 | 2507.67 | 20 | 12.67 |
| `median_minijinja` | `B_agent_summary` | 3 | 3 | 3 | 3 | 27261.33 | 21930.67 | 5330.67 | 563 | 2 | 2 |
| `median_minijinja` | `C_current_spira_flow` | 3 | 3 | 3 | 0 | 42749.67 | 38698.67 | 4051 | 1230.67 | 4 | 8 |
| `median_minijinja` | `D_repeated_exact_context` | 3 | 3 | 3 | 1 | 59692.33 | 51712 | 7980.33 | 2098.67 | 6.67 | 12.67 |
| `p90_nutpie` | `A_raw_discovery` | 3 | 3 | 3 | 3 | 67468.67 | 49578.67 | 17890 | 2189.33 | 15.33 | 10.67 |
| `p90_nutpie` | `B_agent_summary` | 3 | 3 | 3 | 3 | 31829.67 | 29056 | 2773.67 | 799.33 | 2.67 | 2 |
| `p90_nutpie` | `C_current_spira_flow` | 3 | 3 | 3 | 0 | 42849 | 37845.33 | 5003.67 | 1375.67 | 4 | 8 |
| `p90_nutpie` | `D_repeated_exact_context` | 3 | 3 | 3 | 0 | 53936 | 46464 | 7472 | 2129.33 | 6 | 12 |

## Predeclared Ratios

- `median_minijinja/A_vs_B_input_tokens`: 3.419
- `median_minijinja/B_vs_C_input_tokens`: 0.638
- `median_minijinja/C_reduction_vs_B_pct`: -56.814
- `median_minijinja/C_first_vs_D_repeated_input_tokens`: 0.716
- `median_minijinja/D_reduction_vs_C_first_pct`: -39.632
- `p90_nutpie/A_vs_B_input_tokens`: 2.12
- `p90_nutpie/B_vs_C_input_tokens`: 0.743
- `p90_nutpie/C_reduction_vs_B_pct`: -34.62
- `p90_nutpie/C_first_vs_D_repeated_input_tokens`: 0.794
- `p90_nutpie/D_reduction_vs_C_first_pct`: -25.875

## Decision Against Predeclared Thresholds

- Arm B improved over Arm A on input tokens in both frozen cases.
- Arm C did not improve over Arm B on first-query input tokens in either case; it was larger in this run.
- Arm D in this original file is not a valid repeated-query measurement because it used one prompt/turn for both first_query and second_query.
- Therefore this run does not support an additional live token-efficiency claim for status/cache beyond agent_summary.
- Status/cache/unification remain binding, audit, exact-context reuse, and fail-closed features under this benchmark result.

## Arm D Erratum

`D_repeated_exact_context` rows in this file are retained for audit history but are classified as:

```text
NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH
```

They were produced by one Codex turn that returned `first_query` and `second_query` in the same JSON object. The locked protocol requires a true resumed second turn and separate usage measurement. The corrected Arm D measurement is stored under `bench/results/codex_real_agent_v1/arm_d_resume/`.

## Validity Notes

- The safety-overclaim scanner ignores strings inside `not_claimed`; saying `safe` inside a not-claimed list is not counted as a safety claim.
- Arm C compact outputs usually preserved NOT_EVALUATED as a positive count rather than explicit layer names.
- `Strict list valid` requires explicit layer names. That distinction is intentional and is not collapsed into the compact score.

## Not Claimed

- No physical energy or CO2 measurement.
- No claim that Codex behavior generalizes to every agent.
- No claim that any package is safe, malware-free, or production-ready.
- Token savings without action equivalence are not counted as success.
- `Strict list valid` requires explicit NOT_EVALUATED layer names. `Compact NE valid` accepts a positive NOT_EVALUATED count from compact status/cache output.
