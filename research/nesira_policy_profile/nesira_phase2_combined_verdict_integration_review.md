# Nesira Phase 2 Combined Verdict Integration Review

## Verdict

```text
NESIRA_PHASE2_COMBINED_VERDICT_INTEGRATION_ACCEPTED
```

## Scope

This review evaluates the implementation of the Nesira Phase 2 combined verdict
integration gate.

It does not authorize release, version bump, runner behavior, severance action,
or public claim expansion.

## Implementation Reviewed

```text
implementation_commit: 167cce2
changed_source:
  source/spira_core/combined_verdict.py
added_tests:
  tests/test_nesira_phase2_combined_verdict_integration.py
```

## Conservative Integration

The integration is monotonic and fail-closed:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS -> OK
TRUST_INSUFFICIENT                   -> BLOCK
TRUST_NOT_EVALUATED                  -> NOT_EVALUATED
```

`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS` cannot improve an existing `BLOCK` or
`WARN` layer. It only contributes an `OK` layer to the existing worst-wins
combined-verdict aggregation.

Review finding: PASS.

## Explicit Opt-In

No Nesira input and no explicit Nesira requirement leaves the existing combined
verdict behavior unchanged. The layer is introduced only when an explicit
assessment artifact or explicit requirement is supplied.

Review finding: PASS.

## Conditionality

The combined layer carries:

```text
nesira_verdict
nesira_assumptions
nesira_trust_roots_used
nesira_execution_marker
nesira_reason_codes
```

The sufficient isolation path is guarded by `PT-ISOLATION-01`; removing it from
a sufficient isolation assessment produces `BLOCK`.

Review finding: PASS.

## Fail-Closed Guards

The implementation blocks or stops on:

```text
forbidden action-like field
execution marker mismatch
missing assumptions on sufficient
missing PT-ISOLATION-01 on sufficient isolation path
malformed assessment
missing required assessment
unknown verdict
```

Review finding: PASS.

## V1 Boundary

`combined_verdict.py` is part of the V1 external reproduction package. The
implementation therefore required a narrow V1 manifest refresh.

The refresh was limited to:

```text
source/spira_core/combined_verdict.py
research/formal_core/external_reproduction_package/artifact_manifest.json
```

V1 claims, inventory, expected results, and the historical protected-surface
snapshot were not expanded to include Phase 2.

Review finding: PASS.

## Verification

Local verification:

```text
focused tests: 49 passed
full pytest: 361 passed
V1 SHA256SUMS: 622/622
V1 Phase2/Nesira scope hits: 0
```

Cold reproduction from a fresh clone at `167cce2`:

```text
focused tests: 49 passed
V1 SHA256SUMS: 622/622
full pytest: 361 passed
```

Review finding: PASS.

## Still Blocked

```text
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```
