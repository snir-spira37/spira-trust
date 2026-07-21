# Nesira Phase 2 Capability Provider Assumption Ledger

## Status

```text
DOCUMENT_TYPE: RESEARCH -- CAPABILITY PROVIDER ASSUMPTIONS LEDGER
PHASE: PHASE_2_CAPABILITY_PROVIDER_ASSUMPTION_LEDGER_GATE
SCOPE: LEDGER_ONLY
LEDGER_ID: SPIRA_NESIRA_PHASE2_CAPABILITY_PROVIDER_ASSUMPTION_LEDGER_V1
LEDGER_VERSION: 1

AUTHORIZES:
capability-provider assumption IDs
machine-readable capability-provider ledger companion
future provider conformance references

PROVIDER_IMPLEMENTATION: NOT_AUTHORIZED_BY_THIS_LEDGER
RUNNER_API_CHANGE: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
CLI_EXPOSURE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
```

This ledger gives stable meaning to the `CAP-*` assumptions carried by any
future audit append provider or runner result.

## Core Rule

```text
APPEND_APPLIED is never assumption-free.
```

The provider may report a status. SPIRA does not prove provider honesty,
append-only behavior, sink durability, idempotency storage integrity, or sink
root legitimacy.

## Assumption Floor

Every applied result that relies on the audit append provider must carry:

```text
CAP-PROVIDER-01
CAP-PROVIDER-02
CAP-PROVIDER-03
CAP-SINK-01
CAP-SINK-02
CAP-IDEMPOTENCY-01
CAP-IDEMPOTENCY-02
CAP-STATUS-01
CAP-TCB-01
```

## ID Categories

```text
CAP-PROVIDER-*     provider object and implementation assumptions
CAP-SINK-*         declared sink root and sink durability assumptions
CAP-IDEMPOTENCY-*  idempotency enforcement and storage assumptions
CAP-STATUS-*       provider status-report assumptions
CAP-TCB-*          boundary assumptions for provider code outside proven core
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

### CAP-PROVIDER

```text
CAP-PROVIDER-01:
  statement: the provider object is assumed to match the approved capability descriptor.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: descriptor digest matching proves the live provider object is honest or correctly implemented.

CAP-PROVIDER-02:
  statement: the provider implementation is assumed to enforce append-only behavior.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: APPEND_APPLIED proves no overwrite, truncate, delete, or mutation occurred.

CAP-PROVIDER-03:
  statement: the provider is assumed not to expose arbitrary filesystem, network, or command power through the runner-facing capability.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: provider confinement is proven by the runner.
```

### CAP-SINK

```text
CAP-SINK-01:
  statement: legitimacy of the declared audit sink root is assumed, not proven.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: a declared sink root is absolutely legitimate or safe.

CAP-SINK-02:
  statement: sink durability and retention behavior are assumed outside SPIRA.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: APPEND_APPLIED proves durable persistence or future availability.
```

### CAP-IDEMPOTENCY

```text
CAP-IDEMPOTENCY-01:
  statement: the provider is assumed to enforce at most one record per idempotency key.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: SPIRA proves the provider cannot duplicate records.

CAP-IDEMPOTENCY-02:
  statement: idempotency storage durability and non-reset behavior are assumed outside SPIRA.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: repeated-key safety is proven across crashes, migrations, or storage loss.
```

### CAP-STATUS

```text
CAP-STATUS-01:
  statement: provider status reports are assumed honest and correctly mapped.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: APPEND_APPLIED is an independent proof that the append happened.
```

### CAP-TCB

```text
CAP-TCB-01:
  statement: provider code is outside the Lean-proven SPIRA composition core and outside the non-executing assessment proof boundary.
  universality: UNCONDITIONAL
  applies_to: applied provider-backed runner results
  forbidden_reading: provider behavior is proven by SPIRA's formal core.
```

## Stability Rule

Assumption IDs are stable. A future gate must not silently delete, rename, or
weaken an ID.

Any change to statement, universality, mandatory_when, or forbidden_reading
requires:

```text
LEDGER_VERSION_BUMP
explicit revision note
review of md/json consistency
adversarial review
human go/no-go owner approval
```

## Carrier Rule

Applied provider-backed runner results must carry every floor ID. A future
provider that cannot carry these assumptions must not report `APPEND_APPLIED`.

## Forbidden Collapse

No consumer may read these assumptions as:

```text
provider correctness proven
append proven
filesystem safety proven
sink durability proven
idempotency proven
execution generally authorized
severance authorized
automatic remediation authorized
```

## Verdict

```text
SPIRA_NESIRA_PHASE2_CAPABILITY_PROVIDER_ASSUMPTION_LEDGER_SPECIFIED
```
