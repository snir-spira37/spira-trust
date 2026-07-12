# Gate A Regression Methodology

## Status

```text
GATE_A_REGRESSION_METHOD_ACCEPTED
GATE_A_IMPLEMENTATION_PAUSED
CORE_CODE_UNCHANGED
DOMAIN_2_STILL_BLOCKED
GATE_B_NOT_AUTHORIZED
```

## Background

The first Gate A implementation attempt stopped with:

```text
GATE_A_IMPLEMENTATION_STOPPED
GATE_A_DOMAIN1_IDENTITY_REGRESSION_NOT_PASSED
GATE_A_MIGRATION_REQUIRED
```

That result is preserved in:

```text
research/domain_neutral_unification_core_gate_a_implementation_report.md
```

The smoke regression showed:

```text
claims: stable
decision/action: stable
context_sha256: changed
unification_id: changed
compact reference identity: changed
stable proof identity: changed
```

The context change was traced to legacy Domain 1 context construction that binds:

```text
decision_sha256
graph_report_sha256
command_fingerprint
```

Regenerating evidence files can therefore change `context_sha256` even when the
typed claims and action decision remain stable.

## Methodology Decision

Gate A regression must be split into two separate checks:

```text
1. Gate A isolated assembly regression
2. Legacy end-to-end regeneration audit
```

These checks answer different questions and must not be collapsed into one
verdict.

## Gate A Isolated Assembly Regression

This is the required pass/fail gate for Gate A implementation.

It tests only the authorized Gate A change:

```text
Does the generic proof assembly boundary preserve identity when given the exact
same subject, claims, context, and decision inputs?
```

Inputs must be derived from the accepted Domain 1 baseline:

```text
accepted subject
accepted claims
accepted decision
accepted context_sha256
accepted policy/context roots
accepted action fields
```

The implementation must compare:

```text
claims_merkle_root
unification_id
compact reference bytes
stable proof identity
stop
recommended_agent_action
reason_codes
not_evaluated
worst_claim_status
```

Success requires:

```text
1,954 / 1,954 isolated identity matches
```

The successful final status is:

```text
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_PASS
```

Any mismatch produces:

```text
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_FAIL
```

and Gate A implementation must stop.

## Legacy End-To-End Regeneration Audit

This audit is required, but it is not the Gate A assembler pass/fail criterion.

It measures the stability of the existing Domain 1 evidence regeneration path:

```text
wheel bytes
-> graph/trust execution
-> report bytes
-> decision bytes
-> agent summary
-> unification proof
```

It must report:

```text
claims equivalence
decision equivalence
action equivalence
decision report byte drift
graph report byte drift
context_sha256 drift
unification_id drift
compact reference drift
stable proof identity drift
```

The audit may produce drift without failing the isolated Gate A assembler
regression, because it includes legacy report-byte reproducibility.

The audit result must be public in the Gate A implementation report.

## Baseline Rules

The accepted baseline remains immutable:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

Accepted baseline root:

```text
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

The implementation must not:

```text
update the baseline to fit new output
change canonicalization after observing results
remove volatile fields after observing results
lower the 1,954 / 1,954 isolated gate
hide end-to-end drift
describe legacy regeneration drift as a Gate A assembler failure
describe assembler identity drift as harmless legacy drift
```

## Historical Result Preservation

The previous result under the original regression method remains valid:

```text
GATE_A_MIGRATION_REQUIRED
```

It must not be rewritten as a pass.

The new methodology does not erase that result. It explains that the original
method mixed two questions:

```text
Gate A assembly behavior
legacy evidence-file reproducibility
```

## Re-Authorization Requirement

This methodology does not resume implementation by itself.

Before another Gate A implementation attempt begins, a separate authorization
must explicitly reference this methodology and state:

```text
GATE_A_IMPLEMENTATION_RETRY_AUTHORIZED
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_REQUIRED
LEGACY_REGENERATION_AUDIT_REQUIRED
DOMAIN_2_STILL_BLOCKED
```

Until that authorization exists:

```text
no Gate A code
no core refactor
no Domain 2 producer
no oracle population
no Gate B work
```

## Verdict

```text
GATE_A_REGRESSION_METHOD_ACCEPTED
```

Gate A must be judged by isolated assembly identity preservation over frozen
inputs, while legacy end-to-end regeneration drift is measured and reported
separately.
