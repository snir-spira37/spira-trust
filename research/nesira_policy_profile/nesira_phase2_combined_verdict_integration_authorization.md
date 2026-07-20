# Nesira Phase 2 Combined Verdict Integration Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_PRODUCT_INTEGRATION_GATE
SCOPE: NESIRA_PHASE2_COMBINED_VERDICT_INTEGRATION_ONLY

AUTHORIZES:
combined verdict integration plan
combined verdict integration implementation
conformance tests
cold verification record

RUNNER: NOT_AUTHORIZED
SEVERANCE_ACTION: NOT_AUTHORIZED
AUTOMATIC_REMEDIATION: NOT_AUTHORIZED
CLAIM_EXPANSION: NOT_AUTHORIZED
VERSION_BUMP: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

This gate opens the narrow integration of the already published Nesira Phase 2
read-only assessment surface into SPIRA's existing combined verdict machinery.

It does not authorize an isolation runner, runtime observation, filesystem or
network enforcement, severance execution, remediation, or any claim that SPIRA
proves isolation happened.

## Frozen Inputs

The implementation must consume the already accepted Phase 2 assessment
artifact contract:

```text
verdict in:
  TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS
  TRUST_INSUFFICIENT
  TRUST_NOT_EVALUATED

execution_marker:
  ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION

mandatory carried assumptions:
  floor assumptions
  PT-ISOLATION-01 when an isolation sub-assessment is present
```

The implementation must not modify the Phase 2 trust model, NOT_PROVEN ledger,
Lean composition core, adapters, public claim, or 0.7.0 publication record.

## Integration Rule

Nesira may enter the combined verdict only as an explicit policy layer:

```text
layer: nesira_phase2_assessment
source: accepted read-only assessment artifact
```

It is not enabled by default for existing commands. Existing SPIRA behavior must
remain unchanged unless the caller supplies an explicit Nesira assessment
artifact or an explicit policy/configuration requiring this layer.

The layer maps to existing combined-verdict layer status as follows:

```text
TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS -> OK
TRUST_INSUFFICIENT                   -> BLOCK
TRUST_NOT_EVALUATED                  -> NOT_EVALUATED
missing required Nesira assessment   -> NOT_EVALUATED
malformed Nesira assessment          -> NOT_EVALUATED
forbidden execution-like field       -> BLOCK
execution_marker mismatch            -> BLOCK
missing required assumptions         -> BLOCK
missing PT-ISOLATION-01 when isolation is present -> BLOCK
```

`TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS` never upgrades any other layer. It means
only that the Nesira layer is OK under declared roots and recorded NOT_PROVEN
assumptions.

If any existing layer is `BLOCK`, the final combined verdict remains blocking
even when Nesira is sufficient.

If Nesira is required and `TRUST_NOT_EVALUATED`, the final agent decision must
stop with `REPORT_NOT_EVALUATED` through the existing not-evaluated mechanism.

## No New Execution Semantics

The integration may affect SPIRA's already existing reporting and stop contract.
It must not emit any new execution instruction.

Forbidden output fields and labels include:

```text
sever
severance_authorized
permission_to_sever
safe_to_sever
execute
run_isolation
combined_action
automatic_remediation
```

The existing `recommended_agent_action` vocabulary remains the only action
vocabulary:

```text
PROCEED
ASK_HUMAN
STOP_BLOCKED
REPORT_NOT_EVALUATED
REPORT_WITH_NOTES
RERUN_REQUIRED
```

No new action value may be added in this gate.

## Carrying Conditionality

Every combined verdict that consumes a Nesira assessment must carry enough
detail for downstream readers to see that Nesira remains conditional.

Required carried fields:

```text
nesira_verdict
nesira_assumptions
nesira_trust_roots_used
nesira_execution_marker
nesira_reason_codes
```

If `nesira_verdict = TRUST_SUFFICIENT_UNDER_DECLARED_ROOTS`, then
`nesira_assumptions` must still include `PT-ISOLATION-01` whenever the isolation
sub-assessment is present. A sufficient Nesira layer must never be
assumption-free.

## Product Behavior Invariants

The implementation must satisfy:

```text
NO_DEFAULT_NESIRA_REQUIREMENT:
  existing commands without an explicit Nesira assessment/policy behave as
  before

NO_NESIRA_UPGRADE:
  Nesira sufficient cannot change BLOCK/WARN/NOTE into a less conservative
  final verdict

FAIL_CLOSED_MALFORMED_NESIRA:
  malformed or action-looking Nesira artifacts cannot pass

NOT_EVALUATED_IS_NOT_PASS:
  required but not evaluated Nesira produces stop/report-not-evaluated through
  the existing agent decision contract

CONDITIONALITY_VISIBLE:
  assumptions and declared trust roots remain visible in combined output

ASSESSMENT_NOT_EXECUTION:
  the combined verdict may report/stop only; it does not perform severance
```

## Authorized Files

Implementation may touch only:

```text
source/spira_core/combined_verdict.py
source/spira_core/agent_summary.py
source/spira_core/decision_report.py
source/spira_core/trust_cli.py
tests/test_nesira_phase2_combined_verdict_integration.py
tests/test_agent_memory_v0.py
tests/test_unification_proof.py
research/nesira_policy_profile/nesira_phase2_combined_verdict_integration_report.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_integration_results.json
research/nesira_policy_profile/nesira_phase2_combined_verdict_integration_review.md
research/nesira_policy_profile/nesira_phase2_combined_verdict_integration_review_results.json
```

If `pyproject.toml`, `tools/build_spira_trust_public.py`, a workflow, or any
external reproduction manifest must change, stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Required Conformance

Tests must cover:

```text
1. No Nesira input -> existing combined verdict behavior unchanged.
2. Nesira SUFFICIENT + graph OK -> final remains no more permissive than graph OK.
3. Nesira SUFFICIENT + existing BLOCK -> final remains BLOCK.
4. Nesira INSUFFICIENT + graph OK -> final BLOCK / STOP_BLOCKED.
5. Required Nesira NOT_EVALUATED + graph OK -> stop REPORT_NOT_EVALUATED.
6. Missing required Nesira -> NOT_EVALUATED, not pass.
7. Malformed Nesira artifact -> fail closed.
8. Missing PT-ISOLATION-01 on sufficient isolation artifact -> fail closed.
9. Action-looking Nesira artifact -> fail closed.
10. Combined output carries assumptions, trust roots, execution marker, and
    raw Nesira verdict tokens.
```

## Required Verification

Before acceptance:

```text
full pytest passes
V1 SHA256SUMS self-check remains 622/622
public wheel boundary unchanged unless explicitly re-authorized
dependencies=[] remains unchanged
no runner/severance files added
no public claim text expanded
post-change report records the exact behavior matrix
```

## Stop Conditions

Stop immediately if:

```text
Nesira sufficient can override an existing block
Nesira missing/not-evaluated is treated as pass when required
combined output hides NOT_PROVEN assumptions
PT-ISOLATION-01 disappears from a sufficient isolation assessment path
new action vocabulary is introduced
runner/severance behavior appears
implementation requires release/version/public-claim changes
```

## Next Step

If and only if this gate is accepted, a separate human-gated decision may open
discussion of release exposure for the changed combined verdict behavior.

Runner and severance action remain separate future gates.
