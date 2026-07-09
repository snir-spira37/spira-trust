# Agent Context Tax

SPIRA Trust measures a small but concrete cost in agent workflows: how much
local evidence an agent must read before it can answer a narrow gate question.

This is a context-ingestion benchmark, not a safety benchmark.

It does not claim that SPIRA makes the artifact safe, correct, malware-free, or
production-ready. It measures the bytes an agent would need to ingest to answer
questions that SPIRA already records deterministically.

## Dataset

The first measurement uses the public `spira-trust` `0.6.1` release evidence.

Release evidence:

```text
https://github.com/snir-spira37/spira-trust/releases/tag/v0.6.1
```

Measured release evidence files:

```text
graph_report.json       13,301 bytes
spira-decision.json      6,376 bytes
agent_summary.json       2,097 bytes
bill_of_materials.json  22,563 bytes
graph_summary.txt          668 bytes
```

The `status.json` used for Q2 was captured from a local workspace with:

```bash
spira-trust status <wheel> --agent-state-dir <state-dir> --format json > status.json
```

It is not part of the public `0.6.1` release assets. Q2 is reproducible only
with a local checked workspace that has an agent summary index.

## Results

Static benchmark results:

```text
flow                                                                                         base   spira   saved    pct  tok saved
-----------------------------------------------------------------------------------------------------------------------------------
Q1 verdict/stop - baseline pessimistic (full report+decision+BOM)                           42240    2097   40143  95.0%      10036
Q1 verdict/stop - baseline realistic (decision + MODELED 25% report skim)                    9701    2097    7604  78.4%       1901
Q1 verdict/stop - baseline minimal (decision only)                                           6376    2097    4279  67.1%       1070
Q2 already-checked - baseline realistic (MODELED skim)                                       9701    5934    3767  38.8%        942
Q2 already-checked - baseline minimal (decision only)                                        6376    5934     442   6.9%        110
```

The strongest conservative result is Q1 minimal:

```text
6,376 bytes -> 2,097 bytes
67.1% less context
```

That compares `agent_summary.json` against only `spira-decision.json`, the
smallest fair baseline for the verdict/stop question.

The broader Q1 result is:

```text
9,701 bytes -> 2,097 bytes
78.4% less context
```

That uses a modeled baseline: the decision file plus 25% of `graph_report.json`.
It is labeled as modeled because the skim fraction is an assumption.

## Interpretation

The result supports a narrow claim:

```text
For the SPIRA Trust 0.6.1 release evidence, agent_summary.json reduced the
context required to answer the verdict/stop question by 67.1% to 78.4% against
fair baselines.
```

The pessimistic upper bound is 95.0%, but it assumes the baseline agent reads
the full report, decision, and BOM. Treat it as an upper bound, not the headline
claim.

Q2 is weaker in the single-artifact measurement:

```text
6,376 bytes -> 5,934 bytes
6.9% less context
```

That is still positive, but it is not the main result. The likely advantage of
`status` is over a multi-artifact workspace, where one status response can cover
many checked artifacts. That has not been measured here and should remain a
hypothesis until measured.

## Stage B

The live two-arm agent benchmark was not run.

No live model API credentials were available in the measurement environment, so
no live token, latency, cost, or correctness-equivalence claim is made.

Correctness must come before savings:

```text
Arm A and Arm B must reach the same gate decision and materially equivalent
reasons before any live savings number is reported.
```

The absence of Stage B is part of the evidence, not something to hide.

## Reproduce

Run the static benchmark:

```bash
python bench/bench_agent_savings.py \
  --evidence-dir <unzipped-spira-release-evidence> \
  --status-json <captured-status.json> \
  --repeat 10 \
  --json-out bench/results/spira_0.6.1_static.json
```

The repeat factor is recorded in JSON for amortized estimates. Public tables in
this document report the per-question numbers to avoid making the arbitrary
repeat factor look like a measured property.

## Not Claimed

- This does not measure correctness or safety.
- This does not prove SPIRA saves energy or CO2.
- This does not include discovery cost; that favors the baseline.
- Token counts are estimates from bytes divided by four.
- The realistic baseline depends on a modeled 25% report skim.
- The measurement uses a minimal single-wheel graph.
- Savings are expected to grow with graph size, but that is not measured here.
