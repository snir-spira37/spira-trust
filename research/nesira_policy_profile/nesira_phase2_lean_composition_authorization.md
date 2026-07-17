# Nesira Phase 2 Lean Composition Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
AUTHORIZES: LEAN_COMPOSITION_CORE_ONLY
IMPLEMENTATION_SCOPE: COMPOSITE_ASSESSMENT_CORE
SUB_ASSESSMENT_LOGIC: NOT_AUTHORIZED
PYTHON_IMPLEMENTATION: NOT_AUTHORIZED
ADAPTERS: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes a narrow Lean implementation of the Phase 2 assessment
composition core only.

It does not authorize signature verification, identity-chain verification,
authority-policy lookup, revocation lookup, attestation parsing, isolation
execution checks, Python adapters, CLI exposure, public wheel exposure,
combined verdict integration, public claims, or release.

## Authoritative Inputs

The Lean composition core must translate the accepted paper artifacts exactly:

```text
research/nesira_policy_profile/nesira_phase2_proposal.md
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_sketch.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table_spec.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
```

The 81-row JSON decision table is the frozen oracle for this gate:

```text
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
```

Any divergence between the Lean core and the oracle is:

```text
SCOPE_REVISION_REQUIRED
```

and must not be corrected silently.

## Authorized Files

The implementation may add only a separate Phase 2 Lean target and its report
artifacts.

Authorized Lean files:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Assessment.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Assumptions.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Composition.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Proofs.lean
formal/spira_formal_core_v1/SpiraFormalCore/Phase2/Main.lean
```

Authorized Lake change:

```text
formal/spira_formal_core_v1/lakefile.toml
```

The Lake change is limited to adding a separate target:

```text
SpiraFormalCorePhase2
```

with explicit Phase 2 globs such as:

```text
SpiraFormalCore.Phase2.+
```

The existing targets must not be expanded:

```text
SpiraFormalCore
SpiraFormalCoreDomain4
```

Authorized report artifacts:

```text
research/nesira_policy_profile/nesira_phase2_lean_composition_report.md
research/nesira_policy_profile/nesira_phase2_lean_composition_results.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
```

## Mandatory Target Boundary

Phase 2 must be a separate Lean library target.

It must not be imported by:

```text
formal/spira_formal_core_v1/SpiraFormalCore.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/All.lean
```

unless a later review explicitly authorizes that integration.

The V1 external reproduction target must remain V1-scoped:

```text
lake build SpiraFormalCore
```

must not build Phase 2 modules.

Domain4 must remain separate:

```text
lake build SpiraFormalCoreDomain4
```

must not depend on Phase 2 modules.

This target separation is a hard acceptance gate. If Phase 2 enters a V1 or
Domain4 build path, the implementation fails this authorization.

## Frozen Surfaces

The following artifacts are frozen for this gate and must not be edited:

```text
Formal Core V1 source and proofs
Domain4/Nesira Lean source and proofs
Nesira Phase 1 validator implementation
Nesira Phase 1 accepted artifacts
Nesira Phase 2 proposal
Nesira Phase 2 trust model
Nesira Phase 2 trust ledger
Nesira Phase 2 assessment sketch
Nesira Phase 2 assessment decision table spec
Nesira Phase 2 assessment decision table JSON oracle
Lean toolchain version
```

If any frozen surface must change, this authorization is insufficient and a new
scope review is required.

## Required Lean Output Contract

The Lean composition core must model only an assessment output:

```text
verdict
carried_assumptions
per_domain_breakdown
trust_roots_used_sources
execution_marker
```

The verdict type must have no constructor that represents:

```text
execute
sever
permission_to_sever
authorized_to_sever
safe_to_sever
```

The execution marker must be represented as:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## Required Theorems

The implementation must prove the following theorem families:

```text
composition_strict_and:
  composite = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  iff all four sub-verdicts are TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

insufficient_dominates_not_evaluated:
  if at least one sub-verdict is TRUST_INSUFFICIENT,
  composite = TRUST_INSUFFICIENT

otherwise_not_evaluated:
  if no sub-verdict is TRUST_INSUFFICIENT
  and not all sub-verdicts are TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS,
  composite = TRUST_NOT_EVALUATED

composition_total:
  every one of the 81 input combinations has exactly one output

