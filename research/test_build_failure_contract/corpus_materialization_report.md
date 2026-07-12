# Test/Build Failure Contract Corpus Materialization Report

Status:

```text
DOMAIN_2_CORPUS_MATERIALIZED
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
```

Case count: 38

Strata counts:

```json
{
  "public_reproducible_instruction": 8,
  "synthetic": 30
}
```

Mutation pairs: 6

Public real-world logs are not committed. They are represented by public repository identities, pinned commits, generation instructions and hashes.

Synthetic raw evidence is committed because it contains no private data.

Validation:

```json
{
  "case_count": 38,
  "json_validation": "PASS",
  "mutation_pair_count": 6,
  "oracle_population": "NOT_AUTHORIZED",
  "path_scan": "PASS",
  "privacy_scan": "PASS",
  "producer_implementation": "NOT_AUTHORIZED",
  "raw_evidence_exclusion_check": "PASS",
  "schema": "SPIRA_DOMAIN2_CORPUS_MATERIALIZATION_RESULTS",
  "schema_version": 1,
  "secret_scan": "PASS",
  "status": "DOMAIN_2_CORPUS_MATERIALIZED",
  "strata_counts": {
    "public_reproducible_instruction": 8,
    "synthetic": 30
  }
}
```

This report does not authorize oracle population.
