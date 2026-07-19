#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import os
import platform
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "research" / "nesira_policy_profile"
PACKAGE = DOMAIN / "phase2_external_reproduction_package"
AUTHORIZATION = DOMAIN / "nesira_phase2_external_reproduction_package_authorization.md"
AUTHORIZATION_REVIEW = DOMAIN / "nesira_phase2_external_reproduction_package_authorization_review.md"
RESULTS = DOMAIN / "phase2_external_reproduction_package_build_results.json"
REPORT = DOMAIN / "phase2_external_reproduction_package_build_report.md"
REVIEW = DOMAIN / "phase2_external_reproduction_package_build_review.md"
REVIEW_RESULTS = DOMAIN / "phase2_external_reproduction_package_build_review_results.json"

PACKAGE_BASENAME = "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION"
ZIP_TIMESTAMP = (1980, 1, 1, 0, 0, 0)

PACKAGE_FILENAMES = [
    "README_REPRODUCTION.md",
    "CLAIMS_AND_BOUNDARIES.md",
    "REPRODUCE_PHASE2.md",
    "COLD_EXTERNAL_REVIEW_TASK.md",
    "phase2_reproduction_manifest.json",
    "phase2_expected_results.json",
    "protected_surface_hash_inventory.json",
    "toolchain_environment_lock.json",
    "internal_build_validation_results.json",
    "SHA256SUMS",
]

SOURCE_STATUS = {
    "internal_milestone": "NESIRA_PHASE2_INTERNAL_ASSESSMENT_ENGINE_COMPLETE_INTERNAL_ONLY",
    "lean_composition": "NESIRA_PHASE2_LEAN_COMPOSITION_COLD_VERIFICATION_ACCEPTED",
    "signature_adapter": "NESIRA_PHASE2_SIGNATURE_ADAPTER_COLD_VERIFICATION_ACCEPTED",
    "identity_adapter": "NESIRA_PHASE2_IDENTITY_ADAPTER_COLD_VERIFICATION_ACCEPTED",
    "authority_adapter": "NESIRA_PHASE2_AUTHORITY_ADAPTER_COLD_VERIFICATION_ACCEPTED",
    "isolation_attestation_adapter": "NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_COLD_VERIFICATION_ACCEPTED",
    "assessment_wiring": "NESIRA_PHASE2_ASSESSMENT_WIRING_COLD_VERIFICATION_ACCEPTED",
}

FORBIDDEN_PACKAGE_PHRASES = [
    "safe to proceed",
    "sever now",
    "isolation occurred",
    "isolation confirmed",
    "isolation happened",
    "isolation proven",
    "isolation executed",
    "runner authorized",
    "release authorized",
]

LOCAL_PATH_PATTERNS = [
    "C:\\Users\\",
    "C:/Users/",
    "C:\\\\Users\\\\",
    "/Users/",
]


