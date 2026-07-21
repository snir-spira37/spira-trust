# Nesira Phase 2 Audit Append Public Exposure Readiness Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_PUBLIC_EXPOSURE_READINESS_SCOPE_REVISION_GATE
SCOPE: DOCS_ONLY_PUBLIC_EXPOSURE_READINESS_PLANNING

AUTHORIZES:
public exposure readiness planning for the private AUDIT_RECORD_APPEND_ONLY chain
public claim boundary drafting
release-candidate checklist drafting
support and rollback planning
exposure option comparison

SOURCE_CHANGE: NOT_AUTHORIZED
TEST_CHANGE: NOT_AUTHORIZED
PYPROJECT_CHANGE: NOT_AUTHORIZED
PUBLIC_WHEEL_CHANGE: NOT_AUTHORIZED
PUBLIC_CLI_CHANGE: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
WORKFLOW_CHANGE: NOT_AUTHORIZED
FILESYSTEM_MUTATION_BY_THIS_GATE: NOT_AUTHORIZED
NETWORK_EXECUTION: NOT_AUTHORIZED
SUBPROCESS_EXECUTION: NOT_AUTHORIZED
SECOND_SIDE_EFFECT_CLASS: NOT_AUTHORIZED
GENERIC_RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
PUBLIC_CLAIM_USE: NOT_AUTHORIZED
```

This gate accepts the `SCOPE_REVISION_REQUIRED` marker from the private audit
append milestone only for discussion and readiness planning. It does not
authorize implementation, public packaging, publication, or runtime use.

## Baseline

The accepted private milestone is:

```text
verdict:
NESIRA_PHASE2_PRIVATE_AUDIT_APPEND_CHAIN_COMPLETE_PRIVATE_ONLY

milestone commit:
a77ace464dc79214b23468a1d5d981360d6d8517

public package:
spira-trust 0.7.3

public wheel sha256:
308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
```

The public wheel still excludes:

```text
audit append runner
audit append capability provider
execution authorization evaluator
action authority evaluator
```

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

The only side-effect class in scope for this readiness discussion is:

```text
AUDIT_RECORD_APPEND_ONLY
```

## Exposure Question

The readiness question is:

```text
Should the private AUDIT_RECORD_APPEND_ONLY chain ever become a public,
opt-in product surface?
```

It is not:

```text
Should SPIRA expose a generic runner?
Should SPIRA expose arbitrary filesystem writes?
Should SPIRA expose a public CLI that appends to disk?
Should SPIRA authorize severance or remediation?
Should APPEND_APPLIED be claimed as proof of durable append truth?
```

## Core Boundary

Public exposure of this chain is materially different from the public 0.7.3
dry-run surface because it may expose code that can cause a real append through
an injected capability provider.

Any future public exposure must preserve:

```text
class-specific behavior only: AUDIT_RECORD_APPEND_ONLY
effect_count: 1
total_effect_count: 1
retry_count: 0
supporting_effects: none
no generic runner
no arbitrary path
no network sink
no fallback sink
no default enablement
no automatic remediation
```

The private provider may report `APPEND_APPLIED` only when
`native_idempotency_enforced = true` is included in the canonical descriptor and
therefore bound into `append_capability_root_digest`.

Any future public exposure must still state that:

```text
APPEND_APPLIED is a provider status report, not proof of sink durability,
root legitimacy, idempotency truth, or append truth.
```

## Exposure Options

The readiness package must compare at least:

```text
Option A: no public exposure
  keep the full audit append chain private

Option B: public documentation only
  describe the private milestone and boundaries, no runtime code exposure

Option C: public library exposure of non-writing evaluators only
  expose consistency evaluators but keep runner and provider private

Option D: public library exposure of runner without provider
  expose runner orchestration only, no filesystem-capable provider

Option E: public library exposure of runner plus declared provider
  expose the first code path capable of causing one append through opt-in API

Option F: public CLI exposure for append
  highest risk in this family; not recommended for first exposure
