# Nesira Phase 2 Publication Staging Runtime Packaging Fix

## Verdict

```text
NESIRA_PHASE2_PUBLICATION_STAGING_RUNTIME_PACKAGING_FIX_LOCAL_ACCEPTED
NEXT_EXTERNAL_STAGING_REQUIRES_RENEWED_GO_1_FOR_CHANGED_WHEEL_SHA
```

## Scope

This record documents a narrow publication-staging fix found during GO #1
TestPyPI dry-run preparation. It does not publish, tag, upload to real PyPI, or
create a GitHub release.

## Blocker Found

The TestPyPI Trusted Publishing workflow run:

```text
https://github.com/snir-spira37/spira-trust/actions/runs/29689814443
```

failed before TestPyPI upload in the `Generate SPIRA self-evidence` step. The
wheel build and base wheel install succeeded.

Local reproduction showed the blocking runtime packaging issue:

```text
ModuleNotFoundError: No module named 'spira_core.unification_proof'
```

The public wheel included `spira_core/agent_summary.py`, which imports
`spira_core/unification_proof.py`, but the public wheel allowlist omitted
`spira_core/unification_proof.py`.

The optional `cryptography==49.0.0` extra being absent from the base wheel is
not the blocking issue. Source-tree self-evidence over the candidate wheel
returns `GRAPH_OK_WITH_UNVERIFIED` / `GRAPH_OK_WITH_NOTES` with exit code 0,
which is the existing non-blocking semantics for a missing optional extra.

## Fix

```text
tools/build_spira_trust_public.py:
  add spira_core/unification_proof.py to the explicit public wheel allowlist

tests/test_nesira_phase2_read_only_assessment_exposure.py:
  assert unification_proof.py is present
  install the built public wheel into an isolated target
  run spira_core.trust_cli graph from the installed wheel
  assert graph exits 0 and writes unification_proof.json
```

## Local Verification

```text
targeted public-wheel graph runtime tests: PASS
Nesira Phase 2 targeted suite: 64 passed
full pytest: 350 passed
Formal Core V1 SHA256SUMS self-check: 622/622
public wheel rebuild: PASS
new wheel: spira_trust-0.7.0-py3-none-any.whl
new wheel sha256: 956f15e0421d9ec3dabaf10e1ded75318af8834885b95d45620580119b3f57b5
release self-evidence from installed wheel: PASS
trust exit: 0
graph exit: 0
decision: GRAPH_OK_WITH_UNVERIFIED / GRAPH_OK_WITH_NOTES
```

## Boundary

```text
real PyPI upload: NOT_AUTHORIZED
GitHub release publication: NOT_AUTHORIZED
git tag v0.7.0: NOT_PERFORMED
GitHub release draft: NOT_PERFORMED
TestPyPI upload after this fix: NOT_PERFORMED
```

Because the wheel bytes changed, the previously accepted wheel SHA
`29a52445a5045c76264fcce60df5288836cbe870193411c9b84d16ad9e454c6b` is
historical only. Any further GO #1 staging must explicitly refer to the new
wheel SHA:

```text
956f15e0421d9ec3dabaf10e1ded75318af8834885b95d45620580119b3f57b5
```

