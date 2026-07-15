# SPIRA Formal Core V1 All-Domain Adapter Alignment Review

## Status

```text
SPIRA_FORMAL_CORE_V1_ALL_DOMAIN_ADAPTER_ALIGNMENT_ACCEPTED

DOMAIN_1_TYPED_CONFORMANCE_ACCEPTED
DOMAIN_1_RAW_ADAPTER_CONFORMANCE_ACCEPTED

DOMAIN_2_TYPED_CONFORMANCE_ACCEPTED
DOMAIN_2_RAW_ADAPTER_CONFORMANCE_ACCEPTED
DOMAIN_2_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED

DOMAIN_3_TYPED_CONFORMANCE_ACCEPTED
DOMAIN_3_RAW_ADAPTER_CONFORMANCE_ACCEPTED
DOMAIN_3_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED

RAW_WHEEL_ZIP_RECORD_SBOM_PARSER_FORMALLY_PROVED_NO
RAW_PYTEST_JUNIT_PARSER_FORMALLY_PROVED_NO
RAW_TERRAFORM_JSON_PARSER_FORMALLY_PROVED_NO

LIVE_AGENT_SESSIONS_NOT_INCLUDED
BENCHMARK_EXECUTION_NOT_AUTHORIZED
PRODUCTION_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Decision

The Formal Core V1 all-domain adapter alignment checkpoint is accepted for existing offline evidence.

The accepted chain is:

```text
Domain 1 Python artifact identity baseline
Domain 2 pytest/JUnit result evidence
Domain 3 Terraform Plan evidence
-> typed evidence boundary
-> Formal Core V1 action/list preservation semantics
-> authoritative machine contract
```

This checkpoint does not claim parser proofs, production readiness, release readiness, or live-agent benchmark readiness.

## Evidence

Domain 1:

```text
Typed conformance:
1954 / 1954 records pass
false PROCEED = 0
identity drops = 0
list drops = 0

Raw synthetic fixture conformance:
33 / 33 fixtures pass
false PROCEED = 0
identity hash loss = 0
unification ID loss = 0
full pytest = 264 / 264
```

Domain 2:

```text
Typed conformance:
38 / 38 production corpus cases pass
6 / 6 mutation pairs pass

Raw synthetic fixture conformance:
26 / 26 fixtures pass

Production adapter alignment:
accepted
false PROCEED = 0
blocking item loss = 0
NOT_EVALUATED loss = 0
not_claimed loss = 0
```

Domain 3:

```text
Typed conformance:
40 / 40 production corpus cases pass
10 / 10 mutation pairs pass

Raw synthetic fixture conformance:
31 / 31 fixtures pass

Production adapter alignment:
accepted
false PROCEED = 0
resource action loss = 0
replace path loss = 0
unknown path loss = 0
sensitive path loss = 0
full pytest = 260 / 260 at alignment checkpoint
```

## Boundary

The following remain explicitly outside the accepted claim:

```text
arbitrary wheel / ZIP / RECORD / SBOM parser proof
arbitrary pytest / JUnit parser proof
arbitrary Terraform Plan JSON parser proof
filesystem correctness
Python runtime correctness
Terraform execution correctness
provider behavior
cloud-state freshness
package safety
software safety
dependency safety
malware absence
license compliance
production readiness
release readiness
LLM or agent behavior
```

## Interpretation

The deterministic core path now has an accepted adapter-alignment checkpoint for all three domains:

```text
raw bounded evidence fixtures
-> typed evidence projection
-> explicit list and identity preservation
-> fail-closed action semantics
```

The strongest current claim is:

```text
For the accepted typed-evidence boundary and bounded fixture/corpus evidence,
Formal Core V1 preserves action, stop state, explicit lists, uncertainty, not-claimed boundaries,
evidence/proof identity, and fail-closed behavior across Domains 1-3.
```

The claim is not:

```text
SPIRA has formally proved all parsers.
SPIRA has proved package or infrastructure safety.
SPIRA is release-ready.
SPIRA agents are benchmark-ready.
```

## Next Step

The next deterministic step should be:

```text
SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PACKAGE_AUTHORIZATION
```

That package should allow an external reviewer to reproduce the offline formal-core artifacts, fixture checks, and pytest evidence without running live agents.

Live Claude/Codex/DeepSeek sessions remain intentionally deferred until after the deterministic proof/adapter package is externally reproducible.
