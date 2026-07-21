# Nesira Phase 2 Capability Provider Assumption Ledger Review

## Verdict

```text
SPIRA_NESIRA_PHASE2_CAPABILITY_PROVIDER_ASSUMPTION_LEDGER_ACCEPTED
```

## Scope Review

The ledger is docs-only. It defines stable `CAP-*` assumption IDs and does not
authorize provider implementation, runner API changes, public wheel exposure,
CLI exposure, version bump, release, severance, or remediation.

## Floor Review

The assumption floor contains all nine provider assumptions required by the
capability provider model:

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

Every ID has a statement and forbidden reading. This closes the opaque-token
gap before any provider code emits these assumptions.

## Boundary Review

The strongest boundary is stated directly:

```text
APPEND_APPLIED is never assumption-free.
```

The ledger refuses to turn provider status into proof. It records provider
object matching, append-only behavior, sink durability, idempotency, and status
honesty as assumptions, not SPIRA guarantees.

## Stability Review

The stability rule mirrors the EA ledger discipline:

```text
no silent delete
no silent weakening
version bump required
explicit revision note required
md/json consistency review required
adversarial review required
human go/no-go owner approval required
```

This makes `CAP-*` a governed assumption family rather than local prose in a
provider authorization.

## Consistency Review

The markdown and JSON ledgers both define the same nine IDs and the same floor.
A later implementation gate must verify this mechanically before emitting or
testing provider-backed applied results.
