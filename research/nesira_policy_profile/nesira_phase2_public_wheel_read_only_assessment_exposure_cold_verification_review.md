# Nesira Phase 2 Public Wheel Read-Only Assessment Exposure Cold Verification Review

## Verdict

```text
NESIRA_PHASE2_PUBLIC_WHEEL_READ_ONLY_ASSESSMENT_EXPOSURE_COLD_VERIFICATION_ACCEPTED
```

## Source

Cold reproduction was completed from a fresh clone at:

```text
181ee58e06eb56794237ee9fc25e96421d18cb03
```

## Checks

```text
hash-locked cryptography requirements install: PASS
compileall: PASS
focused public-wheel exposure pytest: 63 passed
V1 external reproduction package test: 5 passed
V1 SHA256SUMS self-check: 622/622
full pytest: 349 passed
public wheel runtime execution: PASS
V1 Phase2 scope scan: 0 hits
git diff --check: PASS
```

The built public wheel contains the authorized runtime entries:

```text
spira_core/nesira_phase2_assessment_wiring.py
spira_core/nesira_phase2_authority_adapter.py
spira_core/nesira_phase2_identity_adapter.py
spira_core/nesira_phase2_isolation_attestation_adapter.py
spira_core/nesira_phase2_read_only_assessment_cli.py
spira_core/nesira_phase2_signature_adapter.py
```

The built public wheel contains no harness entries.

## Runtime

The public wheel module ran directly from the built wheel:

```text
python -m spira_core.nesira_phase2_read_only_assessment_cli
```

All three assessment verdicts returned exit code 0 when the tool successfully
produced an artifact:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_NOT_EVALUATED
TRUST_INSUFFICIENT
```

Malformed input returned a clean JSON tool error with exit code 2 and no Python
traceback.

## Boundary

```text
RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

Public wheel code exposure is accepted for the read-only assessment surface
only. This is not release authorization and not a public product claim.
