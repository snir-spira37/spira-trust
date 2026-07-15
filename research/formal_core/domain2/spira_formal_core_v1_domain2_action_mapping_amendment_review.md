# SPIRA Formal Core V1 Domain 2 Action Mapping Amendment Review

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_ACTION_MAPPING_AMENDMENT_ACCEPTED

REPORT_WITH_NOTES_PROJECTS_TO_PROCEED_WITH_TEST_NOTES

FORMAL_CORE_V1_ACTION_ALGEBRA_PRESERVED

DOMAIN2_ORACLE_PRESERVED

TEST_NOTES_PRESERVATION_REQUIRED

BLOCKING_AND_NOT_EVALUATED_SAFETY_INVARIANTS_PRESERVED

DOMAIN2_CONFORMANCE_RERUN_AUTHORIZATION_REQUIRED

LEAN_CODE_CHANGES_NOT_AUTHORIZED

PYTHON_CODE_CHANGES_NOT_AUTHORIZED

DOMAIN_ADAPTER_CHANGES_NOT_AUTHORIZED

DOMAIN3_NOT_AUTHORIZED

DOMAIN1_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Review Scope

This review covers:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_action_mapping_amendment_proposal.md
```

The review resolves the decision required by:

```text
FORMAL_CORE_V1_ACTION_ALGEBRA_OR_DOMAIN2_ACTION_MAPPING_AMENDMENT_REQUIRED
```

from:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_review.md
```

## 2. Decision

The amendment is accepted.

Domain 2 `REPORT_WITH_NOTES` is not added to the Formal Core V1 shared action
algebra.

Instead, Domain 2 conformance must project it as:

```text
REPORT_WITH_NOTES
-> PROCEED
```

while preserving the note semantics through:

```text
reason_codes = [TEST_NOTES]
stop = false
blocking_items = []
not_evaluated = []
```

and preserving all explicit lists, evidence/proof references, and identity
fields.

## 3. Why the Mapping Is Accepted

The two Domain 2 oracle cases that use `REPORT_WITH_NOTES` are note-only
continuation cases.

They do not represent:

```text
a blocker
a required unknown
a malformed result
a conflicting result
a rerun requirement
```

They represent:

```text
continue, but carry TEST_NOTES in the contract
```

Therefore they do not require a new shared Formal Core action.

The accepted mapping keeps Formal Core V1 small while preserving the semantic
distinction between:

```text
plain PROCEED
```

and:

```text
PROCEED with TEST_NOTES
```

through the explicit `reason_codes` field.

## 4. Required Guardrails

The accepted mapping is valid only for non-blocking note-only Domain 2 outcomes.

The conformance layer must reject or fail closed if a `REPORT_WITH_NOTES` case
contains:

```text
stop = true

blocking_items != []

not_evaluated != []

missing TEST_NOTES

malformed evidence

conflicting evidence

identity mismatch

dropped evidence/proof references
```

No conformance implementation may use this amendment to hide blockers,
unknowns, malformed evidence, or missing metadata behind `PROCEED`.

## 5. Preserved Formal Core V1 Invariants

The review confirms that this amendment does not weaken the seven accepted
Formal Core V1 theorem families:

```text
Determinism

Blocking claim prevents PROCEED

Required NOT_EVALUATED prevents silent PASS

Explicit contractual lists are preserved

Gate A preserves the complete domain contract

Model and presentation fields have zero decision authority

Parse/internal/validation errors fail closed
```

The only accepted projection is a domain-specific action-label projection at
the conformance boundary.

It does not permit loss of semantic lists or identities.

## 6. Preserved Negative Finding

The previous Domain 2 conformance attempt remains a valid negative finding:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_NEEDS_REVISION
```

It is not reclassified.

It correctly identified that the mapping was not yet specified.

## 7. No Oracle or Corpus Rewrite

The Domain 2 oracle and corpus remain frozen.

This review does not authorize changing:

```text
research/test_build_failure_contract/oracle_v1.json
research/test_build_failure_contract/corpus_manifest_v1.json
```

The oracle may continue to express the domain-level action:

```text
REPORT_WITH_NOTES
```

The formal conformance layer must record the reviewed projection to:

```text
PROCEED + TEST_NOTES
```

## 8. Required Next Step

The next step is a separate authorization for a Domain 2 conformance rerun under
this accepted mapping.

That rerun should verify at least:

```text
38 / 38 Domain 2 oracle cases evaluated or explicitly rejected

2 / 2 REPORT_WITH_NOTES cases project to PROCEED

2 / 2 REPORT_WITH_NOTES cases preserve TEST_NOTES

0 TEST_NOTES drops

0 blocking-to-proceed mappings

0 not_evaluated-to-proceed mappings

0 malformed-to-proceed mappings

0 identity drops

0 evidence/proof reference drops
```

The rerun authorization must still separately decide whether any Lean or Python
conformance implementation changes are required.

## 9. Still Blocked

This review does not authorize:

```text
Lean code changes

Lean proof changes

Python code changes

Domain adapter changes

Domain 2 conformance rerun execution

Domain 3 conformance

Domain 1 conformance

runtime integration

benchmark execution

new live sessions

existing result reclassification

production formal-verification claim

release
```

## 10. Accepted Summary

```text
REPORT_WITH_NOTES is a Domain 2 presentation/action label for note-only
continuation.

Formal Core V1 remains minimal.

The formal projection is PROCEED.

The note is preserved through TEST_NOTES in reason_codes.

Blocking, unknown, malformed, conflicting, or identity-drifting cases cannot
use this projection to proceed.

Domain 2 conformance may be retried only after separate authorization.
```
