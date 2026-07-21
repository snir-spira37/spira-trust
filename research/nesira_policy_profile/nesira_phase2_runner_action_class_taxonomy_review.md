# Nesira Phase 2 Runner Action Class Taxonomy Review

## Verdict

```text
NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_ACCEPTED
NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_V2_ACCEPTED
NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_V3_ACCEPTED
```

## Scope Reviewed

This review covers the docs-only runner action-class taxonomy.

It does not authorize runner implementation, subprocess execution, filesystem
mutation, network execution, severance, remediation, CLI changes, public wheel
exposure changes, version changes, release, or public claim expansion.

## Findings

No blocking findings.

## Version Review

The taxonomy is now explicitly versioned:

```text
TAXONOMY_ID: SPIRA_NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_V3
TAXONOMY_VERSION: 3
REVISION: authorize AUDIT_RECORD_APPEND_ONLY for one private declared sink append implementation gate
```

V2 closed the governance finding from the audit-append runner scope revision by
making the `ELIGIBLE` tier canonical. V3 now records the separate
implementation authorization for exactly one class without creating a side
status outside the taxonomy.

## Authorized Set Review

The taxonomy now records exactly one authorized class:

```text
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW = [AUDIT_RECORD_APPEND_ONLY]
```

This does not make the taxonomy itself an implementation approval. The class is
authorized only by its separate implementation authorization and only inside
that authorization's exact envelope.

## Generic Runner Rejection

The ineligible list rejects:

```text
generic shell
generic subprocess
generic script runner
generic Python module runner
generic filesystem mutator
generic network client
arbitrary command executor
arbitrary path or network target
live isolation runner
severance executor
automatic remediator
```

This is the load-bearing boundary. A runner must never become a generic
execution adapter.

## Ineligible Stability Review

The taxonomy now treats `INELIGIBLE_ALWAYS` as a stability class, not a
temporary label.

Reclassifying any ineligible action class requires:

```text
SCOPE_REVISION_REQUIRED
new taxonomy version
explicit rationale
adversarial review
human go/no-go owner approval
```

The most dangerous classes are permanently non-reclassifiable:

```text
LIVE_ISOLATION_RUNNER
SEVERANCE_EXECUTOR
AUTOMATIC_REMEDIATOR
SECRET_EXFILTRATION_PRONE_ACTION
SELF_MODIFYING_RUNNER
```

This prevents a later gate from silently turning "always ineligible" into
"candidate for discussion."

## Candidate Classes

The candidate classes are correctly marked:

```text
CANDIDATE_FOR_FUTURE_MODEL_ONLY
```

The remaining candidates are:

```text
LOCAL_STATUS_MARKER_CREATE_ONLY
MANUAL_REVIEW_PACKET_MATERIALIZE_ONLY
ROLLBACK_ABORT_SIGNAL_REQUEST_ONLY
```

They may be modeled later but are not authorized now. Each is constrained to a
specific purpose and requires a future model for roots, side-effect budget,
schema, idempotency, rollback/abort, audit, and public claim boundary.

## Eligible Tier Review

The new tier is correctly defined:

```text
ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION
```

It means only that a later gate may draft an implementation authorization for
the exact class. It does not permit code and does not move the class to
`AUTHORIZED_NOW`.

There are no currently eligible-but-not-authorized classes:

```text
none
```

## Authorized Now Review

The single authorized class is:

```text
AUDIT_RECORD_APPEND_ONLY
```

It is authorized only for private implementation under:

```text
nesira_phase2_audit_append_runner_implementation_authorization.md
```

The taxonomy records the exact maximum implementation envelope:

```text
effect_shape: APPEND_ONE_BOUNDED_RECORD
effect_count: 1
total_effect_count: 1
retry_count: 0
supporting_effects: none
sink_access: declared append capability only
```

This status does not authorize public wheel exposure, CLI exposure, release, or
any other action class.

## Canonical Table Review

The canonical classification table is now the source of truth for Phase 2
runner action-class status.

It records exactly:

```text
16 INELIGIBLE_ALWAYS classes
0 ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION classes
3 CANDIDATE_FOR_FUTURE_MODEL_ONLY classes
1 AUTHORIZED_NOW class
```

Any status not listed in the table is invalid.

## Path, Network, And Executable Content

The taxonomy rejects arbitrary paths, arbitrary network targets, and executable
content. This prevents "review packet" or "audit record" from becoming a
copy-paste runbook or command channel.

## Runner / TCB Review

The taxonomy preserves `EA-TCB-03`: the trusted verifier must compare the
human-approved context to the runner-intended context for the exact action
class. The runner cannot compute and trust its own binding.

## Next Gate

The next gate is correctly constrained to:

```text
nesira_phase2_runner_side_effect_budget_model
```

That remains docs-only and must define side-effect accounting before any
candidate class can approach implementation.

## Accepted Boundary

The taxonomy is accepted.

It opens only side-effect budget modeling. It does not open runner code or
execution.
