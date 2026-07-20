# Nesira Phase 2 Dry-Run Exposure Cold Verification

## Verdict

```text
NESIRA_PHASE2_DRY_RUN_EXPOSURE_COLD_VERIFICATION_ACCEPTED
```

The internal read-only dry-run exposure was reproduced from a fresh clone at:

```text
commit: 797c825dfeba16687918f58df63c359df275cf3c
branch: codex/formal-core-v1-lean
clone: fresh external workspace clone
```

## Results

```text
targeted exposure pytest:
  tests/test_nesira_phase2_dry_run_exposure.py
  9 passed

full pytest:
  387 passed

V1 SHA256SUMS self-check:
  622 OK / 0 FAILED

public wheel rebuild:
  spira_trust-0.7.1-py3-none-any.whl
  sha256=297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
  dry_run_module_present=False
  dry_run_tool_present=False
  metadata_dry_run_mentions=False
```

## Scope Accepted

Accepted:

```text
internal read-only source-tree dry-run review tool
JSON-in / JSON-out local review surface
exit code = tool success only
clean JSON error on malformed input
public wheel non-exposure
```

Still blocked:

```text
public wheel exposure
public CLI exposure
pyproject entry point
version bump
release
public claim expansion
runner execution
subprocess/filesystem/network behavior
severance action
automatic remediation
```

## Boundary

The public wheel remains byte-identical to the published 0.7.1 artifact. The
dry-run evaluator and internal exposure tool remain absent from the wheel and
metadata.

No public product behavior changed in this gate.

## Next Safe Gate

The next possible gate is:

```text
NESIRA_PHASE2_PUBLIC_DRY_RUN_EXPOSURE_READINESS
```

That gate would be a human-gated decision about whether this internal dry-run
surface should ever become public. Actual execution remains separately blocked.
