# Agent Status v1 Smoke

Date: 2026-07-10

This smoke measurement checks:

```bash
spira-trust status --agent --artifact <wheel> --format json
```

The command was run after a graph check wrote an indexed `agent_summary.json`
for the same wheel.

Measured output:

| Case | Output bytes | Checked | Action | Reason codes | Scope |
|---|---:|---:|---|---|---|
| `median_minijinja` | 901 | true | `REPORT_NOT_EVALUATED` | `NOTES_PRESENT`, `REPORT_NOT_EVALUATED` | `index_only` |

The output is below the 1KB target for a single-artifact agent status query.

Not claimed:

- This is not a cache hit implementation.
- This is not a new artifact verdict.
- This status object indexes a prior `agent_summary.json`; it does not replace
  the full summary or evidence pack.
