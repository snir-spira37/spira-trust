# Nesira Phase 2 Audit Append Runner CAP Assumption Alignment Authorization

## Status

```text
DOCUMENT_TYPE: AUTHORIZATION
PHASE: PHASE_2_AUDIT_APPEND_RUNNER_CAP_ASSUMPTION_ALIGNMENT_GATE
SCOPE: RUNNER_APPLIED_ASSUMPTION_VOCABULARY_ONLY

AUTHORIZES:
replace non-canonical provider assumption prose tokens in private audit append runner applied results
use CAP-* IDs from the capability provider assumption ledger
local tests for CAP-* assumption carriage

DOES_NOT_AUTHORIZE:
runner API change
append decision logic change
additional append calls
provider implementation expansion
public wheel exposure
CLI exposure
version bump
release
generic runner behavior
severance
automatic remediation
```

The private audit append runner predates the CAP assumption ledger and currently
uses prose assumption tokens on applied results. This gate aligns that vocabulary
to the canonical CAP ledger.

## Core Lock

```text
ASSUMPTION_VOCABULARY_ALIGNMENT_IS_NOT_RUNNER_BEHAVIOR_EXPANSION
```

The only allowed change is replacing the runner's applied provider-assumption
tokens with the CAP floor:

```text
CAP-PROVIDER-01
CAP-PROVIDER-02
CAP-PROVIDER-03
CAP-SINK-01
CAP-SINK-02
CAP-IDEMPOTENCY-01
CAP-IDEMPOTENCY-02
CAP-STATUS-01
CAP-TCB-01
```

The runner must still call the append capability at most once, only after all
preconditions pass, and all negative cases must still produce zero append calls.

## Authorized Files

```text
source/spira_core/nesira_phase2_audit_append_runner.py
tests/test_nesira_phase2_audit_append_runner.py
tests/test_nesira_phase2_audit_append_provider.py
research/nesira_policy_profile/nesira_phase2_audit_append_runner_cap_assumption_alignment_authorization.md
research/nesira_policy_profile/nesira_phase2_audit_append_runner_cap_assumption_alignment_authorization_review.md
```

Any runner API change, output field addition beyond assumptions, public wheel
change, CLI change, version bump, release, retry, fallback, or side-effect
expansion must stop with:

```text
SCOPE_REVISION_REQUIRED
```

## Required Verification

```text
runner applied output carries CAP-* floor
provider-backed runner applied output carries CAP-* floor
negative cases still zero append calls
runner source side-effect scan unchanged
public wheel exclusion remains true
full pytest
V1 SHA256SUMS remains 622/622 if unchanged
```

## Verdict

```text
NESIRA_PHASE2_AUDIT_APPEND_RUNNER_CAP_ASSUMPTION_ALIGNMENT_AUTHORIZED
```
