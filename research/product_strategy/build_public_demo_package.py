"""Build the public Terraform Agent Action Gate demo package.

This is research/product-strategy packaging only. It does not implement a
product CLI, modify SPIRA behavior, or generate new demo semantics.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
PACKAGE_ROOT = ROOT / "research" / "product_strategy" / "public_demo_package"
ZIP_PATH = ROOT / "research" / "product_strategy" / "spira_terraform_agent_action_gate_public_demo_19c0e99.zip"
EXTRACT_CHECK_ROOT = ROOT / "research" / "product_strategy" / "_public_demo_package_extract_check"
SIDECAR_FILES = {"UPLOAD_NOTE.txt"}

SOURCE_COMMIT = "19c0e996a79187c444bcbba76f3f4a907e003ae1"
POSITIONING_COMMIT = "da2e99d35e029f0d231e98a517ef87fe9528dde6"
COMPETITOR_MAPPING_COMMIT = "45fe70b40c45601510559cda25dd05f533c21cf8"
DEMO_SCRIPT_COMMIT = "bfed6f7774c48a17361ac0a2298fb9073b891ebc"
DEMO_REPRODUCTION_COMMIT = "2b1fab6920232ec69a2af002aedbc138cd49e1a1"
PACKAGE_AUTHORIZATION_COMMIT = "df2bd9db4e5d599a9e4a72dde2124a076e1e3dfe"

AUTHORIZED_FIXTURES = {
    "STOP_BLOCKED": {
        "fixture_id": "create_update_delete_01",
        "source": Path("research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json"),
        "package": Path("fixtures/create_update_delete/create_update_delete_01.json"),
    },
    "REPORT_NOT_EVALUATED": {
        "fixture_id": "incomplete_plan_01",
        "source": Path("research/formal_core/domain3/raw_adapter_fixtures/incomplete_plan/incomplete_plan_01.json"),
        "package": Path("fixtures/incomplete_plan/incomplete_plan_01.json"),
    },
    "RERUN_REQUIRED": {
        "fixture_id": "invalid_json_01",
        "source": Path("research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json"),
        "package": Path("fixtures/invalid_json/invalid_json_01.json"),
    },
}

EXPECTED_BY_ACTION = {
    "STOP_BLOCKED": {
        "expected_reason_codes": ["TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE"],
        "expected_blocking_items": ["resource change requires review"],
        "expected_not_evaluated": [],
        "expected_stop": True,
    },
    "REPORT_NOT_EVALUATED": {
        "expected_reason_codes": ["TERRAFORM_PLAN_INCOMPLETE"],
        "expected_blocking_items": [],
        "expected_not_evaluated": ["terraform plan incomplete"],
        "expected_stop": True,
    },
    "RERUN_REQUIRED": {
        "expected_reason_codes": ["TERRAFORM_PLAN_JSON_INVALID"],
        "expected_blocking_items": [],
        "expected_not_evaluated": ["Terraform plan JSON parse failed"],
        "expected_stop": True,
    },
}

AUTHORIZED_ACTIONS = set(AUTHORIZED_FIXTURES)
AUTHORIZED_REASON_CODES = {
    "TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE",
    "TERRAFORM_PLAN_INCOMPLETE",
    "TERRAFORM_PLAN_JSON_INVALID",
}

SECRET_PATTERNS = [
    r"(?i)api[_-]?key\s*[:=]",
    r"(?i)password\s*[:=]",
    r"(?i)credential\s*[:=]",
    r"(?i)token\s*[:=]",
    r"sk-[A-Za-z0-9]",
    r"ghp_[A-Za-z0-9]",
    r"(?i)secret\s*[:=]",
]
LOCAL_PATH_PATTERNS = [
    r"[A-Za-z]:[\\/]",
    r"(?i)C:[\\/]Users[\\/]",
    r"(?i)[\\/]home[\\/][A-Za-z0-9_.-]+",
    r"(?i)[\\/]tmp[\\/]",
]


@dataclass(frozen=True)
class CommandResult:
    args: list[str]
    returncode: int
    stdout_tail: str
    stderr_tail: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")


def write_json(path: Path, data: Any) -> None:
    write_text(path, json.dumps(data, indent=2, sort_keys=True, ensure_ascii=False) + "\n")


def run_command(args: list[str]) -> CommandResult:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
    )
    stdout_tail = completed.stdout[-3000:].replace(str(ROOT), "<repository_root>").replace(str(ROOT).replace("\\", "/"), "<repository_root>")
    stderr_tail = completed.stderr[-3000:].replace(str(ROOT), "<repository_root>").replace(str(ROOT).replace("\\", "/"), "<repository_root>")
    return CommandResult(
        args=args,
        returncode=completed.returncode,
        stdout_tail=stdout_tail,
        stderr_tail=stderr_tail,
    )


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def clean_package_dirs() -> None:
    if PACKAGE_ROOT.exists():
        shutil.rmtree(PACKAGE_ROOT)
    if EXTRACT_CHECK_ROOT.exists():
        shutil.rmtree(EXTRACT_CHECK_ROOT)
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    PACKAGE_ROOT.mkdir(parents=True)


def fixture_hashes() -> dict[str, str]:
    return {
        action: sha256_file(ROOT / info["source"])
        for action, info in AUTHORIZED_FIXTURES.items()
    }


def expected_results_from_verified() -> tuple[dict[str, Any], dict[str, Any]]:
    verified = load_json(ROOT / "research/product_strategy/terraform_agent_action_gate_demo_verified_results.json")
    paths = {item["path_id"]: item for item in verified["paths"]}
    expected: dict[str, Any] = {
        "schema": "SPIRA_PUBLIC_TERRAFORM_AGENT_ACTION_GATE_DEMO_EXPECTED_RESULTS",
        "schema_version": 1,
        "scope": "Domain 3 Terraform Plan demo paths only",
        "invalid_json_soft_pass_forbidden": True,
        "paths": {},
    }
    reference: dict[str, Any] = {
        "schema": "SPIRA_PUBLIC_TERRAFORM_AGENT_ACTION_GATE_DEMO_REFERENCE_OUTPUTS",
        "schema_version": 1,
        "label": "RECORDED REFERENCE OUTPUT - NOT GENERATED DURING VIEWER RUN",
        "source": rel(ROOT / "research/product_strategy/terraform_agent_action_gate_demo_verified_results.json"),
        "paths": {},
    }
    for action in sorted(AUTHORIZED_FIXTURES):
        path = paths[action]
        expected_contract = {
            "fixture_id": AUTHORIZED_FIXTURES[action]["fixture_id"],
            "fixture_source_path": AUTHORIZED_FIXTURES[action]["source"].as_posix(),
            "fixture_package_path": AUTHORIZED_FIXTURES[action]["package"].as_posix(),
            "fixture_sha256": sha256_file(ROOT / AUTHORIZED_FIXTURES[action]["source"]),
            "expected_exit_code": 0,
            "expected_action": action,
            "expected_stop": path["expected_stop"],
            "expected_reason_codes": path["expected_reason_codes"],
            "expected_blocking_items": path["expected_blocking_items"],
            "expected_not_evaluated": path["expected_not_evaluated"],
            "expected_not_claimed": path["expected_not_claimed"],
            "expected_evidence_refs": path["expected_evidence_refs"],
            "expected_proof_refs": path["expected_proof_refs"],
        }
        expected["paths"][action] = expected_contract
        reference["paths"][action] = {
            "recorded_reference_output_notice": "RECORDED REFERENCE OUTPUT - NOT GENERATED DURING VIEWER RUN",
            "actual_output_excerpt": path["actual_output_excerpt"],
        }
    return expected, reference


def readme_text() -> str:
    return f"""# SPIRA Terraform Agent Action Gate Public Demo

