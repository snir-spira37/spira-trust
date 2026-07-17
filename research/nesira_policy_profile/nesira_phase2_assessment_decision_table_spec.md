# Nesira Phase 2 Assessment Decision Table Spec

## Status

```text
DOCUMENT_TYPE: RESEARCH_ASSESSMENT_DECISION_TABLE_SPEC
PHASE: PHASE_2
SCOPE: COMPOSITE_ASSESSMENT_DECISION_TABLE_ONLY
ROW_COUNT: 81
IMPLEMENTATION: NOT_AUTHORIZED
LEAN_IMPLEMENTATION: NOT_AUTHORIZED
PYTHON_IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document specifies the full 81-row composition table for Nesira Phase 2 assessment outputs. It is a paper research artifact only. It does not authorize sub-assessment logic, implementation, Lean proofs, CLI exposure, public wheel exposure, combined verdict integration, public claims, or release.

## Source Rule

The table is mechanical from the accepted assessment sketch:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS iff all four sub-verdicts are sufficient.
Else TRUST_INSUFFICIENT if one or more sub-verdicts is insufficient.
Else TRUST_NOT_EVALUATED.
```

In mixed rows, `TRUST_INSUFFICIENT` dominates `TRUST_NOT_EVALUATED`. This is a fail-closed precedence rule: an active trust failure is reported as insufficient even when another domain is not evaluated.

## Input Space

The table covers:

```text
signature_sub x identity_sub x authority_sub x isolation_sub
```

Each sub-verdict has exactly three values:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
TRUST_NOT_EVALUATED
```

Therefore:

```text
3^4 = 81
```

All 81 combinations are enumerated below and in the machine-readable companion JSON.

## Assumption-Carrying Rule

Every row carries the unconditional assumption floor:

```text
PT-CRYPTO-01
PT-CLOCK-01
PT-META-01
PT-META-02
PT-META-04
```

Conditional sub-assumptions are carried only from domains whose sub-verdict is:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
TRUST_INSUFFICIENT
```

A domain whose sub-verdict is `TRUST_NOT_EVALUATED` does not contribute conditional assumptions, because the assessment did not rely on that domain root. It still appears in `per_domain_breakdown`.

Whenever `isolation_sub` is evaluated, the row must explicitly carry:

```text
PT-ISOLATION-01
```

The all-sufficient row therefore carries the floor plus signature, identity, authority, and isolation sub-assumptions, including `PT-ISOLATION-01`.

## Output Fields Per Row

Each row defines:

```text
composite_verdict
per_domain_breakdown
assumption_floor_ids
sub_assumption_sources_included
required_explicit_assumption_ids
trust_roots_used_sources
execution_marker
```

The execution marker is always:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

No row authorizes execution, severance, or release.

## Full 81-Row Table

