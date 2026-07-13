# SPIRA Domain 3 — Terraform Plan Evidence Research Declaration

## Status

```text
DOMAIN_3_TERRAFORM_PLAN_RESEARCH_AUTHORIZED
PRODUCTIZATION_BRIDGE_RESEARCH
TERRAFORM_PLAN_JSON_SELECTED
IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_4_NOT_AUTHORIZED
MVP_NOT_YET_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

This document authorizes a bounded third-domain research program for SPIRA.

The research question is:

```text
Can the accepted SPIRA unification architecture process a frozen,
non-Python Infrastructure-as-Code evidence format through a domain-specific
producer, while preserving the accepted shared assembly boundary and
producing oracle-equivalent typed claims and bounded actions?
```

The selected evidence format is:

```text
Terraform Plan JSON
```

Domain 3 is a productization-bridge experiment.

Its purpose is to test whether the accepted multi-domain architecture can cross
from Python-related evidence into a structured, declarative, non-Python
ecosystem before an MVP product boundary is proposed.

It is not an authorization to build a general infrastructure-governance
platform, infrastructure security scanner, policy engine, orchestrator, or
live-state monitoring system.

---

## Relationship to the Completed Multi-Domain Research

The prior research program remains complete and valid:

```text
MULTIDOMAIN_UNIFICATION_RESEARCH_COMPLETE_WITH_BOUNDS
```

That conclusion is not reopened or weakened by Domain 3.

The accepted prior result remains:

```text
Domain 1:
Python wheel artifact evidence validated on a frozen 1,954-wheel corpus

Gate A:
generic proof-assembly boundary accepted
Domain 1 identity preserved 1,954 / 1,954

Domain 2:
Python pytest evidence validated against a frozen corpus,
an accepted independent expected-answer oracle,
and an accepted producer
```

Domain 3 is a new project decision made after the completion of the prior
research.

It is opened because the project now wishes to test a specific unresolved
productization question:

```text
Does the accepted shared assembly boundary remain useful when the producer
operates on frozen, declarative, non-Python Infrastructure-as-Code evidence?
```

Domain 3 is not opened because Domains 1 and 2 were insufficient.

---

## Selected Evidence

The authorized Domain 3 evidence is:

```text
Terraform Plan JSON produced from a saved Terraform plan
```

A Terraform plan JSON document is treated as:

```text
a pinned, structured evidence snapshot
```

It is not treated as universally reproducible output.

A plan is produced from configuration, prior state, provider behavior,
variables, execution context, and potentially refreshed remote state.

Two plan generations may therefore produce different bytes or different
content.

The subject of verification is the exact frozen JSON document that was
provided and pinned by SHA-256.

Required subject form:

```text
subject.type:
terraform_plan

