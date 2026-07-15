# SPIRA Formal Core V1 Domain 1 Raw Adapter Fixture Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_FIXTURES_AUTHORIZED
```

## Purpose

This authorization opens fixture materialization for the accepted Domain 1 raw-adapter conformance specification.

The fixtures provide known expected outcomes for a later Domain 1 raw-adapter implementation phase. They do not implement, prove, or change the adapter.

## Scope

Authorized:

```text
DOMAIN_1_RAW_ADAPTER_FIXTURE_MATERIALIZATION_ONLY
SYNTHETIC_RAW_PYTHON_ARTIFACT_INPUT_FIXTURES_ONLY
EXPECTED_TYPED_EVIDENCE_OUTPUTS_REQUIRED
EXPECTED_FORMAL_CORE_CONTRACTS_REQUIRED
FIXTURE_MANIFEST_REQUIRED
FIXTURE_REPORT_REQUIRED
FIXTURE_REVIEW_REQUIRED
```

Authorized files and directories:

```text
tools/materialize_formal_core_v1_domain1_raw_adapter_fixtures.py
research/formal_core/domain1/raw_adapter_fixtures/
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_fixture_manifest.json
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_fixture_report.md
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_fixture_review.md
```

## Required Coverage

The fixture corpus must cover at least:

```text
3 accepted identity baseline records
3 artifact identity present records
3 RECORD present and matching records
3 RECORD missing or malformed records
3 artifact hash mismatch records
3 claims root mismatch records
2 SBOM present unverified records
2 SBOM missing records
3 previous-version/context unknown records
2 unsupported format records
2 incomplete evidence records
2 private/sensitive path records
2 internal adapter failure simulations
```

Each fixture must include:

```text
fixture_id
classification
input_state
raw_inputs
expected_typed_evidence
expected_formal_core_contract
expected_legacy_action
expected_action
expected_stop
expected_reason_codes
expected_blocking_items
expected_not_evaluated
expected_not_claimed
expected_evidence_refs
expected_proof_refs
expected_identity_fields
expected_unification_id
```

## Boundaries

Not authorized:

```text
DOMAIN_1_ADAPTER_IMPLEMENTATION_CHANGE
RAW_WHEEL_ZIP_PARSER_IMPLEMENTATION_CHANGE
RECORD_OR_SBOM_PARSER_IMPLEMENTATION_CHANGE
LEAN_CHANGE
PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_PROOF_CLAIM
PACKAGE_SAFETY_CLAIM
PRODUCTION_CLAIM
RELEASE
```

Acceptance of the fixtures may authorize only a later conformance harness authorization. It must not claim that raw wheel / ZIP / RECORD / SBOM parsing, package safety, dependency safety, malware absence, or runtime behavior are formally proved.
