# SPIRA Formal Core V1 Domain 2 Conformance Plan

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_PLAN_SPECIFIED

PLAN_ONLY

DOMAIN_2_FIRST_CONFORMANCE_TARGET

NO_DOMAIN_ADAPTER_CHANGES

NO_LEAN_IMPLEMENTATION

NO_PROOF_SCRIPTS

NO_PYTHON_CODE_CHANGES
```

## 1. Purpose

This document specifies why Domain 2, bounded local pytest result evidence, is
the first planned conformance target for SPIRA Formal Core V1.

It is a plan only. It does not implement adapter conformance or proof scripts.

## 2. Why Domain 2 First

Domain 2 has a compact typed-evidence vocabulary:

```text
tests passed
tests failed
collection error
conflicting evidence
malformed evidence
required information unknown
```

This makes it the smallest useful domain for proving the shape of:

```text
typed evidence -> formal core -> authoritative machine contract
```

## 3. Proposed Typed Evidence Vocabulary

The first Domain 2 typed-evidence language should include:

```text
test_run_present: Bool
collection_succeeded: Bool
failed_test_count: Nat
passed_test_count: Nat
error_count: Nat
conflict_present: Bool
malformed_result: Bool
required_unknown: ExplicitList NotEvaluatedItem
evidence_refs: ExplicitList EvidenceRef
```

The final vocabulary may change during conformance authorization, but it must
remain small enough to prove directly.

## 4. Planned Domain 2 Decision Obligations

### 4.1 Proceed Requires Clean Evidence

```text
Domain2Core(E, P).action = PROCEED
=>
failed_test_count = 0
and error_count = 0
and conflict_present = false
and malformed_result = false
and required_unknown = []
```

### 4.2 Failure Blocks Proceed

```text
failed_test_count > 0
=>
action != PROCEED
```

### 4.3 Collection Error Blocks Proceed

```text
collection_succeeded = false
=>
action != PROCEED
```

### 4.4 Unknown Required Information Is Preserved

```text
item in required_unknown
=>
item in contract.not_evaluated
and action != PROCEED
```

### 4.5 Malformed Evidence Fails Closed

```text
malformed_result = true
=>
action != PROCEED
and stop = true
```

## 5. Adapter Boundary

The Domain 2 adapter remains outside the initial proof boundary.

The future conformance work must distinguish:

```text
pytest raw output
JUnit or other result files
adapter extraction
typed evidence
formal core contract
```

Formal Core V1 can prove the decision over typed evidence. It does not prove
that every pytest file was parsed correctly.

## 6. Conformance Evidence Needed Later

A later Domain 2 conformance authorization should require:

```text
typed-evidence schema
adapter mapping table
positive and negative typed-evidence examples
malformed evidence examples
conflicting evidence examples
expected formal core contracts
differential comparison against existing Python behavior
```

## 7. Non-Authorization

This plan does not authorize:

```text
Domain 2 adapter changes
new pytest fixtures
Lean implementation
proof scripts
Python changes
benchmark changes
live sessions
production claims
```

## 8. Success Criteria for Future Conformance

Future Domain 2 conformance should be accepted only if:

```text
typed evidence vocabulary is stable
adapter boundary is explicit
PROCEED requires clean evidence
failures and errors prevent PROCEED
required unknowns are preserved
malformed evidence fails closed
the mapping to Formal Core V1 is reviewable
```
