# SPIRA Formal Core V1 Domain 2 Raw Adapter Fixture Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURES_ACCEPTED
RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO
DOMAIN_2_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 2 raw adapter fixture corpus is accepted.

## Evidence

```json
{
  "coverage": {
    "assertion_failure": 3,
    "clean_success": 3,
    "collection_error": 2,
    "console_junit_conflict": 2,
    "identity_mismatch": 2,
    "incomplete_evidence": 2,
    "internal_adapter_failure": 2,
    "malformed_junit": 2,
    "malformed_metadata_json": 2,
    "nonblocking_note": 2,
    "unsupported_format": 2,
    "withheld_raw_output": 2
  },
  "coverage_pass": true,
  "fixture_count": 26
}
```

## Boundary

The fixtures specify expected raw-to-typed behavior for a future Domain 2 adapter implementation. They do not prove raw parser correctness.

## Next Step

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_IMPLEMENTATION_AUTHORIZATION
```
