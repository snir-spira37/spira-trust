# Domain 1 Identity Baseline Materialization Authorization

## Status

```text
DOMAIN_1_IDENTITY_BASELINE_MATERIALIZATION_AUTHORIZED
BASELINE_MATERIALIZATION_ONLY
GATE_A_IMPLEMENTATION_NOT_AUTHORIZED
CORE_CHANGE_NOT_AUTHORIZED
PRODUCER_NOT_AUTHORIZED
DOMAIN_2_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

This document authorizes one narrow research action: materialize the frozen
Domain 1 identity baseline required by:

```text
research/domain_neutral_unification_core_interface_proposal_v3.md
```

It does not authorize Gate A implementation.

## Authorized Output

The only authorized new result artifact is:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

Supporting logs or scratch files may be generated locally during the run, but
only the reviewed, privacy-safe baseline artifact may become the public result
unless a separate review authorizes additional artifacts.

## Baseline Commit

The baseline must be generated from the current frozen pre-change core:

```text
baseline_commit: 8049eb0eaf49c277b3835f569c7938d2c0ba3817
```

The materialization runner must verify that the checked-out source tree and the
core files used for proof generation match the intended baseline before
writing the artifact.

## Authorized Actions

This authorization permits only:

```text
1. Read the frozen Domain 1 corpus manifest and materialized corpus records.
2. Verify the expected 1,954 Domain 1 corpus entries.
3. Run the existing Domain 1 proof generation path without code changes.
4. Extract identity hashes and decision/action fields for each wheel.
5. Write domain1_identity_baseline_v1.json.
6. Compute domain1_identity_baseline_root.
7. Validate 1,954/1,954 records.
8. Run JSON validation.
9. Run privacy, path, and secret scans.
10. Document any non-materializable condition.
```

## Explicitly Not Authorized

This authorization does not permit:

```text
generic proof assembler implementation
core refactor
new subject interface
action enum changes
claim status changes
decision semantics changes
Domain 2 producer
Domain 2 corpus
oracle population
new corpus selection
corpus replacement
Gate B work
Domain 3 work
release
version bump
tag
PyPI publish
```

## Required Inputs

The baseline materialization must use the frozen Domain 1 corpus artifacts:

```text
research/unification_proof_corpus/results/materialized_v1_2026-07-12.json
research/unification_proof_corpus/results/full_v1_public_results.json
research/unification_proof_corpus/report_v1.md
```

The materialization must record:

```text
source commit
corpus manifest SHA-256
materialized manifest SHA-256
materialization tool name and version
unification proof schema
unification reference schema
decision semantics version
canonicalization rules
volatile fields excluded
record ordering
baseline-root construction
expected record count: 1954
```

## Required Baseline Artifact Shape

The artifact must include top-level metadata:

```text
schema
schema_version
baseline_commit
tool_version
decision_semantics_version
unification_proof_schema
unification_reference_schema
corpus_manifest_sha256
materialized_manifest_sha256
corpus_size: 1954
generation_timestamp
volatile_fields_excluded
canonicalization_contract
record_ordering
domain1_identity_baseline_root
```

It must include exactly 1,954 per-wheel records.

Each record must include:

```text
artifact_sha256
canonical_claims_bytes_sha256
claims_merkle_root
context_sha256
canonical_decision_bytes_sha256
unification_id
compact_reference_bytes_sha256
canonical_proof_bytes_sha256
stop
recommended_agent_action
reason_codes
not_evaluated
worst_claim_status
```

## Canonicalization Rules

The run must choose and record the proof-byte comparison rule before generating
results:

```text
hash canonical proof excluding declared volatile fields
```

or:

```text
hash stable proof identity projection
```

The selected rule must be recorded in `canonicalization_contract`.

The compact reference must be hashed as exact canonical bytes, not as decoded
fields.

Per-record canonical bytes must use deterministic JSON serialization:

```text
UTF-8
sorted keys
no extra whitespace
stable list ordering where the contract defines ordering
```

## Baseline Root Construction

`domain1_identity_baseline_root` must be computed from all 1,954 per-wheel
identity records after sorting by:

```text
artifact_sha256
```

The root construction must be recorded in the artifact. It may use either:

```text
sha256(canonical JSON array of sorted records)
```

or:

```text
the existing SPIRA claims-style Merkle construction over sorted identity records
```

The selected construction must be declared before results are inspected and
must not change after the run.

## Stop Conditions

Any of the following stops the materialization:

```text
missing wheel
hash mismatch
missing historical evidence
identity field not reproducible
record count != 1954
core-file hash changed
unexpected corpus mutation
JSON validation failure
privacy/path/secret scan failure
baseline root cannot be computed
```

The stop result is:

```text
DOMAIN_1_IDENTITY_BASELINE_NOT_MATERIALIZABLE
```

In that state:

```text
do not infer missing data
do not change the corpus
do not replace a corpus case
do not lower the required record count
do not continue to Gate A implementation
return to methodology review
```

## Validation Requirements

The materialization result must pass:

```text
record count == 1954
unique artifact_sha256 count == 1954
all required fields present
all SHA-256 fields lowercase 64-character hex
reason_codes sorted and unique
not_evaluated sorted and unique
domain1_identity_baseline_root recomputes
JSON parses cleanly
no private absolute paths in public artifact
no secrets
no API keys
no raw private logs
```

## Relationship To Gate A

Baseline materialization is a snapshot of existing identity.

Gate A implementation is a future change that may be tested against that
snapshot.

The first does not authorize the second.

After the baseline artifact is committed, the next required step is a separate
baseline review. Only after that review may Gate A design acceptance be
considered.

## Final Boundary

```text
authorized now:
  materialize Domain 1 identity baseline only

not authorized now:
  change the core
  implement Gate A
  implement Domain 2
  populate Domain 2 oracle
  run Domain 2 corpus
  work on Gate B
```
