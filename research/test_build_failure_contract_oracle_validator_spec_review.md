# Test/Build Failure Contract Oracle Validator Spec Review

Status:

```text
DOMAIN_2_ORACLE_VALIDATOR_SPEC_ACCEPTED
VALIDATOR_SPEC_REVIEW_COMPLETE
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed artifact:

```text
research/test_build_failure_contract_oracle_validator_spec.md
```

Upstream accepted schema:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
DOMAIN_2_ORACLE_SCHEMA_V7_ACCEPTED
ORACLE_SCHEMA_V7_LOCKED
```

This is a specification review only. It does not authorize validator
implementation, oracle population, corpus materialization, producer work, Gate
B, Domain 3, or release activity.

## Review Question

The validator spec must determine whether an oracle document satisfies all
requirements that JSON Schema V7 cannot enforce by itself:

```text
hash recomputation
canonicalization checks
case-id uniqueness
related-case referential integrity
relationship symmetry
explicit-list equivalence
action/stop consistency
semantic result invariants
declared-delta validation
fail-closed statuses
machine-readable output
```

The central review risk is whether the validator can ever accept a hash-only
identity without the canonical projection bytes needed for recomputation.

## Finding 1: Hash-Only Projection Is Fail-Closed

The spec explicitly states that if the needed projection is omitted and only a
projection hash is present, the validator must not pretend to recompute omitted
bytes. It may only verify a hash against supplied canonical bytes when those
bytes are present in a reviewed field.

The accepted interpretation is:

```text
hash only without canonical projection bytes
-> PROJECTION_BYTES_NOT_AVAILABLE
-> ORACLE_VALIDATION_FAILED
-> FAIL CLOSED
```

This is sufficient for the validator spec stage. A future schema may choose to
require full projections for every `EMITTED` identity, but that is not required
to accept this validator specification because the spec already forbids passing
hash-only identities.

The validator implementation must include a negative fixture for this case:

```text
scope_identity.status == EMITTED
scope_projection omitted
scope_projection_sha256 present
no reviewed canonical projection bytes available
-> FAIL
-> PROJECTION_BYTES_NOT_AVAILABLE
```

Verdict:

```text
HASH_ONLY_IDENTITY_FAIL_CLOSED_ACCEPTED
```

## Finding 2: Hash Recompute Contract Is Sufficient

The spec defines recomputation for:

```text
scope_identity_sha256
result_identity_sha256
collection_manifest_sha256
```

It also defines explicit domain tags for scope and result identity:

```text
SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1\0
SPIRA_PYTEST_RESULT_IDENTITY_PROJECTION_V1\0
```

This prevents the validator from treating a 64-character string as sufficient
proof of identity. Identity validation requires canonical bytes, a domain tag
and recomputation.

Verdict:

```text
HASH_RECOMPUTATION_SPEC_ACCEPTED
```

## Finding 3: Canonicalization Checks Are Sufficient For Spec Review

The spec covers the V7 canonical scope contract:

```text
PROJECT_IDENTITY_CANONICALIZED
SOURCE_REVISION_CANONICALIZED
SELECTION_COMMAND_CANONICALIZED
PYTHON_VERSION_CONTRACT_CANONICALIZED
PYTEST_VERSION_CANONICALIZED
PLUGIN_CONTRACT_CANONICALIZED
SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE
```

It preserves the fail-closed posture for ambiguous repository URLs, shell
strings, unresolved environment expansion, dirty git revisions, missing plugin
versions, duplicate plugins and unknown active plugins.

The spec also forbids repairing noncanonical input after observing a mismatch.

Verdict:

```text
CANONICALIZATION_SPEC_ACCEPTED
```

## Finding 4: Cross-Case Integrity Is Sufficient

The spec defines:

```text
CASE_ID_UNIQUENESS
RELATED_CASE_ID_EXISTS
IDENTITY_RELATIONSHIP_SYMMETRY
```

