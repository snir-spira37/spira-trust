# Unification Proof

SPIRA Trust emits a small proof-carrying decision reference next to the agent
action contract.

This is not a safety proof.

It is a binding proof:

```text
typed claims
+ claims Merkle root
+ policy/context hashes
+ decision semantics version
+ action contract
-> unification_id
```

The goal is to make one narrow statement reproducible:

```text
These claims, under this policy/context and decision semantics, produced this
agent action.
```

Unification Proof produces a reproducible `unification_id` for identical
canonical claims, decision, subject, and frozen context inputs.

It is not claimed to produce the same context-derived identity across
regenerated legacy report bytes, different workdirs, command fingerprints, or
execution environments.

The distinction is:

```text
Semantic stability:
claims + decision + action

Contextual identity:
subject + claims + decision + exact bound context
```

Therefore:

```text
same meaning
!= necessarily same unification_id

same canonical and contextual inputs
= same unification_id
```

## Files

`agent_summary.json` remains the small agent-facing surface. It includes only a
compact unification reference:

```json
{
  "unification": {
    "id": "...",
    "root": "...",
    "p": "unification_proof.json"
  }
}
```

The full proof lives next to it:

```text
unification_proof.json
```

When an evidence pack is requested, `unification_proof.json` is included in the
pack.

## Claims

V1 claims are derived from the combined policy verdict layers:

```text
graph_core
pep770_sbom_consistency
pep740_offline_attestations
license_policy
entry_point_policy
target_environment
lockfile_cross_check
```

Each claim is canonical JSON with:

```text
claim_id
subject_sha256
status
source_verdict
evidence_ref
policy_ref
reason_codes
producer
```

Claim statuses are closed:

```text
OK
NOTE
WARN
NOT_EVALUATED
RERUN_REQUIRED
BLOCK
```

`NOT_EVALUATED` is preserved. It is never counted as OK.

## Merkle Root

Claims are serialized as sorted-key JSON with no extra whitespace, then placed
in a Merkle tree with SHA-256 domain separation:

```text
leaf = sha256(0x00 || canonical_claim_json)
node = sha256(0x01 || left || right)
```

The root says only:

```text
this exact claim set was used
```

It does not say:

```text
the artifact is safe
the producer identity is trusted
the claims are complete for every possible policy
```

Identity remains an attestation/signature layer. Policy evaluation remains the
deterministic SPIRA decision layer.

## Unification ID

The `unification_id` changes when any of these change:

```text
subject artifact hash
claims Merkle root
policy hash
context hash
decision semantics version
action decision
```

That makes cache and audit behavior stricter: the same action under a different
claim set or policy/context is not the same proof.

Legacy wheel evidence generation may produce equivalent claims and decisions
while changing report bytes that are bound into `context_sha256`. In that case,
semantic stability can hold while contextual identity changes. This is drift in
the exact bound context, not proof that the action semantics changed.

## Agent Rule

Agents should read `agent_summary.json` first.

They may use the unification reference as a compact handle for audit or
drill-down, but they should not infer safety from the hash.

The action remains:

```text
stop
recommended_agent_action
reason_codes
not_evaluated
```

## Not Claimed

- This does not prove the package is safe.
- This does not replace signatures or attestations.
- This does not perform zero-knowledge proof generation.
- This does not turn missing evidence into OK.
- This does not replace the full evidence pack for audit.
- This does not claim identical `unification_id` across regenerated legacy
  report bytes, different workdirs, command fingerprints, or execution
  environments.