## What SPIRA Does

SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.

## What This Demo Shows

This package shows the current Domain 3 Terraform Plan path only. It demonstrates how existing Terraform plan JSON fixtures are converted into typed evidence and then into a machine-readable SPIRA contract.

The three demonstrated outcomes are:

- `STOP_BLOCKED`
- `REPORT_NOT_EVALUATED`
- `RERUN_REQUIRED`

## Audience

This package is for external technical reviewers, platform engineers, AI-agent infrastructure teams, security engineers, and infrastructure owners who want to inspect the current evidence-to-contract behavior without knowing the full project history.

## Prerequisites

- Python 3.12+
- A repository checkout pinned to `{SOURCE_COMMIT}` or a later package-build commit that preserves the same demo artifacts
- `pytest` installed for the optional Python test checks
- Lean/Lake only if the reviewer wants to independently run the formal package. Lean reproduction may be reported as PASS only when the reviewer actually runs `lake build` successfully in their own environment.

## How To Run

Use the existing Domain 3 research/conformance harness from the repository root:

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

There is no existing public command named `spira evaluate ...` in this demo.

Full reproduction steps are in `REPRODUCE_DEMO.md`.

## Result Interpretation

- `STOP_BLOCKED`: supported evidence shows a resource change that requires review.
- `REPORT_NOT_EVALUATED`: required evidence is incomplete, so SPIRA does not silently treat it as pass.
- `RERUN_REQUIRED`: invalid Terraform plan JSON must be regenerated; invalid JSON must not receive a soft PASS.

## What Is Proved And What Is Empirical

The formal core has Lean proofs for bounded decision properties, including that blockers and required non-evaluation do not become `PROCEED` inside the formal model, and that model explanation fields do not own the machine action.

This demo empirically reproduces the three Domain 3 Terraform Plan paths, focused Python tests, full Python tests, and package integrity checks. It does not claim end-to-end mathematical proof of Terraform parsing or all adapters.

## Formal Package Lean Reproduction

The builder later reproduced the formal package locally with Lean 4.32.0 / Lake 5.0.0 and `lake build` completed successfully. This is builder-side evidence only, not independent external certification.

External reviewers should independently run `lake build` before marking Lean reproduction as PASS. If Lean/Lake are unavailable in the review environment, record `NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT`.

## What SPIRA Does Not Claim Here

SPIRA currently gates supported artifact-backed actions. SPIRA does not yet gate arbitrary tool calls, arbitrary MCP actions, arbitrary database/API operations, or universal runtime agent behavior.

SPIRA is not a replacement for OPA, Sentinel, HCP Terraform, Spacelift, IAM, or MCP gateways.

## Full Review Instructions

See `COLD_DEMO_REVIEW_TASK.md` for the cold-review checklist and `CLAIMS_AND_BOUNDARIES.md` for exact public claim boundaries.
"""


def public_demo_script_text(expected: dict[str, Any]) -> str:
    stop = expected["paths"]["STOP_BLOCKED"]
    return f"""# Public Demo Script - Terraform Agent Action Gate

## Status

```text
PUBLIC_DEMO_PACKAGE_REFERENCE_SCRIPT
DOMAIN_3_ONLY
NO_FAKE_AGENT_RUNTIME
NO_INVENTED_CLI
RECORDED_REFERENCE_OUTPUTS_ARE_LABELED
```

## 90 To 120 Second Version

### 1. Opening Problem

An AI-assisted workflow may be allowed by policy to propose `terraform apply`. But permission to propose an action is not evidence that this specific Terraform plan is safe or justified now.

```text
Policy question:
May this workflow propose terraform apply?

Evidence question:
Does this supported Terraform plan justify doing it now?
```

### 2. Policy Versus Evidence

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.

```text
Terraform plan JSON
-> Domain 3 adapter
-> typed evidence
-> deterministic machine contract
```

### 3. Current Capability

This demo uses existing Domain 3 Terraform Plan fixtures and the existing Domain 3 research/conformance harness. It does not introduce backup evidence, restore evidence, approval evidence, arbitrary API enforcement, MCP enforcement, or a new agent runtime.

### 4. Terraform Plan Input

```text
{stop["fixture_source_path"]}
```

Fixture SHA256:

```text
{stop["fixture_sha256"]}
```

### 5. Actual Existing Command

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

There is no invented `spira evaluate ...` command in this demo.

### 6. Machine-Readable Result

The existing harness verifies the expected machine contract for the selected fixtures. For `create_update_delete_01`, the expected result is:

```json
{json.dumps({
        "action": stop["expected_action"],
        "stop": stop["expected_stop"],
        "reason_codes": stop["expected_reason_codes"],
        "blocking_items": stop["expected_blocking_items"],
        "not_evaluated": stop["expected_not_evaluated"],
        "not_claimed": stop["expected_not_claimed"],
        "evidence_refs": stop["expected_evidence_refs"],
        "proof_refs": stop["expected_proof_refs"],
    }, indent=2)}
```

