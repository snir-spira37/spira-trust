# SPIRA Formal Core V1 Adapter Boundary Inventory Report



Status:



```text

SPIRA_FORMAL_CORE_V1_ADAPTER_BOUNDARY_INVENTORY_ACCEPTED

```



## Summary



This inventory maps the remaining raw-adapter boundary after acceptance of the Formal Core V1 typed-evidence proof package and local integration boundary.



```json

{
  "adapter_tests_pass": true,
  "all_three_domains_inventoried": true,
  "authorization_present": true,
  "formal_core_proof_package_preserved": true,
  "full_pytest_pass": true,
  "integration_boundary_preserved": true,
  "no_live_sessions": true,
  "no_product_source_implementation_changes": true,
  "production_claim_absent": true,
  "raw_parser_proof_claim_absent": true,
  "release_not_authorized": true
}

```



## Domain Inventory



### python_artifact

Boundary: Domain 1 identity baseline record consumed by mvp_unified.wrap_domain1_record.

Accepted corpus: 1954 / 1954 accepted identity baseline records

Not formally proved:

```text
wheel parsing
ZIP/RECORD parsing
metadata parsing
SBOM extraction
filesystem correctness
```

### pytest_result

Boundary: test_build_failure_producer emits produced_policy_action, produced_claims, explicit lists, evidence locators, and not_claimed.

Accepted corpus: 38 / 38 accepted pytest cases; 6 / 6 mutation pairs

Not formally proved:

```text
raw console parsing completeness
JUnit XML semantic parsing
metadata JSON parser correctness
file IO correctness
```

### terraform_plan

Boundary: terraform_plan_producer emits produced_policy_action, produced_claims, explicit lists, evidence locators, context, and not_claimed.

Accepted corpus: 40 / 40 accepted Terraform Plan cases; 10 / 10 mutation pairs

Not formally proved:

```text
Terraform JSON parser correctness
JSON pointer extraction completeness
Terraform plan schema completeness
file IO correctness
```



## Recommended Next Track



```text

DOMAIN_2_RAW_ADAPTER_CONFORMANCE_SPECIFICATION

```



## Claim Boundary



Allowed: Formal Core V1 has an accepted typed-evidence proof package and a documented raw-adapter boundary inventory for Domain 1, Domain 2, and Domain 3.



Disallowed: SPIRA has formally proved raw wheel/ZIP parsing, pytest/JUnit parsing, Terraform Plan JSON parsing, Python runtime behavior, live agent behavior, or release readiness.
