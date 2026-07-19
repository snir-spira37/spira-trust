# Nesira Phase 2 Isolation Attestation Adapter Local Review

## Verdict

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_LOCAL_REVIEW_ACCEPTED
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_COLD_VERIFICATION_REQUIRED
```

This review accepts only the local isolation attestation adapter implementation
gate. It does not authorize a runner, runtime observation, CLI, combined
verdict integration, public wheel exposure, public claims, or release.

## Scope Review

Result: PASS

The implementation is limited to attestation checking under a declared
`ATTESTATION_AUTHORITY`. It verifies the attestation signature and checks claims
against caller-supplied expected context.

It does not execute or observe a runtime, filesystem, network, process, or
severance action.

## Language Guard Review

Result: PASS

The harness enforces an allowlist for attestation outputs. Metrics:

```text
forbidden_isolation_language_hits: 0
non_allowlisted_isolation_language_hits: 0
```

Reason codes use attestation language:

```text
ATTESTATION_VERIFIED_UNDER_DECLARED_AUTHORITY
ATTESTATION_CLAIMS_MISMATCH
ATTESTATION_SIGNATURE_INVALID
ATTESTATION_CLOCK_NOT_EVALUATED
```

## Caveat Carrying Review

Result: PASS

Every isolation sub-verdict carries:

```text
PT-ISOLATION-01
```

including the sufficient case:

```text
valid_attestation_under_declared_authority -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

The composition oracle wiring also preserves the caveat on the sufficient
composite row:

```text
composite_caveat_mismatches: 0
```

## Binding Review

Result: PASS

The adapter compares payload claims to caller-supplied expected context:

```text
candidate_id
candidate_hash
environment_id
profile_id
profile_version
```

The expected values are not learned from the attestation payload.

## Trap Review

Result: PASS

The Phase 2 trust-model traps are enforced:

```text
missing declared attestation root -> TRUST_NOT_EVALUATED
known undeclared attestation authority -> TRUST_INSUFFICIENT
claim mismatch -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
clock missing with expired attestation -> TRUST_NOT_EVALUATED
```

Metrics:

```text
missing_root_mapped_to_insufficient: 0
known_undeclared_authority_mapped_to_not_evaluated: 0
claims_mismatch_mapped_to_not_evaluated: 0
clock_failure_mapped_to_temporal_invalid: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
```

## Dependency And Wheel Boundary

Result: PASS

The adapter reuses the existing pinned adapter crypto dependency and adds no
new dependency. The project dependency list remains empty, and the public wheel
excludes the adapter and crypto package:

```text
dependencies = []
wheel_exclusion_failures: 0
adapter_entries: []
cryptography_entries: []
metadata_dependency_headers: []
```

## Regression Gates

Result: PASS

Executed locally:

```text
python tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py --write-results
  -> NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_ACCEPTED

python -m pytest tests/test_nesira_phase2_isolation_attestation_adapter.py -q
  -> 12 passed

python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_nesira_phase2_authority_adapter.py tests/test_nesira_phase2_isolation_attestation_adapter.py tests/test_formal_core_v1_external_reproduction_package.py -q
  -> 46 passed

python -m compileall -q source tools tests
  -> PASS

python -m pytest -q
  -> 327 passed

git diff --check
  -> PASS
```

The Formal Core V1 external reproduction package self-check was also run
directly:

```text
SHA256SUMS total: 622
SHA256SUMS fail: 0
```

## Accepted Boundary

Accepted:

```text
isolation attestation sub-verdict classification
declared attestation authority only
caller-context binding
PT-ISOLATION-01 on every sub-verdict
language allowlist enforcement
attestation-to-composition wiring
public wheel exclusion
V1 package self-check
```

Not accepted or authorized:

```text
actual execution
runner
runtime observation
filesystem observation
network observation
process observation
permission to sever
CLI
combined verdict integration
public wheel exposure
public capability claim
release
```