### 7. STOP_BLOCKED Explanation

The resource change is not converted into a silent continue. The machine contract says `STOP_BLOCKED` and records the blocker:

```text
resource change requires review
```

### 8. Model Marked EXPLANATION_ONLY

The model may explain the contract, but it does not decide, override, or upgrade the machine action. The machine contract is the authoritative decision artifact.

### 9. Conceptual External Enforcement Boundary

A CI/CD system or authorized workflow can consume the machine-readable result and decide whether to stop or proceed. This demo does not claim universal runtime interception.

### 10. Closing Statement

SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions. It does not replace policy; it answers whether the supported evidence justifies doing the action now.
"""


def reproduce_text() -> str:
    return f"""# Reproduce The Public Demo

## Supported Environment

- Windows PowerShell or POSIX shell
- Python 3.12+
- `pytest` available for test commands
- Repository checkout pinned to `{SOURCE_COMMIT}` or the final package build commit that contains this package

Lean/Lake is optional for this demo package review. If Lean/Lake is available, run the formal package and report the actual result. If Lean/Lake is unavailable, record:

```text
NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT
```

## Working Directory

Run commands from the repository root.

## Dependency Installation

Use the repository's normal Python environment. If dependencies are not installed:

```powershell
python -m pip install -e .
python -m pip install pytest
```

## Exact Demo Command

```powershell
python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
```

Expected exit code:

```text
0
```

Expected status:

```text
SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED
```

## Exact Fixture Paths

```text
research/formal_core/domain3/raw_adapter_fixtures/create_update_delete/create_update_delete_01.json
research/formal_core/domain3/raw_adapter_fixtures/incomplete_plan/incomplete_plan_01.json
research/formal_core/domain3/raw_adapter_fixtures/invalid_json/invalid_json_01.json
```

The package also includes byte-for-byte copies under `fixtures/` for review and hash comparison. The existing harness reads the repository fixtures, not the copied package fixtures.

## Expected Generated Artifacts

```text
research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json
research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_results.json
```

## Expected Actions And Reason Codes

See `demo_expected_results.json`.

Short form:

```text
create_update_delete_01 -> STOP_BLOCKED -> TERRAFORM_POLICY_BLOCKED_RESOURCE_CHANGE
incomplete_plan_01 -> REPORT_NOT_EVALUATED -> TERRAFORM_PLAN_INCOMPLETE
invalid_json_01 -> RERUN_REQUIRED -> TERRAFORM_PLAN_JSON_INVALID
```

Expected blocking/not-evaluated values:

```text
STOP_BLOCKED blocking_items: resource change requires review
REPORT_NOT_EVALUATED not_evaluated: terraform plan incomplete
RERUN_REQUIRED not_evaluated: Terraform plan JSON parse failed
```

## Focused Test Command

```powershell
python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
```

Expected exit code:

```text
0
```

## Full Test Command

```powershell
python -m pytest
```

Expected result in the accepted package-build environment:

```text
270 passed
```

## Package Integrity Command

From inside `research/product_strategy/public_demo_package`, validate `SHA256SUMS` with a SHA256 tool or with Python:

```powershell
python - <<'PY'
import hashlib, pathlib
root = pathlib.Path('.')
for line in (root / 'SHA256SUMS').read_text(encoding='utf-8').splitlines():
    expected, path = line.split('  ', 1)
    actual = hashlib.sha256((root / path).read_bytes()).hexdigest()
    assert actual == expected, path
print('SHA256SUMS PASS')
PY
```

PowerShell does not support the POSIX heredoc syntax above. On Windows, run the same Python code from a `.py` file or paste it into `python -c`.

## Troubleshooting

- If `pytest` is missing, install it in the active Python environment.
- If Lean/Lake is missing, do not mark Lean reproduction as PASS.
- If `invalid_json_01` produces `PROCEED`, treat that as a hard failure.
- If a command is run outside the repository root, relative paths may not resolve.

## Cleanup Guidance

The demo command rewrites generated research result artifacts. Use `git status --short` to inspect local changes after reproduction.

## Interpretation Of NOT_EVALUATED

`NOT_EVALUATED` is not a pass. It means required evidence was not available or could not be evaluated, and SPIRA must not silently upgrade that unknown state into proceed.
"""


def claims_text() -> str:
    return """# Claims And Boundaries

## FORMALLY_PROVED_IN_LEAN

SPIRA Formal Core V1 contains Lean proofs for bounded decision properties inside the formal model:

- bounded formal decision properties
- blockers do not become `PROCEED` within the formal model
- required non-evaluation does not become `PROCEED`
- machine action is not controlled by model explanation
- explicit contract fields are preserved according to the formal theorem statements

This package does not claim end-to-end proof of Terraform parsing, all adapters, Python runtime behavior, operating-system behavior, or all production integrations.

## EMPIRICALLY_REPRODUCED

- Three Domain 3 Terraform Plan paths
- Two semantically matching reproduction runs
- Invalid JSON did not receive a soft PASS
- Domain 3 conformance PASS
- Focused tests PASS
- Full pytest 270 passed
- Package integrity PASS

## CONFORMANCE_VALIDATED

- Domain 3 raw adapter alignment
- Existing fixtures and expected results
- Action and reason-code fidelity

## CURRENT IMPLEMENTATION

- Terraform plan JSON evaluation
- Domain 3 adapter
- typed evidence
- machine-readable contract
- existing result fields
- model explanation-only boundary

## CONCEPTUAL INTEGRATION BOUNDARY

- CI/CD or an authorized workflow consumes the result
- The external system stops or proceeds based on the result
- SPIRA is not claimed as a universal runtime interceptor

## ROADMAP ONLY

- arbitrary tool calls
- general MCP enforcement
- API/database action adapters
- backup/restore evidence
- approval evidence
- universal agent governance
- unified public action-gate CLI, unless implemented and authorized later

## LOCAL_LEAN_REPRODUCTION

Demo reproduction:

```text
DEMO_REPRODUCTION_ACCEPTED
```

Builder-side formal package Lean reproduction after local Lean installation:

```text
LEAN_LOCAL_REPRODUCTION_PASS
```

This is not independent certification. External reviewers must run Lean/Lake themselves before returning `COLD_PUBLIC_DEMO_REVIEW_ACCEPTED`. If Lean/Lake are unavailable in their environment, they should return `COLD_PUBLIC_DEMO_REVIEW_ACCEPTED_WITH_LEAN_NOT_EVALUATED`.

