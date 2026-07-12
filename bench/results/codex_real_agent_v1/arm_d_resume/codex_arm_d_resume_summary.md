# Codex Arm D Resume Measurement

Created: 2026-07-12T06:51:04.377184Z
Codex: `codex-cli 0.142.5`

This corrects the Arm D implementation mismatch from the original V1 run by using a true `codex exec resume` second turn.

## Average Usage

| Case | Turn | Runs | Gate/action valid | Compact NE valid | Strict list valid | Avg input | Avg cached input | Avg fresh input | Avg output | Avg tools | Avg file-read estimate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `median_minijinja` | `first` | 3 | 3 | 3 | 2 | 53938 | 47317.33 | 6620.67 | 1628.67 | 5.33 | 9.33 |
| `median_minijinja` | `second` | 3 | 3 | 3 | 2 | 101487.33 | 91178.67 | 10308.67 | 3103.67 | 4 | 7.33 |
| `p90_nutpie` | `first` | 3 | 3 | 3 | 2 | 53858 | 48000 | 5858 | 1531.67 | 5.33 | 9.33 |
| `p90_nutpie` | `second` | 3 | 3 | 3 | 2 | 100163.33 | 91178.67 | 8984.67 | 2829 | 3.33 | 6.67 |

## Predeclared Repeated-Query Ratios

- `median_minijinja/first_vs_second_input_tokens`: 0.531
- `median_minijinja/second_reduction_vs_first_pct`: -88.156
- `p90_nutpie/first_vs_second_input_tokens`: 0.538
- `p90_nutpie/second_reduction_vs_first_pct`: -85.977

## Decision

- The original Arm D result is treated as `NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH`.
- This file is the valid true-resume Arm D measurement.
- The true resumed second turn did not clear the predeclared 20% improvement threshold in either frozen case.
- No live-token benefit claim for repeated exact-context cache queries is supported by this measurement.
- Cache remains an exact-context correctness/reuse feature under this result, not a measured live-token saving feature.

## Not Claimed

- No physical energy or CO2 measurement.
- No claim that Codex behavior generalizes to every agent.
- No claim that any package is safe, malware-free, or production-ready.
