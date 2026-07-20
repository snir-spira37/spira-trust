# Nesira Phase 2 Publication Record

## Verdict

```text
NESIRA_PHASE2_PUBLICATION_COMPLETED
```

## Scope

This record documents the completed publication of the accepted `spira-trust`
0.7.0 read-only assessment release candidate.

The release publishes the opt-in Nesira Phase 2 read-only assessment surface in
the public wheel. It does not authorize combined verdict integration, runner
behavior, or severance action.

## Candidate

```text
version: 0.7.0
publication_authorization_commit: 72937cc97c8ae79492928fbec6798eed6088f456
release_candidate_review_commit: 5eec489d8d03877441de3c443b1f8ab1eff3195a
candidate_code_commit: e2f4af0a2e84abd04f789c4cc6ac1955f6f52c6b
tag_target: 72937cc97c8ae79492928fbec6798eed6088f456
wheel: spira_trust-0.7.0-py3-none-any.whl
wheel_sha256: 0ca716776b54bd8850b1fed0e8ce5d502d17c9ee567c22a5643b2de3aa60b8d7
```

## Prior Blocked Attempt

The first GO #2 production tag push targeted:

```text
tag: v0.7.0
target: e75b0960ece18c41ebdf73008671043f7b0108c1
workflow_run: 29694289448
result: blocked before PyPI upload and before GitHub release publication
failed_step: Guard release agent summary size
failure: agent_summary.json was 3141 bytes; limit was 3072 bytes
```

That failure did not publish to real PyPI and did not publish a GitHub release.
The final publication retargeted `v0.7.0` only after a refreshed RC and
publication authorization re-pin.

## GO #2

GO #2 was received from Snir for:

```text
action: retag v0.7.0 to 72937cc and push to origin for production publication
tag: v0.7.0
target: 72937cc97c8ae79492928fbec6798eed6088f456
```

## Production Workflow

```text
workflow: pypi-production-publish.yml
run_id: 29737614662
run_url: https://github.com/snir-spira37/spira-trust/actions/runs/29737614662
head_sha: 72937cc97c8ae79492928fbec6798eed6088f456
conclusion: success
```

## Published Surfaces

PyPI:

```text
status: PERFORMED
url: https://pypi.org/project/spira-trust/0.7.0/
filename: spira_trust-0.7.0-py3-none-any.whl
sha256: 0ca716776b54bd8850b1fed0e8ce5d502d17c9ee567c22a5643b2de3aa60b8d7
upload_time: 2026-07-20T11:11:07.883902Z
```

GitHub Release:

```text
status: PERFORMED
url: https://github.com/snir-spira37/spira-trust/releases/tag/v0.7.0
published_at: 2026-07-20T11:11:10Z
release_notes_sha256: f944df3b38bdfa43bbd9b91f120f12244e51e884f87704a61ce21cab16cb1db9
```

Attached release evidence assets:

```text
agent_summary.json
previous-version-gate.zip
previous_version_gate.json
release_self_evidence_manifest.json
SHA256SUMS.txt
spira-release-evidence.zip
```

## Final Pre-Publication Checks

```text
HEAD/publication source: 72937cc97c8ae79492928fbec6798eed6088f456
candidate version: 0.7.0
candidate wheel filename: spira_trust-0.7.0-py3-none-any.whl
candidate wheel SHA256: 0ca716776b54bd8850b1fed0e8ce5d502d17c9ee567c22a5643b2de3aa60b8d7
full pytest: 350 passed
V1 SHA256SUMS: 622/622
V1 Phase2/Nesira scope hits: 0
dependencies: []
cryptography posture: optional extra nesira-assessment only
unconditional cryptography Requires-Dist: absent
production notes: approved Nesira public snippet plus release-evidence ritual
rollback plan hash: 9c8a7424a476aba8237fc3d25ccc079bec7b07862c9e35cf37208dacdf61a7f2
combined verdict integration change: absent
runner/severance action change: absent
pre-existing PyPI 0.7.0 release: absent before upload
pre-existing GitHub release v0.7.0: absent before publication
```

## Boundary

The public claim remains:

```text
SPIRA includes an opt-in Nesira Phase 2 read-only assessment surface in the
public wheel. The surface checks declared trust evidence against declared trust
roots and composes the result through a verified fail-closed composition core,
conditional on the declared trust roots and recorded NOT_PROVEN assumptions.
It emits an assessment artifact only.
```

The release remains:

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
