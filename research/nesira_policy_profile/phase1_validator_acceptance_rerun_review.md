# SPIRA Nesira Policy Profile - Phase 1 Validator Acceptance Rerun Review

Verdict:

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED
```

## Commit Identity

```text
remediation commit: 7d11be9a261cb3c61074a8932a8ba58a42b9ae81
acceptance review commit: RECORDED_IN_GIT_COMMIT_CONTAINING_THIS_FILE
branch: codex/formal-core-v1-lean
HEAD at rerun start: 7d11be9a261cb3c61074a8932a8ba58a42b9ae81
clean committed source before artifact generation: True
```

## V1.1 Authority

```text
ZIP SHA256: 14b19bbce4764778599b755ce614404ecc6875349c63a08efa9ad5439ef5370d
SHA256SUMS: PASS
JSON: PASS
forbidden phrase scan: PASS
authorization verdict: SPIRA_NESIRA_PHASE1_AUTHORIZATION_V1_1_ACCEPTED
PROCEED allowed: false
```

## Protected Surfaces

Protected-surface verification against `df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe`: PASS.

## Four-Finding Rerun Table

| Case | Input | Expected | Actual | Pass |
| --- | --- | --- | --- | --- |
| posix_tmp | /tmp/evidence.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| posix_root | / | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| posix_var | /var/log/example | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| posix_normalization | /tmp/../evidence.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| windows_drive_relative | C:tmp/evidence.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| windows_drive_only | C: | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| windows_d_drive | D:folder/file | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| windows_absolute_backslash | C:\tmp\evidence.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| windows_absolute_slash | C:/tmp/evidence.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| unc_backslash | \\server\share\file | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| unc_slash | //server/share/file | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| parent_traversal | ../outside.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| mixed_traversal | safe/..\outside.txt | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | INVALID / LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH | True |
| nonexistent_file | missing.txt | NOT_EVALUATED / LEGACY_ISOLATION_EVIDENCE_FILE_MISSING | NOT_EVALUATED / LEGACY_ISOLATION_EVIDENCE_FILE_MISSING | True |

Additional remediated findings:

```text
directory evidence: INVALID / ['LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE']
duplicate exact: INVALID / ['LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH']
duplicate dot equivalent: INVALID / ['LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH']
duplicate normalized equivalent: INVALID / ['LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH']
```

## Metrics

```text
PROCEED paths: 0
stop=false paths: 0
positive fixtures structurally accepted: 6/6
positive fixtures returning PROCEED: 0/6
negative invariant detection: 100%
false VALID mutation pairs: 0
unsafe paths accepted: 0
hash mismatches accepted: 0
directories accepted: 0
duplicate canonical paths accepted: 0
local path leaks: 0
```

## Required Runs

```text
python -m compileall source tests: PASS
python -m pytest tests/test_nesira_policy_profile_validator.py -q: 11 passed
python -m pytest -q: 281 passed
public wheel build: PASS
wheel inspection: PASS
JSON validation: PASS
protected-surface diff: PASS
action/schema identity: PASS
git diff --check: PASS
```

## Wheel

```text
wheel: C:\Users\snir\Documents\Codex\2026-06-11\we-are-continuing-spira-v10-0\work\github_spira_trust_formal_core_v1_lean\dist\_nesira_phase1_acceptance_rerun_wheel_check\wheelhouse\spira_trust-0.6.1-py3-none-any.whl
sha256: 12a7355f77c293bf3f4f719b1d77071c1adbdf33f88455469ba514f0ae43b497
entry_count: 56
unexpected public modules: 0
```

## Findings

No Critical/High/Medium findings.

## Boundaries Preserved

```text
CRYPTOGRAPHIC_VERIFICATION_NOT_EVALUATED
SIGNER_IDENTITY_AND_AUTHORITY_NOT_EVALUATED
ISOLATION_EXECUTION_NOT_EVALUATED
PHASE2_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
```

## Next Authorized Step

```text
PHASE1_EXTERNAL_REPRODUCTION_REQUIRED_OR_PHASE2_RESEARCH_AUTHORIZATION_PROPOSAL_REQUIRED
```

No Phase 2 work was started by this review.
