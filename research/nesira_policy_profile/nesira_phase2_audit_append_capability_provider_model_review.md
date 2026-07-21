# Nesira Phase 2 Audit Append Capability Provider Model Review

## Verdict

```text
NESIRA_PHASE2_AUDIT_APPEND_CAPABILITY_PROVIDER_MODEL_ACCEPTED
```

## Scope Review

The model is docs-only. It does not authorize provider implementation, runner
code changes, public exposure, CLI exposure, wheel exposure, version bump,
release, generic filesystem behavior, network sinks, severance, or remediation.

## Boundary Review

The model preserves the critical boundary:

```text
runner orchestrates one authorized call
provider owns the real append mechanism
SPIRA does not prove provider correctness
```

This keeps the first side-effect path capability-based rather than ambient. The
runner still must not receive paths or filesystem primitives.

## Capability Shape Review

The operational surface remains exactly:

```text
append_one(record_payload, idempotency_key)
```

The allowed metadata is inert identity metadata:

```text
append_capability_ref
append_capability_root_digest
audit_sink_root_ref
provider_contract_version
```

The forbidden surface explicitly includes path, open, read, arbitrary write,
delete, overwrite, list, stat, exists, resolve, network endpoint, command
execution, retry, flush, and close.

## Digest Binding Review

The model keeps the runner-side digest comparison load-bearing while correctly
refusing to overclaim it:

```text
runner digest == expected context digest == human-go digest == verifier digest
```

This prevents capability substitution at the runner call site. It does not prove
the capability object is honest or backed by the descriptor, and the model says
that explicitly.

## Provider Assumption Review

The provider assumptions are named as assumptions:

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

This is the right layer of honesty: the provider can become evidence-bearing in
a later gate, but it is not pulled into the proven SPIRA core by documentation.

## Idempotency Review

The model treats idempotency as load-bearing and explicitly states that a
repeated key must not create a second record. It also records idempotency storage
durability as an assumption, not a proof.

## No Probe Review

The model keeps probes out of the runner:

```text
does the sink exist?
is the sink writable?
what path will be written?
did the provider write the record?
read the record back
```

Any need for those questions at the runner boundary becomes
`RUNNER_TCB_SCOPE_REVISION_REQUIRED`.

## Claim Review

The forbidden claims prevent the obvious overclaim:

```text
append proof
filesystem safety proven
sink durability proven
provider honesty proven
execution generally authorized
safe to run arbitrary action
```

The allowed language stays narrow: the provider reported a status and provider
correctness remains `NOT_PROVEN`.

## Next Gate

A later gate may discuss a provider implementation authorization, but only after
deciding whether SPIRA should own any provider code at all. If provider code is
implemented inside this repository, the gate must treat it as the first code that
may hold real filesystem authority.