subject.sha256:
SHA256(exact frozen Terraform Plan JSON bytes)
```

The proof binds only what is explicitly present and supplied.

---

## Snapshot and Epoch Boundary

A Terraform plan file is a pinned evidence snapshot.

Infrastructure, configuration, prior state, providers, variables, remote
objects, permissions, or execution context may change after the plan is
generated.

Domain 3 does not evaluate cross-time validity.

The following remain outside Domain 3:

```text
verdict staleness
cross-run reuse
epoch validity
live infrastructure comparison
automatic refresh
semantic cache reuse
cross-time state reconciliation
```

These questions remain associated with the existing open Gate B epoch doubt.

Domain 3 does not reopen, solve, or rename that doubt.

```text
Gate B:
NOT_AUTHORIZED
```

---

## Why Terraform Plan JSON Was Selected

Terraform Plan JSON was selected because it provides:

```text
structured declarative evidence
explicit resource-change objects
explicit create/update/delete/read/no-op actions
replace action sequences
replace paths
unknown-value structure
sensitive-value structure
plan completion and applicability fields
format and Terraform version information
```

It enables a frozen oracle to define expected facts and decisions without
creating or modifying live infrastructure.

It is sufficiently different from Python wheel metadata and pytest evidence to
test the intended foreign-ecosystem boundary.

It does not require a live cluster or a continuously changing control plane.

---

## Kubernetes Exclusion

Kubernetes manifests and live cluster state are not authorized for Domain 3.

Static Kubernetes YAML generally describes desired state.

Meaningful operational conclusions often require comparison against:

```text
live cluster state
controller state
events
permissions
telemetry
time-sensitive observations
```

Introducing those sources would add the time and live-state dimensions that
Domain 3 intentionally excludes.

```text
KUBERNETES_LIVE_STATE_EXCLUDED
```

This exclusion is methodological, not a statement that Kubernetes evidence is
unimportant.

---

## Authorized Architectural Hypothesis

The Domain 3 hypothesis is:

```text
A Terraform-specific deterministic producer can extract typed factual claims
from a frozen Terraform Plan JSON document, and those claims can pass through
the accepted Gate A proof-assembly boundary without changing the shared core.
```

Intended flow:

```text
frozen Terraform Plan JSON
→ Terraform evidence producer
→ typed factual claims
→ existing Gate A assembly boundary
→ policy-bound action
→ contextual unification_id
→ proof and drill-down references
```

The shared assembly boundary must remain unchanged.

Domain-specific extraction belongs in the producer.

Terraform-specific parsing or semantics must not be added to the generic core.

---

## Authorized Claim Boundary

A future Domain 3 producer may extract factual claims about:

```text
plan format version
Terraform version
applyable state
complete state
errored state
resource addresses
resource types
resource action sequences
create resources
update resources
delete resources
replace resources
read resources
no-op resources
replace paths
unknown-value paths
sensitive paths present
explicit resource-change lists
counts derived from explicit sorted unique lists
availability of optional generation provenance
```

The producer may state only what the frozen evidence supports.

It may not claim:

```text
that the infrastructure design is correct
that the infrastructure is secure
that a resource change is operationally safe
that a replacement is acceptable
that an apply will succeed
that the plan is cost-efficient
that the plan is compliant
that a deletion is desirable or undesirable
that the plan reflects current live infrastructure
that an unknown value is harmless
that all sensitive values were protected outside the supplied evidence
```

Domain 3 tests semantic extraction from the Terraform evidence format.

It does not test infrastructure-risk understanding.

---

## Policy Boundary

A future frozen oracle may use a narrow research policy solely to prove the
pipeline:

```text
facts
→ policy
→ bounded action
```

For example, a research policy may block a delete or replace operation for a
resource type listed in a frozen policy fixture.

Such a policy demonstrates deterministic policy application only.

It does not establish:

```text
general infrastructure policy correctness
security expertise
compliance expertise
cost expertise
production deployment judgment
```

The Domain 3 methodology must keep extracted facts separate from
policy-derived decisions.

---

## Plan Applicability Boundary

`applyable == false` must not be interpreted as an automatic blocking finding.

The future methodology must distinguish at least:

```text
errored == true
→ blocking plan error

errored == false
+ complete plan
+ effective change list empty
→ valid no-change result
→ not automatically blocked

