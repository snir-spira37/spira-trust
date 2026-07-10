# Agent Action Contract v1 / Semantics v2 Smoke

Date: 2026-07-10

This smoke measurement checks the `SPIRA_AGENT_ACTION_V1` fields inside
`agent_summary.json` after the `SPIRA_DECISION_SEMANTICS_V2` change.

The measurement reran local graph checks against the two wheels used in
`bench/results/live_v1/` and recorded the resulting `agent_summary.json` sizes.

| Case | agent_summary bytes | Semantics | Graph verdict | Action verdict | Stop | Action | Reason codes |
|---|---:|---|---|---|---:|---|---|
| `median_minijinja` | 2,995 | `SPIRA_DECISION_SEMANTICS_V2` | `GRAPH_OK` | `GRAPH_OK_WITH_NOTES` | true | `REPORT_NOT_EVALUATED` | `NOTES_PRESENT`, `REPORT_NOT_EVALUATED` |
| `p90_nutpie` | 3,023 | `SPIRA_DECISION_SEMANTICS_V2` | `GRAPH_OK_WITH_UNVERIFIED` | `GRAPH_OK_WITH_NOTES` | true | `REPORT_NOT_EVALUATED` | `NOTES_PRESENT`, `REPORT_NOT_EVALUATED` |

This keeps both summaries below the 3KB guard while adding explicit
`decision_semantics_version`, `reason_codes`, and the embedded action contract.
The margin is intentionally small in these frozen cases, so future work should
separate a strict size guard for the embedded action contract from the broader
`agent_summary.json` regression guard.

Not claimed:

- This is not a rerun of the live API token benchmark.
- This does not measure cache savings.
- This does not claim all future summaries will be below 3KB.
