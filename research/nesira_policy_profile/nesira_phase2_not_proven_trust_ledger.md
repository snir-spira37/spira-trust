# Nesira Phase 2 NOT_PROVEN Trust Ledger

## Status

```text
DOCUMENT_TYPE: RESEARCH_TRUST_ASSUMPTIONS_LEDGER
PHASE: PHASE_2
LEDGER_ID: SPIRA_NESIRA_PHASE2_NOT_PROVEN_TRUST_LEDGER_V1
IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This ledger gives every Phase 2 trust assumption a stable ID. The purpose is to
make conditionality mechanical: every Phase 2 assessment must carry assumption
IDs, including the strongest possible result.

## Core Rule

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS is never assumption-free.
```

Every assessment must carry:

```text
assumptions: [PT-..., ...]
```

The unconditional assumption floor is always present:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

Conditional assumptions are added when the corresponding trust domain or trust
root is used.

## ID Categories

```text
PT-CRYPTO-*     cryptographic primitive / implementation / key-management assumptions
PT-KEYLEGIT-*   legitimacy and custody of declared signing keys
PT-IDENTITY-*   legitimacy of identity issuers and identity bindings
PT-AUTHORITY-*  legitimacy and freshness of authority-policy sources
PT-REVOKE-*     revocation-source honesty and revocation freshness
PT-CLOCK-*      clock and time-source trust
PT-ISOLATION-*  isolation truth delegated to attestation roots
PT-META-*       meta-boundaries: roots declared not validated, sufficient is conditional
```

## Entry Schema

Each entry has:

```text
id
version
statement
applies_to
universality: UNCONDITIONAL | CONDITIONAL
mandatory_when
forbidden_reading
cross_ref
```

`forbidden_reading` is required. It states what a consumer must not infer from
the assumption.

## Ledger Entries

### PT-CRYPTO

```text
PT-CRYPTO-01:
  statement: cryptographic verification depends on correctness of the crypto library and implementation.
  universality: UNCONDITIONAL
  applies_to: all Phase 2 assessments
  forbidden_reading: crypto checks prove the trust root is legitimate.

PT-CRYPTO-02:
  statement: accepted cryptographic primitives and algorithms are assumed sound for the declared purpose.
  universality: CONDITIONAL
  mandatory_when: signature verification or attestation signature verification is used
  forbidden_reading: algorithm acceptance proves key legitimacy or signer authority.

PT-CRYPTO-03:
  statement: key management and private-key custody are assumed outside SPIRA.
  universality: CONDITIONAL
  mandatory_when: any signing key or attestation key root is used
  forbidden_reading: signature verification proves the private key was not compromised.
```

### PT-KEYLEGIT

```text
PT-KEYLEGIT-01:
  statement: legitimacy of a declared signing key is assumed from the declared trust root.
  universality: CONDITIONAL
  mandatory_when: signature-key root is used
  forbidden_reading: SPIRA independently proves the key is legitimate.

PT-KEYLEGIT-02:
  statement: the declared signing key is assumed to be in-scope for the bounded purpose and payload class.
  universality: CONDITIONAL
  mandatory_when: signature-key root is used
  forbidden_reading: a key accepted for one scope is universal.
```

### PT-IDENTITY

```text
PT-IDENTITY-01:
  statement: legitimacy of the identity issuer / registry is assumed from the declared identity root.
  universality: CONDITIONAL
  mandatory_when: signer identity root is used
  forbidden_reading: SPIRA proves the issuer is honest.

PT-IDENTITY-02:
  statement: credential-to-identity binding correctness depends on the declared issuer and identity namespace.
  universality: CONDITIONAL
  mandatory_when: signer identity root is used
  forbidden_reading: identity binding proves signer authority.
```

### PT-AUTHORITY

```text
PT-AUTHORITY-01:
  statement: legitimacy of the authority-policy source is assumed from the declared authority root.
  universality: CONDITIONAL
  mandatory_when: signer authority root is used
  forbidden_reading: SPIRA proves the policy source is legitimate.

PT-AUTHORITY-02:
  statement: correctness of the authority policy itself is assumed, not proven.
  universality: CONDITIONAL
  mandatory_when: signer authority root is used
  forbidden_reading: policy lookup proves the policy is correct.

PT-AUTHORITY-03:
  statement: policy freshness is assumed according to the declared freshness policy and clock source.
  universality: CONDITIONAL
  mandatory_when: authority policy freshness is evaluated
  forbidden_reading: a fresh policy is necessarily correct.
```

### PT-REVOKE

