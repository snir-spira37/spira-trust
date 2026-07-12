# Test/Build Failure Contract Oracle Validator Specification

Status:

```text
DOMAIN_2_ORACLE_VALIDATOR_SPEC_LOCKED
VALIDATOR_SPECIFICATION_ONLY
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Upstream accepted schema:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
ORACLE_SCHEMA_V7_LOCKED
DOMAIN_2_ORACLE_SCHEMA_V7_ACCEPTED
```

This document defines the required behavior of a future Domain 2 oracle
validator. It does not implement the validator, authorize oracle population,
materialize a corpus, implement a producer, or change SPIRA core behavior.

## Purpose

Oracle Schema V7 defines the shape of a Domain 2 oracle case. Several required
properties cannot be proven by JSON Schema alone:

```text
hash recomputation
canonicalization
cross-case references
relationship symmetry
canonical sorting
semantic consistency
declared-delta validity
```

The validator exists to fail closed before any oracle case can be accepted into
the Domain 2 corpus.

The validator must answer one narrow question:

```text
Does this oracle document satisfy the accepted V7 schema and every
validator-enforced invariant required before oracle population?
```

It must not answer:

```text
Does the future producer work?
Does SPIRA correctly parse pytest output?
Is the tested project safe?
May Domain 2 proceed to corpus materialization?
May Gate B begin?
```

## Inputs

The validator accepts exactly one candidate oracle document at a time:

```text
SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
```

The input must be bytes read from a local file. The validator must not fetch
remote resources, infer missing data from the filesystem, run pytest, inspect a
git repository, or consult package indexes.

All evidence needed to validate the oracle document must already be present in
the document itself, except for local schema files explicitly supplied to the
validator.

## Required Processing Order

The validator must run checks in this order:

```text
1. Parse JSON bytes.
2. Validate against Oracle Schema V7.
3. Validate document-level uniqueness and references.
4. Validate canonicalization of scope fields.
5. Recompute identity hashes.
6. Validate explicit-list equivalence.
7. Validate relationship symmetry.
8. Validate declared deltas.
9. Validate policy/action consistency.
10. Validate semantic result invariants.
11. Emit a machine-readable validator result.
```

The implementation may continue collecting errors after the first failure, but
the final verdict must be fail-closed if any required check fails.

## Canonical JSON Contract

All validator recomputation uses the same canonical JSON contract:

```text
encoding: UTF-8
object keys: sorted lexicographically
whitespace: none beyond canonical separators
arrays: schema-defined order
set-like arrays: sorted and unique before hashing when the schema declares
                 them canonical sets
hash algorithm: SHA-256
hash format: lowercase 64-character hexadecimal
```

The validator must not normalize fields after seeing a mismatch. It must either
prove that the field is already canonical or fail closed.

## Hash Domain Tags

The validator must use explicit domain tags when recomputing identity hashes.

Required domain tag:

```text
SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1\0
SPIRA_PYTEST_RESULT_IDENTITY_PROJECTION_V1\0
```

Scope identity recomputation:

```text
scope_identity_sha256 =
SHA256("SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1\0"
       + UTF8(canonical_json(scope_identity_projection)))
```

Result identity recomputation must use the result identity domain tag declared
by this validator specification:

```text
result_identity_sha256 =
SHA256("SPIRA_PYTEST_RESULT_IDENTITY_PROJECTION_V1\0"
       + UTF8(canonical_json(result_identity_projection)))
```

Collection manifest recomputation must use the collection manifest contract
declared by:

```text
SPIRA_PYTEST_COLLECTION_MANIFEST_V1
```

## Schema Validation