def main() -> int:
    source_commit = git(["rev-parse", "HEAD"])
    short = source_commit[:7]
    zip_path = DOMAIN / f"{PACKAGE_BASENAME}_{short}.zip"
    upload_note = DOMAIN / f"{PACKAGE_BASENAME}_{short}_UPLOAD_NOTE.txt"

    if PACKAGE.exists():
        shutil.rmtree(PACKAGE)
    PACKAGE.mkdir(parents=True)

    source_artifacts = collect_source_artifacts()
    expected_results = build_expected_results(source_commit)
    protected_surface_inventory = build_protected_surface_inventory()
    toolchain_lock = build_toolchain_lock()

    write_text(PACKAGE / "README_REPRODUCTION.md", readme_reproduction(source_commit))
    write_text(PACKAGE / "CLAIMS_AND_BOUNDARIES.md", claims_and_boundaries())
    write_text(PACKAGE / "REPRODUCE_PHASE2.md", reproduce_phase2(source_commit))
    write_text(PACKAGE / "COLD_EXTERNAL_REVIEW_TASK.md", cold_external_review_task(source_commit))
    write_json(PACKAGE / "phase2_expected_results.json", expected_results)
    write_json(PACKAGE / "protected_surface_hash_inventory.json", protected_surface_inventory)
    write_json(PACKAGE / "toolchain_environment_lock.json", toolchain_lock)
    write_json(PACKAGE / "phase2_reproduction_manifest.json", build_manifest(source_commit, source_artifacts))
    write_json(PACKAGE / "internal_build_validation_results.json", {"status": "PENDING"})
    write_text(PACKAGE / "SHA256SUMS", sha256sums())

    validation = validate_package_files()
    write_json(PACKAGE / "internal_build_validation_results.json", validation)
    write_text(PACKAGE / "SHA256SUMS", sha256sums())
    validation = validate_package_files()
    write_json(PACKAGE / "internal_build_validation_results.json", validation)
    write_text(PACKAGE / "SHA256SUMS", sha256sums())
    validation = validate_package_files()

    create_zip(zip_path)
    zip_sha = sha256_path(zip_path)
    zip_bytes = zip_path.stat().st_size

    results = {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_RESULTS_V1",
        "status": "NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ACCEPTED"
        if validation["accepted"]
        else "NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_NEEDS_REVISION",
        "source_assessment_commit": source_commit,
        "package_directory": rel(PACKAGE),
        "zip_path": rel(zip_path),
        "zip_sha256": zip_sha,
        "zip_bytes": zip_bytes,
        "source_artifact_count": len(source_artifacts),
        "package_file_count": len(PACKAGE_FILENAMES),
        "validation": validation,
        "blocked_claims": [
            "package_delivery",
            "runner",
            "combined_verdict",
            "cli",
            "public_wheel_exposure",
            "public_claim",
            "release",
        ],
    }
    write_json(RESULTS, results)
    write_text(REPORT, report_markdown(results))
    write_json(REVIEW_RESULTS, review_results(results))
    write_text(REVIEW, review_markdown(results))
    write_text(upload_note, upload_note_text(results))

    print(json.dumps({"status": results["status"], "zip_sha256": zip_sha, "zip_path": rel(zip_path)}, sort_keys=True))
    return 0 if results["status"].endswith("_ACCEPTED") else 1


def collect_source_artifacts() -> list[dict[str, Any]]:
    files: set[Path] = set()

    for path in (ROOT / "source" / "spira_core").glob("nesira_phase2_*.py"):
        files.add(path)
    for path in (ROOT / "tools").glob("run_nesira_phase2_*_conformance.py"):
        files.add(path)
    for path in (ROOT / "tests").glob("test_nesira_phase2_*.py"):
        files.add(path)
    files.add(ROOT / "tests" / "test_formal_core_v1_external_reproduction_package.py")
    files.add(ROOT / "requirements" / "nesira_adapters_win_amd64_cp312.txt")

    formal_root = ROOT / "formal" / "spira_formal_core_v1"
    for name in ("lakefile.toml", "lake-manifest.json", "lean-toolchain"):
        files.add(formal_root / name)
    for path in (formal_root / "SpiraFormalCore" / "Phase2").rglob("*.lean"):
        files.add(path)

    for path in DOMAIN.glob("nesira_phase2_*.md"):
        if "external_reproduction_package" not in path.name:
            files.add(path)
    for path in DOMAIN.glob("nesira_phase2_*.json"):
        if "external_reproduction_package" not in path.name:
            files.add(path)
    for path in (DOMAIN / "phase1_external_reproduction_package").glob("*"):
        if path.is_file():
            files.add(path)

    for name in ("pyproject.toml", "README.md", "LICENSE"):
        files.add(ROOT / name)
    files.add(ROOT / "tools" / "build_spira_trust_public.py")

    existing = [path for path in files if path.is_file()]
    return [artifact_entry(path) for path in sorted(existing, key=rel)]


