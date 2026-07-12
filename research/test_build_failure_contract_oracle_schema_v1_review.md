# Test/Build Failure Contract - Oracle Schema V1 Review

## Status

```text
DOMAIN_2_ORACLE_SCHEMA_V1_NEEDS_REVISION
ORACLE_SCHEMA_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Reviewed schema:

```text
research/test_build_failure_contract_oracle_schema_v1.schema.json
```

Reviewed commit:

```text
47b6267e5def05ebb757b84cf718c5639d730e12
```

## Review Scope

This review checks whether Oracle Schema V1 is ready to support oracle case
authoring.

It does not authorize:

```text
oracle population
fixture generation
corpus materialization
producer implementation
Gate B
release/version/tag/PyPI
```

## Accepted Structure

The schema correctly encodes the accepted Dual Identity Model V2 separation:

```text
run_identity: CONTEXTUAL
result_identity: POLICY_INDEPENDENT
scope_identity: REQUIRED_BEFORE_RESULT_IDENTITY
policy_action_binding: OUTSIDE_RESULT_IDENTITY
```

It also correctly separates:

```text
expected_scope_identity
expected_result_identity
expected_policy_action
expected_identity_relationships
expected_claims
expected_explicit_lists
expected_not_evaluated
expected_evidence_locators
```

The review accepts the high-level schema direction.

## Blocking Finding 1 - NOT_EVALUATED Result Identity May Still Carry A Hash

Current behavior:

```text
expected_result_identity.status == NOT_EVALUATED
```

requires:

```text
reason_codes
```

and rejects:

```text
projection
```

but does not reject:

```text
result_identity_sha256
```

This allows a contradictory oracle case:

```json
{
  "status": "NOT_EVALUATED",
  "result_identity_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "reason_codes": ["TEST_RESULT_EVIDENCE_INCOMPLETE"]
}
```

That is not fail-closed enough. If result identity was not evaluated, the
oracle must not publish a digest for it.

Required revision:

```text
status == NOT_EVALUATED
-> no result_identity_sha256
-> no projection
```

## Blocking Finding 2 - NOT_EVALUATED Scope Identity May Still Carry Collection Identity

Current behavior:

```text
expected_scope_identity.status == NOT_EVALUATED
```

requires:

```text
collection_deterministic: false
reason_codes
```

but does not reject:

```text
collection_manifest_sha256
canonical_collected_test_ids
```

This allows a contradictory oracle case:

```json
{
  "status": "NOT_EVALUATED",
  "collection_deterministic": false,
  "collection_manifest_sha256": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "canonical_collected_test_ids": ["tests/test_example.py::test_a"],
  "reason_codes": ["TEST_COLLECTION_IDENTITY_NOT_DETERMINISTIC"]
}
```

If scope identity was not evaluated, the oracle must not publish a collection
identity.

Required revision:

```text
scope status == NOT_EVALUATED
-> no collection_manifest_sha256
-> no canonical_collected_test_ids
```

Because `result_identity` already depends on `scope_identity`, the schema must
also preserve:

```text
scope NOT_EVALUATED
-> result_identity NOT_EVALUATED
```

If JSON Schema cannot enforce that cross-field rule cleanly, the rule must be
declared as requiring a validator before oracle population.

## Additional Review Questions For V2

The following are not necessarily blockers for the schema concept, but must be
resolved or explicitly assigned to a validator before oracle population.

### Policy Action Semantics Version

`expected_policy_action.decision_semantics_version` is currently optional.

Review question:

```text
Should decision_semantics_version be required whenever expected_policy_action
is present?
```

Recommended answer:

```text
yes
```

Reason:

```text
action mapping is semantic-version dependent
```

### Agent Action Enum Scope

The schema permits:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
REPORT_WITH_NOTES
```

It omits any broader or legacy action such as:

```text
ASK_HUMAN
```

Review question:

```text
Is this a deliberate subset of the current frozen agent-action contract?
```

The next schema revision must either document this as intentional or align the
enum with the currently frozen contract.

### Relationship Referential Integrity

`related_case_id` is syntactically constrained but not checked against the set
of case IDs in the same oracle file.

Required handling:

```text
JSON Schema may validate the field shape.
A separate oracle validator must verify that related_case_id exists.
```

### Relationship Symmetry

Identity relationships between paired cases may need symmetric expectations.

Example:

```text
A says B has SAME result_identity
B says A has SAME result_identity
```

JSON Schema cannot reliably enforce pair symmetry. A separate oracle validator
must handle it if symmetry is required.

### Canonical Sorting

The schema can require arrays and unique items, but it does not guarantee
canonical sort order for:

```text
blocking_cases
nonblocking_cases
canonical_collected_test_ids
reason_codes
expected_not_evaluated
expected_not_claimed
```

Required handling:

```text
Either schema V2 must encode stronger constraints where possible,
or a separate oracle validator must enforce canonical sorting before
oracle population.
```

## Required Next Artifact

The next artifact should be a schema revision:

```text
research/test_build_failure_contract_oracle_schema_v2.schema.json
```

It must at minimum close the two fail-closed holes:

```text
NOT_EVALUATED result identity cannot carry result_identity_sha256
NOT_EVALUATED scope identity cannot carry collection identity
```

It must also explicitly classify additional checks as either:

```text
JSON Schema enforced
validator enforced before oracle population
not required, with rationale
```

## Verdict

```text
DOMAIN_2_ORACLE_SCHEMA_V1_NEEDS_REVISION
ORACLE_SCHEMA_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
CORPUS_MATERIALIZATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle Schema V1 has the correct structure and preserves the accepted identity
model, but it is not accepted until the NOT_EVALUATED identity contradictions
are closed.