The validator must first validate the candidate document against:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
```

If JSON parsing fails or schema validation fails:

```text
verdict: FAIL
status: ORACLE_VALIDATION_FAILED
failing_check: JSON_PARSE or JSON_SCHEMA_V7_VALIDATION
```

No downstream identity or semantic check may upgrade a schema-invalid document
to pass.

## Case Identity Checks

The validator must enforce:

```text
CASE_ID_UNIQUENESS
RELATED_CASE_ID_EXISTS
```

Rules:

```text
case_id values must be unique within the oracle document
every related_case_id must point to an existing case_id in the same document
self-references are invalid unless explicitly allowed by a future reviewed spec
missing related cases fail closed
```

Failure codes:

```text
DUPLICATE_CASE_ID
RELATED_CASE_MISSING
SELF_RELATION_NOT_AUTHORIZED
```

## Canonical Array Sorting

The validator must enforce:

```text
CANONICAL_ARRAY_SORTING
```

The following arrays must be canonical:

```text
canonical_collected_test_ids
blocking_cases
nonblocking_cases
failure_classes
run_level_failures
reason_codes
relevant_plugin_contract
declared_input_deltas
identity relationships where ordering is not semantically meaningful
```

Sorting rules:

```text
strings: lexicographic by Unicode code point over the JSON string value
explicit cases: by stable case identity, then outcome/status fields, then
                canonical JSON bytes as tie-breaker
plugins: normalized_name, distribution_identity, version
deltas: source_id, delta_type, canonical JSON bytes
```

Any duplicate in a set-like array is invalid. Any unsorted set-like array is
invalid.

Failure codes:

```text
ARRAY_NOT_CANONICALLY_SORTED
DUPLICATE_SET_MEMBER
PLUGIN_LIST_NOT_CANONICAL
```

## Scope Canonicalization Checks

The validator must enforce:

```text
PROJECT_IDENTITY_CANONICALIZED
SOURCE_REVISION_CANONICALIZED
SELECTION_COMMAND_CANONICALIZED
PYTHON_VERSION_CONTRACT_CANONICALIZED
PYTEST_VERSION_CANONICALIZED
PLUGIN_CONTRACT_CANONICALIZED
SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE
```

### Project Identity

Accepted forms:

```text
repository_url
package_name
project_hash
```

`repository_url` must be an already-canonical HTTPS absolute URL:

```text
lowercase scheme
lowercase host
no user-info
no query
no fragment
no default port
no percent-encoded ambiguity
normalized single-slash path
explicit .git suffix preserved if present
SSH shorthand invalid
relative URL invalid
```

The validator must not repair URL casing, ports, repeated slashes, user-info,
queries, fragments, SSH shorthand, percent-encoded path ambiguity, or trailing
slash ambiguity. Ambiguous input fails closed.

`package_name` must already be in its canonical normalized form. `project_hash`
must be lowercase SHA-256.

Failure codes:

```text
PROJECT_IDENTITY_NOT_CANONICAL
REPOSITORY_URL_NOT_CANONICAL
PROJECT_HASH_INVALID
```

### Source Revision

Accepted forms:

```text
git_commit
source_archive_sha256
working_tree_sha256
```

Rules:

```text
git_commit must be lowercase 40- or 64-character hexadecimal
source_archive_sha256 must be lowercase SHA-256
working_tree_sha256 must be lowercase SHA-256
dirty worktrees must use working_tree_sha256, not git_commit alone
branch names and tags are invalid unless already resolved to a digest
```

Failure codes:

```text
SOURCE_REVISION_NOT_CANONICAL
DIRTY_TREE_WITH_GIT_COMMIT_ONLY
SOURCE_REVISION_DIGEST_INVALID
```

### Selection Command

`normalized_selection_command` must be structured argv:

```json
["pytest", "-q", "tests"]
```

Rules:

```text
shell strings are invalid
argument boundaries are preserved exactly
argv order is preserved
absolute private paths are invalid
unresolved environment expansion is invalid
path separators in project-relative paths use forward slash
```

The validator may only treat option groups as order-insensitive if the option
group is explicitly listed in the implementation's reviewed allowlist. Unknown
option reordering fails closed.

Failure codes:

```text
SELECTION_COMMAND_NOT_CANONICAL
SHELL_COMMAND_STRING_NOT_ALLOWED
PRIVATE_ABSOLUTE_PATH_NOT_ALLOWED
UNKNOWN_ORDER_INSENSITIVE_OPTION
UNRESOLVED_ENVIRONMENT_EXPANSION
```

### Python, Pytest And Plugins

Python contract:

```text
implementation: cpython or pypy
version: exact normalized full version
abi_tag: explicit string or null
```

Pytest contract:

```text
package: pytest
version: exact normalized installed distribution version
```

Plugin contract:

```text
normalized_name: PEP 503 normalized name
version: exact installed distribution version
distribution_identity: PEP 503 normalized distribution identity
order: normalized_name, distribution_identity, version
duplicates: invalid
unknown active pytest-affecting plugin: invalid
```

Failure codes:

```text
PYTHON_VERSION_CONTRACT_NOT_CANONICAL
PYTEST_VERSION_NOT_CANONICAL
PLUGIN_CONTRACT_NOT_CANONICAL
PLUGIN_DUPLICATE
PLUGIN_LIST_UNSORTED
UNKNOWN_ACTIVE_PLUGIN
```

## Identity Recompute Checks

The validator must enforce:

```text
SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION
RESULT_SCOPE_IDENTITY_HASH_MATCHES_EXPECTED_SCOPE
RESULT_IDENTITY_HASH_MATCHES_RESULT_PROJECTION
COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST
```

Rules:

```text
If scope_identity.status == EMITTED:
  recompute scope_identity_sha256 from scope_projection.
  compare to expected_scope_identity.scope_identity_sha256.

