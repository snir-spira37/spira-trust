# Test/Build Failure Contract - Core Compatibility Audit

## Status

```text
CORE_CHANGE_REQUIRED
IMPLEMENTATION_NOT_AUTHORIZED
PRODUCER_NOT_AUTHORIZED
CORPUS_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
```

This is a read-only compatibility audit for the second-domain
`Test/Build Failure Contract` research path.

The audit asks one question:

```text
Can the current frozen Unification Core accept a non-wheel Domain 2 subject and
preconstructed pytest-domain typed claims without changing the core, mislabeling
the subject, or duplicating proof logic outside the core?
```

The answer is:

```text
No.
```

The general Merkle and inclusion primitives are reusable, but the current
proof assembler and adjacent agent state interfaces remain Python-wheel
specific at their input boundary.

## Baseline

```text
baseline_commit: 679c5c57db6bae0a8da7dab39e1a82c945f17492
methodology: research/test_build_failure_contract_methodology.md
declaration: research/second_domain_producer_declaration.md
```

## Reviewed Files And Hashes

```text
56f718c3eee8a829af578b5bbee0065c9ae9fc581b6adaf44cd11f6bed54fb75  source/spira_core/unification_proof.py
b19718ef59cfde37b0fd83464920c5659cd01ac944b124c3024363327e0e2c88  source/spira_core/combined_verdict.py
936e28ace3060e388367db4d5371394176dc2584a49b88eccf29f7d8082af405  source/spira_core/agent_summary.py
fee4842df9b894f2e58297150330979280679008afc892da1afbdd5e4b2ecdb0  source/spira_core/agent_status.py
651219fee08c21069ad2241801a250b2225e2d9aed7957a228efc443993f8243  source/spira_core/agent_cache.py
e9d2a06ce1b6e0b62d93937790b668f02dcd768e49d3a19fc9f3e082d6ea1809  source/spira_core/rerun_planner.py
c46c33c3cb0ca28dbcfe9e9f1b03f18cb43de4ff51fcbffaa4239ebbd838012c  source/spira_core/contracts.py
7e2e17add2be9a233687ea46ec1ee6a9b9fb67e41e4f725f8114743bfe73dc3e  docs/agent_action_contract.md
46ac75d294c2faaa6c8a0a87e3388e5cfba80898696fff5ec1ed1995e060f7c2  docs/unification_proof.md
84956ca32bad248249a4907cd5fa30f96a32c4301623143daa09923270c0739a  research/test_build_failure_contract_methodology.md
2031fb9c136ecdd46c9ef901e94b77ea33503809c06c1cef55fcb82485449993  research/second_domain_producer_declaration.md
```

## Gate Results

### 1. Accept An Explicit Non-Wheel Subject Identity

```text
FAIL
```

Evidence:

```text
source/spira_core/unification_proof.py:38
subject_sha = contract.get("artifact_sha256") or contract.get("artifact_set_sha256")

source/spira_core/unification_proof.py:85
subject.type = "python_wheel" if artifact_sha256 else "python_wheel_set"
```

The current proof assembler has no existing path to represent a subject such
as `pytest_test_run`, `test_evidence_set`, or another non-wheel subject type.

Supplying Domain 2 evidence through `artifact_sha256` would bind bytes but
mislabel the subject as `python_wheel`.

### 2. Accept Preconstructed Domain Claims Without Wheel-Specific `build_claims()`

```text
FAIL
```

Evidence:

```text
source/spira_core/unification_proof.py:34
claims = build_claims(summary, decision)

source/spira_core/unification_proof.py:126-129
build_claims() reads decision.layers.per_layer and artifact/artifact_set SHA
```

The current public assembler always builds claims from existing SPIRA wheel
decision layers. It does not accept a preconstructed list of `SPIRA_CLAIM_V1`
claims as input.

The lower-level `validate_claim_set()`, `merkle_root()`,
`inclusion_proof()`, and `verify_inclusion()` primitives are generic, but using
them directly from a producer would require the producer to assemble the proof
identity itself. That would duplicate or bypass the current core proof
assembler rather than prove compatibility with it.

### 3. Preserve Closed Claim Status Set

```text
PASS
```

Evidence:

```text
source/spira_core/unification_proof.py:15-22
STATUS_RANK includes OK, NOTE, WARN, NOT_EVALUATED, RERUN_REQUIRED, BLOCK

source/spira_core/unification_proof.py:180-188
unknown statuses raise UnificationProofError
```

The current status set is compatible with the methodology's status envelope.

### 4. Construct Existing Claims Merkle Root

```text
PARTIAL_PASS
```

Evidence:

```text
source/spira_core/unification_proof.py:285-289
merkle_root(claims) accepts a list of claim mappings

source/spira_core/unification_proof.py:306-316
leaf/node hashing is generic canonical JSON + SHA-256
```

The primitive is generic. The full proof path is not, because the assembler
does not accept prebuilt Domain 2 claims.

### 5. Construct Existing `unification_id`

```text
PARTIAL_PASS
```

Evidence:

```text
source/spira_core/unification_proof.py:62-70
unification_id binds subject_sha, claims_root, policy_sha, context_sha,
semantics version, and decision hash
```

The calculation itself is domain-neutral once inputs exist. The current
assembler does not provide a valid non-wheel input path for those inputs.

