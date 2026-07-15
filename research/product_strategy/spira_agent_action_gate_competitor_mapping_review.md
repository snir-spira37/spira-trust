# SPIRA Agent Action Gate Competitor Mapping Review

## Status

```text
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
REVIEW_COMPLETE
NO_OUTREACH
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_RELEASE
```

## Documents Reviewed

```text
research/product_strategy/spira_agent_action_gate_competitor_mapping.md
research/product_strategy/spira_agent_action_gate_competitor_mapping_results.json
research/product_strategy/spira_agent_action_gate_competitor_source_register.json
```

## Review Date

```text
2026-07-15
```

## Review Objective

This review checks whether the competitor mapping follows the accepted authorization:

```text
research/product_strategy/competitor_mapping_authorization.md
```

The review verifies that the mapping is source-backed, fair to competitors, preserves the accepted SPIRA boundary, and does not perform outreach, product change, domain expansion or release activity.

## Source Review

The mapping includes:

```text
source_count: 20
primary_sources_count: 20
secondary_sources_count: 0
```

The source register includes official specifications, repositories, documentation, official engineering posts, and project pages.

The source register records:

```text
organization
product_or_project
title
source_type
url
publication_date
last_updated_date
accessed_date
version
release
commit
primary_or_secondary
claims_supported
current_or_historical
freshness_assessment
reliability_assessment
notes
```

Several official sources did not publish explicit update dates on the page. The register handles this as a freshness limitation, not as proof of current version.

## Claim Review

The mapping correctly rejects unsupported claims:

```text
SPIRA has no competitors
SPIRA is the only pre-action agent gate
SPIRA is the only Terraform-plan gate
SPIRA governs arbitrary tool calls today
SPIRA governs arbitrary MCP/API/database actions today
SPIRA replaces IAM or identity systems
SPIRA is a universal AI-agent governance platform
SPIRA formally proves all parsers or upstream producers
```

The supported differentiator is narrow:

```text
artifact-backed evidence-to-contract gating for supported AI-assisted software actions,
with explicit blockers, not_evaluated, not_claimed, evidence/proof references,
and no model decision authority.
```

The mapping labels that differentiator as a multi-source inference based on reviewed sources, not as market exclusivity.

## Competitor Fairness Review

The mapping documents competitor strengths:

```text
APort/OAP:
identity, agent passport, arbitrary pre-tool-call authorization

Microsoft AGT:
broad governance, identity, policy, sandboxing, MCP, SDKs

Docker / Cloudflare:
MCP and gateway control, access, isolation, observability

OPA / HCP Terraform / Sentinel / Spacelift / Conftest:
mature Terraform and infrastructure policy gates

SLSA / Sigstore / in-toto / Scorecard:
supply-chain provenance and artifact trust maturity

OpenAI / NeMo / Lakera / Galileo:
agent/model guardrails, observability and evaluation workflows
```

The mapping does not construct a matrix where SPIRA wins by selecting only SPIRA-native dimensions.

## Accepted SPIRA Boundary Review

The mapping preserves current SPIRA scope:

```text
package artifacts
test evidence
Terraform plan evidence
domain-specific adapters
typed evidence
deterministic machine action contract
blocking_items
reason_codes
not_evaluated
not_claimed
evidence_refs
proof_refs
model explanation without model decision authority
```

It does not claim current support for:

```text
arbitrary tool-call gating
general MCP-action enforcement
arbitrary API actions
arbitrary database actions
agent identity management
IAM replacement
universal agent governance
general runtime monitoring
proof of every parser
universal production safety
autonomous model approval
```

## Findings By Severity

### Critical

None.

### High

None.

### Medium

None.

### Low

Some official sources do not expose explicit update dates. The mapping records this limitation. Future public comparison should refresh source dates and pin releases or commits where possible.

## Acceptance Conditions

```text
major competitors source-backed: PASS
primary source majority: PASS
freshness documented: PASS
current capability separated from roadmap: PASS
competitor strengths documented: PASS
SPIRA gaps documented: PASS
no invented URL: PASS
no invented product: PASS
inference marked: PASS
NOT_FOUND not used as ABSENT: PASS
no total uniqueness claim: PASS
no domain expansion: PASS
no product change: PASS
no outreach: PASS
no release: PASS
```

## Verdict

```text
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
```

The accepted SPIRA positioning is supported as a narrow, source-backed positioning:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.
Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

This review does not authorize public outreach, pitch material, demo implementation, product change, domain expansion, release, version change or tag.

## Next Authorized Step

```text
DEMO_SCRIPT_AUTHORIZATION_REQUIRED
```
