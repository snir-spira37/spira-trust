# SPIRA Agent Action Gate - Positioning and Current Capability Boundary

**Document status:** Positioning draft for review
**Scope:** Current SPIRA product and accepted Domains 1-3
**Purpose:** Define what SPIRA does, how it should be presented, what can be demonstrated today, and what must not yet be claimed.

---

## 1. Positioning Statement

SPIRA is an **artifact-backed evidence gate for consequential AI-agent actions**.

It does not replace an authorization policy, an identity system, an agent runtime, or a tool-call gateway.

Instead, SPIRA answers a different question:

> **Does the available evidence justify performing this action now?**

The central distinction is:

> **Policy says what an agent is allowed to do. SPIRA checks whether the evidence justifies doing it now.**

This distinction must remain present in all product descriptions, demonstrations, technical documentation, and outreach materials.

---

## 2. One-Sentence Product Description

> **SPIRA deterministically converts supported software artifacts into typed evidence, evaluates that evidence through a bounded decision contract, and emits a machine-readable action result with an auditable evidence trail.**

A shorter public version:

> **SPIRA verifies the evidence behind an AI agent's proposed action before that action proceeds.**

Required boundary when using the shorter version:

> **Today, SPIRA evaluates supported artifact-backed evidence. It does not yet evaluate arbitrary tool calls or arbitrary external actions.**

---

## 3. The Problem SPIRA Addresses

AI agents can generate code, packages, test results, infrastructure plans, and recommended actions.

However, a model-generated recommendation is not itself reliable evidence that an action is safe.

An agent may:

* misunderstand an artifact;
* overlook a destructive change;
* work from incomplete evidence;
* treat missing evidence as positive evidence;
* produce a confident explanation despite an unresolved blocker;
* recommend execution before the underlying artifact has been deterministically evaluated.

Traditional authorization systems answer questions such as:

* Is this identity allowed to invoke this tool?
* Is this operation permitted by policy?
* Is this action inside the agent's assigned scope?
* Does this user or service account have permission?

Those questions are necessary, but they are not sufficient.

An agent can be authorized to run `terraform apply` while the proposed plan still contains a resource change that the accepted SPIRA Domain 3 contract blocks from proceeding.

SPIRA addresses this second layer:

> The agent may be authorized to act, but does the evidence support acting on this specific artifact now?

---

## 4. What SPIRA Is

SPIRA is a deterministic evidence and decision layer positioned between:

1. an artifact produced or selected by a human, CI system, or AI agent; and
2. a consequential action based on that artifact.

Its current operating pattern is:

```text
Artifact
  ->
Domain adapter
  ->
Typed evidence
  ->
Deterministic formal core
  ->
Machine action contract
  ->
Auditable evidence output
```

The language model may consume the resulting contract and explain it.

The language model does not own the decision.

```text
Model role:
- summarize
- explain
- present blockers
- suggest the next evidence-producing step

Model non-role:
- override the contract
- convert missing evidence into approval
- silently weaken a blocker
- reinterpret NOT_EVALUATED as safe
- authorize execution independently
```

---

## 5. What SPIRA Is Not

SPIRA must not currently be described as:

* a universal AI-agent governance platform;
* a complete agent authorization system;
* a replacement for IAM or access control;
* a general-purpose tool-call firewall;
* an arbitrary API-action gate;
* an arbitrary database-operation gate;
* a runtime monitor for every agent action;
* a proof that every parser or upstream producer is correct;
* a production authorization for all software domains;
* an autonomous action-approval model;
* an LLM-based judge.

SPIRA currently evaluates artifacts only in domains for which a bounded adapter, evidence model, decision contract, and validation corpus exist.

---

## 6. Current Supported Evidence Domains

SPIRA currently supports three artifact-backed evidence domains.

### Domain 1 - Package Artifact Evidence

Current evidence source:

* Python package and wheel artifacts;
* package identity and related supply-chain evidence;
* structured package-level verification results.

