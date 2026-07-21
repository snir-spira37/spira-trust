# Nesira Phase 2 Private Audit Append Chain Milestone

## Status

```text
DOCUMENT_TYPE: MILESTONE_RECORD
PHASE: PHASE_2_PRIVATE_AUDIT_APPEND_CHAIN
SCOPE: PRIVATE_AUDIT_RECORD_APPEND_ONLY_CHAIN

VERDICT:
NESIRA_PHASE2_PRIVATE_AUDIT_APPEND_CHAIN_COMPLETE_PRIVATE_ONLY

PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLI_EXPOSURE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
GENERIC_RUNNER: NOT_AUTHORIZED
NETWORK_SINK: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
```

This milestone records completion of the private `AUDIT_RECORD_APPEND_ONLY`
chain through the first bounded disk-write provider.

It does not authorize public exposure, CLI exposure, wheel exposure, version
bump, release, a second side-effect class, generic runner behavior, network
execution, severance, or automatic remediation.

## Completed Private Chain

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

The only completed side-effect class is:

```text
AUDIT_RECORD_APPEND_ONLY
```

## Public Baseline

The public package remains `spira-trust` 0.7.3.

The public wheel SHA remains:

```text
308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
```

The public wheel does not include:

```text
audit append runner
audit append capability provider
execution authorization evaluator
action authority evaluator
```

No public claim, release, CLI flag, workflow, pyproject, or version change was
made for this private chain.

## Runner Boundary

The private audit append runner has no ambient filesystem authority.

It imports only:

```text
__future__
typing
```

It receives a runner-facing capability object and may call:

```text
append_one(record_payload, idempotency_key)
```

at most once, only after all runner preconditions pass.

The runner does not receive or resolve filesystem paths.

The runner performs a three-way capability digest check before the call:

```text
runner_supplied.append_capability_root_digest
  == expected_context.append_capability_root_digest
  == human_go_authorized.append_capability_root_digest
  == trusted_verifier_approved.append_capability_root_digest
```

Any missing or mismatched digest prevents the call.

## Provider Boundary

The private provider is the first repository code in this chain that may hold
real append authority.

Its runner-facing surface is limited to:

```text
append_one(record_payload, idempotency_key)
append_capability_ref
append_capability_root_digest
audit_sink_root_ref
provider_contract_version
```

The provider does not expose the sink path to the runner.

The provider's only filesystem primitive is:

```text
open(sink_target, "a")
sink.write(line)
```

It does not use:

```text
mkdir
makedirs
delete
remove
rename
replace
copy
move
rmtree
glob
iterdir
stat
exists
is_file
read
read_text
read_bytes
samefile
resolve
network
subprocess
retry
fallback sink
```

## Idempotency Boundary

The provider reports `APPEND_APPLIED` only when the declared sink binding states:

```text
native_idempotency_enforced = true
```

That value is included in the canonical descriptor and therefore bound into:

```text
append_capability_root_digest
```

If native durable idempotency is not declared, the provider returns:

```text
APPEND_STATUS_UNKNOWN
```

before writing. This prevents the reference provider from reporting success when
it cannot enforce durable idempotency within the one-effect budget.

Idempotency durability remains an assumption:

```text
CAP-IDEMPOTENCY-02
```

## Assumption Boundary

Applied provider-backed results carry the canonical CAP assumption floor:

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

Most importantly:

```text
CAP-TCB-01:
  provider code is outside the Lean-proven SPIRA composition core and outside
  the non-executing assessment proof boundary.
```

The private append provider is tested and bounded. It is not formally proven by
the SPIRA Lean core.

## Hardening Closed

The runner/provider frontier closed the following findings:

```text
dry-run winning_status:
  combined NOT_EVALUATED now fails closed to DRY_RUN_NOT_EVALUATED

execution allowlist:
  missing allowlists now fail closed to NOT_EVALUATED

capability digest:
  runner requires digest agreement across runner/context/human-go/verifier

provider idempotency:
  provider returns UNKNOWN before write unless native durable idempotency is
  declared and digest-bound
```

## Verification Snapshot

Latest accepted verification:

```text
provider + runner targeted tests: 50 passed
full pytest:                      495 passed
V1 SHA256SUMS:                    622 OK / 0 FAILED / 0 MISSING
public wheel SHA:                 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
public wheel runner exposed:      false
public wheel provider exposed:    false
```

## Still Not Authorized

The following remain blocked:

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
claim that APPEND_APPLIED proves append durability
claim that provider behavior is proven by the Lean core
```

## Next Boundary

Any future exposure of the runner/provider chain is a new product and release
decision class.

Any second side-effect class is a new runner taxonomy and side-effect budget
decision class.

Either path must start from:

```text
SCOPE_REVISION_REQUIRED
```

## Milestone Decision

```text
NESIRA_PHASE2_PRIVATE_AUDIT_APPEND_CHAIN_COMPLETE_PRIVATE_ONLY
```
