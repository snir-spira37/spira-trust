# Test/Build Failure Contract Identity Model Question

## Status

```text
DOMAIN_2_IDENTITY_MODEL_OPEN_DESIGN_QUESTION
NO_IDENTITY_MODEL_CHANGE_AUTHORIZED
DOMAIN_2_PRODUCER_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
```

## Background

The Test/Build Failure Contract methodology is already locked:

```text
research/test_build_failure_contract_methodology.md
```

This note does not amend that methodology.

It records an open identity-model question surfaced by Gate A:

```text
Should a pytest test run be identified only by its exact contextual evidence,
or should Domain 2 also define a separate semantic result identity?
```

## Current Rule

The existing `unification_id` remains contextual.

It binds:

```text
subject
typed claims
decision/action
policy/context roots
decision semantics
```

It must not be silently redefined as a semantic-only result ID.

## Candidate Identity Concepts

### Contextual Run Identity

This identity would bind exact run evidence and context:

```text
console bytes
JUnit/XML or structured test output bytes
command
environment
timestamps or run context
source hashes
policy/context roots
```

This is closest to the current `unification_id` model.

It answers:

```text
Was this exact evidence context used to produce this action?
```

### Semantic Result Identity

This identity would bind normalized policy-relevant facts:

```text
normalized failed test IDs
failure classes
counts
decision/action
reason codes
other policy-relevant normalized facts
```

It would answer a different question:

```text
Did these normalized test/build facts produce this action?
```

If this identity is needed, it must be a separate field with a separate schema
and review. It must not be implemented by changing the meaning of
`unification_id`.

## Guardrails

No Domain 2 implementation may:

```text
add semantic identity silently
change the meaning of unification_id
normalize timestamps after seeing corpus results
normalize paths after seeing corpus results
normalize output ordering after seeing corpus results
hide contextual drift
use semantic sameness to overwrite contextual identity
```

If a semantic result identity is introduced later, it must be:

```text
explicit
versioned
documented
tested against an oracle
reported separately from contextual unification identity
```

## Required Future Decision

Before Domain 2 producer implementation, a separate design decision must choose
one of:

```text
DOMAIN_2_CONTEXTUAL_IDENTITY_ONLY
DOMAIN_2_CONTEXTUAL_PLUS_SEMANTIC_RESULT_IDENTITY
DOMAIN_2_IDENTITY_MODEL_NEEDS_REVISION
```

Until that decision exists:

```text
Domain 2 producer remains blocked
oracle population remains blocked
corpus materialization remains blocked
```

## Not Authorized

This note does not authorize:

```text
Domain 2 producer
pytest adapter
oracle population
corpus materialization
semantic identity field
unification_id semantics change
Gate B
release/version/tag/PyPI
```

## Verdict

```text
DOMAIN_2_IDENTITY_MODEL_OPEN_DESIGN_QUESTION
NO_IDENTITY_MODEL_CHANGE_AUTHORIZED
DOMAIN_2_PRODUCER_NOT_AUTHORIZED
```

The identity-model question is recorded, unresolved, and must be decided before
Domain 2 producer implementation.
