# Nesira Phase 2 Identity Adapter Authorization Review

## Verdict

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_AUTHORIZATION_ACCEPTED
```

This review accepts the identity adapter authorization and implementation plan
as the next narrow Phase 2 adapter gate.

It does not authorize authority, isolation-attestation, isolation runner, CLI,
combined verdict wiring, public wheel exposure, public claims, or release.

## Review Summary

The authorization correctly separates:

```text
identity binding
```

from:

```text
signer authority
permission to sever
execution
```

The adapter may only bind a signing key/root to a signer identity under a
declared identity root and explicit assumptions.

## Checks

### 1. Signature Baseline

Result: PASS

The authorization requires:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
```

before identity work begins.

### 2. Scope Is Identity-Only

Result: PASS

The gate opens identity adapter work only and keeps authority,
isolation-attestation, runner, CLI, combined verdict, public claims, and release
blocked.

### 3. Identity Is Not Authority

Result: PASS

The authorization forbids `PT-AUTHORITY-*` assumptions and authority semantics
in identity adapter outputs.

### 4. Sub-Verdict Mapping

Result: PASS

The plan preserves the accepted distinction:

```text
checked and failed -> TRUST_INSUFFICIENT
could not be checked -> TRUST_NOT_EVALUATED
```

The critical guard is explicit:

```text
missing identity root -> TRUST_NOT_EVALUATED
wrong identity root   -> TRUST_INSUFFICIENT
```

### 5. Chain And Issuer Failures

Result: PASS

Broken chains, invalid credential signatures, untrusted issuers, binding
mismatches, namespace mismatches, and context mismatches map to
`TRUST_INSUFFICIENT`.

Malformed or unsupported credentials that cannot be evaluated map to
`TRUST_NOT_EVALUATED`.

### 6. Revocation And Clock

Result: PASS

Unknown, stale, unreachable, missing, or inconclusive revocation cannot support
sufficiency and maps to `TRUST_NOT_EVALUATED`.

Missing or untrusted clock state also maps to `TRUST_NOT_EVALUATED`.

### 7. No Default Trust

Result: PASS

The authorization blocks:

```text
default CA store
browser trust store
trust on first use
any valid certificate
any valid credential
implicit identity issuer
implicit namespace
```

### 8. Assumption Carrying

Result: PASS

The plan requires `PT-IDENTITY-01` and `PT-IDENTITY-02` on sufficient identity
outputs, `PT-META-03` when a chain is used, and `PT-REVOKE-03` for unknown
revocation.

Authority assumptions are explicitly forbidden in this gate.

### 9. Conformance Bar

Result: PASS

The plan requires mutation pairs for root absence, wrong root, malformed root,
unsupported credential, malformed credential, bad signature, broken chain,
untrusted issuer, expiry, revocation, clock, namespace, identity, key-binding,
and context mismatches.

### 10. Composition Wiring

Result: PASS

The identity adapter must feed the accepted composition oracle with:

```text
signature_sub = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
authority_sub = TRUST_NOT_EVALUATED
isolation_sub = TRUST_NOT_EVALUATED
```

This checks wiring without claiming full Phase 2 sufficiency.

### 11. Boundary Preservation

Result: PASS

The plan keeps `pyproject.toml` unchanged, reuses the existing hash-pinned
adapter requirements, and requires public wheel exclusion.

It also explicitly preserves the lesson from the lakefile/manifest issue:
touching `lakefile.toml` requires V1 SHA256SUMS self-check, V1 package tests,
and full pytest in the same gate.

## Required Next Gate

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_IMPLEMENTATION_REQUIRED
```

## Status

```text
NESIRA_PHASE2_IDENTITY_ADAPTER_AUTHORIZATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_IMPLEMENTATION_PLAN_ACCEPTED
IDENTITY_ADAPTER_ONLY_ACCEPTED
SIGNATURE_ADAPTER_BASELINE_COLD_VERIFIED_ACCEPTED
IDENTITY_IS_NOT_AUTHORITY_ACCEPTED
MISSING_IDENTITY_ROOT_NOT_EVALUATED_ACCEPTED
WRONG_IDENTITY_ROOT_INSUFFICIENT_ACCEPTED
CHAIN_BROKEN_INSUFFICIENT_ACCEPTED
UNTRUSTED_ISSUER_INSUFFICIENT_ACCEPTED
BINDING_MISMATCH_INSUFFICIENT_ACCEPTED
MALFORMED_CREDENTIAL_NOT_EVALUATED_ACCEPTED
REVOCATION_UNKNOWN_NOT_EVALUATED_ACCEPTED
CLOCK_FAILURE_NOT_EVALUATED_ACCEPTED
NO_DEFAULT_CA_STORE_ACCEPTED
NO_BROWSER_TRUST_STORE_ACCEPTED
NO_TOFU_ACCEPTED
NO_ANY_VALID_CERTIFICATE_ACCEPTED
PT_IDENTITY_ASSUMPTIONS_REQUIRED_ACCEPTED
PT_AUTHORITY_ASSUMPTIONS_NOT_AUTHORIZED
PUBLIC_WHEEL_EXCLUSION_REQUIRED_ACCEPTED
AUTHORITY_ADAPTER_NOT_AUTHORIZED
ISOLATION_ATTESTATION_ADAPTER_NOT_AUTHORIZED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
