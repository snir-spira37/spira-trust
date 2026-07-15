# SPIRA Agent Action Gate Competitor Mapping

## Status

```text
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
RESEARCH_EXECUTION_COMPLETE
NO_PRODUCT_CHANGE
NO_DOMAIN_EXPANSION
NO_OUTREACH
NO_RELEASE
```

## Research Date And Freshness Boundary

```text
research_date:
2026-07-15

positioning_commit:
da2e99d35e029f0d231e98a517ef87fe9528dde6

authorization_commit:
fe9047488438b40d0a0adf592123c7074acc38a7
```

This mapping uses source material accessed on July 15, 2026. Products in agent governance, MCP security, and AI observability are changing quickly. This report is a current-positioning study, not a permanent market map.

## Executive Summary

The accepted SPIRA positioning is supported, but only as a narrow and qualified position:

```text
Policy says what an agent is allowed to do.
SPIRA checks whether supported evidence justifies doing it now.
```

The research found real overlap. SPIRA does have competitors and adjacent systems.

The strongest overlaps are:

```text
APort / OAP:
pre-action agent authorization and signed policy decisions

Microsoft Agent Governance Toolkit:
broad agent governance, identity, policy, sandboxing and MCP-oriented controls

OPA / HCP Terraform / Sentinel / Spacelift / Conftest:
deterministic policy gates over Terraform and infrastructure artifacts

Sigstore / SLSA / in-toto / Scorecard:
software artifact provenance and supply-chain verification

OpenAI / NeMo / Lakera / Galileo:
model, prompt, output, evaluation and observability guardrails
```

The research did not support claims such as:

```text
SPIRA has no competitors
SPIRA is the only pre-action agent gate
SPIRA is the only Terraform-plan gate
SPIRA currently governs arbitrary tool calls or MCP actions
SPIRA replaces IAM, identity, authorization or runtime policy systems
```

The research does support a narrower differentiation:

> SPIRA combines supported software artifacts, typed evidence, deterministic machine contracts, explicit `not_evaluated`, explicit `not_claimed`, evidence/proof references, and a model-non-authority boundary. The reviewed sources did not document that exact combination in one system.

That sentence must remain qualified. It is based on reviewed sources, not a claim of market exclusivity.

## Methodology

The study followed:

```text
research/product_strategy/competitor_mapping_authorization.md
```

Rules applied:

* official documentation, repositories, specs, and technical papers were preferred;
* every material claim is linked to source IDs in the source register;
* missing documentation is recorded as `NOT_FOUND` or `UNCLEAR`, not treated as proof of absence;
* competitor strengths are documented explicitly;
* current capability is separated from roadmap or not-claimed capability;
* SPIRA's accepted positioning is treated as baseline and not expanded.

Full source register:

```text
research/product_strategy/spira_agent_action_gate_competitor_source_register.json
```

## SPIRA Accepted Baseline

Current SPIRA scope:

```text
Python/package artifacts
test and build evidence
Terraform plan evidence
domain-specific adapters
typed evidence
deterministic machine action contract
explicit action semantics
blocking_items
reason_codes
not_evaluated
not_claimed
evidence_refs
proof_refs
model may explain
model may not decide or override
local artifact-backed evaluation
```

Not claimed:

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

## Category Map

| Category | Systems Reviewed | Relationship To SPIRA |
| --- | --- | --- |
| Agent identity and authorization | APort/OAP, Microsoft AGT | Stronger than SPIRA for identity, capability, and tool/action authorization. SPIRA does not claim identity or arbitrary action authorization. |
| Agent policy and tool-call gateways | APort/OAP, Microsoft AGT, OpenAI tool guardrails | Overlap on pre-action control, but SPIRA gates supported artifact evidence rather than arbitrary tool calls. |
| MCP gateways and MCP security | Docker MCP Gateway, Cloudflare MCP portals, Microsoft AGT | Stronger than SPIRA for MCP isolation, access control, portal/gateway operation and runtime integration. |
| Runtime monitoring and observability | Cloudflare AI Gateway, Galileo, OpenAI tracing/guardrails | Stronger for runtime telemetry and observability. SPIRA is local artifact-backed evaluation, not general runtime monitoring. |
| Agent governance frameworks | Microsoft AGT, APort/OAP | Stronger breadth; SPIRA is narrower and evidence-centered. |
| Artifact and supply-chain verification | SLSA, Sigstore, in-toto, Scorecard | Stronger for provenance/signing/ecosystem maturity. SPIRA overlaps in artifact evidence but focuses on action contracts. |
| Formal or deterministic decision systems | OPA, Sentinel, APort/OAP, SPIRA | Real overlap. SPIRA's distinct point is explicit evidence-to-contract semantics with `not_evaluated` and `not_claimed`. |
| CI/CD, infrastructure and deployment gates | OPA Terraform, HCP Terraform/Sentinel, Spacelift, Conftest | Strong overlap with Domain 3. SPIRA must not imply that Terraform pre-apply gating is unique. |

