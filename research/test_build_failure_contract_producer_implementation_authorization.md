# Test/Build Failure Contract Producer Implementation Authorization

Status:

```text
DOMAIN_2_PRODUCER_IMPLEMENTATION_AUTHORIZED
PRODUCER_IMPLEMENTATION_AUTHORIZATION_ONLY
PYTEST_ADAPTER_AUTHORIZED_WITHIN_PRODUCER_SCOPE
GATE_A_FROZEN
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

This document authorizes a narrow implementation of the Domain 2 pytest
evidence producer against the accepted 38-case corpus and accepted oracle. It
does not authorize corpus, oracle, schema, validator, Gate A, Gate B, Domain 3,
or release changes.

## Accepted Inputs

The producer must be evaluated only against the frozen and accepted Domain 2
materials:

```text
Corpus:
research/test_build_failure_contract/corpus_manifest_v1.json

Oracle:
research/test_build_failure_contract/oracle_v1.json

Oracle acceptance:
research/test_build_failure_contract_oracle_final_review.md

Schema:
research/test_build_failure_contract_oracle_schema_v7.schema.json

Validator:
source/spira_core/test_build_failure_oracle_validator.py
```

Accepted status chain:

```text
Dual Identity Model V2: ACCEPTED
Oracle Schema V7: ACCEPTED
Oracle Validator: ACCEPTED
Domain 2 corpus: ACCEPTED
Domain 2 oracle: ACCEPTED
```

## Authorized Scope

Authorized implementation:

```text
pytest evidence producer only
pytest evidence adapter only as needed by this producer
extraction of Domain 2 typed claims
scope_identity computation
result_identity computation
evidence locators
producer-focused tests
corpus-vs-oracle evaluation runner
machine-readable producer report/results
```

The producer may read:

```text
frozen corpus sources
public_run_materialization records
accepted oracle expected answers
accepted Schema V7
accepted oracle validator
```

The producer may emit:

```text
typed pytest/test-build claims
scope identity projection and hash
result identity projection and hash or NOT_EVALUATED
policy/action binding through the existing action contract
explicit blocking/nonblocking lists
evidence locators
machine-readable evaluation results
implementation report
```

## Frozen Boundaries

The following are frozen and must not be modified:

```text
Domain 2 corpus
Domain 2 oracle
Oracle Schema V7
accepted oracle validator
Gate A generic unification interface
Gate A Domain 1 identity baseline
SPIRA_DECISION_SEMANTICS_V2
action enum
claim status enum
Gate B status/cache/rerun behavior
```

Gate A may be called through its accepted interface, but it must not be
refactored, migrated, or re-baselined as part of this producer work.

## Required Acceptance Gates

The implementation can be accepted only if all gates pass:

```text
38 / 38 oracle claim fidelity
38 / 38 action equivalence
0 false PROCEED
100% strict-list fidelity
100% evidence-pointer validity
identity relationships preserved
NOT_EVALUATED semantics preserved
BLOCK semantics preserved
Schema V7: PASS
accepted validator: PASS
focused producer tests: PASS
full pytest suite: PASS
Gate A identity unchanged
producer_output_observed only during producer evaluation, not oracle authoring
```

Claim fidelity means the producer output matches the accepted oracle for all
expected typed claims that the oracle declares for each case.

Action equivalence means the producer preserves:

```text
stop
recommended_agent_action
reason_codes
decision_semantics_version
```

Strict-list fidelity means count-like facts must derive from explicit sorted
unique lists. A count without the exact list is a failure.

Evidence-pointer validity means every emitted claim and decision fact must
point to a committed corpus source, materialized public-run record, or accepted
withheld-output hash as applicable.

Identity relationship preservation means all six declared mutation pairs must
match the accepted oracle relationships for:

```text
run_identity_relation
scope_identity_relation
result_identity_relation
declared_input_deltas
```

## False Proceed Rule

Any case where the accepted oracle requires:

```text
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
REPORT_WITH_NOTES
```

but the producer emits:

```text
PROCEED
```

is a false proceed.

Allowed false proceeds:

```text
0
```

Any false proceed stops the implementation and requires:

```text
DOMAIN_2_PRODUCER_IMPLEMENTATION_FAILED
```

or a narrower review finding if the producer output is not merged.

## Public Withheld Evidence Rule

For public cases where raw console/JUnit outputs are withheld and only hashes
are committed, the producer must not infer semantic result identities from case
names or exit codes alone.

Required behavior:

```text
result_identity: NOT_EVALUATED
recommended_agent_action: REPORT_NOT_EVALUATED
reason_codes include PUBLIC_RUN_OUTPUT_WITHHELD
```

unless a future separately authorized corpus revision commits sufficient raw
evidence or canonical projection bytes.

No such corpus revision is authorized here.

## Conflict Rule

Console/JUnit contradiction must remain fail-closed:

```text
recommended_agent_action: RERUN_REQUIRED
reason_codes: ["TEST_EVIDENCE_CONFLICT"]
result_identity: NOT_EVALUATED
```

It must not be treated as an ordinary:

```text
STOP_BLOCKED + TEST_FAILURE
```

## Not Authorized

This authorization does not permit:

```text
corpus modification
oracle modification
Schema V7 modification
validator modification
Gate A refactor
Gate A identity migration
Gate B status/cache/rerun work
new action values
new claim status values
decision semantics version change
Domain 3 work
release/version/tag/PyPI publication
```

It also does not permit changing the accepted oracle to match producer output.
The producer must be judged against the accepted oracle, not the reverse.

## Stop Conditions

Implementation must stop if any of the following occur:

```text
corpus case count changes
oracle expected answer changes
schema or validator changes are required
Gate A identity changes
any false PROCEED appears
claim fidelity < 38 / 38
action equivalence < 38 / 38
strict-list fidelity < 100%
evidence-pointer validity < 100%
identity relationship mismatch
NOT_EVALUATED semantics dropped
BLOCK semantics dropped
full pytest fails
producer needs Gate B behavior
producer requires a new action or claim status
```

Stop statuses:

```text
DOMAIN_2_PRODUCER_IMPLEMENTATION_FAILED
DOMAIN_2_PRODUCER_IMPLEMENTATION_INCOMPLETE
PRODUCER_AUTHORIZATION_REVISION_REQUIRED
CORE_CHANGE_REQUIRED
```

## Required Implementation Report

The implementation must publish a report and machine-readable results covering:

```text
producer implementation commit
files changed
authorized scope check
case count
claim fidelity count
action equivalence count
false PROCEED count
strict-list fidelity count
evidence-pointer validity count
identity relationship preservation
NOT_EVALUATED preservation
BLOCK preservation
Schema V7 result
accepted validator result
focused producer test result
full pytest result
Gate A identity check result
not authorized boundaries
```

Allowed success status:

```text
DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS
```

`DOMAIN_2_PRODUCER_IMPLEMENTATION_PASS` does not authorize Gate B, Domain 3, a
release, a version bump, a tag, or PyPI publication.

## Final Authorization

```text
DOMAIN_2_PRODUCER_IMPLEMENTATION_AUTHORIZED
PRODUCER_IMPLEMENTATION_AUTHORIZATION_ONLY
PYTEST_ADAPTER_AUTHORIZED_WITHIN_PRODUCER_SCOPE
GATE_A_FROZEN
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```
