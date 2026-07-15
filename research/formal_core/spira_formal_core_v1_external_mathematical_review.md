# SPIRA Formal Core V1 External Mathematical Review

## Status

```text
SPIRA_FORMAL_CORE_V1_EXTERNAL_MATHEMATICAL_REVIEW_RECORDED

PACKAGE_INTEGRITY_REVIEW_PASSED
MATHEMATICAL_SUBSTANCE_REVIEW_COMPLETED

FORMAL_CORE_V1_CLAIM_BOUNDARY_REFINED

NO_LEAN_IMPLEMENTATION_CHANGE
NO_PYTHON_CODE_CHANGE
NO_ADAPTER_CHANGE
NO_EXISTING_RESULT_RECLASSIFICATION
NO_PRODUCTION_CLAIM
NO_RELEASE
```

## Decision

The external mathematical review is accepted as a substantive critique of Formal Core V1.

Formal Core V1 remains valid as a machine-checked executable specification over typed evidence, with useful branch-level and helper-level invariants. It should not be described, without qualification, as a fully end-to-end formally verified decision core.

The accepted wording is:

```text
SPIRA has a machine-checked deterministic decision core over typed evidence,
with proven fail-closed and uncertainty-preservation invariants at the
branch/helper level; end-to-end core theorems and adapter binding are
validated empirically, not proven.
```

The stronger wording below is not authorized for Formal Core V1:

```text
SPIRA has a formally verified deterministic decision core over typed evidence.
```

## What The Review Confirmed

The review confirmed that the reproduction package contains the expected Lean corpus and proof inventory:

```text
Lean files: 34
Theorem-like declarations: 42
Definition-like declarations: 138
Forbidden proof escape hatches: 0
```

The review also accepted that the project boundary is honestly documented:

```text
Mathematically proven:
- typed-evidence core branch/helper properties
- action priority behavior for blocking and NOT_EVALUATED branches
- fail-closed behavior for the declared error taxonomy
- stop/action consistency for the formal branch functions
- non-authority of model/presentation fields where encoded directly

Tested or trusted, but not proven:
- Python adapters
- raw ZIP, pytest/JUnit, and Terraform parsing
- JSON canonicalization and serialization
- Python runtime, OS, filesystem, and toolchain behavior
- empirical harness bindings between production artifacts and Lean models

Out of scope:
- production security claims
- parser correctness proofs
- live-agent behavior
- release readiness
```

## Main Mathematical Strength

The strongest part of Formal Core V1 is the action algebra and its priority order:

```text
BLOCKED / fail-closed
>
NOT_EVALUATED / unknown
>
PROCEED
```

This is the product thesis in formal shape: unknown evidence does not silently collapse into PASS, and blocking evidence prevents PROCEED at the decision-branch level.

The most important V1 theorem family is:

```text
required NOT_EVALUATED prevents silent PROCEED
```

This captures the core SPIRA distinction:

```text
NOT_EVALUATED != PASS
not_claimed != false
```

## Main Weaknesses

### 1. Policy Fields Are Mostly Inert

`PolicyContext` contains fields such as:

```text
requiredClaims
blockingRules
requiredEvidenceRefs
requiredProofRefs
```

In Formal Core V1, these fields do not materially drive `core` decisions. They are mostly carried for identity or future policy shape, while the active blocking and not-evaluated inputs are supplied by typed claims produced by the adapter boundary.

This means V1 proves properties of the typed-claim algebra more than it proves policy-driven decision semantics.

### 2. Most Central Theorems Are Helper-Level

Several central theorem families are proved over helper functions such as:

```text
decideAction
assembleContract
failClosedAction
```

They do not always prove end-to-end statements directly over:

```text
core evidence policy
```

For example, a broken future `core` implementation that ignored `decideAction` could satisfy helper-level theorems while failing the intended end-to-end behavior. Current Python harnesses and test vectors would detect such a break, but V1 Lean theorems do not fully rule it out.

### 3. Some Theorems Are Vacuous Or Structural

The theorem family named as determinism is currently a structural extensionality statement:

```text
e1 = e2 -> p1 = p2 -> core e1 p1 = core e2 p2
```

This is true, but it is closer to congruence of pure Lean functions than a substantive domain invariant. It should not be used as a headline mathematical claim.

The Gate A and presentation non-authority proofs are also largely structural: they encode the intended architecture cleanly, but their mathematical strength comes from the construction being simple, not from a deep proof.

### 4. Domain Action Paths Need Lean Equivalence Theorems

Domain 2 has both:

```text
evaluate evidence
formalAction evidence
```

The current equivalence between these paths is mainly exercised empirically by Python harnesses. Formal Core V2 should prove in Lean that the domain action path and the core path agree.

The same class of theorem should be added for every domain-specific decision wrapper.

### 5. Derived Lists Need Soundness And Completeness

Formal Core V1 proves that `assembleContract` preserves lists that it is handed. It does not fully prove that the `derive*` functions compute exactly the intended lists from typed evidence.

Formal Core V2 should add both directions:

```text
soundness:
every emitted blocking/not_evaluated/not_claimed item is supported by typed evidence or policy

completeness:
every required typed evidence or policy item appears in the emitted contract list
```

## Revised V1 Claim Boundary

Formal Core V1 supports this bounded claim:

```text
Given typed evidence in the V1 algebra, SPIRA has a machine-checked
decision specification with explicit fail-closed and uncertainty-preserving
branch behavior, plus empirical differential evidence connecting the Python
implementation and domain adapters to the Lean model.
```

Formal Core V1 does not yet support this broader claim:

```text
All SPIRA domain adapters and the full Core(E,P)=C path are formally proven
end-to-end.
```

## Required V2 Direction

Formal Core V2 should focus on strengthening the mathematics, not on adding more agent benchmarks.

The next proof target is:

```text
end-to-end core theorems over core(evidence, policy)
```

not additional package validation or live-agent testing.

## Accepted Outcome

```text
FORMAL_CORE_V1_MACHINE_CHECKED_EXECUTABLE_SPEC_ACCEPTED

FORMAL_CORE_V1_BRANCH_LEVEL_INVARIANTS_ACCEPTED

FORMAL_CORE_V1_END_TO_END_FORMAL_VERIFICATION_NOT_ESTABLISHED

FORMAL_CORE_V2_END_TO_END_THEOREMS_REQUIRED

CLAIM_BOUNDARY_REFINED

NO_EXISTING_RESULT_RECLASSIFICATION
NO_PRODUCTION_CLAIM
NO_RELEASE
```

