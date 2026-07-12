# Test/Build Failure Contract Oracle Population Report

Status:

```text
DOMAIN_2_ORACLE_POPULATED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```

Oracle cases populated: 38 / 38

Validator:

```json
{
  "counts": {
    "case_count": 38,
    "declared_delta_count": 6,
    "error_count": 0,
    "relationship_count": 12,
    "warning_count": 0
  },
  "status": "ORACLE_VALIDATION_PASS",
  "verdict": "PASS"
}
```

Population results:

```json
{
  "case_count": 38,
  "explicit_list_validation": "PASS",
  "gate_b": "NOT_AUTHORIZED",
  "identity_recomputation": "PASS",
  "mutation_relationship_validation": "PASS",
  "not_evaluated_validation": "PASS",
  "oracle_path": "research/test_build_failure_contract/oracle_v1.json",
  "path_scan": "PASS",
  "populated_case_count": 38,
  "privacy_scan": "PASS",
  "producer_implementation": "NOT_AUTHORIZED",
  "producer_output_observed": false,
  "schema": "SPIRA_DOMAIN2_ORACLE_POPULATION_RESULTS",
  "schema_validation": "PASS",
  "schema_version": 1,
  "secret_scan": "PASS",
  "status": "DOMAIN_2_ORACLE_POPULATED",
  "validator_counts": {
    "case_count": 38,
    "declared_delta_count": 6,
    "error_count": 0,
    "relationship_count": 12,
    "warning_count": 0
  },
  "validator_status": "ORACLE_VALIDATION_PASS",
  "validator_verdict": "PASS"
}
```

This report does not authorize producer implementation or Gate B.
