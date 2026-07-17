# Domain 4 / Nesira Python Harness Review

## Verdict

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
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
V1 reproduction boundary fix: PASS
full pytest: PASS
```

The earlier review blocker was resolved by the accepted Option A boundary fix:
the Formal Core V1 external reproduction package remains V1-scoped, while
Domain4 remains independently buildable and outside the V1 package claims.

## Finding F1 - Formal Core V1 reproduction boundary conflict

```text
severity: resolved
affected test: tests/test_formal_core_v1_external_reproduction_package.py::test_external_reproduction_package_manifest_hashes_match
observed full pytest result before fix: 285 passed, 1 failed
observed full pytest result after fix: 286 passed
failing path: formal/spira_formal_core_v1/SpiraFormalCore.lean
```

Root cause:

```text
28c8a72 Domain4 Lean implementation added Domain4 imports to the shared
SpiraFormalCore.lean aggregator.

The accepted Formal Core V1 external reproduction package is V1-scoped and
locks the pre-Domain4 hash of that same aggregator. Its inventory and claims do
not include Domain4.
```

This is not a Python harness defect and not a stale hash to refresh narrowly.
A narrow rehash would make the pytest hash check pass while leaving the
V1-scoped external reproduction package semantically inconsistent: Domain4
would be imported/built through the aggregator without being represented in the
package inventory, expected results, claims-and-boundaries, and SHA256SUMS.

Resolution:

```text
Option A implemented.
SpiraFormalCore.lean restored to the V1-scoped root imports.
SpiraFormalCore.Proofs.All restored to V1 proofs only.
lakefile.toml now defines:
  SpiraFormalCore        = V1 target
  SpiraFormalCoreDomain4 = Domain4 target
verify_all builds only SpiraFormalCore for V1 reproduction.
```

Post-fix gates:

```text
V1 target excludes Domain4: PASS
full Lake build includes Domain4: PASS
source artifact manifest hashes: PASS
SHA256SUMS: PASS
Formal Core V1 verify_all.ps1: PASS
full pytest: 286 passed
post-V1-verify full pytest: 286 passed
```

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
DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED
V1_REPRODUCTION_BOUNDARY_RESOLVED
PHASE2_NOT_AUTHORIZED
```
