# Nesira Phase 2 Audit Append Capability Provider Implementation Authorization Review

## Verdict

```text
NESIRA_PHASE2_AUDIT_APPEND_CAPABILITY_PROVIDER_IMPLEMENTATION_AUTHORIZATION_ACCEPTED
```

## Scope Review

The authorization opens only a private provider implementation gate for:

```text
DECLARED_AUDIT_APPEND_CAPABILITY_PROVIDER
AUDIT_RECORD_APPEND_ONLY
```

It does not authorize runner API changes, public wheel exposure, CLI exposure,
version bump, release, network sinks, generic filesystem adapters, severance, or
automatic remediation.

The authorization now also admits the CAP assumption ledger files as part of
this docs hardening, so the provider may not emit opaque `CAP-*` tokens without
a single-source definition.

## Rubicon Review

This is the first gate that may allow repository code below the runner to hold
real append authority. The authorization treats that as a new risk class, not as
a continuation of the runner implementation.

The key boundary is preserved:

```text
runner receives no path
provider may hold the append authority
provider correctness remains NOT_PROVEN
```

## Capability Surface Review

The runner-facing provider surface remains narrow:

```text
append_one(record_payload, idempotency_key)
append_capability_ref
append_capability_root_digest
audit_sink_root_ref
provider_contract_version
```

The runner-facing object must not expose path/open/read/write/delete/stat/list,
network endpoint, command execution, retry, flush, or close.

## Sink Binding Review

The authorization requires an opaque sink binding and canonical descriptor. This
keeps the runner from learning a path while still making capability substitution
detectable through the digest already checked by the runner.

The sink binding legitimacy remains an assumption:

```text
CAP-SINK-01
```

## Direct Filesystem Review

The authorization is careful about direct filesystem authority. It permits such
authority only inside a future private provider module and only for one append to
the declared sink binding.

The provider must not create directories, delete, truncate, overwrite, rename,
copy, move, list, read back, stat/probe before append, retry, write fallback
diagnostics, or use network/subprocess behavior.

The required source scan includes the probe family explicitly:

```text
stat
exists
is_file
read
read_text
read_bytes
samefile
resolve
absolute
```

## Idempotency Review

The strongest part of the authorization is the idempotency boundary:

```text
if durable idempotency cannot be enforced within the one authorized effect,
the provider must not report APPEND_APPLIED
```

This prevents a simple append-only file writer from overclaiming exactly-once
semantics unless the implementation can actually enforce them within the
authorized envelope or honestly returns status unknown/not authorized.

## Conformance Review

The 23 required cases cover:

```text
deterministic descriptor digest
descriptor mismatch prevents injection
runner-facing surface exposes no path/open/read/write/delete/stat
positive path calls append exactly once
positive path writes at most one record to a controlled test sink
repeated idempotency key does not duplicate
oversized/secret/command/path payloads rejected before append
unknown/exception/malformed provider status is not success
missing or undeclared sink binding prevents append
retry/fallback requests prevent append
no directory creation
no readback/stat/list/exists probes as provider success criteria
negative cases produce zero records
provider NOT_PROVEN assumptions carried
public wheel exclusion remains true
```

Tests may inspect controlled temporary sinks after provider calls, but provider
code must not use readback as proof of success.

## Boundary Verdict

The authorization is accepted as an implementation gate, not as a release or
public exposure gate. The next implementation may write only the private provider
and its tests under this envelope.
