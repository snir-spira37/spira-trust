# Nesira Phase 2 Authority Adapter Authorization Review

## Verdict

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_AUTHORIZATION_ACCEPTED
```

This review accepts the authority adapter authorization and implementation plan
as the next narrow Phase 2 adapter gate.

It does not authorize isolation-attestation, isolation runner, CLI, combined
verdict wiring, public wheel exposure, public claims, or release.

## Review Summary

The authorization correctly separates:

```text
authority policy lookup
```

from:

```text
signature verification
identity verification
permission to sever
execution
```

The adapter may only evaluate whether an already-established signer identity is
explicitly allowed by a declared `AUTHORITY_POLICY_SOURCE`.

## Checks

### 1. Baselines

Result: PASS

The authorization requires:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

before authority work begins.

### 2. Scope Is Authority-Only

Result: PASS

The gate opens authority adapter work only and keeps isolation-attestation,
runner, CLI, combined verdict, public claims, and release blocked.

### 3. Authority Is Policy, Not Crypto

Result: PASS

The plan treats authority as policy evaluation over an already-established
identity. It does not authorize signature verification, certificate validation,
or a new crypto dependency inside the authority adapter.

### 4. Authority Consumes Identity

Result: PASS

The authority adapter consumes established signer identity as an input. It must
not re-verify identity credentials or carry `PT-IDENTITY-*` as if it produced
the identity verdict.

### 5. Default-Deny

Result: PASS

The critical rule is explicit:

```text
explicit allow -> TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
explicit deny -> TRUST_INSUFFICIENT
identity absent from consultable policy -> TRUST_INSUFFICIENT
action not explicitly allowed -> TRUST_INSUFFICIENT
missing/unreadable policy source -> TRUST_NOT_EVALUATED
```

This prevents the dangerous soft-fail where "not listed in policy" is treated
as merely not evaluated.

### 6. Root And Policy Failure Mapping

Result: PASS

Missing, ambiguous, or malformed policy roots map to `TRUST_NOT_EVALUATED`.
Wrong policy root/version, stale version, context mismatch, explicit deny, and
no matching allow map to `TRUST_INSUFFICIENT`.

### 7. Revocation And Clock

Result: PASS

Unknown, stale, unreachable, missing, or inconclusive revocation cannot support
sufficiency and maps to `TRUST_NOT_EVALUATED`.

Missing or untrusted clock state also maps to `TRUST_NOT_EVALUATED`.

### 8. No Default Authority

Result: PASS

The authorization blocks:

```text
default allow
permit unless denied
implicit admin role
implicit owner role
implicit repository owner authority
implicit cloud account owner authority
fallback policy
any known identity is authorized
any valid identity is authorized
```

### 9. Assumption Carrying

Result: PASS

The plan requires `PT-AUTHORITY-01` and `PT-AUTHORITY-02` on sufficient
authority outputs, plus revocation and clock assumptions as applicable.

Identity and isolation assumptions are not produced by this gate.

### 10. Conformance Bar

Result: PASS

The plan requires mutation pairs for policy-root absence, malformed policy root,
policy-source absence/malformed/unsupported, identity absence, identity
sub-verdict not sufficient, explicit deny, identity absent from policy,
action-not-allowed, context mismatches, policy version/root mismatches, expiry,
revocation, and clock failures.

### 11. Composition Wiring

Result: PASS

The authority adapter must feed the accepted composition oracle with:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
identity_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
isolation_sub = TRUST_NOT_EVALUATED
```

This checks wiring without claiming full Phase 2 sufficiency.

### 12. Boundary Preservation

Result: PASS

The plan keeps `pyproject.toml` unchanged, expects no new dependency, and
requires public wheel exclusion.

It also preserves the lakefile/manifest lesson: touching `lakefile.toml` or V1
reproduction artifacts requires V1 SHA256SUMS self-check, V1 package tests, and
full pytest in the same gate.

## Required Next Gate

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_IMPLEMENTATION_REQUIRED
```

## Status

```text
NESIRA_PHASE2_AUTHORITY_ADAPTER_AUTHORIZATION_ACCEPTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
AUTHORITY_ADAPTER_ONLY_ACCEPTED
SIGNATURE_ADAPTER_BASELINE_COLD_VERIFIED_ACCEPTED
IDENTITY_ADAPTER_BASELINE_COLD_VERIFIED_ACCEPTED
AUTHORITY_IS_POLICY_NOT_CRYPTO_ACCEPTED
AUTHORITY_CONSUMES_ESTABLISHED_IDENTITY_ACCEPTED
DEFAULT_DENY_REQUIRED_ACCEPTED
MISSING_POLICY_ROOT_NOT_EVALUATED_ACCEPTED
IDENTITY_ABSENT_FROM_POLICY_INSUFFICIENT_ACCEPTED
EXPLICIT_DENY_INSUFFICIENT_ACCEPTED
ACTION_NOT_ALLOWED_INSUFFICIENT_ACCEPTED
NO_DEFAULT_ALLOW_ACCEPTED
NO_PERMIT_UNLESS_DENIED_ACCEPTED
NO_IMPLICIT_ADMIN_OR_OWNER_ACCEPTED
REVOCATION_UNKNOWN_NOT_EVALUATED_ACCEPTED
CLOCK_FAILURE_NOT_EVALUATED_ACCEPTED
PT_AUTHORITY_ASSUMPTIONS_REQUIRED_ACCEPTED
PUBLIC_WHEEL_EXCLUSION_REQUIRED_ACCEPTED

ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
