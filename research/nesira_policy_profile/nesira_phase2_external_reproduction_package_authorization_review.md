# Nesira Phase 2 External Reproduction Package Authorization Review

## Verdict

```text
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_AUTHORIZATION_ACCEPTED
```

## Review Scope

This review evaluates only whether
`nesira_phase2_external_reproduction_package_authorization.md` correctly
authorizes building a future external reproduction package for the accepted
Nesira Phase 2 internal assessment engine.

This review does not build the package, inspect a ZIP, run a cold reproduction,
authorize delivery to an external reviewer, authorize product integration, or
authorize release.

## Scope Boundary

The authorization opens only:

```text
EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ONLY
```

It explicitly keeps the following closed:

```text
PACKAGE_DELIVERY
RUNNER
COMBINED_VERDICT
CLI
PUBLIC_WHEEL_EXPOSURE
PUBLIC_CLAIM
RELEASE
```

Review finding: PASS.

## Authoritative Starting Point

The authorization pins the package build to the accepted internal assessment
milestone:

```text
a62221b0f8d8f52d9b0bc986bd875122071d134e
```

It also requires future package documents to record both source assessment
commit and package artifact commit when the package is built from a later
package-build commit.

This directly addresses prior commit-authority ambiguity.

Review finding: PASS.

## Accepted Inputs

The authorization lists the accepted Phase 2 chain:

```text
Phase 2 Lean composition cold verification
signature adapter cold verification
identity adapter cold verification
authority adapter cold verification
isolation attestation adapter cold verification
assessment wiring cold verification
internal assessment milestone
```

It also requires the package to carry the trust model, not-proven ledger,
assessment sketch, decision table, adapter reports, wiring report, and milestone
record.

Review finding: PASS.

## Claim Boundary

The authorization preserves the positive claim:

```text
internal assessment of declared trust evidence against declared roots,
composed through a verified fail-closed core, producing an
assumption-carrying assessment artifact
```

It blocks the major overclaims:

```text
trust roots as absolute truth
attestation as proof of isolation
assessment as severance authorization
assessment as execution
runner, combined verdict, CLI, public wheel exposure, public claim, release
```

The required execution marker is preserved:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

Review finding: PASS.

## Toolchain and Crypto Boundary

The authorization requires:

```text
Python 3.12.x
Lean 4.32.0
Lake 5.0.0
cryptography 49.0.0
```

It correctly keeps `cryptography` out of product dependencies and requires
hash-locked adapter installation through:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

Review finding: PASS.

## Required Reproduction Gates

The authorization requires the future package to reproduce:

```text
Lean/Lake build
81-row oracle agreement
four adapter conformance suites
assessment wiring conformance
full pytest with accepted expected count
V1 external reproduction manifest self-check
public wheel exclusion
git diff --check
whole-tree hygiene scan
```

It includes the accepted expected full test count:

```text
339 passed
```

It also requires the V1 external reproduction package to remain coherent:

```text
SHA256SUMS: 622/622 OK
V1 scope: no Phase 2 claims folded into V1
```

Review finding: PASS.

## Adapter and Wiring Coverage

The authorization requires checks for:

```text
no hand-rolled crypto
declared roots only
authority default-deny
attestation checked, not isolation proven
PT-ISOLATION-01 carried on every isolation sub-verdict
one caller-supplied expected context across all adapters
cross_subject_mismatch is not sufficient
81 oracle rows with zero disagreements
full assumption union
public wheel exclusion
empty product dependencies
```

These are the accepted safety-critical properties of the Phase 2 internal
assessment engine.

Review finding: PASS.

## Package Hygiene

The authorization requires path safety, deterministic archive construction,
SHA256SUMS coverage, JSON parsing, local-path and secret scans, stale-commit
checks, and absence of invented public CLI commands.

It correctly requires inspecting the actual ZIP before delivery.

Review finding: PASS.

## Hard Stops

The authorization defines hard stops for:

```text
test mismatch
V1 manifest self-check failure
Lean oracle disagreement
adapter or wiring conformance failure
unpinned crypto
crypto entering product dependencies
adapters or crypto entering public wheel metadata
execution or severance implication
trust roots treated as absolute truth
isolation-proof overclaim
```

Review finding: PASS.

## Final Status

```text
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_AUTHORIZATION_ACCEPTED
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_AUTHORIZED

PACKAGE_DELIVERY: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

The next authorized step is package construction and package-build review. The
external delivery decision remains separate and user-gated.
