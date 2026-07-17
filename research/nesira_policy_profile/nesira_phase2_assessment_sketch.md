# Nesira Phase 2 Assessment Sketch

## Status

```text
DOCUMENT_TYPE: RESEARCH_ASSESSMENT_COMPOSITION_SKETCH
PHASE: PHASE_2
SCOPE: COMPOSITE_ASSESSMENT_ONLY
IMPLEMENTATION: NOT_AUTHORIZED
DECISION_TABLE_SPEC: NOT_AUTHORIZED
LEAN_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This sketch defines how already-computed Phase 2 trust sub-assessments compose
into one severance trust assessment.

It does not define how any sub-assessment is produced. Cryptographic
verification, identity binding, authority lookup, revocation checking,
attestation parsing, and filesystem or runner interaction remain future
adapter work and are not authorized here.

## Composition Boundary

The composition core consumes four sub-verdicts:

```text
signature_sub
identity_sub
authority_sub
isolation_sub
```

Each sub-verdict is a `Phase2Assessment` over its own declared trust root and
must carry:

```text
verdict
trust_roots_used
assumptions
gaps
checked_facts
```

The composition core treats these sub-verdicts as inputs. It does not inspect
raw signatures, certificates, policies, attestation payloads, files, clocks, or
revocation sources.

## Sub-Assessment Domains

```text
signature_sub:
  domain: SIGNING_KEY
  verdict: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS | TRUST_INSUFFICIENT | TRUST_NOT_EVALUATED

identity_sub:
  domain: IDENTITY_BINDING_CA
  verdict: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS | TRUST_INSUFFICIENT | TRUST_NOT_EVALUATED

authority_sub:
  domain: AUTHORITY_POLICY_SOURCE
  verdict: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS | TRUST_INSUFFICIENT | TRUST_NOT_EVALUATED

isolation_sub:
  domain: ATTESTATION_AUTHORITY
  verdict: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS | TRUST_INSUFFICIENT | TRUST_NOT_EVALUATED
  mandatory_assumption: PT-ISOLATION-01
```

`PT-ISOLATION-01` must be present whenever `isolation_sub` is evaluated,
including when `isolation_sub` is sufficient under declared roots.

## Strict AND Composition

The composite verdict is fail-closed and uses strict AND composition:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  iff signature_sub  == TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  and identity_sub   == TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  and authority_sub  == TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  and isolation_sub  == TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS

TRUST_INSUFFICIENT
  if one or more sub-verdicts is TRUST_INSUFFICIENT

TRUST_NOT_EVALUATED
  otherwise
```

Therefore:

```text
any INSUFFICIENT      -> composite INSUFFICIENT
no INSUFFICIENT
and any NOT_EVALUATED -> composite NOT_EVALUATED
all SUFFICIENT        -> composite SUFFICIENT_UNDER_DECLARED_ROOTS
```

Every output must include `per_domain_breakdown`, so a consumer can see which
domain failed or was not evaluated.

## No Scoring Or Majority Rule

Trust does not average.

The composition core must not use:

```text
scoring
weighting
confidence averaging
majority vote
3-of-4 acceptance
isolation weakness offset by signature strength
```

There is no route from partial sufficiency to composite sufficiency.

## Totality And Determinism

The composition function is total over:

```text
3^4 = 81
```

possible sub-verdict combinations.

For every combination, exactly one composite verdict is produced. The output is
deterministic and must not depend on timestamps, environment, dictionary order,
or model output.

This sketch does not enumerate the 81-row decision table. That table is a
future research artifact.

## Composite Output Contract

A future composite assessment must include:

```text
verdict
trust_roots_used
assumptions
per_domain_breakdown
checked_facts
gaps
execution_marker
```

The required execution marker is:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

The composite `assumptions` array is:

```text
assumption_floor
union(signature_sub.assumptions)
union(identity_sub.assumptions)
union(authority_sub.assumptions)
union(isolation_sub.assumptions)
```

The assumption floor is defined by:

```text
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
```

At the time of this sketch, the floor is:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

The composite `trust_roots_used` array is the union of all trust roots used by
the four sub-assessments. It must be versioned:

```text
trust_root_id@version
```

## Meaning Of Composite Sufficiency

Composite sufficiency means only:

```text
The checkable evidence is sufficient against the declared trust roots,
under the non-empty assumption set carried by the assessment.
```

It does not mean:

```text
unconditional trust
permission to sever
sever now
signer authority proven absolutely
actual isolation execution proven
attestation authority honesty proven
external policy legitimacy proven
```

The composite output may be consumed by an authorized external policy layer in
the future, but this sketch does not authorize that policy layer and does not
define an execution path.

## Missing Or Invalid Roots

The trust model remains fail-closed:

```text
missing required root             -> corresponding sub-verdict TRUST_NOT_EVALUATED
ambiguous required root           -> corresponding sub-verdict TRUST_NOT_EVALUATED
revocation unknown or stale        -> corresponding sub-verdict TRUST_NOT_EVALUATED
wrong-scope root                  -> corresponding sub-verdict TRUST_INSUFFICIENT
expired root                      -> corresponding sub-verdict TRUST_INSUFFICIENT
revoked root                      -> corresponding sub-verdict TRUST_INSUFFICIENT
clock missing or not declared      -> corresponding sub-verdict TRUST_NOT_EVALUATED
clock contradiction               -> corresponding sub-verdict TRUST_INSUFFICIENT
```

By strict AND composition, any such sub-verdict prevents composite sufficiency.

## Isolation Caveat Inheritance

The isolation caveat rises to the composite output.

Even when:

```text
isolation_sub == TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

the composite assessment must carry:

```text
PT-ISOLATION-01
```

and must not be read as:

```text
isolation occurred
isolation proven
```

## Not In This Sketch

```text
sub-assessment implementation
signature verification code
identity-chain verification code
authority-policy lookup code
revocation lookup code
clock-source implementation
attestation parsing or verification
isolation runner implementation
full 81-row decision-table specification
Lean implementation
Python implementation
CLI exposure
public wheel exposure
combined verdict integration
public capability claim
release
```

## Required Next Gate

The next research gate should be:

```text
nesira_phase2_assessment_decision_table_spec.md
```

It must enumerate the 81 sub-verdict combinations and prove, on paper, that:

```text
all 81 combinations are covered
only all-sufficient maps to composite sufficient
any insufficient maps to composite insufficient
otherwise not evaluated
assumptions always include the ledger floor
PT-ISOLATION-01 is carried whenever isolation is evaluated
execution_marker is always assessment-only
```

## Status Summary

```text
NESIRA_PHASE2_ASSESSMENT_COMPOSITION_SKETCHED
STRICT_AND_COMPOSITION_SPECIFIED
NO_SCORING_NO_MAJORITY_RULE
TOTAL_81_COMBINATIONS_DECLARED
ASSUMPTION_UNION_AND_FLOOR_SPECIFIED
PT_ISOLATION_01_INHERITS_TO_COMPOSITE
ASSESSMENT_NOT_EXECUTION_PRESERVED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
```
