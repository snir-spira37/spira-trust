# Nesira Phase 2 Adapters Authorization Review

## Verdict

```text
NESIRA_PHASE2_ADAPTERS_AUTHORIZATION_ACCEPTED
```

This review accepts the adapter authorization as a narrow Phase 2 implementation
gate.

It authorizes sub-assessment adapters and conformance only. It does not
authorize an isolation runner, CLI, combined verdict wiring, public wheel
exposure, public claims, release, or changes to the accepted composition core.

## Review Summary

The authorization correctly preserves the central Phase 2 boundary:

```text
adapters classify evidence into sub-assessment verdicts
the proven composition core composes those verdicts
SPIRA still produces assessment only, not severance execution
```

The document treats cryptographic verification and attestation checking as
world-to-verdict adapter work, not as formally proven logic.

## Checks

### 1. Scope Is Narrow

Result: PASS

The authorization opens exactly:

```text
signature adapter
identity adapter
authority adapter
isolation attestation adapter
adapter conformance
```

It keeps blocked:

```text
isolation runner
CLI
combined verdict
public wheel exposure
public capability claim
release
```

### 2. Composition Core Remains Frozen

Result: PASS

The adapters must feed the accepted composition core and must not modify,
replace, or bypass it.

This preserves the cold-verified Phase 2 Lean composition result.

### 3. Crypto Supply-Chain Boundary

Result: PASS

The authorization forbids hand-rolled cryptography and requires a controlled,
maintained, pinned crypto dependency before implementation acceptance.

It also requires crypto-library correctness to travel as trust assumptions:

```text
PT-CRYPTO-01
PT-CRYPTO-02 when applicable
PT-CRYPTO-03 when applicable
```

This prevents crypto verification from being overclaimed as a proof of trust.

### 4. Revocation Fails Closed

Result: PASS

The authorization explicitly rejects soft-pass behavior for:

```text
revoked
stale revocation
unreachable revocation
unknown revocation
missing revocation root
```

All of these are required to be non-sufficient. Unknown revocation must carry
`PT-REVOKE-03`.

### 5. Clock Is an Assumption

Result: PASS

The authorization treats time as declared trust, not ambient truth.

Missing, untrusted, out-of-scope, or uncheckable time state must produce a
non-sufficient verdict and carry clock assumptions.

### 6. No Default Trust

Result: PASS

The authorization blocks:

```text
default operating-system trust store
default CA store
trust on first use
any valid signature
implicit signing authority
implicit attestation authority
```

Every sufficient sub-assessment must bind to a declared `root_id@version`.

### 7. Adapter Output Discipline

Result: PASS

Adapters may emit only sub-verdicts, declared roots, assumptions, reason codes,
blocking items, not-evaluated items, and evidence references.

They must not emit execution, severance, permission-to-sever,
authorization-to-sever, safe-to-sever, isolation-occurred, or isolation-proven
semantics.

### 8. Isolation Attestation Boundary

Result: PASS

The authorization correctly separates:

```text
attestation checked
```

from:

```text
isolation occurred
isolation proven
```

`PT-ISOLATION-01` is mandatory on isolation-related sub-assessments, and no
isolation runner is authorized.

### 9. Conformance Bar

Result: PASS

The authorization requires mutation pairs for safety-critical failures,
end-to-end adapter-to-composition checks, two-run semantic equality, and wheel
exclusion.

The acceptance metrics are binary and fail closed.

### 10. Wheel Boundary

Result: PASS

The authorization requires implementation-location selection to account for
public wheel exclusion before acceptance.

It blocks adapter modules, fixtures, reports, adapter-only crypto dependencies,
and attestation verifier code from the public wheel.

## Residual Risks

This authorization does not choose a crypto library. That choice must be
recorded and justified in the implementation report before the library is used.

The following remain outside this gate:

```text
crypto-library correctness
trust-root legitimacy
signer authority as an absolute fact
isolation execution truth
```

They must remain carried as assumption IDs and must not be converted into
unconditional claims.

## Required Next Gate

```text
NESIRA_PHASE2_ADAPTERS_IMPLEMENTATION_REQUIRED
```

The implementation gate must prove, by tests and conformance reports, that the
authorization is obeyed.

## Status

```text
NESIRA_PHASE2_ADAPTERS_AUTHORIZATION_ACCEPTED
SUB_ASSESSMENT_ADAPTERS_AND_CONFORMANCE_ONLY_ACCEPTED
CRYPTO_DEPENDENCY_GOVERNANCE_ACCEPTED
NO_HAND_ROLLED_CRYPTO_ACCEPTED
NO_DEFAULT_TRUST_ACCEPTED
REVOCATION_UNKNOWN_NOT_SUFFICIENT_ACCEPTED
CLOCK_TRUST_ASSUMPTION_ACCEPTED
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN_ACCEPTED
PT_ISOLATION_01_MANDATORY_ACCEPTED
WHEEL_EXCLUSION_REQUIRED_ACCEPTED
COMPOSITION_CORE_FROZEN_ACCEPTED
ISOLATION_RUNNER_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
