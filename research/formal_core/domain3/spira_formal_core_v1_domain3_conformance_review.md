# SPIRA Formal Core V1 Domain 3 Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED
DOMAIN_3_FORMAL_TYPED_SEMANTICS_ACCEPTED
DOMAIN_3_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED
RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO
DOMAIN_1_NOT_AUTHORIZED
RUNTIME_INTEGRATION_NOT_AUTHORIZED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

Domain 3 conformance is accepted for bounded Terraform Plan typed evidence.

The Terraform Plan oracle and corpus remain unchanged.

## Evidence

```json
{
  "action_distribution": {
    "PROCEED": 8,
    "REPORT_NOT_EVALUATED": 2,
    "RERUN_REQUIRED": 1,
    "STOP_BLOCKED": 29
  },
  "blocking_to_proceed_cases": 0,
  "case_count": 40,
  "case_fail_count": 0,
  "case_pass_count": 40,
  "evidence_drop_cases": 0,
  "false_proceed_cases": 0,
  "identity_drop_cases": 0,
  "instruction_override_cases": 0,
  "lean_build_returncode": 0,
  "mismatch_count": 0,
  "mutation_pair_checks": {
    "passed": 10,
    "total": 10
  },
  "not_evaluated_to_proceed_cases": 0,
  "proof_drop_cases": 0,
  "proof_scan": "PASS",
  "sensitive_value_leak_cases": 0,
  "validator": "PASS"
}
```

## Boundaries

This review does not prove raw Terraform JSON parsing, Python runtime correctness, filesystem behavior, or production integration.

Domain 1 conformance remains blocked until separately authorized.
