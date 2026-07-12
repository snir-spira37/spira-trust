# Test/Build Failure Contract Corpus Materialization Report

Status:

```text
DOMAIN_2_CORPUS_MATERIALIZED
DOMAIN_2_PUBLIC_RUN_MATERIALIZED
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
```

Case count: 38

Strata counts:

```json
{
  "public_reproducible_run": 8,
  "synthetic": 30
}
```

Mutation pairs: 6

Public real-world raw outputs are not committed. They were materialized and are represented by public repository identities, pinned commits, generation instructions, dependency environments, exit codes and hashes of withheld run outputs.

Public run materialization:

| case_id | exit_code | raw output publication |
| --- | ---: | --- |
| public_click_import | 0 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_click_param | 0 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_flask_clean | 0 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_flask_param | 0 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_flask_unicode_path | 1 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_requests_assertion | 4 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_requests_clean | 1 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |
| public_requests_long_traceback | 1 | WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW |

Synthetic raw evidence is committed because it contains no private data.

Validation:

```json
{
  "case_count": 38,
  "dependency_environment_recorded": "PASS",
  "json_validation": "PASS",
  "mutation_pair_count": 6,
  "oracle_population": "NOT_AUTHORIZED",
  "path_scan": "PASS",
  "privacy_scan": "PASS",
  "producer_implementation": "NOT_AUTHORIZED",
  "public_run_case_count": 8,
  "public_run_exit_codes": {
    "public_click_import": 0,
    "public_click_param": 0,
    "public_flask_clean": 0,
    "public_flask_param": 0,
    "public_flask_unicode_path": 1,
    "public_requests_assertion": 4,
    "public_requests_clean": 1,
    "public_requests_long_traceback": 1
  },
  "public_run_materialization": "DOMAIN_2_PUBLIC_RUN_MATERIALIZED",
  "public_run_output_hashes_present": "PASS",
  "public_run_output_publication_statuses": {
    "public_click_import": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_click_param": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_flask_clean": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_flask_param": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_flask_unicode_path": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_requests_assertion": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_requests_clean": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW",
    "public_requests_long_traceback": "WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW"
  },
  "raw_evidence_exclusion_check": "PASS",
  "schema": "SPIRA_DOMAIN2_CORPUS_MATERIALIZATION_RESULTS",
  "schema_version": 1,
  "secret_scan": "PASS",
  "status": "DOMAIN_2_CORPUS_MATERIALIZED",
  "strata_counts": {
    "public_reproducible_run": 8,
    "synthetic": 30
  }
}
```

This report does not authorize oracle population.
