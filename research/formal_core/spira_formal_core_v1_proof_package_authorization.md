# SPIRA Formal Core V1 Proof Package Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_AUTHORIZED

PROOF_PACKAGE_AND_LOCAL_REPRODUCTION_ONLY

ALL_DOMAINS_CONFORMANCE_ACCEPTED_REQUIRED

LEAN_BUILD_REPRODUCTION_AUTHORIZED

DOMAIN1_CONFORMANCE_REPRODUCTION_AUTHORIZED

DOMAIN2_CONFORMANCE_REPRODUCTION_AUTHORIZED

DOMAIN3_CONFORMANCE_REPRODUCTION_AUTHORIZED

FOCUSED_TEST_REPRODUCTION_AUTHORIZED

PROOF_PACKAGE_MANIFEST_AUTHORIZED

CLAIM_BOUNDARY_SUMMARY_AUTHORIZED

REPRODUCTION_GUIDE_AUTHORIZED

PROOF_PACKAGE_REVIEW_REQUIRED

RAW_ADAPTER_PROOFS_NOT_AUTHORIZED

PYTHON_RUNTIME_PROOF_NOT_AUTHORIZED

PRODUCTION_RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes a bounded Formal Core V1 proof package.

The package must make the accepted proof and conformance state reproducible for
a local reviewer without expanding the claim beyond the typed-evidence
boundary.

The package must connect:

```text
Lean Formal Core V1 modules

machine-checked proof inventory

Domain 1 conformance results

Domain 2 conformance rerun results

Domain 3 conformance results

all-domains conformance review

trusted computing base ledger

Python executable reference and differential harness reviews
```

## 2. Authorized Files

Python reproduction harness:

```text
tools/run_formal_core_v1_proof_package.py
```

Research outputs:

```text
research/formal_core/spira_formal_core_v1_proof_package_manifest.json
research/formal_core/spira_formal_core_v1_reproduction_guide.md
research/formal_core/spira_formal_core_v1_claim_boundary_summary.md
research/formal_core/spira_formal_core_v1_proof_package_results.json
research/formal_core/spira_formal_core_v1_proof_package_report.md
research/formal_core/spira_formal_core_v1_proof_package_review.md
```

No other files may be changed under this authorization.

## 3. Authorized Checks

The reproduction harness may run:

```text
lake build

tools/run_formal_core_v1_domain1_conformance.py

tools/run_formal_core_v1_domain2_conformance.py

tools/run_formal_core_v1_domain3_conformance.py

python -m pytest tests/test_formal_core_v1_python_boundary.py

python -m pytest tests/test_unification_proof.py

python -m pytest tests/test_mvp_unified.py
```

The harness may scan Lean files for:

```text
sorry
admit
axiom
sorryAx
```

The harness may verify that required proof/conformance artifacts exist and that
their accepted statuses are present.

## 4. Required Package Manifest

The manifest must list at least:

```text
repository commit

branch

Lean toolchain

Lean files included

Python harnesses included

research artifacts included

accepted domain reviews

trusted computing base ledger

claim boundary summary

sha256 for each package artifact
```

The manifest must be deterministic except for an explicit generation timestamp.

## 5. Required Reproduction Guide

The guide must show how to reproduce the accepted state locally:

```text
1. Ensure Lean 4 toolchain is on PATH.

2. Run lake build.

3. Run the three domain conformance harnesses.

4. Run the proof package harness.

5. Run focused Python tests.
```

The guide must also state the expected pass statuses.

## 6. Required Claim Boundary Summary

The claim boundary summary must separate:

```text
PROVEN / MACHINE-CHECKED

DIFFERENTIALLY CONFORMANT ON ACCEPTED CORPORA

TESTED ONLY

TRUSTED ASSUMPTION

OUT OF SCOPE

NOT AUTHORIZED
```

It must explicitly preserve:

```text
raw wheel / ZIP / RECORD parser proof: no

raw pytest / JUnit parser proof: no

raw Terraform JSON parser proof: no

production claim: no

release: no
```

## 7. Acceptance Gates

The proof package may be accepted only if:

```text
lake build: PASS

proof scan: PASS

Domain 1 conformance: ACCEPTED

Domain 2 conformance rerun: ACCEPTED

Domain 3 conformance: ACCEPTED

all-domains conformance review: ACCEPTED

focused tests: PASS

manifest hashes: PASS

claim boundary summary: COMPLETE

reproduction guide: COMPLETE
```

## 8. Explicitly Not Authorized

This authorization does not permit:

```text
Lean theorem weakening

Formal Core V1 action algebra change

Domain adapter changes

raw parser proofs

Gate A implementation changes

passthrough implementation changes

benchmark runner changes

Claude / Codex / DeepSeek sessions

result reclassification

production claim

merge to main

release

version bump

tag

PyPI publish
```

## 9. Review Outcomes

The review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED

SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_REJECTED
```

Even if accepted, this package does not authorize production integration,
release, or public marketing claims beyond the typed-evidence proof boundary.
