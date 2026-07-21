# Nesira Phase 2 Audit Append Capability Provider Model

## Status

```text
DOCUMENT_TYPE: MODEL
PHASE: PHASE_2_AUDIT_APPEND_CAPABILITY_PROVIDER_MODEL
SCOPE: CAPABILITY_PROVIDER_CONTRACT_ONLY

AUTHORIZES:
provider model documentation
provider trust-boundary description
provider conformance expectations for a later gate

DOES_NOT_AUTHORIZE:
provider implementation
runner code change
public exposure
CLI exposure
wheel exposure
version bump
release
generic filesystem adapter
arbitrary path handling
network sink
severance
automatic remediation
```

This model describes the external append capability that may be injected into
the private `AUDIT_RECORD_APPEND_ONLY` runner. It does not implement that
capability and does not authorize any new side effect.

## Core Lock

```text
PROVIDER_CAPABILITY_IS_NOT_RUNNER_AUTHORIZATION
PROVIDER_CAPABILITY_IS_NOT_APPEND_PROOF
```

Possessing an append capability object does not authorize execution. The runner
may call it only after the runner's own authorization preconditions pass.

The provider may perform the real append in a future implementation. SPIRA does
not prove the provider is honest, append-only, durable, or correctly bound to
the declared sink root. Those facts remain assumptions carried by the runner
result.

## Layer Boundary

```text
assessment
combined verdict
action authority
dry-run
execution authorization
audit append evaluator
audit append runner
append capability provider
```

The provider sits below the runner. It is not allowed to reinterpret upstream
assessment, combined verdict, action authority, dry-run, or human-go artifacts.
It receives only a record payload and idempotency key from the runner after the
runner has already completed its precondition checks.

## Capability Shape

The object supplied to the runner must expose exactly this operational method:

```text
append_one(record_payload, idempotency_key)
```

It may expose only inert identity fields:

```text
append_capability_ref
append_capability_root_digest
audit_sink_root_ref
provider_contract_version
```

It must not expose to the runner:

```text
path
open
read
write arbitrary bytes
delete
overwrite
list
stat
exists
resolve
network endpoint
command execution
retry
flush
close
```

If a future provider needs any of those operations to be exposed to SPIRA code,
it is no longer this capability provider model and must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Capability Root Digest

The provider identity digest is a digest over a canonical capability descriptor,
not over a filesystem path supplied to the runner.

The canonical descriptor must include at least:

```text
provider_id
provider_contract_version
audit_sink_root_id
audit_sink_root_version
append_only_policy_id
append_only_policy_digest
idempotency_namespace
record_schema_id
record_schema_version
max_record_size
authorized_action_class = AUDIT_RECORD_APPEND_ONLY
effect_shape = APPEND_ONE_BOUNDED_RECORD
effect_count = 1
total_effect_count = 1
retry_count = 0
supporting_effects = none
network_allowed = false
arbitrary_path_allowed = false
```

The descriptor may include an opaque sink root reference. It must not require
the runner to receive or resolve a path.

The runner's digest comparison remains a consistency check:

```text
runner_supplied.append_capability_root_digest
  == expected_context.append_capability_root_digest
  == human_go_authorized.append_capability_root_digest
  == trusted_verifier_approved.append_capability_root_digest
```

This comparison does not prove the provider object implements the descriptor.
It only prevents substituting a differently declared capability at the call
site.

## Provider Obligations

A conforming provider is expected to enforce:

```text
append-only behavior
one bounded non-secret record per call
schema validation before append
idempotency-key deduplication
no overwrite
no delete
no truncate
no target artifact mutation
no command execution
no network send
no retry beyond the authorized side-effect budget
```

These obligations are not proven by SPIRA. A future verifier or provider test
may collect evidence for them, but they remain `NOT_PROVEN` assumptions unless a
separate proof exists and is accepted through a later gate.

## Result Mapping

The provider may return only:

```text
APPEND_APPLIED
APPEND_STATUS_UNKNOWN
APPEND_NOT_AUTHORIZED
```

`APPEND_APPLIED` means only that the provider claims the one append was applied.
It is not a proof of durability, append-only semantics, or sink-root
legitimacy.