## Competitor Profiles

### APort / Open Agent Passport

Sources: `SRC-001`, `SRC-002`, `SRC-003`.

APort/OAP is a close conceptual neighbor for pre-action agent authorization. Its official specification describes AI-agent identity, capabilities and policy enforcement, with a standardized decision object and `/verify` flow. The paper frames this as deterministic pre-action authorization for autonomous AI agents.

Strengths relative to SPIRA:

```text
agent identity and passport model
arbitrary pre-tool-call authorization surface
cryptographic decision object / signatures
framework-oriented integrations
policy packs for action categories
```

SPIRA distinction:

```text
SPIRA does not currently authorize arbitrary tool calls.
SPIRA's current wedge is supported artifact evidence -> typed evidence -> machine contract.
APort/OAP sources reviewed do not document SPIRA-style not_evaluated/not_claimed artifact contracts.
```

Claim classification:

```text
APort has pre-action authorization:
PRIMARY_SOURCE_DOCUMENTED

SPIRA is broader than APort:
REJECTED

SPIRA is different from APort:
MULTI_SOURCE_INFERENCE
```

### Microsoft Agent Governance Toolkit

Sources: `SRC-004`, `SRC-005`.

Microsoft AGT is a broad agent governance project. Its repository describes policy enforcement, zero-trust identity, sandboxing, reliability engineering, language SDKs, and MCP-related components.

Strengths relative to SPIRA:

```text
broader governance surface
identity and zero-trust posture
policy engine and sandboxing
MCP gateway-related work
multi-language SDKs
larger ecosystem and maturity signals
```

SPIRA distinction:

```text
SPIRA is narrower and should not be positioned as a replacement.
The reviewed AGT sources do not present the same artifact-specific machine contract with explicit not_evaluated/not_claimed fields.
```

Claim classification:

```text
AGT overlaps with agent governance:
PRIMARY_SOURCE_DOCUMENTED

AGT is a direct one-to-one SPIRA replacement:
UNCLEAR / NOT ESTABLISHED

SPIRA should position as complementary:
MULTI_SOURCE_INFERENCE
```

### Docker MCP Gateway

Source: `SRC-006`.

Docker MCP Gateway addresses MCP server execution and access through Docker's MCP Catalog and Toolkit. The docs describe MCP servers running in isolated containers, restricted privileges, network controls, logging and call tracing.

Strengths relative to SPIRA:

```text
MCP execution control
container isolation
network policy
tool-call tracing
runtime gateway integration
```

SPIRA distinction:

```text
SPIRA does not currently gate arbitrary MCP calls.
SPIRA can later integrate with MCP gateways, but current capability is artifact-backed evaluation.
```

### Cloudflare AI Gateway And MCP Portals

Sources: `SRC-007`, `SRC-008`.

Cloudflare AI Gateway focuses on AI app traffic, observability, rate limiting, caching and gateway behavior. Cloudflare One MCP portal docs cover MCP connection and access surfaces.

Strengths relative to SPIRA:

```text
network/gateway maturity
observability and traffic control
MCP access control
enterprise edge integration
```

SPIRA distinction:

```text
SPIRA does not provide gateway observability or MCP access control today.
SPIRA evaluates supported artifacts before action.
```

### OpenAI Agents SDK Guardrails