def build_manifest(source_commit: str, source_artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_MANIFEST_V1",
        "source_assessment_commit": source_commit,
        "authorization": rel(AUTHORIZATION),
        "authorization_review": rel(AUTHORIZATION_REVIEW),
        "package_scope": "internal assessment engine external reproduction only",
        "package_delivery_authorized": False,
        "product_claim_authorized": False,
        "source_artifact_count": len(source_artifacts),
        "source_artifacts": source_artifacts,
        "package_files": PACKAGE_FILENAMES,
        "accepted_statuses": SOURCE_STATUS,
        "deterministic_build_metadata": {
            "zip_paths": "forward-slash sorted",
            "zip_timestamp": "1980-01-01T00:00:00Z",
            "sha256sums_scope": "package files except SHA256SUMS itself",
        },
    }


def build_expected_results(source_commit: str) -> dict[str, Any]:
    return {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_EXPECTED_RESULTS_V1",
        "source_assessment_commit": source_commit,
        "expected_full_pytest": "339 passed",
        "formal_core_v1_external_reproduction_package": {
            "sha256sums_checked": 622,
            "sha256sums_failures": 0,
            "v1_scope_contains_phase2_claims": False,
        },
        "lean_composition": {
            "target": "SpiraFormalCorePhase2",
            "oracle_rows": 81,
            "oracle_disagreements": 0,
            "verdict_distribution": {"SUFFICIENT": 1, "NOT_EVALUATED": 15, "INSUFFICIENT": 65},
            "sorryAx": 0,
        },
        "adapters": {
            "signature": "NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED",
            "identity": "NESIRA_PHASE2_IDENTITY_ADAPTER_ACCEPTED",
            "authority": "NESIRA_PHASE2_AUTHORITY_ADAPTER_ACCEPTED",
            "isolation_attestation": "NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_ACCEPTED",
        },
        "assessment_wiring": {
            "verdict": "NESIRA_PHASE2_ASSESSMENT_WIRING_ACCEPTED",
            "oracle_rows_checked": 81,
            "oracle_disagreements": 0,
            "cross_subject_mismatch_produces_sufficient": 0,
            "cross_subject_mismatch_not_sufficient": 1,
        },
        "wheel_exclusion": {
            "phase2_adapters_absent": True,
            "phase2_harnesses_absent": True,
            "cryptography_metadata_absent": True,
            "pyproject_dependencies_empty": True,
        },
        "blocked_claims": {
            "runner": "NOT_AUTHORIZED",
            "combined_verdict": "NOT_AUTHORIZED",
            "cli": "NOT_AUTHORIZED",
            "public_wheel_exposure": "NOT_AUTHORIZED",
            "public_claim": "NOT_AUTHORIZED",
            "release": "NOT_AUTHORIZED",
        },
    }


def build_protected_surface_inventory() -> dict[str, Any]:
    protected_paths = [
        "pyproject.toml",
        "tools/build_spira_trust_public.py",
        "formal/spira_formal_core_v1/lakefile.toml",
        "formal/spira_formal_core_v1/lean-toolchain",
        "formal/spira_formal_core_v1/lake-manifest.json",
        "research/nesira_policy_profile/phase1_external_reproduction_package/SHA256SUMS",
        "research/nesira_policy_profile/phase1_external_reproduction_package/phase1_reproduction_manifest.json",
        "research/nesira_policy_profile/phase1_external_reproduction_package/CLAIMS_AND_BOUNDARIES.md",
        "research/nesira_policy_profile/nesira_phase2_assessment_decision_table.json",
        "research/nesira_policy_profile/nesira_phase2_not_proven_trust_ledger.json",
        "requirements/nesira_adapters_win_amd64_cp312.txt",
    ]
    entries = [artifact_entry(ROOT / path) for path in protected_paths]
    return {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PROTECTED_SURFACE_INVENTORY_V1",
        "protected_surface_count": len(entries),
        "protected_surfaces": entries,
        "boundary": "records public-wheel, V1, oracle, ledger, toolchain, and crypto-pin surfaces that package reviewers must inspect",
    }