`APPEND_STATUS_UNKNOWN` means the provider cannot establish whether the append
was applied. It is not success and must not authorize any follow-on action.

`APPEND_NOT_AUTHORIZED` means the provider declined the append. The runner must
not retry or use a fallback sink.

Any malformed provider response maps to status unknown at the runner boundary.

## Idempotency

The provider must treat `idempotency_key` as load-bearing. A repeated key must
not create a second record.

The integrity of the idempotency registry remains an assumption:

```text
CAP-IDEMPOTENCY-01: provider enforces one record per idempotency key
CAP-IDEMPOTENCY-02: idempotency storage is durable and not silently reset
```

If idempotency cannot be established, the provider must not claim
`APPEND_APPLIED`.

## No Probe Leakage To Runner

Provider implementation may need private internal checks. The runner must never
receive those checks as methods, paths, status probes, or copy-paste
instructions.

The runner must not ask:

```text
does the sink exist?
is the sink writable?
what path will be written?
did the provider write the record?
read the record back
```

If correctness requires the runner to ask those questions, the model is
incomplete and must stop with:

```text
RUNNER_TCB_SCOPE_REVISION_REQUIRED
```

## Provider Assumption Ledger

Every applied runner result that relies on a provider must carry assumptions for
at least:

```text
CAP-PROVIDER-01: provider object matches the approved capability descriptor
CAP-PROVIDER-02: provider implementation is append-only
CAP-PROVIDER-03: provider does not expose arbitrary filesystem or network power
CAP-SINK-01: declared sink root legitimacy is assumed
CAP-SINK-02: sink durability is assumed
CAP-IDEMPOTENCY-01: idempotency key prevents duplicate records
CAP-IDEMPOTENCY-02: idempotency registry durability is assumed
CAP-STATUS-01: provider status report is assumed honest
CAP-TCB-01: provider remains outside SPIRA's proven core
```

These IDs are provider assumptions, not trust proofs. They may be mirrored into
a later JSON ledger only under a separate ledger-version gate.

## Forbidden Claims

No document, runner result, or provider result may claim:

```text
append proof
filesystem safety proven
sink durability proven
provider honesty proven
execution generally authorized
safe to run arbitrary action
severance authorized
automatic remediation authorized
```

Allowed language:

```text
declared append capability supplied
capability digest matched
one append call requested
provider reported APPEND_APPLIED
provider correctness remains NOT_PROVEN
```

## Future Conformance Requirements

A later provider implementation authorization must include cases for:

```text
1. descriptor digest matches approved digest -> provider eligible for injection.
2. descriptor digest mismatch -> provider not eligible.
3. provider exposes path/open/read/write/delete/stat -> rejected.
4. provider exposes network endpoint -> rejected.
5. provider returns APPEND_APPLIED -> runner may report one applied effect.
6. provider returns APPEND_STATUS_UNKNOWN -> runner reports status unknown.
7. provider raises -> runner reports status unknown.
8. provider returns malformed response -> runner reports status unknown.
9. repeated idempotency key -> no duplicate record.
10. oversized record -> not authorized or not evaluated, no append claim.
11. secret-bearing record -> rejected before append.
12. command/path/runbook field in payload -> rejected before append.
13. provider attempts retry -> rejected or out of scope.
14. fallback sink request -> rejected or out of scope.
15. provider cannot establish append-only behavior -> NOT_EVALUATED.
16. all outputs carry provider NOT_PROVEN assumptions.
```

## Stop Conditions

Stop with `SCOPE_REVISION_REQUIRED` if a later gate:

```text
implements a provider
adds a filesystem path to the runner API
lets the runner open/read/stat/resolve a sink
allows a generic filesystem adapter
allows network sinks
adds retry or fallback sink behavior
omits provider NOT_PROVEN assumptions
claims provider correctness is proven by the runner
exposes this provider publicly
changes wheel, CLI, version, release, or public claim
```

## Verdict

```text
NESIRA_PHASE2_AUDIT_APPEND_CAPABILITY_PROVIDER_MODEL_SPECIFIED
```
