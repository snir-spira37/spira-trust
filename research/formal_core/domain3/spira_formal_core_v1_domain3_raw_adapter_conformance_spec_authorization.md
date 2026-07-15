# SPIRA Formal Core V1 Domain 3 Raw Adapter Conformance Specification Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_SPEC_AUTHORIZED
```

## Purpose

This authorization opens a specification-only phase for the Domain 3 Terraform Plan raw-adapter boundary.

Domain 3 is the next deterministic adapter track after Domain 2 production alignment.

## Scope

Authorized:

```text
DOMAIN_3_RAW_ADAPTER_CONFORMANCE_SPECIFICATION_ONLY
RAW_TERRAFORM_PLAN_TO_TYPED_EVIDENCE_MAPPING_SPEC
SUPPORTED_INPUT_LANGUAGE_SPEC
UNSUPPORTED_MALFORMED_INCOMPLETE_INPUT_BEHAVIOR_SPEC
SENSITIVE_VALUE_FAIL_CLOSED_OBLIGATIONS
REQUIRED_FIXTURE_CORPUS_PLAN
DIFFERENTIAL_CONFORMANCE_PLAN
REVIEW
```

Authorized files:

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_spec.md
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_spec_review.md
```

## Boundaries

Not authorized:

```text
DOMAIN_3_ADAPTER_IMPLEMENTATION_CHANGE
RAW_TERRAFORM_JSON_PARSER_CHANGE
LEAN_CHANGE
PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
NEW_FIXTURE_MATERIALIZATION
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_TERRAFORM_JSON_PARSER_PROOF_CLAIM
PRODUCTION_CLAIM
RELEASE
```

## Required Specification Questions

The specification must answer:

```text
1. What Terraform Plan raw inputs are in scope?
2. What plan states are supported, unsupported, malformed, incomplete, errored, or sensitive?
3. What typed-evidence fields must the adapter emit?
4. Which observations map to blocking_items, not_evaluated, reason_codes, and not_claimed?
5. How are resource action lists, replace paths, unknown paths, and sensitive paths preserved?
6. What adapter failures must fail closed?
7. What fixtures are required before implementation?
8. What differential checks are required against existing Python behavior?
9. What claim remains disallowed after this specification?
```

## Acceptance Boundary

If accepted, this specification may authorize only a later fixture/materialization authorization.

It must not itself claim that raw Terraform Plan JSON parsing is formally proved.
