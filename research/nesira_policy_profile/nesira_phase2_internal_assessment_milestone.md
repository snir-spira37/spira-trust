# Nesira Phase 2 Internal Assessment Milestone

## Status

```text
DOCUMENT_TYPE: MILESTONE_RECORD
PHASE: PHASE_2
SCOPE: INTERNAL_ASSESSMENT_ENGINE_ONLY

VERDICT:
NESIRA_PHASE2_INTERNAL_ASSESSMENT_ENGINE_COMPLETE_INTERNAL_ONLY

RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This milestone records the accepted internal Nesira Phase 2 assessment engine.
It does not authorize product integration, public exposure, operational action,
or release.

## Accepted Baselines

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED
SPIRA_NESIRA_PHASE1_COLD_EXTERNAL_REPRODUCTION_ACCEPTED
FORMAL_CORE_V1_ACCEPTED
DOMAIN4_NESIRA_LEAN_CORE_ACCEPTED
NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_ASSESSMENT_WIRING_COLD_VERIFICATION_ACCEPTED
```

## What Exists

Nesira Phase 2 now has an internal assessment engine:

```text
signature adapter
identity adapter
authority adapter
isolation attestation adapter
Lean-verified composition core
assessment wiring
```

The engine can evaluate declared evidence against declared trust roots, compose
four sub-assessments through the accepted fail-closed assessment table, and emit
one internal assessment artifact.

The assessment artifact carries:

```text
verdict
per_domain_breakdown
trust_roots_used
assumptions
checked_facts
gaps
not_evaluated_items
blocking_items
evidence_references
reason_codes
execution_marker
```

The required execution marker is:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## Proven Or Verified Properties

The composition core is Lean-verified:

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

The Python-to-world side is empirically verified:

```text
four adapters cold-verified
adapter mutation corpora accepted
assessment wiring cold-verified
81 oracle rows checked with 0 disagreements
cross_subject_mismatch -> not sufficient
public wheel exclusion preserved
pyproject dependencies remain empty
V1 external reproduction manifest remains coherent
```

## Boundaries

This milestone means:

```text
SPIRA/Nesira can internally assess declared trust evidence across signature,
identity, authority, and attestation roots, compose the result through a
verified fail-closed core, and emit an assumption-carrying assessment artifact.
```

It does not mean:

```text
permission to sever
operational severance
runner execution
runtime observation
product combined verdict
CLI availability
public wheel exposure
public capability claim
release readiness
```

## Trust Boundary

The trust roots remain declared assumptions. The engine checks evidence against
declared roots; it does not prove that the roots are legitimate in an absolute
sense.

The assessment remains conditional on the carried assumptions, including:

```text
PT-CRYPTO-*
PT-KEYLEGIT-*
PT-IDENTITY-*
PT-AUTHORITY-*
PT-REVOKE-*
PT-CLOCK-*
PT-ISOLATION-*
PT-META-*
```

Most importantly:

```text
attestation checked != isolation proven
```

`PT-ISOLATION-01` remains carried by the accepted path.

## Human-Gated Territory

The following require separate authorization before any work begins:

```text
runner research or implementation
combined verdict integration
CLI exposure
public wheel exposure
public capability claim
release
```

Any attempt to open one of these areas from this milestone without a separate
authorization must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Milestone Decision

```text
NESIRA_PHASE2_INTERNAL_ASSESSMENT_ENGINE_COMPLETE_INTERNAL_ONLY
```

This is a stable internal milestone. It is intentionally not a public product
claim.
