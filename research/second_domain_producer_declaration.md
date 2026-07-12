# SPIRA Second Domain Producer Declaration

## Status

```text
DECLARATION_LOCKED_BEFORE_SECOND_DOMAIN_METHODOLOGY
```

This document records the next research direction after the successful
Unification Proof V1 corpus validation in the Python wheel evidence domain.

It does not authorize implementation.

The next authorized artifact is a methodology document for one second-domain
producer experiment, including an oracle schema and predeclared validity gates.

## Current Baseline

SPIRA has already demonstrated the following in the Python wheel domain:

```text
artifact evidence
-> deterministic verification
-> combined verdict
-> agent action contract
-> typed claims
-> claims_merkle_root
-> unification_id
-> compact action reference
```

The frozen 1,954-wheel corpus result closed with:

```text
UNIFICATION_CORPUS_PASS
```

That validates the unification core for one real domain. It does not validate a
new domain producer, a broad orchestrator, or a universal Context Firewall.

## Candidate Domain 2

The next candidate is:

```text
Test/Build Failure Contract
```

This is not a general CI-log summarizer.

The experiment may only target closed, deterministic questions such as:

```text
did the test/build pass?
which test or build step failed?
what failure class was observed?
where was the failure located?
what rerun command reproduces the failure?
is the failure new or previously observed?
```

Full logs, tracebacks, and raw build output remain local drill-down evidence.

## Frozen Core Action Enum

The second-domain producer must not extend the core agent-action enum.

Test and build failures must map through the existing blocking action:

```json
{
  "stop": true,
  "recommended_agent_action": "STOP_BLOCKED",
  "reason_codes": [
    "TEST_FAILURE"
  ]
}
```

The core action expresses the agent-level command. Domain-specific meaning is
carried by typed claims and `reason_codes`.

If the Test/Build domain discovers a state that cannot be represented by the
existing action enum, the result is:

```text
CORE_CHANGE_REQUIRED
```

It must be reported as an architectural finding, not bypassed by introducing a
domain-specific action in the methodology or fixtures.

## Strict-List Invariant

The Test/Build producer must preserve explicit lists when the compact contract
claims a count.

This imports the lesson from the Codex Arm C `not_evaluated` regression: a
compact contract that says "there are two items" but cannot identify both items
is not sufficient for action-preserving reporting.

Required invariant:

```text
count fields are derived only from explicit sorted unique lists
count == len(list)
```

Contract violation example:

```json
{
  "failed_test_count": 2,
  "failed_tests": [
    "tests/test_alpha.py::test_one"
  ]
}
```

The example above is invalid because the count says two but the contract
contains only one explicit test identity.

The methodology must define all strict lists needed by the oracle, including
the exact identity fields for failed tests, failed build steps, skipped
required checks, not-evaluated checks, and drill-down references.

## Codex Benchmark Errata Boundary

The methodology and any future report must preserve the public Codex benchmark
history accurately.

It must not imply that the original repeated-cache run was clean.

The correct historical sequence is:

```text
original Arm D:
NOT_EVALUATED_PROTOCOL_IMPLEMENTATION_MISMATCH

true resume added:
valid second turn, but initial interpretation treated cumulative usage as
per-turn usage

canonical correction:
turn 2 usage = second cumulative usage - first cumulative usage
```

Canonical conclusion:

```text
repeated exact-context reuse showed a modest 11.8%-14.0% live input-token
reduction, below the predeclared 20% threshold; no repeated-cache live-token
efficiency claim is supported
```

Future second-domain measurements may cite the benchmark only with that
erratum intact.

## Domain 3 Gate

No third domain may be selected until Domain 2 has passed an independent
methodology and measurement.

Domain 3 discussion requires all five gates:

```text
1. Domain 2 producer methodology was locked before implementation.
2. Domain 2 produced measured compact outputs, not modeled placeholders.
3. Domain 2 passed oracle fidelity and strict-list gates.
4. Domain 2 showed value beyond the existing Python-wheel producer.
5. A specific architectural doubt remains that only a third domain can answer.
```

Desire to expand coverage or demonstrate momentum is not architectural doubt.

If those gates are not met, the status remains:

```text
DOMAIN_3_NOT_AUTHORIZED
```

## Methodology Requirements For Domain 2

The next document must be:

```text
research/test_build_failure_contract_methodology.md
```

It must be locked before implementation and include at least:

```text
scope boundary
event/corpus selection
oracle schema
allowed claim types
allowed action mapping using the frozen core enum
strict-list invariants
fixture set
fidelity gates
sufficiency gates
drill-down accounting
not_claimed block
authorization decision after measurement
```

The oracle schema must define the exact expected answer shape before any
producer output is observed.

## Not Authorized

This declaration does not authorize:

```text
producer implementation
core action enum expansion
new SPIRA Trust release claim
third domain
multi-producer orchestrator
SPIRA OS
universal Context Firewall claim
token, CPU, energy, or CO2 claim
```

## Status Chain

```text
declaration -> methodology required -> implementation not yet authorized
```

The next step is methodology, not code.
