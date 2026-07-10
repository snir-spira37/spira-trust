# Agent Integration

SPIRA Trust can be used by coding agents as a local command-line tool.

The goal is simple:

```text
Agents build artifacts.
SPIRA verifies artifacts.
Humans approve.
```

This is artifact trust, not code review. SPIRA does not decide whether an
agent's patch is good. It gives the agent a deterministic local check for
Python wheel artifacts before install or release.

## Why Give An Agent A Local Gate?

Without a local tool, an agent may spend tokens reading directories, comparing
files, summarizing build outputs, and guessing what changed.

SPIRA turns that into a mechanical command:

```bash
spira-trust graph dist \
  --output-dir out/spira \
  --sbom cyclonedx-json \
  --evidence-pack out/spira-evidence.zip
```

The agent can then read:

```text
out/spira/agent_summary.json
out/spira/spira-decision.json
out/spira/spira-decision.md
out/spira/graph_summary.txt
```

A typical agent-facing funnel looks like:

```text
MB of local artifacts -> KB of evidence -> a small decision/summary the agent reads
```

In one local pytest wheelhouse check, SPIRA reduced about 1.77 MB of wheel
artifacts to a 62 KB graph report, an 85 KB BOM, a 6.3 KB
`spira-decision.json`, and a 1.5 KB human summary. The agent still has access
to the full evidence, but it does not need to infer the verdict by reading the
wheelhouse by hand.

## Agent Action Contract

`agent_summary.json` is the agent action contract. It carries the deterministic
gate action that the agent should follow:

```json
{
  "agent_action_contract": {
    "schema": "SPIRA_AGENT_ACTION_V1",
    "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
    "stop": true,
    "recommended_agent_action": "REPORT_NOT_EVALUATED",
    "reason_codes": ["REPORT_NOT_EVALUATED"]
  }
}
```

The agent may explain the decision, but should not reinvent the gate decision
from `GRAPH_OK_WITH_NOTES`, exit code, blockers, notes, or prose. See
[`agent_action_contract.md`](agent_action_contract.md).

## Prompt Snippet For `CLAUDE.md` / `AGENTS.md`

Paste this into your project instructions if you want the agent to gate wheel
artifacts after builds:

````markdown
## SPIRA Trust Artifact Gate

After building any Python wheel, run SPIRA Trust before installing, releasing,
or marking the build complete.

Use:

```bash
spira-trust graph dist \
  --output-dir out/spira \
  --sbom cyclonedx-json \
  --evidence-pack out/spira-evidence.zip
```

Then read:

- `out/spira/agent_summary.json`
- `out/spira/spira-decision.json`
- `out/spira/spira-decision.md`
- `out/spira/graph_summary.txt`

Rules:

- Treat `agent_summary.json` as the action contract.
- If the decision is `GRAPH_BLOCK`, stop and report the evidence to the human.
- If the decision is `GRAPH_WARN`, stop and ask the human whether to proceed.
- If `agent_summary.json` says `stop: true`, follow its closed
  `recommended_agent_action` value.
- If the decision contains `NOT_EVALUATED`, report exactly which layer did not run.
- Never describe an unchecked layer as OK.
- Never mark a build/release complete without a SPIRA verdict.
- Do not install or execute the wheel to "test it" unless the human explicitly asks.
````

## Single-Wheel Check

For one wheel:

```bash
spira-trust trust dist/example-1.0.0-py3-none-any.whl \
  --output-dir out/spira-trust \
  --format json
```

Read:

```text
out/spira-trust/artifact_trust_report.json
out/spira-trust/artifact_trust_summary.txt
```

Agent rule:

```text
TRUST_BLOCK means stop.
TRUST_WARN means ask.
TRUST_OK_WITH_NOTES means summarize the notes.
```

## Example Agent Workflow

```text
1. Agent edits code.
2. Agent runs tests.
3. Agent builds wheel into dist/.
4. Agent runs spira-trust graph dist --output-dir out/spira --evidence-pack out/spira-evidence.zip.
5. Agent reads out/spira/agent_summary.json, then opens decision/report files if needed.
6. Agent reports:
   - verdict
   - checked layers
   - NOT_EVALUATED layers
   - evidence path
7. Human approves or rejects.
```

## Local Status Index

After at least one graph run, an agent can ask SPIRA what local wheel artifacts
already have a summary:

```bash
spira-trust status dist --format json
```

`status` re-hashes current wheels before matching local state. It is an index,
not a replacement for `agent_summary.json` or the full evidence pack.

For a single artifact, agents can request a compact action status:

```bash
spira-trust status --agent --artifact dist/example-1.0.0-py3-none-any.whl --format json
```

This returns a small `SPIRA_AGENT_ARTIFACT_STATUS_V1` object with `checked`,
`changed_since_check`, `decision_semantics_version`, `stop`,
`recommended_agent_action`, `reason_codes`, and `summary_path`. If the current
artifact bytes do not match the indexed summary, the action is
`RERUN_REQUIRED`.

## Context-Aware Verdict Cache

`status --agent` answers a narrow index question:

```text
Have these exact artifact bytes been seen in local SPIRA summaries?
```

When the agent needs to reuse a prior decision, use the context-aware cache:

```bash
spira-trust cache \
  --artifact dist/example-1.0.0-py3-none-any.whl \
  --command-fingerprint <command-fingerprint-from-agent-summary> \
  --format json
```

The cache re-hashes the current wheel and returns a hit only when the previous
summary matches the requested evidence context:

```json
{
  "schema": "SPIRA_AGENT_VERDICT_CACHE_V1",
  "cache_hit": true,
  "match_scope": "full_evidence_context",
  "context_match": true,
  "stop": true,
  "recommended_agent_action": "REPORT_NOT_EVALUATED"
}
```

If the artifact changed, was not checked, or the same bytes were checked under
a different command, policy, tool version, or decision semantics version, the
cache fails closed with `RERUN_REQUIRED`. If multiple prior summaries exist for
the same artifact bytes but none match the requested context, the result marks
`context_ambiguous: true`.

If multiple summaries match the exact requested context but disagree on the
action result, the cache also fails closed:

```json
{
  "cache_hit": false,
  "context_match": true,
  "result_conflict": true,
  "recommended_agent_action": "RERUN_REQUIRED",
  "reason_codes": ["EXACT_CONTEXT_RESULT_CONFLICT"]
}
```

This indicates non-determinism, corrupted local state, a manually edited
summary, or a missing input in the context fingerprint.
`reason_codes` and `not_evaluated` are canonicalized as sorted unique string
sets for this comparison; their order is not part of the action semantics.

The graph command fingerprint is part of the cache key. Its invariant is:

```text
Any graph input capable of changing verdict/action must change one of:
command_fingerprint, policy_sha256, decision_semantics_version, tool_version.
```

For `graph`, the fingerprint covers artifact bytes, strict-closure mode,
policy files, lockfile, target environment, embedded SBOM verification mode,
attestation inputs, attestation trust root inputs, and tool version.

This preserves the distinction:

```text
status says: "SPIRA has seen these bytes before."
cache says: "SPIRA checked these bytes under this exact evidence context."
```

## What The Agent Should Not Claim

The agent must not say:

- "The code is safe."
- "The package has no malware."
- "The release is production-ready."
- "All layers passed" when some layers are `NOT_EVALUATED`.

The agent may say:

```text
SPIRA verified the local wheel evidence it was configured to check.
The decision file is at out/spira/spira-decision.json.
The evidence pack is at out/spira-evidence.zip.
```

## Install

```bash
python -m pip install spira-trust
```

For production CI, pin the version if your team requires a reproducible
toolchain.
