# Nesira Phase 2 Combined Verdict Integration Report

## Verdict

```text
NESIRA_PHASE2_COMBINED_VERDICT_INTEGRATION_IMPLEMENTED
```

## Scope

This gate integrates an explicit Nesira Phase 2 assessment artifact as a
conservative layer in SPIRA's existing combined verdict machinery.

It does not implement a runner, severance action, release, version bump, or
claim expansion.

## Implementation

Changed source:

```text
source/spira_core/combined_verdict.py
```

Added tests:

```text
tests/test_nesira_phase2_combined_verdict_integration.py
```

The integration adds a new optional layer:

```text
layer: nesira_phase2_assessment
source: report["nesira_phase2_assessment"] or bom["nesira_phase2_assessment"]
```

The layer is not enabled by default. Existing calls without explicit Nesira
input do not include the layer and keep existing behavior.

## Mapping

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS -> OK
TRUST_INSUFFICIENT                   -> BLOCK
TRUST_NOT_EVALUATED                  -> NOT_EVALUATED
missing required Nesira assessment   -> NOT_EVALUATED
malformed Nesira assessment          -> NOT_EVALUATED
forbidden execution-like field       -> BLOCK
execution_marker mismatch            -> BLOCK
missing assumptions on sufficient    -> BLOCK
missing PT-ISOLATION-01 on sufficient isolation path -> BLOCK
```

## Invariants

```text
NO_DEFAULT_NESIRA_REQUIREMENT: PASS
NO_NESIRA_UPGRADE_BLOCK: PASS
NO_NESIRA_UPGRADE_WARN: PASS
FAIL_CLOSED_MALFORMED_NESIRA: PASS
NOT_EVALUATED_IS_NOT_PASS: PASS
CONDITIONALITY_VISIBLE: PASS
ASSESSMENT_NOT_EXECUTION: PASS
```

## Verification

Focused tests:

```text
python -m pytest tests/test_nesira_phase2_combined_verdict_integration.py \
  tests/test_agent_memory_v0.py \
  tests/test_unification_proof.py
```

Result:

```text
49 passed
```

Full test suite:

```text
python -m pytest
361 passed
```

V1 external reproduction boundary:

```text
SHA256SUMS self-check: 622/622
Phase2/Nesira hits in V1 claims/inventory/expected-results: 0
```

The V1 manifest refresh is narrow and covers only:

```text
source/spira_core/combined_verdict.py
research/formal_core/external_reproduction_package/artifact_manifest.json
```

The historical protected-surface inventory remains pinned to its original
snapshot and was not refreshed to HEAD.

## Still Blocked

```text
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```
