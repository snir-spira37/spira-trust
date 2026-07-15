# SPIRA Formal Core V1 Domain 3 Raw Adapter Fixture Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_FIXTURES_AUTHORIZED
```

## Purpose

This authorization opens fixture materialization for the accepted Domain 3 raw-adapter conformance specification.

The fixtures provide known expected outcomes for a later Domain 3 raw-adapter implementation phase. They do not implement, prove, or change the adapter.

## Scope

Authorized:

```text
DOMAIN_3_RAW_ADAPTER_FIXTURE_MATERIALIZATION_ONLY
SYNTHETIC_RAW_TERRAFORM_PLAN_INPUT_FIXTURES_ONLY
EXPECTED_TYPED_EVIDENCE_OUTPUTS_REQUIRED
EXPECTED_FORMAL_CORE_CONTRACTS_REQUIRED
FIXTURE_MANIFEST_REQUIRED
FIXTURE_REPORT_REQUIRED
FIXTURE_REVIEW_REQUIRED
```

Authorized files and directories:

```text
tools/materialize_formal_core_v1_domain3_raw_adapter_fixtures.py
research/formal_core/domain3/raw_adapter_fixtures/
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_fixture_manifest.json
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_fixture_report.md
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_fixture_review.md
```

## Required Coverage

The fixture corpus must cover at least:

```text
3 no-change plans
3 create/update/delete plans
3 replace plans with replace_paths
2 errored plans
2 not-applyable plans
2 incomplete plans
2 unsupported format plans
2 invalid JSON plans
3 unknown path plans
3 sensitive path plans
2 optional provenance plans
2 duplicate resource-address plans
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
expected_action
expected_stop
expected_reason_codes
expected_blocking_items
expected_not_evaluated
expected_not_claimed
expected_evidence_refs
expected_proof_refs
expected_resource_actions
expected_replace_paths
expected_unknown_paths
expected_sensitive_paths
```

## Boundaries

Not authorized:

```text
DOMAIN_3_ADAPTER_IMPLEMENTATION_CHANGE
RAW_TERRAFORM_JSON_PARSER_IMPLEMENTATION_CHANGE
LEAN_CHANGE
PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_TERRAFORM_JSON_PARSER_PROOF_CLAIM
TERRAFORM_EXECUTION_PROOF_CLAIM
PRODUCTION_CLAIM
RELEASE
```

Acceptance of the fixtures may authorize only a later implementation authorization. It must not claim that raw Terraform Plan JSON parsing, Terraform execution, provider behavior, cloud state, security, compliance, cost, or apply success are formally proved.