### 6. Bind Policy, Context, Decision Semantics, And Action

```text
PARTIAL_PASS
```

Evidence:

```text
source/spira_core/unification_proof.py:39-57
context hash is built from artifact-oriented contract fields and report hashes

source/spira_core/unification_proof.py:58-70
decision object and unification_id bind action semantics
```

The binding model is reusable, but the current context object is shaped around
wheel artifacts, graph reports, and decisions. Domain 2 cannot enter it without
either false field reuse or a core contract change.

### 7. Produce Inclusion Proofs

```text
PASS
```

Evidence:

```text
source/spira_core/unification_proof.py:254-283
inclusion_proof() and verify_inclusion() operate on generic claim mappings
```

The inclusion proof primitives do not depend on Python wheels.

### 8. Avoid Labeling Test Evidence As `python_wheel` Or `python_wheel_set`

```text
FAIL
```

Evidence:

```text
source/spira_core/unification_proof.py:85
subject.type is hardcoded to python_wheel or python_wheel_set
```

This is the decisive incompatibility. A Domain 2 proof produced through the
current assembler would be falsely labeled.

### 9. Avoid Deriving Domain 2 Claims From Wheel-Specific Decision Layers

```text
FAIL
```

Evidence:

```text
source/spira_core/unification_proof.py:127
layers = decision.layers.per_layer

source/spira_core/combined_verdict.py
per_layer entries are graph_core, pep770, pep740, license, entry_point,
target_environment, lockfile
```

The current claim builder is coupled to Domain 1 decision layers.

### 10. Avoid Duplicating Or Reimplementing The Core In The Producer

```text
FAIL_IF_FORCED
```

A producer could call lower-level functions such as `merkle_root()` and
`tagged_hash()`, but it would then need to recreate the proof assembly policy,
subject model, context hash, and decision object outside the existing
assembler.

That is not compatibility. It is a parallel proof assembler.

## Agent State And Reuse Compatibility

The methodology also asked whether cache/rerun semantics are independent of
Python wheels.

### Status

```text
FAIL
```

Evidence:

```text
source/spira_core/agent_status.py:94
non-.whl artifact paths return ARTIFACT_NOT_FOUND

source/spira_core/agent_status.py:345-357
_discover_wheels() only discovers *.whl inputs
```

### Cache

```text
FAIL
```

Evidence:

```text
source/spira_core/agent_cache.py:27
non-.whl artifact paths return ARTIFACT_NOT_FOUND

source/spira_core/agent_cache.py:116
cache hit output is keyed as artifact_sha256
```

### Rerun Planner

```text
FAIL_FOR_DOMAIN_2_AS_NAMED
```

Evidence:

```text
source/spira_core/rerun_planner.py:15-32
REQUIRED_CONTEXT_FIELDS include artifact_sha256 and wheel/artifact-domain
context fields

source/spira_core/rerun_planner.py:39
artifact_sha256 maps to ARTIFACT_CHANGED and verification/cache reruns
```

The planner can compare arbitrary dictionaries only if they are shaped like
the current artifact context. Reusing `artifact_sha256` to mean "test evidence
set sha" would be a semantic alias, not a clean Domain 2 compatibility path.

## Summary Matrix

```text
non-wheel subject identity                 FAIL
preconstructed Domain 2 claims             FAIL
closed claim-status set                    PASS
claims Merkle root primitive               PARTIAL_PASS
unification_id primitive                   PARTIAL_PASS
policy/context/action binding model        PARTIAL_PASS
inclusion proof primitive                  PASS
no false python_wheel labeling             FAIL
no wheel-layer claim derivation            FAIL
no proof logic duplication in producer     FAIL_IF_FORCED
status/cache/rerun domain neutrality       FAIL
```

## Decision

```text
CORE_CHANGE_REQUIRED
```

The existing core is not yet general at the input-interface level.

The architecture has reusable primitives:

```text
canonical claim validation
closed status handling
claims Merkle root
inclusion proof verification
tagged unification identity
decision/action binding model
```

But the current assembler and adjacent state interfaces are bound to:

```text
python_wheel / python_wheel_set subjects
artifact_sha256 / artifact_set_sha256 fields
wheel decision layers
.whl path checks
artifact-shaped cache/status/rerun contexts
```

## Consequences

The following remain not authorized:

```text
producer implementation
oracle population
corpus materialization
Domain 2 benchmark
Domain 3 discussion
release claim
```

The next valid step is an architectural proposal for a minimal core interface
change, not producer code.

That proposal must preserve Domain 1 behavior and should be reviewed as a
core contract change. It may not be hidden inside a pytest adapter.

## Minimal Change Surface To Consider Later

This audit does not authorize changes, but it identifies the likely shape of a
future proposal:

```text
accept explicit subject {type, sha256}
accept preconstructed validated SPIRA_CLAIM_V1 list
keep status/action enum unchanged
reuse existing Merkle/inclusion/tagged-hash primitives
generalize context key names away from wheel-only artifact fields
keep Domain 1 wheel assembler as an adapter over the generic proof assembler
add Domain 1 regression proving identical unification_id/reference behavior
```

Any such proposal must include:

```text
Domain 1 regression plan
versioned contract review
frozen file manifest
explicit owner authorization
```

Until then:

```text
IMPLEMENTATION_NOT_AUTHORIZED
```