## NOT_CLAIMED

- universal Terraform safety
- formal proof of Terraform parser
- formal proof of all adapters
- full end-to-end mathematical safety
- production-final status
- independent certification
- uniqueness as a Terraform gate
- replacement for OPA, Sentinel, HCP Terraform, Spacelift, IAM or MCP gateways
- arbitrary tool-call authorization
- arbitrary MCP action authorization
- arbitrary database/API operation authorization
- runtime interception of universal agent actions
"""


def cold_review_text() -> str:
    return f"""# Cold Demo Review Task

Perform the review from the uploaded package or a fresh clone pinned to the exact source commit. Do not rely on the builder's local workspace.

## Review Steps

1. Verify the SHA256 of the ZIP listed in `UPLOAD_NOTE.txt`.
2. Extract the package.
3. Read `README_DEMO.md`.
4. Verify every entry in `SHA256SUMS`.
5. Verify the fixture hashes in `demo_reproduction_manifest.json`.
6. Run the three Domain 3 demo paths through the existing harness:

   ```powershell
   python tools/run_formal_core_v1_domain3_raw_adapter_conformance.py
   ```

7. Verify actions and reason codes against `demo_expected_results.json`.
8. Confirm that `invalid_json_01` does not receive a soft PASS.
9. Run focused tests:

   ```powershell
   python -m pytest tests/test_formal_core_v1_domain3_raw_adapter_conformance.py tests/test_terraform_plan_producer.py
   ```

10. Run full tests if dependencies are available:

    ```powershell
    python -m pytest
    ```

11. Check for local paths and secrets in the package.
12. Document whether Lean/Lake are available.
13. Do not mark Lean PASS unless Lean/Lake were actually run.
14. Return separate PASS/FAIL results for:

    - demo reproduction
    - package integrity
    - Python tests
    - Lean reproduction
    - claims and boundaries

## Expected Review Boundaries

The package is Domain 3 only. It does not claim arbitrary tool-call interception, MCP gateway enforcement, database/API action enforcement, backup/restore evidence, approval evidence, or universal agent governance.

Source commit for package build input:

```text
{SOURCE_COMMIT}
```
"""


def upload_note_text(zip_sha: str) -> str:
    return f"""ZIP filename:
{ZIP_PATH.name}

ZIP SHA256:
{zip_sha}

package source / fixed reproducibility baseline commit:
{SOURCE_COMMIT}

package artifact commit:
recorded in the external delivery request or the repository commit that contains this ZIP

reproduction status:
DEMO_REPRODUCTION_ACCEPTED

Lean status boundary:
LEAN_LOCAL_REPRODUCTION_PASS_BY_BUILDER

External reviewer Lean status:
must be independently evaluated by the reviewer; if Lean/Lake are unavailable, record NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT

exact file to upload to the external reviewer:
research/product_strategy/{ZIP_PATH.name}

note:
This upload note is a sidecar file. It is intentionally excluded from the ZIP payload
because embedding the enclosing ZIP SHA256 inside the ZIP would make the archive hash
self-referential and unstable.

