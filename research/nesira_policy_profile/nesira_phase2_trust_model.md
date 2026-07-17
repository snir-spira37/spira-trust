# Nesira Phase 2 Trust Model

## Status

```text
DOCUMENT_TYPE: RESEARCH_SPECIFICATION
PHASE: PHASE_2
SCOPE: TRUST_ROOTS_MODEL_ONLY
IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document refines the trust-root model proposed in:

```text
research/nesira_policy_profile/nesira_phase2_proposal.md
```

It is a research artifact only. It does not authorize code, schemas, product
integration, release, or public claims.

## Core Rule

```text
NO_DEFAULT_TRUST
```

No signature key, signer identity issuer, authority policy, attestation source,
clock, revocation source, or execution observer is trusted unless a declared
trust root explicitly says so.

If a required trust root is missing, ambiguous, expired, revoked, stale,
wrong-scope, or unverifiable, the assessment must fail closed:

```text
TRUST_INSUFFICIENT
```

or:

```text
TRUST_NOT_EVALUATED
```

It must never default to:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

## Trust Root Definition

A trust root is a bounded assumption record:

```text
TrustRoot:
  trust_root_id
  trust_root_kind
  version
  issuer_or_designator
  subject_scope
  environment_scope
  action_scope
  purpose_scope
  valid_from
  valid_until
  revocation_source
  revocation_freshness_policy
  clock_source
  evidence_binding_requirements
  not_proven_assumptions