It requires unique `case_id` values, rejects missing related cases and requires
reciprocal relationships. Self-reference is explicitly not authorized unless a
future reviewed spec allows it.

Verdict:

```text
CROSS_CASE_INTEGRITY_SPEC_ACCEPTED
```

## Finding 5: Strict Lists And Deltas Are Sufficient

The spec preserves the strict-list invariant:

```text
RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS
```

It requires canonical equality of explicit blocking and nonblocking lists, not
count-only agreement.

It also defines:

```text
DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY
```

and rejects broad "noise" buckets. This preserves the Domain 2 rule that only
declared, bounded deltas can explain identity relationships.

Verdict:

```text
STRICT_LIST_AND_DELTA_SPEC_ACCEPTED
```

## Finding 6: Action And Semantic Invariants Are Sufficient

The spec defines bidirectional action consistency:

```text
stop == false
  -> PROCEED / REPORT_WITH_NOTES

stop == true
  -> STOP_BLOCKED / RERUN_REQUIRED / REPORT_NOT_EVALUATED
```

It also preserves semantic result invariants:

```text
PASSED_RESULT_HAS_NO_BLOCKING_CASES
TIMEOUT_PROCESS_HAS_TIMEOUT_RUN_LEVEL_FAILURE
FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES
```

The accepted Domain 2 distinctions are kept:

```text
per-test timeout != run-level timeout
SKIPPED / XFAILED / XPASSED remain identity-bearing
```

Verdict:

```text
ACTION_AND_SEMANTIC_INVARIANTS_ACCEPTED
```

## Finding 7: Machine-Readable Output Is Sufficient

The spec requires one JSON validator result with:

```text
schema
schema_version
validator_spec
oracle_schema
verdict
status
input hash
counts
per-check results
not_authorized list
```

It separates:

```text
PASS
FAIL
TOOL_ERROR
```

and explicitly prevents converting validator tool failure into an oracle
finding, or converting oracle validation failure into a tool failure.

The review accepts the top-level fail-closed status:

```text
ORACLE_VALIDATION_FAILED
```

with check-level failure codes such as:

```text
PROJECTION_BYTES_NOT_AVAILABLE
SCOPE_IDENTITY_HASH_MISMATCH
RESULT_IDENTITY_HASH_MISMATCH
ARRAY_NOT_CANONICALLY_SORTED
RELATIONSHIP_NOT_SYMMETRIC
ACTION_STOP_INCONSISTENT
```

No separate schema change is required to introduce
`ORACLE_DOCUMENT_INSUFFICIENT`; the equivalent machine-readable condition is
captured as:

```text
status: ORACLE_VALIDATION_FAILED
check.error_code: PROJECTION_BYTES_NOT_AVAILABLE
```

Verdict:

```text
MACHINE_READABLE_OUTPUT_SPEC_ACCEPTED
```

## Required Implementation Notes

A future implementation authorization must require negative fixtures for at
least:

```text
hash-only scope projection
hash-only result projection
scope hash mismatch
result hash mismatch
collection manifest mismatch
duplicate case_id
missing related_case_id
asymmetric relationship
unsorted canonical arrays
strict-list mismatch
invalid declared delta
stop/action contradiction
passed result with blocking cases
run timeout without TIMEOUT run-level failure
failure classes not derived from cases
ambiguous repository URL
shell command string instead of argv
unknown active plugin
validator internal exception
```

These notes do not authorize implementation. They define what a later
implementation authorization must preserve.

## Final Verdict

```text
DOMAIN_2_ORACLE_VALIDATOR_SPEC_ACCEPTED
VALIDATOR_SPEC_REVIEW_COMPLETE
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

The validator specification is accepted because it defines a fail-closed path
for every V7 validator-enforced invariant and resolves the hash-only projection
risk without allowing false recomputation.

The next step is not implementation by default. A separate implementation
authorization document is still required before writing validator code.