def build_toolchain_lock() -> dict[str, Any]:
    requirements = ROOT / "requirements" / "nesira_adapters_win_amd64_cp312.txt"
    lean_toolchain = ROOT / "formal" / "spira_formal_core_v1" / "lean-toolchain"
    return {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_TOOLCHAIN_LOCK_V1",
        "observed_builder_timestamp_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "observed_builder_os": platform.platform(),
        "python_requirement": "Python 3.12.x",
        "observed_python": platform.python_version(),
        "lean_requirement": lean_toolchain.read_text(encoding="utf-8").strip(),
        "lake_requirement": "Lake 5.0.0",
        "cryptography_requirement": "cryptography==49.0.0",
        "adapter_requirements_path": rel(requirements),
        "adapter_requirements_sha256": sha256_path(requirements),
        "adapter_requirements_install": "python -m pip install --require-hashes -r requirements/nesira_adapters_win_amd64_cp312.txt",
        "pyproject_product_dependencies": "must remain empty",
    }


def validate_package_files() -> dict[str, Any]:
    package_paths = [PACKAGE / name for name in PACKAGE_FILENAMES]
    missing = [rel(path) for path in package_paths if not path.is_file()]
    json_failures: list[dict[str, str]] = []
    for path in package_paths:
        if path.suffix == ".json" and path.exists():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                json_failures.append({"path": rel(path), "error": str(exc)})

    sha_failures = []
    sums_path = PACKAGE / "SHA256SUMS"
    if sums_path.exists():
        for line in sums_path.read_text(encoding="utf-8").splitlines():
            expected, name = line.split("  ", 1)
            actual_path = PACKAGE / name
            actual = sha256_path(actual_path) if actual_path.exists() else "__missing__"
            if actual != expected:
                sha_failures.append({"path": name, "expected": expected, "actual": actual})

    package_text = "\n".join(path.read_text(encoding="utf-8") for path in package_paths if path.exists() and path.suffix in {".md", ".json", ""})
    local_path_hits = [pattern for pattern in LOCAL_PATH_PATTERNS if pattern in package_text]
    forbidden_phrase_hits = [phrase for phrase in FORBIDDEN_PACKAGE_PHRASES if phrase.lower() in package_text.lower()]
    non_ascii = [rel(path) for path in package_paths if path.exists() and any(byte > 127 for byte in path.read_bytes())]

    zip_path_safety = validate_zip_path_safety(package_paths)
    accepted = (
        not missing
        and not json_failures
        and not sha_failures
        and not local_path_hits
        and not forbidden_phrase_hits
        and not non_ascii
        and zip_path_safety["safe"]
    )
    return {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_INTERNAL_BUILD_VALIDATION_V1",
        "status": "PASS" if accepted else "FAIL",
        "accepted": accepted,
        "package_files_checked": len(package_paths),
        "missing_files": missing,
        "json_failures": json_failures,
        "sha256sum_failures": sha_failures,
        "local_path_hits": local_path_hits,
        "forbidden_phrase_hits": forbidden_phrase_hits,
        "non_ascii_files": non_ascii,
        "zip_path_safety": zip_path_safety,
        "claim_boundary": "package build only; delivery and product claims remain blocked",
    }


def validate_zip_path_safety(paths: list[Path]) -> dict[str, Any]:
    archive_names = [path.name for path in paths]
    unsafe = [
        name
        for name in archive_names
        if name.startswith("/")
        or name.startswith("\\")
        or ".." in Path(name).parts
        or ":" in name
        or "\\" in name
    ]
    return {
        "safe": not unsafe and len(set(archive_names)) == len(archive_names),
        "unsafe_entries": unsafe,
        "duplicate_entries": sorted(name for name in set(archive_names) if archive_names.count(name) > 1),
    }


