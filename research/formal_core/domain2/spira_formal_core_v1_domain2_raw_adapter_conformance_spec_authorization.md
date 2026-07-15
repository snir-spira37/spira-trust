# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Specification Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_SPEC_AUTHORIZED
```

## Purpose

This authorization opens a specification-only phase for the Domain 2 raw adapter boundary.

Domain 2 is the first adapter track because the accepted adapter boundary inventory identifies it as the smallest useful raw-input surface:

```text
console text
JUnit XML text
metadata JSON
public run materialization JSON
```

## Scope

Authorized:

```text
DOMAIN_2_RAW_ADAPTER_CONFORMANCE_SPECIFICATION_ONLY
RAW_INPUT_TO_TYPED_EVIDENCE_MAPPING_SPEC
SUPPORTED_INPUT_LANGUAGE_SPEC
UNSUPPORTED_AND_MALFORMED_INPUT_BEHAVIOR_SPEC
FAIL_CLOSED_ADAPTER_OBLIGATIONS
REQUIRED_FIXTURE_CORPUS_PLAN
DIFFERENTIAL_CONFORMANCE_PLAN
REVIEW
```

Authorized files:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_spec.md
research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_spec_review.md
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
NEW_FIXTURE_MATERIALIZATION
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_PARSER_PROOF_CLAIM
PRODUCTION_CLAIM
RELEASE
```

## Required Specification Questions

The specification must answer:

```text
1. What raw Domain 2 inputs are in scope?
2. What input states are supported, unsupported, malformed, incomplete, or conflicting?
3. What typed-evidence fields must the adapter emit?
4. Which raw observations map to blocking_items, not_evaluated, reason_codes, and not_claimed?
5. What adapter failures must fail closed?
6. What fixtures are required before implementation?
7. What differential checks are required against existing Python behavior?
8. What claim remains disallowed after this specification?
```

## Acceptance Boundary

If accepted, this specification may authorize only a later fixture/materialization or implementation authorization.

It must not itself claim that raw pytest/JUnit parsing is formally proved.
