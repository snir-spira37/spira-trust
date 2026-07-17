# Domain 4 / Nesira Python Harness Implementation Report

## Status

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_IMPLEMENTED
HARNESS_INTERNAL_VERDICT: DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
IMPLEMENTATION_REVIEW_REQUIRED
```

This report covers the authorized Domain 4 / Nesira Python bridge only:

```text
raw artifact world -> Python classifier -> V2 outcome tuple
V2 outcome tuple -> PythonCore decision
V2 outcome tuple -> LeanCore decision
accepted Phase 1 validator output -> end-to-end reproduction oracle
```

No Lean files, Phase 1 validator files, frozen specs, public wheel exposure,
CLI product surface, combined verdict integration, Phase 2 trust checks, or
release surfaces were modified.

## Implemented Files

```text
source/spira_core/nesira_domain4_v2_core.py
source/spira_core/nesira_domain4_v2_classifier.py
source/spira_core/nesira_domain4_v2_harness.py
tools/run_domain4_nesira_python_harness.py

tests/test_domain4_nesira_python_core.py
tests/test_domain4_nesira_classifier.py
tests/test_domain4_nesira_harness.py

research/formal_core/domain4/nesira_python_harness_fixtures/*
research/formal_core/domain4_nesira_python_harness_results.json
```

## Layer 1 - Exhaustive PythonCore / LeanCore Agreement

```text
core_agreement_total_tuples: 118098
python_record_count: 118098
lean_record_count: 118098
core_agreement_disagreements: 0
```

PythonCore was implemented as a direct translation of the accepted V2 decision
table:

```text
ExecutionMeta first
artifact_kind branch second
first-match outcome precedence
Phase1Action without PROCEED
```

The Layer 1 check compares every PythonCore output to the accepted Lean dump.
The comparison is exhaustive, not sampled.

## Layer 2 - Classification Mutation Pairs

All required safety-critical mutation targets are covered:

```text
ContextOutcome.CONTEXT_EXPECTED_MISSING
ContextOutcome.CONTEXT_MISMATCH
DirectoryEvidenceOutcome.DIR_AS_FILE
DuplicateOutcome.DUP_PRESENT
ExecutionMeta.INPUT_MALFORMED
ExecutionMeta.TOOL_ERROR
HashOutcome.HASH_MISMATCH
PathOutcome.PATH_UNSAFE
SymlinkOutcome.SYMLINK_ESCAPE
```

Metrics:

```text
safety_critical_values_without_mutation_pair: 0
mutation_pair_misses: 0
false_valid_count: 0
false_proceed_count: 0
ordinary_document_failure_classified_as_tool_error_count: 0
not_applicable_misread_as_check_performed_count: 0
```

During implementation, the classifier initially misread
`LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH` as a context mismatch because it
matched a broad `_MISMATCH` suffix rule. The harness caught the projection
defect. The classifier now maps only explicit context/profile mismatch reason
codes to `ContextOutcome.CONTEXT_MISMATCH`.

## Layer 3 - Phase 1 Reproduction

```text
phase1_reproduction_divergences: 0
phase1_outcomes_not_reproduced: 0
reason_codes_not_reproduced: 0
reproduced_reason_code_count: 14
```

The bridge preserves Phase 1 action/status semantics:

```text
VALID -> VALID_STRUCTURAL_ONLY -> REPORT_NOT_EVALUATED
INVALID -> INVALID -> STOP_BLOCKED
RERUN_REQUIRED -> RERUN_REQUIRED -> RERUN_REQUIRED
NOT_EVALUATED -> NOT_EVALUATED -> REPORT_NOT_EVALUATED
TOOL_ERROR -> TOOL_ERROR -> STOP_BLOCKED
```

## Determinism and Public Surface

```text
two_run_semantic_diff: 0
public_wheel_built: true
domain4_or_phase1_modules_present_in_public_wheel: []
```

The public wheel builder is allowlist-based. The new Domain 4 modules are not
included in the public wheel and no wheel-builder change was required.

## Verification Commands

```text
$env:PYTHONPATH='source'; python tools/run_domain4_nesira_python_harness.py --output research/formal_core/domain4_nesira_python_harness_results.json
```

Result:

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
```

```text
$env:PYTHONPATH='source'; python -m pytest tests/test_domain4_nesira_python_core.py tests/test_domain4_nesira_classifier.py tests/test_domain4_nesira_harness.py -q
```

Result:

```text
5 passed
```

```text
$env:PYTHONPATH='source'; python -m compileall -q source/spira_core/nesira_domain4_v2_core.py source/spira_core/nesira_domain4_v2_classifier.py source/spira_core/nesira_domain4_v2_harness.py tools/run_domain4_nesira_python_harness.py
```

Result:

```text
PASS
```

```text
git diff --check
```

Result:

```text
PASS
```

New-artifact local path / secret scan:

```text
PASS
```

## Full Pytest Status

Full pytest was executed:

```text
$env:PYTHONPATH='source'; python -m pytest -q
```

Result:

```text
286 passed
```

The previous full-pytest blocker was resolved by the accepted Option A boundary
fix. The Formal Core V1 external reproduction package now verifies the
V1-scoped Lean target (`lake build SpiraFormalCore`) and does not import or
build Domain4 through the V1 verification path. A full `lake build` still builds
Domain4 independently through the separate `SpiraFormalCoreDomain4` target.

Boundary result:

```text
V1 target excludes Domain4: PASS
full Lake build includes Domain4: PASS
Formal Core V1 package hash checks: PASS
Formal Core V1 verify_all.ps1: PASS
post-V1-verify full pytest: 286 passed
```

## Boundary

This implementation does not prove raw-world classification in general. The
following remain empirical and ledger-bound:

```text
JSON parsing correctness
DSSE envelope / payload decoding correctness
filesystem reads, file existence, and file type classification
symlink resolution on Windows and POSIX
SHA-256 computed over the correct bytes
path normalization and canonicalization correctness
faithfulness of each computed flag to the real artifact
```

This implementation does not authorize:

```text
Phase 2
signature verification
signer identity or authority checks
isolation runner implementation
permission to sever
public CLI or public wheel exposure
combined verdict integration
public capability claim
release
```