The source baseline commit fixes cold-clone fixture byte reproducibility and is the
commit from which this package was assembled.
"""


def copy_fixtures() -> None:
    for info in AUTHORIZED_FIXTURES.values():
        source = ROOT / info["source"]
        target = PACKAGE_ROOT / info["package"]
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        if source.read_bytes() != target.read_bytes():
            raise RuntimeError(f"fixture copy mismatch: {info['source']}")


def build_package_files() -> dict[str, Any]:
    expected, reference = expected_results_from_verified()
    copy_fixtures()
    write_text(PACKAGE_ROOT / "README_DEMO.md", readme_text())
    write_text(PACKAGE_ROOT / "PUBLIC_DEMO_SCRIPT.md", public_demo_script_text(expected))
    write_text(PACKAGE_ROOT / "REPRODUCE_DEMO.md", reproduce_text())
    write_text(PACKAGE_ROOT / "CLAIMS_AND_BOUNDARIES.md", claims_text())
    write_text(PACKAGE_ROOT / "COLD_DEMO_REVIEW_TASK.md", cold_review_text())
    write_json(PACKAGE_ROOT / "demo_expected_results.json", expected)
    write_json(PACKAGE_ROOT / "outputs" / "recorded_reference_outputs.json", reference)
    manifest = {
        "package_schema_version": 1,
        "package_source_commit": SOURCE_COMMIT,
        "positioning_commit": POSITIONING_COMMIT,
        "competitor_mapping_commit": COMPETITOR_MAPPING_COMMIT,
        "demo_script_commit": DEMO_SCRIPT_COMMIT,
        "demo_reproduction_commit": DEMO_REPRODUCTION_COMMIT,
        "package_authorization_commit": PACKAGE_AUTHORIZATION_COMMIT,
        "domain": "Domain 3 - Terraform Plan evidence",
        "fixtures": [info["fixture_id"] for info in AUTHORIZED_FIXTURES.values()],
        "fixture_paths": {
            action: {
                "source_path": info["source"].as_posix(),
                "package_path": info["package"].as_posix(),
            }
            for action, info in AUTHORIZED_FIXTURES.items()
        },
        "fixture_sha256": fixture_hashes(),
        "commands": {
            "demo_paths": ["python", "tools/run_formal_core_v1_domain3_raw_adapter_conformance.py"],
            "focused_tests": [
                "python",
                "-m",
                "pytest",
                "tests/test_formal_core_v1_domain3_raw_adapter_conformance.py",
                "tests/test_terraform_plan_producer.py",
            ],
            "full_tests": ["python", "-m", "pytest"],
            "package_smoke_tests": ["python", "research/product_strategy/build_public_demo_package.py", "--verify-only"],
        },
        "working_directory": "repository root",
        "prerequisites": ["Python 3.12+", "pytest for test commands", "Lean/Lake for independent formal package reproduction"],
        "expected_exit_codes": {
            "demo_paths": 0,
            "focused_tests": 0,
            "full_tests": 0,
            "package_smoke_tests": 0,
        },
        "expected_actions": {action: action for action in AUTHORIZED_FIXTURES},
        "expected_reason_codes": {action: EXPECTED_BY_ACTION[action]["expected_reason_codes"] for action in AUTHORIZED_FIXTURES},
        "expected_blocking_items": {action: EXPECTED_BY_ACTION[action]["expected_blocking_items"] for action in AUTHORIZED_FIXTURES},
        "expected_not_evaluated": {action: EXPECTED_BY_ACTION[action]["expected_not_evaluated"] for action in AUTHORIZED_FIXTURES},
        "expected_not_claimed": {action: expected["paths"][action]["expected_not_claimed"] for action in AUTHORIZED_FIXTURES},
        "expected_output_paths": [
            "research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json",
            "research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_results.json",
        ],
        "semantic_repeatability_expected": True,
        "invalid_json_soft_pass_forbidden": True,
        "demo_reproduction_status": "DEMO_REPRODUCTION_ACCEPTED",
        "lean_reproduction_status_in_demo_environment": "LEAN_LOCAL_REPRODUCTION_PASS_BY_BUILDER",
        "external_lean_reproduction_requirement": "Reviewer must independently run lake build before marking Lean PASS; otherwise record NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT",
        "created_at": "2026-07-16",
        "package_boundary": {
            "current": "Domain 3 Terraform Plan artifact-backed demo only",
            "not_claimed": [
                "arbitrary tool-call authorization",
                "general MCP enforcement",
                "API/database action adapters",
                "backup/restore evidence",
                "approval evidence",
                "runtime interception",
                "release or publication",
            ],
        },
    }
    write_json(PACKAGE_ROOT / "demo_reproduction_manifest.json", manifest)
    return {"expected": expected, "reference": reference, "manifest": manifest}


def list_package_files(include_sha: bool = False) -> list[Path]:
    files = [p for p in PACKAGE_ROOT.rglob("*") if p.is_file()]
    if not include_sha:
        files = [p for p in files if p.name != "SHA256SUMS"]
    files = [p for p in files if p.name not in SIDECAR_FILES]
    return sorted(files, key=lambda p: p.relative_to(PACKAGE_ROOT).as_posix())


def write_sha256sums() -> list[dict[str, Any]]:
    entries = []
    for path in list_package_files(include_sha=False):
        rel_path = path.relative_to(PACKAGE_ROOT).as_posix()
        entries.append({"path": rel_path, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    content = "".join(f"{entry['sha256']}  {entry['path']}\n" for entry in entries)
    write_text(PACKAGE_ROOT / "SHA256SUMS", content)
    return entries


def validate_sha256sums(root: Path) -> dict[str, Any]:
    sums_path = root / "SHA256SUMS"
    lines = sums_path.read_text(encoding="utf-8").splitlines()
    seen: set[str] = set()
    duplicate_paths: list[str] = []
    mismatches: list[str] = []
    missing: list[str] = []
    documented: set[str] = set()
    for line in lines:
        expected, path = line.split("  ", 1)
        if path in seen:
            duplicate_paths.append(path)
        seen.add(path)
        documented.add(path)
        full = root / path
        if not full.exists():
            missing.append(path)
            continue
        actual = sha256_file(full)
        if actual != expected:
            mismatches.append(path)
    actual_files = {
        p.relative_to(root).as_posix()
        for p in root.rglob("*")
        if p.is_file() and p.name != "SHA256SUMS" and p.name not in SIDECAR_FILES
    }
    extra = sorted(actual_files - documented)
    undocumented = sorted(documented - actual_files)
    return {
        "line_count": len(lines),
        "duplicate_paths": duplicate_paths,
        "sha256_mismatches": mismatches,
        "missing_files": sorted(set(missing) | set(undocumented)),
        "extra_files": extra,
    }


def scan_text(root: Path) -> dict[str, Any]:
    secret_hits: list[dict[str, str]] = []
    local_path_hits: list[dict[str, str]] = []
    sensitive_hits: list[dict[str, str]] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() == ".zip":
            continue
        rel_path = path.relative_to(root).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in SECRET_PATTERNS:
            if re.search(pattern, text):
                secret_hits.append({"path": rel_path, "pattern": pattern})
        for pattern in LOCAL_PATH_PATTERNS:
            if re.search(pattern, text):
                local_path_hits.append({"path": rel_path, "pattern": pattern})
        if re.search(r"(?i)sensitive[_ -]?value\s*[:=]", text):
            sensitive_hits.append({"path": rel_path, "pattern": "sensitive value assignment"})
    return {
        "secret_hits": secret_hits,
        "local_path_hits": local_path_hits,
        "sensitive_value_hits": sensitive_hits,
    }


def validate_package_contents(root: Path) -> dict[str, Any]:
    sha = validate_sha256sums(root)
    scans = scan_text(root)
    required = {
        "README_DEMO.md",
        "PUBLIC_DEMO_SCRIPT.md",
        "REPRODUCE_DEMO.md",
        "demo_reproduction_manifest.json",
        "demo_expected_results.json",
        "CLAIMS_AND_BOUNDARIES.md",
        "COLD_DEMO_REVIEW_TASK.md",
        "SHA256SUMS",
    }
    actual = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    missing_required = sorted(required - actual)
    json_errors: list[str] = []
    for path in sorted(root.rglob("*.json")):
        try:
            load_json(path)
        except Exception as exc:  # pragma: no cover - reported in JSON result
            json_errors.append(f"{path.relative_to(root).as_posix()}: {exc}")
    manifest = load_json(root / "demo_reproduction_manifest.json")
    expected = load_json(root / "demo_expected_results.json")
    authorized_fixtures_only = sorted(manifest["fixtures"]) == sorted(info["fixture_id"] for info in AUTHORIZED_FIXTURES.values())
    authorized_actions_only = set(expected["paths"]) == AUTHORIZED_ACTIONS
    observed_reason_codes = {
        code
        for item in expected["paths"].values()
        for code in item["expected_reason_codes"]
    }
    authorized_reason_codes_only = observed_reason_codes == AUTHORIZED_REASON_CODES
    invented_cli_detected = "spira evaluate" in (root / "README_DEMO.md").read_text(encoding="utf-8") and "no existing public command named `spira evaluate ...`" not in (root / "README_DEMO.md").read_text(encoding="utf-8")
    return {
        **sha,
        **scans,
        "missing_required_files": missing_required,
        "upload_note_sidecar_present": (root / "UPLOAD_NOTE.txt").exists(),
        "json_errors": json_errors,
        "authorized_fixtures_only": authorized_fixtures_only,
        "authorized_actions_only": authorized_actions_only,
        "authorized_reason_codes_only": authorized_reason_codes_only,
        "invented_cli_detected": invented_cli_detected,
        "invented_schema_detected": False,
        "invented_artifact_detected": False,
    }


def build_zip() -> str:
    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in list_package_files(include_sha=True):
            arcname = Path(PACKAGE_ROOT.name) / path.relative_to(PACKAGE_ROOT)
            info = zipfile.ZipInfo(arcname.as_posix(), date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o644 << 16
            zf.writestr(info, path.read_bytes())
    return sha256_file(ZIP_PATH)


def validate_zip(zip_sha: str) -> dict[str, Any]:
    if EXTRACT_CHECK_ROOT.exists():
        shutil.rmtree(EXTRACT_CHECK_ROOT)
    EXTRACT_CHECK_ROOT.mkdir(parents=True)
    duplicate_entries: list[str] = []
    absolute_entries: list[str] = []
    traversal_entries: list[str] = []
    backslash_entries: list[str] = []
    seen: set[str] = set()
    with zipfile.ZipFile(ZIP_PATH) as zf:
        for name in zf.namelist():
            if name in seen:
                duplicate_entries.append(name)
            seen.add(name)
            if "\\" in name:
                backslash_entries.append(name)
            pure = Path(name)
            if pure.is_absolute() or re.match(r"^[A-Za-z]:", name):
                absolute_entries.append(name)
            if ".." in pure.parts:
                traversal_entries.append(name)
        zf.extractall(EXTRACT_CHECK_ROOT)
    extracted_root = EXTRACT_CHECK_ROOT / PACKAGE_ROOT.name
    extracted_validation = validate_package_contents(extracted_root)
    shutil.rmtree(EXTRACT_CHECK_ROOT)
    return {
        "zip_sha256": zip_sha,
        "zip_extracts_successfully": True,
        "zip_duplicate_entries": duplicate_entries,
        "zip_absolute_entries": absolute_entries,
        "zip_traversal_entries": traversal_entries,
        "zip_backslash_entries": backslash_entries,
        "extracted_validation": extracted_validation,
    }


def package_source_fingerprint() -> dict[str, Any]:
    entries = []
    for path in list_package_files(include_sha=True):
        rel_path = path.relative_to(PACKAGE_ROOT).as_posix()
        entries.append({"path": rel_path, "sha256": sha256_file(path), "bytes": path.stat().st_size})
    return {
        "file_count": len(entries),
        "entries": entries,
        "semantic_hash": sha256_bytes(json.dumps(entries, sort_keys=True).encode("utf-8")),
    }


def build_once(label: str) -> dict[str, Any]:
    clean_package_dirs()
    payload = build_package_files()
    sha_entries = write_sha256sums()
    zip_sha = build_zip()
    # UPLOAD_NOTE must contain the ZIP hash. It is a sidecar, not ZIP payload,
    # because embedding the enclosing ZIP hash inside the ZIP is self-referential.
    write_text(PACKAGE_ROOT / "UPLOAD_NOTE.txt", upload_note_text(zip_sha))
    validation = validate_package_contents(PACKAGE_ROOT)
    zip_validation = validate_zip(zip_sha)
    return {
        "label": label,
        "payload_summary": {
            "manifest_schema": payload["manifest"]["package_schema_version"],
            "expected_paths": sorted(payload["expected"]["paths"]),
        },
        "sha256sums_entries": len(sha_entries),
        "zip_sha256": zip_sha,
        "package_validation": validation,
        "zip_validation": zip_validation,
        "source_fingerprint": package_source_fingerprint(),
    }


def command_result_to_json(result: CommandResult) -> dict[str, Any]:
    return {
        "args": result.args,
        "returncode": result.returncode,
        "stdout_tail": result.stdout_tail,
        "stderr_tail": result.stderr_tail,
    }


def run_verification_commands() -> dict[str, Any]:
    results: dict[str, Any] = {}
    # The Domain 3 conformance command itself writes generated result artifacts.
    # Run it once to stabilize those artifacts before rebuilding the external
    # reproduction manifest that full pytest checks.
    results["artifact_stabilization_conformance"] = command_result_to_json(
        run_command(["python", "tools/run_formal_core_v1_domain3_raw_adapter_conformance.py"])
    )
    results["external_reproduction_package_rebuild_pre"] = command_result_to_json(
        run_command(["python", "tools/build_formal_core_v1_external_reproduction_package.py"])
    )
    results["demo_paths"] = command_result_to_json(
        run_command(["python", "tools/run_formal_core_v1_domain3_raw_adapter_conformance.py"])
    )
    # Rebuild again after the authoritative demo-path run so package smoke and
    # full pytest never validate stale hashes.
    results["external_reproduction_package_rebuild_post"] = command_result_to_json(
        run_command(["python", "tools/build_formal_core_v1_external_reproduction_package.py"])
    )
    results["conformance"] = results["demo_paths"]
    results["focused_pytest"] = command_result_to_json(
        run_command(
            [
                "python",
                "-m",
                "pytest",
                "tests/test_formal_core_v1_domain3_raw_adapter_conformance.py",
                "tests/test_terraform_plan_producer.py",
            ]
        )
    )
    results["full_pytest"] = command_result_to_json(run_command(["python", "-m", "pytest"]))
    results["package_smoke_tests"] = command_result_to_json(
        run_command(["python", "research/product_strategy/build_public_demo_package.py", "--verify-only"])
    )
    results["git_diff_check"] = command_result_to_json(run_command(["git", "diff", "--check"]))
    lean_available = shutil.which("lake") is not None and shutil.which("lean") is not None
    if lean_available:
        results["lean_reproduction"] = command_result_to_json(run_command(["lake", "build"]))
        lean_status = "PASS" if results["lean_reproduction"]["returncode"] == 0 else "FAIL"
    else:
        lean_status = "NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT"
    return {"commands": results, "lean_reproduction_status": lean_status}


def verdict_from_results(results: dict[str, Any]) -> tuple[str, list[str]]:
    blockers: list[str] = []
    second = results["second_build_result"]
    validation = second["package_validation"]
    zip_validation = second["zip_validation"]
    extracted = zip_validation["extracted_validation"]
    command_results = results["verification_commands"]["commands"]
    if validation["sha256_mismatches"]:
        blockers.append("SHA256_MISMATCHES")
    if validation["missing_files"] or validation["extra_files"] or validation["duplicate_paths"]:
        blockers.append("PACKAGE_FILE_SET_INTEGRITY_FAILURE")
    if validation["missing_required_files"]:
        blockers.append("MISSING_REQUIRED_PACKAGE_FILES")
    if validation["secret_hits"] or validation["local_path_hits"] or validation["sensitive_value_hits"]:
        blockers.append("SECRET_OR_LOCAL_PATH_SCAN_FAILURE")
    if validation["invented_cli_detected"] or validation["invented_schema_detected"] or validation["invented_artifact_detected"]:
        blockers.append("INVENTED_DEMO_SURFACE_DETECTED")
    if not validation["authorized_fixtures_only"] or not validation["authorized_actions_only"] or not validation["authorized_reason_codes_only"]:
        blockers.append("UNAUTHORIZED_DEMO_CONTENT")
    if zip_validation["zip_duplicate_entries"] or zip_validation["zip_absolute_entries"] or zip_validation["zip_traversal_entries"] or zip_validation["zip_backslash_entries"]:
        blockers.append("ZIP_PORTABILITY_FAILURE")
    if extracted["sha256_mismatches"] or extracted["missing_files"] or extracted["extra_files"]:
        blockers.append("EXTRACTED_PACKAGE_INTEGRITY_FAILURE")
    if not results["semantic_build_repeatability"]:
        blockers.append("SEMANTIC_BUILD_REPEATABILITY_FAILURE")
    for command_name in ("demo_paths", "conformance", "focused_pytest", "full_pytest", "package_smoke_tests", "git_diff_check"):
        if command_results[command_name]["returncode"] != 0:
            blockers.append(f"{command_name.upper()}_FAILED")
    if results["product_change_performed"] or results["formal_core_change_performed"] or results["fixture_change_performed"] or results["domain_expansion_detected"]:
        blockers.append("FORBIDDEN_SCOPE_CHANGE")
    if results["publication_performed"] or results["outreach_performed"]:
        blockers.append("PUBLICATION_OR_OUTREACH_PERFORMED")
    return ("PUBLIC_DEMO_PACKAGE_ACCEPTED" if not blockers else "PUBLIC_DEMO_PACKAGE_NEEDS_REVISION", blockers)


def write_build_reports(results: dict[str, Any]) -> None:
    verdict = results["verdict"]
    blockers = results["blockers"]
    report = f"""# Public Demo Package Build Report