Source: `SRC-009`.

OpenAI's agent docs describe guardrails and human review around agent workflows, including input, output and tool guardrail patterns.

Strengths relative to SPIRA:

```text
native agent workflow integration
tool/workflow guardrail ergonomics
model-provider integration
human review flow support
```

SPIRA distinction:

```text
SPIRA is provider-independent and artifact-backed.
SPIRA does not rely on the model as the decision authority for its machine contract.
```

### NVIDIA NeMo Guardrails

Source: `SRC-010`.

NeMo Guardrails documents rail types across input, dialog, retrieval, execution and output behavior.

Strengths relative to SPIRA:

```text
general LLM application guardrails
dialog and retrieval rails
execution rails
ecosystem maturity
```

SPIRA distinction:

```text
NeMo-like systems are stronger for conversational guardrails.
SPIRA is not a general content guardrail; it is a deterministic artifact evidence gate.
```

### Lakera Guard

Source: `SRC-011`.

Lakera Guard is positioned around AI guardrails and defenses such as prompt-injection and unsafe-content protection.

Strengths relative to SPIRA:

```text
prompt and content security
real-time AI security use cases
broad LLM threat coverage
```

SPIRA distinction:

```text
SPIRA does not compete as a prompt-injection classifier.
SPIRA gates supported artifacts and contracts.
```

### Galileo AI

Source: `SRC-012`.

Galileo positions as an AI observability and evaluation platform.

Strengths relative to SPIRA:

```text
observability
evaluation workflows
production monitoring and quality analysis
```

SPIRA distinction:

```text
SPIRA is not a full observability platform.
SPIRA emits a bounded action contract for supported artifacts.
```

### Open Policy Agent Terraform Policy

Source: `SRC-013`.

OPA is a major overlap for Domain 3. Its Terraform docs explicitly describe checking Terraform changes before Terraform makes them, operating over Terraform JSON plans, and using policies to enforce organizational rules.

Strengths relative to SPIRA:

```text
mature policy language
broad deployment footprint
Terraform plan JSON policy examples
many integrations beyond SPIRA's current domains
```

SPIRA distinction:

```text
SPIRA must not claim Terraform pre-action gating is unique.
SPIRA's Domain 3 differentiation is the accepted machine contract shape, explicit not_evaluated/not_claimed boundary, evidence/proof references, and model non-authority for agent presentation.
```

### HCP Terraform / Sentinel / OPA Policy Enforcement

Source: `SRC-014`.

HCP Terraform policy enforcement supports Sentinel and OPA policy checks in the Terraform workflow.

Strengths relative to SPIRA:

```text
native Terraform workflow integration
production maturity
policy enforcement in established infrastructure pipelines
organizational policy features
```

SPIRA distinction:

```text
SPIRA is not replacing HCP Terraform policy enforcement.
SPIRA's Terraform demo is valid but must be framed as evidence-contract gating for AI-assisted actions, not as a novel discovery that plans can be policy-checked.
```

### Spacelift Policies

Source: `SRC-015`.

Spacelift provides policy-as-code for infrastructure workflows, including OPA-based policy behavior.

Strengths relative to SPIRA:

```text
infrastructure workflow integration
policy lifecycle
production platform maturity
broader CI/CD control surface
```

SPIRA distinction:

```text
SPIRA is narrower and local artifact-backed.
SPIRA may complement infrastructure platforms by producing bounded evidence contracts.
```

### Conftest

Source: `SRC-016`.

Conftest tests structured configuration data using OPA/Rego, including common IaC and configuration artifacts.

Strengths relative to SPIRA:

```text
general structured-config testing
OPA/Rego ecosystem
simple CLI adoption
wide artifact formats
```

SPIRA distinction:

```text
SPIRA produces a specific machine action contract with explicit non-evaluation and non-claim boundaries.
```

### SLSA

Source: `SRC-017`.

SLSA is a supply-chain security specification for artifacts, levels, provenance and verification.

Strengths relative to SPIRA:

```text
industry-recognized supply-chain specification
provenance model
broad ecosystem adoption
```

SPIRA distinction:

