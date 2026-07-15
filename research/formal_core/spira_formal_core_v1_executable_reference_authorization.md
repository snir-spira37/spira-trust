# SPIRA Formal Core V1 Executable Reference Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_AUTHORIZED

EXECUTABLE_REFERENCE_PHASE_ONLY

MACHINE_CHECKED_PROOFS_FROZEN

LEAN_REFERENCE_EVALUATOR_AUTHORIZED

TYPED_EVIDENCE_TEST_VECTORS_AUTHORIZED

REFERENCE_MAIN_AUTHORIZED

REFERENCE_RESULTS_AUTHORIZED

REFERENCE_REPORT_AUTHORIZED

REFERENCE_REVIEW_REQUIRED

PYTHON_INTEGRATION_NOT_AUTHORIZED

PYTHON_LEAN_EQUIVALENCE_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a pure executable Lean reference layer for SPIRA
Formal Core V1.

The objective is to demonstrate that the accepted and proved Lean definitions
can evaluate bounded typed-evidence test vectors.

This is not Python integration and not a Python/Lean equivalence claim.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

SEVEN_THEOREM_FAMILIES_MACHINE_CHECKED

LAKE_BUILD_PASS

NO_SORRY_ADMIT_CUSTOM_AXIOM_OR_SORRYAX
```

## 3. Authorized Files

This phase may create or modify:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Reference.lean
formal/spira_formal_core_v1/SpiraFormalCore/TestVectors.lean
formal/spira_formal_core_v1/SpiraFormalCore/Main.lean
formal/spira_formal_core_v1/SpiraFormalCore.lean
formal/spira_formal_core_v1/lakefile.toml
```

Required research outputs:

```text
research/formal_core/spira_formal_core_v1_executable_reference_results.json
research/formal_core/spira_formal_core_v1_executable_reference_report.md
research/formal_core/spira_formal_core_v1_executable_reference_review.md
```

## 4. Required Reference Behavior

The executable reference must:

```text
accept only typed evidence

validate evidence validity/version

execute the accepted Lean core definitions

return a machine contract or fail-closed error result

never call a model

never parse wheel/JUnit/Terraform raw input

never implement separate decision logic outside the accepted core definitions
```

## 5. Required Test Vectors

At least the following typed-evidence vectors are required:

```text
valid proceed vector

blocking vector

required unknown vector

conflicting evidence vector

invalid evidence vector

version-incompatible vector

Gate A preservation vector

model-non-authority vector
```

The vectors must exercise the accepted core definitions and must not introduce
domain raw parsers.

## 6. Acceptance Gates

This phase can be accepted only if:

```text
lake build: PASS

reference vectors: PASS

valid proceed vector: PASS

blocking vector: PASS

required unknown vector: PASS

conflicting evidence vector: PASS

invalid evidence vector: PASS

version-incompatible vector: PASS

Gate A preservation vector: PASS

model-non-authority vector: PASS

no sorry/admit/axiom/sorryAx: PASS

no Python changes: PASS

no domain adapter changes: PASS
```

## 7. Non-Authorization

This document does not authorize:

```text
Python source changes

Python/Lean equivalence protocol

generic differential harness

Domain 1/2/3 conformance

runtime integration

benchmark execution

merge to main

release/version/tag/PyPI
```

## 8. Required Review Result

The executable reference review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_REJECTED
```

Only accepted status may open the Python/Lean equivalence protocol phase.