```

The first exposure, if any, must prefer the smallest surface that satisfies the
product need. Public CLI exposure requires a separate authorization and must
not be bundled into a library exposure gate.

## Provider Exposure Boundary

If the provider is ever considered for public exposure, the public interface
must not accept a raw path as a runner-facing value.

Any public provider constructor or binding API must preserve:

```text
declared sink binding
opaque runner-facing identifiers
append_capability_root_digest binding
native_idempotency_enforced binding
no path exposure to runner output
no probe before append
no fallback write
no retry
```

A public API that accepts an arbitrary path, opens a generic filesystem writer,
or exposes `open/read/write/stat/exists/resolve/list/delete` to the runner must
stop with:

```text
PUBLIC_AUDIT_APPEND_EXPOSURE_SCOPE_REVISION_REQUIRED
```

## Mandatory Public Claim Boundary

Any future public text for this chain may state only:

```text
SPIRA contains an opt-in, class-specific AUDIT_RECORD_APPEND_ONLY path that can
evaluate and, only through a declared capability provider, attempt one bounded
audit append under recorded assumptions.
```

It must also state:

```text
the public 0.7.3 surface remains assessment and dry-run only
audit append exposure, if released later, is opt-in only
AUDIT_RECORD_APPEND_ONLY is the only action class in scope
APPEND_APPLIED is not proof of durable append truth
provider behavior is outside the Lean-proven composition core
CAP-* assumptions remain NOT_PROVEN
EA-TCB-03 remains an assumption, not a proved runner-truth property
no severance, remediation, arbitrary command, or generic filesystem action is authorized
```

Forbidden public wording:

```text
safe to write
safe to run
execution approved
permission granted
action authorized by Nesira
audit durability proven
append truth proven
idempotency proven
sink legitimacy proven
provider proven by Lean
secure filesystem runner
generic runner
arbitrary path support
automatic remediation
severance authorized
certified
audited
endorsed
third-party validated
security guarantee
trust guarantee
```

Any text that a reasonable reader could interpret as a guarantee that the sink
append happened, is durable, is safe, or is formally proven by SPIRA must stop
with:

```text
PUBLIC_AUDIT_APPEND_CLAIM_SCOPE_REVISION_REQUIRED
```

## Required Release Candidate Consequences

Any actual public exposure later would require a new release-candidate gate
because it would change the public wheel or public interface.

That gate must account for:

```text
version bump
wheel SHA change
public wheel allowlist update
pyproject decision
release notes review
public claim review
TestPyPI staging
post-install verification from the built wheel
provider source scan
runner source scan
installed-wheel negative tests with zero records for all blocked cases
installed-wheel positive test with at most one record in a controlled sink
V1 manifest narrow refresh if a V1-pinned file changes
```

No release action is authorized by this readiness gate.

## Required Tests For A Later RC

A later RC must prove at least:

```text
1. public wheel includes only the modules explicitly authorized by that RC.
2. base install posture remains intentional.
3. no public CLI exists unless separately authorized.
4. runner/provider remain opt-in and class-specific.
5. runner imports no filesystem, subprocess, socket, or network-capable modules.
6. provider uses only append-mode open plus one write to a controlled sink.
7. provider performs no stat/exists/readback/resolve/list/mkdir/delete/rename.
8. capability digest mismatch produces zero append attempts.
9. missing native durable idempotency produces UNKNOWN before write.
10. positive path writes at most one bounded record.
11. every negative case writes zero records.
12. outputs expose no path, command, runbook, or network target.
13. APPLIED carries CAP-* assumptions.
14. release notes stay inside the public claim boundary.
15. public package inspection confirms no second side-effect class is exposed.
```

If public CLI exposure is proposed, it must be a separate gate and must prove:

```text
no --execute-generic / --path / --shell / --subprocess / --network flags
no copy-paste runbook output
exit code reflects tool success or tool failure only
no default append sink
no environment-derived sink
```

## Authorized Files

This gate may create only:

```text
research/nesira_policy_profile/nesira_phase2_audit_append_public_exposure_readiness_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_public_exposure_readiness_authorization_review.md
research/nesira_policy_profile/nesira_phase2_audit_append_public_exposure_readiness_plan.md
research/nesira_policy_profile/nesira_phase2_audit_append_public_exposure_claim_draft.md
research/nesira_policy_profile/nesira_phase2_audit_append_public_exposure_readiness_review.md
```

Any source, test, pyproject, workflow, manifest, public wheel builder, version,
release, tag, or publication change must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Stop Conditions

Stop if readiness work:

```text
recommends public exposure without public claim review
collapses APPEND_APPLIED into proof
collapses Nesira sufficient into action authorization
exposes a raw path API to the runner
adds CLI exposure to a library exposure gate
adds a second side-effect class
requires code or release changes in this gate
omits CAP-TCB-01 or CAP-IDEMPOTENCY-02 from public boundary text
describes provider behavior as Lean-proven
```

## Next Step

If this authorization is accepted, draft the readiness plan and public claim
text. Implementation, RC, release, and publication remain separate future gates.