```text
SPIRA does not replace SLSA.
SPIRA may consume or produce bounded artifact evidence in workflows where action decisions depend on supported artifacts.
```

### Sigstore Policy Controller

Source: `SRC-018`.

Sigstore Policy Controller is a Kubernetes admission controller using verifiable supply-chain metadata.

Strengths relative to SPIRA:

```text
container/image signing and verification ecosystem
Kubernetes admission control
production supply-chain enforcement use case
```

SPIRA distinction:

```text
SPIRA is not an image-signing or Kubernetes admission replacement.
SPIRA's package-artifact evidence story is narrower and action-contract oriented.
```

### in-toto

Source: `SRC-019`.

in-toto focuses on software supply-chain integrity, layouts, metadata and provenance.

Strengths relative to SPIRA:

```text
supply-chain metadata model
provenance tracking
recognized ecosystem role
```

SPIRA distinction:

```text
SPIRA is not a full supply-chain provenance framework.
SPIRA's current value is bounded decision contracts over supported evidence.
```

### OpenSSF Scorecard

Source: `SRC-020`.

OpenSSF Scorecard performs automated checks for open-source project security risks.

Strengths relative to SPIRA:

```text
open-source security risk scoring
large ecosystem usage
automated project checks
```

SPIRA distinction:

```text
SPIRA is not a general open-source project risk score.
SPIRA evaluates supported artifacts into action contracts.
```

## Capability Matrix

| System | Primary Input | Pre-Action Gate | Deterministic | Typed Evidence | Explicit Not Evaluated | Explicit Not Claimed | Machine Contract | Model Override Boundary | Stronger Than SPIRA |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| SPIRA | package/test/Terraform artifacts | yes for supported artifacts | yes | yes | yes | yes | yes | yes | no arbitrary tool/MCP gateway |
| APort/OAP | agent passport, policy, capability/action request | yes | documented as deterministic | structured decision objects | unclear | not found | decision object | yes, via external authorization | identity, arbitrary pre-tool-call auth |
| Microsoft AGT | agent runtime, policy, identity, MCP/tool events | yes / runtime | policy-based | structured schemas | unclear | not found | governance/audit artifacts | yes in governance layer | breadth, SDKs, identity, MCP |
| Docker MCP Gateway | MCP server/tool traffic | yes/runtime gateway | policy/runtime controls | structured gateway metadata | not found | not found | gateway logs/traces | yes via gateway | MCP isolation and runtime control |
| Cloudflare AI Gateway / MCP portals | AI traffic, MCP portal access | yes/runtime gateway | gateway policy | structured logs/config | not found | not found | gateway logs/config | yes via gateway/access | edge, access and observability |
| OpenAI Agents guardrails | prompts, tool calls, model outputs | workflow guardrails | mixed | structured workflows | unclear | not found | guardrail/human review result | configurable | model-native agent workflow |
| NeMo Guardrails | prompts, dialog, retrieval, execution, output | runtime rails | mixed | rails/config | unclear | not found | rail outcome | configurable | LLM app guardrail breadth |
| Lakera Guard | prompts/content | runtime/input-output | model/classifier-based | detection result | not found | not found | guardrail result | external filter | prompt-injection/content security |
| Galileo AI | traces, eval data, runtime quality | monitoring/eval | mixed | eval/observability data | not found | not found | eval/monitoring outputs | observability layer | production observability/evals |
| OPA Terraform | Terraform plan JSON | yes | yes | policy input data | Terraform limitation documented | not found | policy decision | not model based | policy ecosystem, Terraform maturity |
| HCP Terraform/Sentinel/OPA | Terraform runs/plans | yes | yes | run/plan policy data | policy-dependent | not found | policy check result | not model based | native Terraform workflow |
| Spacelift | IaC workflow data | yes | yes | OPA policy input | policy-dependent | not found | policy result | not model based | infrastructure workflow platform |
| Conftest | structured config data | yes/offline | yes | structured input | policy-dependent | not found | test/policy result | not model based | broad config format testing |
| SLSA | build/source provenance | yes in verification workflows | spec/verification dependent | provenance/attestation | not found | not found | provenance/verification artifacts | not model based | supply-chain standard |
| Sigstore Policy Controller | image signatures/attestations | yes | yes | policy + signed metadata | policy-dependent | not found | admission decision | not model based | Kubernetes/image enforcement |
| in-toto | supply-chain layout/metadata | yes in verification workflows | yes | metadata/provenance | not found | not found | verification result | not model based | supply-chain provenance |
| OpenSSF Scorecard | repository metadata | offline score | yes/mixed checks | check results | not found | not found | score/check result | not model based | ecosystem security checks |

