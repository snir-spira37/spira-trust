# SPIRA Domain 4 / Nesira Python Harness Authorization

## Verdict

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_AUTHORIZED
```

This authorization opens the second Domain 4 / Nesira code gate. It authorizes
only the Python bridge between accepted Phase 1 behavior and the accepted Lean
Domain 4 core:

```text
raw artifact world -> Python classifier -> V2 outcome tuple
V2 outcome tuple -> PythonCore decision
V2 outcome tuple -> LeanCore decision
accepted Phase 1 validator output -> end-to-end reproduction oracle
```

The goal is to prove by executable checks that the accepted Lean core is
faithfully connected to Python and to the accepted Phase 1 validator. This is
not Phase 2 trust implementation.

## Document Type

```text
DOCUMENT_TYPE: AUTHORIZATION
OPENS: Python core + classifier + fixtures + conformance harness
PHASE: PHASE_2_RESEARCH
PYTHON_CODE: AUTHORIZED
FIXTURES: AUTHORIZED
HARNESS_IMPLEMENTATION: AUTHORIZED
LEAN_CHANGES: NOT_AUTHORIZED
PHASE1_CHANGES: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

## Prior Accepted Inputs

This authorization depends on:

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED
SPIRA_NESIRA_PHASE1_COLD_EXTERNAL_REPRODUCTION_ACCEPTED

