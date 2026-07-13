# Domain 3 Terraform Plan Retry Authorization

## Status

```text
DOMAIN_3_TERRAFORM_RETRY_AUTHORIZED
RETRY_AFTER_ENVIRONMENT_REMEDIATION
PRIOR_NEGATIVE_CLOSEOUT_PRESERVED
PHASE_C_RETRY_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Authorization Chain

This retry authorization follows the preserved negative result:

```text
negative closeout:
research/domain3_terraform_plan_research_closeout.md
DOMAIN_3_TERRAFORM_PLAN_NEGATIVE_RESULT_ACCEPTED

negative closeout review:
research/domain3_terraform_plan_negative_closeout_review.md
DOMAIN_3_TERRAFORM_PLAN_NEGATIVE_CLOSEOUT_ACCEPTED
```

It also follows the environment readiness sequence:

```text
first readiness:
88768da
research/domain3_terraform_retry_environment_readiness.md
DOMAIN_3_TERRAFORM_RETRY_ENVIRONMENT_NOT_READY

remediated readiness:
d921c72
research/domain3_terraform_retry_environment_readiness_ready.md
DOMAIN_3_TERRAFORM_RETRY_ENVIRONMENT_READY
```

The retry uses the already locked declaration and methodology:

```text
research/domain3_terraform_plan_research_declaration.md
research/terraform_plan_evidence_methodology_v1.md
```

No declaration or methodology rewrite is authorized.

## What Changed Since the Negative Closeout

The original negative closeout remains true:

```text
Night Run 1 stopped in Phase C.
Terraform CLI was unavailable.
Authentic Terraform corpus was not materialized.
Oracle and producer phases were not reached.
```

After that closeout, Terraform was installed and pinned as environment
remediation:

```text
Terraform v1.15.8
binary sha256:
6eb0a1cb89344c97ccf2928ddc2d7a6cb71a1837b7ecccfd5991466b6d751e03
```

The readiness smoke demonstrated:

```text
terraform init: PASS
terraform plan -out: PASS
terraform show -json: PASS
provider download observed: false
cloud/live infrastructure used: false
credentials detected: none
```

This removes the local tooling precondition that blocked the first run. It does
not retroactively change the first run's result.

## Retry Scope

The retry starts at Phase C only.

Authorized:

```text
materialize the previously defined 8 authentic Terraform-generated cases
complete the previously defined frozen 40-case corpus
corpus review
oracle schema and validator path
oracle population and review
producer authorization
producer implementation and review
Domain 3 retry closeout
```

The retry must continue gate-by-gate under the existing methodology. Completion
of one gate does not authorize weakening or skipping the next.

## Required Corpus Target

The retry must keep the same corpus target:

```text
40 cases
32 synthetic/controlled fixtures
8 authentic locally generated Terraform Plan JSON cases
10 declared mutation pairs minimum
```

The authentic cases must be generated locally using the ready Terraform
environment and must not be replaced with synthetic JSON.

## Required Terraform Constraints

The retry may use only local synthetic fixtures that do not require:

```text
network access
provider download
remote backend
cloud credentials
cloud infrastructure
live Terraform state
Kubernetes
```

Provider behavior must remain one of:

```text
built-in Terraform provider
pinned local provider already available before the retry
explicitly documented local mirror/cache with no network use during materialization
```

If these constraints cannot be satisfied for the 8 authentic cases, the retry
must stop with a second negative result.

## Allowed Files for Phase C Retry

The retry may create or update only the Domain 3 Terraform contract artifacts
authorized by the prior methodology and each subsequent gate:

```text
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/corpus_materialization_results.json
research/terraform_plan_contract/corpus_materialization_report.md
research/terraform_plan_contract/corpus_review.md
tools/materialize_terraform_plan_corpus.py
```

Later phases may add their own authorization documents and artifacts only after
their prerequisite reviews pass.

Any need to modify declaration, methodology, Gate A, Gate B, Domain 1, Domain 2,
MVP boundary, release files, or package metadata requires stopping and recording
a revision-required result.

## Mandatory Preservation Rules

The retry must not:

```text
delete or alter the original negative closeout
delete or alter the NOT_READY readiness report
rewrite the declaration
rewrite the methodology
weaken the 40-case target
replace the 8 authentic cases with synthetic JSON
download providers during materialization
use remote backend
use cloud credentials
touch live infrastructure
open Gate B
open Domain 4
change MVP boundary
authorize release
```

## Retry Closeout Outcomes

The retry must end with exactly one of:

```text
DOMAIN_3_TERRAFORM_PLAN_RETRY_COMPLETE_WITH_BOUNDS
DOMAIN_3_TERRAFORM_PLAN_RETRY_NEGATIVE_RESULT_ACCEPTED
```

A second negative result is valid.

The retry closeout must document both runs:

```text
Run 1:
environment prerequisite failure

Retry 1:
executed after pinned local Terraform readiness
```

## MVP Boundary Consequence

Even if the retry succeeds:

```text
Domain 3 success != automatic MVP inclusion
Domain 3 success != release authorization
Domain 3 success != Gate B authorization
```

A separate future artifact would be required to reconsider MVP scope:

```text
research/mvp_product_boundary_amendment_proposal.md
```

That artifact is not authorized by this retry authorization.

## Final Authorization

```text
DOMAIN_3_TERRAFORM_RETRY_AUTHORIZED
PHASE_C_RETRY_AUTHORIZED
PRIOR_NEGATIVE_CLOSEOUT_PRESERVED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```