```

The trust root is not proven by SPIRA. It is supplied to SPIRA as a declared
assumption and must travel with the assessment output.

## Trust Root Kinds

### Signature Key Root

Purpose:

```text
declare that key K is accepted for verifying signatures over a bounded payload
class and trust domain
```

Must declare:

```text
key identity
accepted algorithms
payload class
subject scope
environment scope
validity window
revocation source
revocation freshness policy
```

Does not prove:

```text
key was never compromised
crypto library is correct
revocation source is honest
```

### Identity Issuer Root

Purpose:

```text
declare that issuer I may bind credentials / certificates / keys to signer identities
within a bounded namespace
```

Must declare:

```text
issuer identity
identity namespace
accepted credential type
validity window
revocation source
freshness policy
```

Does not prove:

```text
issuer honesty
identity registry correctness
absence of credential compromise
```

### Authority Policy Root

Purpose:

```text
declare that policy source P is authoritative for deciding whether signer identity S
may assert action A for subject/environment/time T
```

Must declare:

```text
policy source identity
policy version
action scope
subject scope
environment scope
validity window
freshness policy
clock source
```

Does not prove:

```text
policy correctness
policy author legitimacy beyond the declared root
clock correctness
```

### Attestation Authority Root

Purpose:

```text
declare that attestation source R may produce isolation-execution evidence for
a bounded runner/profile/environment domain
```

Must declare:

```text
attestation source identity
runner identity scope
isolation profile scope
environment scope
claim vocabulary
accepted signature keys or credential roots
freshness policy
clock source
```

Does not prove:

```text
isolation actually occurred
runner honesty
operating-system correctness
container-runtime correctness
attestation-source honesty
```

Hard boundary:

```text
attestation checked against R != isolation proven
```

### External Severance Policy Root

Purpose:

```text
declare which external policy authority may consume the Nesira assessment and
decide whether operational severance is permitted
```

Must declare:

```text
external policy authority
permitted assessment consumers
subject scope
environment scope
validity window
freshness policy
```

Does not prove:

```text
external policy legitimacy
external execution correctness
permission to sever in the physical world
```

Nesira still emits an assessment, not an execution instruction.

## Revocation And Freshness

Revocation is fail-closed.

```text
revocation status revoked      -> TRUST_INSUFFICIENT
revocation status expired      -> TRUST_INSUFFICIENT
revocation status unknown      -> TRUST_NOT_EVALUATED
revocation source unreachable  -> TRUST_NOT_EVALUATED
revocation data stale          -> TRUST_NOT_EVALUATED
revocation data wrong-scope    -> TRUST_INSUFFICIENT
```

A trust root may only support sufficiency when its revocation status is known,
fresh, and within scope.

There is no default assumption that a key, credential, issuer, policy, or
attestation source remains valid when revocation cannot be checked.

## Clock And Time Trust

Time is a trust dependency.

Any use of:

```text
valid_from
valid_until
freshness window
revocation freshness
attestation timestamp
policy timestamp
```

depends on a declared clock source.

If the required clock source is missing or not declared:

```text
TRUST_NOT_EVALUATED
```

If the clock source contradicts the evidence, validity window, or freshness
policy:

```text
TRUST_INSUFFICIENT
```

Clock correctness is not proven by SPIRA and must appear in the trust
assumption ledger.

## Scope Matching

Trust roots are bounded. A root must match all applicable scope fields:

```text
subject
candidate
environment
action
payload class
isolation profile
time window
policy version
```

Out-of-scope roots cannot support sufficiency.

```text
root missing        -> TRUST_NOT_EVALUATED
root ambiguous      -> TRUST_NOT_EVALUATED
root wrong-scope    -> TRUST_INSUFFICIENT
root version stale  -> TRUST_INSUFFICIENT or TRUST_NOT_EVALUATED
```

The trust model must not use a broad root to fill a narrow missing root unless
that delegation is explicit, versioned, and in-scope.

## Evidence Binding

Every trust check must bind evidence to the assessment context:

```text
candidate identity
environment identity
subject identity
policy/version identity
payload digest
trust_root_id@version
time / freshness context
```

Missing binding prevents sufficiency.

The binding check is structural and deterministic. The legitimacy of the trust
root remains an assumption.

## Assessment Output Requirements

Every Phase 2 assessment must carry:

```text
verdict
conditional_on_roots
not_proven_assumptions
checked_facts
gaps
freshness_status
revocation_status
execution_marker
```

Required marker:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

If the verdict is `TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`, the output must still
carry:

```text
conditional_on_roots
not_proven_assumptions
```

The output must not contain:

```text
execute
sever
safe_to_sever
authorized_to_sever
```

## Failure Matrix

```text
missing required root             -> TRUST_NOT_EVALUATED
ambiguous required root           -> TRUST_NOT_EVALUATED
wrong-scope root                  -> TRUST_INSUFFICIENT
expired root                      -> TRUST_INSUFFICIENT
revoked root                      -> TRUST_INSUFFICIENT
unknown revocation status         -> TRUST_NOT_EVALUATED
stale revocation evidence         -> TRUST_NOT_EVALUATED
missing clock source              -> TRUST_NOT_EVALUATED
clock contradiction               -> TRUST_INSUFFICIENT
signature check failure           -> TRUST_INSUFFICIENT
signature check not run           -> TRUST_NOT_EVALUATED
identity binding failure          -> TRUST_INSUFFICIENT
identity binding not evaluated    -> TRUST_NOT_EVALUATED
authority lookup denial           -> TRUST_INSUFFICIENT
authority lookup not evaluated    -> TRUST_NOT_EVALUATED
attestation check failure         -> TRUST_INSUFFICIENT
attestation check not evaluated   -> TRUST_NOT_EVALUATED
```

No failure row may map to `TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`.

## Not Proven By This Trust Model

```text
crypto implementation correctness
key custody
absence of key compromise
issuer honesty
authority policy correctness
attestation source honesty
actual isolation execution
operating system correctness
container runtime correctness
clock correctness
revocation source honesty
external severance policy legitimacy
external severance execution correctness
```

These must be carried forward into:

```text
nesira_phase2_not_proven_trust_ledger.md
nesira_phase2_not_proven_trust_ledger.json
```

## Explicitly Not Authorized

```text
implementation
schema changes
signature-verification code
signer-identity code
signer-authority code
attestation verifier implementation
isolation runner implementation
permission-to-sever implementation
CLI exposure
public wheel exposure
combined verdict integration
public capability claim
release
```

## Status

```text
NESIRA_PHASE2_TRUST_MODEL_SPECIFIED
NO_DEFAULT_TRUST
TRUST_ROOTS_EXPLICIT_BOUNDED_VERSIONED
REVOCATION_UNKNOWN_FAILS_CLOSED
CLOCK_IS_TRUST_ASSUMPTION
ATTESTATION_CHECKED_NOT_ISOLATION_PROVEN
ASSESSMENT_NOT_EXECUTION
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
```

