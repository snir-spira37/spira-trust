# SPIRA Formal Core V1 Trusted Computing Base Ledger

## Status

```text
SPIRA_FORMAL_CORE_V1_TRUSTED_COMPUTING_BASE_LEDGER_SPECIFIED

SPECIFICATION_ONLY

PROVEN_TESTED_TRUSTED_OUT_OF_SCOPE_SEPARATED

NO_PRODUCTION_CLAIM
```

## 1. Purpose

This ledger records what a future Formal Core V1 proof may prove, what it must
trust, what remains tested only, and what is outside the initial proof boundary.

No SPIRA claim may collapse these categories.

## 2. Classification Values

```text
PROVEN_TARGET
TRUSTED_ASSUMPTION
TESTED_ONLY
FUTURE_CONFORMANCE_REQUIRED
OUT_OF_SCOPE
```

## 3. Ledger

| Component | V1 Classification | Notes |
| --- | --- | --- |
| Lean kernel | TRUSTED_ASSUMPTION | Future proof depends on Lean soundness. |
| Lean standard library used by proofs | TRUSTED_ASSUMPTION | Exact dependency set must be locked later. |
| Formal core definitions | PROVEN_TARGET | Once implementation is authorized. |
| Seven theorem proofs | PROVEN_TARGET | Future proof scripts, not authorized yet. |
| Contract algebra statements | PROVEN_TARGET | Specification target only in this phase. |
| Typed-evidence validity predicates | PROVEN_TARGET | Defined formally later. |
| Domain 2 conformance | FUTURE_CONFORMANCE_REQUIRED | Planned first; not proven now. |
| Domain 1 conformance | FUTURE_CONFORMANCE_REQUIRED | Later domain plan required. |
| Domain 3 conformance | FUTURE_CONFORMANCE_REQUIRED | Later domain plan required. |
| Raw wheel/ZIP parsing | OUT_OF_SCOPE | Adapter responsibility. |
| pytest/JUnit parsing | OUT_OF_SCOPE | Adapter responsibility until conformance work. |
| Terraform Plan JSON parsing | OUT_OF_SCOPE | Adapter responsibility until conformance work. |
| Python runtime | TRUSTED_ASSUMPTION | Not proven by Lean core. |
| Operating system | TRUSTED_ASSUMPTION | Not proven by Lean core. |
| JSON serialization | TESTED_ONLY | Unless separately formalized. |
| Canonical JSON implementation | TESTED_ONLY | Hash claims depend on this unless proven later. |
| SHA-256 implementation | TRUSTED_ASSUMPTION | External cryptographic primitive. |
| Existing Python SPIRA implementation | TESTED_ONLY | Differential equivalence may be later work. |
| Gate A Python implementation | TESTED_ONLY | Formal preservation theorem applies to abstract Gate A first. |
| Passthrough envelope implementation | TESTED_ONLY | Already tested; not part of formal core proof. |
| Envelope validator implementation | TESTED_ONLY | Deterministic tests exist; not formal proof target now. |
| LLM providers | OUT_OF_SCOPE | Model behavior not proven. |
| Benchmark runners | OUT_OF_SCOPE | Paused and not part of Formal Core V1. |
| Reports and UI | OUT_OF_SCOPE | Presentation only. |

## 4. Canonicalization and Identity Assumptions

Formal Core V1 may use structural identity internally.

External identity mechanisms must be classified separately:

```text
contract hash: TESTED_ONLY unless hash/canonicalization is proved
source contract hash: TESTED_ONLY unless hash/canonicalization is proved
canonical JSON bytes: TESTED_ONLY unless canonicalizer is proved
evidence reference hash: TRUSTED_ASSUMPTION or TESTED_ONLY depending on source
proof reference hash: TRUSTED_ASSUMPTION or TESTED_ONLY depending on source
```

The future proof must not imply byte-level JSON identity unless byte-level
canonicalization is brought into the proof boundary.

## 5. Claim Discipline

Allowed future claim shape:

```text
Given typed evidence satisfying the formal evidence language and a valid policy,
the SPIRA Formal Core V1 produces an authoritative machine contract satisfying
the proven theorem set.
```

Disallowed claim shape:

```text
SPIRA has formally proven all parsers, adapters, agents, files, reports, and
runtime behavior.
```

## 6. Required Updates Later

This ledger must be updated before:

```text
Lean implementation authorization

Domain 2 conformance authorization

Python differential equivalence authorization

external reproduction package

any production or release claim
```