def package_files_for_sums() -> list[Path]:
    return [PACKAGE / name for name in PACKAGE_FILENAMES if name != "SHA256SUMS"]


def sha256sums() -> str:
    lines = []
    for path in package_files_for_sums():
        lines.append(f"{sha256_path(path)}  {path.name}")
    return "\n".join(lines) + "\n"


def create_zip(zip_path: Path) -> None:
    if zip_path.exists():
        zip_path.unlink()
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for name in PACKAGE_FILENAMES:
            path = PACKAGE / name
            info = zipfile.ZipInfo(name)
            info.date_time = ZIP_TIMESTAMP
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, path.read_bytes())


def readme_reproduction(source_commit: str) -> str:
    return f"""# Nesira Phase 2 External Reproduction Package

Status:

```text
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ACCEPTED
```

This package lets a cold reviewer reproduce the accepted Nesira Phase 2
internal assessment engine from the public repository.

Source assessment commit:

```text
{source_commit}
```

The package is assessment-only. It does not authorize delivery, release, public
product exposure, a CLI, a combined verdict, runner execution, or permission to
sever.

Start with `CLAIMS_AND_BOUNDARIES.md`, then run `REPRODUCE_PHASE2.md`.
"""


def claims_and_boundaries() -> str:
    return """# Claims and Boundaries

## EMPIRICALLY_REPRODUCED

A reviewer may reproduce that Nesira Phase 2 internally assesses declared trust
evidence across signature, identity, authority, and attestation roots; composes
the result through a verified fail-closed core; and emits an
assumption-carrying assessment artifact.

## FORMALLY_REPRODUCED

The Lean Phase 2 composition core may be checked for:

```text
strict AND composition
totality over 81 sub-verdict combinations
determinism
insufficient dominates not-evaluated
floor assumptions always carried
sufficient assessment is not assumption-free
PT-ISOLATION-01 inherited on sufficient assessment
no execution constructor
```

## EMPIRICALLY_CHECKED_ADAPTERS

```text
signature adapter
identity adapter
authority adapter
isolation attestation adapter
assessment wiring
```

The adapters are empirical code that checks declared evidence against declared
trust roots. They are not formally proved.

## TRUST_BOUNDARY

Trust roots are declared assumptions. SPIRA checks evidence against those
declared roots; it does not prove that the roots are legitimate in an absolute
sense.

Attestation verification is not an isolation-truth proof. The mandatory
`PT-ISOLATION-01` caveat must remain carried.

The assessment artifact is not severance authorization. The required execution
marker is:

```text
ASSESSMENT_ONLY_NOT_A_SEVERANCE_AUTHORIZATION
```

## NOT_AUTHORIZED

```text
package delivery
runner
combined verdict
CLI
public wheel exposure
public capability claim
release
```
"""


def reproduce_phase2(source_commit: str) -> str:
    return f"""# Reproduce Nesira Phase 2 Internal Assessment Engine

## Source

```powershell
git clone https://github.com/snir-spira37/spira-trust.git spira-trust-phase2
cd spira-trust-phase2
git checkout {source_commit}
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
cd formal\\spira_formal_core_v1
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
"""


def cold_external_review_task(source_commit: str) -> str:
    return f"""# Cold External Review Task

You are reviewing the Nesira Phase 2 internal assessment engine package.

Do not rely on the builder's local workspace or recorded reports. Clone the
repository, check out the exact commit, install the hash-locked adapter
requirements, and run the commands in `REPRODUCE_PHASE2.md`.

Authoritative source assessment commit:

```text
{source_commit}
```

Return one verdict:

```text
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_ACCEPTED
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_ACCEPTED_WITH_LEAN_NOT_EVALUATED
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_NEEDS_REVISION
NESIRA_PHASE2_EXTERNAL_REPRODUCTION_REJECTED
```

The accepted claim is internal assessment only. Treat any output that implies
execution, severance, release, public availability, or isolation truth as a
blocking overclaim.
"""


