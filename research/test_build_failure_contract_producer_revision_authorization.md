# Test/Build Failure Contract Producer Revision Authorization

Status:

```text
DOMAIN_2_PRODUCER_REVISION_AUTHORIZED
PRODUCER_REVISION_AUTHORIZATION_ONLY
PRODUCER_SEMANTIC_BEHAVIOR_CHANGE_NOT_AUTHORIZED
GATE_A_REFACTOR_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed implementation:

```text
106cc98 Implement Domain 2 pytest producer
DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS
```

Accepted review:

```text
fb5a7e2 Review Domain 2 producer implementation
DOMAIN_2_PRODUCER_IMPLEMENTATION_NEEDS_REVISION
PRODUCER_IMPLEMENTATION_REVIEW_COMPLETE
```

This document authorizes only a narrow revision of the producer evaluation
harness, focused tests, and implementation report/results needed to close the
two review findings. It does not authorize producer semantic behavior changes,
corpus changes, oracle changes, Schema V7 changes, oracle validator changes,
Gate A refactor, Gate B, Domain 3, or release activity.

## Findings To Close

The revision may address only:

```text
PRODUCER_IDENTITY_FIDELITY_NOT_GATING_PASS
GATE_A_UNCHANGED_CHECK_INSUFFICIENT
```

## Authorized Files

The revision may edit only:

```text
tools/evaluate_test_build_failure_producer.py
tests/test_test_build_failure_producer.py
research/test_build_failure_contract/producer_implementation_report.md
research/test_build_failure_contract/producer_implementation_results.json
```

The revision may add a narrowly scoped helper only if the existing evaluator
cannot invoke the accepted Gate A identity regression without it:

```text
tools/check_gate_a_identity_regression.py
```

If any other file is required, work must stop and a new authorization document
must be committed before making that change.

## Authorized Correction 1: Identity Fidelity Gates

The evaluator must make these explicit pass/fail gates:

```text
scope_identity_fidelity: 38 / 38
result_identity_fidelity: 38 / 38
mismatch_count == 0
```

The machine-readable results and implementation report must include:

```text
scope_identity_fidelity
result_identity_fidelity
mismatch_count
```

The final `DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS` decision must fail if any of
these are not satisfied.

Required negative tests:

```text
scope identity mismatch fails evaluation
result identity mismatch fails evaluation
mismatch_count > 0 fails evaluation
```

These tests may mutate in-memory evaluation inputs. They must not modify the
accepted oracle or corpus files.

## Authorized Correction 2: Gate A Identity Check

The evaluator must replace the current worktree-only check with a stronger
Gate A identity check.

Preferred requirement:

```text
run the accepted Gate A isolated regression
require 1,954 / 1,954 identity matches
require accepted baseline root:
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
```

If invoking the full existing Gate A regression is not practical within this
revision, the evaluator must at minimum verify:

```text
accepted Domain 1 identity baseline root recomputes
accepted baseline root equals:
85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c
source/spira_core/unification_proof.py has no diff from HEAD
research/unification_proof_corpus/results/domain1_identity_baseline_v1.json has no diff from HEAD
```

If the lighter check is used, the report field must not overclaim full
1,954-case regression. It must be named precisely, for example:

```text
gate_a_baseline_root_check: PASS
gate_a_core_worktree_check: PASS
gate_a_identity_regression: NOT_RUN
```

or, if the full regression is run:

```text
gate_a_identity_regression: PASS
```

## Required Re-Run

The revision must rerun:

```text
38-case producer evaluation
Schema V7 validation
accepted oracle validator
focused producer tests
full pytest suite
JSON validation
privacy/path/secret scan
```

The expected success result remains:

```text
DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS
```

but only after the new identity gates and strengthened Gate A check pass.

## Not Authorized

This authorization does not permit:

```text
producer semantic behavior changes
pytest extraction behavior changes
corpus modification
oracle modification
Schema V7 modification
oracle validator modification
Gate A refactor
Gate A rebaseline
Gate B status/cache/rerun work
new action values
new claim status values
decision semantics version change
Domain 3 work
release/version/tag/PyPI publication
```

If closing the findings requires changing producer semantics rather than the
evaluator gates and report, the required result is:

```text
PRODUCER_REVISION_AUTHORIZATION_REVISION_REQUIRED
```

## Stop Conditions

The revision must stop if any of the following occur:

```text
accepted corpus changes
accepted oracle changes
Schema V7 changes
accepted validator changes
producer semantic output changes
Gate A baseline root mismatch
Gate A core diff appears
scope identity fidelity < 38 / 38
result identity fidelity < 38 / 38
mismatch_count != 0
false PROCEED appears
focused producer tests fail
full pytest fails
```

Stop statuses:

```text
DOMAIN_2_PRODUCER_REVISION_FAILED
DOMAIN_2_PRODUCER_REVISION_INCOMPLETE
PRODUCER_REVISION_AUTHORIZATION_REVISION_REQUIRED
```

## Completion Statuses

The revision must end in exactly one of:

```text
DOMAIN_2_PRODUCER_REVISION_COMPLETE
DOMAIN_2_PRODUCER_REVISION_FAILED
DOMAIN_2_PRODUCER_REVISION_INCOMPLETE
PRODUCER_REVISION_AUTHORIZATION_REVISION_REQUIRED
```

`DOMAIN_2_PRODUCER_REVISION_COMPLETE` is not final implementation acceptance.
After revision, a separate final implementation review is required before the
producer can be accepted.

## Final Authorization

```text
DOMAIN_2_PRODUCER_REVISION_AUTHORIZED
PRODUCER_REVISION_AUTHORIZATION_ONLY
PRODUCER_SEMANTIC_BEHAVIOR_CHANGE_NOT_AUTHORIZED
GATE_A_REFACTOR_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```
