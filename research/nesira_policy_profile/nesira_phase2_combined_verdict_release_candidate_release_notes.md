# spira-trust 0.7.1 Release Candidate Notes

## Status

```text
DOCUMENT_TYPE: RELEASE_NOTES_DRAFT
CANDIDATE_VERSION: 0.7.1

PUBLICATION: NOT_AUTHORIZED
PYPI_UPLOAD: NOT_AUTHORIZED
GITHUB_RELEASE: NOT_AUTHORIZED
GIT_TAG: NOT_AUTHORIZED
```

## Summary

This release candidate includes the accepted Nesira Phase 2 combined verdict
integration as an explicit opt-in conservative policy layer.

Existing default `spira-trust` behavior is unchanged. Nesira is not required by
default. When a caller supplies or requires a Nesira Phase 2 assessment
artifact, the combined verdict can use that artifact only as a conservative
layer.

`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS` contributes only `OK` and cannot upgrade
another layer's `BLOCK`, `WARN`, `NOTE`, or `NOT_EVALUATED` result.
`TRUST_INSUFFICIENT` contributes `BLOCK`. `TRUST_NOT_EVALUATED` remains not
sufficient. Malformed, action-looking, marker-mismatched, or caveat-missing
Nesira artifacts fail closed.

## Boundary

This is assessment composition inside the combined verdict, not execution.

It is not severance authorization, not permission to proceed, not runner
behavior, not automatic remediation, not proof that isolation happened, and not
proof that trust roots are absolutely legitimate.

External reproduction means the recorded checks were reproduced from a fresh
clone. It does not mean independent certification, audit, endorsement,
third-party validation, or a security or trust guarantee.

## Candidate Artifact

```text
wheel: spira_trust-0.7.1-py3-none-any.whl
sha256: 297d9d8074dd1a6b95b70e74ef2f14ec1cf1b7af976a14c34411354492882664
```

This release candidate is local evidence only until a separate publication
authorization is granted.
