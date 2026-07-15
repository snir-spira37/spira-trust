# SPIRA Formal Core V1 Domain 3 Raw Adapter Fixture Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURES_ACCEPTED
RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO
TERRAFORM_EXECUTION_FORMALLY_PROVED_NO
DOMAIN_3_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 3 raw adapter fixture corpus is accepted.

## Evidence

```json
{
  "action_distribution": {
    "PROCEED": 5,
    "REPORT_NOT_EVALUATED": 10,
    "RERUN_REQUIRED": 2,
    "STOP_BLOCKED": 14
  },
  "coverage": {
    "create_update_delete": 3,
    "duplicate_resource_address": 2,
    "errored_plan": 2,
    "incomplete_plan": 2,
    "internal_adapter_failure": 2,
    "invalid_json": 2,
    "no_change": 3,
    "not_applyable": 2,
    "optional_provenance": 2,
    "replace_path": 3,
    "sensitive_path": 3,
    "unknown_path": 3,
    "unsupported_format": 2
  },
  "coverage_pass": true,
  "fixture_count": 31
}
```

## Boundary

The fixtures specify expected raw-to-typed behavior for a future Domain 3 adapter implementation. They do not prove raw Terraform JSON parsing, Terraform execution, provider behavior, live cloud state, security, compliance, cost, or apply success.

The fixture corpus preserves `RERUN_REQUIRED` as the accepted Domain 3 policy/action target for invalid JSON. A later implementation must reconcile this target with the Formal Core V1 Python reference and accepted action algebra without weakening fail-closed behavior.

## Next Step

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_IMPLEMENTATION_AUTHORIZATION
```
