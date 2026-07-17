# Nesira Phase 2 Proposal

## Status

```text
DOCUMENT_TYPE: RESEARCH_PROPOSAL
PHASE: PHASE_2
OUTPUT: TRUST_AND_AUTHORIZATION_ASSESSMENT_ONLY
IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This proposal is authorized by:

```text
research/nesira_policy_profile/nesira_phase2_research_authorization.md
```

It does not authorize code, schemas, CLI exposure, public wheel exposure,
combined verdict integration, release, or public claims.

## Core Principle

Nesira Phase 2 produces an assessment, not execution.

It may answer:

```text
Are the provided trust-dependent facts sufficient under declared trust roots?
Which trust roots is the answer conditional on?
Which assumptions remain not proven?
Which gaps block sufficiency?
```

It must not answer:

```text
Execute severance.
Severance is unconditionally authorized.
Isolation execution is proven.
Trust roots are proven legitimate by SPIRA.
```

The action itself remains outside SPIRA/Nesira and belongs to a separately
authorized external policy / execution system.

## Output Type Discipline

The output type must make severance execution unrepresentable:

```text
Phase2Assessment =
  TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  TRUST_INSUFFICIENT
  TRUST_NOT_EVALUATED
```

There must be no constructor or field with these meanings:

```text
SEVER
EXECUTE
AUTHORIZED_TO_SEVER
SAFE_TO_SEVER
```

`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS` is conditional. It is not an
unconditional authorization and not an execution instruction.

## Five Trust Domains

Phase 2 research covers exactly five trust domains.

### 1. Signature Verification

```text
checkable:
  cryptographic verification of a signature over a bounded payload using key K

trust-root:
  legitimacy of K for the declared trust domain
  designation authority for K
  freshness and revocation status of K

not proven:
  crypto library correctness
  key-management correctness
  trust-root legitimacy
  revocation-source correctness and freshness
```

### 2. Signer Identity

```text
checkable:
  binding from credential / certificate / key material to claimed signer identity

trust-root:
  identity issuer / registry authority
  accepted identity namespace
  issuer freshness / validity

not proven:
  issuer honesty
  identity registry correctness
  absence of credential compromise
```

### 3. Signer Authority

```text
checkable:
  policy lookup showing whether the signer identity may make the requested
  assertion for the subject, environment, action, and time window

trust-root:
  source of the authority policy
  policy issuer authority
  policy version and freshness

not proven:
  correctness of the authority policy
  correctness of policy distribution
  clock and freshness trust
```

### 4. Isolation Attestation

```text
checkable:
  attestation is well-formed
  attestation is signed by a declared attestation authority
  attestation binds expected isolation claims to the candidate / environment

trust-root:
  honesty of the attestation authority
  runner identity and authority
  runner / observer freshness and clock assumptions

not proven:
  that isolation actually occurred in the physical world
  runner honesty
  attestation-source honesty
  operating system / container runtime correctness
```

Hard boundary:

```text
attestation checked != isolation proven
```

The strongest allowed statement is:

```text
isolation attestation verified against declared authority X
```

plus the explicit assumption:

```text
isolation execution truth is delegated to trust in authority X
```

Nesira must never say:

```text
isolation occurred
```

### 5. Severance Assessment

```text
checkable:
  deterministic composition of the four trust-domain assessments above

trust-root:
  all roots used by the four trust-domain assessments
  external policy authority that consumes the assessment

not proven:
  external policy legitimacy
  external execution correctness
  permission to sever in the physical / operational world
```

The severance assessment is sufficient only if all required trust domains are
sufficient under their declared roots. Any insufficient or not-evaluated domain
must prevent sufficiency.

## Trust Roots Model

A trust root is an explicit, bounded, versioned assumption:

```text
trust_root_id
trust_root_kind
issuer_or_designator
scope
purpose
version
validity_window
revocation_source
freshness_policy
```

Rules:

```text
1. A trust root is input, not something SPIRA proves.
2. SPIRA checks evidence against the root; it does not prove the root.
3. Roots are bounded by purpose and scope, not universal.
4. Expired, revoked, stale, missing, or wrong-scope roots cannot support sufficiency.
5. Every sufficient assessment must list the roots it is conditional on.
```

## Phase2AssessmentContract Sketch

The proposed assessment contract is:

```text
Phase2AssessmentContract:
  verdict: Phase2Assessment
  conditional_on_roots: [trust_root_id@version, ...]
  assumptions: [not_proven_id, ...]
  gaps: [missing_or_insufficient_fact, ...]
  checked_facts: [checkable_fact_id, ...]
  execution_marker: ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

There is no execution field.

The contract must always carry the trust roots and assumptions that make the
assessment meaningful.

## Fail-Closed Composition

Composition is fail-closed:

```text
missing signature verification       -> TRUST_INSUFFICIENT or TRUST_NOT_EVALUATED
missing signer identity              -> TRUST_INSUFFICIENT or TRUST_NOT_EVALUATED
missing signer authority             -> TRUST_INSUFFICIENT or TRUST_NOT_EVALUATED
missing isolation attestation         -> TRUST_INSUFFICIENT or TRUST_NOT_EVALUATED
expired / revoked / stale trust root -> TRUST_INSUFFICIENT
ambiguous trust root                  -> TRUST_NOT_EVALUATED
```

The composite assessment may be:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

only if every required trust domain is sufficient under its declared roots.

The composite assessment must expose which sub-domain failed or remained
not evaluated.

## Double Conditionality

Even a sufficient result is conditional twice:

```text
conditional on declared trust roots
conditional on the NOT_PROVEN / trust-assumption ledger
```

This is the Phase 2 analogue of Phase 1's structural-validity boundary:

```text
VALID in Phase 1 did not mean safe-to-proceed.
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS in Phase 2 does not mean execute severance.
```

## Future Research Artifacts

The next research artifacts, if authorized separately, should be:

```text
nesira_phase2_trust_model.md
nesira_phase2_not_proven_trust_ledger.md
nesira_phase2_not_proven_trust_ledger.json
nesira_phase2_permission_to_sever_decision_sketch.md
```

Those artifacts remain research-only until a separate implementation
authorization exists.

## Future Formalization Direction

A later Phase 2 formal core may mirror Domain4:

```text
typed trust flags -> deterministic assessment contract
```

The formal part would prove the decision/composition table over typed trust
flags. It would not prove:

```text
cryptography implementation correctness
key management
trust-root legitimacy
attestation-source honesty
clock correctness
revocation freshness
real-world isolation execution
external severance execution correctness
```

The discipline remains:

```text
prove the decision, delegate the world
```

## Explicitly Not Authorized

```text
Phase 2 implementation
signature-verification code
signer-identity code
signer-authority code
attestation verifier implementation
isolation runner implementation
permission-to-sever implementation
CLI exposure
public wheel exposure
combined verdict integration
Phase 1 changes
Domain4 Lean changes
Domain4 Python harness changes
accepted schema changes
public capability claim
release
```

## Status

```text
NESIRA_PHASE2_PROPOSAL_SPECIFIED
ASSESSMENT_NOT_EXECUTION
TRUST_ROOTS_ARE_ASSUMPTIONS
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

