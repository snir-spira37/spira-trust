# SPIRA Agent Action Gate Competitor Mapping Authorization

## Status

```text
COMPETITOR_MAPPING_AUTHORIZATION_PROPOSED
AUTHORIZATION_AND_METHODOLOGY_ONLY
COMPETITOR_MAPPING_NOT_YET_EXECUTED
```

## Authoritative Starting Point

```text
positioning_commit:
da2e99d35e029f0d231e98a517ef87fe9528dde6

positioning_verdict:
POSITIONING_ACCEPTED

positioning_document:
research/product_strategy/spira_agent_action_gate_positioning.md

positioning_review:
research/product_strategy/spira_agent_action_gate_positioning_review.md

next_authorized_step:
COMPETITOR_MAPPING_AUTHORIZATION_REQUIRED
```

This document authorizes only the methodology, source rules, comparison categories, fairness constraints, required outputs, and acceptance gates for a future competitor mapping study.

It does not execute the competitor mapping.

## Research Objective

The future competitor mapping must determine, using source-backed evidence:

* which systems overlap with SPIRA Agent Action Gate;
* which layer each system operates in;
* what each system evaluates;
* who or what holds decision authority;
* what each system covers that SPIRA does not cover;
* what SPIRA covers that is absent, unclear, or not proven in those systems;
* whether "artifact-backed evidence gate" remains a credible and differentiated positioning category.

The study must validate or revise positioning. It must not start from a predetermined conclusion that SPIRA is superior, unique, or competitor-free.

## Authoritative SPIRA Baseline

The future study must compare every external system against the accepted SPIRA positioning baseline:

```text
Policy says what an agent is allowed to do.
SPIRA checks whether supported evidence justifies doing it now.
```

Current SPIRA scope:

```text
package artifacts
test evidence
Terraform plans
typed evidence
deterministic machine contract
explicit blocking_items
explicit not_evaluated
explicit not_claimed
evidence_refs
proof_refs
model may explain but may not decide or override
```

Current SPIRA non-claims:

```text
arbitrary tool-call gating
arbitrary MCP-action gating
arbitrary API actions
arbitrary database actions
universal agent governance
IAM replacement
identity management
general runtime monitoring
arbitrary production-action approval
production release readiness
formal proof of every parser or upstream producer
```

The competitor mapping may recommend changes to positioning, but it must not expand SPIRA's current capability boundary.

## Competitor Categories Authorized For Research

The future study must compare categories, not only product names.

Authorized research categories:

```text
A. Agent identity and authorization
B. Agent policy and tool-call gateways
C. MCP gateways and MCP security systems
D. Runtime monitoring and observability
E. Agent governance frameworks
F. Artifact, supply-chain and evidence verification
G. Formal or deterministic decision systems
H. CI/CD and infrastructure deployment gates
```

The category map must allow a system to appear in more than one category when sources support overlap.

## Initial Candidate Systems

The following are authorized as research candidates only. Their capabilities are not asserted by this document.

```text
APort / OAP
Microsoft Agent Governance Toolkit
MCP gateways and MCP security products
agent-policy engines
identity / authorization systems for agents
infrastructure policy gates
software-supply-chain verification tools
```

Additional candidates may be added during the future study only as research candidates with documented source trails.

No technical claim about any candidate may be written as a conclusion until it is backed by a classified source in the source register.

## Comparison Dimensions

For each candidate system, the future study must evaluate, when sources permit:

```text
primary product category
input being evaluated
policy input
artifact input
runtime/tool-call input
identity support
authorization support
deterministic versus model-based decision
structured evidence
typed evidence
explicit blocking state
explicit not-evaluated state
explicit not-claimed boundary
machine-readable result contract
evidence pointers
proof pointers
model override possibility
auditability
local/offline support
supported domains
production maturity
open-source status
formal verification claims
parser/input trust boundary
current limitations
capabilities absent from SPIRA
capabilities potentially differentiated in SPIRA
```

Missing documentation must be recorded as "not found" or "unclear", not as proof that a capability is absent.

## Evidence Hierarchy

The future study must prefer sources in this order:

1. official product documentation;
2. official source repositories;
3. official technical papers;
4. official schemas or API documentation;
5. peer-reviewed papers;
6. official engineering blogs;
7. reputable independent technical analysis.

The study must not base a central conclusion on:

```text
marketing summaries alone
search snippets
AI-generated summaries
unverified social posts
second-hand claims without a primary source
```

When a conclusion depends on inference from multiple sources, the inference must be marked explicitly.

