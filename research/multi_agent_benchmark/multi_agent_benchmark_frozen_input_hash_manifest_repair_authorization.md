# Multi-Agent Benchmark Frozen Input Hash Manifest Repair Authorization

Status:

```text
MULTI_AGENT_BENCHMARK_FROZEN_INPUT_HASH_MANIFEST_REPAIR_AUTHORIZED
```

## Scope

This authorization permits a narrow manifest repair for the existing frozen multi-agent benchmark input corpus.

Authorized:

```text
EXISTING_FROZEN_INPUT_FILES_ONLY
FROZEN_INPUT_MANIFEST_INPUT_SHA256_FIELDS_ONLY
MECHANICAL_BYTE_HASH_RECOMPUTATION_ONLY
ASSET_VALIDATOR_RERUN_AUTHORIZED
FOCUSED_TEST_RERUN_AUTHORIZED
FULL_PYTEST_RERUN_AUTHORIZED
REPAIR_RESULTS_REPORT_AND_REVIEW_AUTHORIZED
```

The repair may update only `input_sha256` values in:

```text
research/multi_agent_benchmark/frozen_input_manifest.json
```

Each new value must be the SHA-256 digest of the bytes already present at the corresponding `path`.

## Boundaries

Not authorized:

```text
FROZEN_INPUT_CONTENT_CHANGE
CASE_MANIFEST_CHANGE
PROMPT_CHANGE
SCHEMA_CHANGE
ORACLE_CHANGE
COMPARATOR_CHANGE
RANDOMIZATION_CHANGE
BENCHMARK_RUNNER_CHANGE
LIVE_AGENT_SESSIONS
RESULT_RECLASSIFICATION
PRIMARY_BENCHMARK
HOLDOUT
CARRYOVER
DEEPSEEK
EFFICIENCY_CLAIM
RELEASE
```

## Required Evidence

The repair must record:

```text
mismatch_count_before
updated_input_sha256_count
frozen_input_content_changes
manifest_non_hash_semantic_changes
asset_validator_result
focused_test_result
full_pytest_result
```

Acceptance requires:

```text
MULTI_AGENT_BENCHMARK_ASSET_VALIDATION_PASS
test_multi_agent_benchmark_assets PASS
full pytest PASS
frozen_input_content_changes = 0
manifest_non_hash_semantic_changes = 0
```

## Status Boundaries

Even if accepted, this repair does not authorize live sessions, primary benchmark execution, release readiness claims, version bumps, tags, publishing, or result reclassification.
