# SPIRA Formal Core V1 Python Typed-Evidence Boundary Report

## Status

```text
SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_COMPLETE

ACCEPTED_ENTRYPOINT_AVAILABLE

FOCUSED_PYTEST_PASS_8_OF_8

DOMAIN_ADAPTER_CHANGES_0

RAW_PARSER_CHANGES_0

RUNTIME_INTEGRATION_CHANGES_0

BENCHMARK_CHANGES_0
```

## 1. Scope

This report covers the Python typed-evidence boundary authorized by:

```text
research/formal_core/spira_formal_core_v1_python_typed_evidence_boundary_authorization.md
```

## 2. Implemented Boundary

Accepted entrypoint:

```text
spira_core.formal_core_v1.evaluate_typed_evidence(document)
```

The entrypoint accepts canonical typed evidence and returns a machine contract.

It does not:

```text
parse raw artifacts
call Lean
call a model
change domain adapters
integrate into production runtime
run benchmarks
```

## 3. Test Result

Command:

```text
python -m pytest tests/test_formal_core_v1_python_boundary.py -q
```

Result:

```text
8 passed
```

## 4. Covered Vectors

```text
valid proceed vector
blocking vector
required unknown vector
conflicting evidence vector
invalid evidence vector
version-incompatible vector
missing explicit list fails closed
empty explicit list distinct from missing field
model/presentation fields have no decision authority
```

## 5. Boundary Preservation

No changes were made to:

```text
Domain 1 adapter
Domain 2 adapter
Domain 3 adapter
raw parsers
runtime integration
benchmark runners
historical results
```

## 6. Result

```text
SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_READY_FOR_REVIEW
```

The next step is a separate differential harness rerun. This boundary report
does not itself claim Python/Lean equivalence.
