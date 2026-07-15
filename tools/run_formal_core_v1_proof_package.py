from __future__ import annotations

import json
import os
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping


ROOT = Path(__file__).resolve().parents[1]
LEAN_PROJECT = ROOT / "formal" / "spira_formal_core_v1"
RESEARCH = ROOT / "research" / "formal_core"

MANIFEST = RESEARCH / "spira_formal_core_v1_proof_package_manifest.json"
RESULTS = RESEARCH / "spira_formal_core_v1_proof_package_results.json"
REPORT = RESEARCH / "spira_formal_core_v1_proof_package_report.md"
REVIEW = RESEARCH / "spira_formal_core_v1_proof_package_review.md"
CLAIM_BOUNDARY = RESEARCH / "spira_formal_core_v1_claim_boundary_summary.md"
REPRODUCTION_GUIDE = RESEARCH / "spira_formal_core_v1_reproduction_guide.md"

AUTHORIZED_DIRTY_PATHS = {
    "tools/run_formal_core_v1_proof_package.py",
    "research/formal_core/spira_formal_core_v1_claim_boundary_summary.md",
    "research/formal_core/spira_formal_core_v1_reproduction_guide.md",
    "research/formal_core/spira_formal_core_v1_proof_package_manifest.json",
    "research/formal_core/spira_formal_core_v1_proof_package_results.json",
    "research/formal_core/spira_formal_core_v1_proof_package_report.md",
    "research/formal_core/spira_formal_core_v1_proof_package_review.md",
}

DYNAMIC_PACKAGE_OUTPUTS = {MANIFEST, RESULTS, REPORT, REVIEW}

REQUIRED_STATUS_ARTIFACTS = {
    "all_domains": (
        RESEARCH / "spira_formal_core_v1_all_domains_conformance_review.md",
        "SPIRA_FORMAL_CORE_V1_ALL_DOMAINS_CONFORMANCE_ACCEPTED",
    ),
    "domain1": (
        RESEARCH / "domain1" / "spira_formal_core_v1_domain1_conformance_review.md",
        "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED",
    ),
    "domain2": (
        RESEARCH / "domain2" / "spira_formal_core_v1_domain2_conformance_rerun_review.md",
        "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED",
    ),
    "domain3": (
        RESEARCH / "domain3" / "spira_formal_core_v1_domain3_conformance_review.md",
        "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED",
    ),
    "tcb": (
        RESEARCH / "spira_formal_core_v1_trusted_computing_base_ledger.md",
        "SPIRA_FORMAL_CORE_V1_TRUSTED_COMPUTING_BASE_LEDGER_SPECIFIED",
    ),
    "machine_checked": (
        RESEARCH / "spira_formal_core_v1_machine_checked_proof_review.md",
        "SPIRA_FORMAL_CORE_V1_MACHINE_CHECKED_PROOFS_ACCEPTED",
    ),
    "executable_reference": (
        RESEARCH / "spira_formal_core_v1_executable_reference_review.md",
        "SPIRA_FORMAL_CORE_V1_EXECUTABLE_REFERENCE_ACCEPTED",
    ),
    "differential_harness": (
        RESEARCH / "spira_formal_core_v1_differential_harness_review.md",
        "SPIRA_FORMAL_CORE_V1_DIFFERENTIAL_HARNESS_ACCEPTED",
    ),
    "typed_boundary": (
        RESEARCH / "spira_formal_core_v1_python_typed_evidence_boundary_review.md",
        "SPIRA_FORMAL_CORE_V1_PYTHON_TYPED_EVIDENCE_BOUNDARY_ACCEPTED",
    ),
}

FOCUSED_TESTS = [
    ["python", "-m", "pytest", "tests/test_formal_core_v1_python_boundary.py"],
    ["python", "-m", "pytest", "tests/test_unification_proof.py"],
    ["python", "-m", "pytest", "tests/test_mvp_unified.py"],
]

DOMAIN_HARNESSES = [
    ["python", "tools/run_formal_core_v1_domain1_conformance.py"],
    ["python", "tools/run_formal_core_v1_domain2_conformance.py"],
    ["python", "tools/run_formal_core_v1_domain3_conformance.py"],
]