```text
PT-REVOKE-01:
  statement: honesty and correctness of the revocation source are assumed from the declared root.
  universality: CONDITIONAL
  mandatory_when: revocation status is used for any key, issuer, policy, or attestation source
  forbidden_reading: revocation check proves the source is honest.

PT-REVOKE-02:
  statement: revocation freshness depends on the declared freshness policy and clock source.
  universality: CONDITIONAL
  mandatory_when: revocation freshness is evaluated
  forbidden_reading: stale or unreachable revocation data may be treated as valid.

PT-REVOKE-03:
  statement: unknown revocation status is not evidence of non-revocation.
  universality: CONDITIONAL
  mandatory_when: revocation source is missing, unreachable, stale, or inconclusive
  forbidden_reading: unknown revocation status can support sufficiency.
```

### PT-CLOCK

```text
PT-CLOCK-01:
  statement: all freshness, validity-window, revocation, and attestation-time checks depend on declared clock trust.
  universality: UNCONDITIONAL
  applies_to: all Phase 2 assessments
  forbidden_reading: SPIRA proves clock correctness.

PT-CLOCK-02:
  statement: clock-source identity and freshness are assumed according to the declared trust root.
  universality: CONDITIONAL
  mandatory_when: a specific clock root is used
  forbidden_reading: timestamp comparison proves real-world time correctness.
```

### PT-ISOLATION

```text
PT-ISOLATION-01:
  statement: isolation execution truth is delegated to the declared attestation authority; SPIRA does not verify isolation occurred.
  universality: CONDITIONAL
  mandatory_when: isolation attestation is evaluated
  forbidden_reading: isolation occurred / isolation is proven.

PT-ISOLATION-02:
  statement: honesty of the runner or observer producing the attestation is assumed.
  universality: CONDITIONAL
  mandatory_when: isolation attestation source is used
  forbidden_reading: a signed attestation proves the runner was honest.

PT-ISOLATION-03:
  statement: operating system, container runtime, and isolation substrate behavior are assumed outside SPIRA.
  universality: CONDITIONAL
  mandatory_when: isolation attestation is used
  forbidden_reading: SPIRA proves OS, runtime, or container isolation correctness.
```

### PT-META

```text
PT-META-01:
  statement: trust roots are declared inputs, not validated or proven by SPIRA.
  universality: UNCONDITIONAL
  applies_to: all Phase 2 assessments
  forbidden_reading: declared root means legitimate root.

PT-META-02:
  statement: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS is conditional on declared roots and this ledger.
  universality: UNCONDITIONAL
  applies_to: all Phase 2 assessments
  forbidden_reading: sufficient means unconditional authorization or permission to sever.

PT-META-03:
  statement: a validated chain of trust still exposes every trusted link as an assumption ID.
  universality: CONDITIONAL
  mandatory_when: certificate chain, delegation chain, revocation chain, or policy delegation chain is used
  forbidden_reading: chain validated means assumptions disappeared.

PT-META-04:
  statement: Phase 2 assessment is not execution and not severance authorization.
  universality: UNCONDITIONAL
  applies_to: all Phase 2 assessments
  forbidden_reading: assessment output authorizes or executes severance.
```

## Assumption Floor

The assumption floor is mandatory for every Phase 2 assessment:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

Therefore, even:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
```

must carry a non-empty `assumptions` array.

## Chain Rule

Trust chains do not erase assumptions.

If an assessment uses:

```text
certificate chain
delegated identity chain
delegated authority policy chain
revocation chain
attestation delegation chain
```

then every trusted link must contribute either:

```text
its own trust_root_id@version
or
a ledger assumption ID explaining why the link is trusted
```

The phrase:

```text
chain validated
```

must never be used to hide the assumptions behind the chain.

## Assessment Carrier Rule

Every future `Phase2AssessmentContract` must include:

```text
assumptions: [PT-..., ...]
conditional_on_roots: [trust_root_id@version, ...]
```

Missing `assumptions` is invalid.

An empty `assumptions` array is invalid.

## Stability Rule

Ledger IDs are stable.

```text
IDs are never deleted silently.
Removing an assumption requires a new ledger version and a review explaining
why the trust scope is being expanded.
```

Changing `forbidden_reading`, `universality`, or `mandatory_when` also requires
a new ledger version.

## Machine-Readable Companion

The companion JSON file is:

```text
research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json
```

Future assessment logic and harnesses must reference assumption IDs from the
JSON companion rather than copying prose.

## Explicitly Not Authorized

```text
assessment decision table
implementation
schema changes
signature verification code
attestation verification code
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
NESIRA_PHASE2_NOT_PROVEN_TRUST_LEDGER_SPECIFIED
ASSUMPTION_FLOOR_SPECIFIED
SUFFICIENT_IS_NEVER_ASSUMPTION_FREE
PT_ISOLATION_01_MANDATORY_FOR_ISOLATION
CHAIN_ASSUMPTIONS_MUST_REMAIN_VISIBLE
MACHINE_READABLE_LEDGER_COMPANION_SPECIFIED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
```
