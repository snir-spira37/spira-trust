# Nesira Phase 2 Public Dry-Run Exposure Readiness Plan

## Status

```text
DOCUMENT_TYPE: READINESS PLAN
PHASE: PHASE_2_PUBLIC_DRY_RUN_EXPOSURE_READINESS_GATE
SCOPE: READINESS_ONLY

IMPLEMENTATION: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
PUBLICATION: NOT_AUTHORIZED
```

## Recommendation

The safest first public exposure, if any, is:

```text
Option B: public library module only
```

Rationale:

```text
smaller public surface than CLI
no exit-code ambiguity for users
no help text or examples that can be misread as runner behavior
no command-line affordance that resembles execution
```

Public CLI exposure should remain a later, higher-risk gate.

## Options

### Option A: No Public Exposure

Keep the dry-run evaluator internal only.

Pros:

```text
no new public surface
no release required
no claim risk
```

Cons:

```text
external users cannot inspect the dry-run artifact directly from the package
```

### Option B: Public Library Module Only

Add the evaluator module to the public wheel allowlist, with no console entry
point and no CLI flag.

Pros:

```text
smallest useful public surface
no exit-code semantics
JSON artifact remains data-only
easier to test post-install
```

Cons:

```text
requires version bump and release
requires public claim and release notes
changes wheel content and SHA
```

### Option C: Public Read-Only CLI

Expose a public command or subcommand that emits the dry-run artifact.

Pros:

```text
easier for users
```

Cons:

```text
exit code can be misread
help text becomes claim surface
examples can look like runbooks
larger public surface
```

### Option D: Public CLI + Docs

Highest-risk option in this family. Not recommended as first exposure.

## Required RC For Option B

If Option B is chosen later, the RC must include:

```text
version bump
public wheel allowlist update for spira_core/nesira_phase2_dry_run_runner.py
no pyproject console entry point
no public CLI flag
release notes using approved claim draft
post-install import and artifact test
full pytest
V1 SHA256SUMS self-check
public wheel content check
TestPyPI dry-run
```

If `tools/build_spira_trust_public.py` changes, and if that file is V1-pinned
in the external reproduction package, the RC must include a narrow V1 manifest
refresh for that file only.

## Required RC Tests

```text
from installed wheel, import spira_core.nesira_phase2_dry_run_runner
evaluate strongest dry-run path
assert ACTION_NOT_PERFORMED is carried
assert no executable keys are emitted
assert no public console entry point was added
assert base dependency posture remains intentional
assert actual execution modules are absent
```

## Public Text Checklist

Any release notes must include:

```text
dry-run is not execution
dry-run is not action authorization
ACTION_NOT_PERFORMED is always carried
separate execution authorization remains required
actual execution remains out of scope
reproduction is not certification
```

Forbidden:

```text
ready to run
safe to run
permission granted
action authorized
runner
executes
severance authorized
automatic remediation
security guarantee
certified/audited/endorsed
```

## Stop Conditions

Stop before any future RC if:

```text
public CLI is required for first exposure
release notes cannot keep ACTION_NOT_PERFORMED prominent
wheel exposure requires adding execution code
post-install tests cannot prove no executable fields
V1 narrow refresh scope cannot be kept narrow
```

## Next Step

If Snir chooses public dry-run exposure, open a separate release-candidate
authorization for Option B. This readiness plan does not authorize that RC.
