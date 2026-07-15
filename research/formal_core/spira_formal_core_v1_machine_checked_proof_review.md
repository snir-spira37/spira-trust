# SPIRA Formal Core V1 Machine-Checked Proof Review

## Status

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

SEVEN_THEOREM_FAMILIES_MACHINE_CHECKED

LAKE_BUILD_PASS

NO_SORRY_ADMIT_CUSTOM_AXIOM_OR_SORRYAX

APPROVED_BUILTIN_AXIOM_PROPEXT_RECORDED

DEFINITION_DRIFT_0

THEOREM_STATEMENT_DRIFT_0

PYTHON_CHANGES_0

DOMAIN_ADAPTER_CHANGES_0

EXECUTABLE_REFERENCE_AUTHORIZATION_REQUIRED_NEXT

PYTHON_LEAN_EQUIVALENCE_NOT_AUTHORIZED

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Review Scope

This review covers the machine-checked proof phase for the seven accepted
Formal Core V1 theorem families.

Reviewed artifacts:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Proofs/
research/formal_core/spira_formal_core_v1_proof_inventory.json
research/formal_core/spira_formal_core_v1_machine_checked_proof_results.json
research/formal_core/spira_formal_core_v1_machine_checked_proof_report.md
```

## 2. Decision

The proof phase is accepted.

All seven theorem families authorized for Formal Core V1 were encoded and
checked by Lean:

```text
T1 Determinism
T2 Blocking evidence prevents PROCEED
T3 Required NOT_EVALUATED prevents silent PASS
T4 Explicit contractual lists are preserved
T5 Gate A preserves the complete domain contract
T6 Model and presentation fields have zero decision authority
T7 Invalid/internal/validation errors fail closed
```

## 3. Build Gate

```text
lake build:
PASS
```

The project built successfully with:

```text
Lean 4.32.0
Lake 5.0.0-src+8c9756b
```

## 4. Proof Hygiene Gate

The proof hygiene gates passed:

```text
sorry/admit: 0
custom axioms: 0
sorryAx: 0
opaque hiding obligation: 0
unsafe decision core: 0
```

The only reported axiom dependency is Lean's built-in:

```text
propext
```

This is accepted as a disclosed TCB assumption for this phase.

## 5. Drift Gate

No unauthorized changes were made to:

```text
Python code
Domain adapters
benchmark runners
historical results
corpora
oracles
```

No theorem obligation was weakened.

The only definition-file edit during the proof phase was importing:

```text
SpiraFormalCore.Proofs.All
```

from the top-level Lean module.

## 6. Claim Boundary

This review does not authorize a production or broad formal-verification claim.

The accepted claim is limited to:

```text
The SPIRA Formal Core V1 Lean definitions satisfy the seven checked theorem
families included in this proof phase, subject to the disclosed Lean trusted
computing base and the approved built-in propext axiom.
```

It does not prove:

```text
raw parser correctness
Python implementation equivalence
Domain 1/2/3 adapter conformance
runtime integration
LLM behavior
benchmark runner behavior
production readiness
```

## 7. Required Next Authorization

The next document should be:

```text
research/formal_core/spira_formal_core_v1_executable_reference_authorization.md
```

It may authorize:

```text
pure executable Lean reference evaluator
typed-evidence-only test vectors
reference build checks
reference report and review
```

It must not authorize:

```text
Python integration
Python/Lean equivalence harness
Domain conformance
runtime integration
production claim
release
```

## 8. Final Review Result

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

EXECUTABLE_REFERENCE_AUTHORIZATION_REQUIRED_NEXT
```
