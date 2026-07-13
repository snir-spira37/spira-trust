# Terraform Plan Oracle Population Authorization

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATION_AUTHORIZED
ORACLE_POPULATION_AUTHORIZATION_ONLY
ORACLE_SCHEMA_V1_ACCEPTED
ORACLE_VALIDATOR_SPEC_ACCEPTED
ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
CORPUS_CHANGES_NOT_AUTHORIZED
SCHEMA_OR_VALIDATOR_CHANGES_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows the accepted Domain 3 Terraform Plan truth-layer
chain:

```text
corpus:
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED

Oracle Schema V1:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED

validator specification:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED

validator implementation:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED
```

The accepted corpus manifest remains:

```text
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

## Authorized Work

Only the following work is authorized:

```text
1. Populate expected oracle answers for the 40 accepted corpus cases.
2. Derive answers only from frozen corpus evidence.
3. Populate expected typed claims.
4. Populate subject/context identities.
5. Populate optional provenance states.
6. Populate explicit resource lists.
7. Populate policy/action binding.
8. Populate evidence locators.
9. Populate mutation relationships.
10. Run Oracle Schema V1 validation.
11. Run the accepted Terraform Plan oracle validator.
12. Produce machine-readable oracle population results.
13. Produce an oracle population report.
14. Run JSON/privacy/path/secret scans.
```

The oracle population may use:

```text
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/cases/
research/terraform_plan_contract/oracle_schema_v1.schema.json
source/spira_core/terraform_plan_oracle_validator.py
tools/validate_terraform_plan_oracle.py
```

It may not use producer output.

## Allowed Files

The population step may create or update only:

```text
research/terraform_plan_contract/oracle_v1.json
research/terraform_plan_contract/oracle_population_results.json
research/terraform_plan_contract/oracle_population_report.md
tools/populate_terraform_plan_oracle.py
```

If any additional file is required, work must stop and a new authorization must
be written before changing that file.

## Frozen Inputs

These artifacts are frozen for oracle population:

```text
corpus_manifest_v1.json
all files under research/terraform_plan_contract/cases/
oracle_schema_v1.schema.json
oracle_validator_spec.md
terraform_plan_oracle_validator.py
validate_terraform_plan_oracle.py
```

Population must not modify the corpus, schema, spec, or accepted validator to
fit expected answers.

## Oracle Authoring Rules

Expected answers must be derived from evidence, not from a producer. The
allowed evidence is:

```text
Terraform Plan JSON bytes
malformed Terraform Plan JSON bytes
main.tf fixtures when present
case metadata from the accepted corpus manifest
declared mutation-pair deltas from the accepted corpus manifest
```

Case IDs and fixture names may help locate evidence, but they are not
standalone expected answers.

## Required Populated Fields

Each of the 40 oracle cases must include:

```text
case_id
subject identity
context identity
optional_provenance
expected_claims
explicit_lists
policy_action
mutation_membership
not_claimed
evidence locators
```

The top-level oracle must include:

```text
schema
schema_version
status
corpus_manifest_sha256
case_count
cases
mutation_relationships
not_claimed
not_authorized
```

## Identity Requirements

Population must compute:

```text
subject.sha256 from exact plan.json or plan.json.invalid bytes
context_sha256 from the accepted Domain 3 context projection
claims identity and claims root through the accepted validator contract
unification_id_expected through the accepted Gate A input contract
```

Hash-only identity fields without canonical bytes are forbidden.

## Sensitive / Unknown / Provenance Semantics

Population must preserve:

```text
sensitive structural paths as SENSITIVE_PATH_PRESENT -> NOT_EVALUATED
unknown planned values as PLANNED_VALUE_UNKNOWN -> NOT_EVALUATED
optional provenance BOUND / NOT_PROVIDED / NOT_APPLICABLE states
```

It must not expose sensitive values as ordinary claim strings.

It must not infer unknown Terraform planned values.

It must not convert NOT_PROVIDED provenance into guessed hashes.

## Mutation Relationship Requirements

Population must include all 10 accepted mutation relationships.

For each pair it must populate:

```text
pair_id
base_case_id
mutated_case_id
declared_delta
expected_claims_relation
expected_claims_root_relation
expected_unification_id_relation
```

Relationships must match the accepted manifest and the recomputed oracle
identities. A mismatch must stop population rather than weakening the relation.

## Validation Gates

Population may report success only if all gates pass:

```text
40 / 40 oracle cases populated
10 / 10 mutation relationships populated
Oracle Schema V1 validation: PASS
accepted validator: PASS
identity hashes recompute: PASS
explicit lists match evidence: PASS
resource actions match evidence: PASS
replace_paths match evidence: PASS
unknown_paths match evidence: PASS
sensitive structural paths remain not-evaluated: PASS
optional provenance states are evidence-derived: PASS
policy/action binding is consistent: PASS
JSON validation: PASS
privacy/path/secret scan: PASS
producer output observed: false
corpus changed: false
schema/validator changed: false
```

The only success status is:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATED
```

## Stop Conditions

Population must stop with a non-success status if any of these occur:

```text
accepted corpus evidence is insufficient
case evidence cannot be parsed when parsing is required
expected answer would require guessing
required identity cannot be recomputed
sensitive value would need to be exposed
unknown value would need to be inferred
mutation relation cannot be justified
Schema V1 fails
accepted validator fails
corpus/schema/spec/validator changes are needed
producer output is needed or observed
```

Allowed non-success statuses:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATION_INCOMPLETE
DOMAIN_3_TERRAFORM_PLAN_ORACLE_NEEDS_REVISION
ORACLE_POPULATION_AUTHORIZATION_REVISION_REQUIRED
```

## Required Results

The machine-readable result file must be:

```text
research/terraform_plan_contract/oracle_population_results.json
```

It must include:

```text
schema
schema_version
status
case_count
populated_case_count
mutation_relationship_count
schema_validation
validator_validation
validator_error_count
producer_output_observed
corpus_changed
schema_or_validator_changed
privacy_path_secret_scan
errors
```

## Required Report

The report must be:

```text
research/terraform_plan_contract/oracle_population_report.md
```

It must document:

```text
authorization chain
evidence sources
population method
case count
mutation relationship count
Schema V1 result
accepted validator result
privacy/path/secret scan result
producer output observed: false
corpus/schema/validator unchanged
terminal population status
```

## Post-Population Review Requirement

Even if population reports:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATED
```

the oracle is not accepted until a separate review records one of:

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_ACCEPTED
DOMAIN_3_TERRAFORM_PLAN_ORACLE_NEEDS_REVISION
DOMAIN_3_TERRAFORM_PLAN_ORACLE_REJECTED
```

Producer implementation remains blocked until the oracle is accepted by that
separate review and a further producer authorization is written.

## Non-Authorization

This document does not authorize:

```text
producer implementation
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```