If result_identity.status == EMITTED:
  require expected_scope_identity.status == EMITTED.
  require result_identity.projection.scope_identity_sha256 to equal the
  expected scope_identity_sha256.
  recompute result_identity_sha256 from result projection.

If collection_manifest_sha256 is present:
  recompute it from the canonical collected-test manifest contract.
```

If the needed projection is omitted and only a projection hash is present, the
validator may not pretend to recompute the omitted bytes. It may only verify
the hash against supplied canonical bytes if those bytes are present in a
reviewed field. Otherwise the document is not sufficient for oracle population.

Failure codes:

```text
SCOPE_IDENTITY_HASH_MISMATCH
RESULT_SCOPE_IDENTITY_MISMATCH
RESULT_IDENTITY_HASH_MISMATCH
COLLECTION_MANIFEST_HASH_MISMATCH
PROJECTION_BYTES_NOT_AVAILABLE
```

## Explicit-List Equivalence

The validator must enforce:

```text
RESULT_PROJECTION_EXPLICIT_LISTS_MATCH_EXPECTED_LISTS
```

Rules:

```text
result_identity.projection.blocking_cases
  == expected_explicit_lists.blocking_cases

result_identity.projection.nonblocking_cases
  == expected_explicit_lists.nonblocking_cases
```

The equality is equality of canonical JSON values after applying the required
canonical sorting rules. Count-only agreement is not sufficient.

Failure codes:

```text
BLOCKING_LIST_MISMATCH
NONBLOCKING_LIST_MISMATCH
STRICT_LIST_CONTRACT_VIOLATION
```

## Relationship Symmetry

The validator must enforce:

```text
IDENTITY_RELATIONSHIP_SYMMETRY
```

Rules:

```text
If case A declares a relationship to case B, case B must declare the reciprocal
relationship to case A.

