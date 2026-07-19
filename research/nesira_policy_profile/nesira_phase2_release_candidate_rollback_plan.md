# Nesira Phase 2 Release Candidate Rollback Plan

## Status

```text
DOCUMENT_TYPE: ROLLBACK_PLAN_DRAFT
CANDIDATE_VERSION: 0.7.0

PUBLICATION: NOT_AUTHORIZED
ROLLBACK_ACTION: NOT_EXECUTED
```

This plan prepares rollback instructions for a possible later publication. It
does not perform any rollback action and does not assume that a release already
exists.

## Human Owner

```text
release_go_no_go_owner: Snir
rollback_go_no_go_owner: Snir
```

No automated process may publish, yank, delete, supersede, or announce a
release without explicit human authorization.

## If a PyPI Release Is Later Published

If a later authorized PyPI publication must be withdrawn:

```text
1. Stop any further publication or announcement work.
2. Use PyPI project administration to yank the affected file/version.
3. Record the yanked version, file name, SHA256, time, and reason.
4. Publish a correction notice that states the precise boundary issue.
5. Point users to the prior accepted version or to a corrected successor.
```

No PyPI yank is authorized by this release-candidate gate.

## If a GitHub Release Is Later Created

If a later authorized GitHub release must be removed or superseded:

```text
1. Stop any further release asset upload or announcement work.
2. Remove or mark the affected GitHub release as superseded.
3. Record the tag, commit, asset filename, SHA256, time, and reason.
4. Publish a correction notice that states the precise boundary issue.
5. Point users to the prior accepted version or to a corrected successor.
```

No GitHub release deletion, tag deletion, or release editing is authorized by
this release-candidate gate.

## If Claim Text Overstates Scope

If any later public claim is found to imply execution, severance authorization,
permission to proceed, isolation truth, absolute trust-root legitimacy,
certification, audit, endorsement, third-party validation, or a security or
trust guarantee:

```text
1. Stop distribution of the claim text.
2. Publish corrected claim text with the assessment-only boundary restored.
3. Identify the exact phrase that caused the overclaim.
4. Link the correction to the recorded NOT_PROVEN assumptions.
5. Re-run the release-claim review before any replacement publication.
```

## Prior Version Guidance

If the 0.7.0 candidate or a later 0.7.0 publication is rejected, users should
be directed to the last accepted public version until a corrected successor is
approved.

This plan does not assert that 0.7.0 has been published.
