# SPIRA Domain 4 / Nesira Lean Implementation Authorization

## Verdict

```text
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_AUTHORIZED
```

This authorization opens the first Domain 4 / Nesira code gate. It authorizes
only a faithful Lean translation of the accepted paper design chain:

```text
Domain4 / Nesira formal-core proposal
-> V2 flag schema
-> NOT_PROVEN ledger
-> V2 decision table
-> V2 conformance harness specification
```

Lean must translate the frozen paper design. Lean must not design new behavior.

If any accepted paper artifact cannot be translated faithfully, the correct
outcome is:

```text
SCOPE_REVISION_REQUIRED
```

not an unreviewed workaround in Lean.

## Document Type

```text
DOCUMENT_TYPE: AUTHORIZATION
OPENS: Lean implementation - FIRST CODE GATE
PHASE: PHASE_2_RESEARCH
LEAN_CODE: AUTHORIZED
PYTHON: NOT_AUTHORIZED
HARNESS_IMPLEMENTATION: NOT_AUTHORIZED
FIXTURES: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

## Frozen Inputs

The implementation must translate these accepted artifacts:

```text
research/formal_core/domain4_nesira_formal_core_proposal.md
research/formal_core/domain4_nesira_formal_core_proposal_review.md
research/formal_core/domain4_nesira_flag_schema_v1_spec.md
research/formal_core/domain4_nesira_flag_schema_v1_review.md
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.md
research/formal_core/domain4_nesira_not_proven_in_lean_ledger.json
research/formal_core/domain4_nesira_flag_schema_v2_spec.md
research/formal_core/domain4_nesira_flag_schema_v2.json
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.md
research/formal_core/domain4_nesira_phase1_outcome_traceability_v2.json
research/formal_core/domain4_nesira_flag_schema_v2_review.md
research/formal_core/domain4_nesira_decision_table_v2_spec.md
research/formal_core/domain4_nesira_decision_table_v2_review.md
research/formal_core/domain4_nesira_conformance_harness_v2_spec.md
research/formal_core/domain4_nesira_conformance_harness_v2_review.md
```

The existing Formal Core V1 Lean package remains the host package:

```text
formal/spira_formal_core_v1/
```

The toolchain remains frozen:

```text
leanprover/lean4:v4.32.0
```

## Authorized Lean Files

This phase may create only:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Meta.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Proofs.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Main.lean
```

It may update only the following existing Lean aggregation files, and only to
add imports for the authorized Domain 4 modules:

```text
formal/spira_formal_core_v1/SpiraFormalCore.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/All.lean
```

No other Lean files may be modified. In particular, this phase does not
authorize changing Domain 1, Domain 2, Domain 3, generic core definitions,
existing proof files, Lake configuration, or the Lean toolchain.

## Authorized Research Outputs

This phase may create only:

```text
research/formal_core/domain4_nesira_lean_implementation_results.json
research/formal_core/domain4_nesira_lean_implementation_report.md
research/formal_core/domain4_nesira_lean_implementation_review.md
```

If an additional artifact is required, this phase must stop and request a
separate authorization.

## Required Faithful Translation

The Lean implementation must satisfy:

```text
each Lean inductive value = one frozen V2 enum value, name-for-name or with a
documented direct mapping.

each Lean decision branch = one accepted Decision Table V2 row.

Phase1Action has no PROCEED constructor.

NesiraCoreV2 is a total pure function over ArtifactKind, ExecutionMeta,
OutcomeTuple, and Policy.

not-applicable enum values are skipped by consulted-set discipline and cannot
be read as check performed.

ordinary document-validation failures cannot be represented as TOOL_ERROR in
the decision core.
```

Lean must not introduce:

```text
new enum values
new statuses
new actions
new reason-code semantics
new trust semantics
new Phase 2 behavior
```

Any divergence from the accepted paper chain must produce:

```text
LEAN_TRANSLATION_SCOPE_REVISION_REQUIRED
```

## Required Theorem Families

The Lean implementation must prove, at minimum:

```text
tool_error_stops:
  execution_meta = TOOL_ERROR -> action = STOP_BLOCKED

input_malformed_rerun:
  execution_meta = INPUT_MALFORMED -> action = RERUN_REQUIRED

schema_structural_violation_not_valid:
  schema_outcome = SCHEMA_STRUCTURAL_VIOLATION -> action = STOP_BLOCKED

hash_mismatch_not_valid:
  artifact_kind = LEGACY_ISOLATION_RESULT
  -> hash_outcome = HASH_MISMATCH
  -> action = STOP_BLOCKED

unsafe_path_not_valid:
  artifact_kind = LEGACY_ISOLATION_RESULT
  -> path_outcome = PATH_UNSAFE
  -> action = STOP_BLOCKED

missing_evidence_not_evaluated:
  artifact_kind = LEGACY_ISOLATION_RESULT
  -> evidence_presence_outcome = EVIDENCE_MISSING
  -> action = REPORT_NOT_EVALUATED

context_expected_missing_not_evaluated:
  context_outcome = CONTEXT_EXPECTED_MISSING
  -> action = REPORT_NOT_EVALUATED

phase1_no_proceed:
  PROCEED is unrepresentable in Phase1Action.

core_deterministic:
  same artifact_kind, execution_meta, outcome tuple, and policy
  -> same machine contract.

stop_true:
  every produced Domain 4 Phase 1 contract has stop = true.
```