def main() -> None:
    manifest = build_manifest()
    _write_json(MANIFEST, manifest)
    checks = run_checks()
    results = evaluate_package(manifest, checks)
    _write_json(RESULTS, results)
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    REVIEW.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"status": results["status"]}, sort_keys=True))
    if results["status"] != "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED":
        raise SystemExit(1)


def build_manifest() -> dict[str, Any]:
    artifact_paths = sorted(package_artifact_paths(), key=lambda path: path.as_posix())
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_MANIFEST",
        "schema_version": 1,
        "generated_at": now(),
        "repository": {
            "commit": git(["rev-parse", "HEAD"]),
            "branch": git(["rev-parse", "--abbrev-ref", "HEAD"]),
            "status_short": git(["status", "--short"]),
            "unexpected_dirty_paths": unexpected_dirty_paths(),
        },
        "lean_toolchain": (LEAN_PROJECT / "lean-toolchain").read_text(encoding="utf-8").strip(),
        "artifacts": [
            {
                "path": str(path.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_file(path),
                "bytes": path.stat().st_size,
            }
            for path in artifact_paths
        ],
        "accepted_reviews": {
            key: str(path.relative_to(ROOT)).replace("\\", "/")
            for key, (path, _status) in REQUIRED_STATUS_ARTIFACTS.items()
        },
        "claim_boundary": "typed evidence boundary only; raw adapters and production runtime not formally proved",
    }


def package_artifact_paths() -> list[Path]:
    paths: list[Path] = []
    paths.extend(sorted((LEAN_PROJECT / "SpiraFormalCore").rglob("*.lean")))
    paths.extend(sorted(RESEARCH.glob("spira_formal_core_v1_*.md")))
    paths.extend(sorted(RESEARCH.glob("spira_formal_core_v1_*.json")))
    for domain in ("domain1", "domain2", "domain3"):
        paths.extend(sorted((RESEARCH / domain).glob("spira_formal_core_v1_*.md")))
        paths.extend(sorted((RESEARCH / domain).glob("spira_formal_core_v1_*.json")))
    paths.extend(ROOT / item for item in (
        "tools/run_formal_core_v1_domain1_conformance.py",
        "tools/run_formal_core_v1_domain2_conformance.py",
        "tools/run_formal_core_v1_domain3_conformance.py",
        "tools/run_formal_core_v1_differential_harness.py",
        "tools/run_formal_core_v1_proof_package.py",
        "tests/test_formal_core_v1_python_boundary.py",
        "tests/test_unification_proof.py",
        "tests/test_mvp_unified.py",
    ))
    return [path for path in paths if path.exists() and path not in DYNAMIC_PACKAGE_OUTPUTS]


def run_checks() -> dict[str, Any]:
    return {
        "lake_build": run_command(["lake", "build"], cwd=LEAN_PROJECT),
        "proof_scan": scan_lean_sources(),
        "domain_harnesses": [run_command(command, cwd=ROOT) for command in DOMAIN_HARNESSES],
        "focused_tests": [run_command(command, cwd=ROOT) for command in FOCUSED_TESTS],
        "status_artifacts": verify_status_artifacts(),
    }


