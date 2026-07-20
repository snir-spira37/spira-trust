# Nesira Phase 2 Post-Publication Verification

## Verdict

```text
NESIRA_PHASE2_POST_PUBLICATION_VERIFICATION_ACCEPTED
```

## Scope

This record documents a read-only verification of the already published
`spira-trust` 0.7.0 artifacts from public distribution surfaces.

It does not authorize a new release, combined verdict integration, runner
behavior, severance action, or claim expansion.

## Published Artifacts

```text
version: 0.7.0
tag: v0.7.0
tag_target: 72937cc97c8ae79492928fbec6798eed6088f456
PyPI: https://pypi.org/project/spira-trust/0.7.0/
GitHub Release: https://github.com/snir-spira37/spira-trust/releases/tag/v0.7.0
wheel: spira_trust-0.7.0-py3-none-any.whl
wheel_sha256: 0ca716776b54bd8850b1fed0e8ce5d502d17c9ee567c22a5643b2de3aa60b8d7
production_workflow_run: 29737614662
```

## Public Install Checks

The package was installed from real PyPI in a fresh local virtual environment.

Base install:

```text
command: pip install --no-cache-dir spira-trust==0.7.0
installed_version: 0.7.0
cryptography_present: false
public_cli_version: spira-trust 0.7.0
public_cli_help: PASS
```

Optional assessment extra:

```text
command: pip install --no-cache-dir spira-trust[nesira-assessment]==0.7.0
cryptography_version: 49.0.0
read_only_assessment_cli_help: PASS
```

## Read-Only Assessment Smoke

A valid request was generated from the already accepted conformance fixture
shape and passed to the installed public wheel.

```text
command: python -m spira_core.nesira_phase2_read_only_assessment_cli valid_request.json
exit: 0
verdict: TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
execution_marker: ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
PT-ISOLATION-01 carried: true
```

Malformed input check:

```text
command: python -m spira_core.nesira_phase2_read_only_assessment_cli bad_request.json
exit: 2
stderr_schema: NESIRA_PHASE2_READ_ONLY_ASSESSMENT_TOOL_ERROR_V1
traceback_leaked: false
local_path_leaked: false
```

## Boundary

This verification confirms only that the published package installs and the
published read-only assessment surface runs within the already accepted claim
boundary.

It remains:

```text
assessment-only
not execution
not severance authorization
not permission to proceed
not proof that isolation happened
not proof that trust roots are absolutely legitimate
not combined verdict integration
not runner behavior
not independent certification
not audit
not endorsement
not third-party validation
not security guarantee
not trust guarantee
```

## Still Blocked

```text
COMBINED_VERDICT: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
VERSION_CHANGE_AFTER_RELEASE: NOT_AUTHORIZED
PUBLIC_CLAIM_EXPANSION: NOT_AUTHORIZED
```
