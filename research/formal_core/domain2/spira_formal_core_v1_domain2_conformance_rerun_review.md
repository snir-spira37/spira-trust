# SPIRA Formal Core V1 Domain 2 Conformance Rerun Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED
DOMAIN_2_FORMAL_TYPED_SEMANTICS_ACCEPTED
DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED
DOMAIN_2_REPORT_WITH_NOTES_MAPPING_ACCEPTED_IN_CONFORMANCE
RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO
DOMAIN_3_NOT_AUTHORIZED
DOMAIN_1_NOT_AUTHORIZED
RUNTIME_INTEGRATION_NOT_AUTHORIZED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

Domain 2 conformance is accepted under the reviewed action mapping.

The accepted `REPORT_WITH_NOTES` projection is:

```text
REPORT_WITH_NOTES -> PROCEED + TEST_NOTES
```

The Domain 2 oracle and corpus remain unchanged. The previous negative conformance result remains preserved.

## Evidence

```json
{
  "blocking_to_proceed_cases": 0,
  "case_count": 38,
  "case_fail_count": 0,
  "case_pass_count": 38,
  "evidence_drop_cases": 0,
  "identity_drop_cases": 0,
  "lean_build_returncode": 0,
  "mismatch_count": 0,
  "mutation_pair_checks": {
    "passed": 6,
    "total": 6
  },
  "not_evaluated_to_proceed_cases": 0,
  "proof_drop_cases": 0,
  "proof_scan": "PASS",
  "report_with_notes_case_count": 2,
  "test_notes_drops": 0
}
```

## Boundaries

This review does not prove raw pytest/JUnit parsing, Python runtime correctness, filesystem behavior, or production integration.

Domain 3 and Domain 1 conformance remain blocked until separately authorized.

## Verification Notes

```text
lake build: PASS

focused pytest:
tests/test_formal_core_v1_python_boundary.py
tests/test_test_build_failure_producer.py
tests/test_test_build_failure_oracle_validator.py
=> 24 / 24 PASS

full pytest:
244 / 247 PASS
```

The three full-suite failures are existing out-of-scope hash-manifest gates in
passthrough fixture and multi-agent benchmark assets. They are not caused by
the Formal Core V1 Domain 2 conformance files and are not modified or
reclassified by this review.
