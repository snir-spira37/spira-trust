# Machine Contract Passthrough Primary Raw Retention Preflight Report

## Summary

```text
status: MACHINE_CONTRACT_PASSTHROUGH_PRIMARY_RAW_RETENTION_PREFLIGHT_PASS
new live sessions: 0
historical results reclassified: false
focused tests: 35 passed
```

## Raw Retention Finding

The existing Claude primary raw-private manifest from the latest historical
attempt contains:

```text
raw entries: 120
unique path hashes: 72
path collision groups: 48
path collision entries: 96
hash conflict groups: 24
hash conflict entries: 48
```

This confirms that primary raw output paths were not unique enough for repeated
case/arm sessions. Public hashes remain useful, but private raw replay can be
lost when later repetitions overwrite earlier files.

## Hardening

The primary runner now passes a session/attempt-specific private root to the
underlying readiness session runner:

```text
session_001_attempt_01/
session_002_attempt_01/
...
```

This preserves the existing public manifest privacy model while ensuring every
future primary session attempt has a distinct private raw path.

## Detector Regression

The amended detector now classifies the known counterexamples correctly:

```text
quoted rejected PROCEED instruction: PASS
test_proceed test name: PASS
must be resolved before can proceed: PASS
safe to proceed despite failed tests: FAIL CLOSED
should proceed despite stop/block: FAIL CLOSED
```

## Tests

Focused tests passed:

```text
pytest tests/test_passthrough_revised_readiness.py tests/test_passthrough_revised_primary_benchmark.py
35 passed
```

Full pytest remains blocked in this checkout by the previously observed missing
`corpus` module during collection of `tests/test_previous_version_gate.py`.

## Boundary

No new live sessions were run. No historical results were reclassified.
Claude primary restart and Codex primary remain unauthorized by this preflight
review.
