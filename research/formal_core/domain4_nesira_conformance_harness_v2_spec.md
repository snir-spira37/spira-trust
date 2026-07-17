# SPIRA Domain 4 / Nesira Conformance Harness V2 Specification

## Status

```text
DOCUMENT_TYPE: SPECIFICATION
HARNESS_ID: SPIRA_NESIRA_DOMAIN4_CONFORMANCE_HARNESS_V2
INPUT_SCHEMA: SPIRA_NESIRA_DOMAIN4_FLAGS_V2
DECISION_TABLE: SPIRA_NESIRA_DOMAIN4_DECISION_TABLE_V2
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_PROOF: NOT_AUTHORIZED
PYTHON_CHANGES: NOT_AUTHORIZED
FIXTURE_MATERIALIZATION: NOT_AUTHORIZED
PHASE1_REOPEN: NOT_AUTHORIZED
PHASE2_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document specifies the future conformance harness between:

```text
world -> flags      Python classification, not proven in Lean
flags -> contract   future Lean decision core, intended to be proven
```

It is a paper specification only. It does not implement Lean, Python, fixtures,
tests, product integration, Phase 2 trust, public claims, or release behavior.

## Purpose

The harness has two layers with different strength:

```text
Layer 1: core agreement
  PythonCore and LeanCore agree on every tuple in the finite V2 enum space.
  This is exhaustive, not sampled.

Layer 2: classification faithfulness
  Python raw-artifact classification flips the expected V2 enum value under
  minimal mutation pairs for safety-critical outcomes.
  This is empirical, not a Lean proof.
```

The harness closes:

```text
Python decision-core implementation agrees with the future Lean decision core
over the full finite enum space.

Python raw-to-enum classification is sensitive to the dangerous mutations that
could otherwise create false VALID / unsafe weakening.
```

The harness does not close:

```text
general correctness of JSON parsing
general correctness of DSSE decoding
general filesystem behavior
general symlink resolution correctness
general SHA-256 correctness over arbitrary bytes
general path canonicalization correctness
general faithfulness of raw -> enum classification
```

Those remain covered by `SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1`.

## Layer 1: Exhaustive Core Agreement

### Finite Space

The V2 core input space is finite:

```text
artifact_kind: 2 values
execution_meta: 3 values
outcome types: 9
values per outcome type: 3
```

The full Cartesian space is:

```text
2 * 3 * 3^9 = 118098 tuples
```

The future harness must enumerate all 118098 tuples, including tuples that
cannot arise from accepted Phase 1 raw artifacts. Impossible tuples still test
totality and agreement of the decision core.

### Core Interfaces

The future harness must define two identical core interfaces:

```text
PythonCore:
  canonical OutcomeTuple JSON
  -> canonical MachineContract JSON

LeanCore:
  canonical OutcomeTuple JSON
  -> canonical MachineContract JSON
```

An equivalent Lean interface may emit the full decision table as canonical data
instead of evaluating one tuple at a time, if and only if the comparison remains
exhaustive over the same finite tuple space.

### Agreement Assertion

For every tuple:

```text
canonical(PythonCore(tuple)) == canonical(LeanCore(tuple))
```

Required metric:

```text
core_agreement_total_tuples: 118098
core_agreement_disagreements: 0
```

Any nonzero disagreement is a hard failure:

```text
DOMAIN4_NESIRA_CORE_AGREEMENT_FAILED
```

### Tuple Totality

The future harness must confirm both cores return a non-permissive, canonical
machine contract for every tuple. No tuple may:

```text
fall through
return null
return an exception as PASS
return PROCEED
omit stop=true
omit not_claimed boundaries
```

If a tuple is outside the raw-artifact reachable set but inside the V2 enum
Cartesian space, both cores must still agree deterministically.

## Layer 2: Classification Faithfulness Mutation Pairs

Layer 2 checks the unproven raw -> enum boundary empirically.

For each safety-critical enum value or meta state listed below, the future
harness must provide at least one minimal mutation pair:

```text
base artifact:
  classifies to the safe/OK enum value

mutated artifact:
  changes exactly the intended raw condition
  classifies to the target unsafe enum value
  changes the resulting machine contract as expected
```

### Required Mutation Targets

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

`ContextOutcome.CONTEXT_EXPECTED_MISSING` is included even though its action is
`REPORT_NOT_EVALUATED`, because a false classification could hide a required
absence of evaluation.

The harness may add mutation pairs for non-safety-critical outcomes, but these
additional pairs must not dilute or replace the required safety-critical set.

### Required Mutation-Pair Fields

Each mutation pair must specify:

```text
mutation_pair_id
artifact_kind
base_fixture_id
mutated_fixture_id
target_enum_type
base_enum_value
mutated_enum_value
raw_change_description
expected_base_status
expected_mutated_status
expected_base_action
expected_mutated_action
expected_reason_codes
expected_not_evaluated
expected_not_claimed
safety_critical
derived_from
ledger_ids
```

### Mutation Minimality

The mutation must be local to the intended classification boundary.

Examples:

```text
HASH_MISMATCH:
  change evidence file bytes while leaving declared digest unchanged.

PATH_UNSAFE:
  change only the evidence path string to traversal / absolute / UNC /
  drive-qualified / empty component form.

