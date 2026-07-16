# SPIRA Nesira Policy Profile - Phase 1 External Reproduction Authorization Review

Verdict:

```text
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_AUTHORIZATION_ACCEPTED
```

## Review Scope

This review evaluates only whether
`phase1_external_reproduction_authorization.md` correctly defines the
methodology, evidence boundary, acceptance gates, and prohibitions for a future
cold external reproduction of the accepted Nesira Phase 1 validator.

This review did not build the reproduction package and did not run a cold
external reproduction.

## Accepted Phase 1 Identity

```text
accepted_phase1_implementation_commit:
a6e69cf8ea17a1a7d8e188cf3da6735cbfa7a0aa

hygiene_clean_reproduction_source_commit:
c21abef47dd174284a5d1938182a633b93bd8785

accepted_phase1_verdict:
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED

baseline_commit:
df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe

authorization_v1_1_sha256:
14b19bbce4764778599b755ce614404ecc6875349c63a08efa9ad5439ef5370d
```

The authorization is pinned to the accepted Phase 1 commit and does not allow
using earlier historical or superseded packages as implementation authority.

## Claim Boundary

The authorization preserves the only permitted Phase 1 claim:

```text
SPIRA validates structure, binding, evidence integrity,
and safe evidence paths for the two supported Phase 1 artifact types.
```

It explicitly blocks claims for:

```text
cryptographic signature verification
signer identity
signer authority
signer trust
actual isolation execution
independent isolation observation
severance authorization
permission to sever
production readiness
product integration
public capability availability
```

Review finding: PASS.

## Artifact Scope

The authorized artifact types are limited to:

```text
SEVERANCE_AUTHORIZATION
LEGACY_ISOLATION_RESULT
```

The authorization does not expand Phase 1 to arbitrary policy documents,
runtime severance execution, signing infrastructure, or product integration.

Review finding: PASS.

## Required Reproduction Source

The authorization requires the future reproduction to start from the
hygiene-clean reproduction source commit:

```text
c21abef47dd174284a5d1938182a633b93bd8785
```

The original Phase 1 acceptance remains anchored in
`a6e69cf8ea17a1a7d8e188cf3da6735cbfa7a0aa`; `c21abef...` is a forward-only
artifact hygiene commit that redacts local builder paths from tracked reports
without changing validator code or semantics.

It allows only:

```text
fresh clone pinned to exact commit
clean worktree created from exact commit
```

It correctly forbids calling a clean worktree an external clone.

Review finding: PASS.

## Required Matrices

The authorization requires fixture-level and mutation-pair-level reporting,
including:

```text
6/6 positive structural acceptance
0/6 positive PROCEED
100% negative invariant detection
0 false VALID mutation pairs
0 unsafe paths accepted
0 hash mismatches accepted
0 directories accepted as evidence files
0 duplicate canonical evidence paths accepted
0 local absolute path leaks
0 PROCEED paths
0 stop=false paths
```

It also requires path-security, hash-binding, error-hygiene, capability-absence,
protected-surface, and public-wheel-exclusion checks.

Review finding: PASS.

## Public Wheel Boundary

The authorization requires future wheel construction and archive inspection
from the public builder, rather than relying on previous reports.

It requires verifying:

```text
validator module absent
research schemas absent
research fixtures absent
public allowlist unchanged
unexpected public-wheel modules = 0
```

Review finding: PASS.

## Capability Absence

The authorization requires checking imports, functions, call sites, and public
exports for absence of:

```text
cryptographic verification
Sigstore trust verification
signer authority evaluation
isolation runner
container/sandbox execution
combined-verdict integration
agent-summary integration
CLI registration
public exports
Phase 2 code
release code
```

It correctly states that keyword search alone is insufficient.

Review finding: PASS.

## Lean Boundary

The authorization separates:

```text
existing Formal Core identity check
Phase 1 validator empirical reproduction
absence of a formal proof of the new validator
```

It explicitly blocks claims that the Phase 1 validator, DSSE parser, path
validator, or end-to-end trust path are formally proved.

Review finding: PASS.

## Current-Step Prohibitions

The authorization preserves:

```text
PHASE2_NOT_AUTHORIZED
PRODUCT_INTEGRATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
REPRODUCTION_PACKAGE_BUILD_NOT_AUTHORIZED_IN_THIS_STEP
EXTERNAL_REPRODUCTION_EXECUTION_NOT_AUTHORIZED_IN_THIS_STEP
```

Review finding: PASS.

## Blockers

No blockers.

## Findings

No Critical, High, Medium, or Low findings.

## Next Step

After this accepted authorization, the next step is:

```text
SPIRA_NESIRA_PHASE1_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_REQUIRED
```

That next step still requires separate execution. This review does not build
the package, does not run external reproduction, and does not authorize Phase 2.
