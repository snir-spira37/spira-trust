# Terraform Plan Corpus Materialization Report

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_CORPUS_MATERIALIZED
CORPUS_MATERIALIZATION_RETRY_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_BOUNDARY_UNCHANGED
RELEASE_NOT_AUTHORIZED
```

## Corpus

```text
total cases: 40
authentic Terraform-generated cases: 8
synthetic/controlled cases: 32
mutation pairs: 10
manifest sha256: 28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

## Terraform Environment

```text
Terraform version: 1.15.8
Terraform binary sha256: 6eb0a1cb89344c97ccf2928ddc2d7a6cb71a1837b7ecccfd5991466b6d751e03
provider download observed: false
cloud/live infrastructure used: false
remote backend used: false
```

The authentic cases were generated locally with the built-in Terraform provider
only. No cloud, live infrastructure, Kubernetes, remote backend, or provider
download was used.

## Validation

```text
case count: PASS
unique case IDs: PASS
authentic count: PASS
synthetic count: PASS
mutation pair count: PASS
missing files: 0
hash mismatches: 0
privacy/path/secret scan: PASS
```

## Boundaries

```text
oracle expected answers: NOT_POPULATED
producer output observed: false
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
MVP boundary: UNCHANGED
release/version/tag/PyPI: NOT_AUTHORIZED
```

## Verdict

```text
DOMAIN_3_TERRAFORM_PLAN_CORPUS_MATERIALIZED
```
