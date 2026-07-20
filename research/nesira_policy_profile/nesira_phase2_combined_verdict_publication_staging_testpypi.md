# Nesira Phase 2 Combined Verdict TestPyPI Staging Record

## Verdict

```text
NESIRA_PHASE2_COMBINED_VERDICT_TESTPYPI_STAGING_ACCEPTED
```

## Scope

This record covers GO #1 TestPyPI staging for the accepted `spira-trust` 0.7.1
combined verdict release candidate.

This record does not authorize or perform real PyPI upload, GitHub release
publication, git tag push, runner execution, or severance action.

## Accepted Candidate

```text
publication_readiness_commit: 5293497
candidate_version: 0.7.1
candidate_wheel: spira_trust-0.7.1-py3-none-any.whl
candidate_wheel_sha256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
```

## Workflow Run

The accepted TestPyPI dry-run was:

```text
workflow: testpypi-trusted-publishing.yml
run_id: 29750223929
run_number: 5
event: workflow_dispatch
branch: codex/formal-core-v1-lean
head_sha: 5293497cb99cf716241d22d2b65bdfbaf83e800e
conclusion: success
url: https://github.com/snir-spira37/spira-trust/actions/runs/29750223929
```

An earlier manual workflow-dispatch attempt was accidentally run on `main`:

```text
run_id: 29749659900
run_number: 4
branch: main
head_sha: 4656bc98d53b0e2803b823fe01a7d13a8bcea9e2
conclusion: failure
real_pypi_upload: none
testpypi_0_7_1_upload: none
```

The failed `main` attempt did not publish `spira-trust` 0.7.1 to TestPyPI and
did not touch real PyPI or GitHub Releases.

## TestPyPI Artifact

TestPyPI reports:

```text
version: 0.7.1
file: spira_trust-0.7.1-py3-none-any.whl
sha256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
size: 751670
```

This matches the accepted release-candidate wheel SHA256.

## Installation Checks

Base install from TestPyPI:

```text
command: pip install --no-cache-dir --no-deps -i https://test.pypi.org/simple/ spira-trust==0.7.1
version: spira-trust 0.7.1
cryptography_present: false
```

Optional extra install from TestPyPI plus PyPI dependency index:

```text
command: pip install --no-cache-dir -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ "spira-trust[nesira-assessment]==0.7.1"
version: spira-trust 0.7.1
cryptography_version: 49.0.0
```

Installed command surface:

```text
spira-trust version: spira-trust 0.7.1
spira-trust graph --help: exit 0
python -m spira_core.trust_cli --help: exit 0
```

## External Surfaces

Immediately after TestPyPI staging:

```text
real PyPI spira-trust 0.7.1: absent / 404
GitHub release v0.7.1: absent / 404
remote tag v0.7.1: absent before staging checks
```

## Boundary

GO #1 covered TestPyPI staging only.

```text
PYPI_UPLOAD_REAL: NOT_EXECUTED
GITHUB_RELEASE_PUBLICATION: NOT_EXECUTED
GIT_TAG_PUSH: NOT_EXECUTED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```

GO #2 remains a separate human decision owned by Snir.
