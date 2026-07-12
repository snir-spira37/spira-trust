# Codex Arm D Resume Measurement

## Historical Note

The original Arm D result was invalidated by a protocol implementation mismatch.
The first true-resume interpretation was then corrected because Codex usage
counters were cumulative.

Canonical Arm D interpretation: see [`../ERRATA.md`](../ERRATA.md) and the
turn-delta results in this directory.

Created: 2026-07-12T06:58:30.301837Z
Codex: `codex-cli 0.142.5`

This corrects the Arm D implementation mismatch from the original V1 run by using a true `codex exec resume` second turn.

`codex exec --json` reports cumulative session usage on resumed turns. This report uses turn-scoped usage: first turn equals cumulative usage; second turn is computed as second cumulative usage minus first cumulative usage.

## Average Usage

| Case | Turn | Runs | Gate/action valid | Compact NE valid | Strict list valid | Avg turn input | Avg turn cached input | Avg turn fresh input | Avg turn output | Avg tools | Avg file-read estimate |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `median_minijinja` | `first` | 3 | 3 | 3 | 2 | 53938 | 47317.33 | 6620.67 | 1628.67 | 5.33 | 9.33 |
| `median_minijinja` | `second` | 3 | 3 | 3 | 2 | 47549.33 | 43861.33 | 3688 | 1475 | 4 | 7.33 |
| `p90_nutpie` | `first` | 3 | 3 | 3 | 2 | 53858 | 48000 | 5858 | 1531.67 | 5.33 | 9.33 |
| `p90_nutpie` | `second` | 3 | 3 | 3 | 2 | 46305.33 | 43178.67 | 3126.67 | 1297.33 | 3.33 | 6.67 |

## Predeclared Repeated-Query Ratios

- `median_minijinja/first_vs_second_input_tokens`: 1.134
- `median_minijinja/second_reduction_vs_first_pct`: 11.844
- `p90_nutpie/first_vs_second_input_tokens`: 1.163
- `p90_nutpie/second_reduction_vs_first_pct`: 14.023

## Decision

- The original Arm D result is treated as `NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH`.
- This file is the valid true-resume Arm D measurement.
- The true resumed second turn showed a modest input-token reduction, but did not clear the predeclared 20% improvement threshold in either frozen case.
- No live-token benefit claim for repeated exact-context cache queries is supported by this measurement.
- Cache remains an exact-context correctness/reuse feature under this result, not a measured live-token saving feature.

## Not Claimed

- No physical energy or CO2 measurement.
- No claim that Codex behavior generalizes to every agent.
- No claim that any package is safe, malware-free, or production-ready.
