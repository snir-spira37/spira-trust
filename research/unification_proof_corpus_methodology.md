# SPIRA Unification Proof Corpus Methodology

## Status

```text
METHODOLOGY_LOCKED_BEFORE_UNIFICATION_CORPUS_RUN
```

## Boundary

This document authorizes one measurement experiment for one existing SPIRA
domain:

```text
Python wheel artifact evidence with PEP 770 / SBOM coverage
```

The experiment evaluates `Unification Proof V1` as a binding layer over the
existing SPIRA Trust decision flow.

It does not authorize:

```text
broad Context Firewall claim
new adapter
second producer
SPIRA OS
orchestrator
new safety claim
new SBOM correctness claim
```

The current implementation baseline is:

```text
commit: 01edc85338b9d2a2a942f06014e188e56d54a56a
feature: Harden unification proof invariants
```

## Research Question

Can the existing SPIRA Trust verification flow emit a deterministic
proof-carrying action reference across a frozen real corpus, while preserving
the same action semantics as the combined verdict and failing closed on
ambiguous or invalid claim state?

The measured chain is:

```text
artifact evidence
-> combined verdict
-> agent action contract
-> typed claims
-> claims_merkle_root
-> unification_id
-> compact agent reference
```

The experiment tests the unification core. It does not test whether every claim
is true in the external world.

## Corpus

The primary corpus is derived from the already frozen PEP 770 survey manifest:

```text
manifest: research/pep770_survey/results/snapshot_v3_2026-07-09_manifest.json
schema: SPIRA_PEP770_SURVEY_CORPUS_MANIFEST_V3
packages: 2,085
selection rule: newest x86_64/amd64 wheel by PyPI upload time, falling back to newest py3-none-any wheel
```

Only wheels materialized from this manifest may be used for the main corpus
run. If the wheels are not already present locally, a materialization step must
run before the corpus evaluation and must write:

```text
package
version
wheel filename
download URL
downloaded_at
wheel_sha256
download status
```

The materialized wheel manifest is frozen before any unification result is
computed. After unification results are observed, the corpus may not be
replaced merely because another corpus produces a more favorable outcome.

If a wheel from the frozen manifest cannot be downloaded or its SHA does not
match the materialization record, that wheel is reported as corpus-unavailable.
It is not silently replaced.

## Negative Fixtures

The corpus run must include a separate fixture block for known invalid or
boundary states. Fixture results are reported separately from the real PyPI
corpus.

The fixture block must cover, where locally available:

```text
RECORD mismatch
SBOM not wheel-scoped
schema-invalid but checked fields consistent
attestation digest mismatch
missing identity trust root
policy change
artifact byte mutation
unknown claim status
missing or invalid subject hash
duplicate claim_id
```

Fixture failures do not become findings about PyPI packages. They test whether
the unification layer preserves the fail-closed behavior required by the
contract.

## Measurements

For every successfully evaluated wheel, the run records:

```text
wheel_sha256
combined_verdict
action_verdict
stop
recommended_agent_action
reason_codes
not_evaluated
proof_generated
proof_error
claim_count
worst_claim_status
claims_merkle_root
unification_id
compact_reference_bytes
full_proof_bytes
evidence_pack_overhead_bytes
generation_time_ms
```

The run also verifies at least one inclusion proof per generated proof. If a
proof has no claims, that is a failure because `Unification Proof V1` requires
an explicit claim set.

For reproducibility, each selected item is evaluated twice from the same inputs
in the same run environment. The following fields must be identical across both
evaluations:

```text
claims_merkle_root
unification_id
decision.stop
decision.recommended_agent_action
decision.reason_codes
decision.not_evaluated
coverage.claim_count
coverage.worst_claim_status
```

`created_at` is excluded from reproducibility checks.

## Equivalence Rules

The proof decision must match the existing agent action contract exactly for:

```text
action_verdict
stop
recommended_agent_action
reason_codes
not_evaluated
decision_semantics_version
```

`NOT_EVALUATED` must remain visible. It is never counted as OK, never dropped
from the action contract, and never hidden inside the proof.

`BLOCK` must remain blocking. A proof may bind a blocking decision, but it may
not reinterpret that decision into a proceed action.

## Mutation Rules

The run must include deterministic mutation checks on a bounded sample of the
corpus and on the negative fixtures.

Each relevant mutation must change either `claims_merkle_root`,
`unification_id`, or fail closed:

