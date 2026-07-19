# Reproduce Nesira Phase 2 Internal Assessment Engine

## Source

```powershell
git clone https://github.com/snir-spira37/spira-trust.git spira-trust-phase2
cd spira-trust-phase2
git checkout 26b560822ca9ad2a518ec74334fe6cc7abb864e5
git status --short
```

The initial status must be clean.

## Adapter Requirements

Use Python 3.12.x. Install the hash-locked adapter dependency:

```powershell
python -m pip install --require-hashes -r requirements/nesira_adapters_win_amd64_cp312.txt
```

Do not add `cryptography` to product dependencies.

## Required Commands

```powershell
python -m compileall source tools tests
python tools/run_nesira_phase2_signature_adapter_conformance.py
python tools/run_nesira_phase2_identity_adapter_conformance.py
python tools/run_nesira_phase2_authority_adapter_conformance.py
python tools/run_nesira_phase2_isolation_attestation_adapter_conformance.py
python tools/run_nesira_phase2_assessment_wiring_conformance.py
python -m pytest tests/test_nesira_phase2_signature_adapter.py tests/test_nesira_phase2_identity_adapter.py tests/test_nesira_phase2_authority_adapter.py tests/test_nesira_phase2_isolation_attestation_adapter.py tests/test_nesira_phase2_assessment_wiring.py tests/test_formal_core_v1_external_reproduction_package.py -q
python -m pytest -q
git diff --check
```

Expected outcomes:

```text
compileall: exit 0
five Phase 2 conformance tools: accepted verdicts
focused adapter/wiring/V1 tests: pass
full pytest: 339 passed
git diff --check: exit 0
```

## Formal Core

With Lean 4.32.0 and Lake 5.0.0 available:

```powershell
cd formal\spira_formal_core_v1
lake build SpiraFormalCorePhase2
```

The Phase 2 composition dump must match
`research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json`
over all 81 rows.

If Lean/Lake is unavailable in the reviewer environment, report that layer as
`NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT`, not `PASS`.

## V1 Boundary

The V1 external reproduction package must remain coherent and V1-scoped:

```text
SHA256SUMS: 622/622 OK
no Phase 2 claims folded into the V1 package
```

## Public Wheel Boundary

Build and inspect the public wheel through the repository public builder. The
Phase 2 adapters, harnesses, wiring, and `cryptography` metadata must be absent.