| Row | Signature | Identity | Authority | Isolation | Composite Verdict | Included Sub-Assumption Sources | Required Explicit IDs |
| --- | --- | --- | --- | --- | --- | --- | --- |
| NESIRA-P2-ASSESS-001 | SUFFICIENT | SUFFICIENT | SUFFICIENT | SUFFICIENT | SUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-002 | SUFFICIENT | SUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-003 | SUFFICIENT | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-004 | SUFFICIENT | SUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-005 | SUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-006 | SUFFICIENT | SUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-007 | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-008 | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-009 | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | signature_sub.assumptions, identity_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-010 | SUFFICIENT | INSUFFICIENT | SUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-011 | SUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-012 | SUFFICIENT | INSUFFICIENT | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-013 | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-014 | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-015 | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-016 | SUFFICIENT | INSUFFICIENT | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-017 | SUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-018 | SUFFICIENT | INSUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-019 | SUFFICIENT | NOT_EVALUATED | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-020 | SUFFICIENT | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-021 | SUFFICIENT | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | signature_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-022 | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-023 | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-024 | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-025 | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | signature_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-026 | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-027 | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | signature_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-028 | INSUFFICIENT | SUFFICIENT | SUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-029 | INSUFFICIENT | SUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-030 | INSUFFICIENT | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-031 | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-032 | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-033 | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-034 | INSUFFICIENT | SUFFICIENT | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-035 | INSUFFICIENT | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-036 | INSUFFICIENT | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-037 | INSUFFICIENT | INSUFFICIENT | SUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-038 | INSUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-039 | INSUFFICIENT | INSUFFICIENT | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-040 | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-041 | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-042 | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-043 | INSUFFICIENT | INSUFFICIENT | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-044 | INSUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-045 | INSUFFICIENT | INSUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, identity_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-046 | INSUFFICIENT | NOT_EVALUATED | SUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-047 | INSUFFICIENT | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-048 | INSUFFICIENT | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-049 | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-050 | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-051 | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-052 | INSUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | signature_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-053 | INSUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | signature_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-054 | INSUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | signature_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-055 | NOT_EVALUATED | SUFFICIENT | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-056 | NOT_EVALUATED | SUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-057 | NOT_EVALUATED | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-058 | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-059 | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-060 | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-061 | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-062 | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-063 | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | identity_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-064 | NOT_EVALUATED | INSUFFICIENT | SUFFICIENT | SUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-065 | NOT_EVALUATED | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-066 | NOT_EVALUATED | INSUFFICIENT | SUFFICIENT | NOT_EVALUATED | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-067 | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-068 | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-069 | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | identity_sub.assumptions, authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-070 | NOT_EVALUATED | INSUFFICIENT | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-071 | NOT_EVALUATED | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | identity_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-072 | NOT_EVALUATED | INSUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | identity_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-073 | NOT_EVALUATED | NOT_EVALUATED | SUFFICIENT | SUFFICIENT | NOT_EVALUATED | authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-074 | NOT_EVALUATED | NOT_EVALUATED | SUFFICIENT | INSUFFICIENT | INSUFFICIENT | authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-075 | NOT_EVALUATED | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | NOT_EVALUATED | authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-076 | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | SUFFICIENT | INSUFFICIENT | authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-077 | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | INSUFFICIENT | authority_sub.assumptions, isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-078 | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | NOT_EVALUATED | INSUFFICIENT | authority_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |
| NESIRA-P2-ASSESS-079 | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | SUFFICIENT | NOT_EVALUATED | isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-080 | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | INSUFFICIENT | INSUFFICIENT | isolation_sub.assumptions | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04, PT-ISOLATION-01 |
| NESIRA-P2-ASSESS-081 | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | NOT_EVALUATED | floor only | PT-CRYPTO-01, PT-CLOCK-01, PT-META-01, PT-META-02, PT-META-04 |

## Machine-Readable Oracle

The companion oracle is:

```text
research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json
```

Future Lean composition-core dumps and Python composition-core outputs must compare against this oracle before any implementation claim is accepted.

## Self-Check Summary

```text
row_count: 81
unique_row_ids: 81
sufficient_rows: 1
insufficient_rows: 65
not_evaluated_rows: 15
rows_missing_floor: 0
rows_missing_execution_marker: 0
rows_using_scoring_or_majority: 0
rows_authorizing_execution: 0
isolation_evaluated_rows_missing_pt_isolation_01: 0
```

## Explicitly Not Authorized

```text
sub-assessment logic
signature verification code
identity-chain verification code
authority-policy lookup code
revocation lookup code
attestation parsing or verification
isolation runner implementation
Lean composition core
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
nesira_phase2_lean_composition_core_authorization.md
```

It must authorize, separately and narrowly, a Lean composition core that proves totality, determinism, no execution constructor, and exact agreement with the 81-row oracle.

## Status

```text
NESIRA_PHASE2_ASSESSMENT_DECISION_TABLE_SPECIFIED
TOTAL_81_ROWS_SPECIFIED
STRICT_AND_FAITHFULNESS_SPECIFIED
INSUFFICIENT_DOMINATES_NOT_EVALUATED_SPECIFIED
ASSUMPTION_FLOOR_IN_ALL_ROWS_SPECIFIED
PT_ISOLATION_01_CARRIED_WHEN_ISOLATION_EVALUATED
JSON_ORACLE_SPECIFIED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
```