def evaluate_package(manifest: Mapping[str, Any], checks: Mapping[str, Any]) -> dict[str, Any]:
    gates = {
        "manifest_artifacts_hashed": all(is_sha256(item.get("sha256")) for item in manifest["artifacts"]),
        "working_tree_has_no_unexpected_changes": not manifest["repository"]["unexpected_dirty_paths"],
        "lake_build_pass": checks["lake_build"]["returncode"] == 0,
        "proof_scan_pass": checks["proof_scan"]["status"] == "PASS",
        "domain_harnesses_pass": all(item["returncode"] == 0 for item in checks["domain_harnesses"]),
        "focused_tests_pass": all(item["returncode"] == 0 for item in checks["focused_tests"]),
        "status_artifacts_pass": all(item["present"] and item["status_present"] for item in checks["status_artifacts"].values()),
    }
    status = "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED" if all(gates.values()) else "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_NEEDS_REVISION"
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_RESULTS",
        "schema_version": 1,
        "generated_at": now(),
        "status": status,
        "authorization": "research/formal_core/spira_formal_core_v1_proof_package_authorization.md",
        "manifest": "research/formal_core/spira_formal_core_v1_proof_package_manifest.json",
        "artifact_count": len(manifest["artifacts"]),
        "gates": gates,
        "checks": checks,
        "not_authorized": [
            "RAW_ADAPTER_PROOFS",
            "PYTHON_RUNTIME_PROOF",
            "PRODUCTION_RUNTIME_INTEGRATION",
            "BENCHMARK_CHANGES",
            "NEW_LIVE_SESSIONS",
            "EXISTING_RESULT_RECLASSIFICATION",
            "PRODUCTION_CLAIM",
            "RELEASE",
        ],
    }


def verify_status_artifacts() -> dict[str, Any]:
    result = {}
    for key, (path, status) in REQUIRED_STATUS_ARTIFACTS.items():
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        result[key] = {
            "path": str(path.relative_to(ROOT)).replace("\\", "/"),
            "present": path.exists(),
            "required_status": status,
            "status_present": status in text,
        }
    return result


def scan_lean_sources() -> dict[str, Any]:
    forbidden = ["sorry", "admit", "sorryAx", "axiom "]
    matches = []
    for path in sorted((LEAN_PROJECT / "SpiraFormalCore").rglob("*.lean")):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                matches.append({"path": str(path.relative_to(ROOT)).replace("\\", "/"), "token": token})
    return {"status": "PASS" if not matches else "FAIL", "matches": matches}


def run_command(command: list[str], *, cwd: Path) -> dict[str, Any]:
    completed = subprocess.run(
        command,
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ),
    )
    return {
        "command": " ".join(command),
        "cwd": str(cwd.relative_to(ROOT)).replace("\\", "/") if cwd != ROOT else ".",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Proof Package Report",
            "",
            "Status:",
            "",
            "```text",
            str(results["status"]),
            "```",
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(
                {
                    "artifact_count": results["artifact_count"],
                    "gates": results["gates"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "The package reproduces the accepted typed-evidence proof boundary only.",
            "",
        ]
    )


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = results["status"] == "SPIRA_FORMAL_CORE_V1_PROOF_PACKAGE_ACCEPTED"
    statuses = [
        results["status"],
        "FORMAL_CORE_V1_TYPED_EVIDENCE_BOUNDARY_PACKAGE_ACCEPTED" if accepted else "FORMAL_CORE_V1_TYPED_EVIDENCE_BOUNDARY_PACKAGE_NOT_ACCEPTED",
        "RAW_ADAPTER_PROOFS_NOT_INCLUDED",
        "PYTHON_RUNTIME_PROOF_NOT_INCLUDED",
        "PRODUCTION_CLAIM_NOT_AUTHORIZED",
        "RELEASE_NOT_AUTHORIZED",
    ]
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Proof Package Review",
            "",
            "## Status",
            "",
            "```text",
            *statuses,
            "```",
            "",
            "## Decision",
            "",
            (
                "The Formal Core V1 proof package is accepted as a local reproduction package for the typed-evidence boundary."
                if accepted
                else "The Formal Core V1 proof package requires revision."
            ),
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(
                {
                    "artifact_count": results["artifact_count"],
                    "gates": results["gates"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundaries",
            "",
            "This package does not prove raw parsers, Python runtime, OS behavior, LLM behavior, benchmark runners, production integration, or release readiness.",
            "",
        ]
    )


def git(args: list[str]) -> str:
    completed = subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def unexpected_dirty_paths() -> list[str]:
    paths = []
    for line in git(["status", "--short"]).splitlines():
        if not line:
            continue
        path = line[3:].replace("\\", "/")
        if path not in AUTHORIZED_DIRTY_PATHS:
            paths.append(path)
    return sorted(paths)


def sha256_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
