# Nesira Phase 2 External Reproduction Package Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2
SCOPE: INTERNAL_ASSESSMENT_ENGINE_EXTERNAL_REPRODUCTION_PACKAGE

AUTHORIZES:
EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ONLY

PACKAGE_DELIVERY: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This document authorizes building a local external reproduction package for the
accepted Nesira Phase 2 internal assessment engine. It authorizes package
construction, package self-verification, and package-build review only.

It does not authorize sending the package to an external reviewer, publishing
the package, integrating the engine into a product verdict, exposing a CLI,
adding the engine to the public wheel, making a public capability claim, running
isolation, granting permission to sever, or releasing.

## Authoritative Starting Point

```text
authoritative_internal_assessment_milestone_commit:
a62221b0f8d8f52d9b0bc986bd875122071d134e

authoritative_milestone_record:
research/nesira_policy_profile/nesira_phase2_internal_assessment_milestone.md

accepted_status:
NESIRA_PHASE2_INTERNAL_ASSESSMENT_ENGINE_COMPLETE_INTERNAL_ONLY

current_authorized_step:
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_AUTHORIZED
```

The future package may be built from the authoritative milestone commit above,
or from a later package-build commit that preserves the accepted Phase 2 source,
proof, adapter, wiring, and boundary artifacts and changes only package-build
materials.

Any package document that uses a later package-build commit must explicitly
record both:

```text
source_assessment_commit
package_artifact_commit
```

The relationship between the two commits must be explained in the package notes
to avoid stale or contradictory commit authority.

## Accepted Inputs

The package may rely on the following accepted records:

```text
SPIRA_NESIRA_PHASE1_VALIDATOR_ACCEPTED
SPIRA_NESIRA_PHASE1_COLD_EXTERNAL_REPRODUCTION_ACCEPTED
FORMAL_CORE_V1_ACCEPTED
DOMAIN4_NESIRA_LEAN_CORE_ACCEPTED
NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_COLD_VERIFICATION_ACCEPTED
NESIRA_PHASE2_ASSESSMENT_WIRING_COLD_VERIFICATION_ACCEPTED
```

The package must include or point to the accepted Phase 2 research records:

```text
nesira_phase2_proposal.md
nesira_phase2_trust_model.md
nesira_phase2_not_proven_trust_ledger.md
nesira_phase2_not_proven_trust_ledger.json
nesira_phase2_assessment_sketch.md
nesira_phase2_assessment_decision_table_spec.md
nesira_phase2_assessment_decision_table.json
nesira_phase2_lean_composition_report.md
nesira_phase2_signature_adapter_report.md
nesira_phase2_identity_adapter_report.md
nesira_phase2_authority_adapter_report.md
nesira_phase2_isolation_attestation_adapter_report.md
nesira_phase2_assessment_wiring_report.md
nesira_phase2_internal_assessment_milestone.md
```

The package must not rewrite the accepted claims, assumptions, or boundaries.
If a package-build script discovers that an accepted record is stale or
inconsistent, it must stop with a revision verdict rather than patching the
record silently.

## Authorized Package Shape

The package build may create a local directory and ZIP containing reproduction
instructions and machine-verifiable metadata. The recommended package directory
is:

```text
research/nesira_policy_profile/phase2_external_reproduction_package/
```

The authorized package contents are:

```text
README_REPRODUCTION.md
CLAIMS_AND_BOUNDARIES.md
REPRODUCE_PHASE2.md
COLD_EXTERNAL_REVIEW_TASK.md
phase2_reproduction_manifest.json
phase2_expected_results.json
protected_surface_hash_inventory.json
toolchain_environment_lock.json
SHA256SUMS
```

The build may also create local package-build reports:

```text
research/nesira_policy_profile/phase2_external_reproduction_package_build_report.md
research/nesira_policy_profile/phase2_external_reproduction_package_build_results.json
research/nesira_policy_profile/phase2_external_reproduction_package_build_review.md
research/nesira_policy_profile/phase2_external_reproduction_package_build_review_results.json
```

The build may create a ZIP and upload note for later review, but this
authorization does not authorize delivery of that ZIP.

## Required Claim Boundary

Every package document must preserve this positive claim:

```text
SPIRA/Nesira can internally assess declared trust evidence across signature,
identity, authority, and attestation roots, compose the result through a
verified fail-closed core, and emit an assumption-carrying assessment artifact.
```

