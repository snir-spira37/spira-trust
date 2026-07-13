# Terraform Plan Oracle Review

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_ACCEPTED
ORACLE_REVIEW_COMPLETE
SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
PRODUCER_IMPLEMENTATION_AUTHORIZATION_REQUIRED_NEXT
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Reviewed Artifacts

```text
oracle: research/terraform_plan_contract/oracle_v1.json
population report: research/terraform_plan_contract/oracle_population_report.md
population results: research/terraform_plan_contract/oracle_population_results.json
population tool: tools/populate_terraform_plan_oracle.py
validator: source/spira_core/terraform_plan_oracle_validator.py
review_type: SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
```

## Prior Gates

```text
corpus:
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED

Oracle Schema V1:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED

validator specification:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED

validator implementation:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED

oracle population:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_POPULATED
```

The accepted corpus manifest remains:

```text
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

## Mechanical Validation

The populated oracle reports:

```text
cases: 40 / 40
mutation relationships: 10 / 10
Schema V1: PASS
accepted validator: PASS
validator errors: 0
privacy/path/secret scan: PASS
producer output observed: false
corpus changed: false
schema or validator changed: false
```

Direct validator rerun:

```text
verdict: PASS
status: DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATION_PASS
validated_case_count: 40
mutation_relationship_count: 10
error_count: 0
```

## Semantic Review Checklist

```text
expected answers derived from plan evidence, not case names: PASS
no-change is not blocked merely because applyable:false: PASS
errored / incomplete / unsupported are mapped by methodology: PASS
resource action sequences are preserved exactly: PASS
update and replace differ even when counts are similar: PASS
replace_paths enter claims and mutation relationships: PASS
unknown paths are NOT_EVALUATED structural facts: PASS
sensitive paths are structural and do not expose values: PASS
NOT_PROVIDED provenance is not invented into hashes: PASS
instruction-like values do not affect verdicts: PASS
10 / 10 mutation relationships match methodology: PASS
```

## Evidence-Derived Answers Review

The oracle population tool derives claims from frozen evidence:

```text
Terraform Plan JSON bytes
malformed Terraform Plan JSON bytes
main.tf hashes where present
accepted corpus manifest
accepted mutation-pair deltas
```

It does not read producer output. The population results explicitly record:

```text
producer_output_observed: false
```

Case IDs are used to locate evidence, not as standalone expected answers.

## No-Change and Applyable Review

The review specifically checks the distinction:

```text
applyable:false + no effective changes
```

This is not treated as a blocking resource-change case. The oracle maps:

```text
auth_no_changes -> PROCEED / TERRAFORM_PLAN_NO_CHANGES
syn_applyable_false_no_changes -> PROCEED / TERRAFORM_PLAN_NO_CHANGES
```

In contrast:

```text
applyable:false + effective changes
```

is mapped to:

```text
STOP_BLOCKED / TERRAFORM_PLAN_NOT_APPLYABLE
```

This preserves the distinction between a no-op plan that is not applyable and a
non-applyable plan with changes.

## Error and Not-Evaluated Review

The oracle maps:

```text
malformed JSON -> RERUN_REQUIRED / TERRAFORM_PLAN_JSON_INVALID
errored true -> STOP_BLOCKED / TERRAFORM_PLAN_ERRORED
complete false -> REPORT_NOT_EVALUATED / TERRAFORM_PLAN_INCOMPLETE
unsupported format major -> REPORT_NOT_EVALUATED / TERRAFORM_PLAN_FORMAT_UNSUPPORTED
```

These mappings are accepted.

## Resource Action Review

The oracle preserves Terraform action sequences exactly:

```text
["create"]
["update"]
["delete"]
["read"]
["no-op"]
["delete","create"]
["create","delete"]
```

Replacement order is identity-bearing:

```text
delete/create replacement != create/delete replacement
```

The oracle does not collapse both into a generic replacement.

## replace_paths Review

Replacement paths are represented as explicit structural facts:

```text
TERRAFORM_REPLACE_PATH_PRESENT
explicit_lists.replace_paths
mutation_replace_paths -> DIFFERENT
```

The `syn_replace_path_base` and `syn_replace_path_mutation` pair differs by
replace path evidence while preserving the same replacement action sequence.
The oracle marks the claims, claims root, and contextual unification identity as
different.

## Unknown Path Review

Unknown planned values are represented as:

```text
PLANNED_VALUE_UNKNOWN
status: NOT_EVALUATED
explicit_lists.unknown_paths
```

The oracle does not infer the unknown runtime value. The
`mutation_unknown_paths` pair marks the semantic claim relation as different
because the structural unknown paths differ.

## Sensitive Path Review

Sensitive values are represented only as structural paths:

```text
SENSITIVE_PATH_PRESENT
status: NOT_EVALUATED
explicit_lists.sensitive_paths
```

The oracle does not expose secret values as claim strings. The privacy/path/
secret scan passes.

## Optional Provenance Review

Optional provenance states are preserved as:

```text
BOUND
NOT_PROVIDED
NOT_APPLICABLE
```

The oracle does not invent hashes for `NOT_PROVIDED` provenance. The
`mutation_provenance_bound_to_not_provided` pair is marked different because the
observable provenance state changes.

## Instruction-Like Value Review

The instruction-text cases are treated as Terraform plan values, not as
instructions. They do not alter policy/action behavior beyond the structural
Terraform evidence they appear in.

The `mutation_instruction_location` pair remains different because the
instruction-like text appears in a different evidence location, not because the
text is obeyed.

## Mutation Relationship Review

All 10 accepted mutation relationships are populated and validator-checked.

Accepted examples:

```text
update -> replace delete/create: DIFFERENT
replace delete/create -> replace create/delete: DIFFERENT
same replace action -> changed replace_paths: DIFFERENT
same address/counts -> changed action sequence: DIFFERENT
same actions -> changed unknown paths: DIFFERENT
resource_changes reordered only: claims SAME, claims root SAME, unification_id DIFFERENT
create -> delete: DIFFERENT
no changes -> applyable false with changes: DIFFERENT
optional provenance BOUND -> NOT_PROVIDED: DIFFERENT
instruction text in tag -> instruction text in description: DIFFERENT
```

The order-only pair is important: the oracle preserves semantic claim equality
while allowing contextual identity to differ because the frozen plan bytes and
contextual subject identity differ.

## Boundary Review

The oracle does not claim:

```text
infrastructure correctness
infrastructure security
infrastructure cost
infrastructure compliance
apply success
live state freshness
Terraform provider safety
Gate B reuse
Kubernetes support
Domain 4
MVP inclusion
release readiness
```

## What This Acceptance Means

The Domain 3 Terraform Plan oracle is accepted as the independent expected
answer set for the accepted 40-case Terraform Plan corpus.

It may be used, after separate authorization, to evaluate a future Terraform
Plan producer.

## What This Acceptance Does Not Mean

This acceptance does not authorize:

```text
producer implementation
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```

It does not prove that a Terraform producer exists or that Terraform
infrastructure is safe, correct, compliant, cheap, or applyable.

## Verdict

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_ACCEPTED
```

## Next Gate

The next gate may be a narrow Terraform Plan producer implementation
authorization document.

That authorization must be separate and explicit. It must not authorize Gate B,
Domain 4, MVP boundary amendment, release/version/tag/PyPI, or changes to the
accepted corpus, oracle schema, validator, or oracle.