## Overlap Analysis

### Strong Overlap

OPA, HCP Terraform/Sentinel, Spacelift and Conftest overlap strongly with the Terraform part of SPIRA.

This means the Terraform demo should be framed carefully:

```text
Valid:
SPIRA demonstrates evidence-to-contract gating over Terraform plan evidence in an AI-agent action context.

Invalid:
SPIRA is the first or only system to gate Terraform plans before apply.
```

APort/OAP and Microsoft AGT overlap strongly with agent action governance. They are closer to arbitrary action/tool authorization than SPIRA is today.

### Moderate Overlap

SLSA, Sigstore, in-toto and Scorecard overlap with Domain 1 and artifact trust, but they do not appear in reviewed sources as AI-agent action evidence-to-contract systems.

### Weak Or Adjacent Overlap

OpenAI guardrails, NeMo, Lakera and Galileo address model behavior, guardrails, evaluation, observability and prompt/content risks. They are adjacent and may be integrated with SPIRA, but they are not direct replacements for deterministic artifact evidence contracts.

## Competitors Stronger Than SPIRA

```text
Identity and authorization:
APort/OAP, Microsoft AGT, Cloudflare Access/MCP portals

Arbitrary tool-call / MCP control:
APort/OAP, Microsoft AGT, Docker MCP Gateway, Cloudflare MCP portals

Runtime interception and observability:
Cloudflare AI Gateway, Galileo, OpenAI agent workflows, Microsoft AGT

Terraform and infrastructure policy maturity:
OPA, HCP Terraform/Sentinel, Spacelift, Conftest

Supply-chain provenance maturity:
SLSA, Sigstore, in-toto, OpenSSF Scorecard

LLM prompt/content guardrails:
OpenAI, NeMo, Lakera

Adoption and ecosystem breadth:
Microsoft, OPA, HashiCorp, Sigstore/SLSA, Docker, Cloudflare
```

These strengths should be preserved in external positioning. SPIRA is not trying to beat every layer.

## SPIRA Potentially Differentiated Areas

The reviewed sources support the following narrow differentiators:

```text
1. artifact-backed evidence-to-contract boundary for supported software actions

2. explicit not_evaluated as a first-class non-approval state

3. explicit not_claimed boundary in the machine contract

4. evidence_refs and proof_refs as part of the current accepted contract shape

5. model may explain but cannot decide, override or upgrade the machine contract

6. formally reviewed small core supporting bounded decision semantics
```

Important limitation:

```text
The reviewed sources did not document this exact combination in one competing system.
This is not the same as proving no such system exists.
```

## Unsupported Differentiation Claims

Rejected claims:

```text
SPIRA has no competitors.
SPIRA is the only pre-action agent gate.
SPIRA is the only Terraform-plan gate.
SPIRA is broader than Microsoft AGT or APort.
SPIRA replaces IAM, policy engines, MCP gateways or runtime observability.
SPIRA currently handles arbitrary backup/restore/approval/database/API evidence.
SPIRA formally proves parsers or upstream producers.
```

## Evidence Gaps

```text
1. Several systems expose docs without explicit version/date metadata.

2. Microsoft AGT and APort are moving quickly; a future revision should pin commits/releases before public comparison.

3. Some product pages describe capabilities at marketing level; deeper repo/API review is needed before detailed feature-by-feature public claims.

4. Lack of documented not_claimed/not_evaluated fields in competitors is NOT_FOUND, not proof of absence.

5. SPIRA's own current external story still needs a precise Domain 3 demo script before outreach.
```

## Implications For Positioning

The accepted positioning is supported:

```text
Policy says what an agent is allowed to do.
SPIRA checks whether supported evidence justifies doing it now.
```

