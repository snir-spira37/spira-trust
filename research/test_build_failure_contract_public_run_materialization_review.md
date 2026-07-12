# Test/Build Failure Contract Public Run Materialization Review

Status:

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_ACCEPTED
DOMAIN_2_CORPUS_ACCEPTED
PUBLIC_RUN_MATERIALIZATION_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
RELEASE_VERSION_TAG_PYPI_NOT_AUTHORIZED
```

Reviewed commit:

```text
2124f7d Materialize Domain 2 public runs
```

Authorization:

```text
042c389 Authorize Domain 2 public run materialization
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_AUTHORIZED
```

This is a corpus and public-run materialization review only. It does not
authorize oracle population, producer implementation, Gate B, Domain 3, or any
release activity.

## Review Question

The review separates two decisions:

```text
Public stratum:
Did the 8 public runs become materialized, pinned and reviewable evidence?

Overall corpus:
Do the 38 cases together provide a frozen input basis sufficient for later
independent oracle authoring?
```

This review does not decide the expected claims, expected actions,
result_identity values, or whether a public case "should" have passed based on
its name. Exit codes are treated as raw evidence.

## Public Stratum Verdict

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_ACCEPTED
```

The public stratum now contains 8 materialized public run records:

```text
public_click_import
public_click_param
public_flask_clean
public_flask_param
public_flask_unicode_path
public_requests_assertion
public_requests_clean
public_requests_long_traceback
```

Each public case records:

```text
repository identity
pinned commit
dependency environment
structured execution argv
console output hash
JUnit XML hash
exit-code hash
capture-completeness metadata
raw output publication status
```

The raw public outputs are not committed. They are recorded as:

```text
WITHHELD_AFTER_PRIVACY_OR_LICENSE_REVIEW
```

This publication mode is allowed by the public-run materialization
authorization because the outputs were materialized and their hashes were
recorded. These hashes are not hashes of instruction files alone.

## Public Exit Codes

The recorded exit codes are:

```text
public_click_import: 0
public_click_param: 0
public_flask_clean: 0
public_flask_param: 0
public_flask_unicode_path: 1
public_requests_assertion: 4
public_requests_clean: 1
public_requests_long_traceback: 1
```

These are raw evidence values only. They are not oracle answers and are not
interpreted in this review.

For example, this review does not decide:

```text
whether public_requests_clean should have exited 0
whether public_requests_assertion should have failed differently
whether public_flask_unicode_path should pass in another environment
```

Those are oracle-authoring questions that remain blocked until a separate
oracle population authorization exists.

## Overall Corpus Verdict

```text
DOMAIN_2_CORPUS_ACCEPTED
```

The corpus now contains:

```text
total cases: 38
synthetic cases: 30
public materialized runs: 8
declared mutation pairs: 6
```

The synthetic stratum and mutation pairs were already accepted by the prior
corpus review. The remaining blocker was the public stratum, which has now
been materialized.

The accepted corpus is a frozen input corpus for later oracle authoring. It is
not an accepted oracle and not a producer benchmark.

## Mechanical Checks

Independent review checks:

```text
case_count: 38
unique case IDs: 38
synthetic cases: 30
public materialized run cases: 8
declared mutation pairs: 6
missing files: 0
source hash mismatches: 0
missing public materialization records: 0
missing public output hashes: 0
oracle_expected_answers values: NOT_POPULATED
producer_output_seen values: false
```

Materialization results report:

```text
json_validation: PASS
privacy_scan: PASS
path_scan: PASS
secret_scan: PASS
raw_evidence_exclusion_check: PASS
public_run_output_hashes_present: PASS
dependency_environment_recorded: PASS
```

Targeted path and secret scans found no committed private paths or secrets in
the published corpus materialization artifacts.

## Scope Preservation

No public case was replaced, removed, or added.

The public cases remain the 8 cases authorized for materialization:

```text
public_click_import
public_click_param
public_flask_clean
public_flask_param
public_flask_unicode_path
public_requests_assertion
public_requests_clean
public_requests_long_traceback
```

The overall corpus still has 38 cases and 6 mutation pairs. Oracle expected
answers remain unpopulated.

## What This Acceptance Means

Corpus acceptance means:

```text
the evidence inputs are frozen
public runs are materialized or hash-backed
source identities and dependency environments are recorded
case structure is stable
the corpus is suitable for later independent oracle authoring
```

It does not mean:

```text
the exit codes are semantically correct
the expected claims are known
the expected action is known
the result_identity is known
the producer is correct
Gate B is ready
```

## Still Not Authorized

This review does not authorize:

```text
oracle population
oracle expected answers
producer implementation
pytest adapter implementation
Gate B status/cache/rerun work
Domain 3 work
core changes
schema changes
validator changes
release/version/tag/PyPI publication
```

## Next Authorized Step

After this acceptance, the next possible artifact is a separate oracle
population authorization.

That future authorization must remain narrow and must not authorize producer
implementation or Gate B.

## Final Verdict

```text
DOMAIN_2_PUBLIC_RUN_MATERIALIZATION_ACCEPTED
DOMAIN_2_CORPUS_ACCEPTED
PUBLIC_RUN_MATERIALIZATION_REVIEW_COMPLETE
ORACLE_POPULATION_NOT_AUTHORIZED
PRODUCER_IMPLEMENTATION_NOT_AUTHORIZED
GATE_B_NOT_AUTHORIZED
DOMAIN_3_NOT_AUTHORIZED
```
