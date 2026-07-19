# Nesira Phase 2 Publication Record

## Verdict

```text
NESIRA_PHASE2_PUBLICATION_BLOCKED
NESIRA_PHASE2_TESTPYPI_DRY_RUN_ACCEPTED
NESIRA_PHASE2_PRODUCTION_TAG_PUSH_PRE_UPLOAD_GUARD_FAILED
```

## Scope

This record documents GO #1 staging and the first GO #2 production attempt for
the refreshed 0.7.0 read-only assessment release candidate.

The GO #2 tag push was performed, but the production workflow stopped before
real PyPI upload and before GitHub release publication.

## Candidate

```text
version: 0.7.0
publication_authorization_commit: 3559bcf20e89130bafefa7d7cb29f41f712d533e
candidate_code_commit: cdceab25292e7d4522865df09f9695468990b3f9
wheel: spira_trust-0.7.0-py3-none-any.whl
wheel_sha256: 956f15e0421d9ec3dabaf10e1ded75318af8834885b95d45620580119b3f57b5
```

## GO #1

GO #1 was received from Snir for TestPyPI dry-run only:

```text
TestPyPI dry-run via workflow_dispatch
no tag
no GitHub release
no real PyPI
```

## TestPyPI Workflow

```text
workflow: testpypi-trusted-publishing.yml
run_id: 29692127879
run_url: https://github.com/snir-spira37/spira-trust/actions/runs/29692127879
head_sha: 3559bcf20e89130bafefa7d7cb29f41f712d533e
conclusion: success
```

The workflow built the public wheel, installed it, generated SPIRA
self-evidence, uploaded release evidence, and published the wheel to TestPyPI.

TestPyPI metadata:

```text
version: 0.7.0
filename: spira_trust-0.7.0-py3-none-any.whl
sha256: 956f15e0421d9ec3dabaf10e1ded75318af8834885b95d45620580119b3f57b5
```

## TestPyPI Install Checks

Base install from TestPyPI:

```text
spira-trust version: 0.7.0
cryptography installed: false
dependencies posture: cryptography appears only as optional extra
```

Extra install from TestPyPI:

```text
package: spira-trust[nesira-assessment]==0.7.0
cryptography version: 49.0.0
```

Installed read-only assessment tool:

```text
sufficient assessment exit: 0
verdict: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
execution_marker: ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
PT-ISOLATION-01 carried: true
malformed input exit: 2
malformed input error schema: NESIRA_PHASE2_READ_ONLY_ASSESSMENT_TOOL_ERROR_V1
traceback leaked: false
local path leaked: false
```

## External Actions

```text
TestPyPI upload: PERFORMED
git tag v0.7.0: PERFORMED
git push tag v0.7.0: PERFORMED
GitHub release draft: NOT_PERFORMED
real PyPI upload: NOT_PERFORMED
GitHub release publication: NOT_PERFORMED
announcement: NOT_PERFORMED
```

## GO #2 Attempt

GO #2 was received from Snir for:

```text
tag: v0.7.0
target: e75b0960ece18c41ebdf73008671043f7b0108c1
action: tag push triggering production workflow
```

Production workflow:

```text
workflow: pypi-production-publish.yml
run_id: 29694289448
run_url: https://github.com/snir-spira37/spira-trust/actions/runs/29694289448
head_sha: e75b0960ece18c41ebdf73008671043f7b0108c1
conclusion: failure
failed_step: Guard release agent summary size
failure: dist/release-evidence/graph/agent_summary.json is 3141 bytes; limit is 3072 bytes
```

The workflow stopped before:

```text
Run previous public version gate
Prepare release evidence assets
Attach evidence to draft GitHub Release
Publish package distributions to PyPI
Publish GitHub Release
```

## Still Blocked

```text
REAL_PYPI_UPLOAD: NOT_PERFORMED
GITHUB_RELEASE_PUBLICATION: NOT_PERFORMED
GITHUB_RELEASE_DRAFT: NOT_PERFORMED
PRODUCTION_RELEASE_NOTES_WORKFLOW_MISMATCH: RESOLVED
PRODUCTION_AGENT_SUMMARY_SIZE_GUARD: FAILED_BEFORE_UPLOAD
TAG_V0_7_0_REMOTE_EXISTS: TRUE
COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

## Boundary

TestPyPI is a staging dry-run. It is not a production release, not a public
claim, not a GitHub release, not a real PyPI upload, not combined verdict
integration, not runner behavior, and not severance action.

No real PyPI upload or production GitHub release publication occurred. Any
retry that retargets, deletes, or recreates `v0.7.0` requires a separate,
explicit human authorization because the tag is already public.