SYMLINK_ESCAPE:
  change only filesystem topology so an existing evidence path becomes a
  symlink or resolves outside evidence_root.

DUP_PRESENT:
  add or alter one manifest entry so two entries resolve to the same canonical
  path.

DIR_AS_FILE:
  replace one evidence file with a directory at the same path.

CONTEXT_MISMATCH:
  change one context field while keeping required context present.

CONTEXT_EXPECTED_MISSING:
  remove one required expected/current context field.

INPUT_MALFORMED:
  provide bytes that cannot be decoded as JSON before artifact validation.

TOOL_ERROR:
  induce a validator/tool failure path without representing an ordinary
  document-validation failure as TOOL_ERROR.
```

If a mutation requires changing multiple independent raw properties, the future
review must reject it or mark:

```text
MUTATION_PAIR_NOT_MINIMAL
```

## Layer 3: Reason-Code Fidelity

The decision table intentionally leaves fine reason-code resolution outside the
Lean proof core. The harness must verify that accepted Phase 1 reason-code
fidelity is preserved.

For each fixture:

```text
expected validation_status
expected recommended_agent_action
expected reason_codes
expected blocking_items
expected not_evaluated
expected not_claimed
expected V2 enum classification
```

must match actual Python Phase 1 output and classifier output.

Reason-code refinements that must remain testable include at least:

```text
DSSE payload missing / invalid type / invalid base64 / invalid UTF-8 / invalid JSON
severance schema invalid / unsupported version
severance expected context missing / context mismatch
severance temporal invalid / issued in future / expired
legacy isolation schema invalid / unsupported version
legacy isolation expected context missing / context mismatch / profile mismatch
unsafe evidence path refinements under PATH_UNSAFE
missing evidence file
symlink escape
directory-as-file
duplicate canonical path
hash mismatch
validator tool error
```

Required metric:

```text
reason_codes_not_reproduced: 0
phase1_outcomes_not_reproduced: 0
```

## Canonical Serialization

The future harness must use canonical JSON for:

```text
OutcomeTuple
MachineContract
expected results
actual results
core-agreement table
mutation-pair manifest
```

Canonical JSON means:

```text
UTF-8
sorted object keys
exact enum strings
no insignificant whitespace
no timestamps
no host paths
no environment metadata
no runtime duration
no nondeterministic ordering
```

## Two-Run Equality

The future harness must run all deterministic checks twice:

```text
core agreement enumeration
classification mutation pairs
reason-code fidelity checks
```

Required metric:

```text
two_run_semantic_diff: 0
```

The comparison must be byte-for-byte over canonical artifacts, not a loose
summary comparison.

## Required Metrics

The future harness result must include:

```text
core_agreement_total_tuples
core_agreement_disagreements
safety_critical_values_without_mutation_pair
mutation_pairs_total
mutation_pairs_passed
phase1_outcomes_not_reproduced
reason_codes_not_reproduced
false_valid_count
false_proceed_count
not_applicable_misread_as_check_performed_count
ordinary_document_failure_classified_as_tool_error_count
two_run_semantic_diff
```

Acceptance requires:

```text
core_agreement_disagreements: 0
safety_critical_values_without_mutation_pair: 0
phase1_outcomes_not_reproduced: 0
reason_codes_not_reproduced: 0
false_valid_count: 0
false_proceed_count: 0
not_applicable_misread_as_check_performed_count: 0
ordinary_document_failure_classified_as_tool_error_count: 0
two_run_semantic_diff: 0
```

## Required Harness Artifacts In A Future Implementation

This specification does not authorize creation of these artifacts now. A future
implementation authorization must define at least:

```text
domain4_nesira_core_agreement_results.json
domain4_nesira_classification_mutation_manifest.json
domain4_nesira_classification_mutation_results.json
domain4_nesira_reason_code_fidelity_results.json
domain4_nesira_conformance_harness_results.json
domain4_nesira_conformance_harness_report.md
domain4_nesira_conformance_harness_review.md
```

## NOT_PROVEN Binding

Every report or claim produced by a future harness must carry the accepted
NOT_PROVEN ledger boundary:

```text
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
```

In particular, the harness must not claim that mutation pairs prove general
raw -> enum correctness. They provide empirical evidence over selected
safety-critical boundaries.

## Not Authorized

This specification does not authorize:

```text
Lean definitions
Lean proof scripts
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation
conformance harness implementation
decision-table implementation
Phase 1 reopening
Phase 2 implementation
signature verification
signer authority checks
isolation runner implementation
combined verdict integration
CLI or wheel exposure
public capability claims
release
```

## Status

```text
SPIRA_NESIRA_DOMAIN4_CONFORMANCE_HARNESS_V2_SPECIFIED

EXHAUSTIVE_CORE_AGREEMENT_REQUIRED
FULL_ENUM_SPACE_SIZE_118098
CLASSIFICATION_MUTATION_PAIRS_REQUIRED
SAFETY_CRITICAL_ENUM_MUTATIONS_REQUIRED
REASON_CODE_FIDELITY_REQUIRED
TWO_RUN_EQUALITY_REQUIRED
NOT_PROVEN_LEDGER_BINDING_REQUIRED

LEAN_IMPLEMENTATION_AUTHORIZATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
