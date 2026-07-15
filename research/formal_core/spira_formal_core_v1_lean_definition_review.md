# SPIRA Formal Core V1 Lean Definition Review

## Status

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_ACCEPTED

TOOLCHAIN_LOCK_ACCEPTED

LAKE_PROJECT_SKELETON_ACCEPTED

CONTRACT_ALGEBRA_DEFINITIONS_ACCEPTED

TYPED_EVIDENCE_DEFINITIONS_ACCEPTED

POLICY_CONTEXT_DEFINITIONS_ACCEPTED

PURE_CORE_FUNCTION_DEFINITIONS_ACCEPTED

SPECIFICATION_TO_DEFINITION_TRACEABILITY_ACCEPTED

LAKE_BUILD_PASS

NO_SORRY_ADMIT_AXIOM_IN_LEAN_FILES

NO_PLACEHOLDER_THEOREM_DECLARATIONS

NO_PYTHON_CHANGES

NO_DOMAIN_ADAPTER_CHANGES

SEVEN_CORE_PROOFS_REQUIRE_SEPARATE_AUTHORIZATION

DOMAIN_CONFORMANCE_NOT_AUTHORIZED

PYTHON_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Review Scope

This review covers the Lean definition implementation phase only.

Reviewed artifacts:

```text
formal/spira_formal_core_v1/
research/formal_core/spira_formal_core_v1_lean_definition_mapping.json
research/formal_core/spira_formal_core_v1_lean_definition_report.md
```

The review does not cover theorem proofs because theorem proofs were not
authorized and were not implemented.

## 2. Decision

The Lean definition phase is accepted.

The implementation provides a bounded Lean reference definition layer for:

```text
typed evidence
policy/version/context
machine contract
pure core function shape
Gate A wrapper/projection
passthrough model-non-authority shape
```

It is sufficient to proceed to a separate proof authorization.

## 3. Build and Hygiene Review

The required build gate passed:

```text
lake build: PASS
```

The forbidden-token scan over Lean source passed:

```text
sorry: 0
admit: 0
axiom: 0
sorryAx: 0
theorem declarations: 0
opaque: 0
unsafe: 0
```

No theorem proofs were smuggled into the definition phase.

## 4. Specification Mapping Review

The accepted specification fields are represented:

```text
action
stop
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
domain identity
subject identity
policy identity
schema/version identity
producer identity
contract identity
```

The accepted action algebra is represented:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

The accepted typed-evidence validity states are represented:

```text
valid
invalid
incomplete
conflicting
versionIncompatible
internalFailure
```

## 5. Limitations

This review does not claim:

```text
the seven theorem families are proved
Domain 1/2/3 conformance is established
Python behavior is equivalent to Lean
raw parsers are verified
runtime integration is accepted
production release is authorized
```

The current Lean definitions are accepted as the object that the next proof
phase may freeze and prove against.

## 6. Required Next Authorization

The next document should be:

```text
research/formal_core/spira_formal_core_v1_seven_theorem_proof_authorization.md
```

It must freeze:

```text
Lean toolchain
Lake project
all core definitions
accepted theorem statements
trusted-computing-base ledger
allowed built-in axioms
proof file list
```

It may authorize proof files for exactly the seven accepted theorem families.

It must not authorize:

```text
Python source changes
Domain adapter conformance
runtime integration
benchmark changes
production claim
release
```

## 7. Final Review Result

```text
SPIRA_FORMAL_CORE_V1_LEAN_DEFINITIONS_ACCEPTED

SEVEN_CORE_PROOFS_REQUIRE_SEPARATE_AUTHORIZATION
```
