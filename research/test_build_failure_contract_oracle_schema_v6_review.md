# Test/Build Failure Contract - Oracle Schema V6 Review

## Status

```text
DOMAIN_2_ORACLE_SCHEMA_V6_NEEDS_REVISION
ORACLE_SCHEMA_V6_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed schema:

```text
research/test_build_failure_contract_oracle_schema_v6.schema.json
```

Reviewed commit:

```text
f33b7075f2afc858740b5cd14e1f7b1ac0070907
```

## Review Scope

This review checks whether Oracle Schema V6 is ready to support oracle case
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

## Accepted Improvements From V6

V6 correctly introduces a named canonicalization contract:

```text
SPIRA_PYTEST_SCOPE_CANONICALIZATION_V1
```

The schema now explicitly describes canonicalization for:

```text
project_identity
source_revision
normalized_selection_command
python_version_contract
pytest_version
relevant_plugin_contract
scope_projection_hash
```

It also requires validator enforcement for:

```text
PROJECT_IDENTITY_CANONICALIZED
SOURCE_REVISION_CANONICALIZED
SELECTION_COMMAND_CANONICALIZED
PYTHON_VERSION_CONTRACT_CANONICALIZED
PYTEST_VERSION_CANONICALIZED
PLUGIN_CONTRACT_CANONICALIZED
SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE
```

These are the right categories.

## Blocking Finding 1 - Selection Command Contract Conflicts With Projection Shape

The canonicalization contract says:

```text
accepted_form: canonical argv JSON array
```

But `scope_identity_projection.normalized_selection_command` is currently:

```json
{
  "type": "string",
  "minLength": 1
}
```

This is ambiguous. A future oracle could store either:

```text
pytest -q tests
```

or:

```text
["pytest","-q","tests"]
```

inside a string field. Two validators could then disagree about whether the
field is already canonical or still needs parsing.

Required revision:

```text
normalized_selection_command must be a structured canonical argv array
```

or the field must be renamed to make clear that it is:

```text
normalized_selection_command_json
```

with an explicit rule that the string is canonical JSON bytes. The structured
array is preferred because it is less ambiguous.

## Blocking Finding 2 - URL Canonicalization Still Leaves Edge Cases Open

The project identity rule says repository URLs:

```text
lowercase scheme and host
remove a single trailing slash
preserve explicit .git suffix
```

It does not state how to handle:

```text
default ports
query strings
fragments
percent-encoding
user-info
case-sensitive path segments
multiple trailing slashes
SSH shorthand forms
```

Required revision:

```text
repository_url canonicalization must either define each of these cases or
fail closed on them.
```

The simplest acceptable rule is:

```text
Only absolute https URLs with no user-info, no query, no fragment, no default
port, no percent-encoded ambiguity, and a normalized single-slash path are
accepted. All other forms fail closed.
```

## Blocking Finding 3 - Version And Plugin Canonicalization Need Machine-Level Shape

The contract describes Python, pytest, and plugin versions in prose. The
projection still stores:

```text
python_version_contract: string
pytest_version: string
relevant_plugin_contract: [{ name, version }]
```

This may be enough for human review, but not yet for independent validators.

Required revision:

```text
python_version_contract should be structured:
  implementation
  version
  abi_tag or explicit none

pytest_version should use an exact normalized version field.

relevant_plugin_contract should define:
  normalized_name
  version
  source or distribution identity when needed
```

If the schema keeps string fields, it must add exact regex or canonical grammar
references for each string.

## Not A Blocker

It is acceptable that many checks remain validator-enforced rather than
JSON-Schema-enforced.

The problem is not that V6 delegates to a validator. The problem is that some
validator inputs are still not shaped or forbidden precisely enough for two
independent validators to recompute the same bytes.

## Required Next Artifact

The next artifact should be:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
```

It must at minimum:

```text
1. Replace normalized_selection_command string with a canonical argv structure,
   or define a precise canonical JSON string contract.
2. Close repository URL edge cases by normalization rules or fail-closed rules.
3. Give Python, pytest, and plugin version fields machine-level canonical
   shapes or exact grammars.
4. Keep oracle population blocked.
5. Keep validator implementation blocked unless separately authorized.
```

## Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V6_NEEDS_REVISION
ORACLE_SCHEMA_V6_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle Schema V6 adds the right canonicalization layer, but it is not accepted
until the canonical scope fields have machine-level shapes precise enough for
independent validator recomputation.
