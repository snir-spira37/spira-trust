# Claude Native Usage Telemetry Invocation Repair Probe Report

## Status

```text
CLAUDE_NATIVE_USAGE_TELEMETRY_INVOCATION_REPAIR_PROBE_PASS
SIX_UNSCORED_TELEMETRY_PROBES_ONLY
READINESS_RERUN_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
session count: 6
schema valid: 6 / 6
correct: 6 / 6
JSON result envelope present: 6 / 6
structured_output present: 6 / 6
usage available: 6 / 6
permission denials: 0
false PROCEED: 0
workspace mutations: 0
repository mutation observed: false
forbidden tool calls: 0
```

## Cell Summary

- pytest_result synthetic_clean_success arm B CRITICAL_ARM_B: exact=2/2 envelope=2/2 structured=2/2 usage=2/2
- pytest_result synthetic_clean_success arm C MATCHED_ARM_C: exact=1/1 envelope=1/1 structured=1/1 usage=1/1
- technical_probe read_nonce arm N/A READ_NONCE_TECHNICAL_PROBE: exact=3/3 envelope=3/3 structured=3/3 usage=3/3

## Errors

- none
