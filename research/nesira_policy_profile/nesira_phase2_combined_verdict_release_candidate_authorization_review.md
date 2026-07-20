# Nesira Phase 2 Combined Verdict Release Candidate Authorization Review

## Verdict

```text
NESIRA_PHASE2_COMBINED_VERDICT_RELEASE_CANDIDATE_AUTHORIZATION_ACCEPTED
```

## Review Scope

This review evaluates whether
`nesira_phase2_combined_verdict_release_candidate_authorization.md` opens only
release-candidate preparation for the accepted combined verdict integration.

It does not authorize publication, PyPI upload, GitHub release, git tag,
runner behavior, severance action, or public claim expansion.

## Candidate Boundary

The authorization limits the candidate to:

```text
0.7.1 version bump
accepted combined verdict integration
explicit opt-in Nesira layer
conservative / fail-closed behavior
```

It keeps runner, severance action, automatic remediation, and new action
vocabulary blocked.

Review finding: PASS.

## V1 Manifest Catch

The authorization explicitly anticipates that `pyproject.toml` and
`tools/build_spira_trust_public.py` are V1-pinned and permits only a narrow V1
manifest refresh for those files plus the changed artifact manifest itself.

It forbids expanding V1 claims, inventory, expected results, or the historical
protected-surface snapshot.

Review finding: PASS.

## Public Claim Ceiling

The release candidate notes may describe only conservative combined verdict
integration:

```text
explicit opt-in
can block or report-not-evaluated
sufficient cannot upgrade another layer
does not authorize action
```

The release candidate notes must not imply execution, severance authorization,
isolation truth, absolute root legitimacy, certification, audit, endorsement,
or guarantee.

Review finding: PASS.

## Required Verification

The authorization requires:

```text
wheel SHA recorded
full pytest
V1 SHA256SUMS 622/622
V1 scope scan
dependency posture
agent_summary <= 3KB
cold reproduction
```

Review finding: PASS.

## Final Status

```text
NESIRA_PHASE2_COMBINED_VERDICT_RELEASE_CANDIDATE_AUTHORIZATION_ACCEPTED

NEXT_ALLOWED_STEP:
RELEASE_CANDIDATE_PREPARATION_FOR_0_7_1

PUBLICATION: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
```
