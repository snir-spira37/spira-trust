# Test/Build Failure Contract - Oracle Schema V4 Review

## Status

```text
DOMAIN_2_ORACLE_SCHEMA_V4_NEEDS_REVISION
ORACLE_SCHEMA_V4_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed schema:

```text
research/test_build_failure_contract_oracle_schema_v4.schema.json
```

Reviewed commit:

```text
3be7c7c0ad088dd734ef768c39eaf5df0cb8353b
```

## Review Scope

This review checks whether Oracle Schema V4 is ready to support oracle case
authoring.

It does not authorize:

```text
oracle population
fixture generation
corpus materialization
producer implementation
validator implementation
Gate B
release/version/tag/PyPI
```

## Accepted Fixes From V4

Oracle Schema V4 correctly closes the gaps found in the V3 review.

### Hash Recomputation Requirements

V4 requires validator checks for:

```text
SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION
RESULT_IDENTITY_HASH_MATCHES_RESULT_PROJECTION
COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST
```

This is accepted.

### Explicit List Equivalence

V4 requires:

```text
RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS
```

This is accepted.

### Bidirectional Action Stop Consistency

V4 enforces:

```text
stop:false
-> PROCEED / REPORT_WITH_NOTES

stop:true
-> STOP_BLOCKED / RERUN_REQUIRED / REPORT_NOT_EVALUATED
```

This is accepted.

## Blocking Finding 1 - Scope Projection Is Too Narrow

The accepted Dual Identity Model V2 defines collection identity under a pinned
scope. Its canonical collection manifest includes:

```text
schema
schema_version
project identity
source revision
normalized selection command
sorted unique canonical collected test IDs
Python version contract
pytest version
relevant plugin contract
collection-contract version
```

V4's `scope_identity_projection` currently contains only:

```text
collection_manifest_sha256
canonical_collected_test_ids
```

This leaves a gap between the identity model and the oracle schema.

If `collection_manifest_sha256` is intended to bind all of the missing fields,
V4 does not state that contract in the schema. If it is not intended to bind
them, the scope identity is too narrow.

Required revision:

```text
scope_identity_projection must either:

1. include a full canonical collection manifest projection with:
   schema
   schema_version
   project_identity
   source_revision
   normalized_selection_command
   canonical_collected_test_ids
   python_version_contract
   pytest_version
   relevant_plugin_contract
   collection_contract_version

or:

2. explicitly require collection_manifest_sha256 to be recomputed from a
   canonical collection manifest containing all of those fields.
```

The second option may keep the projection compact, but it must be explicit and
validator-enforced before oracle population.

## Blocking Finding 2 - Result Semantic Consistency Is Not Fully Declared

V4 restricts emitted `result_identity` to complete evidence and valid process /
result states. That is necessary but not sufficient.

The validator must also ensure internal semantic consistency, including:

```text
result_state == PASSED
-> blocking_cases is empty

process_state == TIMEOUT
-> run_level_failures contains TIMEOUT

failure_classes
-> exactly derives from blocking_cases and run_level_failures
```

Without these invariants, a syntactically valid oracle case can describe a
semantically contradictory result.

Required revision:

```text
validator_enforced_before_oracle_population must include:
  PASSED_RESULT_HAS_NO_BLOCKING_CASES
  TIMEOUT_PROCESS_HAS_TIMEOUT_RUN_LEVEL_FAILURE
  FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES
```

If any of these can be schema-enforced directly, V5 may classify them as
schema-enforced. Otherwise they must be validator-enforced before oracle
population.

## Required Next Artifact

The next artifact should be a schema revision:

```text
research/test_build_failure_contract_oracle_schema_v5.schema.json
```

It must at minimum:

```text
1. Close the scope projection gap.
2. Define whether collection_manifest_sha256 binds the full canonical manifest.
3. Add semantic consistency requirements for result_state, process_state, and
   failure_classes.
4. Keep oracle population blocked.
5. Keep validator implementation blocked unless separately authorized.
```

## Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V4_NEEDS_REVISION
ORACLE_SCHEMA_V4_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle Schema V4 is a strong improvement, but it is not accepted until scope
identity binds the full pinned collection context and result semantic
consistency is locked.
