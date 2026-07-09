# SPIRA Trust Pilot Readiness Pack

This pack is for a pilot user who wants to run SPIRA Trust without the larger
SPIRA workspace.

## Quick Start

Create a fresh environment and install from production PyPI:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install spira-trust==0.6.0
spira-trust version
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install spira-trust==0.6.0
spira-trust version
```

## Scenario 1: Vendor Wheel Intake

```bash
mkdir spira_out
spira-trust trust ./vendor/some_package.whl --output-dir spira_out
```

`TRUST_OK` means no blocking contradiction was found by the checks that ran.
`TRUST_BLOCK` means a hard contradiction was found, such as broken `RECORD`
integrity or a package-lock/evidence mismatch.

## Scenario 2: Air-Gapped CI Gate

```bash
spira-trust graph ./wheels \
  --output-dir spira_graph_out \
  --sbom cyclonedx-json \
  --verify-embedded-sboms \
  --evidence-pack spira-evidence.zip
```

SPIRA analyzes only the local wheels you explicitly provide. It does not
resolve, fetch, install, or execute dependencies.

## Scenario 3: Baseline Drift

```bash
spira-trust drift ./wheels \
  --baseline ./baseline/bill_of_materials.json \
  --baseline-sha256 <pinned-baseline-sha256> \
  --output-dir spira_drift_out
```

Drift is a fact, not a verdict. It means the current local wheel set no longer
matches the baseline you approved. It does not prove the change is bad.

## Pilot Feedback Questions

Ask the pilot user:

```text
1. Did SPIRA change a decision you would have made about this wheel or wheelhouse?
2. Was the terminal verdict enough, or did you need the JSON?
3. Which command would you put into CI tomorrow?
4. Which finding was useful, noisy, or confusing?
5. What local input do you already trust more: a wheelhouse, a lockfile, or a baseline BOM?
```

The useful outcome is not praise. The useful outcome is whether the evidence
changed an action.