Recommended public wording:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.
Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

Reason for the wording change:

```text
"evidence-to-contract" makes the machine-contract output visible and reduces confusion with generic guardrails, policy engines, or observability tools.
```

No formal positioning revision is required. This is a sharpening, not a change in accepted scope.

## Implications For Product Roadmap

Roadmap should not expand immediately. The strongest next product logic remains:

```text
1. keep current Domains 1-3 bounded;
2. make Domain 3 Terraform agent-action demo exact and reproducible;
3. later consider integrations with policy/MCP layers rather than replacing them;
4. treat backup/restore/approval/database/API adapters as separate future domains.
```

Potential integration directions:

```text
SPIRA + OPA/Sentinel/HCP Terraform:
SPIRA provides agent-facing machine contract and not_evaluated/not_claimed boundary around artifact evidence.

SPIRA + APort/OAP or Microsoft AGT:
policy layer authorizes whether an agent may call the tool; SPIRA evaluates whether the artifact justifies doing it now.

SPIRA + MCP gateways:
MCP gateway controls access and runtime; SPIRA controls supported evidence gates before selected actions.
```

## Implications For Demo

The approved demo remains Domain 3 only:

```text
Terraform plan JSON
-> typed evidence
-> machine contract
-> STOP_BLOCKED or REPORT_NOT_EVALUATED / RERUN_REQUIRED
-> model explanation with no decision authority
```

The demo should explicitly say:

```text
This is not a generic MCP gateway.
This is not arbitrary API/database action approval.
This is artifact-backed evidence gating for a supported Terraform plan artifact.
```

## Implications For Outreach

Outreach is not authorized by this report.

When later authorized, outreach should avoid:

```text
no competitors
first/only pre-action gate
universal agent governance
arbitrary tool-call safety
formal proof of all inputs
```

Safer outreach thesis:

```text
Existing systems handle policy, identity, MCP/runtime control, observability, and infrastructure policy. SPIRA adds a bounded artifact-evidence contract layer: before a supported software action proceeds, the artifact is converted into typed evidence and a machine contract that preserves blockers, not-evaluated claims and not-claimed boundaries.
```

## Recommended Positioning Wording

Primary:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.
```

Supporting:

```text
Policy says what an agent is allowed to do.
SPIRA checks whether supported evidence justifies doing it now.
```

Boundary:

```text
Today SPIRA supports package artifacts, test evidence and Terraform plans.
Arbitrary tool calls, MCP actions, API/database operations and backup/approval evidence remain roadmap.
```

Competitive qualifier:

```text
SPIRA is not a replacement for identity, authorization, MCP gateways, OPA/Sentinel, supply-chain provenance systems, or AI observability. It is a complementary evidence-to-contract layer for supported artifacts.
```

## not_claimed

This competitor mapping does not claim:

```text
SPIRA has no competitors
SPIRA is market-exclusive
SPIRA is the only pre-action gate
SPIRA is the only Terraform-plan gate
SPIRA is broader than agent governance platforms
SPIRA replaces policy engines or IAM
SPIRA controls arbitrary tool calls or MCP actions today
SPIRA proves parsers or upstream producers
SPIRA is production-ready for all domains
```

## Limitations

```text
Research was performed on 2026-07-15.
Only public sources were reviewed.
No private enterprise features were tested.
No product execution or live competitor trial was performed.
No claims were verified by running competitor code.
Fast-moving systems require future freshness review before public publication.
```

## Final Verdict

```text
COMPETITOR_MAPPING_ACCEPTED_POSITIONING_SUPPORTED
```

The accepted SPIRA positioning is supported as a narrow, source-backed market position.

SPIRA should not claim it has no competitors. It should claim a narrower wedge:

```text
artifact-backed evidence-to-contract gating for supported AI-assisted software actions,
with explicit blockers, not_evaluated, not_claimed, evidence/proof references,
and no model decision authority.
```

## Next Step

```text
DEMO_SCRIPT_AUTHORIZATION_REQUIRED
```

This report does not authorize outreach, pitch material, public claims, demo implementation, product changes, domain expansion, release, version change or tag.