DOMAIN4_NESIRA_PAPER_DESIGN_CHAIN_COMPLETE
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_ACCEPTED
DOMAIN4_NESIRA_LEAN_COLD_VERIFICATION_ACCEPTED
```

Frozen artifacts include:

```text
research/formal_core/domain4_nesira_flag_schema_v2_spec.md
research/formal_core/domain4_nesira_flag_schema_v2.json
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.md
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.json
research/formal_core/domain4_nesira_decision_table_v2_spec.md
research/formal_core/domain4_nesira_decision_table_v2_review.md
research/formal_core/domain4_nesira_conformance_harness_v2_spec.md
research/formal_core/domain4_nesira_conformance_harness_v2_review.md
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/*
research/formal_core/domain4_nesira_lean_implementation_review.md
```

## Frozen Inputs Not To Edit

This phase must not modify:

```text
source/spira_core/nesira_policy_profile_validator.py
formal/spira_formal_core_v1/**
research/formal_core/domain4_nesira_*_spec.md
research/formal_core/domain4_nesira_*_review.md
research/formal_core/domain4_nesira_*_authorization.md
Phase 1 fixtures, acceptance artifacts, and external reproduction package
Domain 1 / Domain 2 / Domain 3 Lean or Python artifacts
```

The Phase 1 validator is an oracle for Layer 3. It is read-only in this phase.

## Authorized Python Files

This phase may create only these new implementation files:

```text
source/spira_core/nesira_domain4_v2_core.py
source/spira_core/nesira_domain4_v2_classifier.py
source/spira_core/nesira_domain4_v2_harness.py
tools/run_domain4_nesira_python_harness.py
```

These files must be research / harness files. They must not wire the module into
public CLI, public wheel exposure, combined verdict, MVP, release packaging, or
Phase 2 execution.

## Authorized Tests

This phase may create only these tests:

```text
tests/test_domain4_nesira_python_core.py
tests/test_domain4_nesira_classifier.py
tests/test_domain4_nesira_harness.py
```

The tests must not modify existing Phase 1 tests except through separate
authorization.

## Authorized Fixtures

This phase may create a new fixture corpus only under:

```text
research/formal_core/domain4/nesira_python_harness_fixtures/
```

The corpus must include:

```text
fixture_manifest.json
README.md
base/*.json
mutations/*.json
expected_results.json
```

Any filesystem fixture payloads must remain inside this directory and must be
path-safe:

```text
no absolute paths
no local home paths
no traversal
no symlink escape unless intentionally modeled as a mutation fixture
no credentials or private data
synthetic evidence only
```

## Authorized Result Artifacts

This phase may create:

```text
research/formal_core/domain4_nesira_python_harness_results.json
research/formal_core/domain4_nesira_python_harness_report.md
research/formal_core/domain4_nesira_python_harness_review.md
```

If any additional file is needed, this phase must stop and request a separate
authorization.

## Required Three Agreement Layers

### Layer 1 - Exhaustive Core Agreement

PythonCore must faithfully translate the accepted `decision_table_v2` and agree
with LeanCore over the entire finite V2 core space:

```text
2 artifact kinds * 3 execution meta values * 3^9 outcome tuples = 118098
```

Acceptance requires:

```text
core_agreement_total_tuples: 118098
core_agreement_disagreements: 0
```

This is exhaustive, not sampled.

### Layer 2 - Classification Faithfulness

The classifier must map raw Phase 1 artifacts and evidence conditions to V2
outcome tuples. For every safety-critical target, the fixture corpus must
include a minimal mutation pair that flips the expected enum value.

Required mutation targets:

```text
ExecutionMeta.INPUT_MALFORMED
ExecutionMeta.TOOL_ERROR
HashOutcome.HASH_MISMATCH
PathOutcome.PATH_UNSAFE
SymlinkOutcome.SYMLINK_ESCAPE
DuplicateOutcome.DUP_PRESENT
DirectoryEvidenceOutcome.DIR_AS_FILE
ContextOutcome.CONTEXT_MISMATCH
ContextOutcome.CONTEXT_EXPECTED_MISSING
```

Acceptance requires:

```text
safety_critical_values_without_mutation_pair: 0
mutation_pair_misses: 0
false_valid_count: 0
false_proceed_count: 0
ordinary_document_failure_classified_as_tool_error_count: 0
not_applicable_misread_as_check_performed_count: 0
```

### Layer 3 - End-To-End Phase 1 Reproduction

The harness must close the loop back to the accepted Phase 1 validator:

```text
PythonCore(classifier(raw_artifact)) == Phase1Validator(raw_artifact)
```

over the authorized Domain 4 fixture corpus.

The comparison must cover:

```text
validation_status
recommended_agent_action
stop
reason_codes
blocking_items
not_evaluated
not_claimed
artifact_type
phase1_evaluation_completed
```

Acceptance requires:

```text
phase1_reproduction_divergences: 0
phase1_outcomes_not_reproduced: 0
reason_codes_not_reproduced: 0
```

## Reason-Code Fidelity

The V2 Lean proof core resolves action/status. The Python harness must verify
the fine Phase 1 reason-code layer that the proof core intentionally leaves out.

Required reason-code families include at least:

```text
NESIRA_PHASE1_MALFORMED_JSON
NESIRA_PHASE1_MALFORMED_DSSE_ENVELOPE
DSSE_PAYLOAD_TYPE_INVALID
DSSE_PAYLOAD_MISSING
DSSE_PAYLOAD_BASE64_INVALID
DSSE_PAYLOAD_UTF8_INVALID
DSSE_PAYLOAD_JSON_INVALID
SEVERANCE_SCHEMA_INVALID
SEVERANCE_SCHEMA_VERSION_UNSUPPORTED
SEVERANCE_EXPECTED_CONTEXT_MISSING
SEVERANCE_<FIELD>_MISMATCH
SEVERANCE_TEMPORAL_BINDING_INVALID
SEVERANCE_ISSUED_AT_IN_FUTURE
SEVERANCE_EXPIRED
LEGACY_ISOLATION_RESULT_SCHEMA_INVALID
LEGACY_ISOLATION_SCHEMA_VERSION_UNSUPPORTED
LEGACY_ISOLATION_PROFILE_VERSION_UNSUPPORTED
LEGACY_ISOLATION_EVIDENCE_SCHEMA_INVALID
LEGACY_ISOLATION_EXPECTED_CONTEXT_MISSING
LEGACY_ISOLATION_<FIELD>_MISMATCH
LEGACY_ISOLATION_PROFILE_MISMATCH
LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH
LEGACY_ISOLATION_EVIDENCE_FILE_MISSING
LEGACY_ISOLATION_SYMLINK_ESCAPE
LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE
LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH
LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH
NESIRA_PHASE1_VALIDATOR_TOOL_ERROR
```

Reason-code-only refinements must not be promoted into Lean proof-core enums.

## Required Determinism

The harness must run twice and compare canonical semantic outputs:

```text
core agreement results
classifier results
mutation-pair results
Phase 1 reproduction results
reason-code fidelity results
```

Acceptance requires:

```text
two_run_semantic_diff: 0
```

Canonical output must contain no timestamps, host paths, local usernames,
runtime durations, nondeterministic ordering, credentials, or private data.

## Faithful Translation Requirements

PythonCore must translate the accepted V2 decision table. It must not design
new behavior.

If PythonCore and LeanCore disagree for any tuple:

```text
PYTHONCORE_LEANCORE_DISAGREEMENT
IMPLEMENTATION_MUST_STOP
```

If the classifier cannot faithfully derive a required V2 enum from accepted
Phase 1 behavior:

```text
CLASSIFIER_SCOPE_REVISION_REQUIRED
```

If V2 reproduction differs from accepted Phase 1:

```text
PHASE1_REPRODUCTION_DIVERGENCE
IMPLEMENTATION_MUST_STOP
```

Silent correction by changing Phase 1, Lean, or the frozen specs is forbidden.

## Public Surface Restrictions

The new Domain 4 Python/harness files must remain research-only. This phase
does not authorize:

```text
public wheel inclusion
CLI command
combined verdict integration
MVP integration
release packaging
public capability claim
```

If a wheel is built during verification, the review must confirm that Domain 4
Nesira harness modules are not exposed as a public product surface unless a
separate authorization explicitly changes that boundary.

## Required Verification

The implementation review must run:

```text
fresh clone or clean checkout
python harness command
focused tests
full pytest
two-run equality
whole-tree local path / secret scan for new artifacts
public wheel exclusion check, if a wheel is built
git diff --check
```

It must report:

```text
Layer 1: 118098 / 118098 agreement, 0 disagreements
Layer 2: all required mutation pairs pass
Layer 3: 0 divergences against accepted Phase 1 validator
reason-code fidelity: PASS
two-run equality: PASS
```

## Not Proven By This Harness

The harness remains empirical for raw-world classification:

```text
NP-ADAPTER-01 JSON parsing correctness
NP-ADAPTER-02 DSSE envelope / payload decoding correctness
NP-ADAPTER-03 filesystem reads, file existence, and file type classification
NP-ADAPTER-04 symlink resolution on Windows and POSIX
NP-ADAPTER-05 SHA-256 computed over the correct bytes
NP-ADAPTER-06 path normalization and canonicalization correctness
NP-ADAPTER-07 faithfulness of each computed flag to the real artifact
```

The harness does not prove general raw -> enum correctness. It demonstrates
agreement and mutation sensitivity over the authorized corpus.

## Not Authorized

This authorization does not authorize:

```text
Lean changes
Phase 1 validator changes
accepted paper-spec changes
existing Domain 1/2/3 changes
public wheel exposure
CLI exposure
combined verdict integration
MVP integration
Phase 2 implementation
signature verification
signer authority checks
isolation runner implementation
permission to sever
public capability claims
release
version bump
tag
PyPI
```

## Required Review Outcomes

The implementation review must end in exactly one of:

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
DOMAIN4_NESIRA_PYTHON_HARNESS_NEEDS_REVISION
DOMAIN4_NESIRA_PYTHON_HARNESS_REJECTED
```

Even `ACCEPTED` does not authorize Phase 2, public product integration, public
claims, or release. It only permits a later, separate authorization request.

## Status

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_AUTHORIZED

PYTHONCORE_IMPLEMENTATION_AUTHORIZED
RAW_TO_ENUM_CLASSIFIER_AUTHORIZED
FIXTURE_MUTATION_CORPUS_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_AUTHORIZED
THREE_LAYER_AGREEMENT_REQUIRED
LAYER1_EXHAUSTIVE_CORE_AGREEMENT_REQUIRED
LAYER2_MUTATION_PAIR_CLASSIFICATION_REQUIRED
LAYER3_PHASE1_REPRODUCTION_REQUIRED
REASON_CODE_FIDELITY_REQUIRED
TWO_RUN_EQUALITY_REQUIRED

LEAN_CHANGES_NOT_AUTHORIZED
PHASE1_CHANGES_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
