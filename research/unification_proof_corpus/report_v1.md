# SPIRA Unification Proof Corpus Report V1

## Status

```text
UNIFICATION_CORPUS_PASS
```

This run evaluates `Unification Proof V1` on the frozen PEP 770 corpus under:

```text
methodology: research/unification_proof_corpus_methodology.md
runner: research/unification_proof_corpus/run_corpus.py
implementation baseline: 01edc85338b9d2a2a942f06014e188e56d54a56a
runner cleanup hardening: 2495ad9
tool-error closure: retry against same frozen corpus after review fail-closed hardening
```

## Corpus Materialization

The frozen PEP 770 survey manifest was materialized before evaluation:

```text
source manifest: research/pep770_survey/results/snapshot_v3_2026-07-09_manifest.json
materialized manifest: research/unification_proof_corpus/results/materialized_v1_2026-07-12.json
entries: 1,954
bytes downloaded and SHA-verified: 16,803,758,787
download errors: 0
SHA-256 mismatches: 0
```

Wheels were streamed and deleted after SHA verification because the full corpus
is larger than the available free disk budget. The materialized manifest records
the package, version, wheel filename, URL, byte count, and SHA-256 used for the
evaluation.

## Evaluation Result

Aggregate public results:

```text
results: research/unification_proof_corpus/results/full_v1_public_results.json
processed: 1,954
PASS: 1,954
TOOL_ERROR: 0
```

The first full pass produced 14 `TOOL_ERROR` entries. They were classified as
tooling/environment handling, not package findings. After hardening review
fail-closed behavior and runner cleanup/retry behavior, the same frozen
materialized corpus was retried for `TOOL_ERROR` entries only. The final corpus
status is `PASS` for all 1,954 materialized wheels.

For all generated proofs:

```text
action_equivalence failures: 0
reproducibility failures: 0
disk_matches_rebuilt failures: 0
inclusion_verifies failures: 0
inclusion_rejects_mutation failures: 0
mutation_changes_identity failures: 0
not_evaluated_preserved failures: 0
block_preserved failures: 0
```

Fixture fail-closed checks passed:

```text
unknown claim status -> fail closed
missing subject hash -> fail closed
duplicate claim_id -> fail closed
```

## Size And Timing

For the 1,954 generated proofs:

```text
compact reference bytes:
  median: 176
  p90: 176
  max: 176

agent_summary.json bytes:
  median: 3,184
  p90: 3,249
  max: 3,413

unification_proof.json bytes:
  median: 7,079
  p90: 7,139
  max: 7,139

evidence pack bytes:
  median: 31,276
  p90: 37,972
  max: 159,284

proof generation time:
  median: 5.47 ms
  p90: 8.897 ms
  max: 42.257 ms
```

The compact reference is the agent-facing handle. The full
`unification_proof.json` remains a drill-down artifact.

## Interpretation

This run supports the narrow claim:

```text
Across the frozen 1,954-wheel corpus, Unification Proof V1 preserved the
existing SPIRA action contract, reproduced deterministically for the same
inputs, verified selected claim inclusion, rejected selected claim mutation,
and preserved NOT_EVALUATED/BLOCK semantics for every generated proof.
```

It does not support a broad product claim outside the existing Python wheel
evidence domain.

## Not Claimed

This run does not claim:

```text
the wheels are safe
the SBOMs are correct
every claim represents external reality
producer identity is trusted by the proof alone
the proof is a signature
the proof is a zero-knowledge proof
SPIRA is a universal Context Firewall
the result generalizes to Kubernetes, Terraform, DB schemas, logs, or tests
token, CPU, energy, or CO2 savings
```

## Closed Tooling Gap

The 14 initial `TOOL_ERROR` entries were closed before this final report status.
They were not package findings.

The closure consisted of:

```text
review fail-closed hardening for post-extraction OSError/ValueError paths
runner retry support for selected result statuses
best-effort cleanup for transient Windows file-handle lifecycle issues
```

The corpus was not changed. Only prior `TOOL_ERROR` entries were retried against
the same frozen materialized manifest.

## Next Step

The next engineering step is not a new producer.

The next step is a narrow release/readiness review of the Unification Proof V1
corpus result:

```text
verify public artifacts
decide whether docs should mention corpus-scale validation
keep not_claimed boundaries unchanged
avoid cross-domain claims
```
