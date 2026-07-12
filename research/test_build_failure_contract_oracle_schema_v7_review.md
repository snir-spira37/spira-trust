# Test/Build Failure Contract Oracle Schema V7 Review

Status:

```text
DOMAIN_2_ORACLE_SCHEMA_V7_ACCEPTED
ORACLE_SCHEMA_V7_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed artifact:

```text
research/test_build_failure_contract_oracle_schema_v7.schema.json
```

Reviewed schema status:

```text
ORACLE_SCHEMA_V7_LOCKED
SPIRA_TEST_BUILD_FAILURE_ORACLE_V7
SPIRA_PYTEST_SCOPE_CANONICALIZATION_V1
```

This is a schema review only. It does not authorize oracle case population,
validator implementation, corpus materialization, producer implementation,
Gate B, Domain 3, or release activity.

## Review Question

The V6 review found that the oracle schema was structurally close but still
not mechanically canonical enough for independent validators to compute the
same scope bytes and the same `scope_identity`.

V7 was required to address three blockers:

```text
1. Replace normalized_selection_command string with structured canonical argv.
2. Close repository URL ambiguity with explicit fail-closed rules.
3. Replace prose-level Python / pytest / plugin identities with machine-level
   canonical shapes.
```

This review asks whether V7 closes those blockers without weakening the
invariants accepted in V1 through V6.

## Finding 1: Structured Argv Is Accepted

V7 changes `scope_identity_projection.normalized_selection_command` from an
opaque string to an array of strings:

```json
["pytest", "-q", "tests"]
```

The scope canonicalization contract now states:

```text
shell strings are forbidden
argv is represented as an array of strings
argument order is preserved except for explicitly order-insensitive option
groups defined by the validator contract
```

This closes the V6 ambiguity where two validators could parse the same shell
string differently, or where quoting and shell expansion could change argument
boundaries.

The remaining ordering rules are correctly assigned to the validator, because
JSON Schema can enforce the array shape but cannot prove semantic equivalence
of command-line option groups.

Verdict:

```text
STRUCTURED_ARGV_ACCEPTED
```

## Finding 2: Repository URL Contract Is Accepted

V7 keeps `project_identity.kind` explicit and, for `repository_url`, requires
an HTTPS absolute URL shape while the canonicalization contract defines the
closed normalization and fail-closed boundary:

```text
lowercase scheme and host
no user-info
no query
no fragment
no default port
no percent-encoded ambiguity
normalized single-slash path
preserved explicit .git suffix
SSH shorthand invalid
relative or unauthenticated forms invalid
```

This is sufficient for the oracle schema stage. The schema constrains the
field shape, and the validator requirements explicitly require:

```text
PROJECT_IDENTITY_CANONICALIZED
SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE
```

Therefore noncanonical repository forms are not silently repaired by the
oracle contract; they must fail closed before oracle population.

Verdict:

```text
REPOSITORY_URL_CANONICALIZATION_ACCEPTED
```

## Finding 3: Runtime And Plugin Shapes Are Accepted

V7 replaces prose-level runtime identity with structured fields:

```json
{
  "python_version_contract": {
    "implementation": "cpython",
    "version": "3.12.4",
    "abi_tag": "cp312"
  },
  "pytest_version": {
    "package": "pytest",
    "version": "8.3.2"
  },
  "relevant_plugin_contract": [
    {
      "normalized_name": "pytest-timeout",
      "version": "2.3.1",
      "distribution_identity": "pytest-timeout"
    }
  ]
}
```

The corresponding validator requirements are explicit:

```text
PYTHON_VERSION_CONTRACT_CANONICALIZED
PYTEST_VERSION_CANONICALIZED
PLUGIN_CONTRACT_CANONICALIZED
CANONICAL_ARRAY_SORTING
```

This gives the future validator a deterministic shape for runtime identity and
plugin identity. Missing plugin versions, duplicate plugin identities and
unsorted plugin lists remain fail-closed validation concerns before oracle
population.

Verdict:

```text
RUNTIME_AND_PLUGIN_SHAPES_ACCEPTED
```

## Finding 4: Scope Identity Recomputability Is Accepted

V7 preserves the domain-tagged scope identity contract:

```text
scope_identity_sha256 =
SHA256("SPIRA_PYTEST_SCOPE_IDENTITY_PROJECTION_V1\0"
       + UTF8(canonical_json(scope_identity_projection)))
```

The schema also requires the validator to enforce:

```text
SCOPE_IDENTITY_HASH_MATCHES_SCOPE_PROJECTION
RESULT_SCOPE_IDENTITY_HASH_MATCHES_EXPECTED_SCOPE
SCOPE_PROJECTION_CANONICAL_BYTES_RECOMPUTE
COLLECTION_MANIFEST_HASH_MATCHES_CANONICAL_MANIFEST
```

This is the right separation. JSON Schema ensures the expected structure is
present; the validator must recompute canonical bytes and hashes before any
oracle case can be accepted.

Verdict:

```text
SCOPE_IDENTITY_RECOMPUTABILITY_ACCEPTED
```

## Finding 5: V1 Through V6 Invariants Remain Preserved

V7 does not weaken the previously accepted constraints:

```text
run_identity remains contextual
result_identity remains policy-independent
policy/action binding remains outside result_identity
NOT_EVALUATED identities cannot carry hashes or projections
scope NOT_EVALUATED implies result_identity NOT_EVALUATED
EMITTED result_identity requires complete evidence
explicit lists must match result projection lists
hashes must be recomputed by the validator
PASSED cannot carry blocking cases
TIMEOUT process state must carry timeout run-level failure
failure classes derive from cases and run-level failures
ACTION_STOP_CONSISTENCY is bidirectional
ASK_HUMAN is not introduced for Domain 2 oracle actions
```

The schema still separates JSON Schema-enforced invariants from
validator-enforced invariants. This is acceptable because several of the
remaining checks are cross-record, ordering or recomputation checks that JSON
Schema cannot express fully.

Verdict:

```text
PRIOR_INVARIANTS_PRESERVED
```

## Accepted Boundary

This review accepts Oracle Schema V7 as the schema contract for the Domain 2
oracle design stage.

It does not authorize:

```text
oracle population
validator implementation
corpus materialization
producer implementation
pytest adapter implementation
Gate B work
Domain 3 work
release, version bump, tag, or PyPI publication
```

Before oracle cases can be populated, a separately authorized validator path
must exist for every validator-enforced invariant listed by V7.

## Final Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V7_ACCEPTED
ORACLE_SCHEMA_V7_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

V7 is accepted because it gives the Domain 2 oracle a mechanically canonical
scope model: structured argv, closed project identity, structured runtime and
plugin identity, domain-tagged scope hashing, and explicit validator
requirements for recomputation and cross-record invariants.

The next step is not execution. Any validator or oracle-population work
requires a separate authorization artifact.
