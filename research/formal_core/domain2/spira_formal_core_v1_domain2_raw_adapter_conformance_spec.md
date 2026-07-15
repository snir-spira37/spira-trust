# SPIRA Formal Core V1 Domain 2 Raw Adapter Conformance Specification

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_SPEC_PROPOSED
SPECIFICATION_ONLY
RAW_PARSER_PROOF_NOT_CLAIMED
```

## 1. Purpose

This specification defines the next deterministic boundary after the accepted Formal Core V1 typed-evidence package:

```text
raw Domain 2 pytest evidence
-> Domain 2 adapter
-> typed evidence
-> Formal Core V1
-> authoritative machine contract
```

It does not implement or prove the adapter. It defines what a later implementation and conformance phase must prove or test.

## 2. In-Scope Raw Inputs

Domain 2 raw adapter conformance is limited to bounded local pytest result evidence:

```text
console text
JUnit XML text
metadata JSON
public run materialization JSON
declared collection/test-id metadata from the corpus manifest
```

Out of scope for this phase:

```text
arbitrary pytest plugin semantics
networked test execution
runtime execution correctness
operating-system behavior
filesystem correctness
unbounded XML language proof
LLM or agent behavior
```

## 3. Input State Classification

The adapter must classify each raw evidence bundle into exactly one top-level input state:

```text
SUPPORTED_COMPLETE
SUPPORTED_WITH_NONBLOCKING_NOTES
INCOMPLETE
MALFORMED
CONFLICTING
UNSUPPORTED
INTERNAL_ADAPTER_FAILURE
```

### 3.1 Supported Complete

Required conditions:

```text
metadata required fields present
collection identity present
test result evidence complete
console/JUnit evidence not conflicting
no malformed required source
```

Allowed outcomes:

```text
PROCEED
STOP_BLOCKED
REPORT_NOT_EVALUATED
```

`PROCEED` is allowed only when no blocking failure and no required unknown are present.

### 3.2 Supported With Nonblocking Notes

Nonblocking notes include:

```text
SKIPPED
XFAILED
REPORT_WITH_NOTES legacy projection
```

Formal Core projection:

```text
REPORT_WITH_NOTES -> PROCEED + TEST_NOTES
```

The note must be preserved as a reason code or typed note claim; it must not silently disappear.

### 3.3 Incomplete

Incomplete evidence includes:

```text
missing required metadata
missing required result source
capture_complete = false for a required source
public raw outputs withheld when required for the decision
```

Required behavior:

```text
action = REPORT_NOT_EVALUATED
stop = true
not_evaluated includes the missing or withheld item
PROCEED forbidden
```

### 3.4 Malformed

Malformed evidence includes:

```text
malformed required JSON
malformed required JUnit/XML
unparseable required result structure
invalid required field type
```

Required behavior:

```text
fail closed
PROCEED forbidden
not_evaluated or blocking_items must preserve the malformed source
```

### 3.5 Conflicting

Conflicting evidence includes:

```text
console says pass while JUnit says fail
console says fail while JUnit says pass
inconsistent exit-code/result-state combinations
identity mismatch across required sources
```

Required behavior:

```text
PROCEED forbidden
reason_codes includes TEST_EVIDENCE_CONFLICT or equivalent typed reason
not_evaluated preserves the unresolved source conflict when the final state is unknown
```

### 3.6 Unsupported

Unsupported evidence includes:

```text
unsupported schema version
unsupported result format
unsupported source media type
unbounded plugin-dependent semantics
```

Required behavior:

```text
REPORT_NOT_EVALUATED or STOP_BLOCKED
PROCEED forbidden
not_evaluated records unsupported format or unsupported semantics
```

### 3.7 Internal Adapter Failure

Internal adapter failure includes:

```text
unexpected exception
identity construction failure
hashing failure
canonicalization failure
```

Required behavior:

```text
fail closed
PROCEED forbidden
error recorded outside the authoritative contract when needed
```

## 4. Required Typed Evidence Fields

The adapter output must be projectable into Formal Core V1 typed evidence with:

```text
domain_id = pytest_result
subject_id
schema_version
producer_id
evidence_validity
typed_claims
evidence_refs
proof_refs
policy_id
policy_schema_version
policy_required_claims
policy_blocking_rules
policy_not_claimed_rules
```

The adapter must preserve:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence references
proof references
scope identity
result identity
collection identity
```

## 5. Mapping Obligations

### 5.1 Clean Success

If all required sources are complete and consistent, exit code is zero, and no failure/error is present:

```text
typed blocking claims = []
typed not_evaluated claims = []
reason_codes includes TESTS_PASSED
not_claimed includes producer_correctness and software_safety
action may be PROCEED
```

### 5.2 Blocking Failure

If any blocking test failure is observed:

```text
blocking_items contains the failed test or run-level blocker
reason_codes includes TEST_FAILURES_DETECTED or equivalent accepted reason
action = STOP_BLOCKED
PROCEED forbidden
```

### 5.3 Collection Or Run-Level Error

If collection, setup, import, or run-level evidence prevents reliable success:

```text
blocking_items or not_evaluated records the affected run-level condition
action != PROCEED
```

### 5.4 Unknown Required Information

If a required source cannot be evaluated:

```text
not_evaluated includes the source or required fact
action = REPORT_NOT_EVALUATED
PROCEED forbidden
```

### 5.5 Evidence Conflict

If required sources conflict:

```text
reason_codes includes TEST_EVIDENCE_CONFLICT
not_evaluated records unresolved source truth
PROCEED forbidden
```

### 5.6 Nonblocking Notes

If only nonblocking notes are present:

```text
blocking_items = []
not_evaluated = []
reason_codes includes TEST_NOTES
Formal Core conformance action = PROCEED
```

This mapping is accepted only under the prior Domain 2 action mapping amendment. It must not hide blockers or unknowns.

## 6. Fixture Corpus Required Before Implementation

A later fixture authorization should materialize at least:

```text
3 clean successes
3 assertion failures
2 collection/import errors
2 malformed JUnit/XML cases
2 malformed metadata JSON cases
2 incomplete evidence cases
2 console/JUnit conflict cases
2 withheld raw output cases
2 unsupported format cases
2 nonblocking note cases
2 identity mismatch cases
2 internal adapter failure simulations
```

Each fixture must include expected:

```text
input_state
typed evidence projection
Formal Core contract
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
validator outcome
```

## 7. Differential Conformance Plan

A later implementation must compare:

```text
existing Python Domain 2 producer output
new typed-evidence adapter output
Formal Core V1 Python reference output
Lean theorem boundary expectations
existing Domain 2 conformance corpus
new raw-adapter fixtures
```

Acceptance requires:

```text
no false PROCEED
no blocking item loss
no not_evaluated loss
no not_claimed loss
no evidence/proof identity loss
malformed inputs fail closed
conflicts fail closed
nonblocking notes preserved
existing accepted Domain 2 conformance still passes
full pytest passes
```

## 8. Claim Boundary

Allowed after this specification:

```text
SPIRA has specified a Domain 2 raw-adapter conformance boundary for mapping bounded pytest evidence into Formal Core V1 typed evidence.
```

Disallowed:

```text
SPIRA has formally proved raw pytest/JUnit parsing.
SPIRA has proved arbitrary pytest behavior.
SPIRA has proved runtime, filesystem, OS, or LLM behavior.
SPIRA is release-ready based on this specification.
```

## 9. Recommended Next Authorization

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_FIXTURE_AUTHORIZATION
```

That next step should materialize the fixture corpus only. It should still not change the adapter implementation or claim parser proof.
