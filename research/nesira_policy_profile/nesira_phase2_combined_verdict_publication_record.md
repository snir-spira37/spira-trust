# Nesira Phase 2 Combined Verdict Publication Record

## Verdict

```text
NESIRA_PHASE2_COMBINED_VERDICT_PUBLICATION_COMPLETED
```

## Scope

This record documents the authorized publication of `spira-trust` 0.7.1 after
explicit GO #2 from Snir.

This publication carries the accepted Nesira Phase 2 combined verdict
integration as an explicit opt-in conservative policy layer.

## Human Authorization

```text
go_no_go_owner: Snir
go_2_text: GO #2: publish v0.7.1
operator: Codex under explicit Snir GO #2
publication_time_utc: 2026-07-20T14:46:59Z
```

## Tag

```text
tag: v0.7.1
tag_target: a1ddde7f157e9ede03130cfbc99d9ae0442145f5
remote_tag: a1ddde7f157e9ede03130cfbc99d9ae0442145f5 refs/tags/v0.7.1
```

## Production Workflow

```text
workflow: pypi-production-publish.yml
run_id: 29751805181
run_number: 12
event: push
branch: v0.7.1
head_sha: a1ddde7f157e9ede03130cfbc99d9ae0442145f5
conclusion: success
url: https://github.com/snir-spira37/spira-trust/actions/runs/29751805181
```

## PyPI Publication

```text
project_url: https://pypi.org/project/spira-trust/0.7.1/
version: 0.7.1
file: spira_trust-0.7.1-py3-none-any.whl
sha256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
size: 751670
file_url: https://files.pythonhosted.org/packages/e2/23/844d6fcff608ca6ee0c49affb990271209241c966ef1ede20ecb1532fcdd/spira_trust-0.7.1-py3-none-any.whl
```

The uploaded wheel SHA256 matches the accepted release-candidate SHA256 and the
TestPyPI staging SHA256.

## GitHub Release

```text
release_url: https://github.com/snir-spira37/spira-trust/releases/tag/v0.7.1
draft: false
prerelease: false
release_notes_sha256: cd765a27a2049bb946881ee70efa8f53fc4c6b543fc4579d96edd3945ddcd52b
asset_count: 6
```

Attached assets:

```text
agent_summary.json                         3017
previous-version-gate.zip                  11207020
previous_version_gate.json                 2692
release_self_evidence_manifest.json        1972
SHA256SUMS.txt                             481
spira-release-evidence.zip                 34012
```

## Final Pre-Publication Checks

Immediately before GO #2 publication:

```text
HEAD: a1ddde7f157e9ede03130cfbc99d9ae0442145f5
remote branch tip: a1ddde7f157e9ede03130cfbc99d9ae0442145f5
working tree: clean
remote tag v0.7.1: absent
real PyPI 0.7.1: absent / 404
GitHub release v0.7.1: absent / 404
rebuilt wheel SHA256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
full pytest: 361 passed
V1 SHA256SUMS: 622/622
V1 Phase2/Nesira scope hits: 0
dependencies: []
cryptography: optional extra only, cryptography==49.0.0
```

## Post-Public Verification

Public surface verification after workflow success:

```text
PyPI JSON: 0.7.1 present
PyPI wheel SHA256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
GitHub release v0.7.1: present
GitHub release notes: combined verdict snippet present and boundary text present
base pip install from PyPI: PASS
base installed version: spira-trust 0.7.1
base cryptography_present: false
extra pip install from PyPI: PASS
extra installed version: spira-trust 0.7.1
extra cryptography_version: 49.0.0
```

The first immediate `pip install spira-trust==0.7.1` attempt observed a short
PyPI simple-index propagation delay after PyPI JSON already showed the file.
Retry after propagation succeeded.

## Boundary

The published release remains within the accepted boundary:

```text
Nesira combined verdict integration is explicit opt-in.
Existing default behavior remains unchanged.
Nesira sufficient contributes only OK and cannot upgrade another layer.
Nesira insufficient contributes BLOCK.
Nesira not-evaluated remains not sufficient.
Malformed/action-looking/marker/caveat-missing artifacts fail closed.
```

Still not claimed:

```text
execution
severance authorization
permission to proceed
runner behavior
automatic remediation
proof that isolation happened
proof that trust roots are absolutely legitimate
independent certification
audit
endorsement
third-party validation
security guarantee
trust guarantee
```

## Rollback Reference

Rollback plan:

```text
research/nesira_policy_profile/nesira_phase2_combined_verdict_release_candidate_rollback_plan.md
```

No rollback action was executed.

