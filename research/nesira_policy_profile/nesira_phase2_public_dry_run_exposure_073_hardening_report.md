# Nesira Phase 2 Public Dry-Run Exposure 0.7.3 Hardening Report

## Verdict

```text
NESIRA_PHASE2_PUBLIC_DRY_RUN_EXPOSURE_0_7_3_HARDENING_LOCAL_VERIFICATION_ACCEPTED
```

## Why 0.7.3

The 0.7.2 TestPyPI staging passed, but a read-only review found a semantic
hardening gap in the dry-run evaluator:

```text
combined verdict NOT_EVALUATED could still allow the dry-run artifact to report
DRY_RUN_PRECONDITIONS_SATISFIED_NOT_EXECUTION when Nesira and action-authority
inputs were otherwise sufficient.
```

The artifact still carried `ACTION_NOT_PERFORMED`, so this was not an execution
path. It was nevertheless too loose for the dry-run precondition semantics.

Because 0.7.2 had already been uploaded to TestPyPI, the corrected release
candidate is versioned as 0.7.3.

## Hardening

`_evaluate_combined` now treats the following as not evaluated:

```text
winning_status == NOT_EVALUATED
combined_verdict == GRAPH_NOT_EVALUATED
any non-empty not_evaluated_layers
```

BLOCK/WARN/NOTE behavior remains fail-closed. The change only prevents an
unevaluated upstream product-verdict layer from being summarized as satisfied
dry-run preconditions.

## Candidate

```text
version: 0.7.3
wheel: spira_trust-0.7.3-py3-none-any.whl
wheel_sha256: 308b2bd94b96a3911fdce822c35642daa1bfd9452046a4d3e2d6f5092fce6cf5
```

## Verification

Local verification passed:

```text
targeted dry-run/public-wheel/V1 tests: 36 passed
full pytest: 392 passed
V1 SHA256SUMS: 622/622
wheel rebuild determinism: PASS
combined NOT_EVALUATED case: DRY_RUN_NOT_EVALUATED
```

## Boundary

The module remains non-executing. No public CLI, pyproject entry point, tag,
TestPyPI upload, PyPI upload, or GitHub release was performed by this hardening
gate.

0.7.3 requires fresh TestPyPI staging before any GO #2 discussion.