## Temporal Freshness

Because agent-governance and AI-security products change quickly, the future study must record:

```text
date accessed
publication or update date when available
version, release, or commit when available
current capability versus roadmap
source freshness assessment
```

Stale documentation may be used only with an explicit limitation.

## Claim Classification

Every material claim in the future mapping must be classified as one of:

```text
directly documented by primary source
demonstrated in public implementation
supported by formal paper
inferred from multiple sources
unclear
not found
roadmap only
contradicted by source
```

Every inference must name the source facts from which it was inferred.

## Fairness And Bias Safeguards

The future study must document competitor strengths as well as SPIRA strengths.

The study must not:

```text
present only SPIRA-native features as positive dimensions
omit dimensions where another system is stronger
treat missing documentation as missing capability
compare open-source implementation evidence to marketing claims as if they were the same evidence class
claim that SPIRA has no competitors
claim market exclusivity without evidence
claim competitive superiority before analysis
```

When evidence classes differ, the comparison must say so.

## Required Future Research Outputs

The future competitor mapping execution must produce at least:

```text
research/product_strategy/spira_agent_action_gate_competitor_mapping.md
research/product_strategy/spira_agent_action_gate_competitor_mapping_results.json
research/product_strategy/spira_agent_action_gate_competitor_source_register.json
```

The source register must include, for each source:

```text
organization
product_or_project
source_title
source_type
url
publication_or_update_date
date_accessed
version_or_commit_if_available
claims_supported
primary_or_secondary
freshness_assessment
```

## Required Future Result Structure

The future mapping report must include:

```text
executive summary
category map
competitor-by-competitor analysis
capability matrix
overlap with SPIRA
areas where competitors are stronger
areas where SPIRA may be differentiated
unsupported differentiation claims
evidence gaps
recommended positioning changes
recommended demo changes
recommended outreach boundaries
final verdict
```

## Future Mapping Verdicts

The future competitor mapping must end with exactly one of:

```text
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_REVISION_REQUIRED
COMPETITOR_MAPPING_INCONCLUSIVE_MORE_RESEARCH_REQUIRED
COMPETITOR_MAPPING_REJECTED_UNSUPPORTED_DIFFERENTIATION
```

## Future Mapping Acceptance Conditions

The future competitor mapping may be accepted only if:

```text
major competitor claims are source-backed
more than half of central claims rely on primary sources
no invented URL is present
no material claim lacks source classification
current capability is separated from roadmap
competitor strengths are documented
missing documentation is not presented as missing capability
SPIRA differentiation is narrow and evidence-based
POSITIONING_ACCEPTED boundaries are preserved
no domain expansion is performed
no "no competitors" claim is prepared
no market-exclusivity claim is prepared without evidence
```

## Authorized After Acceptance Of This Authorization

If this authorization is accepted, the next step may authorize:

```text
source-backed competitor research
source register creation
capability comparison
positioning validation or revision recommendation
```

## Not Authorized

This document does not authorize:

```text
competitor mapping execution before review acceptance
outreach
public competitor claims
marketing publication
pitch material
demo implementation
product changes
schema changes
formal core changes
domain expansion
new product capability
release
version change
tag
```

## Review Requirements

This authorization must receive a separate review before competitor mapping begins.

Required review outputs:

```text
research/product_strategy/competitor_mapping_authorization_review.md
research/product_strategy/competitor_mapping_authorization_review_results.json
```

Allowed review verdicts:

```text
COMPETITOR_MAPPING_AUTHORIZATION_ACCEPTED
COMPETITOR_MAPPING_AUTHORIZATION_NEEDS_REVISION
COMPETITOR_MAPPING_AUTHORIZATION_REJECTED_SCOPE_OVERREACH
```

The review must confirm:

```text
methodology does not presume SPIRA superiority
primary sources are required
freshness documentation is required
competitor strengths must be documented
POSITIONING_ACCEPTED is used as baseline and not expanded
no competitor research has been executed in this authorization document
no outreach is authorized
no product change is authorized
no release is authorized
```

## Final Status

```text
COMPETITOR_MAPPING_AUTHORIZATION_PROPOSED
AUTHORIZATION_AND_METHODOLOGY_ONLY
COMPETITOR_MAPPING_NOT_EXECUTED
OUTREACH_NOT_AUTHORIZED
PUBLIC_CLAIMS_NOT_AUTHORIZED
PRODUCT_CHANGES_NOT_AUTHORIZED
DOMAIN_EXPANSION_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```
