# Terraform Plan Oracle Schema V1 Review

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED
ORACLE_SCHEMA_V1_REVIEW_COMPLETE
SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
ORACLE_VALIDATOR_SPEC_AUTHORIZED_NEXT
ORACLE_POPULATION_NOT_AUTHORIZED
VALIDATOR_IMPLEMENTATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifact

```text
schema: research/terraform_plan_contract/oracle_schema_v1.schema.json
corpus: DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED
review_type: SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
```

## Review Checklist

```text
subject/context identity: PASS
optional provenance states: PASS
typed claims: PASS
resource action sequences: PASS
explicit resource lists: PASS
replace_paths: PASS
unknown paths: PASS
sensitive structural paths: PASS
NOT_EVALUATED states: PASS
policy/action binding: PASS
evidence locators: PASS
mutation relationships: PASS
not-claimed boundaries: PASS
sensitive-value public fields blocked structurally: PASS
oracle population remains blocked: PASS
producer remains blocked: PASS
```

## Schema Validation

The schema is valid JSON and declares:

```text
$schema: https://json-schema.org/draft/2020-12/schema
schema: SPIRA_DOMAIN3_TERRAFORM_PLAN_ORACLE
schema_version: 1
case_count: 40
```

The schema is intentionally structural. Cross-case integrity, canonical sorting,
hash recomputation, strict-list equivalence, and semantic consistency remain
validator responsibilities in the next gate.

## Identity Review

The schema requires:

```text
subject.type = terraform_plan
subject.sha256 = SHA256(exact frozen Terraform Plan JSON bytes)
context.run_identity_kind = CONTEXTUAL_UNIFICATION_ID
context.unification_id_expected
```

It does not introduce a semantic result identity for Domain 3 V1.

## Optional Provenance Review

The schema requires all optional provenance fields:

```text
configuration_sha256
prior_state_sha256
provider_lockfile_sha256
variables_manifest_sha256
generation_command_fingerprint
workspace_or_fixture_identity
```

Each must use:

```text
BOUND
NOT_PROVIDED
NOT_APPLICABLE
```

`BOUND` requires a hash/fingerprint. `NOT_PROVIDED` and `NOT_APPLICABLE` forbid
hash/fingerprint fields. This prevents empty-hash ambiguity.

## Claims and Lists Review

The schema represents the accepted Terraform claim taxonomy, including:

```text
format/version facts
applyable/complete/errored facts
resource address/type facts
resource action sequences
create/update/delete/replace/read/no-op facts
replace paths
unknown paths
sensitive structural paths
optional provenance states
```

It also requires explicit lists for:

```text
create_resources
update_resources
delete_resources
replace_resources
read_resources
noop_resources
replace_paths
unknown_paths
sensitive_paths
not_evaluated
```

The future validator must verify canonical sorting, count/list equivalence, and
claim/list equivalence.

## Sensitive and Unknown Review

The schema forces:

```text
SENSITIVE_PATH_PRESENT -> NOT_EVALUATED
PLANNED_VALUE_UNKNOWN -> NOT_EVALUATED
```

It also restricts claim string values with a sensitive-value pattern. This is
not a complete secret scanner, so the validator and corpus scans remain
required. The schema does, however, prevent the oracle from intentionally
modeling sensitive values as ordinary claim strings.

## Policy and Action Review

The schema preserves the closed action vocabulary:

```text
PROCEED
REPORT_WITH_NOTES
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

It requires:

```text
decision_semantics_version = SPIRA_DECISION_SEMANTICS_V2
```

It also encodes bidirectional stop/action consistency:

```text
stop:false -> PROCEED / REPORT_WITH_NOTES
stop:true -> STOP_BLOCKED / RERUN_REQUIRED / REPORT_NOT_EVALUATED
```

## Mutation Relationship Review

The schema represents mutation relationships with:

```text
pair_id
base_case_id
mutated_case_id
declared_delta
expected_claims_relation
expected_claims_root_relation
expected_unification_id_relation
```

The future validator must enforce cross-case references and relationship
consistency.

## Boundaries

The schema keeps these blocked:

```text
oracle population before schema acceptance
producer implementation
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```

## Verdict

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED
```

## Next Authorized Artifact

```text
research/terraform_plan_contract/oracle_validator_spec.md
research/terraform_plan_contract/oracle_validator_spec_review.md
```

Validator implementation, oracle population, and producer implementation remain
blocked until their own gates are accepted.
