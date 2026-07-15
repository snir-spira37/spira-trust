# SPIRA Formal Core V1 Domain 1 Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED
DOMAIN_1_FORMAL_TYPED_SEMANTICS_ACCEPTED
DOMAIN_1_BASELINE_DIFFERENTIAL_CONFORMANCE_ACCEPTED
DOMAIN_1_LEGACY_ASK_HUMAN_MAPPED_TO_REPORT_NOT_EVALUATED
RAW_WHEEL_ZIP_PARSER_FORMALLY_PROVED_NO
GATE_A_IMPLEMENTATION_NOT_AUTHORIZED
RUNTIME_INTEGRATION_NOT_AUTHORIZED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

Domain 1 conformance is accepted for the bounded Python artifact identity baseline.

The accepted Domain 1 identity baseline remains unchanged.

Legacy `ASK_HUMAN` is preserved as a Domain 1 baseline action and maps to the Formal Core V1 non-proceeding action `REPORT_NOT_EVALUATED`; the Formal Core V1 action algebra is unchanged.

## Evidence

```json
{
  "baseline_root_match": true,
  "core_action_distribution": {
    "REPORT_NOT_EVALUATED": 1786,
    "STOP_BLOCKED": 168
  },
  "false_proceed_records": 0,
  "identity_drop_records": 0,
  "lean_build_returncode": 0,
  "legacy_action_distribution": {
    "ASK_HUMAN": 911,
    "REPORT_NOT_EVALUATED": 875,
    "STOP_BLOCKED": 168
  },
  "list_drop_records": 0,
  "mismatch_count": 0,
  "not_evaluated_to_proceed_records": 0,
  "proof_scan": "PASS",
  "record_count": 1954,
  "record_fail_count": 0,
  "record_pass_count": 1954,
  "sensitive_or_private_leak_records": 0,
  "worst_claim_status_distribution": {
    "BLOCK": 168,
    "NOT_EVALUATED": 1786
  }
}
```

## Boundaries

This review does not prove raw wheel / ZIP parsing, RECORD parsing, SBOM parsing, filesystem behavior, Python runtime correctness, or production integration.

No benchmark runner, live agent session, result reclassification, release, tag, or PyPI work is authorized.
