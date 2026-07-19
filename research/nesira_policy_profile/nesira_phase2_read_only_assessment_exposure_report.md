# Nesira Phase 2 Read-Only Assessment Exposure Report

## Status

```text
NESIRA_PHASE2_READ_ONLY_ASSESSMENT_EXPOSURE_ACCEPTED
```

## Implemented Surface

This gate implements a narrow read-only tool:

```text
tools/run_nesira_phase2_read_only_assessment.py
```

The tool reads a JSON assessment request, invokes the accepted Nesira Phase 2
assessment wiring, and emits the raw canonical JSON assessment artifact.

It optionally writes the same artifact to an output file. That is the only
authorized write.

## Read-Only Boundary

The tool does not implement:

```text
runner
combined verdict
public wheel exposure
public claim
release
severance action
```

It does not add a console entry point and does not modify `pyproject.toml`.
`cryptography` remains gated through the existing hash-locked adapter
requirements and is not a product dependency.

## Important CLI Invariants

```text
exit code reflects tool success, not permission to act
verdict tokens are emitted verbatim
no relabeling to approved/safe/proceed language
no action-like flags
no forbidden action-like output fields
malformed input returns a clean tool error, not a Python traceback
two-run semantic equality is preserved
```

The implemented tool returns exit code 0 for any successfully produced
assessment artifact, including non-sufficient assessments. Non-zero exit codes
are reserved for tool/input failures.

## Focused Tests

```text
tests/test_nesira_phase2_read_only_assessment_exposure.py
8 passed

read-only exposure + wiring + V1 package tests:
25 passed
```

## Full Verification

Completed:

```text
compileall: PASS
focused read-only/wiring/V1 pytest: 25 passed
full pytest: 347 passed
git diff --check: PASS
```

## Cold Reproduction

Completed from a fresh clone at commit:

```text
9f9729d83015a1a2bc4948a0867ca4672c5aef2a
```

Cold reproduction covered:

```text
hash-locked cryptography requirements install: PASS
read-only CLI exit-code matrix: PASS
malformed input clean JSON error: PASS
compileall: PASS
focused read-only/wiring/V1 pytest: 25 passed
full pytest: 347 passed
V1 SHA256SUMS self-check: 622/622
public wheel exclusion: PASS
two-run byte equality: PASS
git diff --check: PASS
```

The final accepted status is therefore backed by cold reproduction, not only by
local implementation checks.
