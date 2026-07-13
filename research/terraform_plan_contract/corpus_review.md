# Terraform Plan Corpus Review

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED
CORPUS_RETRY_REVIEW_COMPLETE
SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
ORACLE_SCHEMA_AUTHORIZED_NEXT
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
manifest: research/terraform_plan_contract/corpus_manifest_v1.json
results: research/terraform_plan_contract/corpus_materialization_results.json
report: research/terraform_plan_contract/corpus_materialization_report.md
tool: tools/materialize_terraform_plan_corpus.py
review_type: SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
```

The earlier negative corpus review remains preserved in Git history. This file
now records the retry review after the environment remediation and explicit
retry authorization.

## Authorization Chain

```text
prior negative closeout: PRESERVED
environment readiness: DOMAIN_3_TERRAFORM_RETRY_ENVIRONMENT_READY
retry authorization: DOMAIN_3_TERRAFORM_RETRY_AUTHORIZED
restart point: PHASE_C_RETRY_AUTHORIZED
```

The retry did not rewrite the declaration, methodology, or prior negative
closeout.

## Corpus Shape

```text
total cases: 40
authentic locally generated Terraform Plan JSON cases: 8
synthetic/controlled cases: 32
mutation pairs: 10
manifest sha256: 28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

The corpus matches the locked methodology target:

```text
40 cases
32 synthetic/controlled fixtures
8 authentic locally generated Terraform Plan JSON cases
10 declared mutation pairs minimum
```

## Authentic Terraform-Generated Stratum

The eight authentic cases are:

```text
auth_create_only
auth_no_changes
auth_update_only
auth_delete_only
auth_replace_delete_create
auth_replace_create_delete
auth_moved_previous_address
auth_mixed_changes
```

Observed authentic action coverage:

```text
create
no-op
update
delete
delete/create replacement
create/delete replacement
moved previous_address
mixed create/update/delete
```

They were generated locally using:

```text
Terraform v1.15.8
terraform.io/builtin/terraform
```

The materialization report records:

```text
provider download observed: false
cloud/live infrastructure used: false
remote backend used: false
```

## Synthetic / Controlled Stratum

The controlled stratum covers required edge cases that are not all convenient or
safe to force through local Terraform generation:

```text
read
no-op
replace delete/create
replace create/delete
sensitive paths
unknown after values
applyable false + no changes
applyable false + changes
complete false
errored true
unsupported format major
malformed JSON
missing required structure
duplicate resource address
summary/list conflict
replace-path inconsistency
instruction text in tag
instruction text in description
fabricated SPIRA JSON in a value
optional provenance BOUND
optional provenance NOT_PROVIDED
order-only mutation
unknown-path mutation
replace-path mutation
```

Synthetic fixtures are explicitly marked:

```text
evidence_kind: SYNTHETIC_CONTROLLED
```

They are not mislabeled as Terraform-generated evidence.

## Mutation Pair Review

The manifest contains ten declared mutation pairs:

```text
mutation_update_to_replace
mutation_replace_order
mutation_replace_paths
mutation_action_sequence_same_count
mutation_unknown_paths
mutation_order_only
mutation_create_to_delete
mutation_no_changes_to_not_applyable_changes
mutation_provenance_bound_to_not_provided
mutation_instruction_location
```

All referenced case IDs exist.

The matrix includes the required semantic and order-only cases:

```text
update -> replace delete/create
replace delete/create -> replace create/delete
same replace action -> changed replace_paths
same address/counts -> changed action sequence
same actions -> changed unknown paths
resource_changes reordered only
```

## Validation Review

The materialization results report:

```text
validation.passed: true
case_count: 40
unique_case_ids: 40
authentic_count: 8
synthetic_count: 32
mutation_pair_count: 10
missing_files: 0
hash_mismatches: 0
broken_mutation_pairs: 0
privacy/path/secret scan: PASS
```

Additional commands run during materialization/review:

```text
python -m json.tool corpus_manifest_v1.json: PASS
python -m json.tool corpus_materialization_results.json: PASS
git diff --check: PASS
python -m pytest: 94 passed
```

## Boundary Review

The corpus review confirms:

```text
oracle expected answers: NOT_POPULATED
producer output observed: false
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
MVP boundary: UNCHANGED
release/version/tag/PyPI: NOT_AUTHORIZED
```

This acceptance does not authorize oracle population or producer
implementation. It only accepts the frozen corpus as input evidence for the next
gate.

## Verdict

```text
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED
```

## Next Authorized Artifact

The next gate is oracle schema design:

```text
research/terraform_plan_contract/oracle_schema_v1.schema.json
research/terraform_plan_contract/oracle_schema_v1_review.md
```

Oracle population remains blocked until schema and validator gates are
separately accepted.
