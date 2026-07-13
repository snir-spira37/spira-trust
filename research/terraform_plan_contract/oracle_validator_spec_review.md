# Terraform Plan Oracle Validator Specification Review

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED
ORACLE_VALIDATOR_SPEC_REVIEW_COMPLETE
SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
VALIDATOR_IMPLEMENTATION_AUTHORIZATION_REQUIRED_NEXT
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
spec: research/terraform_plan_contract/oracle_validator_spec.md
schema: research/terraform_plan_contract/oracle_schema_v1.schema.json
schema_review: DOMAIN_3_TERRAFORM_PLAN_ORACLE_SCHEMA_ACCEPTED
corpus: DOMAIN_3_TERRAFORM_PLAN_CORPUS_ACCEPTED
review_type: SOLO_MAINTAINER_PROCESS_SEPARATION_REVIEW
```

## Review Checklist

```text
Schema V1 validation: PASS
canonical hash recomputation: PASS
case/reference integrity: PASS
relationship symmetry: PASS
strict-list equivalence: PASS
resource action-sequence validation: PASS
replace_paths consistency: PASS
unknown-path representation: PASS
sensitive-value absence: PASS
optional provenance states: PASS
action/stop consistency: PASS
machine-readable PASS / FAIL / TOOL_ERROR: PASS
negative fixture requirements: PASS
oracle population remains blocked: PASS
validator implementation remains blocked: PASS
producer remains blocked: PASS
```

## Scope Review

The specification is correctly scoped to validation of future oracle documents
against:

```text
accepted Oracle Schema V1
accepted 40-case Terraform Plan corpus
accepted corpus manifest root:
28cdea89c9fc26d9230e8788726abf73e076c268044cd2dff1bf3f67f50ef79c
```

It does not authorize oracle population or implementation code.

## Processing Order Review

The required order is accepted:

```text
parse JSON
validate full Schema V1
bind to accepted corpus
recompute hashes
validate references and relationships
validate lists and Terraform semantics
emit machine-readable output
```

This prevents a future implementation from replacing full schema validation
with a narrow top-level shape check.

## Hash Recalculation Review

The specification requires recomputation rather than format-only hash checks.
It covers:

```text
manifest file hashes
subject.sha256 from exact Terraform Plan bytes
canonical expected_claims bytes
claims Merkle root
policy/action bytes
context_sha256 from a declared Domain 3 context projection
unification_id_expected from accepted Gate A assembly inputs
```

The fail-closed rule is accepted:

```text
canonical bytes unavailable
-> CANONICAL_BYTES_NOT_AVAILABLE
-> ORACLE_VALIDATION_FAILED
```

This avoids the Domain 2 hash-only failure mode.

## Corpus Binding Review

The spec requires:

```text
40 / 40 accepted case IDs
10 / 10 accepted mutation pair IDs
no extra oracle cases
no missing oracle cases
all file hashes recomputed against the accepted manifest
producer output observed: false
```

This is sufficient for the validator contract. Cross-case comparison remains a
validator task, not a JSON Schema task.

## Resource Semantics Review

The spec correctly treats Terraform action sequences as identity-bearing:

```text
["delete","create"] != ["create","delete"]
```

It also requires evidence-derived checks for:

```text
create/update/delete/read/no-op
replace
replace_paths
unknown_paths
sensitive_paths
```

This preserves the Terraform Plan evidence contract without claiming apply
success, live state freshness, cost, security, compliance, or safety.

## Strict List Review

The strict-list contract is accepted:

```text
missing item -> FAIL
extra item -> FAIL
wrong canonical order -> FAIL
duplicate item -> FAIL
```

The explicit lists must match recomputed evidence and claims, not merely be
well-formed arrays.

## Optional Provenance Review

The spec preserves the V1 provenance states:

```text
BOUND
NOT_PROVIDED
NOT_APPLICABLE
```

It correctly requires BOUND provenance to be recomputable from source bytes or
declared canonical fingerprint inputs, and to fail closed otherwise.

## Machine Output Review

The PASS / FAIL / TOOL_ERROR distinction is accepted:

```text
malformed oracle JSON -> FAIL / ORACLE_VALIDATION_FAILED
schema failure -> FAIL / ORACLE_VALIDATION_FAILED
semantic validation failure -> FAIL / ORACLE_VALIDATION_FAILED
internal validator exception -> TOOL_ERROR / ORACLE_VALIDATOR_TOOL_ERROR
```

This prevents invalid oracle input from being mislabeled as a tooling failure.

## Negative Fixture Review

The required negative fixtures are sufficient for implementation authorization
discussion. They cover schema failures, hash-only failures, corpus binding
failures, resource semantic failures, sensitive-value leakage, provenance
failures, action/stop failures, mutation failures, and producer-output leakage.

## Boundaries

The spec preserves:

```text
oracle population: NOT AUTHORIZED
validator implementation: NOT AUTHORIZED
producer implementation: NOT AUTHORIZED
Gate B: NOT AUTHORIZED
Domain 4: NOT AUTHORIZED
MVP boundary amendment: NOT AUTHORIZED
release/version/tag/PyPI: NOT AUTHORIZED
```

## Verdict

```text
DOMAIN_3_TERRAFORM_PLAN_ORACLE_VALIDATOR_SPEC_ACCEPTED
```

## Next Gate

The next gate may be a narrow implementation authorization document for the
validator.

That authorization must still be separate and explicit. It must not authorize:

```text
oracle population
producer implementation
Gate B
Domain 4
MVP boundary amendment
release/version/tag/PyPI
```