The domain converts supported package artifacts into a deterministic evidence representation and preserves the relevant artifact identity through the decision path.

This domain must not be generalized publicly into "all software supply-chain artifacts" without a corresponding adapter and validation corpus.

---

### Domain 2 - Test and Build-Run Evidence

Current evidence source:

* supported test-run artifacts;
* build or test failure information;
* bounded failure classifications;
* structured evidence pointers and action results.

The domain evaluates whether the available test evidence supports proceeding, blocking, rerunning, or reporting that the required conclusion was not evaluated.

This domain does not prove that an entire application is correct.

It evaluates the bounded claims represented by its accepted evidence contract.

---

### Domain 3 - Terraform Plan Evidence

Current evidence source:

* supported Terraform plan JSON;
* parsed infrastructure changes;
* resource-change, errored-plan, not-applyable, malformed, incomplete, unsupported, unknown, and sensitive-path evidence;
* incomplete or non-evaluable plan states.

This is the authoritative domain for the current agent-action demonstration.

It directly supports the product message because an agent may propose an infrastructure action while SPIRA independently evaluates the artifact behind that proposal.

---

## 7. Current Product Category

The most accurate category description is:

> **Artifact-backed AI action evidence gate**

Alternative technical description:

> **Deterministic evidence-to-action contract engine**

Alternative buyer-oriented description:

> **Pre-action evidence verification for AI-assisted software operations**

SPIRA should not currently be categorized simply as an "agent policy engine."

Policy engines primarily establish what is allowed.

SPIRA establishes whether the supported evidence justifies acting in the present case.

---

## 8. Core Differentiation

SPIRA's differentiation is not that no other system addresses agent governance.

Its differentiation is the combination of the following properties.

### 8.1 Evidence Before Explanation

SPIRA evaluates the artifact before allowing a model-generated explanation to influence presentation.

The explanation is downstream of the decision contract.

```text
Incorrect pattern:
Model reads evidence -> model decides -> model explains

SPIRA pattern:
Artifact -> deterministic evaluation -> contract -> model explains contract
```

---

### 8.2 Typed Evidence

Raw logs, plans, packages, and test outputs are not treated as interchangeable text.

Each supported domain converts its source artifact into bounded typed evidence.

This prevents an arbitrary natural-language interpretation from becoming the decision interface.

---

### 8.3 Explicit Non-Evaluation

Missing, unreadable, unsupported, or insufficient evidence must not silently become approval.

Where the required claim cannot be evaluated, the contract must preserve that state explicitly.

For example:

```text
REPORT_NOT_EVALUATED
```

This means:

* the evidence was insufficient for the required decision;
* the action was not justified by the evaluated contract;
* the result is not equivalent to safe;
* the result is not equivalent to a minor warning;
* the model may explain what evidence is missing but may not upgrade the result.

---

### 8.4 Fail-Closed Action Semantics

A blocker remains a blocker through:

* adapter output;
* formal-core processing;
* machine-contract generation;
* compact agent summary;
* model explanation.

No downstream layer may transform a blocked or non-evaluated state into permission to proceed.

---

### 8.5 Auditability

SPIRA emits machine-readable artifacts that allow a reviewer to determine:

* what source artifact was evaluated;
* what evidence was extracted;
* what claims were evaluated;
* what blockers were found;
* what action result was produced;
* which evidence pointers support the result;
* which claims were not evaluated;
* what boundaries remain outside the result.

---

### 8.6 Published Boundaries

SPIRA treats `not_claimed` information as part of the product contract.

A trustworthy result includes not only what was established, but also what was not established.

This is a product feature, not a disclaimer added after the fact.

---

## 9. Authoritative Demonstration

### 9.1 Demonstration Scenario

An AI coding or infrastructure agent proposes:

```text
terraform apply
```

The proposed action is authorized at the policy level.

However, before execution, SPIRA receives an existing supported Terraform plan JSON artifact.

