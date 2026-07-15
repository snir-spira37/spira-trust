# SPIRA Formal Core V1 Reproduction Guide

## Scope

This guide reproduces the Formal Core V1 typed-evidence proof package.

It does not reproduce or claim raw parser proofs, production runtime proofs,
agent benchmarks, release readiness, or package-safety claims.

## Expected Environment

```text
Windows PowerShell
Python 3.12
Lean 4 toolchain from formal/spira_formal_core_v1/lean-toolchain
```

Lean must be available on `PATH`.

## Reproduction Steps

From the repository root:

```powershell
cd formal\spira_formal_core_v1
lake build
cd ..\..
python tools\run_formal_core_v1_domain1_conformance.py
python tools\run_formal_core_v1_domain2_conformance.py
python tools\run_formal_core_v1_domain3_conformance.py
python tools\run_formal_core_v1_proof_package.py
python -m pytest tests\test_formal_core_v1_python_boundary.py tests\test_unification_proof.py tests\test_mvp_unified.py
```

## Expected Statuses

```text
lake build: PASS

Domain 1: SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED

Domain 2: SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED

Domain 3: SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED

Proof package: SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED

Focused pytest: PASS
```

## Boundary

The reproduced claim is limited to:

```text
Formal Core V1 typed-evidence semantics and accepted domain conformance.
```

The reproduced claim excludes:

```text
raw wheel / ZIP / RECORD parser proof
raw pytest / JUnit parser proof
raw Terraform JSON parser proof
JSON canonicalizer proof
SHA-256 implementation proof
Python runtime proof
OS proof
LLM behavior
benchmark runners
production integration
release readiness
```