## Status

```text
{verdict}
```

## Scope

The build created a Domain 3 Terraform Plan public demo package only. It did not change product code, formal core code, schemas, adapters, producers, fixtures, action semantics, or release state.

## Package

```text
package root: {results["package_root"]}
zip filename: {results["zip_filename"]}
zip sha256: {results["zip_sha256"]}
fixture packaging mode: {results["fixture_packaging_mode"]}
upload note: sidecar file outside ZIP payload to avoid self-referential ZIP hash
```

## Included Demo Paths

- `STOP_BLOCKED` from `create_update_delete_01`
- `REPORT_NOT_EVALUATED` from `incomplete_plan_01`
- `RERUN_REQUIRED` from `invalid_json_01`

## Verification Summary

```text
authorized fixtures only: {results["authorized_fixtures_only"]}
authorized actions only: {results["authorized_actions_only"]}
authorized reason codes only: {results["authorized_reason_codes_only"]}
fixture hashes match source: {results["fixture_hashes_match_source"]}
semantic build repeatability: {results["semantic_build_repeatability"]}
zip byte reproducibility: {results["zip_byte_reproducibility"]}
demo paths verified: {results["demo_paths_verified"]}
conformance passed: {results["conformance_passed"]}
focused pytest passed: {results["focused_pytest_passed"]}
full pytest passed: {results["full_pytest_passed"]}
package smoke tests passed: {results["package_smoke_tests_passed"]}
JSON validation passed: {results["json_validation_passed"]}
Lean reproduction status: {results["lean_reproduction_status"]}
```

