# SPIRA Formal Core V1 All-Domains Conformance Review

## Status

```text
SPIRA_FORMAL_CORE_V1_ALL_DOMAINS_CONFORMANCE_ACCEPTED

DOMAIN_1_FORMAL_TYPED_SEMANTICS_ACCEPTED

DOMAIN_1_BASELINE_DIFFERENTIAL_CONFORMANCE_ACCEPTED

DOMAIN_2_FORMAL_TYPED_SEMANTICS_ACCEPTED

DOMAIN_2_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED

DOMAIN_3_FORMAL_TYPED_SEMANTICS_ACCEPTED

DOMAIN_3_PYTHON_ADAPTER_DIFFERENTIAL_CONFORMANCE_ACCEPTED

FORMAL_CORE_V1_ACTION_ALGEBRA_UNCHANGED

RAW_WHEEL_ZIP_PARSER_FORMALLY_PROVED_NO

RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO

RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO

RUNTIME_INTEGRATION_NOT_AUTHORIZED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```

## Decision

Formal Core V1 conformance is accepted across the three bounded typed-evidence
domains currently in scope:

```text
Domain 1 - Python artifact identity evidence
Domain 2 - pytest result evidence
Domain 3 - Terraform Plan evidence
```

This review accepts only typed-evidence conformance and differential agreement
with the accepted domain artifacts. It does not prove raw parser correctness,
Python runtime correctness, operating-system behavior, model behavior,
benchmark runner behavior, production integration, or release readiness.

## Evidence Summary

```text
Domain 1:
  records: 1954 / 1954 PASS
  baseline root recomputation: PASS
  false PROCEED: 0
  NOT_EVALUATED -> PROCEED: 0
  identity drops: 0
  list drops: 0
  sensitive/private leakage: 0
  lake build: PASS
  proof scan: PASS

Domain 2:
  cases: 38 / 38 PASS
  mutation pairs: 6 / 6 PASS
  REPORT_WITH_NOTES mapping: PROCEED + TEST_NOTES
  blocking -> PROCEED: 0
  NOT_EVALUATED -> PROCEED: 0
  identity/evidence/proof drops: 0
  lake build: PASS
  proof scan: PASS

Domain 3:
  cases: 40 / 40 PASS
  mutation pairs: 10 / 10 PASS
  false PROCEED: 0
  blocking -> PROCEED: 0
  NOT_EVALUATED -> PROCEED: 0
  malformed -> PROCEED: 0
  instruction overrides: 0
  identity/evidence/proof drops: 0
  lake build: PASS
  proof scan: PASS
```

## Accepted Domain Reviews

```text
research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_review.md

research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_rerun_review.md

research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_review.md
```

The original negative Domain 2 conformance review remains preserved. The
accepted Domain 2 result is the rerun after the reviewed mapping amendment:

```text
REPORT_WITH_NOTES -> PROCEED + TEST_NOTES
```

The Formal Core V1 action algebra remains:

```text
PROCEED
STOP_BLOCKED
RERUN_REQUIRED
REPORT_NOT_EVALUATED
```

Domain 1 legacy `ASK_HUMAN` is preserved as a Domain 1 baseline action and maps
to the non-proceeding Formal Core V1 action:

```text
ASK_HUMAN -> REPORT_NOT_EVALUATED
```

## What Is Now Supported

The accepted claim is:

```text
Given typed evidence satisfying the Formal Core V1 domain language and bounded
policy context, the Formal Core V1 projection preserves the authoritative
action, stop state, explicit reason_codes, blocking_items where applicable,
NOT_EVALUATED, not_claimed where modeled, evidence/proof identity, and fails
closed rather than producing unsafe PROCEED under the accepted domain gates.
```

The accepted conformance evidence covers:

```text
Domain 1 accepted identity baseline: 1954 records

Domain 2 accepted pytest corpus: 38 cases and 6 mutation pairs

Domain 3 accepted Terraform Plan corpus: 40 cases and 10 mutation pairs
```

## What Is Still Not Proven

This review does not prove:

```text
wheel / ZIP / RECORD parsing

pytest / JUnit parsing

Terraform Plan JSON parsing

JSON canonicalization implementation correctness

SHA-256 implementation correctness

Python runtime correctness

filesystem behavior

operating-system behavior

LLM provider behavior

benchmark runner behavior

passthrough live-agent behavior

production integration

release readiness
```

These remain classified according to the Trusted Computing Base ledger as
trusted assumptions, tested-only components, future conformance work, or
out-of-scope components.

## Required Next Step

The next methodological step may be proposed separately as a proof package /
integration boundary review that connects:

```text
Formal Core V1 typed-evidence conformance

Gate A abstract preservation

machine-contract passthrough authority

Python executable reference / differential harness

trusted computing base ledger
```

That next step must not claim production readiness unless it receives separate
authorization and review.

## Final Boundary

```text
FORMAL_CORE_V1_ALL_DOMAINS_CONFORMANCE_ACCEPTED

TYPED_EVIDENCE_BOUNDARY_ONLY

RAW_ADAPTERS_NOT_FORMALLY_PROVED

PRODUCTION_CLAIM_NOT_AUTHORIZED

RELEASE_NOT_AUTHORIZED
```
