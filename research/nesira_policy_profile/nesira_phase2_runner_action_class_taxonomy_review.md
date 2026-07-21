# Nesira Phase 2 Runner Action Class Taxonomy Review

## Verdict

```text
NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_ACCEPTED
NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_V2_ACCEPTED
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
TAXONOMY_ID: SPIRA_NESIRA_PHASE2_RUNNER_ACTION_CLASS_TAXONOMY_V2
TAXONOMY_VERSION: 2
REVISION: add ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION status for AUDIT_RECORD_APPEND_ONLY
```

This closes the governance finding from the audit-append runner scope revision:
the `ELIGIBLE` tier is now part of the canonical taxonomy, not a status created
only by a downstream document.

## Empty Authorized Set

The taxonomy correctly locks:

```text
AUTHORIZED_RUNNER_ACTION_CLASSES_NOW = []
```

This prevents the taxonomy itself from becoming an implementation approval.

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

The single eligible class is:

```text
AUDIT_RECORD_APPEND_ONLY
```

The taxonomy records the same maximum future envelope as the runner scope
revision:

```text
effect_shape: APPEND_ONE_BOUNDED_RECORD
effect_count: 1
total_effect_count: 1
retry_count: 0
supporting_effects: none
```

The status is now centralized in the taxonomy.

## Canonical Table Review

The canonical classification table is now the source of truth for Phase 2
runner action-class status.

It records exactly:

```text
16 INELIGIBLE_ALWAYS classes
1 ELIGIBLE_FOR_SEPARATE_IMPLEMENTATION_AUTHORIZATION class
3 CANDIDATE_FOR_FUTURE_MODEL_ONLY classes
0 AUTHORIZED_NOW classes
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
