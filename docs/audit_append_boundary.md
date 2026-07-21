# Audit Append Boundary

SPIRA has a private, opt-in, class-specific `AUDIT_RECORD_APPEND_ONLY` chain.
It evaluates declared preconditions for one bounded audit append and can
delegate the append attempt to a declared capability provider under recorded
assumptions.

This page is boundary documentation. It is not a release announcement, not a
public runtime exposure, and not a public CLI.

## Public Package Boundary

The public `spira-trust` 0.7.3 wheel remains an assessment and non-executing
dry-run surface.

It does not include:

```text
audit append runner
audit append capability provider
execution authorization evaluator
action authority evaluator
```

The public wheel SHA for 0.7.3 is:

```text
308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
```

## Private Chain

The completed private chain is:

```text
assessment
  -> combined verdict
  -> action authority
  -> non-executing dry-run
  -> execution-authorization evaluator
  -> audit append evaluator
  -> audit append runner
  -> audit append capability provider
```

The only action class in this chain is:

```text
AUDIT_RECORD_APPEND_ONLY
```

The envelope is:

```text
effect_count: 1
total_effect_count: 1
retry_count: 0
supporting_effects: none
```

No second side-effect class is authorized.

## Runner Boundary

The private runner has no ambient filesystem authority. It receives a
runner-facing capability object and may call:

```text
append_one(record_payload, idempotency_key)
```

at most once, only after its preconditions pass.

The runner does not receive or resolve filesystem paths. It checks that the
declared append capability digest matches the expected context, the human-go
artifact, and the trusted-verifier artifact before it calls the capability.

## Provider Boundary

The private provider is the first code in this chain that may hold real append
authority.

Its runner-facing surface is limited to:

```text
append_one(record_payload, idempotency_key)
append_capability_ref
append_capability_root_digest
audit_sink_root_ref
provider_contract_version
```

The provider does not expose the sink path to the runner.

The provider's direct filesystem primitive is limited to one append-mode open
and one write to a declared sink binding. It does not perform retries, fallback
writes, readback, path probes, directory creation, network sends, subprocess
execution, severance, or remediation.

## Idempotency Boundary

The provider reports `APPEND_APPLIED` only when the declared sink binding
states:

```text
native_idempotency_enforced = true
```

That value is included in the canonical descriptor and is bound into:

```text
append_capability_root_digest
```

If native durable idempotency is not declared, the provider returns:

```text
APPEND_STATUS_UNKNOWN
```

before writing.

## Assumption Boundary

`APPEND_APPLIED` is a provider status report. It is not proof that the append is
durable, that the sink root is legitimate, that idempotency is truly enforced,
or that the provider behavior is covered by SPIRA's Lean-proven composition
core.

Provider behavior and sink properties remain conditional on recorded `CAP-*`
assumptions, including:

```text
CAP-TCB-01
CAP-IDEMPOTENCY-02
CAP-STATUS-01
```

`EA-TCB-03` also remains an assumption. It records that the trusted verifier
sees the runner-intended context; it does not prove runner truth by itself.

## Not Claimed

This boundary does not claim:

```text
safe to write
safe to run
execution approved
permission granted by Nesira
append truth proven
durability proven
idempotency proven
sink legitimacy proven
provider proven by Lean
secure filesystem runner
generic runner
arbitrary path support
automatic remediation
severance authorized
security guarantee
trust guarantee
independent certification
audit
endorsement
third-party validation
```

## Still Not Authorized

The following remain outside this documentation-only boundary:

```text
public runner exposure
public provider exposure
public CLI for append
public wheel change
version bump
release
second side-effect class
generic filesystem adapter
network sink
retry
fallback sink
severance action
automatic remediation
```

Any future public runtime exposure of the runner or provider requires a
separate release-candidate gate and a separate publication decision.
