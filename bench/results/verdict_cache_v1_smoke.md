# SPIRA Agent Verdict Cache v1 Smoke

Date: 2026-07-10

Command under test:

```bash
spira-trust cache \
  --artifact <wheel> \
  --command-fingerprint <summary.summary_of.command_fingerprint> \
  --agent-state-dir <state-dir> \
  --format json
```

Result on a local synthetic wheel:

```json
{
  "schema": "SPIRA_AGENT_VERDICT_CACHE_V1",
  "cache_hit": true,
  "match_scope": "full_evidence_context",
  "context_match": true,
  "recommended_agent_action": "STOP_BLOCKED"
}
```

Measured compact JSON size:

```text
1022 bytes
```

Interpretation:

```text
status --agent says: "SPIRA has seen these artifact bytes before."
cache says: "SPIRA checked these artifact bytes under this exact evidence context."
```

The cache re-hashes the current wheel before matching state. It fails closed with
`RERUN_REQUIRED` when the artifact is missing, unchecked, changed since check,
or when the requested command/policy/tool/decision-semantics context does not
match prior summaries.

Additional guards added after the initial smoke:

```text
CONTEXT_AMBIGUOUS:
same artifact bytes, multiple available contexts, no exact requested match

EXACT_CONTEXT_RESULT_CONFLICT:
same artifact bytes, same requested context, conflicting action results
```

The second case fails closed because it indicates non-determinism, corrupted
local state, manual summary edits, or an input capable of changing action that
was not included in the context fingerprint.

For conflict detection, `reason_codes` and `not_evaluated` are compared as
sorted unique string sets. Order alone is not a semantic difference.

Not claimed:

```text
This is not human approval.
This is not a malware or safety claim.
This does not reuse decisions across different evidence contexts.
```
