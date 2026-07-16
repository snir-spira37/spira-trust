# SPIRA Formal Core V1 Lean Definition Report

## Status

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITION_IMPLEMENTATION_COMPLETE

LAKE_PROJECT_CREATED

LEAN_TOOLCHAIN_PINNED

LEAN_DEFINITIONS_IMPLEMENTED

LAKE_BUILD_PASS

NO_SORRY_ADMIT_AXIOM_IN_LEAN_FILES

NO_THEOREM_PROOFS_IMPLEMENTED

NO_PYTHON_CHANGES

NO_DOMAIN_ADAPTER_CHANGES

SEVEN_CORE_PROOFS_REQUIRE_SEPARATE_AUTHORIZATION
```

## 1. Scope

This report covers the Lean definition phase authorized by:

```text
research/formal_core/spira_formal_core_v1_lean_definition_implementation_authorization.md
```

It implements definitions only.

It does not implement:

```text
theorem proofs
proof scripts
Domain 1/2/3 conformance
Python integration
runtime integration
benchmark changes
production claims
release work
```

## 2. Worktree and Branch

```text
source baseline commit:
cfa8c925217fea08cbf4736490765d676bfddf3f

formal branch:
codex/formal-core-v1-lean

formal worktree:
<REPO_ROOT>
```

The paused benchmark artifacts in the original worktree were not modified.

## 3. Toolchain

```text
lean-toolchain:
leanprover/lean4:v4.32.0

Lean:
Lean (version 4.32.0, x86_64-w64-windows-gnu, commit 8c9756b28d64dab099da31a4c09229a9e6a2ef35, Release)

Lake:
Lake version 5.0.0-src+8c9756b (Lean version 4.32.0)

Elan:
NOT_AVAILABLE_LOCAL_RELEASE_ZIP_USED

release zip sha256:
57828abb276461c4cf62a75b1e71aa798c0bb329ab3d353c743d06b19c0ad0ac

operating system:
Microsoft Windows 10 Enterprise 10.0.19045

architecture:
64-bit
```

The project uses:

```text
Lean core
Lean Std bundled with Lean
```

It does not use:

```text
Mathlib
Batteries
external formal libraries
```

The Lake manifest records no external packages.

## 4. Created Project Structure

```text
formal/spira_formal_core_v1/
  lean-toolchain
  lakefile.toml
  lake-manifest.json
  README.md
  SpiraFormalCore.lean
  SpiraFormalCore/
    Basic.lean
    Action.lean
    ExplicitList.lean
    Evidence.lean
    Policy.lean
    Contract.lean
    Errors.lean
    Core.lean
    GateA.lean
    Passthrough.lean
```

## 5. Definition Coverage

The implementation defines:

```text
DomainId
SubjectId
PolicyId
SchemaVersion
ProducerId
ContractId
EvidenceRef
ProofRef
ReasonCode
BlockingItem
NotEvaluatedItem
NotClaimedItem
Action
EvidenceValidity
TypedClaim
TypedEvidence
PolicyContext
MachineContract
CoreError
CoreResult
```

The accepted action algebra is represented:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

The core functions are represented:

```text
validateTypedEvidence
aggregateClaims
deriveReasonCodes
deriveBlockingItems
deriveNotEvaluated
deriveNotClaimed
decideAction
assembleContract
core
gateAWrap
projectDomainContract
passthrough
executedAction
```

## 6. Build Result

Command:

```text
lake build
```

Result:

```text
PASS
```

Observed build output included:

```text
Build completed successfully (13 jobs).
```

## 7. Proof Hygiene

Lean-source scan:

```text
rg -n "\b(sorry|admit|axiom|sorryAx|theorem|opaque|unsafe)\b" formal/spira_formal_core_v1 -g "*.lean"
```

Result:

```text
NO_FORBIDDEN_LEAN_TOKENS
```

This phase intentionally contains no theorem declarations and no proofs.

## 8. Non-Changes

This phase did not modify:

```text
Python source
Domain adapters
Gate A Python implementation
passthrough Python implementation
benchmark runners
historical benchmark results
corpora
oracles
```

## 9. Remaining Boundaries

Still not authorized:

```text
seven theorem proofs
proof scripts
Python/Lean equivalence
Domain 2 conformance execution
Domain 3 conformance
Domain 1 conformance
runtime integration
production claims
release
```

## 10. Result

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_READY_FOR_REVIEW

SEVEN_CORE_PROOFS_REQUIRE_SEPARATE_AUTHORIZATION
```
