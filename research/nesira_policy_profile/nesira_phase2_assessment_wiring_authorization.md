# Nesira Phase 2 Assessment Wiring Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
AUTHORIZES: ASSESSMENT_WIRING_PLAN_AND_IMPLEMENTATION_GATE
SCOPE: INTERNAL_ASSESSMENT_WIRING_ONLY
SIGNATURE_ADAPTER_BASELINE: COLD_VERIFIED
IDENTITY_ADAPTER_BASELINE: COLD_VERIFIED
AUTHORITY_ADAPTER_BASELINE: COLD_VERIFIED
ISOLATION_ATTESTATION_ADAPTER_BASELINE: COLD_VERIFIED
COMPOSITION_CORE_BASELINE: LEAN_VERIFIED_AND_COLD_VERIFIED
ISOLATION_RUNNER: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes the next narrow Phase 2 gate: wiring the four
cold-verified sub-assessment adapters into the accepted Phase 2 composition
core.

The wiring may produce one internal Phase 2 assessment artifact. It must not
produce an action verdict, operational severance decision, public combined
verdict, CLI result, wheel-exposed API, public claim, or release artifact.

## Preconditions

The following baselines are required and accepted:

```text
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_ACCEPTED
```

Recorded in:

```text
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_signature_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_identity_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_authority_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_authority_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_cold_verification_review.md
research/nesira_policy_profile/nesira_phase2_isolation_attestation_adapter_cold_verification_results.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
research/nesira_policy_profile/nesira_phase2_lean_composition_results.json
```

The four adapters and the composition core are frozen for this gate. Assessment
wiring must not modify them except through a separate remediation
authorization.

## Authoritative Inputs

The assessment wiring must obey:

```text
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_assessment_sketch.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table_spec.md
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
research/nesira_policy_profile/nesira_phase2_lean_composition_review.md
research/nesira_policy_profile/nesira_phase2_adapters_authorization.md
```

Any conflict is:

```text
SCOPE_REVISION_REQUIRED
```

and must not be resolved by silently changing the trust model, ledger,
decision table, composition core, adapters, or V1 artifacts.

## Authorized Wiring Scope

The wiring may:

```text
accept one caller-supplied assessment context
call the accepted signature adapter
call the accepted identity adapter
call the accepted authority adapter
call the accepted isolation attestation adapter
collect four sub-verdict outputs
compose those outputs by the accepted 81-row decision table
return one internal assessment artifact
```

The output may include:

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

## Explicitly Not Authorized

This gate does not authorize:

```text
runner implementation
runtime observation
filesystem observation
network observation
process observation
permission to sever
operational severance
combined verdict integration
product CLI
public wheel exposure
public API surface
public capability claim
release
```

The assessment artifact is internal research output only.

## Wiring Semantics

The wiring must be a faithful composition of already-computed sub-verdicts.
It must not reinterpret or override an adapter result.

Accepted reading:

```text
The four sub-assessment results were evaluated against declared roots and
composed by the accepted Phase 2 assessment table, under carried assumptions.
```

Forbidden readings:

```text
severance permission language
severance authorization language
the assessment is a product combined verdict
the assessment is a release claim
the model may override the assessment
any one adapter may bypass the composition core
```

## Strict Composition Rule

The wiring must use the accepted 81-row table:

```text
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
```

Required behavior:

```text
all four sub-verdicts sufficient -> composite sufficient under declared roots
any sub-verdict insufficient -> composite insufficient
otherwise -> composite not evaluated
```

The implementation may translate this rule directly, or load and compare
against the frozen 81-row oracle. In either case, conformance must prove:

```text
wiring_rows_checked: 81
wiring_oracle_disagreements: 0
```

## Assumption Carrying

The wiring must carry:

```text
the unconditional floor on every assessment
the union of assumptions from all evaluated sub-domains
PT-ISOLATION-01 whenever the isolation attestation sub-verdict is evaluated
```

The sufficient composite row must carry the full four-domain union, including:

```text
PT-ISOLATION-01
```

The wiring must not collapse `TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS` into an
assumption-free statement.

## Caller Context Rule

The caller-supplied assessment context is the source of expected:

```text
candidate
environment
bounded action
identity
authority policy purpose
attestation profile
```

The wiring must pass the same `expected_context` object to all four adapters.
It must not create per-adapter expected contexts, let adapters derive expected
context from their own evidence, or allow the four sub-assessments to bind
against different subjects.

The wiring must not learn the expected context from the evidence being checked.

If the caller context is missing, malformed, or internally inconsistent, the
wiring must fail closed:

```text
affected sub-domain -> TRUST_NOT_EVALUATED
composite -> not sufficient
```

## Malformed Sub-Result Rule

If any adapter returns an unknown verdict, missing execution marker, malformed
root reference, missing assumptions, or an output that carries execution
semantics, the wiring must not upgrade it.

Required behavior:

```text
affected domain -> TRUST_NOT_EVALUATED
reason code -> ASSESSMENT_WIRING_SUB_RESULT_MALFORMED
composite -> not sufficient unless another domain is explicitly insufficient
```

This is a wiring failure, not a permission path.

## Boundary Against Combined Verdict

Assessment wiring is not combined verdict integration.

Combined verdict integration would connect this assessment to a product
decision surface or an action gate. That remains blocked:

```text
COMBINED_VERDICT_NOT_AUTHORIZED
```

Any implementation that exposes the assessment through an existing product
verdict path must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Wheel Boundary

The wiring module, harness, fixtures, reports, and any adapter-only dependency
must remain excluded from the public wheel.

`pyproject.toml` must remain unchanged:

```text
dependencies = []
```

The existing adapter crypto dependency remains gated by:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

No new dependency is authorized by this gate.

## Required Conformance

The wiring conformance corpus must verify:

```text
4 accepted adapters invoked
81 composition rows checked
0 oracle disagreements
0 adapter result overrides
0 missing floor assumptions
0 missing PT-ISOLATION-01 on sufficient composite row
0 outputs with execution or severance semantics
0 product combined-verdict calls
0 public wheel inclusion failures
two-run semantic diff: 0
full pytest: PASS
V1 SHA256SUMS: PASS
cross-subject mismatch fixture: composite not sufficient
```

## Stop Conditions

The implementation must stop if:

```text
adapter result is reinterpreted or overridden
composition differs from the 81-row oracle
assumptions are dropped
PT-ISOLATION-01 is absent from an evaluated isolation path
the output can be read as permission to sever
the wiring touches combined verdict, CLI, public wheel, or release surfaces
pyproject.toml dependencies change
V1 external reproduction manifest becomes stale
```

## Review Checklist

The implementation review must check:

```text
1. Does the wiring consume all four accepted adapters and no unaccepted source?
2. Does it compose by the accepted 81-row table with 0 disagreements?
3. Does it preserve per-domain breakdown exactly?
4. Does it preserve assumptions, including the unconditional floor?
5. Does it preserve PT-ISOLATION-01 in the sufficient composite row?
6. Does malformed adapter output fail closed without upgrade?
7. Does caller context flow into adapters without being learned from evidence?
8. Does one shared expected_context feed all four adapters?
9. Does a cross-subject mismatch fixture produce a not-sufficient composite?
10. Does the output avoid execution, severance, CLI, and combined-verdict semantics?
11. Is the wiring excluded from the public wheel?
12. Are frozen adapters, composition core, V1, Domain4, and Phase 1 unchanged?
```

## Verdict

```text
NESIRA_PHASE2_ASSESSMENT_WIRING_AUTHORIZATION_READY_FOR_REVIEW
```
