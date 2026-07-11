# Agent Action Contract

`agent_summary.json` is an agent action contract, not a second report.

The full evidence surface is for humans and auditors:

- `graph_report.json`
- `bill_of_materials.json`
- `spira-decision.json`
- evidence packs

The agent action surface is smaller and deterministic:

- `stop`
- `recommended_agent_action`
- `reason_codes`
- `not_evaluated`
- evidence pointers
- compact unification proof reference

The agent may explain the decision. It should not reinvent the artifact gate.

## Why This Exists

In the live API benchmark, a model that read broad evidence saw true facts such
as `GRAPH_OK_WITH_NOTES`, `exit_code: 0`, no blockers, and non-empty
`not_evaluated`, then inferred `PROCEED`.

When the same decision was served through `agent_summary.json`, the model kept
the intended `STOP / REPORT_NOT_EVALUATED` action in 6/6 runs.

The point is not only fewer tokens. The point is that SPIRA decides the gate
locally and serves a small, explicit action contract.

## Contract Fields

`agent_summary.json` keeps the existing `SPIRA_AGENT_SUMMARY_V1` schema and
includes an embedded action contract:

```json
{
  "schema": "SPIRA_AGENT_ACTION_V1",
  "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
  "artifact_sha256": "...",
  "artifact_set_sha256": "...",
  "policy_sha256": null,
  "command_fingerprint": "...",
  "graph_verdict": "GRAPH_OK",
  "combined_verdict": "GRAPH_OK_WITH_NOTES",
  "action_verdict": "GRAPH_OK_WITH_NOTES",
  "stop": true,
  "stop_source": "default",
  "recommended_agent_action": "REPORT_NOT_EVALUATED",
  "reason_codes": ["REPORT_NOT_EVALUATED"],
  "not_evaluated": ["pep740_offline_attestations"],
  "evidence": "spira-decision.json"
}
```

`agent_summary.json` also includes a compact unification reference:

```json
{
  "unification": {
    "id": "...",
    "root": "...",
    "p": "unification_proof.json"
  }
}
```

The full `unification_proof.json` binds typed claims, the claims Merkle root,
policy/context hashes, decision semantics, and the action decision. It proves
that this action came from this claim set and context. It does not prove that
the artifact is safe. See [`unification_proof.md`](unification_proof.md).

`policy_sha256` is `null` when no pinned policy context was supplied. A missing
policy hash is reported as missing context, not silently treated as OK.

## Closed Actions

The action value is closed and policy-neutral:

- `PROCEED`
- `ASK_HUMAN`
- `STOP_BLOCKED`
- `REPORT_NOT_EVALUATED`
- `REPORT_WITH_NOTES`
- `RERUN_REQUIRED`

Agents should dispatch on this value instead of inferring gate policy from
prose, exit codes, or report shape.

`SPIRA_DECISION_SEMANTICS_V2` derives the action from the combined policy
verdict when present, falling back to the raw graph verdict only when no
combined verdict is available. A `GRAPH_OK_WITH_NOTES` decision with no
`NOT_EVALUATED` layers becomes `REPORT_WITH_NOTES` with `stop: false`, not
`ASK_HUMAN`.

## Not Claimed

- This does not make the artifact safe.
- This does not create new evidence.
- This does not make a hash a safety claim.
- This does not turn `NOT_EVALUATED` into OK.
- This does not replace the full evidence pack for audit.
