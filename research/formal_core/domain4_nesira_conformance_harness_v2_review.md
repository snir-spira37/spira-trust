# SPIRA Domain 4 / Nesira Conformance Harness V2 Review

## Verdict

```text
DOMAIN4_NESIRA_CONFORMANCE_HARNESS_V2_ACCEPTED
```

This review accepts the V2 conformance-harness specification as the correct
paper plan for connecting future Python raw-artifact classification to the
future Lean decision core.

It does not authorize Lean implementation, Lean proof scripts, Python changes,
fixture materialization, harness implementation, Phase 2 work, public claims, or
release.

Reviewed artifact:

```text
research/formal_core/domain4_nesira_conformance_harness_v2_spec.md
```

## Review Findings

### 1. The Harness Is Correctly Split Into Two Strength Levels

The review accepts the split:

```text
Layer 1:
  exhaustive core agreement over the finite V2 enum space

Layer 2:
  empirical raw -> enum classification faithfulness through mutation pairs
```

This avoids overclaiming mutation tests as proof while still making the future
Lean proof relevant to Python behavior.

### 2. Exhaustive Core Agreement Is Required

The finite core space is:

```text
2 artifact kinds * 3 execution meta values * 3^9 outcome tuples = 118098 tuples
```

The review accepts the requirement that future PythonCore and LeanCore must
agree on all 118098 tuples, including raw-unreachable tuples, because those
tuples test totality and deterministic behavior.

### 3. Mutation-Pair Requirements Target The Safety Boundary

The required mutation targets are accepted:

```text
ExecutionMeta.INPUT_MALFORMED
ExecutionMeta.TOOL_ERROR
HashOutcome.HASH_MISMATCH
PathOutcome.PATH_UNSAFE
SymlinkOutcome.SYMLINK_ESCAPE
DuplicateOutcome.DUP_PRESENT
DirectoryEvidenceOutcome.DIR_AS_FILE
ContextOutcome.CONTEXT_MISMATCH
ContextOutcome.CONTEXT_EXPECTED_MISSING
```

These are the boundaries where a false raw -> enum classification could produce
a false VALID, hide a required NOT_EVALUATED path, or weaken a safety stop.

### 4. Mutation Minimality Is Required

The review accepts the requirement that each mutation pair changes exactly the
raw condition under test. A mutation that changes several independent
properties cannot prove classifier sensitivity for one enum value.

### 5. Reason-Code Fidelity Is Correctly Assigned To The Harness

The decision table intentionally stayed at action/status resolution. The harness
spec correctly carries the remaining obligation:

```text
exact accepted Phase 1 reason codes and details must be reproduced by fixtures
and future conformance results.
```

This preserves a lean proof core without losing Phase 1 fidelity.

### 6. Canonical Serialization And Two-Run Equality Are Required

The review accepts canonical JSON and byte-for-byte two-run equality as required
determinism checks for:

```text
OutcomeTuple
MachineContract
core-agreement results
mutation-pair results
reason-code fidelity results
```

### 7. NOT_PROVEN Ledger Boundary Is Preserved

The harness specification explicitly preserves:

```text
SPIRA_NESIRA_DOMAIN4_NOT_PROVEN_V1
```

The review confirms that the harness does not claim:

```text
general raw -> enum correctness
filesystem correctness
hash correctness over all possible bytes
signature trust
signer authority
actual isolation execution
permission to sever
production readiness
```

### 8. This Completes The Paper Design Chain

The accepted paper chain is now:

```text
Domain4 / Nesira formal-core proposal
-> V2 flag schema
-> NOT_PROVEN ledger
-> V2 decision table
-> V2 conformance harness specification
```

The next step may be a separate Lean implementation authorization. That
authorization must still be explicit and narrow.

## Required Next Step

The next document should be:

```text
research/formal_core/domain4_nesira_lean_implementation_authorization.md
```

It should authorize only:

```text
Lean definitions for Domain4 / Nesira V2
Lean decision-table implementation
Lean theorem statements and proof scripts for the accepted V2 table
exhaustive core-space enumeration support, if needed for proof/reproduction
local proof results and review
```

It must not authorize:

```text
Python changes
fixture materialization
conformance harness implementation
Phase 2 implementation
public claims
release
```

## Not Authorized

This review does not authorize:

```text
Lean definitions
Lean proof scripts
Python code changes
Nesira validator changes
new fixtures
fixture materialization
test implementation
conformance harness implementation
decision-table implementation
Phase 1 reopening
Phase 2 implementation
signature verification
signer authority checks
isolation runner implementation
combined verdict integration
CLI or wheel exposure
public capability claims
release
```

## Status

```text
DOMAIN4_NESIRA_CONFORMANCE_HARNESS_V2_ACCEPTED

EXHAUSTIVE_CORE_AGREEMENT_ACCEPTED
FULL_ENUM_SPACE_SIZE_118098_ACCEPTED
CLASSIFICATION_MUTATION_PAIRS_ACCEPTED
SAFETY_CRITICAL_ENUM_MUTATIONS_ACCEPTED
REASON_CODE_FIDELITY_ACCEPTED
TWO_RUN_EQUALITY_ACCEPTED
NOT_PROVEN_LEDGER_BINDING_ACCEPTED

DOMAIN4_NESIRA_PAPER_DESIGN_CHAIN_COMPLETE
LEAN_IMPLEMENTATION_AUTHORIZATION_REQUIRED_NEXT

LEAN_IMPLEMENTATION_NOT_AUTHORIZED
PROOF_SCRIPTS_NOT_AUTHORIZED
PYTHON_CODE_CHANGES_NOT_AUTHORIZED
FIXTURE_MATERIALIZATION_NOT_AUTHORIZED
CONFORMANCE_HARNESS_IMPLEMENTATION_NOT_AUTHORIZED
PHASE2_IMPLEMENTATION_NOT_AUTHORIZED
PUBLIC_CAPABILITY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
