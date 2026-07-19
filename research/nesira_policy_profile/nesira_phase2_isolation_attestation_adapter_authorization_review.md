# Nesira Phase 2 Isolation Attestation Adapter Authorization Review

## Verdict

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_AUTHORIZATION_ACCEPTED
```

This review accepts the isolation attestation adapter authorization and
implementation plan as the next narrow Phase 2 adapter gate.

It does not authorize an isolation runner, runtime observation, CLI, combined
verdict wiring, public wheel exposure, public claims, or release.

## Review Summary

The authorization correctly separates:

```text
attestation checking
```

from:

```text
isolation execution truth
runtime observation
permission to sever
execution
```

The adapter may only evaluate whether an attestation is authentic under a
declared `ATTESTATION_AUTHORITY` and whether it claims the expected isolation
profile.

## Checks

### 1. Baselines

Result: PASS

The authorization requires:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

before isolation attestation work begins.

### 2. Scope Is Attestation-Only

Result: PASS

The gate opens isolation attestation adapter work only and keeps the isolation
runner, CLI, combined verdict, public claims, and release blocked.

### 3. Attestation Checked Is Not Isolation Proven

Result: PASS

The central non-confusion rule is explicit:

```text
attestation checked != isolation proven
```

The authorization forbids outputs, reason codes, reports, and tests from
claiming:

```text
isolation occurred
isolation happened
isolation confirmed
isolation proven
```

### 4. PT-ISOLATION-01 Always Carried

Result: PASS

The plan requires `PT-ISOLATION-01` on every isolation sub-verdict, including
`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`.

This preserves the trust ledger boundary: isolation execution truth is
delegated to the attestation authority and is not proven by SPIRA.

### 5. Declared Authority Only

Result: PASS

The adapter may verify an attestation only against a declared
`ATTESTATION_AUTHORITY` root. No default attestation authority, TOFU, any-valid
attestation, or fallback authority is authorized.

### 6. Sub-Verdict Mapping

Result: PASS

The mapping is fail-closed and consistent with prior adapter gates:

```text
valid attestation under declared authority -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
missing declared attestation root -> TRUST_NOT_EVALUATED
bad attestation signature -> TRUST_INSUFFICIENT
known but undeclared authority -> TRUST_INSUFFICIENT
claim mismatch -> TRUST_INSUFFICIENT
revocation unknown/stale/unreachable -> TRUST_NOT_EVALUATED
clock missing/untrusted -> TRUST_NOT_EVALUATED
```

### 7. No Runner Or Observation

Result: PASS

The authorization blocks:

```text
isolation runner
runtime observation
filesystem observation
network observation
process observation
execution/severance output
permission to sever
```

### 8. Crypto Boundary

Result: PASS

The adapter may reuse the existing pinned and hash-locked `cryptography==49.0.0`
adapter dependency. It does not authorize a new dependency or any hand-rolled
crypto.

`pyproject.toml` remains blocked:

```text
dependencies = []
```

### 9. Conformance Bar

Result: PASS

The plan requires mutation pairs for root absence, malformed root, missing or
malformed attestation, unsupported attestation type, invalid signature, known
undeclared authority, root mismatch, candidate/environment/profile claim
mismatch, expiry, revocation, and clock failures.

The plan also requires metrics for:

```text
outputs_without_pt_isolation_01
outputs_with_execution_semantics
outputs_with_isolation_truth_semantics
```

### 10. Composition Wiring

Result: PASS

The isolation adapter must feed the accepted composition oracle with all prior
sub-verdicts sufficient:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
authority_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
isolation_sub = adapter output
```

The harness must verify that a sufficient composite assessment still carries
`PT-ISOLATION-01`.

### 11. Boundary Preservation

Result: PASS

The plan keeps `pyproject.toml` unchanged, expects no new dependency, and
requires public wheel exclusion.

It also preserves the lakefile/manifest lesson: touching `lakefile.toml` or V1
reproduction artifacts requires V1 SHA256SUMS self-check, V1 package tests, and
full pytest in the same gate.

## Required Next Gate

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_IMPLEMENTATION_REQUIRED
```

## Status

```text
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_AUTHORIZATION_ACCEPTED
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
ISOLATION_ATTESTATION_ADAPTER_ONLY_ACCEPTED
SIGNATURE_ADAPTER_BASELINE_COLD_VERIFIED_ACCEPTED
IDENTITY_ADAPTER_BASELINE_COLD_VERIFIED_ACCEPTED
AUTHORITY_ADAPTER_BASELINE_COLD_VERIFIED_ACCEPTED
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN_ACCEPTED
PT_ISOLATION_01_ALWAYS_CARRIED_ACCEPTED
DECLARED_ATTESTATION_AUTHORITY_ONLY_ACCEPTED
NO_DEFAULT_ATTESTATION_AUTHORITY_ACCEPTED
KNOWN_UNDECLARED_AUTHORITY_INSUFFICIENT_ACCEPTED
CLAIMS_MISMATCH_INSUFFICIENT_ACCEPTED
REVOCATION_UNKNOWN_NOT_EVALUATED_ACCEPTED
CLOCK_FAILURE_NOT_EVALUATED_ACCEPTED
FORBIDDEN_ISOLATION_TRUTH_LANGUAGE_SCAN_REQUIRED
PUBLIC_WHEEL_EXCLUSION_REQUIRED_ACCEPTED

ISOLATION_RUNNER_NOT_AUTHORIZED
RUNTIME_OBSERVATION_NOT_AUTHORIZED
FILESYSTEM_OBSERVATION_NOT_AUTHORIZED
NETWORK_OBSERVATION_NOT_AUTHORIZED
PROCESS_OBSERVATION_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
