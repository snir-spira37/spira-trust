# Nesira Phase 2 Audit Append Capability Provider Implementation Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_CAPABILITY_PROVIDER_IMPLEMENTATION_GATE
SCOPE: PRIVATE_PROVIDER_IMPLEMENTATION_AUTHORIZATION

AUTHORIZES:
private audit append capability provider implementation for AUDIT_RECORD_APPEND_ONLY
private provider conformance tests
provider implementation report and results

DOES_NOT_AUTHORIZE:
runner API change
runner behavior change
generic filesystem adapter
arbitrary path handling
network sink
public exposure
CLI exposure
wheel exposure
version bump
release
severance
automatic remediation
```

This authorization may permit the first repository code whose implementation
can hold real append authority. It is limited to one private provider for the
already-authorized `AUDIT_RECORD_APPEND_ONLY` runner path.

## Core Lock

```text
PROVIDER_APPEND_AUTHORITY_IS_NOT_GENERAL_FILESYSTEM_AUTHORITY
PROVIDER_REPORTED_APPLIED_IS_NOT_APPEND_PROOF
RUNNER_MUST_STILL_NOT_RECEIVE_PATHS
```

The provider may be able to append one bounded record to one declared sink. It
must not become a generic filesystem writer, path resolver, log framework,
network client, or remediation mechanism.

## Selected Provider Class

```text
PROVIDER_CLASS: DECLARED_AUDIT_APPEND_CAPABILITY_PROVIDER
ACTION_CLASS: AUDIT_RECORD_APPEND_ONLY
EFFECT_SHAPE: APPEND_ONE_BOUNDED_RECORD
EFFECT_COUNT: 1
TOTAL_EFFECT_COUNT: 1
RETRY_COUNT: 0
SUPPORTING_EFFECTS: none
```

No other provider class is authorized.

## Capability Surface

The provider object supplied to the runner may expose exactly:

```text
append_one(record_payload, idempotency_key)
append_capability_ref
append_capability_root_digest
audit_sink_root_ref
provider_contract_version
```

The provider object supplied to the runner must not expose:

```text
path
open
read
write
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

Those operations must not be visible through the runner-facing object, even if a
future provider implementation uses a private lower-level substrate internally.

## Sink Binding

The provider must be constructed from a declared sink binding. The runner must
receive only opaque identifiers and digests, never a filesystem path.

The provider's canonical descriptor must include:

```text
provider_id
provider_contract_version
audit_sink_root_id
audit_sink_root_version
sink_binding_digest
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
```

The descriptor digest becomes `append_capability_root_digest`.

The sink binding may identify a local sink to the provider, but that identity is
not exposed to the runner and is not a public claim. The legitimacy of the sink
binding remains `CAP-SINK-01`.

## Direct Filesystem Authority

If the implementation uses direct filesystem primitives internally, they are
authorized only inside the private provider module and only for one append
operation to the declared sink binding.

The implementation must not:

```text
accept paths from the runner
accept arbitrary paths from evidence
write outside the declared sink binding
create parent directories
delete
truncate
overwrite
rename
copy
move
list directories
read back the sink
stat or probe before append
retry
write fallback diagnostics
write failure audit records
write checkpoints
write lock files
write caches
send network traffic
spawn subprocesses
```

If appending cannot be attempted without a probe, setup write, retry, lock, or
fallback side effect, this provider class is incomplete and must stop with:

```text
PROVIDER_SCOPE_REVISION_REQUIRED
```

## Idempotency Boundary

The provider must not create a duplicate record for a repeated idempotency key.

If durable idempotency cannot be enforced within the one authorized effect, the
provider must not report `APPEND_APPLIED`. It must return:

```text
APPEND_STATUS_UNKNOWN
```

or decline before append with:

```text
APPEND_NOT_AUTHORIZED
```

An idempotency registry that requires a second write, readback, lock, cleanup, or
checkpoint is not authorized by this gate.

