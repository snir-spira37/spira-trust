# SPIRA Formal Core V1 Domain 2 Action Mapping Amendment Proposal

## Status

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_ACTION_MAPPING_AMENDMENT_PROPOSED

DOMAIN2_REPORT_WITH_NOTES_MAPPING_PROPOSED

FORMAL_CORE_V1_ACTION_ALGEBRA_PRESERVED

REPORT_WITH_NOTES_PROJECTS_TO_PROCEED_WITH_TEST_NOTES

DOMAIN2_ORACLE_PRESERVED

NO_LEAN_CODE_CHANGE_AUTHORIZATION

NO_PYTHON_CODE_CHANGE_AUTHORIZATION

NO_DOMAIN_ADAPTER_CHANGE_AUTHORIZATION

DOMAIN2_CONFORMANCE_RERUN_AUTHORIZATION_REQUIRED

DOMAIN3_NOT_AUTHORIZED

DOMAIN1_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## 1. Purpose

This proposal resolves the conformance blocker recorded in:

```text
research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_review.md
```

The blocker is:

```text
DOMAIN2_ORACLE_ACTION_OUTSIDE_FORMAL_CORE_V1_ACTION_ALGEBRA
```

The frozen Domain 2 oracle contains two note-only outcomes with:

```text
recommended_agent_action = REPORT_WITH_NOTES
reason_codes = [TEST_NOTES]
stop = false
```

Formal Core V1 intentionally keeps the shared action algebra minimal:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

The conformance layer therefore needs an explicit, reviewed mapping between
Domain 2's richer presentation action and the smaller Formal Core V1 action
algebra.

## 2. Decision Proposed

This proposal chooses the narrow mapping option:

```text
REPORT_WITH_NOTES
-> PROCEED
```

with the required preservation of:

```text
reason_codes = [TEST_NOTES]
stop = false
blocking_items = []
not_evaluated = []
not_claimed
evidence references
proof references
domain identity
subject identity
policy identity
schema/version identity
producer identity
contract identity
```

The note is not discarded. It is carried as explicit contract metadata through
the authoritative fields that Formal Core V1 already proves are semantic and
preserved.

## 3. Rationale

`REPORT_WITH_NOTES` is not a blocking decision category.

For the Domain 2 cases that triggered the blocker, the oracle says:

```text
stop = false
blocking_items = []
not_evaluated = []
reason_codes = [TEST_NOTES]
```

This is semantically a continuing outcome with non-blocking notes, not a fifth
shared action category needed by all domains.

Expanding the Formal Core V1 action algebra would make the shared core larger
to represent a Domain 2 presentation distinction. That would weaken the design
goal of a small shared proof target.

The better boundary is:

```text
Domain-specific action vocabulary
-> reviewed conformance projection
-> minimal shared Formal Core action algebra
```

## 4. Mapping Table

Domain 2 conformance should use the following action projection:

| Domain 2 oracle action | Formal Core V1 action | Required preservation |
| --- | --- | --- |
| `PROCEED` | `PROCEED` | All explicit lists and identities preserved |
| `REPORT_WITH_NOTES` | `PROCEED` | `TEST_NOTES` preserved in `reason_codes`; `stop=false`; no blockers or required unknowns |
| `STOP_BLOCKED` | `STOP_BLOCKED` | Blocking items and reasons preserved |
| `RERUN_REQUIRED` | `RERUN_REQUIRED` | Rerun reason and blocking state preserved |
| `REPORT_NOT_EVALUATED` | `REPORT_NOT_EVALUATED` | `not_evaluated` preserved |

No other Domain 2 action is accepted by this amendment.

## 5. Validity Preconditions

The `REPORT_WITH_NOTES -> PROCEED` projection is valid only when all of the
following are true:

```text
domain = Domain 2 / pytest result evidence

recommended_agent_action = REPORT_WITH_NOTES

stop = false

reason_codes contains TEST_NOTES

blocking_items = []

not_evaluated = []

the note is represented in explicit contract metadata

all evidence/proof/identity fields are preserved
```

If any of these preconditions fail, the conformance projection must not silently
produce `PROCEED`.

Instead it must record a conformance error and fail closed for the attempted
mapping.

## 6. Preservation Requirements

The action projection is the only permitted semantic projection.

The following fields must remain exact under Domain 2 conformance comparison:

```text
reason_codes
blocking_items
not_evaluated
not_claimed
evidence_refs
proof_refs
domain_id
subject_id
policy_id
schema_version
producer_id
contract_id
```

For `REPORT_WITH_NOTES`, `TEST_NOTES` must not be dropped, converted into
presentation text only, or treated as optional.

The conformance harness must be able to distinguish:

```text
clean proceed with no notes
```

from:

```text
proceed with TEST_NOTES
```

even though both project to the same Formal Core V1 action.

## 7. Safety Invariants

This amendment must not weaken any Formal Core V1 safety theorem.

In particular:

```text
blocking claim prevents PROCEED

required NOT_EVALUATED prevents silent PASS

explicit lists are preserved

parse/internal/validation errors fail closed

model and presentation fields have zero decision authority
```

`REPORT_WITH_NOTES` may project to `PROCEED` only because it is a non-blocking,
fully evaluated, note-only outcome.

It does not authorize:

```text
REPORT_WITH_NOTES with blockers -> PROCEED

REPORT_WITH_NOTES with required unknowns -> PROCEED

REPORT_WITH_NOTES with malformed evidence -> PROCEED

REPORT_WITH_NOTES with conflicting evidence -> PROCEED

dropped TEST_NOTES metadata
```

## 8. Why This Is Not Oracle Reclassification

The frozen Domain 2 oracle remains unchanged.

The oracle may still say:

```text
REPORT_WITH_NOTES
```

This amendment only defines how that Domain 2 oracle action is projected into
the smaller Formal Core V1 action algebra for formal conformance.

Therefore:

```text
Domain 2 oracle action:
REPORT_WITH_NOTES

Formal Core conformance action:
PROCEED

Required preserved reason code:
TEST_NOTES
```

The original Domain 2 result is not rewritten.

## 9. Required Conformance Rerun Scope

If accepted, the next step should be a separate Domain 2 conformance rerun
authorization.

That rerun should verify:

```text
all 38 Domain 2 oracle cases are mapped or rejected explicitly

2 / 2 REPORT_WITH_NOTES cases project to PROCEED with TEST_NOTES preserved

0 TEST_NOTES drops

0 blocking-to-proceed mappings

0 not_evaluated-to-proceed mappings

0 identity drops

Lean/Python formal boundary remains unchanged unless separately authorized
```

## 10. Non-Authorization

This proposal does not authorize:

```text
Lean Action algebra changes

Lean proof script changes

Python typed-evidence boundary changes

Domain 2 adapter changes

oracle changes

corpus changes

Gate A changes

passthrough changes

benchmark changes

new live sessions

Domain 3 conformance

Domain 1 conformance

runtime integration

production claim

release
```

## 11. Proposed Status If Accepted

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

DOMAIN3_NOT_AUTHORIZED

DOMAIN1_NOT_AUTHORIZED

RUNTIME_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```
