# Nesira Phase 2 Public Wheel Read-Only Assessment Exposure Review

## Verdict

```text
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_ACCEPTED
```

## Review Scope

This review covers the implementation and cold reproduction of the narrow
public wheel read-only assessment exposure. It does not authorize combined
verdict integration, runner execution, public claims, release, or severance
action.

## Findings

The implementation exposes only the authorized runtime surface in the public
wheel:

```text
assessment wiring
signature adapter
identity adapter
authority adapter
isolation attestation adapter
read-only assessment CLI module
```

Harnesses, fixtures, tests, reports, Lean files, runner code, and combined
verdict integration are absent from the wheel.

## Crypto Posture

The base project dependency list remains empty. `cryptography==49.0.0` appears
only under the explicit optional extra:

```text
nesira-assessment
```

It is not an unconditional base wheel dependency.

## Runtime Boundary

The public wheel module preserves the read-only contract:

```text
exit 0 for successfully produced SUFFICIENT / INSUFFICIENT / NOT_EVALUATED artifacts
non-zero only for tool/input failure
raw verdict tokens preserved
clean JSON error for malformed input
no action-like output fields
```

## V1 Boundary

The V1 external reproduction manifest refresh is narrow:

```text
artifact_manifest.json: pyproject.toml entry only
SHA256SUMS: pyproject.toml + artifact_manifest.json only
V1 SHA256SUMS self-check: 622/622
```

The V1 inventory, claims, expected results, and Formal Claims documents were
not changed and do not include Nesira Phase 2 runtime claims.

## Local Verification

```text
focused public-wheel exposure pytest: 63 passed
V1 external reproduction package test: 5 passed
full pytest: 349 passed
compileall: PASS
git diff --check: PASS
```

## Boundary

```text
RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

## Cold Reproduction

Cold reproduction was completed from a fresh clone at:

```text
181ee58e06eb56794237ee9fc25e96421d18cb03
```

Cold checks passed:

```text
hash-locked cryptography requirements install
focused public-wheel exposure pytest: 63 passed
V1 external reproduction package test: 5 passed
V1 SHA256SUMS self-check: 622/622
full pytest: 349 passed
compileall
public wheel runtime execution from built wheel
V1 Phase2 scope scan: 0 hits
git diff --check
```

The gate is fully accepted after cold reproduction.