```text
AI agent
  proposes terraform apply
        ->
Terraform plan JSON
        ->
SPIRA Domain 3 adapter
        ->
Typed Terraform evidence
        ->
Deterministic decision contract
        ->
STOP_BLOCKED or REPORT_NOT_EVALUATED
        ->
Existing machine-readable result artifact + bounded explanation
```

---

### 9.2 Resource-Change Blocking Path

The Terraform plan contains an infrastructure resource change classified by the accepted Domain 3 contract as requiring review before proceeding.

Accepted Domain 3 evidence includes Terraform resource-change actions such as create, update, delete, and replacement-related sequences. Under the current Domain 3 contract, effective resource changes are blocked from automatic proceed.

SPIRA reads the plan artifact and produces typed evidence representing the effective change.

The resulting machine contract returns:

```text
STOP_BLOCKED
```

The result includes a blocking item and evidence references. In the accepted Domain 3 raw-adapter fixture shape, a representative blocked contract contains:

```json
{
  "action": "STOP_BLOCKED",
  "stop": true,
  "reason_codes": [
    "TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"
  ],
  "blocking_items": [
    "resource change requires review"
  ],
  "not_evaluated": [],
  "not_claimed": [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS"
  ],
  "evidence_refs": [
    "plan.json:create_update_delete_01",
    "manifest:create_update_delete_01"
  ],
  "proof_refs": [
    "domain3_raw_adapter_fixture:create_update_delete_01"
  ]
}
```

The exact fixture ID and evidence references in a live demonstration must come from the selected accepted Domain 3 fixture or generated artifact. They must not be invented for presentation.

The model may explain:

```text
The requested apply is blocked because the evaluated Terraform plan contains
an infrastructure resource change that the Domain 3 contract requires review
for before proceeding.
```

The model may not say:

```text
The deletion is probably intentional, so it is safe to continue.
```

The contract, not the model, controls the action result.

---

### 9.3 Incomplete Or Non-Evaluable Evidence Path

The plan is malformed, unreadable, partial, unsupported, or insufficient to evaluate the required claim.

SPIRA does not infer safety from the absence of a detected destructive change.

Depending on the accepted Domain 3 condition, the result is either:

```text
REPORT_NOT_EVALUATED
```

or, for malformed JSON that requires a clean rerun:

```text
RERUN_REQUIRED
```

For a representative unsupported or incomplete plan path, the model may explain:

```text
SPIRA could not establish whether the proposed apply is justified because the
required Terraform plan evidence was not fully evaluable under the accepted
Domain 3 contract.
```

The model may recommend generating a new plan or supplying the missing artifact.

It may not convert the state into permission to apply.

---

### 9.4 Demonstration Output

The demonstration should show four separate surfaces.

#### A. Agent proposal

```text
Proposed action:
terraform apply
```

#### B. Artifact evidence

```text
Input:
terraform-plan.json
```

#### C. SPIRA machine contract

Use the current accepted Domain 3 contract shape. At minimum, show the fields that exist in the implementation and fixtures:

```json
{
  "action": "STOP_BLOCKED",
  "stop": true,
  "reason_codes": [
    "TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"
  ],
  "blocking_items": [
    "resource change requires review"
  ],
  "not_evaluated": [],
  "not_claimed": [
    "APPLY_SUCCESS",
    "INFRASTRUCTURE_COMPLIANCE",
    "INFRASTRUCTURE_CORRECTNESS",
    "INFRASTRUCTURE_COST",
    "INFRASTRUCTURE_SECURITY",
    "LIVE_STATE_FRESHNESS"
  ],
  "evidence_refs": [
    "plan.json:create_update_delete_01",
    "manifest:create_update_delete_01"
  ],
  "proof_refs": [
    "domain3_raw_adapter_fixture:create_update_delete_01"
  ]
}
```

Do not use invented presentation-only fields such as `type` or `evidence_pointer` unless a future accepted schema introduces them.

#### D. Model explanation