effective changes present
+ applyable == false
→ blocking or non-continuation result under the frozen decision table
```

A no-change plan is not a false-block condition merely because there is nothing
to apply.

The corpus and oracle must contain distinct cases that prove this difference.

---

## Optional Generation Provenance

The following evidence may be available:

```text
configuration hash
prior-state hash
provider-lockfile hash
variables-manifest hash
generation-command fingerprint
workspace or fixture identity
```

Each item must carry an explicit state:

```text
BOUND
NOT_PROVIDED
NOT_APPLICABLE
```

Missing optional generation provenance must not be guessed.

It must not be represented by an empty hash.

A valid proof may still be produced for the exact frozen plan JSON when
optional generation context is unavailable.

In that case, the proof means:

```text
This decision is bound to these exact Terraform Plan JSON bytes.
```

It does not mean:

```text
This decision is also bound to the configuration, state, variables, providers,
or workspace that generated the plan.
```

The proof binds what is present.

It does not imply what was not provided.

---

## Sensitive-Value Doctrine

Terraform plan evidence may contain sensitive values.

Domain 3 must use synthetic evidence or reviewed public fixtures only.

Production or private live-environment plans are not authorized for the
research corpus.

A future producer must never:

```text
copy sensitive values into claims
log sensitive values
quote sensitive values
hash sensitive values as claim values
publish sensitive values
expose sensitive values through evidence pointers
use sensitive values as model instructions
```

The producer may inspect the structural sensitive masks required to determine
that a sensitive path exists.

Permitted structural claim:

```text
SENSITIVE_PATH_PRESENT
status: NOT_EVALUATED
```

The claim may identify a safe normalized structural path only when that path
does not itself disclose the sensitive value.

The value must remain unread and unavailable in public research output.

A sensitive-value leak into a public claim, proof, report, corpus artifact, or
log is a hard stop condition.

---

## Unknown-Value Doctrine

Terraform may mark values as unknown until apply.

An unknown value is:

```text
not malformed evidence
not a conflict
not a known value
```

A future producer must preserve it explicitly as an unknown planned value.

Possible claim:

```text
PLANNED_VALUE_UNKNOWN
status: NOT_EVALUATED
```

The producer must not:

```text
guess the value
replace it with null and treat it as known
infer safety from its absence
treat unknown as malformed by default
```

---

## Evidence Is Not Instruction

All values inside the plan are evidence content.

They are never instructions to SPIRA, the producer, the oracle author, or an
agent.

The Domain 3 corpus must include adversarial values such as:

```text
"PROCEED"
"IGNORE PREVIOUS FINDINGS"
"ALL RESOURCES ARE SAFE"
fabricated SPIRA claim JSON
instruction-like text in tags
instruction-like text in descriptions
instruction-like output values
```

Such text must not override:

```text
plan structure
resource actions
policy
typed claims
decision semantics
oracle answers
```

---

## Identity Boundary

Domain 3 V1 uses the existing contextual identity:

```text
run_identity:
existing unification_id
```

No semantic `result_identity` is authorized for Domain 3 V1.

The exact frozen Terraform Plan JSON bytes and bound context define the
contextual subject.

The research does not assume that regenerated plans will produce the same
identity.

If future evidence demonstrates that regeneration instability creates a
separate semantic-identity requirement, that finding must be documented and
reviewed separately.

It must not silently change the meaning of `unification_id`.

It must not automatically open Gate B.

---

## Semantic Extraction Requirement

Domain 3 must prove extraction of Terraform action semantics, not only resource
counts.

The future mutation matrix must include cases such as:

```text
update
→ replace delete/create

replace delete/create
→ replace create/delete

same replace action
→ different replace_paths

same resource address and counts
→ different action sequence

