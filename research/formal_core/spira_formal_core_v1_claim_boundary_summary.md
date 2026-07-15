# SPIRA Formal Core V1 Claim Boundary Summary

## Proven / Machine-Checked

```text
Formal Core V1 Lean definitions build successfully.

The accepted theorem/proof modules build without sorry, admit, custom axiom,
or sorryAx.

The core typed-evidence theorems cover determinism, blocking behavior,
NOT_EVALUATED preservation, explicit-list preservation, Gate A abstract
preservation, model non-authority, and fail-closed error behavior.
```

## Differentially Conformant On Accepted Corpora

```text
Domain 1:
  1954 / 1954 accepted identity baseline records

Domain 2:
  38 / 38 accepted pytest cases
  6 / 6 mutation pairs

Domain 3:
  40 / 40 accepted Terraform Plan cases
  10 / 10 mutation pairs
```

## Tested Only

```text
Python executable reference
Python typed-evidence boundary
Domain conformance harnesses
JSON serialization used by harnesses
Canonical JSON used by harnesses
Passthrough envelope validator
Passthrough MVP integration
```

## Trusted Assumptions

```text
Lean kernel soundness
Lean standard library behavior
Python runtime for harness execution
Operating system behavior
SHA-256 implementation
Filesystem behavior
```

## Out Of Scope

```text
LLM provider behavior
benchmark runner behavior
reports and UI
raw private model outputs
live agent sessions
```

## Not Formally Proved

```text
raw wheel / ZIP / RECORD parsing
raw pytest / JUnit parsing
raw Terraform Plan JSON parsing
JSON canonicalization implementation correctness
SHA-256 implementation correctness
Python runtime correctness
filesystem correctness
operating-system correctness
production integration
release readiness
```

## Not Authorized

```text
production claim
release
version bump
tag
PyPI publish
result reclassification
new live agent benchmark sessions
```

## Accepted Claim Shape

```text
Given typed evidence satisfying the Formal Core V1 domain language and bounded
policy context, the Formal Core V1 projection preserves the authoritative
action, stop state, explicit contractual lists, evidence/proof identity, and
fails closed rather than producing unsafe PROCEED under the accepted domain
gates.
```

## Disallowed Claim Shape

```text
SPIRA has formally proved all parsers, adapters, runtime behavior, LLM behavior,
release readiness, or package safety.
```