```text
The apply is blocked because the evaluated Terraform plan contains a resource
change that the Domain 3 contract blocks from automatic proceed. The model can
explain the result but cannot override it.
```

The demo must use an existing accepted machine-readable result artifact or evidence output alongside the explanation. It must not invent a new audit schema for presentation.

---

## 10. Why This Demonstration Is Valid

The Terraform demonstration uses an existing accepted domain.

It does not require:

* a new backup adapter;
* a restore-verification adapter;
* an approval-record adapter;
* a database-action adapter;
* synthetic evidence that the current product cannot actually parse;
* a placeholder governance layer;
* a model-generated simulation of a deterministic decision.

The demonstration is therefore aligned with the current product rather than with a future roadmap.

---

## 11. Demonstrations That Must Not Be Presented As Current Capability

The following scenario must not be used as the principal live demonstration today:

```text
Before a database deletion:
- verify that a backup exists;
- verify that restore was tested;
- verify that human approval exists;
- decide whether deletion may proceed.
```

This is a valid future SPIRA use case, but only after corresponding evidence adapters and contracts exist.

Until then, it belongs in a roadmap section.

It must be labeled:

```text
Future action-evidence adapter example
Not current product capability
```

The same boundary applies to:

* arbitrary production database writes;
* arbitrary cloud API calls;
* arbitrary shell commands;
* payment execution;
* user-account deletion;
* medical or legal decisions;
* generalized browser-agent actions;
* arbitrary MCP tool invocations.

---

## 12. Current Capability Boundary

The required public boundary statement is:

> **SPIRA currently gates artifact-backed actions using supported package artifacts, test evidence, and Terraform plans. It does not yet gate arbitrary tool calls, arbitrary API actions, or arbitrary database operations.**

A shorter version:

> **Today, SPIRA checks supported artifact-backed evidence. Arbitrary action-evidence adapters are roadmap, not current capability.**

This boundary must appear in:

* the positioning document;
* the demonstration script;
* external technical presentations;
* competitor comparisons;
* investor or partner materials;
* outreach to agent-platform vendors;
* any claim using the phrase "agent action gate."

---

## 13. Relationship To Policy And Authorization Systems

SPIRA should be presented as complementary to policy and authorization systems.

### Policy layer

Answers:

```text
May this identity invoke this capability?
```

Examples of policy concerns include:

* identity;
* role;
* scope;
* permissions;
* tool allowlists;
* resource boundaries;
* organizational rules.

### SPIRA evidence layer

Answers:

```text
Does the evaluated artifact justify this proposed action now?
```

Examples of SPIRA concerns include:

* Is the package artifact valid under the supported contract?
* Does the test evidence contain a blocking failure?
* Does the Terraform plan contain a resource change that blocks automatic proceed?
* Was the required claim actually evaluated?
* Is the evidence sufficient to support proceeding?
* What machine-readable blockers and evidence pointers exist?

Combined architecture:

```text
Authorization policy
        +
SPIRA evidence contract
        ->
Action eligibility
```

Neither layer replaces the other.

---

## 14. Relationship To AI Models

SPIRA is not positioned as a better reasoning model.

Its purpose is to remove specific action decisions from unconstrained model judgment.

### The model may:

* request artifact evaluation;
* present the result;
* summarize evidence;
* explain blockers;
* identify missing evidence;
* recommend a rerun or evidence-producing step;
* help a human understand the contract.

### The model may not:

* override `STOP_BLOCKED`;
* reinterpret `REPORT_NOT_EVALUATED` as permission;
* remove required blocking items;
* invent missing evidence;
* claim evaluation of an unsupported domain;
* substitute its own confidence for the deterministic contract;
* describe a roadmap adapter as already implemented.

The intended operating principle is:

> **AI agents generate or select artifacts. SPIRA verifies supported artifacts. Humans and authorized systems act on the bounded contract.**

---

## 15. Intended Users

Current likely users include:

* teams introducing coding agents into CI/CD workflows;
* platform engineering teams;
* infrastructure teams using Terraform;
* software-supply-chain teams;
* security and governance teams;
* teams requiring reproducible evidence before automated execution;
* regulated organizations evaluating agent-assisted development;
* vendors building agent runtimes or orchestration platforms.

The initial buyer should not be told that SPIRA governs every agent action.

The more accurate value proposition is:

> SPIRA adds a deterministic evidence gate to selected high-consequence artifact-backed workflows.

---

## 16. Current Use Cases

### Package release verification

A package or wheel is evaluated before a release-related action proceeds.

### Test-evidence gating

A supported test artifact is evaluated before an agent recommends or performs a downstream action.

### Terraform apply gating

A Terraform plan is evaluated before an AI agent or automation proceeds toward `terraform apply`.

### Agent-context compression

The deterministic contract can be presented to an agent in a compact form, reducing the need to provide the model with broad raw evidence while preserving blockers and non-evaluated claims.

Context-efficiency results must be cited only from the relevant accepted benchmark artifacts and must preserve any protocol limitations or errata.

---

## 17. Approved Messaging

### Primary message

> **Policy says what an agent is allowed to do. SPIRA checks whether the evidence justifies doing it now.**

### Supporting message

> **SPIRA turns supported software artifacts into deterministic, auditable action contracts.**

### Agent-focused message

> **The agent may explain the result. It does not control the result.**

### Trust-focused message

> **Missing evidence does not become approval.**

### Technical message

> **Typed evidence in. Bounded machine contract out.**

### Current-boundary message

> **Today, SPIRA evaluates package artifacts, test evidence, and Terraform plans. Broader action adapters remain roadmap.**

---

## 18. Claims That Require Qualification

### "SPIRA blocks unsafe actions"

Use instead:

> **SPIRA blocks actions when the accepted domain contract identifies a blocking condition in the evaluated artifact.**

SPIRA does not establish universal safety.

---

### "SPIRA verifies AI-agent actions"

Use instead:

> **SPIRA verifies supported artifact-backed evidence associated with proposed AI-agent actions.**

---

### "SPIRA governs AI agents"

Use instead:

> **SPIRA provides an evidence-gating layer that can integrate with agent-governance and authorization systems.**

---

### "SPIRA proves the parser is correct"

Not currently claimed.

The formal core, adapter conformance, parser behavior, and upstream artifact production must remain separate claims.

---

### "SPIRA is production-ready for every domain"

Not claimed.

Production readiness must be evaluated per release, integration, adapter, operating environment, and authorized action surface.

---

## 19. Formal And Reproduction Boundaries

Formal Core V1 and its external reproduction package strengthen the claim that the bounded core and associated artifacts can be inspected and reproduced under the specified toolchain.

They do not automatically establish:

* correctness of every external parser;
* correctness of Terraform itself;
* correctness of every test producer;
* correctness of every package repository;
* absence of all software defects;
* authorization to release;
* authorization to enable live agents;
* universal production readiness;
* arbitrary-domain coverage.

The positioning document must not merge these separate layers into one broad "formally proven AI governance" claim.

---

## 20. Roadmap Boundary

Future adapters may extend SPIRA to evidence such as:

* backup existence;
* independent backup status;
* restore-test results;
* approval records;
* change tickets;
* deployment-health evidence;
* database migration plans;
* API-operation evidence;
* cloud-provider change sets;
* security scan results;
* policy attestations;
* runtime observations.

Each new adapter requires its own bounded process:

```text
Domain declaration
-> evidence contract
-> corpus
-> oracle
-> validator
-> producer
-> conformance evaluation
-> mutation testing
-> false-PROCEED analysis
-> acceptance
-> product integration authorization
```

A roadmap idea is not a current capability until this chain is completed and accepted.

---

## 21. Competitive-Mapping Boundary

Competitor mapping must begin only after this positioning is reviewed.

The comparison should distinguish at least four categories:

1. identity and authorization systems;
2. agent policy and tool-call gateways;
3. runtime monitoring and observability systems;
4. artifact-backed evidence and decision systems.

The comparison must not begin from the claim that SPIRA has no competitors.

It must determine:

* where products overlap;
* where their decision authority sits;
* whether they inspect raw tool calls or structured artifacts;
* whether they preserve explicit non-evaluation;
* whether their result is deterministic;
* whether the model can override the result;
* whether they emit an auditable machine contract;
* whether their evidence schemas are domain-specific;
* which capabilities they possess that SPIRA does not yet possess.

No competitor URL or technical claim should be included in a locked document until independently verified.

---

## 22. Product Narrative

The complete product narrative is:

```text
AI agents are increasingly capable of generating code, packages, tests,
infrastructure plans, and operational recommendations.

Authorization systems determine which tools an agent may access.

That does not establish that a specific proposed action is justified by
the current evidence.

SPIRA evaluates supported artifacts through bounded domain adapters and
a deterministic formal core.

It produces a machine-readable action contract, explicit blockers,
evidence pointers, and not-evaluated boundaries.

The model may explain that contract, but it cannot override it.

Today, SPIRA supports package artifacts, test evidence, and Terraform
plans.

Broader action-evidence adapters are part of the roadmap, not current
capability.
```

---

## 23. Demo Closing Statement

The Terraform demonstration should end with:

> **The agent was authorized to propose the action. SPIRA independently evaluated the artifact behind it. The plan contained a resource change that the accepted Domain 3 contract blocks from automatic proceed, so the machine contract stopped the action. The model explained the result, but it did not make or override the decision.**

For incomplete or unsupported plan evidence:

> **SPIRA did not find enough evaluable evidence to justify the action. It returned `REPORT_NOT_EVALUATED` rather than treating missing evidence as approval.**

For malformed Terraform plan JSON:

> **SPIRA returned `RERUN_REQUIRED` because the plan JSON itself could not be parsed into evaluable evidence.**

---

## 24. Final Positioning Lock

The proposed authoritative positioning is:

> **SPIRA is an artifact-backed evidence gate for consequential AI-agent actions. Policy establishes what an agent is allowed to do; SPIRA evaluates whether supported evidence justifies doing it now. SPIRA currently supports bounded package, test, and Terraform-plan evidence. It does not yet govern arbitrary tool calls or arbitrary external actions. Models may explain SPIRA's machine contract, but they may not decide or override it.**

This document is a positioning draft for review. It does not itself accept the positioning, authorize competitor mapping, authorize outreach, authorize a release, or authorize domain expansion.

---

## 25. Required Next Documents

After this document is reviewed, the next proposed sequence is:

```text
1. spira_agent_action_gate_positioning_review.md
   Scope: review and positioning acceptance

2. competitor_mapping_authorization.md
   Scope: authorize evidence-based competitor research only

3. spira_agent_action_gate_competitor_mapping.md
   Scope: verified comparison against selected systems

4. terraform_agent_action_gate_demo_script.md
   Scope: exact Domain 3 demonstration using current implementation

5. outreach_message_pack.md
   Scope: external communication derived only from accepted claims
```

Domain expansion, release activity, live-agent authorization, and new action adapters remain separate decisions.

---

## Final Status

```text
POSITIONING_DRAFTED_FOR_REVIEW
DOMAIN_3_DEMO_SELECTED
ARTIFACT_BACKED_SCOPE_EXPLICIT
ARBITRARY_TOOL_CALL_GATING_NOT_CLAIMED
MODEL_DECISION_AUTHORITY_DENIED
COMPETITOR_MAPPING_PENDING_AUTHORIZATION
OUTREACH_NOT_YET_AUTHORIZED

NO_DOMAIN_EXPANSION
NO_COMPETITOR_MAPPING
NO_OUTREACH
NO_RELEASE
NO_PRODUCT_BEHAVIOR_CHANGE
NO_SCHEMA_CHANGE
NO_FORMAL_CORE_CHANGE
```
