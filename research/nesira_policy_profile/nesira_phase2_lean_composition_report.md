# Nesira Phase 2 Lean Composition Report

## Status

```text
NESIRA_PHASE2_LEAN_COMPOSITION_IMPLEMENTED
ACCEPTED_PENDING_COLD_VERIFICATION
```

This report records the implementation of the Phase 2 Lean composition core
authorized by:

```text
research/nesira_policy_profile/nesira_phase2_lean_composition_authorization.md
```

The implementation is limited to the composition core:

```text
four sub-assessment verdicts -> composite Phase 2 assessment
```

It does not implement sub-assessment logic, cryptographic verification,
identity-chain verification, authority-policy lookup, revocation lookup,
attestation parsing, isolation execution checks, Python adapters, CLI exposure,
public wheel exposure, combined verdict integration, public claims, or release.

## Files Added Or Modified

```text
formal/spira_formal_core_v1/lakefile.toml
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Assessment.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Assumptions.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Composition.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Proofs.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Main.lean
research/nesira_policy_profile/nesira_phase2_lean_composition_results.json
research/nesira_policy_profile/nesira_phase2_lean_composition_report.md
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
```

## Target Boundary

Phase 2 is implemented as a separate Lean library target:

```text
SpiraFormalCorePhase2
```

The existing targets remain separate:

```text
SpiraFormalCore
SpiraFormalCoreDomain4
```

Boundary verification:

```text
lake build SpiraFormalCore: PASS, 35 jobs
Phase2 oleans after clean V1 build: 0

lake build SpiraFormalCoreDomain4: PASS, 8 jobs
Phase2 oleans after clean Domain4 build: 0

lake build SpiraFormalCorePhase2: PASS, 7 jobs
full lake build: PASS, 48 jobs
```

This preserves the Option A boundary: Phase 2 does not enter the V1 external
reproduction target or the Domain4 target.

## Lean Core

The Lean core defines:

```text
Phase2Assessment
SubVerdicts
AssumptionId
AssumptionSet
AssessmentContract
compose
```

The verdict type has only:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

It has no constructor for:

```text
execute
sever
permission_to_sever
authorized_to_sever
safe_to_sever
```

## Assumption-Carrying Model

`AssumptionSet` is represented as a dependency-free Bool structure, one field
per assumption ID. It avoids Mathlib and `Finset` while keeping membership and
floor checks decidable in Lean core.

The implemented carrying rules are:

```text
floor always carried
conditional assumptions carried only for evaluated sub-domains
PT-ISOLATION-01 carried whenever isolation is evaluated
SUFFICIENT carries the full four-domain union
```

## Proved Theorems

```text
composition_strict_and
insufficient_dominates_not_evaluated
otherwise_not_evaluated
composition_total
composition_deterministic
floor_always_carried
sufficient_carries_full_union
isolation_caveat_inherited
sufficient_is_not_assumption_free
execution_marker_constant
```

## Axiom Inventory

```text
composition_strict_and: no axioms
insufficient_dominates_not_evaluated: propext
otherwise_not_evaluated: propext
composition_total: no axioms
composition_deterministic: no axioms
floor_always_carried: propext
sufficient_carries_full_union: propext
isolation_caveat_inherited: propext
sufficient_is_not_assumption_free: propext
execution_marker_constant: no axioms
```

No theorem depends on `sorryAx`.

## Oracle Agreement

The Lean dump was compared against:

```text
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
```

Result:

```text
lean_rows: 81
oracle_rows: 81
missing_rows: 0
agreement_errors: 0
```

The comparison checked:

```text
inputs
composite_verdict
per_domain_breakdown
trust_roots_used_sources
sub_assumption_sources_included
execution_marker
carried_assumptions floor
PT-ISOLATION-01 inheritance
```

## Quality Gates

```text
forbidden strings: 0
non-ASCII in Phase2 Lean: 0
git diff --check: PASS
lake build SpiraFormalCorePhase2: PASS
lake build SpiraFormalCore: PASS
lake build SpiraFormalCoreDomain4: PASS
full lake build: PASS
```

## Still Not Authorized

```text
sub-assessment logic
signature verification code
identity-chain verification code
authority-policy lookup code
revocation lookup code
clock-source implementation
attestation parsing or verification
isolation runner implementation
Python composition implementation
Python adapters
CLI exposure
public wheel exposure
combined verdict integration
public capability claim
release
```

## Required Next Gate

```text
NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_REQUIRED
```

The next review must reproduce this from a clean clone before any adapter or
Python work is authorized.
