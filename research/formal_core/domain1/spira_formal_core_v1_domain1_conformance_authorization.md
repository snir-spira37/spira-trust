# SPIRA Formal Core V1 Domain 1 Conformance Authorization

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_AUTHORIZED

DOMAIN_1_ONLY

DOMAIN2_CONFORMANCE_ACCEPTED_REQUIRED

DOMAIN3_CONFORMANCE_ACCEPTED_REQUIRED

FORMAL_DOMAIN1_TYPED_SEMANTICS_AUTHORIZED

DOMAIN1_LEAN_DEFINITIONS_AUTHORIZED

DOMAIN1_LEAN_PROOFS_AUTHORIZED

DOMAIN1_BASELINE_DIFFERENTIAL_EVALUATION_AUTHORIZED

DOMAIN1_CONFORMANCE_HARNESS_AUTHORIZED

ACCEPTED_DOMAIN1_IDENTITY_BASELINE_FROZEN

BASELINE_ROOT_RECOMPUTATION_AUTHORIZED

RESULTS_REPORT_REVIEW_REQUIRED

FORMAL_CORE_V1_ACTION_ALGEBRA_FROZEN

RAW_WHEEL_ZIP_PARSER_PROOF_NOT_AUTHORIZED

DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED

GATE_A_IMPLEMENTATION_CHANGES_NOT_AUTHORIZED

PRODUCTION_RUNTIME_INTEGRATION_NOT_AUTHORIZED

BENCHMARK_CHANGES_NOT_AUTHORIZED

NO_NEW_LIVE_SESSIONS

NO_EXISTING_RESULT_RECLASSIFICATION

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This document authorizes bounded Domain 1 conformance work for SPIRA Formal
Core V1.

Domain 1 is bounded Python artifact identity evidence at the accepted typed
evidence boundary.

The phase must keep three claims separate:

```text
A. Domain 1 typed-evidence semantics formally modeled and proved.

B. The accepted Domain 1 identity baseline differentially conforms to the
   Formal Core V1 action/list/identity projection.

C. Raw wheel, ZIP, RECORD, metadata, SBOM, filesystem, and parser correctness
   remain outside this proof boundary.
```

It must not merge these into a stronger parser, adapter, runtime, package
safety, or production claim.

## 2. Authorization Basis

This authorization follows:

```text
SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED

SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_ACCEPTED

SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED

SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED

DOMAIN_1_IDENTITY_BASELINE_ACCEPTED
```

## 3. Authorized Files

Lean files:

```text
formal/spira_formal_core_v1/SpiraFormalCore/Domain1/Evidence.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain1/Policy.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain1/Decision.lean
formal/spira_formal_core_v1/SpiraFormalCore/Domain1/Proofs.lean
```

The top-level Lean module may be updated only to import Domain 1 modules.

Python research harness:

```text
tools/run_formal_core_v1_domain1_conformance.py
```

Research outputs:

```text
research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_results.json
research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_report.md
research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_review.md
```

## 4. Frozen Inputs

The phase may read but must not modify:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json

research/domain1_identity_baseline_review.md

source/spira_core/unification_proof.py

source/spira_core/formal_core_v1.py
```

The accepted baseline root is frozen as:

```text
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

The expected record count is frozen as:

```text
1954
```

## 5. Formal Domain 1 Language

Model at least the typed evidence already present in the accepted identity
baseline:

```text
artifact identity

subject identity

claims identity

context identity

decision identity

proof identity

recommended agent action

stop state

reason_codes

not_evaluated

worst claim status

not_claimed boundaries derived from the Formal Core V1 policy context
```

The formal language may abstract away raw wheel bytes, ZIP members, RECORD rows,
SBOM documents, filesystem paths, and parser-specific internal structures.

## 6. Required Domain 1 Proof Obligations

The phase must prove at least:

```text
NOT_EVALUATED worst-claim status prevents silent PASS

required unknown artifact checks prevent PROCEED

explicit reason_codes are preserved

explicit not_evaluated lists are preserved

stop state is consistent with the bounded Domain 1 action projection

artifact / subject / claims / context / decision / proof identities are
preserved in the formal projection

parse / validation / internal error evidence fails closed
```

Proofs must contain:

```text
no sorry
no admit
no custom axiom
no sorryAx
```

## 7. Differential Baseline Gates

The research harness must evaluate:

```text
1954 / 1954 accepted Domain 1 identity baseline records
```

and compare:

```text
accepted baseline record

Formal Core V1 Domain 1 typed-evidence projection

bounded Domain 1 action/list/identity semantics
```

Required gates:

```text
1954 / 1954 records evaluated

1954 / 1954 formal projection matches accepted baseline action

1954 / 1954 stop state preserved

1954 / 1954 reason_codes preserved

1954 / 1954 not_evaluated preserved

1954 / 1954 artifact identity preserved

1954 / 1954 subject identity preserved

1954 / 1954 claims identity preserved

1954 / 1954 context identity preserved

1954 / 1954 decision identity preserved

1954 / 1954 proof identity preserved

baseline root recomputes exactly

false PROCEED count = 0

NOT_EVALUATED to PROCEED count = 0

identity drop count = 0

list drop count = 0

sensitive / private path leakage count = 0
```

## 8. Required Tests

The phase must run at least:

```text
lake build

Domain 1 conformance harness

focused Python tests covering the Domain 1 baseline and Formal Core boundary
```

The full pytest suite may be run if practical, but known unrelated failures
must not be fixed under this authorization.

## 9. Required Outputs

The results JSON must include:

```text
status
record_count
record_pass_count
record_fail_count
action_distribution
baseline_root_recomputed
baseline_root_expected
baseline_root_match
false_proceed_records
not_evaluated_to_proceed_records
identity_drop_records
list_drop_records
sensitive_or_private_leak_records
lean_build
proof_scan
mismatches
```

The report must summarize the executed checks.

The review must end with one of:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED

SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_NEEDS_REVISION

SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_REJECTED
```

## 10. Explicitly Not Authorized

This authorization does not permit:

```text
raw wheel / ZIP parser proof

RECORD parser proof

SBOM parser proof

filesystem proof

Python runtime proof

Domain 1 adapter changes

Gate A implementation changes

Formal Core V1 action algebra changes

Domain 2 changes

Domain 3 changes

benchmark runner changes

Claude / Codex / DeepSeek sessions

result reclassification

production claim

merge to main

release

version bump

tag

PyPI publish
```

## 11. Stop Conditions

Stop and produce a needs-revision review if any of the following occurs:

```text
accepted baseline root does not recompute

record count is not 1954

Lean build fails

proof scan finds sorry / admit / axiom / sorryAx

any baseline record maps to an unsupported Formal Core V1 action

any non-PROCEED baseline action is projected as PROCEED

any NOT_EVALUATED record is projected as silent PASS

any explicit reason_codes or not_evaluated list is dropped

any identity hash is dropped or changed

private path or sensitive value leakage appears in public outputs
```

## 12. Final Boundary

Successful Domain 1 conformance may support only this claim:

```text
Given the accepted Domain 1 typed identity baseline records, the Formal Core V1
Domain 1 projection preserves the bounded action, stop state, explicit lists,
and identity bindings across 1,954 records.
```

It may not support this stronger claim:

```text
SPIRA has formally proved raw Python wheel parsing, package safety, SBOM
correctness, filesystem behavior, Python runtime behavior, or release readiness.
```