SAME is reciprocal with SAME.
DIFFERENT is reciprocal with DIFFERENT.
NOT_EMITTED is reciprocal with NOT_EMITTED unless a future reviewed spec
defines an asymmetric relation.
```

All declared relationships must be consistent across:

```text
run_identity_relation
scope_identity_relation
result_identity_relation
declared_input_deltas
```

Failure codes:

```text
RELATIONSHIP_NOT_SYMMETRIC
RELATIONSHIP_CONFLICT
DECLARED_DELTA_RELATIONSHIP_MISMATCH
```

## Declared-Delta Validation

The validator must enforce:

```text
DECLARED_DELTA_SEMANTIC_FIELD_VALIDITY
```

Rules:

```text
Each declared delta must point to a known source_id.
delta_type must be one of the schema-defined values.
description must be non-empty.
forbidden_semantic_fields must name only fields that the identity model allows
to vary for that delta type.
Declared deltas cannot excuse changes to policy-independent result fields
unless the delta type explicitly names that semantic field.
The word noise, or any equivalent broad bucket, is not a valid delta type.
```

Failure codes:

```text
DECLARED_DELTA_UNKNOWN_SOURCE
DECLARED_DELTA_INVALID_FIELD
DECLARED_DELTA_TOO_BROAD
DECLARED_DELTA_CONTRADICTS_RELATIONSHIP
```

## Policy Action Checks

The validator must enforce:

```text
ACTION_STOP_CONSISTENCY
```

Rules:

```text
stop == false
  -> recommended_agent_action in [PROCEED, REPORT_WITH_NOTES]

stop == true
  -> recommended_agent_action in
     [STOP_BLOCKED, RERUN_REQUIRED, REPORT_NOT_EVALUATED]

decision_semantics_version must be SPIRA_DECISION_SEMANTICS_V2.
ASK_HUMAN is not a Domain 2 oracle action.
```

Failure codes:

```text
ACTION_STOP_INCONSISTENT
DECISION_SEMANTICS_VERSION_INVALID
ASK_HUMAN_NOT_AUTHORIZED
```

## Semantic Result Invariants

The validator must enforce:

```text
PASSED_RESULT_HAS_NO_BLOCKING_CASES
TIMEOUT_PROCESS_HAS_TIMEOUT_RUN_LEVEL_FAILURE
FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES
```

Rules:

```text
If result_state == PASSED:
  blocking_cases must be empty.

If process_state == TIMEOUT:
  run_level_failures must include TIMEOUT.

