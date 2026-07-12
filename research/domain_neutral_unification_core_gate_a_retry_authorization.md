# Gate A Implementation Retry Authorization

## Status

```text
GATE_A_IMPLEMENTATION_RETRY_AUTHORIZED
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_REQUIRED
LEGACY_REGENERATION_AUDIT_REQUIRED
DOMAIN_2_STILL_BLOCKED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Authorization Basis

This retry authorization follows:

```text
research/domain_neutral_unification_core_gate_a_implementation_authorization.md
research/domain_neutral_unification_core_gate_a_implementation_report.md
research/domain_neutral_unification_core_gate_a_regression_methodology.md
```

The previous result remains historically valid:

```text
GATE_A_MIGRATION_REQUIRED
```

That result was produced under the original full-regeneration regression method.
This authorization does not rewrite it, erase it, or convert it into a pass.

This document authorizes a new implementation attempt only under the corrected
Gate A regression methodology.

## Authorized Code Scope

The retry may implement only:

```text
minimal generic proof assembler
legacy Domain 1 wrapper
isolated assembly regression runner
legacy regeneration audit runner
Gate A implementation and audit reports
focused tests required for Gate A
```

The generic assembler must be a proof assembly boundary only. It may accept:

```text
explicit subject {type, sha256}
prevalidated SPIRA_CLAIM_V1 claims
context roots
decision/action object
```

It must not perform domain extraction.

## Forbidden In The Generic Assembler

The generic assembler must not contain:

```text
pytest logic
wheel parsing
Domain 2 claims
cache/status/rerun generalization
new action enum
new claim status
decision-semantics change
producer-specific extraction logic
```

## Isolated Assembly Regression Gate

The isolated regression is the pass/fail gate for Gate A.

Frozen inputs must produce:

```text
1,954 / 1,954 identity matches
```

The comparison must include:

```text
canonical claims identity
claims_merkle_root
frozen context_sha256
canonical decision identity
unification_id
compact reference bytes
stable proof identity
stop
recommended_agent_action
reason_codes
not_evaluated
worst_claim_status
BLOCK semantics
NOT_EVALUATED semantics
```

Any mismatch produces:

```text
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_FAILED
```

and the implementation must stop without merge.

The successful status is:

```text
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_PASS
```

## Legacy Regeneration Audit

The full legacy Domain 1 wheel path must be audited separately.

The audit must report:

```text
claims equivalence
decision equivalence
action equivalence
report-byte drift
context_sha256 drift
unification_id drift
compact-reference drift
proof-identity drift
```

Legacy drift must not be hidden.

Legacy drift must not update the accepted baseline.

Legacy drift does not automatically fail the isolated assembler gate, because
it measures a different question: regenerated evidence-file stability.

## Baseline Rules

The accepted baseline remains immutable:

```text
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json
```

Accepted baseline root:

```text
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

The retry must not:

```text
modify the baseline artifact
modify the baseline root
change canonicalization
remove volatile fields after observing results
lower the 1,954 / 1,954 isolated gate
use legacy drift as an excuse for assembler identity drift
hide legacy drift after it is observed
```

## Still Not Authorized

This retry does not authorize:

```text
Domain 2 producer
Domain 2 corpus
oracle population
pytest adapter
Gate B
Domain 3
release
version bump
tag
PyPI publication
```

Domain 2 remains blocked even if Gate A passes.

## Merge Conditions

Gate A implementation may be merged only if all of the following are true:

```text
isolated regression: 1,954 / 1,954 PASS
focused tests: PASS
full pytest: PASS
legacy drift audit: completed and published
core scope: within this authorization
baseline artifact: unchanged
baseline root: unchanged
```

If any condition fails:

```text
do not merge code
do not update the baseline
do not reclassify a mismatch as a pass
publish a stop report only
```

## Verdict

```text
GATE_A_IMPLEMENTATION_RETRY_AUTHORIZED
GATE_A_ISOLATED_ASSEMBLY_REGRESSION_REQUIRED
LEGACY_REGENERATION_AUDIT_REQUIRED
DOMAIN_2_STILL_BLOCKED
```

This authorization permits a second Gate A implementation attempt under the
corrected regression methodology. It does not authorize Domain 2 or Gate B.