Auxiliary lemmas are allowed only if they preserve the accepted theorem
obligations. Theorems must not be weakened to obtain a build pass.

## Domain4 Main Dump

`Domain4/Main.lean` may expose a deterministic decision-table dump over the
full finite V2 core space:

```text
2 artifact kinds * 3 execution meta values * 3^9 outcome tuples = 118098 tuples
```

The purpose is early Lean-to-spec fidelity checking before any Python harness
exists.

Acceptance requires the implementation report to compare the Lean dump against
the frozen V2 schema / decision-table expectations and record:

```text
lean_dump_total_tuples: 118098
lean_dump_spec_disagreements: 0
```

This dump is not the Python/Lean conformance harness. The exhaustive
PythonCore == LeanCore check remains separately authorized later.

## Proof Hygiene Requirements

Acceptance requires:

```text
lake build: exit 0
offline build: required
dependency-free package: preserved
sorry occurrences in Lean files: 0
admit occurrences in Lean files: 0
custom axiom declarations: 0
sorryAx in #print axioms output: 0
unsafe decision core: 0
opaque proof escape hatches: 0
native_decide proof shortcuts: 0 unless separately reviewed
```

For every final Domain 4 theorem, the report must record:

```text
#print axioms theoremName
```

The only acceptable built-in logical axioms are the same class previously
accepted for Formal Core V1, such as:

```text
propext
Classical.choice
Quot.sound
```

Any additional axiom must stop the phase with:

```text
UNAPPROVED_AXIOM_FOUND
```

## Regression Requirements

The implementation must not regress existing Formal Core domains:

```text
Domain 1 builds
Domain 2 builds
Domain 3 builds
existing generic proofs build
existing imports remain valid
```

The report must record:

```text
lake build: PASS
Domain 1/2/3 regression: PASS
Domain 4 theorem families proved: required count / required count
```

## Stop Conditions

The implementer must stop if:

```text
accepted paper spec cannot be translated faithfully to Lean
the decision table requires a behavior not present in the frozen paper chain
a theorem cannot be proved without sorry/admit/custom axiom
Lean dump differs from the frozen decision table
Domain 1/2/3 regress
Python changes appear necessary
fixture or harness implementation appears necessary
```

The correct status in these cases is one of:

```text
LEAN_TRANSLATION_SCOPE_REVISION_REQUIRED
THEOREM_NOT_PROVABLE_WITH_ACCEPTED_DESIGN
LEAN_DUMP_SPEC_MISMATCH
DOMAIN_REGRESSION_DETECTED
IMPLEMENTATION_BLOCKED_BY_UNAUTHORIZED_DEPENDENCY
```

## Independent Verification Requirements

The implementation review must require:

```text
fresh clone or clean checkout
lake build
proof hygiene scan
#print axioms for every Domain 4 theorem
Phase1Action constructor inspection showing no PROCEED
Lean dump vs frozen decision table comparison
Domain 1/2/3 no-regression check
```

If Lean/Lake is unavailable in a review environment, the result must be:

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

not PASS.

## Not Authorized

This authorization does not authorize:

```text
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation outside Lean
conformance harness implementation
PythonCore implementation
Python/Lean exhaustive agreement implementation
Phase 1 reopening
Phase 2 implementation
signature verification
signer authority checks
isolation runner implementation
combined verdict integration
CLI or wheel exposure
public capability claims
release
version bump
tag
PyPI
```

## Required Review Outcomes

The implementation review must end in exactly one of:

```text
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_ACCEPTED
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_NEEDS_REVISION
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_REJECTED
```

Even `ACCEPTED` does not authorize Python changes, fixtures, conformance harness
implementation, Phase 2 work, public claims, or release. It only permits a
later, separate authorization request for the Python/harness gate.

## Status

```text
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_AUTHORIZED

FIRST_CODE_GATE_AUTHORIZED
LEAN_ONLY_IMPLEMENTATION_AUTHORIZED
FAITHFUL_TRANSLATION_REQUIRED
PHASE1ACTION_NO_PROCEED_REQUIRED
DOMAIN4_THEOREM_FAMILIES_REQUIRED
LEAN_DUMP_SPEC_FIDELITY_REQUIRED
LAKE_BUILD_REQUIRED
SORRY_ADMIT_AXIOM_FORBIDDEN
PRINT_AXIOMS_REQUIRED
DOMAIN1_DOMAIN2_DOMAIN3_REGRESSION_CHECK_REQUIRED

PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
