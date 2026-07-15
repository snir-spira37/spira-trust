# SPIRA Formal Core V1 Domain 1 Raw Adapter Conformance Harness Authorization

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_HARNESS_AUTHORIZED
```

## Purpose

This authorization opens a deterministic reference/conformance harness for the accepted Domain 1 raw Python artifact adapter fixture corpus.

The harness may evaluate synthetic raw fixtures against the accepted Domain 1 raw-adapter mapping specification. It must not change any production adapter or parser.

## Scope

Authorized:

```text
REFERENCE_FIXTURE_ADAPTER_HARNESS_ONLY
SYNTHETIC_RAW_PYTHON_ARTIFACT_FIXTURE_TO_TYPED_EVIDENCE_PROJECTION
EXPECTED_CONTRACT_COMPARISON
FIXTURE_HASH_VALIDATION
IDENTITY_HASH_AND_UNIFICATION_ID_VALIDATION
FOCUSED_TESTS
FULL_PYTEST
RESULTS_REPORT_AND_REVIEW
```

Authorized files:

```text
tools/run_formal_core_v1_domain1_raw_adapter_conformance.py
tests/test_formal_core_v1_domain1_raw_adapter_conformance.py
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_results.json
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_report.md
research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_review.md
```

## Boundaries

Not authorized:

```text
production adapter changes
raw wheel / ZIP parser implementation change
RECORD or SBOM parser implementation change
raw wheel / ZIP / RECORD / SBOM parser proof claim
package safety claim
Lean changes
proof script changes
Python core changes
MVP / passthrough changes
fixture changes
live agent sessions
benchmark execution
result reclassification
production claim
release
```

## Acceptance Gates

Acceptance requires:

```text
33 / 33 fixtures evaluated
33 / 33 fixture hashes match manifest
33 / 33 projected typed evidence matches expected typed evidence
33 / 33 contracts match expected contracts
false PROCEED = 0
blocking item loss = 0
NOT_EVALUATED loss = 0
not_claimed loss = 0
evidence/proof identity loss = 0
identity hash loss = 0
unification ID loss = 0
focused tests PASS
full pytest PASS
```

Even if accepted, this harness only proves conformance of the synthetic fixture mapping. It does not prove arbitrary raw wheel / ZIP parsing, RECORD parsing, SBOM parsing, package safety, dependency safety, malware absence, runtime behavior, or production readiness.
