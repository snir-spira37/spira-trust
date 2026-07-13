# Terraform Plan Corpus Materialization Authorization

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_CORPUS_MATERIALIZATION_AUTHORIZED
CORPUS_MATERIALIZATION_ONLY
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_NOT_YET_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Chain

```text
declaration: DOMAIN_3_TERRAFORM_PLAN_DECLARATION_ACCEPTED
methodology: DOMAIN_3_TERRAFORM_PLAN_METHODOLOGY_ACCEPTED
```

This document authorizes only corpus materialization for Domain 3 Terraform Plan
evidence.

## Authorized Corpus Target

The target corpus is exactly:

```text
40 cases
32 synthetic/controlled fixtures
8 authentic locally generated Terraform Plan JSON cases
10 declared mutation pairs minimum
```

## Authentic Local Terraform Gate

The eight authentic cases may be generated only if all conditions hold:

```text
local Terraform CLI exists
no network/provider download is required
only local synthetic state/resources are used
no cloud provider or remote backend is used
no live infrastructure is touched
```

If those conditions cannot be met:

```text
DOMAIN_3_CORPUS_NOT_MATERIALIZABLE
```

The run must then proceed to a negative closeout rather than weakening the
corpus requirement.

## Authorized Files

If the corpus is materializable, this authorization permits:

```text
research/terraform_plan_contract/corpus_manifest_v1.json
research/terraform_plan_contract/corpus_materialization_results.json
research/terraform_plan_contract/corpus_materialization_report.md
tools/materialize_terraform_plan_corpus.py
```

For a negative materialization result, this authorization permits a narrowed
subset:

```text
research/terraform_plan_contract/corpus_materialization_results.json
research/terraform_plan_contract/corpus_materialization_report.md
```

## Required Coverage If Materialized

The materialized corpus must include at least:

```text
no changes
create only
update only
delete only
read
no-op
replace delete/create
replace create/delete
mixed changes
moved/previous address
unknown after values
sensitive paths
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
```

## Required Validation

If materialized, the corpus must pass:

```text
JSON validation
all source-hash recomputation
case-id uniqueness
mutation-pair integrity
privacy scan
absolute-path scan
secret scan
sensitive sentinel scan
git diff --check
full pytest
```

## Forbidden Work

This authorization does not permit:

```text
oracle expected answers
oracle population
producer implementation
Terraform producer/parser/adapter code
Gate A changes
Gate B
Domain 4
MVP implementation
release / version / tag / PyPI
network fetching of Terraform providers, repositories, packages, or evidence
cloud infrastructure
live Terraform environment
Kubernetes
```

## Terminal Outcomes

```text
DOMAIN_3_TERRAFORM_PLAN_CORPUS_MATERIALIZED
DOMAIN_3_CORPUS_NOT_MATERIALIZABLE
CORPUS_MATERIALIZATION_AUTHORIZATION_REVISION_REQUIRED
```

`DOMAIN_3_CORPUS_NOT_MATERIALIZABLE` is a valid research result and must route
to negative closeout.