```text
artifact bytes changed
policy_sha256 changed
command_fingerprint changed
decision_semantics_version changed
claim status changed
claim evidence_ref changed
recommended_agent_action changed
reason_codes changed
not_evaluated changed
```

For invalid claim states, the expected result is fail-closed proof creation:

```text
unknown claim status -> UnificationProofError
missing/invalid subject hash -> UnificationProofError
duplicate claim_id -> UnificationProofError
```

## Inclusion Proof Rules

For every generated proof, inclusion verification is tested for at least one
claim selected deterministically:

```text
prefer a BLOCK claim
else prefer a NOT_EVALUATED claim
else use the lexicographically first claim_id
```

The selected inclusion proof must verify against the claim and fail after a
single deterministic claim mutation.

This proves membership in the typed claim set only. It does not prove the raw
evidence files are complete or true.

## Size Rules

The size measurements are descriptive unless a separate guard already exists.

The run reports:

```text
compact reference bytes in agent_summary.json
full unification_proof.json bytes
evidence-pack overhead bytes caused by adding unification_proof.json
```

The compact agent-facing reference is the value relevant to context ingestion.
The full proof size is reported separately and must not be described as the
agent summary size.

No fixed 2.8KB claim is predeclared. The measured distribution decides the
reported numbers.

## Timing Rules

Generation time is measured locally as wall-clock time around proof creation
and serialization.

Timing is reported as:

```text
median
p90
max
```

The timing result is not a CPU, energy, or CO2 claim.

## Success Criteria

The corpus run passes only if all required correctness gates pass:

```text
100% action equivalence for generated proofs
100% reproducibility for same inputs, excluding timestamps
100% inclusion proof verification for selected claims
100% inclusion proof failure after selected claim mutation
100% fail-closed behavior for invalid claim status, subject hash, and duplicate claim_id fixtures
100% preservation of NOT_EVALUATED and BLOCK semantics
```

If any correctness gate fails, the result is:

```text
UNIFICATION_CORPUS_FAIL
```

and no release or product claim may be made from that run.

Unavailable corpus wheels are counted separately and do not count as proof
failures, but a high unavailable rate must be reported prominently.

## Value Criteria

After correctness passes, the report may evaluate whether `Unification Proof
V1` adds value beyond the existing `agent_action_contract`.

Valid value evidence includes:

```text
claim membership can be verified without reading the full report
claim-set changes produce a different identity
policy/context/action binding is reproducible by another process
selective audit drill-down reads fewer bytes than full evidence
the compact reference preserves the action while keeping the proof out of the agent-facing summary
```

If no workflow shows value beyond the existing action contract, the result is
still allowed to be a useful audit layer, but not a product-centerpiece claim.

## Not Claimed

This experiment does not claim:

```text
the wheel is safe
the SBOM is correct
every typed claim represents reality
the claim producer is trusted by itself
the proof is a signature
the proof is a zero-knowledge proof
SPIRA is a universal Context Firewall
the architecture works for Kubernetes, Terraform, DB schemas, logs, or tests
large token savings across all agent work
energy or CO2 savings
```

## Reporting Rules

The final report must include:

```text
methodology commit
implementation commit
corpus manifest path
materialized wheel manifest path, if any
number of corpus wheels selected
number of wheels materialized
number unavailable
number evaluated
number with proof generated
number failed closed
all correctness gate results
compact reference size distribution
full proof size distribution
evidence-pack overhead distribution
generation time distribution
fixture results
not_claimed block
```

Aggregate statistics may be public.

Named package findings are not published as package defects unless they were
manually reviewed and maintainers were contacted when appropriate.

## Next Authorized Action

The only next authorized action under this methodology is:

```text
materialize the frozen PEP 770 corpus, if needed
run the Unification Proof V1 corpus evaluation
write aggregate results
```

The next action is not:

```text
build another producer
build an orchestrator
generalize to Context Firewall
publish a safety claim
replace the corpus after observing results
```

## Decision After The Run

If the run fails any correctness gate:

```text
stop
fix the implementation or methodology bug
rerun only under a new versioned methodology if the measurement contract changes
```

If the run passes correctness but shows no value beyond the action contract:

```text
keep Unification Proof V1 as an audit/reproducibility layer
do not expand to a second producer from this result alone
```

If the run passes correctness and demonstrates a real selective-audit or
drill-down workflow:

```text
document the value
then, and only then, consider a second independent producer experiment
```

The preferred second producer candidate remains:

```text
Test/Build Failure Contract
```

It is not authorized by this document.

