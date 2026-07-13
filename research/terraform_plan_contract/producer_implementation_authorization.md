# Terraform Plan Producer Implementation Authorization

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_AUTHORIZED
PRODUCER_IMPLEMENTATION_AUTHORIZATION_ONLY
TERRAFORM_PLAN_JSON_PRODUCER_AUTHORIZED
ORACLE_ACCEPTED
GATE_A_FROZEN
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

This authorization follows:

```text
corpus:
DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED

Oracle Schema V1:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED

validator implementation:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_IMPLEMENTATION_ACCEPTED

oracle:
DOMAIN_3_TERRAFORM_PLAN_ORACLE_ACCEPTED
```

The accepted corpus manifest remains:

```text
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

## Authorized Work

Only the following work is authorized:

```text
1. Terraform Plan JSON producer implementation.
2. Typed factual claim extraction.
3. Explicit resource/action lists.
4. replace_paths extraction.
5. unknown paths extraction.
6. sensitive-path detection without value exposure.
7. optional provenance state extraction.
8. evidence locator generation.
9. Gate A assembly usage.
10. 40-case evaluation against the accepted oracle.
11. focused producer tests.
12. machine-readable evaluation results.
13. producer implementation report.
14. focused and full test-suite execution.
```

The producer may read:

```text
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/cases/
research/terraform_plan_contract/oracle_v1.json
research/terraform_plan_contract/oracle_schema_v1.schema.json
source/spira_core/terraform_plan_oracle_validator.py
source/spira_core/unification_proof.py
```

It may not modify accepted truth-layer artifacts.

## Allowed Files

Implementation may create or update only:

```text
source/spira_core/terraform_plan_producer.py
tests/test_terraform_plan_producer.py
tools/evaluate_terraform_plan_producer.py
research/terraform_plan_contract/producer_implementation_results.json
research/terraform_plan_contract/producer_implementation_report.md
```

If implementation requires any file outside this list, work must stop and a new
authorization must be written before changing that file.

## Frozen Artifacts

The following artifacts are frozen:

```text
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/cases/
research/terraform_plan_contract/oracle_v1.json
research/terraform_plan_contract/oracle_schema_v1.schema.json
research/terraform_plan_contract/oracle_validator_spec.md
source/spira_core/terraform_plan_oracle_validator.py
source/spira_core/unification_proof.py
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

Producer work must not update baselines, rebaseline Gate A, or modify the
accepted oracle to fit producer output.

## Required Producer Behavior

The producer must derive outputs from Terraform Plan evidence:

```text
plan.json exact bytes
plan.json.invalid exact bytes
main.tf when present
accepted corpus manifest metadata
```

It must not derive expected answers from the accepted oracle except for
evaluation. It must not embed oracle answers as constants.

The producer must emit:

```text
case_id
subject identity
context identity
typed claims
explicit lists
policy/action binding
mutation relationship inputs
evidence locators
not-claimed boundaries
Gate A proof assembly output, where applicable
```

## Terraform Evidence Requirements

The producer must preserve:

```text
resource action sequence order
create / update / delete / read / no-op distinction
delete/create replacement vs create/delete replacement
replace_paths
unknown paths as NOT_EVALUATED structural facts
sensitive paths as NOT_EVALUATED structural facts
optional provenance BOUND / NOT_PROVIDED / NOT_APPLICABLE states
malformed JSON -> RERUN_REQUIRED evidence path
unsupported format -> REPORT_NOT_EVALUATED evidence path
errored plan -> STOP_BLOCKED evidence path
incomplete plan -> REPORT_NOT_EVALUATED evidence path
```

It must not expose sensitive values, infer unknown values, or obey
instruction-like text embedded inside Terraform values.

## Evaluation Gates

The implementation can be reported as pass only if all gates pass:

```text
40 / 40 claim fidelity
40 / 40 action equivalence
0 false PROCEED
40 / 40 strict-list fidelity
40 / 40 evidence-pointer validity
10 / 10 mutation relationships
all semantic mutations detected
all order-only mutations invariant
0 sensitive-value leaks
0 instruction-injection overrides
NOT_EVALUATED preservation
BLOCK preservation
mismatch_count == 0
Oracle Schema V1 validation: PASS
accepted oracle validator: PASS
focused producer tests: PASS
full pytest suite: PASS
Gate A unchanged check: PASS
```

The only successful status is:

```text
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_PASS
```

## Gate A Check

The evaluation must not overclaim Gate A regression.

Preferred check:

```text
Gate A isolated regression
1,954 / 1,954 identity matches
accepted baseline root:
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

If the full isolated regression is not run, the report must state that clearly
and may only claim a fallback check:

```text
accepted baseline root unchanged
Gate A core worktree unchanged
Gate A full identity regression: NOT_RUN
```

The fallback must not be labeled as full Gate A identity regression.

## Required Negative Tests

Focused producer/evaluator tests must prove that these fail evaluation:

```text
claim mismatch
action mismatch
false PROCEED
strict-list mismatch
evidence-pointer mismatch
mutation relationship mismatch
sensitive value leak
unknown value inference
instruction-like value overriding policy
NOT_EVALUATED dropped
BLOCK dropped
mismatch_count > 0
```

## Machine-Readable Results

The result file must be:

```text
research/terraform_plan_contract/producer_implementation_results.json
```

It must include:

```text
schema
schema_version
status
case_count
producer_case_count
oracle_claim_fidelity
action_equivalence
false_proceed_count
strict_list_fidelity
evidence_pointer_validity
mutation_relationship_fidelity
sensitive_value_leaks
instruction_override_count
not_evaluated_preservation
block_preservation
mismatch_count
schema_validation
validator_validation
focused_tests
full_tests
gate_a_check
corpus_changed
oracle_changed
schema_or_validator_changed
errors
```

## Implementation Report

The report must be:

```text
research/terraform_plan_contract/producer_implementation_report.md
```

It must document:

```text
authorization chain
implemented producer behavior
evaluation command
focused tests
full tests
40-case oracle comparison
mutation relationship evaluation
sensitive/unknown/instruction safeguards
Gate A unchanged check
truth-layer artifacts unchanged
terminal status
```

## Stop Conditions

Implementation must stop with a non-pass status if any of these occur:

```text
corpus/oracle/schema/validator change is required
Gate A refactor or rebaseline is required
Gate B behavior is required
producer needs provider download, cloud credentials, or live infrastructure
Terraform evidence cannot be parsed under the accepted contract
sensitive values must be exposed to match oracle
unknown values must be guessed to match oracle
instruction-like values influence action
any evaluation mismatch remains
full tests fail
```

Allowed non-pass statuses:

```text
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_INCOMPLETE
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_FAILED
PRODUCER_AUTHORIZATION_REVISION_REQUIRED
ORACLE_REVISION_REQUIRED
```

## Post-Implementation Review Requirement

Even if implementation reports:

```text
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_PASS
```

the producer is not accepted until a separate review records one of:

```text
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_ACCEPTED
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_NEEDS_REVISION
DOMAIN_3_TERRAFORM_PLAN_PRODUCER_IMPLEMENTATION_REJECTED
```

## Non-Authorization

This document does not authorize:

```text
corpus changes
oracle changes
schema changes
validator changes
Gate A refactor or rebaseline
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```
