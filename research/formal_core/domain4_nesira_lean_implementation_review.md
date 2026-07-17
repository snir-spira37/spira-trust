# SPIRA Domain 4 / Nesira Lean Implementation Review

## Verdict

```text
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_ACCEPTED
```

This review accepts the Lean-only Domain 4 / Nesira implementation as a faithful
translation of the accepted V2 paper design chain.

It does not authorize Python changes, fixture materialization, conformance
harness implementation, Phase 2 implementation, public claims, or release.

Reviewed artifacts:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Meta.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Proofs.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain4/Main.lean
formal/spira_formal_core_v1/SpiraFormalCore.lean
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/All.lean
research/formal_core/domain4_nesira_lean_implementation_results.json
research/formal_core/domain4_nesira_lean_implementation_report.md
```

## Review Findings

### 1. Scope Was Preserved

The change is Lean-only plus authorized research outputs. No Python, fixture,
harness, Phase 2, product, release, or public capability file was changed.

### 2. The Enum Translation Is Faithful

The Lean implementation defines the accepted V2 enum space:

```text
ExecutionMeta: 3 values
Outcome types: 9
Outcome values: 27
Artifact kinds: 2
```

Enum names follow the frozen schema names.

### 3. PROCEED Is Type-Level Impossible

`Phase1Action` contains only:

```text
REPORT_NOT_EVALUATED
STOP_BLOCKED
RERUN_REQUIRED
```

There is no `PROCEED` constructor in Domain 4 Phase 1.

### 4. The Decision Table Is Faithful

`NesiraCoreV2` implements:

```text
ExecutionMeta first
artifact_kind branching
severance first-match table
isolation first-match table
status -> action projection
stop = true
```

The Lean dump covers the full finite core space:

```text
118098 tuples
```

An independent local checker compared every dumped Lean row against the frozen
decision-table V2 ordering:

```text
disagreements: 0
```

### 5. Theorem Families Passed

The required theorem families were proved. For evidence checks that occur after
earlier first-match rows, theorems include the necessary precedence
preconditions. This is faithful to the table and avoids false overbroad claims.

### 6. Build And Proof Hygiene Passed

```text
lake build: PASS
sorry/admit/custom axiom/sorryAx/native_decide/unsafe/opaque: 0
unapproved axioms: 0
```

`#print axioms` shows only `propext` for the `simp`-based row theorems and no
axioms for `core_deterministic`.

### 7. Existing Domains Did Not Regress

The complete Formal Core package builds with Domain4 imported, preserving
existing Domain 1, Domain 2, Domain 3, and generic proof modules.

## Not Accepted In This Review

This review does not accept or authorize:

```text
Python raw -> enum classifier
PythonCore
Python/Lean exhaustive conformance harness
fixtures or mutation pairs
reason-code fidelity harness
Phase 2 signer trust
signer authority
actual isolation execution
permission to sever
combined verdict integration
CLI / wheel exposure
public capability claim
release
```

## Required Next Step

The next stage requires a separate authorization:

```text
DOMAIN4_NESIRA_PYTHON_HARNESS_AUTHORIZATION_REQUIRED
```

That stage should implement the Python/harness side and independently verify:

```text
PythonCore == LeanCore over all 118098 tuples
safety-critical mutation pairs
reason-code fidelity
two-run equality
external cold reproduction
```

## Status

```text
DOMAIN4_NESIRA_LEAN_IMPLEMENTATION_ACCEPTED

LEAN_ONLY_IMPLEMENTATION_ACCEPTED
FAITHFUL_TRANSLATION_ACCEPTED
PHASE1ACTION_NO_PROCEED_ACCEPTED
DOMAIN4_THEOREM_FAMILIES_ACCEPTED
LEAN_DUMP_SPEC_FIDELITY_ACCEPTED
LAKE_BUILD_PASS
SORRY_ADMIT_AXIOM_SCAN_PASS
PRINT_AXIOMS_ACCEPTED
DOMAIN1_DOMAIN2_DOMAIN3_REGRESSION_PASS

PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED

DOMAIN4_NESIRA_PYTHON_HARNESS_AUTHORIZATION_REQUIRED_NEXT
```
