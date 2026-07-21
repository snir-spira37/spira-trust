# Nesira Phase 2 Audit Append Public Exposure Readiness Plan

## Status

```text
DOCUMENT_TYPE: READINESS PLAN
PHASE: PHASE_2_AUDIT_APPEND_PUBLIC_EXPOSURE_READINESS_SCOPE_REVISION_GATE
SCOPE: READINESS_ONLY

IMPLEMENTATION: NOT_AUTHORIZED
PUBLIC_WHEEL_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_CHANGE: NOT_AUTHORIZED
PYPROJECT_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLICATION: NOT_AUTHORIZED
```

This plan compares possible future exposure paths for the completed private
`AUDIT_RECORD_APPEND_ONLY` chain. It does not select, implement, or release any
public runtime surface.

## Recommendation

The safest first public step, if any, is:

```text
Option B: public documentation only
```

The safest first runtime exposure, if a runtime surface is later required, is:

```text
Option C: public library exposure of non-writing evaluators only
```

The runner and provider should remain private until a separate release-candidate
gate proves that exposing side-effect-capable code is necessary and bounded.

Rationale:

```text
documentation-only preserves the public 0.7.3 wheel unchanged
non-writing evaluator exposure preserves side_effect_budget=0
runner exposure introduces an API that can call a side-effect capability
provider exposure introduces code that can hold append authority
CLI exposure adds user-facing execution ambiguity
```

## Baseline

Current public state:

```text
package: spira-trust 0.7.3
public wheel sha256: 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
public surface: assessment + conservative combined verdict + non-executing dry-run
public runner/provider exposure: false
```

Current private state:

```text
private chain complete through audit append provider
authorized action class: AUDIT_RECORD_APPEND_ONLY
side-effect envelope: effect_count=1, total_effect_count=1, retry_count=0
provider applied result requires native_idempotency_enforced=true
provider behavior remains outside Lean-proven core
```

## Option A: No Further Exposure

Keep the private append chain private.

Pros:

```text
no new public product surface
no wheel SHA change
no release risk
no side-effect-capable code distributed
```

Cons:

```text
external users cannot inspect or integrate the private audit append chain
public claim remains limited to the already released 0.7.3 surface
```

## Option B: Public Documentation Only

Publish or include documentation describing the private milestone and its
boundaries, without shipping runner/provider code.

Pros:

```text
no runtime exposure
no side-effect-capable public code
can state the boundary honestly
keeps provider assumptions visible
```

Cons:

```text
documentation can be misread as product capability unless carefully worded
does not let users run the chain
still requires public text review
```

Required future gate:

```text
documentation publication authorization
public claim review
reasonable-reader overclaim review
```

## Option C: Public Library Exposure Of Non-Writing Evaluators Only

Expose only the private consistency evaluators that cannot write:

```text
action authority evaluator
execution authorization evaluator
audit append non-executing evaluator
```

Do not expose:

```text
audit append runner
audit append capability provider
filesystem-capable sink binding API
public CLI
```

Pros:

```text
keeps public runtime side_effect_budget=0
preserves consistency-not-truth boundary
allows external users to inspect readiness artifacts
avoids distributing provider append authority
```

Cons:

```text
requires wheel allowlist change and version bump
requires RC and TestPyPI staging
claim must distinguish evaluator consistency from runner truth
```

This is the recommended first runtime exposure if runtime exposure is chosen.

## Option D: Public Runner Library Without Provider

Expose the audit append runner but not the provider.

Pros:

```text
runner still has no filesystem imports
runner can call only an injected append capability
capability digest matching remains testable by users
```

Cons:

```text
public users may supply their own capability object
misconfigured capabilities can cause real side effects outside SPIRA
claim risk is significantly higher than evaluator-only exposure
requires explicit public capability-safety documentation
```

This option requires a stronger RC than Option C and must not be combined with
CLI exposure.

## Option E: Public Runner Plus Declared Provider Library

Expose the runner and the declared audit append capability provider.

Pros:

```text
complete class-specific public path for one bounded audit append
provider surface remains append-only and descriptor-bound
```

Cons:

```text
ships the first SPIRA code path that can open a sink and write
requires installed-wheel side-effect tests
requires native idempotency behavior to be stated with extreme care
provider behavior is not Lean-proven
APPEND_APPLIED can be misread as append proof
```

This option is not recommended as the first public runtime exposure unless the
product need specifically requires public append capability.

## Option F: Public CLI Exposure For Append

Expose append behavior through a command or subcommand.

Pros:

```text
easier to invoke manually
```

Cons:

```text
highest confusion risk
exit codes can be misread as permission
flags and examples can become runbooks
sink selection can drift toward arbitrary path behavior
```

This option is not recommended for the first audit-append exposure.

## Future RC Requirements

Any future RC that changes public wheel content must include:

```text
version bump
wheel SHA pin
public wheel allowlist diff
V1 narrow refresh if a V1-pinned file changes
release notes review
public claim review
TestPyPI staging
post-install verification from built wheel
full pytest
public wheel inspection
```

If Option C is selected, the RC must prove:

```text
non-writing evaluator modules are importable from installed wheel
side_effect_budget remains 0 for exposed modules
runner/provider remain absent
outputs carry ACTION_NOT_PERFORMED or equivalent non-execution markers
EA-TCB-03 remains carried as an assumption
no executable fields are emitted
```

If Option D or E is selected, the RC must additionally prove:

```text
runner source imports no filesystem/network/subprocess primitives
provider source scan covers open mode and forbidden probes
negative installed-wheel cases write zero records
positive installed-wheel case writes at most one bounded record to a controlled sink
capability digest mismatch writes zero records
missing native durable idempotency returns UNKNOWN before write
APPLIED carries CAP-* assumption floor
public output exposes no path, command, runbook, or network target
```

If Option F is ever proposed, it must be a separate authorization.

## Public Text Requirements

Future public text must preserve:

```text
opt-in only
class-specific only
AUDIT_RECORD_APPEND_ONLY only
not a generic runner
not arbitrary filesystem access
APPEND_APPLIED is a status report, not proof
provider behavior is outside the Lean-proven core
CAP-* assumptions remain NOT_PROVEN
EA-TCB-03 remains assumed, not proven
no severance or remediation
```

Forbidden:

```text
safe to write
safe to run
execution approved
action authorized by Nesira
append proven
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
certified/audited/endorsed
```

## Support And Rollback Planning

Any future exposure gate must define:

```text
how to yank a release if public append behavior is wrong
how to delete or supersede a GitHub release
how to communicate that APPEND_APPLIED was a status report only
how to advise users to stop using a flawed provider binding
how to preserve evidence for any reported duplicate append
```

Rollback documentation must not imply that an append can be undone by this
class. Immutable audit append correction requires a later compensating record
that is not authorized by this readiness gate.

## Stop Conditions

Stop before any RC if:

```text
the chosen exposure path requires public CLI for first exposure
the claim cannot keep APPEND_APPLIED below proof language
runner/provider exposure is treated as routine packaging
raw paths are accepted as runner-facing API
provider APPLIED does not carry CAP-* assumptions
installed-wheel tests cannot prove zero records for negative cases
public text describes provider behavior as Lean-proven
```

## Next Step

If Snir chooses a public exposure path, open a separate release-candidate
authorization for that exact option. This readiness plan does not authorize
implementation, release, or publication.
