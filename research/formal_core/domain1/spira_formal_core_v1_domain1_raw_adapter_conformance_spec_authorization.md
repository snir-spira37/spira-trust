# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Specification Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_SPEC_AUTHORIZED
```

## Purpose

This authorization opens a specification-only phase for the Domain 1 Python artifact raw-adapter boundary.

Domain 1 is the final deterministic domain adapter track after accepted Domain 2 and Domain 3 production alignment.

## Scope

Authorized:

```text
DOMAIN_1_RAW_ADAPTER_CONFORMANCE_SPECIFICATION_ONLY
RAW_PYTHON_ARTIFACT_TO_TYPED_EVIDENCE_MAPPING_SPEC
SUPPORTED_INPUT_LANGUAGE_SPEC
UNSUPPORTED_MALFORMED_INCOMPLETE_INPUT_BEHAVIOR_SPEC
IDENTITY_HASH_AND_PROOF_BINDING_OBLIGATIONS
SENSITIVE_OR_PRIVATE_PATH_FAIL_CLOSED_OBLIGATIONS
REQUIRED_FIXTURE_CORPUS_PLAN
DIFFERENTIAL_CONFORMANCE_PLAN
REVIEW
```

Authorized files:

```text
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_spec.md
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_spec_review.md
```

## Boundaries

Not authorized:

```text
DOMAIN_1_ADAPTER_IMPLEMENTATION_CHANGE
RAW_WHEEL_ZIP_PARSER_CHANGE
RECORD_OR_SBOM_PARSER_CHANGE
LEAN_CHANGE
PROOF_SCRIPT_CHANGE
PYTHON_CORE_CHANGE
MVP_OR_PASSTHROUGH_CHANGE
NEW_FIXTURE_MATERIALIZATION
LIVE_AGENT_SESSIONS
BENCHMARK_EXECUTION
RESULT_RECLASSIFICATION
RAW_WHEEL_ZIP_PARSER_PROOF_CLAIM
PACKAGE_SAFETY_CLAIM
PRODUCTION_CLAIM
RELEASE
```

## Required Specification Questions

The specification must answer:

```text
1. What Python artifact raw inputs are in scope?
2. What wheel / ZIP / RECORD / SBOM states are supported, unsupported, malformed, incomplete, blocked, or private?
3. What typed-evidence fields must the adapter emit?
4. Which observations map to blocking_items, not_evaluated, reason_codes, and not_claimed?
5. How are artifact identity, subject identity, claims root, context hash, decision hash, proof hash, and unification identity preserved?
6. How does legacy ASK_HUMAN map to REPORT_NOT_EVALUATED without changing Formal Core action algebra?
7. What adapter failures must fail closed?
8. What fixtures are required before implementation?
9. What differential checks are required against the accepted Domain 1 identity baseline?
10. What claim remains disallowed after this specification?
```

## Acceptance Boundary

If accepted, this specification may authorize only a later fixture/materialization authorization.

It must not itself claim that raw wheel / ZIP / RECORD / SBOM parsing is formally proved.