failure_classes must be derived exactly from blocking_cases,
nonblocking_cases, and run_level_failures.
```

The validator must also preserve the accepted distinction:

```text
per-test timeout != run-level timeout
SKIPPED / XFAILED / XPASSED remain identity-bearing
```

Failure codes:

```text
PASSED_RESULT_HAS_BLOCKING_CASES
TIMEOUT_PROCESS_MISSING_TIMEOUT_FAILURE
FAILURE_CLASSES_NOT_DERIVED
TEST_TIMEOUT_RUN_TIMEOUT_CONFUSED
IDENTITY_BEARING_TEST_OUTCOME_DROPPED
```

## Not Evaluated And Fail-Closed Rules

The validator must preserve the schema-level fail-closed rules:

```text
NOT_EVALUATED result identity has no hash
NOT_EVALUATED result identity has no projection
NOT_EVALUATED scope identity has no collection hash
NOT_EVALUATED scope identity has no collected test IDs
NOT_EVALUATED scope identity implies NOT_EVALUATED result identity
EMITTED result identity requires COMPLETE evidence
EMITTED result identity rejects NOT_EVALUATED / CONFLICTING / UNSUPPORTED states
```

Any contradiction in these rules is a validator failure even if the document
appears otherwise well formed.

Failure codes:

```text
NOT_EVALUATED_IDENTITY_HAS_HASH
NOT_EVALUATED_IDENTITY_HAS_PROJECTION
NOT_EVALUATED_SCOPE_HAS_COLLECTION_IDENTITY
SCOPE_NOT_EVALUATED_RESULT_EMITTED
EMITTED_IDENTITY_WITH_INCOMPLETE_EVIDENCE
EMITTED_IDENTITY_WITH_INVALID_STATE
```

## Machine-Readable Output Schema

The validator must emit one JSON object with this shape:

```json
{
  "schema": "SPIRA_DOMAIN2_ORACLE_VALIDATOR_RESULT",
  "schema_version": 1,
  "validator_spec": "SPIRA_DOMAIN2_ORACLE_VALIDATOR_SPEC_V1",
  "oracle_schema": "SPIRA_TEST_BUILD_FAILURE_ORACLE_V7",
  "verdict": "PASS",
  "status": "ORACLE_VALIDATION_PASS",
  "checked_at": "ISO-8601 timestamp",
  "input": {
    "path": "relative or redacted path",
    "sha256": "lowercase 64-character sha256"
  },
  "counts": {
    "case_count": 0,
    "relationship_count": 0,
    "declared_delta_count": 0,
    "error_count": 0,
    "warning_count": 0
  },
  "checks": [
    {
      "check_id": "JSON_SCHEMA_V7_VALIDATION",
      "status": "PASS",
      "error_code": null,
      "case_id": null,
      "details": {}
    }
  ],
  "not_authorized": [
    "ORACLE_POPULATION",
    "VALIDATOR_IMPLEMENTATION_BEYOND_THIS_SPEC",
    "CORPUS_MATERIALIZATION",
    "PRODUCER_IMPLEMENTATION",
    "GATE_B",
    "DOMAIN_3"
  ]
}
```

Allowed `verdict` values:

```text
PASS
FAIL
TOOL_ERROR
```

Allowed `check.status` values:

```text
PASS
FAIL
NOT_RUN
TOOL_ERROR
```

`PASS` is allowed only when every required check is `PASS`.

`FAIL` means the oracle document failed validation.

`TOOL_ERROR` means the validator could not complete its own work. It must not
be converted into `PASS`, and it must not be treated as a package or test
finding.

Paths in output must be relative, redacted, or explicitly safe for publication.
Secrets and absolute private paths must not appear in validator output.

## Required Stop Conditions

The validator must stop with fail-closed output if any of these occur:

```text
JSON parse failure
V7 schema validation failure
unsupported schema version
missing required projection bytes
unknown canonicalization contract
unknown hash domain tag
unknown active plugin in the scope contract
ambiguous repository URL
ambiguous selection command
case ID conflict
missing related case
hash recomputation mismatch
strict-list mismatch
relationship asymmetry
semantic invariant violation
validator internal exception
```

Stop status:

```text
ORACLE_VALIDATION_FAILED
```

or, for validator internal failures:

```text
ORACLE_VALIDATOR_TOOL_ERROR
```

## Forbidden Behavior

The validator must not:

```text
populate oracle cases
modify oracle cases
repair noncanonical input
infer missing data from the workspace
run pytest
materialize a corpus
build a producer
generalize Gate B status/cache/rerun behavior
change action enums
change claim status enums
change decision semantics
change the accepted Oracle Schema V7
change the policy-independent result identity model
emit broad noise buckets
hide TOOL_ERROR as a validation failure
hide validation failure as TOOL_ERROR
```

## Acceptance Criteria For A Future Implementation

A future implementation can be reviewed only if it demonstrates:

```text
all V7 schema-valid positive fixtures pass
each validator-required invariant has at least one negative fixture
each failure emits the expected machine-readable error code
hash recomputation fixtures cover scope, result, and collection identities
cross-case fixtures cover missing references and asymmetric relationships
canonicalization fixtures cover URL, argv, Python, pytest, and plugins
semantic fixtures cover passed, failed, error, per-test timeout, run timeout,
SKIPPED, XFAILED, and XPASSED
tool-error behavior is tested separately from validation failure
privacy/path/secret scans pass
```

The implementation review must not accept a validator that only checks JSON
Schema and skips validator-enforced invariants.

## Next Authorized Step

The next document may be:

```text
research/test_build_failure_contract_oracle_validator_spec_review.md
```

with one of:

```text
DOMAIN_2_ORACLE_VALIDATOR_SPEC_ACCEPTED
DOMAIN_2_ORACLE_VALIDATOR_SPEC_NEEDS_REVISION
DOMAIN_2_ORACLE_VALIDATOR_SPEC_REJECTED
```

Until that review is complete:

```text
validator implementation: NOT AUTHORIZED
oracle population: NOT AUTHORIZED
corpus materialization: NOT AUTHORIZED
producer implementation: NOT AUTHORIZED
Gate B: NOT AUTHORIZED
Domain 3: NOT AUTHORIZED
```

Even if the validator specification is accepted, implementation still requires
a separate authorization artifact.