Every package document must also preserve these non-claims:

```text
trust roots are declared assumptions, not absolute truth
attestation checked is not isolation proven
assessment artifact is not severance authorization
assessment artifact is not operational execution
no permission to sever is granted
no runner is implemented or authorized
no combined product verdict is implemented or authorized
no CLI is implemented or authorized
no public wheel exposure is authorized
no public capability claim is authorized
no release is authorized
```

The required execution marker remains:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

No package text, JSON field, reason code, expected result, or review task may
state or imply an isolation-truth claim.

## Required Toolchain Locks

The package must record the exact toolchain required for reproduction:

```text
Python: 3.12.x
Lean: 4.32.0
Lake: 5.0.0
cryptography: 49.0.0
```

The crypto dependency must remain outside `pyproject.toml` product
dependencies. Reproduction must install it only from the hash-locked adapter
requirements file:

```text
requirements/nesira_adapters_win_amd64_cp312.txt
```

The package must require `--require-hashes` installation for the adapter
requirements. If the pinned version or wheel hash cannot be reproduced, the
package must fail closed.

## Required Reproduction Gates

A cold reviewer must be instructed to reproduce at least:

```text
git clone and checkout of the exact source commit
adapter requirements install with --require-hashes
compileall over relevant source, tools, and tests
Lean/Lake build of accepted targets
Lean Phase 2 81-row dump compared to the frozen oracle
Phase 2 signature adapter conformance
Phase 2 identity adapter conformance
Phase 2 authority adapter conformance
Phase 2 isolation attestation adapter conformance
Phase 2 assessment wiring conformance
full pytest with the accepted expected count
V1 external reproduction manifest self-check
public wheel build and exclusion inspection
git diff --check
whole-tree local path and secret scan
```

The expected current full pytest count at the accepted milestone is:

```text
339 passed
```

The V1 external reproduction package self-check must remain coherent:

```text
SHA256SUMS: 622/622 OK
V1 scope: no Phase 2 claims folded into the V1 external reproduction package
```

If a later package-build commit changes `lakefile.toml` or any file locked by
the V1 external reproduction manifest, the package build must refresh and
verify the affected hashes in the same commit, or stop.

## Required Adapter and Wiring Checks

The package must require verification of these accepted Phase 2 properties:

```text
signature adapter uses cryptography, not hand-rolled crypto
identity adapter uses declared roots only, not OS or browser trust stores
authority adapter is default-deny
isolation attestation adapter verifies attestation only, not isolation truth
PT-ISOLATION-01 is carried on every isolation sub-verdict
assessment wiring uses one caller-supplied expected context for all adapters
cross_subject_mismatch is not sufficient
81 oracle rows have zero disagreements
assumption union includes the floor and all applicable conditional assumptions
public wheel excludes adapters, harnesses, and cryptography metadata
pyproject product dependencies remain empty
```

The package must also require a language-boundary scan that rejects any
unapproved isolation, sandbox, or containment wording in code, outputs, reason
codes, and reports.

## Required Package Hygiene

The package build must verify:

```text
ZIP paths are relative only
no path traversal entries
no duplicate archive paths
deterministic archive timestamps
SHA256SUMS covers every packaged file
SHA256SUMS validates against the checked-out working tree bytes
all JSON files parse
no local absolute paths
no usernames from local builder paths
no API keys, tokens, private keys, or credentials
no stale commit references
no invented public CLI command
```

If the package contains local path leaks, secret-like values, contradictory
commit authority, or stale expected results, it must receive a revision verdict.

## Required Hard Stops

The package build must stop if any of the following occurs:

```text
full pytest does not match the accepted expected result
V1 manifest self-check fails
Lean dump differs from the frozen 81-row oracle
adapter conformance fails
assessment wiring conformance fails
cryptography is not pinned and hash-locked
cryptography appears in product dependencies
adapters or cryptography appear in public wheel metadata
any output implies execution, severance, or public product availability
any trust root is treated as absolute truth rather than a declared assumption
any package artifact claims isolation was proven
```

## Review Requirement

Before any ZIP is delivered, the package-build output must receive a separate
package-build review. That review must inspect the actual ZIP, not only the
documents describing it.

The package-build review must report one of:

```text
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ACCEPTED
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_NEEDS_REVISION
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_REJECTED
```

Only the user may separately authorize actual delivery to an external reviewer.
