# Nesira Phase 2 Research Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
OPENS: PHASE_2_RESEARCH_AND_PLANNING_ONLY
CODE: NOT_AUTHORIZED
TRUST_CLAIM: NOT_MADE
```

This document authorizes research and planning only. It does not authorize
implementation, product integration, release, or any public capability claim.

## Why Phase 2 Is Different

Phase 1 and Domain4 proved or reproduced structural and decision behavior:

```text
structure
binding
evidence integrity
safe evidence paths
decision-table behavior over typed outcomes
```

Phase 2 is different. It concerns trust in external facts:

```text
who signed
whether the signer is the claimed identity
whether that identity is authorized
whether isolation execution actually occurred
whether severance is permitted
```

These facts are not self-contained and are not proved in Lean. Phase 2 may only
describe what is checked against declared trust roots and what remains assumed.

Required framing:

```text
Phase 2 does not turn trust into PROVEN.

Phase 2 may only turn trust-dependent claims into:

CHECKED_AGAINST_DECLARED_TRUST_ROOTS

where the trust roots themselves are explicit assumptions, not proofs.
```

Any statement that collapses `verified` into `trusted`, `authorized`, or
`safe-to-sever` is an overclaim and blocks review.

## Authorized Research Scope

Research is authorized for exactly five areas:

```text
signature verification
signer identity
signer authority
isolation execution evidence
permission-to-sever decision
```

For each area, the research must separate:

```text
checkable fact
declared trust-root dependency
remaining NOT_PROVEN assumption
failure behavior
```

No implementation is authorized by this document.

## Frozen Inputs

The following are accepted and frozen for this research gate:

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED
SPIRA_NESIRA_PHASE1_COLD_EXTERNAL_REPRODUCTION_ACCEPTED
DOMAIN4_NESIRA_COLD_EXTERNAL_REPRODUCTION_ACCEPTED
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
Domain4 V2 flag schema
Domain4 V2 decision table
Domain4 Python/Lean harness
Option A V1/Domain4 reproduction boundary
```

The research must not edit or reinterpret these artifacts.

## Checkable Versus Trust-Root Breakdown

### Signature Verification

```text
checkable:
  cryptographic verification of a signature over a bounded payload using key K

trust-root dependency:
  whether K is legitimate for the claimed trust domain
  who designated K as trusted
  whether K is current and not revoked

NOT_PROVEN:
  crypto library correctness
  key management correctness
  trust-root legitimacy
  revocation freshness
```

### Signer Identity

```text
checkable:
  binding from credential / certificate / key identity material to a claimed signer identity

trust-root dependency:
  who issues or accepts the identity binding
  whether the identity registry / issuer is authoritative for the policy

NOT_PROVEN:
  issuer honesty
  identity registry correctness
  absence of credential compromise
```

### Signer Authority

```text
checkable:
  policy lookup showing whether the signer identity is authorized for the requested action,
  subject, environment, and time window

trust-root dependency:
  who defines the authority policy
  whether the policy source is authoritative
  whether policy freshness is acceptable

NOT_PROVEN:
  authority-policy correctness
  policy distribution integrity beyond declared roots
  clock / freshness trust
```

### Isolation Execution Evidence

```text
checkable:
  attestation evidence from a declared runner / observer source
  binding of that attestation to the candidate, environment, and isolation profile

trust-root dependency:
  honesty and correctness of the attestation source
  runner identity and runner authority
  clock and freshness assumptions

NOT_PROVEN:
  that isolation actually happened in the physical world
  runner honesty
  attestation-source honesty
  operating-system / container-runtime correctness
```

Important boundary:

```text
Phase 2 must not claim "isolation execution proven."

The strongest allowed form is:

isolation execution evidence checked against declared attestation authority.
```

### Permission-To-Sever Decision

```text
checkable:
  deterministic composition over trust-dependent flags and policy context

trust-root dependency:
  correctness of the declared trust roots feeding those flags
  authority of the policy that permits severance

required behavior:
  fail closed
  missing trust evidence -> no PROCEED
  unverifiable trust evidence -> no PROCEED
  ambiguous trust root -> no PROCEED
```

No automatic `PROCEED` path is authorized by this research gate.

## Required Research Artifacts

The authorized research outputs are:

```text
research/nesira_policy_profile/nesira_phase2_proposal.md
research/nesira_policy_profile/nesira_phase2_trust_model.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.md
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
research/nesira_policy_profile/nesira_phase2_permission_to_sever_decision_sketch.md
research/nesira_policy_profile/nesira_phase2_research_review.md
```

Each artifact must preserve the checkable-versus-trust-root distinction.

## Mandatory Research Discipline

The research must carry forward the Domain4 discipline:

```text
prove the decision, delegate the world
fail closed when trust evidence is missing or unverifiable
declare TRUST_ROOTS explicitly
declare NOT_PROVEN assumptions explicitly
never collapse verified -> authorized / trusted / safe-to-sever
```

The Phase 2 `NOT_PROVEN` / trust-assumption ledger must include at least:

```text
crypto library correctness
key management correctness
trust-root legitimacy
signer identity issuer correctness
signer authority policy correctness
attestation-source honesty
runner identity and authority
clock / time trust
revocation freshness
policy freshness
filesystem / OS / runtime trust for evidence collection
```

## Explicitly Not Authorized

```text
Phase 2 implementation
signature-verification code
signer-identity code
signer-authority code
isolation runner implementation
attestation verifier implementation
permission-to-sever implementation
CLI exposure
public wheel exposure
combined verdict integration
Phase 1 changes
Domain4 Lean changes
Domain4 Python harness changes
schema changes to accepted Phase 1 artifacts
public capability claim
release
```

## Stop Conditions

The research must stop with `SCOPE_REVISION_REQUIRED` if:

```text
a trust root cannot be declared explicitly
a trust assumption is required but cannot be written plainly
isolation execution cannot be separated from attestation checking
verified is used as a synonym for authorized / trusted / safe-to-sever
permission-to-sever has any automatic PROCEED path
any required research output would require implementation to be meaningful
any frozen Phase 1 / Domain4 artifact needs to change
```

## Review Checklist

The review must attack the authorization and any research outputs for:

```text
1. all five areas separated into checkable facts and trust-root dependencies
2. all trust roots declared as assumptions, not proofs
3. permission-to-sever remains fail-closed
4. the trust ledger covers crypto, keys, authority, attestation, clocks, and revocation
5. no wording collapses verified into authorized / trusted / safe-to-sever
6. implementation, CLI, wheel, combined verdict, release, and claims remain blocked
7. no frozen Phase 1 / Domain4 artifact was edited
```

## Status After This Authorization

```text
PHASE_2_RESEARCH_AND_PLANNING_AUTHORIZED
PHASE_2_IMPLEMENTATION_NOT_AUTHORIZED
SIGNATURE_VERIFICATION_CODE_NOT_AUTHORIZED
SIGNER_AUTHORITY_CODE_NOT_AUTHORIZED
ISOLATION_EXECUTION_CODE_NOT_AUTHORIZED
PERMISSION_TO_SEVER_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

