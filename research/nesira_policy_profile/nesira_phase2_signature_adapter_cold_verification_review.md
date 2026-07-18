# Nesira Phase 2 Signature Adapter Cold Verification Review

## Verdict

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

The signature adapter was reproduced from a fresh clone at:

```text
5801f054bc346b786e9cc1d2a2384ab99e8337b6
```

This review accepts the signature adapter as externally reproducible in the
current cold-verification environment.

It does not authorize identity, authority, isolation-attestation, an isolation
runner, CLI wiring, combined verdict integration, public wheel exposure, public
claims, or release.

## What Was Verified

The cold verification performed the checks that are material to this gate:

```text
fresh clone
checkout exact commit
hash-locked cryptography install
Formal Core V1 SHA256SUMS self-check
signature adapter conformance harness
signature adapter focused pytest
Formal Core V1 external reproduction package pytest
full pytest
compileall
public wheel exclusion through the harness
```

## Results

```text
cryptography runtime version: 49.0.0
Formal Core V1 SHA256SUMS failures: 0
signature conformance verdict: NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED
signature fixtures: 19
focused signature tests: 9 passed
Formal Core V1 external reproduction package tests: 5 passed
full pytest: 295 passed
```

Signature conformance metrics:

```text
required_signature_failure_modes_without_fixture: 0
required_signature_failure_modes_without_mutation_pair: 0
sub_verdict_mismatches: 0
unexpected_sufficient_verdicts: 0
soft_pass_revocation_unknown: 0
soft_pass_clock_failure: 0
default_trust_paths: 0
adapter_outputs_with_execution_semantics: 0
composition_mismatches: 0
wheel_exclusion_failures: 0
metadata_mentions_cryptography: false
two_run_semantic_diff: 0
```

## Boundary Finding

The previous Phase 2 Lean composition commit had left the Formal Core V1
external reproduction manifest stale for:

```text
formal/spira_formal_core_v1/lakefile.toml
```

The signature adapter implementation commit repaired that stale manifest entry
without adding Domain4, Phase 2, or adapter files to the V1 inventory.

Cold verification explicitly checked this time:

```text
Formal Core V1 SHA256SUMS self-check: PASS, 0 failures
Formal Core V1 external reproduction package tests: PASS, 5 passed
```

This closes the specific blind spot from the earlier Phase 2 Lean composition
cold verification.

## Accepted Claims

This milestone accepts only:

```text
signature adapter reproducible from a fresh clone
cryptography==49.0.0 installed from the hash-pinned requirements file
signature sub-verdict mapping matches the accepted plan
revocation unknown fails closed
clock failure fails closed
missing declared root fails closed as NOT_EVALUATED
wrong declared root fails closed as INSUFFICIENT
adapter output contains no execution or severance semantics
adapter feeds the accepted composition oracle for wiring checks
adapter and cryptography remain outside the public wheel
```

## Not Accepted

This milestone does not accept:

```text
identity established
signer authority established
authority policy checked
attestation checked
isolation occurred
isolation proven
permission to sever
safe to sever
production readiness
release readiness
```

## Required Next Gate

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_AUTHORIZATION_REQUIRED
```

The next adapter must not begin until this cold verification is treated as the
accepted baseline for the signature adapter.

## Status

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
SIGNATURE_ADAPTER_EXTERNALLY_REPRODUCIBLE
CRYPTOGRAPHY_49_0_0_HASH_LOCK_REPRODUCED
FORMAL_CORE_V1_SHA256SUMS_SELF_CHECK_ACCEPTED
FULL_PYTEST_295_PASSED
PUBLIC_WHEEL_EXCLUSION_ACCEPTED
NO_EXECUTION_SEMANTICS_ACCEPTED
IDENTITY_ADAPTER_NOT_AUTHORIZED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
