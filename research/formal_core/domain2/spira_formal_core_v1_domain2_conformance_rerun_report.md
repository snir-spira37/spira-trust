# SPIRA Formal Core V1 Domain 2 Conformance Rerun Report

Status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED
```

Summary:

```json
{
  "blocking_to_proceed_cases": [],
  "case_count": 38,
  "case_fail_count": 0,
  "case_pass_count": 38,
  "mismatch_count": 0,
  "mutation_pair_checks": {
    "passed": 6,
    "total": 6
  },
  "not_evaluated_to_proceed_cases": [],
  "report_with_notes_cases": [
    "synthetic_skipped_test",
    "synthetic_xfail"
  ],
  "test_notes_drops": []
}
```

Lean:

```json
{
  "lake_build_returncode": 0,
  "proof_scan": "PASS"
}
```

Local verification:

```text
lake build: PASS

focused pytest:
24 / 24 PASS

full pytest:
244 / 247 PASS
3 out-of-scope hash-manifest failures in existing passthrough/benchmark asset
gates, not in Formal Core V1 Domain 2 conformance.
```

Raw pytest/JUnit parser formally proved: no.

This report does not authorize Domain 1, Domain 3, runtime integration, production claims, or release activity.
