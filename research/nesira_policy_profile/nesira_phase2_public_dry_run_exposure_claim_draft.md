# Nesira Phase 2 Public Dry-Run Exposure Claim Draft

## Status

```text
DOCUMENT_TYPE: PUBLIC CLAIM DRAFT
PUBLICATION: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

## Proposed Public Claim

SPIRA can emit a non-executing dry-run artifact that reports whether declared
preconditions are present for later human review. The dry-run artifact is
conditional on supplied evidence, declared roots, recorded assumptions, and a
separate action-authority result. It always carries `ACTION_NOT_PERFORMED`.

The dry-run artifact is not execution, not action authorization, not severance
authorization, not automatic remediation, and not permission to proceed.
`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`, `GRAPH_OK`, and
`ACTION_AUTHORITY_SUFFICIENT_FOR_CONSIDERATION` remain insufficient to execute
an action. Separate execution authorization is still required.

## Short Form

SPIRA's dry-run surface emits a JSON artifact for later human review. It reports
precondition status only, always carries `ACTION_NOT_PERFORMED`, and does not
execute, authorize, remediate, or sever.

## Boundary

This claim does not mean:

```text
ready to run
safe to run
execution approved
permission granted
action authorized
severance authorized
automatic remediation
runner behavior
proof that isolation happened
security guarantee
trust guarantee
independent certification
audit
endorsement
third-party validation
```

## Evidence Statement

External or cold reproduction, if later performed for a public release
candidate, would mean only that the recorded checks were reproduced. It would
not mean independent certification, audit, endorsement, third-party validation,
or a security or trust guarantee.

## Required Public Wording

Any future release notes or public description must preserve:

```text
dry-run is not execution
dry-run is not action authorization
ACTION_NOT_PERFORMED is always carried
separate execution authorization remains required
actual execution remains out of scope
```
