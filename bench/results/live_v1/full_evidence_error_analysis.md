# Full-Evidence Error Analysis

Date: 2026-07-10

This note explains the six incorrect `PROCEED` answers from the DeepSeek API file-ingestion benchmark.

## What Happened

In the broad full-evidence arm, the model received:

- `spira-decision.json`
- `graph_report.json`
- `bill_of_materials.json`
- `graph_summary.txt`
- `input_manifest.json`
- `graph_evidence_manifest.json`

It did not receive `agent_summary.json`.

Across 6/6 full-evidence runs, the model returned `PROCEED` even though the benchmark gate target was `STOP / REPORT_NOT_EVALUATED`.

## Why It Answered PROCEED

The model consistently found:

- `combined_verdict: GRAPH_OK_WITH_NOTES`
- no blockers
- no warnings
- exit code 0
- non-empty `not_evaluated`

But without the `agent_summary.json` fields `stop: true` and `recommended_agent_action: REPORT_NOT_EVALUATED`, it inferred that notes and non-evaluated layers did not block the gate.

Representative reasons:

- "All evaluated layers report OK or NOTE; no stop condition or REPORT_NOT_EVALUATED found."
- "The combined verdict is GRAPH_OK_WITH_NOTES, which maps to exit code 0 (PROCEED)."
- "5 layers were not evaluated because policies were not provided, but that does not trigger a STOP per the evidence."

## Control Run

A small control was run with the same full evidence, but with one stricter prompt rule:

> If not_evaluated is a non-empty list, answer STOP.

Result:

- `median_minijinja`: corrected to `STOP`
- `p90_nutpie`: corrected to `STOP`

Token cost remained high:

- `median_minijinja`: 15,124 prompt tokens
- `p90_nutpie`: 40,353 prompt tokens

The model still did not preserve `recommended_agent_action: REPORT_NOT_EVALUATED` exactly.

## Correct Interpretation

Do not claim:

- "More context always makes the model wrong."
- "This is a full autonomous agent benchmark."
- "This measures physical energy."

Claim:

- In this API file-ingestion benchmark, `agent_summary.json` made the gate decision cheaper and less ambiguous.
- Without an explicit deterministic stop/action surface, the model had to infer policy from broad evidence and converted `GRAPH_OK_WITH_NOTES` into `PROCEED`.
- With a hand-coded strict prompt rule, full evidence can recover the correct `STOP`, but at 15x-41x higher prompt-token cost than the summary path.

## Publication-Safe Sentence

In live DeepSeek API runs with evidence injected into the prompt, `agent_summary.json` used 2.1x fewer prompt tokens than the minimal `spira-decision.json` baseline and 15x-41x fewer than broad evidence injection. More importantly, the summary path returned the intended `STOP / REPORT_NOT_EVALUATED` decision in 6/6 runs, while the broad evidence path converted `GRAPH_OK_WITH_NOTES` into `PROCEED` in 6/6 runs unless the prompt manually encoded the missing stop rule.
