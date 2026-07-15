# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Specification Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_SPEC_ACCEPTED
SPECIFICATION_ONLY
RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO
DOMAIN_2_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_AUTHORIZATION_REQUIRED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 2 raw adapter conformance specification is accepted.

It is accepted as a specification only. It does not prove raw parser correctness and does not authorize adapter implementation changes.

## Accepted Boundary

The accepted chain remains:

```text
raw pytest/JUnit evidence
-> tested/untrusted Domain 2 adapter
-> typed evidence
-> Formal Core V1
-> authoritative machine contract
```

Formal Core V1 is already accepted at the typed-evidence boundary. This review defines what the Domain 2 adapter must preserve before that boundary:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence references
proof references
scope identity
result identity
collection identity
```

## Required Fail-Closed Behavior

The specification correctly requires `PROCEED` to be forbidden for:

```text
blocking test failure
collection or run-level error
unknown required information
malformed required evidence
conflicting required evidence
unsupported required format
internal adapter failure
```

The accepted nonblocking-note mapping remains narrow:

```text
REPORT_WITH_NOTES -> PROCEED + TEST_NOTES
```

It may not be used to hide blockers, unknowns, malformed evidence, or conflicts.

## Next Step

The next deterministic step should be:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE_AUTHORIZATION
```

That step should materialize fixtures with known expected typed-evidence and Formal Core contracts. It should still not modify the adapter implementation.

## Not Authorized

```text
raw parser proof claim
Domain 2 adapter implementation changes
Lean changes
proof script changes
MVP / passthrough changes
live agent sessions
benchmark execution
result reclassification
production claim
release
```
