# SPIRA Formal Core V1 Domain 2 Raw Adapter Fixture Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURES_AUTHORIZED
```

## Purpose

This authorization opens fixture materialization for the accepted Domain 2 raw-adapter conformance specification.

The fixtures provide known expected outcomes for a later implementation phase. They do not implement or prove the adapter.

## Scope

Authorized:

```text
DOMAIN_2_RAW_ADAPTER_FIXTURE_MATERIALIZATION_ONLY
SYNTHETIC_RAW_INPUT_FIXTURES_ONLY
EXPECTED_TYPED_EVIDENCE_OUTPUTS_REQUIRED
EXPECTED_FORMAL_CORE_CONTRACTS_REQUIRED
FIXTURE_MANIFEST_REQUIRED
FIXTURE_REVIEW_REQUIRED
```

Authorized files and directories:

```text
tools/materialize_formal_core_v1_domain2_raw_adapter_fixtures.py
research/formal_core/domain2/raw_adapter_fixtures/
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_fixture_manifest.json
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_fixture_report.md
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_fixture_review.md
```

## Required Coverage

The fixture corpus must cover at least:

```text
3 clean successes
3 assertion failures
2 collection/import errors
2 malformed JUnit/XML cases
2 malformed metadata JSON cases
2 incomplete evidence cases
2 console/JUnit conflict cases
2 withheld raw output cases
2 unsupported format cases
2 nonblocking note cases
2 identity mismatch cases
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
```

## Boundaries

Not authorized:

```text
DOMAIN_2_ADAPTER_IMPLEMENTATION_CHANGE
RAW_PARSER_IMPLEMENTATION_CHANGE
LEAN_CHANGE
PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_PARSER_PROOF_CLAIM
PRODUCTION_CLAIM
RELEASE
```

Acceptance of the fixtures may authorize only a later implementation authorization. It must not claim that raw pytest/JUnit parsing is formally proved.
