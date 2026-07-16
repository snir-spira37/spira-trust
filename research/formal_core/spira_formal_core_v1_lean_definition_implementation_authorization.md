# SPIRA Formal Core V1 Lean Definition Implementation Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITION_IMPLEMENTATION_AUTHORIZED

LEAN_DEFINITION_PHASE_ONLY

TOOLCHAIN_LOCK_AUTHORIZED

LAKE_PROJECT_SKELETON_AUTHORIZED

CONTRACT_ALGEBRA_DEFINITIONS_AUTHORIZED

TYPED_EVIDENCE_DEFINITIONS_AUTHORIZED

POLICY_CONTEXT_DEFINITIONS_AUTHORIZED

PURE_CORE_FUNCTION_DEFINITIONS_AUTHORIZED

SPECIFICATION_TO_DEFINITION_TRACEABILITY_REQUIRED

BUILD_AND_LINT_CHECKS_AUTHORIZED

DEFINITION_RESULTS_AUTHORIZED

DEFINITION_REPORT_AUTHORIZED

DEFINITION_REVIEW_REQUIRED

SEVEN_THEOREM_PROOFS_NOT_AUTHORIZED

THEOREM_PROOF_FILES_NOT_AUTHORIZED

PYTHON_INTEGRATION_NOT_AUTHORIZED

PYTHON_CODE_CHANGES_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes the first Lean implementation phase for SPIRA Formal
Core V1.

It permits a bounded implementation of Lean definitions corresponding to the
accepted Formal Core V1 specification.

It does not authorize proving the seven theorem families. It also does not
authorize Python integration, domain adapter conformance, runtime integration,
benchmark changes, production claims, or release work.

## 2. Baseline and Isolation

Formal work is isolated in a dedicated worktree and branch.

```text
source repository:
snir-spira37/spira-trust

source baseline commit:
cfa8c925217fea08cbf4736490765d676bfddf3f

formal branch:
codex/formal-core-v1-lean

formal worktree:
<REPO_ROOT>

baseline branch:
codex/domain3-terraform-plan-retry-1
```

The original benchmark worktree contains paused benchmark artifacts. They must
not be reset, cleaned, overwritten, or modified by this formal-core phase.

## 3. Frozen Specification Artifacts

The following accepted specification artifacts are frozen for this phase:

```text
research/formal_core/spira_formal_core_v1_contract_algebra_spec.md
sha256:
d7d60aad2f2f0127888ae4710acb93ab51909471e2aa619a70c25a7ec4062153

research/formal_core/spira_formal_core_v1_theorem_spec.md
sha256:
b760f746df6f909b1cee3a74e42978948dd437d284cbb234eb9b707c27824e71

research/formal_core/spira_formal_core_v1_trusted_computing_base_ledger.md
sha256:
91c7a5096c29180c22f993a2d9bfb50c53cdfcef3c3854bf14c50a29d87e0b63

research/formal_core/spira_formal_core_v1_domain2_conformance_plan.md
sha256:
f81f9a595bff4d8d67eb2a17b43a6ac146c901b538417a86c7512c21cbbe64ab

research/formal_core/spira_formal_core_v1_specification_review.md
sha256:
9d1b3d26484adca7677325f73da4b729a0012f731aefaa2fb5da8dcf1115c31b
```

If any definition cannot match these accepted specifications, the
implementation must stop. The specification must not be changed inside this
definition phase.

## 4. Authorized Files

This phase may create or modify only files under:

```text
formal/spira_formal_core_v1/
research/formal_core/
```

Expected Lean project files:

```text
formal/spira_formal_core_v1/lean-toolchain
formal/spira_formal_core_v1/lakefile.toml
formal/spira_formal_core_v1/README.md

formal/spira_formal_core_v1/SpiraFormalCore/Basic.lean
formal/spira_formal_core_v1/SpiraFormalCore/Action.lean
formal/spira_formal_core_v1/SpiraFormalCore/ExplicitList.lean
formal/spira_formal_core_v1/SpiraFormalCore/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Contract.lean
formal/spira_formal_core_v1/SpiraFormalCore/Errors.lean
formal/spira_formal_core_v1/SpiraFormalCore/Core.lean
formal/spira_formal_core_v1/SpiraFormalCore/GateA.lean
formal/spira_formal_core_v1/SpiraFormalCore/Passthrough.lean
```

Required research outputs:

```text
research/formal_core/spira_formal_core_v1_lean_definition_mapping.json
research/formal_core/spira_formal_core_v1_lean_definition_report.md
research/formal_core/spira_formal_core_v1_lean_definition_review.md
```

## 5. Toolchain Policy

This phase may select and pin one exact stable Lean 4 toolchain.

It must create:

```text
formal/spira_formal_core_v1/lean-toolchain
```

The toolchain must not be:

```text
nightly
floating
unpinned
```

The project may use:

```text
Lean core
Lean Std
```

The phase must not add:

```text
Mathlib
Batteries
other external formal libraries
```

unless a separate trusted-computing-base amendment authorizes them.

The definition report must record:

```text
Lean version
Elan version
Lake version
toolchain identifier
dependency graph
dependency hashes or locked revisions
operating system
architecture
```

At authorization time, `lean`, `lake`, and `elan` were not available in the
formal worktree shell. Toolchain installation or activation may be performed
only as needed to satisfy this definition phase and must be recorded in the
report.

## 6. Authorized Definitions

This phase may define:

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

The accepted action algebra must be represented:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

The definitions must preserve:

```text
stop(contract) = nonProceeding(contract.action)

NOT_EVALUATED != PASS

not_claimed != false

empty list != missing field

empty blocking_items != unknown blocking status
```

Explicit lists must remain:

```text
ordered
required
canonical
deduplicated by construction
structurally comparable
```

## 7. Authorized Pure Functions

This phase may implement pure definitions corresponding to:

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

The functions may be executable Lean definitions, but they must remain pure and
typed-evidence-only.

They must not parse:

```text
wheel files
ZIP files
pytest raw output
JUnit files
Terraform JSON
```

## 8. Proof Hygiene Boundaries

This phase must not introduce:

```text
theorem proof files
proof scripts
accepted theorem proofs
placeholder theorem declarations
custom axioms
unapproved axioms
opaque definitions used to hide obligations
unsafe decision-core code
```

Lean files must contain:

```text
no sorry
no admit
no axiom
no sorryAx
```

If the implementation needs any of these, it must stop with a non-pass review.

## 9. Definition Acceptance Gates

The implementation may be accepted only if:

```text
lake build: PASS

no sorry/admit/axiom: PASS

no placeholder theorem declarations: PASS

no Python changes: PASS

no domain-adapter changes: PASS

specification fields represented: 100%

action algebra represented: 100%

explicit-list distinctions represented: 100%

typed-evidence validity states represented: 100%

policy/context fields represented: 100%

specification-to-definition mapping: COMPLETE
```

The required accepted result is:

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_ACCEPTED

SEVEN_CORE_PROOFS_REQUIRE_SEPARATE_AUTHORIZATION
```

## 10. Required Review

The definition review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_ACCEPTED

SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_NEED_REVISION

SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_REJECTED
```

Only `SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_ACCEPTED` may open a later proof
authorization.

## 11. Explicit Non-Authorization

This document does not authorize:

```text
seven theorem proofs

proof scripts

Domain 1 conformance

Domain 2 conformance

Domain 3 conformance

Python source changes

runtime integration

benchmark runner changes

live agent sessions

result reclassification

merge to main

release/version/tag/PyPI
```
