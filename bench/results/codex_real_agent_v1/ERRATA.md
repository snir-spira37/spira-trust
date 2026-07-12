# Codex Real-Agent Benchmark Errata

This file records two corrections to the Codex real-agent benchmark history.
The original JSON/CSV files are retained for audit history; this errata file
defines the canonical interpretation.

## Erratum 1: Arm D Implementation Mismatch

The original `D_repeated_exact_context` rows in
`codex_real_agent_benchmark_results.json` did not create a true second Codex
turn. They asked the model to answer `first_query` and `second_query` inside one
`codex exec` invocation.

Status:

```text
NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH
```

Those rows are retained as historical data, but they are not a valid repeated
exact-context cache measurement.

The corrected measurement is:

```text
bench/results/codex_real_agent_v1/arm_d_resume/
```

## Erratum 2: Cumulative Usage Interpretation

The first true-resume Arm D run used `codex exec resume`, but interpreted
`turn.completed.usage` from the resumed turn as usage for the second turn only.
Codex reports cumulative session usage on resumed turns.

Correct calculation:

```text
second_turn_usage = second_cumulative_usage - first_cumulative_usage
```

Commit `5805e77` updated the runner and public results to store both cumulative
counters and turn-scoped deltas.

## Canonical Arm D Results

```text
median_minijinja:
first turn input:  53,938
second turn input: 47,549
reduction:         11.844%

p90_nutpie:
first turn input:  53,858
second turn input: 46,305
reduction:         14.023%
```

Conclusion:

```text
A modest live reduction was observed,
but the predeclared 20% threshold was not met.
No new repeated-cache live-token-efficiency claim is supported.
```

## Current Benchmark Interpretation

```text
A -> B:
LIVE EFFICIENCY SUPPORTED

B -> C, first query:
NO ADDITIONAL FIRST-QUERY TOKEN EFFICIENCY

D true resume:
MODEST REDUCTION OBSERVED
PREDECLARED 20% THRESHOLD NOT MET

Cache:
CORRECTNESS / SAFE REUSE / STALENESS
not a new live-token-efficiency claim
```

## Not Claimed

- No physical energy or CO2 measurement.
- No claim that Codex behavior generalizes to every agent.
- No claim that cache produces a live-token-efficiency benefit under the
  predeclared threshold.
- No claim that any package is safe, malware-free, or production-ready.