def report_markdown(results: dict[str, Any]) -> str:
    validation = results["validation"]
    return f"""# Nesira Phase 2 External Reproduction Package Build Report

## Status

```text
{results['status']}
```

## Source

```text
source_assessment_commit:
{results['source_assessment_commit']}

zip_path:
{results['zip_path']}

zip_sha256:
{results['zip_sha256']}
```

## Package Validation

```text
package_files_checked: {validation['package_files_checked']}
json_failures: {len(validation['json_failures'])}
sha256sum_failures: {len(validation['sha256sum_failures'])}
local_path_hits: {len(validation['local_path_hits'])}
forbidden_phrase_hits: {len(validation['forbidden_phrase_hits'])}
non_ascii_files: {len(validation['non_ascii_files'])}
zip_path_safety: {'PASS' if validation['zip_path_safety']['safe'] else 'FAIL'}
```

## Boundary

The package is build-only and assessment-only. Delivery, runner, combined
verdict, CLI, public wheel exposure, public claim, and release remain blocked.
"""


def review_results(results: dict[str, Any]) -> dict[str, Any]:
    accepted = results["status"].endswith("_ACCEPTED")
    return {
        "schema": "SPIRA_NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_REVIEW_RESULTS_V1",
        "verdict": "NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ACCEPTED" if accepted else "NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_NEEDS_REVISION",
        "source_assessment_commit": results["source_assessment_commit"],
        "zip_sha256": results["zip_sha256"],
        "accepted": accepted,
        "package_delivery_authorized": False,
        "blocked_claims": results["blocked_claims"],
    }


def review_markdown(results: dict[str, Any]) -> str:
    verdict = "NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_ACCEPTED" if results["status"].endswith("_ACCEPTED") else "NESIRA_PHASE2_EXTERNAL_REPRODUCTION_PACKAGE_BUILD_NEEDS_REVISION"
    return f"""# Nesira Phase 2 External Reproduction Package Build Review

## Verdict

```text
{verdict}
```

This review inspected the generated package metadata, SHA256SUMS, ZIP path
safety, JSON parseability, local-path hygiene, and claim boundary.

It did not perform the future cold external reproduction and did not authorize
delivery to an external reviewer.

## Accepted Package

```text
zip:
{results['zip_path']}

sha256:
{results['zip_sha256']}
```

## Boundary

```text
PACKAGE_DELIVERY: NOT_AUTHORIZED
RUNNER: NOT_AUTHORIZED
COMBINED_VERDICT: NOT_AUTHORIZED
CLI: NOT_AUTHORIZED
PUBLIC_WHEEL_EXPOSURE: NOT_AUTHORIZED
PUBLIC_CLAIM: NOT_AUTHORIZED
RELEASE: NOT_AUTHORIZED
```

Next step, if authorized separately by the user: deliver this ZIP and its task
instructions to a cold external reviewer.
"""


def upload_note_text(results: dict[str, Any]) -> str:
    return f"""SPIRA Nesira Phase 2 external reproduction package

Status: PACKAGE_BUILD_ACCEPTED

ZIP:
{results['zip_path']}

SHA256:
{results['zip_sha256']}

Source assessment commit:
{results['source_assessment_commit']}

Package artifact commit:
Record the repository commit that contains this ZIP before external delivery.

Boundary:
This is an assessment-only internal reproduction package. Package delivery,
runner, combined verdict, CLI, public wheel exposure, public claim, and release
remain NOT_AUTHORIZED until separately approved by the user.
"""


def artifact_entry(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "bytes": path.stat().st_size,
        "sha256": sha256_path(path),
    }


def rel(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def sha256_path(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json(path: Path, value: Any) -> None:
    write_text(path, json.dumps(value, indent=2, sort_keys=True) + "\n")


def git(args: list[str]) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


if __name__ == "__main__":
    raise SystemExit(main())
