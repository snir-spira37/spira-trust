# Nesira Phase 2 Lean Composition Review

## Verdict

```text
NESIRA_PHASE2_LEAN_COMPOSITION_ACCEPTED_PENDING_COLD_VERIFICATION
```

This review accepts the local implementation of the Phase 2 Lean composition
core and requires cold verification before any subsequent implementation gate.

It does not authorize sub-assessment logic, Python adapters, CLI exposure,
public wheel exposure, combined verdict integration, public claims, or release.

## Review Summary

The implementation correctly adds a separate Lean target:

```text
SpiraFormalCorePhase2
```

and keeps Phase 2 out of:

```text
SpiraFormalCore
SpiraFormalCoreDomain4
```

The core composes four already-computed sub-assessment verdicts into a composite
assessment. It does not inspect signatures, certificates, policy sources,
revocation sources, attestation payloads, files, clocks, or runner state.

## Checks

### 1. Separate Target Boundary

Result: PASS

```text
lake build SpiraFormalCore: PASS, 35 jobs
Phase2 oleans after clean V1 build: 0

lake build SpiraFormalCoreDomain4: PASS, 8 jobs
Phase2 oleans after clean Domain4 build: 0
```

Phase 2 does not contaminate V1 or Domain4 reproduction paths.

### 2. Phase2 Build

Result: PASS

```text
lake build SpiraFormalCorePhase2: PASS, 7 jobs
```

### 3. Full Build

Result: PASS

```text
lake build: PASS, 48 jobs
```

### 4. No Execution Constructor

Result: PASS

`Phase2Assessment` contains only:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

There is no Lean constructor for execution, severance, permission to sever,
authorization to sever, or safe-to-sever.

### 5. Strict AND Composition

Result: PASS

The theorem family includes:

```text
composition_strict_and
insufficient_dominates_not_evaluated
otherwise_not_evaluated
```

### 6. Assumption-Carrying Theorems

Result: PASS

The theorem family includes:

```text
floor_always_carried
sufficient_carries_full_union
isolation_caveat_inherited
sufficient_is_not_assumption_free
```

These make `SUFFICIENT` conditionality mechanical rather than merely
documentary.

### 7. Oracle Agreement

Result: PASS

```text
lean_rows: 81
oracle_rows: 81
missing_rows: 0
agreement_errors: 0
```

The Lean dump agrees with the frozen 81-row oracle on verdicts, breakdown,
source carrying, execution marker, assumption floor, and isolation caveat
inheritance.

### 8. Proof Hygiene

Result: PASS

```text
sorry: 0
admit: 0
sorryAx: 0
custom axiom keyword: 0
native_decide: 0
unsafe: 0
opaque: 0
```

`#print axioms` shows only `propext` for the nontrivial theorem families and no
axioms for the definitional theorems.

### 9. Dependency Hygiene

Result: PASS

The assumption set uses a Bool-field structure. It does not introduce Mathlib,
`Finset`, or external dependencies.

### 10. Scope Boundary

Result: PASS

No sub-assessment logic, cryptographic verification, attestation verifier,
isolation runner, Python adapter, CLI, wheel exposure, combined verdict, public
claim, or release path was implemented.

## Residual Risk

Cold verification is still required. The local implementation and local gates
passed, but the next milestone must reproduce the same result from a fresh
clone.

The adapter side remains outside this gate:

```text
raw world -> sub-assessment verdicts
```

Only the composition core is accepted locally:

```text
sub-assessment verdicts -> composite assessment
```

## Required Next Gate

```text
NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_REQUIRED
```

## Status

```text
NESIRA_PHASE2_LEAN_COMPOSITION_ACCEPTED_PENDING_COLD_VERIFICATION
SEPARATE_PHASE2_TARGET_ACCEPTED
V1_BOUNDARY_PRESERVED
DOMAIN4_BOUNDARY_PRESERVED
NO_EXECUTION_CONSTRUCTOR_ACCEPTED
ASSUMPTION_CARRYING_THEOREMS_ACCEPTED
JSON_ORACLE_AGREEMENT_ACCEPTED
PROOF_HYGIENE_ACCEPTED
SUB_ASSESSMENT_LOGIC_NOT_AUTHORIZED
PYTHON_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
PUBLIC_WHEEL_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