same action sequence
→ different unknown-value paths
```

Required expectation:

```text
semantic action mutation
→ typed claims change
→ claims root changes
→ contextual unification identity changes
```

A mutation that only reorders equivalent `resource_changes` must not alter the
canonical claim set or claims root.

This demonstrates semantic extraction beyond count matching.

It does not demonstrate infrastructure-risk understanding.

---

## Format-Version Boundary

Domain 3 must recognize the Terraform Plan JSON format version.

A future methodology must define:

```text
supported major version
supported minor-version behavior
unknown-field handling
unsupported-major fail-closed behavior
```

Unsupported major versions must not be guessed into the supported format.

Permitted result:

```text
REPORT_NOT_EVALUATED
TERRAFORM_PLAN_FORMAT_UNSUPPORTED
```

Forward-compatible minor fields may be ignored only under a locked methodology
that preserves known semantics and records what was not evaluated.

---

## Research Sequence

The required sequence is:

```text
1. Domain 3 research declaration
2. Declaration review and acceptance
3. Terraform Plan evidence methodology
4. Methodology review and acceptance
5. Corpus authorization
6. Corpus materialization and review
7. Oracle schema and validator path
8. Oracle population and review
9. Producer authorization
10. Producer implementation and evaluation
11. Domain 3 closeout
12. MVP product-boundary proposal
```

Completion of one step does not authorize the next unless a separate committed
authorization explicitly says so.

---

## Authorized Work

This declaration authorizes:

```text
Domain 3 declaration
declaration review
Terraform Plan evidence methodology drafting
methodology review
```

It does not authorize:

```text
Terraform producer implementation
Terraform parser or adapter code
Terraform corpus materialization
Terraform oracle population
changes to Gate A
Gate B
semantic cache reuse
Kubernetes work
Domain 4
MVP implementation
release
version bump
tag
PyPI publication
```

---

## Success Criteria

Domain 3 is successful only if a future accepted producer:

```text
passes its frozen accepted corpus
matches its independent accepted oracle
preserves strict explicit lists
preserves NOT_EVALUATED and blocking semantics
produces valid evidence pointers
detects sensitive paths without exposing values
preserves unknown-value semantics
distinguishes no-change from non-applyable planned changes
detects action-sequence and replace-path mutations
uses the accepted shared Gate A assembly boundary unchanged
introduces no Terraform logic into the generic core
produces zero false PROCEED decisions under the frozen decision contract
```

All exact thresholds must be locked in the methodology before producer
implementation.

---

## Negative Result

A negative result is valid research output.

Domain 3 must stop if:

```text
a reliable oracle cannot be authored
sensitive values cannot be protected
Terraform semantics cannot be extracted deterministically
strict lists cannot be preserved
unknown and sensitive structures cannot be represented fail-closed
the accepted Gate A boundary requires an unapproved change
false PROCEED cannot be eliminated
the producer merely reformats the plan without extracting sufficient facts
```

A negative result must not be rescued by:

```text
changing the corpus after results
weakening the oracle
changing thresholds
adding a new action enum
changing unification_id semantics
opening Gate B
switching to Kubernetes
creating Domain 4
claiming infrastructure-risk understanding
```

---

## Domain 3 Completion Criterion

Domain 3 is complete when:

```text
the Terraform Plan producer passes its frozen accepted corpus
and independent accepted oracle under the locked acceptance gates,
while the accepted shared Gate A assembly boundary remains unchanged.
```

A positive result closes the defined foreign-ecosystem doubt within the tested
Terraform Plan evidence boundary.

A negative result is recorded and accepted.

Neither result authorizes Domain 4.

```text
DOMAIN_4_NOT_AUTHORIZED
```

The open epoch and staleness doubt routes to Gate B.

It must not be converted into another evidence domain.

```text
EPOCH_DOUBT_ROUTES_TO_GATE_B
```

---

## Post-Closeout Direction

Upon Domain 3 closeout, the next authorized artifact is:

```text
MVP product-boundary proposal
```

The next artifact is not:

```text
Domain 4 declaration
another producer
Gate B implementation
orchestrator
release
```

Domain 3 is a bridge to an explicit product decision.

It must not become an indefinite research sequence used to postpone
productization.

---

## Final Declaration

```text
Prior two-domain research:
COMPLETE AND UNCHANGED

Domain 3:
DOMAIN_3_TERRAFORM_PLAN_RESEARCH_AUTHORIZED

Research role:
PRODUCTIZATION_BRIDGE_RESEARCH

Selected evidence:
FROZEN_TERRAFORM_PLAN_JSON

Kubernetes live state:
EXCLUDED

Implementation:
NOT_AUTHORIZED

Gate B:
NOT_AUTHORIZED

Domain 4:
NOT_AUTHORIZED

MVP:
NOT_YET_AUTHORIZED

Release/version/tag/PyPI:
NOT_AUTHORIZED

Next required artifact:
DOMAIN_3_DECLARATION_REVIEW
```

## Governing Principle

```text
Bind the exact frozen plan.

Extract facts, not infrastructure opinions.

Treat sensitive values as unavailable.

Preserve unknowns explicitly.

Do not confuse no changes with failure.

Do not confuse semantic extraction with risk understanding.

Keep time and reuse inside Gate B.

Close Domain 3 before proposing the MVP.

Do not open Domain 4 to avoid a product decision.
```