## Result Mapping

The provider may return only:

```text
APPEND_APPLIED
APPEND_STATUS_UNKNOWN
APPEND_NOT_AUTHORIZED
```

The runner maps these as already specified:

```text
APPEND_APPLIED -> one applied effect reported
APPEND_STATUS_UNKNOWN -> not success, no follow-on action
APPEND_NOT_AUTHORIZED -> not success, no retry or fallback
malformed/exception -> status unknown
```

`APPEND_APPLIED` is a provider status report, not proof that the sink is durable,
append-only, or legitimate.

## Required Assumptions

Any applied result through this provider must carry:

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
EA-TCB-03
EA-META-01
EA-META-02
```

If implementation adds provider-specific assumption IDs, they must be documented
before acceptance. Assumption IDs must not be silently removed or weakened.

## Required Conformance

A future implementation must prove at least:

```text
1. provider descriptor digest is deterministic.
2. descriptor digest mismatch prevents injection into the runner.
3. runner-facing provider object exposes no path/open/read/write/delete/stat.
4. positive path calls provider append exactly once through the runner.
5. positive path writes at most one record to a controlled test sink.
6. repeated idempotency key does not create a duplicate record.
7. oversized record is rejected before append.
8. secret-bearing record is rejected before append.
9. command/path/runbook field in payload is rejected before append.
10. provider status unknown maps to no success.
11. provider exception maps to status unknown and no fallback write.
12. missing sink binding prevents append.
13. undeclared sink binding prevents append.
14. request for retry prevents append.
15. request for fallback sink prevents append.
16. no parent directory creation.
17. no readback/stat/list/exists probes by provider if direct filesystem is used.
18. all negative cases produce zero records in the controlled test sink.
19. all applied outputs carry provider NOT_PROVEN assumptions.
20. public wheel exclusion remains true.
21. no CLI exposure.
22. full pytest.
23. V1 SHA256SUMS remains 622/622 if unchanged.
```

Tests may inspect controlled temporary sinks after provider calls. Provider code
itself must not use readback as a success condition.

## Source Scan Requirements

If direct filesystem primitives are used, the scan must prove they occur only in
the provider module and only in the append implementation path.

The runner source must still have zero imports or calls for:

```text
os
pathlib
open
subprocess
socket
requests
urllib
http
stat
exists
read
resolve
list
```

Provider source must have zero imports or calls for:

```text
subprocess
socket
requests
urllib
http
delete
remove
rename
replace
copy
move
rmtree
mkdir
makedirs
glob
iterdir
```

Any broader filesystem authority must stop with:

```text
PROVIDER_SCOPE_REVISION_REQUIRED
```

## Authorized Files

This gate may edit only:

```text
source/spira_core/nesira_phase2_audit_append_provider.py
tests/test_nesira_phase2_audit_append_provider.py
research/nesira_policy_profile/nesira_phase2_audit_append_capability_provider_implementation_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_capability_provider_implementation_authorization_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_capability_provider_implementation_report.md
research/nesira_policy_profile/nesira_phase2_audit_append_capability_provider_implementation_results.json
research/nesira_policy_profile/nesira_phase2_audit_append_capability_provider_implementation_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_capability_provider_implementation_review_results.json
```

Any runner API change, public wheel change, CLI change, workflow change,
pyproject/version change, release, claim expansion, generic filesystem adapter,
network sink, severance, or remediation change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Stop Conditions

Stop if the implementation:

```text
exposes paths to the runner
uses arbitrary paths
creates directories
uses retry
uses fallback sink
writes diagnostics or failure audit records
performs readback/stat/list/exists probes as success criteria
claims APPEND_APPLIED is a proof
omits provider NOT_PROVEN assumptions
enters the public wheel
adds a CLI or release surface
```

## Verdict

```text
NESIRA_PHASE2_AUDIT_APPEND_CAPABILITY_PROVIDER_IMPLEMENTATION_AUTHORIZED
```
