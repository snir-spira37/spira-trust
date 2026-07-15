# SPIRA Formal Core V1 Domain 1 Raw Adapter Fixture Report

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURES_ACCEPTED
```

Summary:

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

The corpus contains synthetic raw Python artifact adapter fixtures with expected typed-evidence and Formal Core contract outcomes.

No adapter implementation, Lean proof, benchmark, live agent session, production claim, or release is authorized by this fixture corpus.
