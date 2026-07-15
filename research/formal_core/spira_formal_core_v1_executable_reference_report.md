# SPIRA Formal Core V1 Executable Reference Report

## Status

```text
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_COMPLETE

LAKE_BUILD_PASS

REFERENCE_VECTORS_PASS_8_OF_8

MODEL_CALLS_0

RAW_PARSERS_0

PYTHON_CHANGES_0

DOMAIN_ADAPTER_CHANGES_0
```

## 1. Scope

This report covers the executable Lean reference phase authorized by:

```text
research/formal_core/spira_formal_core_v1_executable_reference_authorization.md
```

The reference evaluator accepts typed evidence only and evaluates the accepted
Lean core definitions.

It does not parse raw artifacts and does not call a model.

## 2. Added Lean Files

```text
SpiraFormalCore/Reference.lean
SpiraFormalCore/TestVectors.lean
SpiraFormalCore/Main.lean
```

The Lake executable target is:

```text
spira-formal-core-v1
```

## 3. Commands

```text
lake build

lake exe spira-formal-core-v1
```

## 4. Results

The executable produced:

```text
valid proceed vector: PASS
blocking vector: PASS
required unknown vector: PASS
conflicting evidence vector: PASS
invalid evidence vector: PASS
version-incompatible vector: PASS
Gate A preservation vector: PASS
model-non-authority vector: PASS
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_PASS
```

## 5. Boundary Preservation

The reference phase did not introduce:

```text
wheel parsing
pytest/JUnit parsing
Terraform JSON parsing
model calls
Python integration
Domain adapter conformance
benchmark execution
```

## 6. Result

```text
SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_READY_FOR_REVIEW
```

The next phase requires a Python/Lean equivalence protocol. No Python changes
are authorized by this result.
