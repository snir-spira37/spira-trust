# SPIRA Formal Core V1 Contract Algebra Specification

## Status

```text
SPIRA_FORMAL_CORE_V1_CONTRACT_ALGEBRA_SPECIFIED

SPECIFICATION_ONLY

NO_LEAN_DEFINITIONS

NO_PROOF_SCRIPTS

NO_PYTHON_CODE_CHANGES

NO_DOMAIN_ADAPTER_CHANGES

NO_PRODUCTION_CLAIM
```

## 1. Purpose

This document specifies the abstract contract algebra for SPIRA Formal Core V1.

The algebra is the future proof target for:

```text
Core(E, P) = C
```

where:

```text
E = typed evidence
P = policy, version, and bounded context
C = authoritative SPIRA machine contract
```

This is a specification only. It does not create Lean definitions or change the
Python implementation.

## 2. Core Sets

Formal Core V1 should model the following abstract sets:

```text
DomainId
SubjectId
PolicyId
SchemaVersion
ProducerId
EvidenceRef
ProofRef
ContractId
ReasonCode
BlockingItem
NotEvaluatedItem
NotClaimedItem
```

The future Lean model may represent these as opaque types first. Domain-specific
enumerations can be introduced later during conformance work.

## 3. Action Algebra

The minimum action algebra is:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

The action order is not a ranking. It is a decision category.

The core safety predicate is:

```text
nonProceeding(action)
```

where:

```text
nonProceeding(PROCEED) = false
nonProceeding(STOP_BLOCKED) = true
nonProceeding(RERUN_REQUIRED) = true
nonProceeding(REPORT_NOT_EVALUATED) = true
```

The `stop` state is derived from the action in Formal Core V1:

```text
stop(C) = nonProceeding(C.action)
```

If a future implementation stores both `action` and `stop`, the proof target
must require consistency between them.

## 4. Machine Contract

The abstract machine contract contains:

```text
domain_id: DomainId
subject_id: SubjectId
policy_id: PolicyId
schema_version: SchemaVersion
producer_id: ProducerId
contract_id: ContractId

action: Action
stop: Bool

reason_codes: ExplicitList ReasonCode
blocking_items: ExplicitList BlockingItem
not_evaluated: ExplicitList NotEvaluatedItem
not_claimed: ExplicitList NotClaimedItem

evidence_refs: ExplicitList EvidenceRef
proof_refs: ExplicitList ProofRef
```

The fields are semantic. They are not presentation details.

## 5. Explicit List Semantics

Formal Core V1 uses explicit lists with structural equality.

The specification chooses:

```text
ordered: true
deduplicated by construction: required for canonical contracts
multiplicity-preserving: not used for semantic multiplicity
empty allowed: true
field required: true
```

Rationale:

```text
empty list = known empty list
missing field = invalid contract
unknown list = represented through not_evaluated or fail-closed error
```

The future proof may use lists, finite sets, or vectors internally, but it must
define a canonical external equality relation.

## 6. Required Distinctions

The algebra must preserve these distinctions:

```text
NOT_EVALUATED != PASS

not_claimed != false

empty blocking_items != unknown blocking status

empty not_evaluated != missing not_evaluated field

empty not_claimed != missing not_claimed field
```

No theorem may erase these distinctions.

## 7. Typed Evidence

Formal Core V1 abstracts typed evidence as:

```text
TypedEvidence =
  domain_id
  subject_id
  evidence_claims
  evidence_refs
  adapter_identity
  evidence_validity
```

The core does not prove that raw input was parsed correctly.

The core only consumes:

```text
valid typed evidence
invalid typed evidence
incomplete typed evidence
conflicting typed evidence
version-incompatible typed evidence
```

Invalid or incompatible typed evidence must fail closed.

## 8. Policy and Context

Formal Core V1 abstracts policy/context as:

```text
PolicyContext =
  policy_id
  schema_version
  required_claims
  blocking_rules
  not_claimed_rules
  evidence_reference_rules
  proof_reference_rules
```

The proof target may assume `PolicyContext` is valid when proving normal
operation. Separate fail-closed theorems cover invalid policy/context.

## 9. Core Function Shape

The future formal function should be total:

```text
Core : TypedEvidence -> PolicyContext -> MachineContract
```

Failures are represented as fail-closed machine contracts rather than as
unhandled exceptions.

If a future Lean model uses an explicit result type, it must still prove that
all invalid or error cases cannot yield `PROCEED`.

## 10. Gate A Algebra

Gate A is specified as a wrapper over complete domain contracts:

```text
GateA : MachineContract -> UnifiedContract
```

Formal Core V1 requires preservation:

```text
GateA(C).machine_contract = C
```

or an equivalent structural preservation relation over all authoritative
fields.

Gate A may add identity and presentation metadata. It may not weaken, replace,
drop, or regenerate the domain contract.

## 11. Model and Presentation Fields

Model and presentation fields are outside the authoritative algebra.

If modeled, they must be typed as non-authoritative:

```text
ModelExplanation
PresentationText
SelfReport
Telemetry
```

No function from these fields may override:

```text
action
stop
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
```

## 12. Identity Assumptions

Formal Core V1 treats identity values as opaque unless separately proven.

The algebra requires equality relations for:

```text
contract_id
policy_id
schema_version
producer_id
evidence_refs
proof_refs
```

Hash correctness, canonical JSON byte equality, and serialization correctness
are not proven by the algebra unless separately authorized.

## 13. Non-Goals

This algebra does not specify:

```text
raw wheel parsing
pytest/JUnit parsing
Terraform JSON parsing
canonical JSON implementation
hash implementation
Python serialization
LLM behavior
benchmark runner behavior
```

Those remain outside Formal Core V1 unless separately brought into scope.
