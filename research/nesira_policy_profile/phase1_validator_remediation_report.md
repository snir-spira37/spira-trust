# SPIRA Nesira Policy Profile - Phase 1 Validator Remediation Report

Verdict:

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_REMEDIATION_COMPLETE
```

This remediation addressed only the four High path/evidence findings from the failed acceptance review. It did not start Phase 2, change Formal Core, change action vocabulary, or expose the validator in the public wheel.

## Authority

```text
Authorization: SPIRA_NESIRA_PHASE1_AUTHORIZATION_V1_1_ACCEPTED
Authoritative V1.1 ZIP SHA256: 14b19bbce4764778599b755ce614404ecc6875349c63a08efa9ad5439ef5370d
Previous acceptance verdict: SPIRA_NESIRA_PHASE1_VALIDATOR_NEEDS_REVISION
```

## Four Findings

```text
POSIX absolute path classification: PASS
Windows drive/UNC path classification: PASS
Directory-as-evidence classification: PASS
Duplicate canonical evidence path classification: PASS
local absolute path leaks in remediated directory result: 0
```

## Remediation Case Matrix

| Case | Status | Reason Codes | Action | Stop |
| --- | --- | --- | --- | --- |
| posix_absolute_tmp | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| posix_absolute_root | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| posix_absolute_var | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| posix_absolute_with_normalization | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| windows_drive_relative | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| windows_drive_only | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| windows_drive_relative_lower | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| windows_absolute_backslash | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| windows_absolute_slash | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| unc_backslash | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| unc_slash | INVALID | LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | STOP_BLOCKED | True |
| directory_evidence | INVALID | LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE | STOP_BLOCKED | True |
| duplicate_exact | INVALID | LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH | STOP_BLOCKED | True |
| duplicate_dot_equivalent | INVALID | LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH | STOP_BLOCKED | True |

## Regression

```text
compileall: PASS
focused pytest: 11 passed
full pytest: 281 passed
git diff --check: PASS
protected surfaces: PASS
public wheel build: PASS
public wheel exclusion: PASS
```

## Acceptance Metrics

```text
positive fixtures structurally accepted: 6/6
positive fixtures yielding PROCEED: 0/6
negative invariant detection: 100%
false VALID mutation pairs: 0
unsafe evidence paths accepted: 0
hash mismatches accepted: 0
directories accepted as evidence files: 0
duplicate canonical evidence paths accepted: 0
local absolute paths leaked in results: 0
```

## Next Step

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTANCE_RERUN_REQUIRED
```

This remediation verdict does not declare Phase 1 accepted.
