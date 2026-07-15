# SPIRA Formal Core V1 Domain 3 Raw Adapter Fixture Report

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURES_ACCEPTED
```

Summary:

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

The corpus contains synthetic raw Terraform Plan adapter fixtures with expected typed-evidence and Formal Core contract outcomes.

Invalid JSON fixtures expect `RERUN_REQUIRED` according to the accepted Domain 3 policy/action algebra. This is a fixture target for the later adapter implementation phase, not a raw parser proof.

No adapter implementation, Lean proof, benchmark, live agent session, production claim, or release is authorized by this fixture corpus.