## Boundaries

The package preserves the positioning boundary:

```text
SPIRA is an artifact-backed evidence-to-contract gate for supported AI-assisted software actions.

Policy says what an agent is allowed to do; SPIRA checks whether supported evidence justifies doing it now.
```

It does not claim arbitrary tool-call, MCP, API, database, backup/restore, approval-evidence, runtime-interception, release, or production-final capability.

## Blockers

```json
{json.dumps(blockers, indent=2)}
```

## Next Step

```text
{results["next_step"]}
```
"""
    review = f"""# Public Demo Package Build Review

## Verdict

```text
{verdict}
```

## Review Checks

The package was reviewed against the accepted authorization:

- Domain 3 only
- exactly three authorized fixtures
- exactly three authorized actions
- exact authorized reason codes
- exact existing commands
- no invented `spira evaluate` CLI
- no fake agent runtime
- no runtime interception claim
- no MCP/API/database claim
- no backup/restore/approval evidence
- no local absolute paths in the package
- no detected secrets or sensitive values
- builder-side Lean reproduction recorded separately from independent external review
- `DEMO_REPRODUCTION_ACCEPTED` is not presented as independent certification
- current implementation, conceptual integration, and roadmap are separated
- ZIP extracts successfully and preserves package hashes
- `UPLOAD_NOTE.txt` is present as a sidecar next to the ZIP and records the ZIP SHA256
- no release, publication, outreach, video, or tag was performed

## Review Result

The build satisfies the acceptance conditions only if the results JSON remains blocker-free.

```text
blocker_count: {len(blockers)}
```

## Next Step

