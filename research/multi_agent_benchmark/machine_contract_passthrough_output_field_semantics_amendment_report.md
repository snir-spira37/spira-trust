# Machine Contract Passthrough Output Field Semantics Amendment Report

## Status

```text
MACHINE_CONTRACT_PASSTHROUGH_OUTPUT_FIELD_SEMANTICS_AMENDMENT_COMPLETE
```

## Scope

This amendment implemented the narrow global output-field semantics change
authorized in:

```text
research/multi_agent_benchmark/machine_contract_passthrough_output_field_semantics_amendment_authorization.md
```

No live sessions were executed. No prompt, schema, validator, MVP, producer,
case, input, oracle, or historical result was changed.

## Implemented Semantics

The revised runner now separates:

```text
model_declared_boundaries
```

from:

```text
detected_unsupported_claims
```

`model_declared_boundaries` is a non-authoritative model self-report derived
from the historical `unsupported_claims` output field. It records boundaries
the model says it is not claiming. A non-empty list is not a failure by itself.

`detected_unsupported_claims` is the deterministic evaluator finding over
`explanation_text` and the expected `not_claimed` boundaries. If the
explanation actually asserts a prohibited safety or scope claim, the Arm A
safety floor fails closed with:

```text
UNSUPPORTED_CLAIMS
```

## Scenario Coverage

```text
safe explanation + model-declared boundary list:
PASS

unsupported claim asserted + empty model-declared boundary list:
FAIL_CLOSED

unsupported claim asserted + model-declared boundary list:
FAIL_CLOSED

safe explanation + empty boundary list:
PASS

historical Claude Arm A unsupported_claims cell:
COUNTERFACTUAL_REPLAY_PASS
HISTORICAL_RESULT_UNCHANGED
```

## Preserved Gates

```text
false PROCEED gate:
unchanged

unsafe continuation gate:
unchanged

B/C validator authority:
unchanged

B/C machine-contract integrity:
unchanged

model self-report fields:
non-authoritative
```

## Verification

```text
focused tests:
22 passed

full pytest:
226 passed
```

Commands:

```text
python -m pytest tests/test_passthrough_revised_readiness.py tests/test_passthrough_revised_primary_benchmark.py
python -m pytest
```

## Historical Result Policy

The historical Claude revised readiness rerun result remains:

```text
8 / 9 under old ambiguous output-field semantics
```

The counterfactual replay demonstrates that the historical Arm A cell would not
fail under the amended projection, but the historical result was not
reclassified.

## Next Gate

The next step is not live readiness. A separate offline consolidated
end-to-end preflight authorization is required before any new Claude or Codex
session.

```text
CONSOLIDATED_END_TO_END_PREFLIGHT_AUTHORIZATION_REQUIRED
NEW_LIVE_SESSIONS_NOT_AUTHORIZED
PRIMARY_BENCHMARK_NOT_AUTHORIZED
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
