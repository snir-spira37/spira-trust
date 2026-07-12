# Test/Build Failure Contract - Oracle Schema V5 Review

## Status

```text
DOMAIN_2_ORACLE_SCHEMA_V5_NEEDS_REVISION
ORACLE_SCHEMA_V5_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed schema:

```text
research/test_build_failure_contract_oracle_schema_v5.schema.json
```

Reviewed commit:

```text
ea4fb71d09813f0ca6dbe297b23108a248843c21
```

## Review Scope

This review checks whether Oracle Schema V5 is ready to support oracle case
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

## Accepted Fixes From V5

Oracle Schema V5 correctly addresses the main V4 review finding by expanding
`scope_identity_projection`.

The projection now includes:

```text
project_identity
source_revision
normalized_selection_command
collection_manifest_sha256
canonical_collected_test_ids
python_version_contract
pytest_version
relevant_plugin_contract
collection_contract_version
```

V5 also carries forward validator requirements for:

```text
PASSED_RESULT_HAS_NO_BLOCKING_CASES
TIMEOUT_PROCESS_HAS_TIMEOUT_RUN_LEVEL_FAILURE
FAILURE_CLASSES_DERIVE_FROM_CASES_AND_RUN_LEVEL_FAILURES
```

These structural improvements are accepted.

## Blocking Finding - Scope Components Lack Canonicalization Contracts

V5 makes the required scope fields present, but does not define enough
canonicalization for a future validator to recompute the same `scope_identity`
deterministically.

The following fields are currently structurally constrained but not
canonically specified:

```text
project_identity.value
source_revision.value
normalized_selection_command
python_version_contract
pytest_version
relevant_plugin_contract
```

Examples of unresolved questions:

```text
repository_url:
  Are scheme and host lowercased?
  Are trailing slashes removed?
  Are .git suffixes normalized or preserved?

source_revision:
  Must git_commit be a lowercase 40-character SHA-1 / SHA-256?
  Are dirty worktrees represented only by working_tree_sha256?

normalized_selection_command:
  Is it argv-canonical JSON or a shell string?
  Are path separators normalized?
  Are redundant pytest flags normalized?
  Is argument ordering preserved or canonicalized?

python_version_contract:
  Is it major.minor, full version, implementation plus version, or ABI tag?

pytest_version:
  Is it exact package version only, or does it include plugin-resolved behavior?

relevant_plugin_contract:
  Is plugin ordering canonical?
  Are plugin names normalized?
  Are transitive pytest-affecting plugins included?
```

Without these rules, two validators could compute different canonical bytes for
the same intended test scope, or the same bytes for scopes that should differ.

Required revision:

```text
scope_identity_projection must either:

1. define canonicalization rules directly for each scope component; or

2. require a named canonical scope contract version that defines them, and
   require the validator to enforce that exact contract before oracle
   population.
```

The second path is acceptable if it is explicit, versioned, and referenced by
the schema.

## Required Additional Validator Invariants

V6 should add validator requirements for:

```text
PROJECT_IDENTITY_CANONICALIZED
SOURCE_REVISION_CANONICALIZED
SELECTION_COMMAND_CANONICALIZED
PYTHON_VERSION_CONTRACT_CANONICALIZED
PYTEST_VERSION_CANONICALIZED
PLUGIN_CONTRACT_CANONICALIZED
SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE
```

These are not producer features. They are oracle-validity invariants needed
before oracle population.

## What Is Not A Blocker

The review does not require oracle cases yet.

It also does not require implementing the validator now.

But it does require the schema to say which canonicalization contract the
future validator must enforce. Without that, oracle authoring would begin on
ambiguous identity bytes.

## Required Next Artifact

The next artifact should be a schema revision:

```text
research/test_build_failure_contract_oracle_schema_v6.schema.json
```

It must at minimum:

```text
1. Add a versioned canonical scope contract.
2. Define or reference canonicalization for project identity, source revision,
   selection command, Python version, pytest version, and plugin contract.
3. Require validator enforcement of the canonical scope contract before oracle
   population.
4. Keep oracle population blocked.
5. Keep validator implementation blocked unless separately authorized.
```

## Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V5_NEEDS_REVISION
ORACLE_SCHEMA_V5_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle Schema V5 is structurally close, but it is not accepted until the scope
projection has a deterministic canonicalization contract.
