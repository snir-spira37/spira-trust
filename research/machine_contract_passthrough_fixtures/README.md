# Machine Contract Passthrough Fixtures

This directory contains deterministic fixtures for the accepted SPIRA machine-contract passthrough envelope schema.

The fixtures are static test artifacts only. They do not implement a validator, do not run model sessions, and do not change MVP code.

Fixture categories:

```text
positive/
machine_contract_integrity_failures/
model_explanation_contradictions/
telemetry_failures/
sensitive_value_failures/
```

Each fixture has expected outcomes recorded in `fixture_manifest.json`. Sensitive-value fixtures use synthetic marker strings only.
