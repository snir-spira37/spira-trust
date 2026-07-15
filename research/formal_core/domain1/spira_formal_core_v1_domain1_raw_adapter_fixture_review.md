# SPIRA Formal Core V1 Domain 1 Raw Adapter Fixture Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURES_ACCEPTED
RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_FORMALLY_PROVED_NO
PACKAGE_SAFETY_FORMALLY_PROVED_NO
DOMAIN_1_ADAPTER_IMPLEMENTATION_NOT_AUTHORIZED
LIVE_AGENT_SESSIONS_NOT_INCLUDED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Domain 1 raw adapter fixture corpus is accepted.

## Evidence

```json
{
  "action_distribution": {
    "REPORT_NOT_EVALUATED": 25,
    "STOP_BLOCKED": 8
  },
  "coverage": {
    "accepted_identity_baseline": 3,
    "artifact_hash_mismatch": 3,
    "artifact_identity_present": 3,
    "claims_root_mismatch": 3,
    "incomplete_evidence": 2,
    "internal_adapter_failure": 2,
    "previous_version_context_unknown": 3,
    "private_sensitive_path": 2,
    "record_matching": 3,
    "record_missing_or_malformed": 3,
    "sbom_missing": 2,
    "sbom_present_unverified": 2,
    "unsupported_format": 2
  },
  "coverage_pass": true,
  "fixture_count": 33
}
```

## Boundary

The fixtures specify expected raw-to-typed behavior for a future Domain 1 adapter implementation. They do not prove raw wheel/ZIP parsing, RECORD parsing, SBOM parsing, package safety, dependency safety, malware absence, or runtime behavior.

## Next Step

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_HARNESS_AUTHORIZATION
```
