# SPIRA Formal Core V1 Differential Harness Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_NEEDS_REVISION
PYTHON_TYPED_EVIDENCE_ENTRYPOINT_NOT_ACCEPTED
DOMAIN_CONFORMANCE_NOT_AUTHORIZED
RUNTIME_INTEGRATION_NOT_AUTHORIZED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The differential harness phase needs revision before semantic comparison can run.

The Lean executable reference exists, but the repository does not yet expose an accepted Python
typed-evidence entrypoint matching the Formal Core V1 protocol.

Creating a new Python decision core inside this phase would violate the protocol. The correct
next step is a separate authorization to define or expose a Python typed-evidence boundary,
or to amend the differential harness scope.

## Preserved Boundaries

```text
Python source changes: 0
domain adapter changes: 0
benchmark changes: 0
result reclassification: 0
```

## Required Next Step

```text
SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_AUTHORIZATION_REQUIRED
```
