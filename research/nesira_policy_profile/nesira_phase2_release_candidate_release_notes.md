# spira-trust 0.7.0 Release Candidate Notes

## Status

```text
DOCUMENT_TYPE: RELEASE_NOTES_DRAFT
CANDIDATE_VERSION: 0.7.0

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
```

## Summary

This release candidate includes an opt-in Nesira Phase 2 read-only assessment
surface in the public wheel.

Existing `spira-trust` functionality is unchanged. This candidate adds only
the opt-in assessment surface described here.

The surface checks declared trust evidence against declared trust roots and
composes the result through a verified fail-closed composition core,
conditional on the declared trust roots and recorded NOT_PROVEN assumptions.
It emits an assessment artifact only.

## Included Surface

```text
spira_core/nesira_phase2_assessment_wiring.py
spira_core/nesira_phase2_authority_adapter.py
spira_core/nesira_phase2_identity_adapter.py
spira_core/nesira_phase2_isolation_attestation_adapter.py
spira_core/nesira_phase2_read_only_assessment_cli.py
spira_core/nesira_phase2_signature_adapter.py
```

The Nesira assessment surface is opt-in. The base package dependencies remain
empty. The crypto dependency is available only through the
`nesira-assessment` optional extra:

```text
cryptography==49.0.0
```

## Boundary

This is assessment-only.

It is not execution, not severance authorization, not permission to proceed,
not proof that isolation happened, not proof that trust roots are absolutely
legitimate, not combined verdict integration, and not runner behavior.

External reproduction means the recorded checks were reproduced from a fresh
clone. It does not mean independent certification, audit, endorsement,
third-party validation, or a security or trust guarantee.

## Candidate Artifact

```text
wheel: spira_trust-0.7.0-py3-none-any.whl
sha256: 29a52445a5045c76264fcce60df5288836cbe870193411c9b84d16ad9e454c6b
```

This release candidate is local evidence only until a separate publication
authorization is granted.
