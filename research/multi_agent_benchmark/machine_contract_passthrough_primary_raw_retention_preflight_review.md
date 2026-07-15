# Machine Contract Passthrough Primary Raw Retention Preflight Review

## Verdict

```text
MACHINE_CONTRACT_PASSTHROUGH_PRIMARY_RAW_RETENTION_PREFLIGHT_PASS

RAW_PRIVATE_PATH_COLLISION_CONFIRMED
PRIMARY_RAW_RETENTION_HARDENED
SESSION_ATTEMPT_UNIQUE_RAW_PATHS_ACCEPTED
PUBLIC_RAW_MANIFEST_PRIVACY_PRESERVED

DETECTOR_REGRESSION_PREFLIGHT_PASS
FOCUSED_TESTS_PASS

HISTORICAL_RESULTS_PRESERVED
NO_RESULT_RECLASSIFICATION
NO_NEW_LIVE_SESSIONS

CLAUDE_PRIMARY_RESTART_AUTHORIZATION_REQUIRED_NEXT
CODEX_PRIMARY_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review

The preflight is accepted.

The raw-private path collision analysis confirmed that previous primary
attempts could overwrite raw stdout/stderr files across repeated primary
sessions for the same case and arm. The public manifest retained hashes, but a
complete future audit requires distinct private raw paths for every
session/attempt.

The primary runner now stores future raw outputs in session/attempt-specific
private subdirectories while preserving the public manifest privacy boundary.

## Detector Regression

The known detector false-positive family is covered:

```text
quoted hostile instruction rejected by the model
test name containing test_proceed
blocking precondition phrased as "must be resolved before ... can proceed"
```

The known unsafe forms remain fail-closed.

## Tests

Focused tests passed:

```text
35 passed
```

Full pytest was attempted previously and remains blocked by:

```text
ModuleNotFoundError: No module named 'corpus'
```

## Required Next Step

The next live step requires a fresh primary restart authorization or an
explicit reaffirmation of the existing restart authorization after this raw
retention hardening.

The next Claude primary must start from session 1 under:

```text
amended detector
session/attempt-unique raw private storage
same prompt/schema/validator/MVP/cases
```

Codex primary remains blocked until Claude has a completed report/review or a
separate authorization changes that order.
