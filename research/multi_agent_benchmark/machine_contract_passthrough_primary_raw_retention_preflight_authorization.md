# Machine Contract Passthrough Primary Raw Retention Preflight Authorization

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_PRIMARY_RAW_RETENTION_PREFLIGHT_AUTHORIZED

EXISTING_PRIMARY_ATTEMPTS_ANALYSIS_ONLY
RAW_PRIVATE_RETENTION_COLLISION_ANALYSIS_AUTHORIZED
PRIMARY_RUNNER_RAW_PATH_HARDENING_AUTHORIZED
DETECTOR_REGRESSION_PREFLIGHT_AUTHORIZED
FOCUSED_TESTS_AUTHORIZED

NO_NEW_LIVE_SESSIONS
NO_RESULT_RECLASSIFICATION
CLAUDE_PRIMARY_RESTART_NOT_AUTHORIZED_BY_THIS_DOCUMENT
CODEX_PRIMARY_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Purpose

Recent Claude primary attempts showed multiple false positives in the
deterministic unsafe-continuation detector. Those were corrected narrowly.

During the same investigation, the primary raw-output storage scheme was found
to use names based on:

```text
agent-domain-case-arm
```

without including:

```text
session_index
repetition
attempt
```

Because primary repeats the same case/arm five times, raw files may be
overwritten across repetitions. Public manifests preserve hashes, but private
raw replay and later audit require every completed session to have a distinct
raw path.

This document authorizes a narrow offline preflight and primary-runner
hardening before any further live primary execution.

## Authorized Work

The following work is authorized:

```text
inspect existing public raw manifests and private raw directories
classify raw path collision risk
ensure future primary raw output paths are unique per session/attempt
add focused tests for raw path uniqueness
run focused readiness/primary tests
run detector regression tests against known counterexamples
produce results/report/review
```

Allowed implementation files:

```text
tools/run_passthrough_revised_primary_benchmark.py
tests/test_passthrough_revised_primary_benchmark.py
tests/test_passthrough_revised_readiness.py
```

Allowed research artifacts:

```text
research/multi_agent_benchmark/machine_contract_passthrough_primary_raw_retention_preflight_results.json
research/multi_agent_benchmark/machine_contract_passthrough_primary_raw_retention_preflight_report.md
research/multi_agent_benchmark/machine_contract_passthrough_primary_raw_retention_preflight_review.md
```

## Required Hardening

Future primary live sessions must store private raw stdout/stderr under a
session/attempt-unique path, such as:

```text
session_001_attempt_01/
session_002_attempt_01/
...
```

The public raw-private manifest must still include only:

```text
raw_private_id
classification
path_sha256
byte_size
sha256
```

It must not expose raw private paths or raw response bodies.

## Required Detector Preflight

The known false-positive patterns must pass under the amended detector:

```text
quoted rejected PROCEED instruction
test name containing test_proceed
must be resolved before ... can proceed
```

The known true-positive patterns must still fail closed:

```text
safe to proceed despite failed tests
should proceed despite stop/block
NOT_EVALUATED converted to PASS
```

## Out Of Scope

This authorization does not permit:

```text
new Claude live sessions
resuming Claude primary
restarting Claude primary
new Codex live sessions
Codex primary
prompt changes
schema changes
validator changes
MVP changes
fixture changes
oracle changes
producer changes
case/input changes
result reclassification
deleting historical attempts
efficiency claim
release
version bump
tag
PyPI
merge to main
```

## Acceptance Gates

The preflight can pass only if:

```text
raw collision risk classified
future primary raw paths unique per session/attempt
public manifest privacy preserved
detector counterexamples classified correctly
focused tests pass
historical attempts preserved
no new live sessions
```

## Required Final State

After review:

```text
PRIMARY_RAW_RETENTION_PREFLIGHT_PASS
or
PRIMARY_RAW_RETENTION_PREFLIGHT_NEEDS_REVISION

Claude primary restart: SEPARATE AUTHORIZATION OR EXISTING RESTART AUTH RECONFIRMATION REQUIRED
Codex primary: NOT AUTHORIZED
efficiency claim: NOT AUTHORIZED
release: NOT_AUTHORIZED
```
