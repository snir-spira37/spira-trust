# Domain 4 / Nesira Python Harness Review

## Verdict

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_NEEDS_REVISION
```

## Summary

The authorized Domain 4 / Nesira Python harness itself passes all internal
acceptance gates:

```text
Layer 1 exhaustive agreement: PASS
Layer 2 mutation pairs: PASS
Layer 3 Phase 1 reproduction: PASS
reason-code fidelity: PASS
two-run equality: PASS
public wheel exclusion: PASS
focused tests: PASS
compileall: PASS
git diff --check: PASS
new-artifact path/secret scan: PASS
```

However, the review cannot end in `DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED`
because the authorization required full pytest, and full pytest currently has
one failing test outside the authorized harness surface.

## Finding F1 - Full pytest blocked by stale external reproduction manifest

```text
severity: blocker for final review acceptance
affected test: tests/test_formal_core_v1_external_reproduction_package.py::test_external_reproduction_package_manifest_hashes_match
observed full pytest result: 285 passed, 1 failed
failing path: formal/spira_formal_core_v1/SpiraFormalCore.lean
```

The file is not modified by this implementation. The working tree diff confirms
no change to:

```text
formal/spira_formal_core_v1/SpiraFormalCore.lean
research/formal_core/external_reproduction_package/artifact_manifest.json
artifact_manifest.json
```

This appears to be a pre-existing stale hash in the formal external
reproduction package manifest. Because those artifacts are frozen and outside
the Domain 4 Python harness authorization, this review does not repair them.

Required next action:

```text
EXTERNAL_REPRODUCTION_MANIFEST_REFRESH_AUTHORIZATION_REQUIRED
```

or a narrower authorization that explicitly permits correcting the stale formal
external reproduction package manifest and rerunning full pytest.

## Confirmed Non-Findings

```text
PythonCore / LeanCore disagreement: none
required mutation pair missing: none
false VALID: 0
false PROCEED: 0
ordinary document failure classified as TOOL_ERROR: 0
NOT_APPLICABLE misread as check performed: 0
Phase 1 reproduction divergence: 0
reason-code fidelity divergence: 0
public wheel exposure of Domain4/Nesira modules: none
new local path / secret leak: none
```

## Projection Defect Caught During Implementation

The harness caught one local classifier projection defect before review:

```text
LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH
was initially interpreted as both:
  HashOutcome.HASH_MISMATCH
  ContextOutcome.CONTEXT_MISMATCH
```

Root cause:

```text
broad suffix matching on *_MISMATCH
```

Fix:

```text
ContextOutcome.CONTEXT_MISMATCH is now assigned only for explicit accepted
context/profile mismatch reason codes.
```

Regression coverage:

```text
tests/test_domain4_nesira_classifier.py::test_hash_mismatch_does_not_project_to_context_mismatch
```

## Boundary

This review does not authorize:

```text
Lean changes
Phase 1 validator changes
formal external reproduction package changes
Phase 2 implementation
signature verification
signer authority checks
isolation execution
permission to sever
public wheel exposure
CLI exposure
combined verdict integration
public capability claim
release
```

## Recommended Status

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_IMPLEMENTED
HARNESS_INTERNAL_VERDICT_ACCEPTED
FINAL_IMPLEMENTATION_REVIEW_NEEDS_REVISION
FULL_PYTEST_BASELINE_MANIFEST_BLOCKER_OUT_OF_SCOPE
```