composition_deterministic:
  equal inputs produce equal outputs
```

The Phase 2-specific assumption-carrying theorems are mandatory:

```text
floor_always_carried:
  for every input combination,
  the unconditional floor is included in carried_assumptions

sufficient_carries_full_union:
  if composite = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS,
  carried_assumptions includes the floor and all four evaluated
  sub-assumption sources

isolation_caveat_inherited:
  if isolation_sub is evaluated,
  PT-ISOLATION-01 is included in carried_assumptions

sufficient_is_not_assumption_free:
  if composite = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS,
  carried_assumptions is non-empty and includes the floor
```

The no-execution boundary must be enforced at the type level:

```text
no_execution_constructor:
  the Phase 2 assessment verdict type cannot express execution or severance
```

## Oracle Agreement Gate

`Main.lean` must emit or define a canonical 81-row dump containing at least:

```text
row_id
signature_sub
identity_sub
authority_sub
isolation_sub
composite_verdict
carried_assumptions
per_domain_breakdown
execution_marker
```

Acceptance requires:

```text
diff(Lean 81-row dump, nesira_phase2_assessment_decision_table.json) == 0
```

The comparison must cover all fields, not only verdicts.

## Proof Quality Bar

The proof quality bar matches the accepted Domain4 standard:

```text
lake build SpiraFormalCorePhase2: exit 0
sorry: 0
admit: 0
sorryAx: 0
custom axiom: 0
native_decide: 0
unsafe: 0
opaque: 0
```

`#print axioms` for every Phase 2 theorem must show only accepted Lean kernel
dependencies:

```text
propext
Classical.choice
Quot.sound
```

`sorryAx` is forbidden.

## No-Regression Gates

The implementation must preserve:

```text
lake build SpiraFormalCore: passes, no Phase 2 modules
lake build SpiraFormalCoreDomain4: passes, no Phase 2 dependency
lake build SpiraFormalCorePhase2: passes
full lake build: passes
```

The V1 external reproduction boundary remains mandatory:

```text
V1 verify builds V1 only
Phase 2 oleans in V1 verification: 0
```

Domain4 cold-verification status must remain unchanged.

## Explicitly Not Authorized

```text
signature verification implementation
identity-chain verification implementation
authority-policy lookup implementation
revocation lookup implementation
clock-source implementation
attestation parsing or verification
isolation runner implementation
Python composition implementation
Python adapters
fixtures for sub-assessment adapters
CLI exposure
public wheel exposure
combined verdict integration
public capability claim
release
```

## Stop Conditions

The implementation must stop with `SCOPE_REVISION_REQUIRED` if:

```text
the 81-row oracle cannot be translated exactly
a theorem requires sorry/admit/custom axioms
the Lean dump differs from the JSON oracle
Phase 2 enters the V1 target
Phase 2 enters the Domain4 target
an execution/severance constructor becomes necessary
the assumption-carrying theorems cannot be proved
```

## Required Verification Report

The report must include:

```text
commit hash
files changed
lake build SpiraFormalCore result
lake build SpiraFormalCoreDomain4 result
lake build SpiraFormalCorePhase2 result
full lake build result
81-row dump comparison result
theorem list
axiom inventory
forbidden-string scan
V1 target boundary result
Domain4 target boundary result
not-authorized surface check
```

## Required Next Gate

After implementation and review, the next gate must be:

```text
NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_REQUIRED
```

Only after cold verification may a separate authorization consider Python
composition or sub-assessment adapter work.

## Status

```text
NESIRA_PHASE2_LEAN_COMPOSITION_AUTHORIZED
LEAN_COMPOSITION_CORE_ONLY
PHASE2_SEPARATE_LEAN_TARGET_REQUIRED
V1_AND_DOMAIN4_TARGET_BOUNDARY_REQUIRED
NO_EXECUTION_CONSTRUCTOR_REQUIRED
ASSUMPTION_CARRYING_THEOREMS_REQUIRED
JSON_ORACLE_AGREEMENT_REQUIRED
SUB_ASSESSMENT_LOGIC_NOT_AUTHORIZED
PYTHON_NOT_AUTHORIZED
CLI_NOT_AUTHORIZED
PUBLIC_WHEEL_NOT_AUTHORIZED
COMBINED_VERDICT_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
