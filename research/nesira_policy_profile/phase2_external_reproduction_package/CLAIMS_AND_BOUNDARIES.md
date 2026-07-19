# Claims and Boundaries

## EMPIRICALLY_REPRODUCED

A reviewer may reproduce that Nesira Phase 2 internally assesses declared trust
evidence across signature, identity, authority, and attestation roots; composes
the result through a verified fail-closed core; and emits an
assumption-carrying assessment artifact.

## FORMALLY_REPRODUCED

The Lean Phase 2 composition core may be checked for:

```text
strict AND composition
totality over 81 sub-verdict combinations
determinism
insufficient dominates not-evaluated
floor assumptions always carried
sufficient assessment is not assumption-free
PT-ISOLATION-01 inherited on sufficient assessment
no execution constructor
```

## EMPIRICALLY_CHECKED_ADAPTERS

```text
signature adapter
identity adapter
authority adapter
isolation attestation adapter
assessment wiring
```

The adapters are empirical code that checks declared evidence against declared
trust roots. They are not formally proved.

## TRUST_BOUNDARY

Trust roots are declared assumptions. SPIRA checks evidence against those
declared roots; it does not prove that the roots are legitimate in an absolute
sense.

Attestation verification is not an isolation-truth proof. The mandatory
`PT-ISOLATION-01` caveat must remain carried.

The assessment artifact is not severance authorization. The required execution
marker is:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## NOT_AUTHORIZED

```text
package delivery
runner
combined verdict
CLI
public wheel exposure
public capability claim
release
```
