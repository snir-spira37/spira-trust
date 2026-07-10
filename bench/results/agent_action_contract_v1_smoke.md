# Agent Action Contract v1 Smoke

Date: 2026-07-10

This smoke measurement checks the first `SPIRA_AGENT_ACTION_V1` fields inside
`agent_summary.json`.

The measurement reran local graph checks against the two wheels used in
`bench/results/live_v1/` and recorded the resulting `agent_summary.json` sizes.

| Case | agent_summary bytes | Contract schema | Stop | Action | Reason codes |
|---|---:|---|---:|---|---|
| `median_minijinja` | 2,879 | `SPIRA_AGENT_ACTION_V1` | true | `REPORT_NOT_EVALUATED` | `REPORT_NOT_EVALUATED` |
| `p90_nutpie` | 2,907 | `SPIRA_AGENT_ACTION_V1` | true | `REPORT_NOT_EVALUATED` | `REPORT_NOT_EVALUATED` |

This keeps both summaries below the 3KB guard while adding explicit
`decision_semantics_version`, `reason_codes`, and the embedded action contract.

Not claimed:

- This is not a rerun of the live API token benchmark.
- This does not measure cache savings.
- This does not claim all future summaries will be below 3KB.