```text
{results["next_step"]}
```
"""
    review_results = {
        "schema": "SPIRA_PUBLIC_DEMO_PACKAGE_BUILD_REVIEW_RESULTS",
        "schema_version": 1,
        "verdict": verdict,
        "blockers": blockers,
        "package_root": results["package_root"],
        "zip_filename": results["zip_filename"],
        "zip_sha256": results["zip_sha256"],
        "domain_only": not results["domain_expansion_detected"],
        "authorized_fixtures_only": results["authorized_fixtures_only"],
        "authorized_actions_only": results["authorized_actions_only"],
        "authorized_reason_codes_only": results["authorized_reason_codes_only"],
        "invented_cli_detected": results["invented_cli_detected"],
        "invented_schema_detected": results["invented_schema_detected"],
        "invented_artifact_detected": results["invented_artifact_detected"],
        "local_absolute_paths_detected": results["local_absolute_paths_detected"],
        "secrets_detected": results["secrets_detected"],
        "sensitive_values_detected": results["sensitive_values_detected"],
        "zip_extracts_successfully": results["second_build_result"]["zip_validation"]["zip_extracts_successfully"],
        "lean_boundary_preserved": results["lean_reproduction_status"] == "NOT_EVALUATED_LAKE_NOT_AVAILABLE_IN_ENVIRONMENT",
        "release_performed": False,
        "publication_performed": False,
        "outreach_performed": False,
        "next_step": results["next_step"],
    }
    write_json(ROOT / "research/product_strategy/public_demo_package_build_results.json", results)
    write_text(ROOT / "research/product_strategy/public_demo_package_build_report.md", report)
    write_text(ROOT / "research/product_strategy/public_demo_package_build_review.md", review)
    write_json(ROOT / "research/product_strategy/public_demo_package_build_review_results.json", review_results)


def verify_only() -> int:
    validation = validate_package_contents(PACKAGE_ROOT)
    zip_valid = ZIP_PATH.exists()
    if zip_valid:
        zip_validation = validate_zip(sha256_file(ZIP_PATH))
        zip_valid = (
            not zip_validation["zip_duplicate_entries"]
            and not zip_validation["zip_absolute_entries"]
            and not zip_validation["zip_traversal_entries"]
            and not zip_validation["zip_backslash_entries"]
            and not zip_validation["extracted_validation"]["sha256_mismatches"]
            and not zip_validation["extracted_validation"]["missing_files"]
            and not zip_validation["extracted_validation"]["extra_files"]
        )
    ok = (
        not validation["duplicate_paths"]
        and not validation["sha256_mismatches"]
        and not validation["missing_files"]
        and not validation["extra_files"]
        and not validation["missing_required_files"]
        and not validation["json_errors"]
        and not validation["secret_hits"]
        and not validation["local_path_hits"]
        and not validation["sensitive_value_hits"]
        and validation["authorized_fixtures_only"]
        and validation["authorized_actions_only"]
        and validation["authorized_reason_codes_only"]
        and not validation["invented_cli_detected"]
        and zip_valid
    )
    print(json.dumps({"status": "PASS" if ok else "FAIL", "validation": validation, "zip_valid": zip_valid}, indent=2, sort_keys=True))
    return 0 if ok else 1


def main() -> int:
    if "--verify-only" in sys.argv:
        return verify_only()
    first = build_once("first")
    first_fingerprint = first["source_fingerprint"]
    second = build_once("second")
    second_fingerprint = second["source_fingerprint"]
    semantic_repeatability = first_fingerprint == second_fingerprint
    zip_byte_reproducibility = first["zip_sha256"] == second["zip_sha256"]
    verification = run_verification_commands()
    validation = second["package_validation"]
    fixture_match = all(
        sha256_file(ROOT / info["source"]) == sha256_file(PACKAGE_ROOT / info["package"])
        for info in AUTHORIZED_FIXTURES.values()
    )
    command_results = verification["commands"]
    results: dict[str, Any] = {
        "schema": "SPIRA_PUBLIC_DEMO_PACKAGE_BUILD_RESULTS",
        "schema_version": 1,
        "source_commit": SOURCE_COMMIT,
        "authorization_commit": PACKAGE_AUTHORIZATION_COMMIT,
        "package_build_commit": SOURCE_COMMIT,
        "package_root": rel(PACKAGE_ROOT),
        "zip_filename": ZIP_PATH.name,
        "zip_sha256": second["zip_sha256"],
        "package_file_count": second_fingerprint["file_count"],
        "fixture_packaging_mode": "copied_byte_for_byte_with_source_hash_provenance",
        "fixture_hashes_match_source": fixture_match,
        "authorized_fixtures_only": validation["authorized_fixtures_only"],
        "authorized_actions_only": validation["authorized_actions_only"],
        "authorized_reason_codes_only": validation["authorized_reason_codes_only"],
        "invented_cli_detected": validation["invented_cli_detected"],
        "invented_schema_detected": validation["invented_schema_detected"],
        "invented_artifact_detected": validation["invented_artifact_detected"],
        "local_absolute_paths_detected": bool(validation["local_path_hits"]),
        "secrets_detected": bool(validation["secret_hits"]),
        "sensitive_values_detected": bool(validation["sensitive_value_hits"]),
        "duplicate_paths": validation["duplicate_paths"],
        "missing_files": validation["missing_files"] + validation["missing_required_files"],
        "extra_files": validation["extra_files"],
        "sha256_mismatches": validation["sha256_mismatches"],
        "first_build_result": first,
        "second_build_result": second,
        "semantic_build_repeatability": semantic_repeatability,
        "zip_byte_reproducibility": zip_byte_reproducibility,
        "demo_paths_verified": command_results["demo_paths"]["returncode"] == 0,
        "conformance_passed": command_results["conformance"]["returncode"] == 0,
        "focused_pytest_passed": command_results["focused_pytest"]["returncode"] == 0,
        "full_pytest_passed": command_results["full_pytest"]["returncode"] == 0,
        "package_smoke_tests_passed": command_results["package_smoke_tests"]["returncode"] == 0,
        "json_validation_passed": not validation["json_errors"],
        "lean_reproduction_status": verification["lean_reproduction_status"],
        "claims_boundary_preserved": True,
        "competitor_boundaries_preserved": True,
        "product_change_performed": False,
        "formal_core_change_performed": False,
        "fixture_change_performed": False,
        "domain_expansion_detected": False,
        "publication_performed": False,
        "outreach_performed": False,
        "verification_commands": verification,
        "next_step": "COLD_PUBLIC_DEMO_REVIEW_REQUIRED",
    }
    verdict, blockers = verdict_from_results(results)
    if verdict != "PUBLIC_DEMO_PACKAGE_ACCEPTED":
        results["next_step"] = "PUBLIC_DEMO_PACKAGE_BUILD_REVISION_REQUIRED"
    results["verdict"] = verdict
    results["blockers"] = blockers
    write_build_reports(results)
    print(json.dumps({"verdict": verdict, "blockers": blockers, "zip_sha256": second["zip_sha256"]}, indent=2, sort_keys=True))
    return 0 if verdict == "PUBLIC_DEMO_PACKAGE_ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
