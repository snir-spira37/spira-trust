# SPIRA Nesira Policy Profile - Phase 1 Validator Acceptance Review

Verdict:

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_NEEDS_REVISION
```

Phase 2 is not authorized. Release and public capability claims are not authorized.

## Environment

```text
branch: codex/formal-core-v1-lean
HEAD: e9417dccbae966244fc70f5b9dc32d157cfb5e07
clean worktree: false
git status entries: 4
OS: Windows-10-10.0.19045-SP0
Python: Python 3.12.10
working directory: C:\Users\snir\Documents\Codex\2026-06-11\we-are-continuing-spira-v10-0\work\github_spira_trust_formal_core_v1_lean
review commit: NOT_CREATED_IMPLEMENTATION_NEEDS_REVISION
```

The implementation is not accepted and is not committed by this review because High findings remain.

## V1.1 Package Verification

```text
ZIP SHA256: 14b19bbce4764778599b755ce614404ecc6875349c63a08efa9ad5439ef5370d
SHA256SUMS: PASS
JSON parse: PASS
path safety: PASS
package verdict: SPIRA_NESIRA_PHASE1_AUTHORIZATION_V1_1_ACCEPTED
PROCEED allowed: false
forbidden payload-authentication phrase: ABSENT
```

## Protected Surfaces

Protected-surface verification against baseline `df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe`: PASS.

No protected surface changes were observed.

## Positive / Negative / Mutation Metrics

```text
positive fixtures structurally accepted: 6/6
positive fixtures yielding PROCEED: 0/6
false VALID mutation pairs: 0
unsafe evidence paths accepted: 0
hash mismatches accepted: 0
duplicate evidence paths accepted: 1
```

## Path Security Matrix

| Case | Expected | Actual | Accepted | Finding |
| --- | --- | --- | --- | --- |
| parent traversal | INVALID | INVALID | False |  |
| nested traversal | INVALID | INVALID | False |  |
| posix absolute path | INVALID | NOT_EVALUATED | False | HIGH_STATUS_MAPPING_DIVERGENCE |
| windows absolute path | INVALID | INVALID | False |  |
| drive-relative path | INVALID | NOT_EVALUATED | False | HIGH_STATUS_MAPPING_DIVERGENCE |
| backslash traversal | INVALID | INVALID | False |  |
| mixed slash traversal | INVALID | INVALID | False |  |
| UNC path | INVALID | INVALID | False |  |
| percent-encoded traversal literal | NOT_EVALUATED_OR_INVALID | NOT_EVALUATED | False |  |
| directory evidence path | INVALID_OR_NOT_EVALUATED | TOOL_ERROR | False | HIGH_VALIDATION_FAILURE_MASKED_AS_TOOL_ERROR |
| symlink parent escape | INVALID | INVALID | False |  |
| duplicate evidence path | INVALID | VALID | True | HIGH_DUPLICATE_EVIDENCE_PATH_ACCEPTED |

## Findings

- F-HIGH-001 [High]: POSIX-style absolute evidence paths are not classified as unsafe paths on Windows
  Evidence: /tmp/evidence.txt returned NOT_EVALUATED / missing evidence instead of INVALID / unsafe evidence path.
  Required fix: Reject root-relative/POSIX-style absolute paths as unsafe before evidence existence checks.
- F-HIGH-002 [High]: Drive-relative evidence paths are not classified as unsafe paths
  Evidence: C:tmp/evidence.txt returned NOT_EVALUATED / missing evidence instead of INVALID / unsafe evidence path.
  Required fix: Reject drive-qualified or drive-relative strings before path resolution.
- F-HIGH-003 [High]: Directory evidence paths become TOOL_ERROR with local path disclosure
  Evidence: A directory in evidence_manifest triggered TOOL_ERROR with a local temp path in tool_errors/details.
  Required fix: Classify directories before read_bytes, return deterministic validation status, and avoid local path disclosure.
- F-HIGH-004 [High]: Duplicate evidence paths are accepted as VALID
  Evidence: Two identical evidence_manifest entries for evidence_a.txt returned VALID.
  Required fix: Reject duplicate evidence paths or duplicate evidence identities deterministically.
- F-INFO-001 [Informational]: Phase 1 preserves fail-closed action invariants for reviewed failures
  Evidence: All reviewed failures preserved recommended_agent_action != PROCEED and stop == true.
  Required fix: None

## Mandatory Runs

```text
python -m compileall source tests: PASS
python -m pytest tests/test_nesira_policy_profile_validator.py -q: 8 passed
python -m pytest -q: 278 passed
public wheel build: PASS
git diff --check: PASS
```

## Wheel Inspection

```text
wheel: C:\Users\snir\Documents\Codex\2026-06-11\we-are-continuing-spira-v10-0\work\github_spira_trust_formal_core_v1_lean\dist\_nesira_phase1_acceptance_wheel_check\wheelhouse\spira_trust-0.6.1-py3-none-any.whl
sha256: 12a7355f77c293bf3f4f719b1d77071c1adbdf33f88455469ba514f0ae43b497
entries: 56
nesira module present: false
research fixtures present: false
tests present: false
unexpected public-wheel modules: 0
```

## Acceptance Decision

The implementation preserves the most important fail-closed invariant: no reviewed path returned PROCEED and all reviewed paths returned stop=true. However, acceptance is blocked by High findings in path classification, duplicate evidence handling, and TOOL_ERROR overuse.

The correct next step is:

```text
SPIRA_NESIRA_PHASE1_IMPLEMENTATION_SCOPE_REVISION_REQUIRED
```

No Phase 2 work is authorized.
