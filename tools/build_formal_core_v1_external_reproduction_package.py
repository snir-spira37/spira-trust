from __future__ import annotations

import hashlib
import json
import re
import stat
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "research" / "formal_core"
PACKAGE = DOMAIN / "external_reproduction_package"
AUTHORIZATION = DOMAIN / "spira_formal_core_v1_external_reproduction_package_authorization.md"
RESULTS = DOMAIN / "spira_formal_core_v1_external_reproduction_package_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_external_reproduction_package_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_external_reproduction_package_review.md"

FORBIDDEN_LEAN_TOKENS = ("sorry", "admit", "sorryAx", "axiom ")


def main() -> int:
    PACKAGE.mkdir(parents=True, exist_ok=True)
    source_artifacts = collect_source_artifacts()
    proof_inventory = build_proof_inventory()
    expected_results = build_expected_results()
    toolchain_lock = build_toolchain_lock()

    write_text(PACKAGE / "README_TASK.txt", readme_task())
    write_text(PACKAGE / "FORMAL_CLAIMS_AND_BOUNDARIES.md", claims_and_boundaries())
    write_json(PACKAGE / "expected_results.json", expected_results)
    write_json(PACKAGE / "proof_and_axiom_inventory.json", proof_inventory)
    write_json(PACKAGE / "toolchain_lock.json", toolchain_lock)
    write_text(PACKAGE / "COLD_EXTERNAL_REVIEW_TASK.md", cold_external_review_task())
    write_text(PACKAGE / "verify_all.ps1", verify_all_ps1())
    write_text(PACKAGE / "verify_all.sh", verify_all_sh())

    artifact_manifest = build_artifact_manifest(source_artifacts)
    write_json(PACKAGE / "artifact_manifest.json", artifact_manifest)
    write_text(PACKAGE / "SHA256SUMS", sha256sums(source_artifacts, package_files_for_sums()))

    results = build_results(source_artifacts, proof_inventory, expected_results, artifact_manifest)
    write_json(RESULTS, results)
    write_text(REPORT, report_markdown(results))
    write_text(REVIEW, review_markdown(results))
    print(json.dumps({"status": results["status"], "artifact_count": results["artifact_count"]}, sort_keys=True))
    return 0 if results["status"].endswith("_ACCEPTED") else 1


def collect_source_artifacts() -> list[dict[str, Any]]:
    files: set[Path] = set()
    include_roots = [
        ROOT / "formal" / "spira_formal_core_v1",
        ROOT / "source" / "spira_core",
        ROOT / "tests",
        ROOT / "research" / "formal_core",
        ROOT / "research" / "test_build_failure_contract",
        ROOT / "research" / "terraform_plan_contract",
        ROOT / "research" / "unification_proof_corpus" / "results",
    ]
    for base in include_roots:
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if (
                path.is_file()
                and ".lake" not in path.parts
                and "__pycache__" not in path.parts
                and path.suffix != ".pyc"
                and PACKAGE not in path.parents
                and path not in {RESULTS, REPORT, REVIEW}
            ):
                files.add(path)
    for name in ("pyproject.toml", "README.md", "LICENSE"):
        path = ROOT / name
        if path.is_file():
            files.add(path)
    for pattern in (
        "tools/run_formal_core_v1*.py",
        "tools/materialize_formal_core_v1*.py",
    ):
        for path in ROOT.glob(pattern):
            if path.is_file():
                files.add(path)
    return [artifact_entry(path) for path in sorted(files, key=rel)]


def build_artifact_manifest(source_artifacts: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_ARTIFACT_MANIFEST",
        "schema_version": 1,
        "authorization": rel(AUTHORIZATION),
        "source_artifact_count": len(source_artifacts),
        "source_artifacts": source_artifacts,
        "package_files": [rel(path) for path in package_files_for_sums()],
        "claim_boundary": "offline deterministic reproduction only; parser proofs, production claims, live agents, and release are not authorized",
    }


def build_expected_results() -> dict[str, Any]:
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_EXPECTED_RESULTS",
        "schema_version": 1,
        "all_domain_alignment": {
            "status": "SPIRA_FORMAL_CORE_V1_ALL_DOMAIN_ADAPTER_ALIGNMENT_ACCEPTED",
            "review_path": "research/formal_core/spira_formal_core_v1_all_domain_adapter_alignment_review.md",
        },
        "domain1": {
            "typed_conformance": {
                "results_path": "research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED",
                "record_count": 1954,
                "record_pass_count": 1954,
                "false_proceed_records": 0,
                "identity_drop_records": 0,
                "list_drop_records": 0,
            },
            "raw_fixture_conformance": {
                "results_path": "research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN1_RAW_ADAPTER_CONFORMANCE_ACCEPTED",
                "fixture_count": 33,
                "false_proceed_count": 0,
                "identity_hash_loss_count": 0,
                "unification_id_loss_count": 0,
            },
        },
        "domain2": {
            "typed_conformance": {
                "results_path": "research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_rerun_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN2_CONFORMANCE_ACCEPTED",
                "case_count": 38,
                "case_pass_count": 38,
                "mutation_pairs": {"passed": 6, "total": 6},
            },
            "raw_fixture_conformance": {
                "results_path": "research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN2_RAW_ADAPTER_CONFORMANCE_ACCEPTED",
                "fixture_count": 26,
                "false_proceed_count": 0,
            },
            "production_alignment": {
                "results_path": "research/formal_core/domain2/spira_formal_core_v1_domain2_production_adapter_alignment_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN2_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED",
            },
        },
        "domain3": {
            "typed_conformance": {
                "results_path": "research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN3_CONFORMANCE_ACCEPTED",
                "case_count": 40,
                "case_pass_count": 40,
                "mutation_pairs": {"passed": 10, "total": 10},
            },
            "raw_fixture_conformance": {
                "results_path": "research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN3_RAW_ADAPTER_CONFORMANCE_ACCEPTED",
                "fixture_count": 31,
                "false_proceed_count": 0,
            },
            "production_alignment": {
                "results_path": "research/formal_core/domain3/spira_formal_core_v1_domain3_production_adapter_alignment_results.json",
                "status": "SPIRA_FORMAL_CORE_V1_DOMAIN3_PRODUCTION_ADAPTER_ALIGNMENT_ACCEPTED",
            },
        },
        "pytest": {
            "last_full_count": 269,
            "expected_result": "PASS",
        },
        "forbidden": {
            "live_agents": True,
            "parser_proof_claim": True,
            "production_claim": True,
            "release": True,
        },
    }


def build_proof_inventory() -> dict[str, Any]:
    lean_files = sorted((ROOT / "formal" / "spira_formal_core_v1").rglob("*.lean"), key=rel)
    matches = []
    theorem_like = []
    definition_like = []
    for path in lean_files:
        text = path.read_text(encoding="utf-8")
        for token in FORBIDDEN_LEAN_TOKENS:
            if token in text:
                matches.append({"path": rel(path), "token": token})
        for line in text.splitlines():
            stripped = line.strip()
            if stripped.startswith("theorem ") or stripped.startswith("lemma "):
                theorem_like.append({"path": rel(path), "line": stripped[:200]})
            if stripped.startswith("def ") or stripped.startswith("inductive ") or stripped.startswith("structure "):
                definition_like.append({"path": rel(path), "line": stripped[:200]})
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_PROOF_AND_AXIOM_INVENTORY",
        "lean_file_count": len(lean_files),
        "lean_files": [rel(path) for path in lean_files],
        "forbidden_tokens": list(FORBIDDEN_LEAN_TOKENS),
        "forbidden_token_matches": matches,
        "no_forbidden_tokens": matches == [],
        "definition_like_count": len(definition_like),
        "theorem_like_count": len(theorem_like),
        "definition_like": definition_like,
        "theorem_like": theorem_like,
        "axiom_claim_boundary": "no custom axiom/sorry/admit token found by textual scan; Lean kernel and toolchain remain trusted",
    }


def build_toolchain_lock() -> dict[str, Any]:
    lean_toolchain = ROOT / "formal" / "spira_formal_core_v1" / "lean-toolchain"
    lakefile = ROOT / "formal" / "spira_formal_core_v1" / "lakefile.toml"
    lake_manifest = ROOT / "formal" / "spira_formal_core_v1" / "lake-manifest.json"
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_TOOLCHAIN_LOCK",
        "lean_toolchain": lean_toolchain.read_text(encoding="utf-8").strip() if lean_toolchain.exists() else "__missing__",
        "lean_toolchain_sha256": sha256_path(lean_toolchain) if lean_toolchain.exists() else "__missing__",
        "lakefile_sha256": sha256_path(lakefile) if lakefile.exists() else "__missing__",
        "lake_manifest_sha256": sha256_path(lake_manifest) if lake_manifest.exists() else "__missing__",
        "python_requirement": "Python 3.12 recommended; exact interpreter is part of reviewer environment TCB",
        "network_required": False,
    }


def readme_task() -> str:
    return """SPIRA Formal Core V1 External Reproduction Task

Purpose
=======

Reproduce the offline deterministic Formal Core V1 evidence without live agents.

Start from the repository root and run one of:

  PowerShell:
    research\\formal_core\\external_reproduction_package\\verify_all.ps1

  POSIX shell:
    bash research/formal_core/external_reproduction_package/verify_all.sh

Expected result:

  SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PASS

This package intentionally does not run Claude, Codex, DeepSeek, holdout, carryover, or any live benchmark.

"""


def claims_and_boundaries() -> str:
    return """# Formal Claims And Boundaries

## Proved / Machine-Checked

Formal Core V1 Lean sources are included with a toolchain lock and no-sorry/no-admit/no-custom-axiom textual scan.

## Differentially Conformant

Domain 1, Domain 2, and Domain 3 are accepted for bounded typed evidence, frozen corpora, synthetic fixtures, and recorded adapter-alignment checkpoints.

## Tested

Python reference harnesses, raw fixture conformance, production adapter alignment for Domains 2-3, and full pytest are reproducible offline.

## Trusted

Lean kernel/toolchain, Python runtime, JSON parsing in Python, SHA-256 implementation, filesystem reads, and OS process execution remain trusted computing base components.

## Out Of Scope

Parser proofs for arbitrary wheel/ZIP/RECORD/SBOM, pytest/JUnit, and Terraform Plan JSON are not claimed. Package safety, software safety, malware absence, Terraform execution correctness, provider behavior, cloud-state freshness, production readiness, release readiness, and LLM behavior are not claimed.
"""


def cold_external_review_task() -> str:
    return """# Cold External Review Task

Answer these questions after running the reproduction script in a clean checkout:

1. Can all deterministic results be reproduced?
2. Do the claims match the evidence exactly?
3. Is there a way to bypass the Formal Core path for an authoritative contract?
4. Is any parser proof claimed by mistake?
5. Are trusted computing base assumptions visible?
6. Does any PASS depend on undocumented manual judgment?
7. Were Claude, Codex, DeepSeek, or other live agents required?

Expected conclusion if all checks pass:

SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PASS
"""


def verify_all_ps1() -> str:
    return r'''$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $root

function Assert-NativeSuccess {
  param([Parameter(Mandatory=$true)][string]$Label)
  if ($LASTEXITCODE -ne 0) {
    throw "$Label failed with exit code $LASTEXITCODE"
  }
}

Write-Host "SPIRA Formal Core V1 external reproduction"

@'
import hashlib, json, pathlib, sys
root = pathlib.Path.cwd()
manifest = json.loads((root / "research/formal_core/external_reproduction_package/artifact_manifest.json").read_text(encoding="utf-8"))
for item in manifest["source_artifacts"]:
    data = (root / item["path"]).read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != item["sha256"]:
        raise SystemExit(f"hash mismatch: {item['path']}")
print("artifact_manifest_hashes: PASS")
'@ | python -
Assert-NativeSuccess "artifact manifest hash check"

if (Get-Command lake -ErrorAction SilentlyContinue) {
  Push-Location formal\spira_formal_core_v1
  try {
    lake build
    Assert-NativeSuccess "lake build"
  } finally {
    Pop-Location
  }
} else {
  throw "lake not found; install the Lean toolchain declared in formal\spira_formal_core_v1\lean-toolchain"
}

@'
from pathlib import Path
root = Path.cwd()
tokens = ("sorry", "admit", "sorryAx", "axiom ")
matches = []
for path in sorted((root / "formal/spira_formal_core_v1").rglob("*.lean")):
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token in text:
            matches.append((path.as_posix(), token))
if matches:
    raise SystemExit(f"forbidden Lean tokens: {matches}")
print("lean_no_sorry_no_admit_scan: PASS")
'@ | python -
Assert-NativeSuccess "Lean forbidden-token scan"

python -m pytest `
  tests/test_formal_core_v1_python_boundary.py `
  tests/test_unification_proof.py `
  tests/test_formal_core_v1_domain1_raw_adapter_conformance.py `
  tests/test_formal_core_v1_domain2_raw_adapter_conformance.py `
  tests/test_formal_core_v1_domain2_production_adapter_alignment.py `
  tests/test_formal_core_v1_domain3_raw_adapter_conformance.py `
  tests/test_formal_core_v1_domain3_production_adapter_alignment.py `
  tests/test_test_build_failure_producer.py `
  tests/test_test_build_failure_oracle_validator.py `
  tests/test_terraform_plan_producer.py `
  tests/test_terraform_plan_oracle_validator.py
Assert-NativeSuccess "focused pytest"

python -m pytest
Assert-NativeSuccess "full pytest"

@'
import json, pathlib, re
root = pathlib.Path.cwd()
expected = json.loads((root / "research/formal_core/external_reproduction_package/expected_results.json").read_text(encoding="utf-8"))

def load_json(rel):
    return json.loads((root / rel).read_text(encoding="utf-8"))

def assert_eq(label, got, want):
    if got != want:
        raise SystemExit(f"{label}: got {got!r}, expected {want!r}")

def assert_empty(label, value):
    if value:
        raise SystemExit(f"{label}: expected empty, got {value!r}")

review_text = (root / expected["all_domain_alignment"]["review_path"]).read_text(encoding="utf-8")
if expected["all_domain_alignment"]["status"] not in review_text:
    raise SystemExit("all-domain alignment accepted status missing from review")

d1 = load_json(expected["domain1"]["typed_conformance"]["results_path"])
e1 = expected["domain1"]["typed_conformance"]
assert_eq("domain1 typed status", d1["status"], e1["status"])
assert_eq("domain1 record_count", d1["record_count"], e1["record_count"])
assert_eq("domain1 record_pass_count", d1["record_pass_count"], e1["record_pass_count"])
assert_eq("domain1 false_proceed_records", len(d1["false_proceed_records"]), e1["false_proceed_records"])
assert_eq("domain1 identity_drop_records", len(d1["identity_drop_records"]), e1["identity_drop_records"])
assert_eq("domain1 list_drop_records", len(d1["list_drop_records"]), e1["list_drop_records"])

d1r = load_json(expected["domain1"]["raw_fixture_conformance"]["results_path"])
e1r = expected["domain1"]["raw_fixture_conformance"]
assert_eq("domain1 raw status", d1r["status"], e1r["status"])
assert_eq("domain1 raw fixture_count", d1r["counts"]["fixture_count"], e1r["fixture_count"])
assert_eq("domain1 raw false_proceed_count", d1r["counts"]["false_proceed_count"], e1r["false_proceed_count"])
assert_eq("domain1 raw identity_hash_loss_count", d1r["counts"]["identity_hash_loss_count"], e1r["identity_hash_loss_count"])
assert_eq("domain1 raw unification_id_loss_count", d1r["counts"]["unification_id_loss_count"], e1r["unification_id_loss_count"])

d2 = load_json(expected["domain2"]["typed_conformance"]["results_path"])
e2 = expected["domain2"]["typed_conformance"]
assert_eq("domain2 typed status", d2["status"], e2["status"])
assert_eq("domain2 case_count", d2["case_count"], e2["case_count"])
assert_eq("domain2 case_pass_count", d2["case_pass_count"], e2["case_pass_count"])
assert_eq("domain2 mutation passed", d2["mutation_pair_checks"]["passed"], e2["mutation_pairs"]["passed"])
assert_eq("domain2 mutation total", d2["mutation_pair_checks"]["total"], e2["mutation_pairs"]["total"])
assert_empty("domain2 blocking_to_proceed_cases", d2["blocking_to_proceed_cases"])
assert_empty("domain2 not_evaluated_to_proceed_cases", d2["not_evaluated_to_proceed_cases"])

d2r = load_json(expected["domain2"]["raw_fixture_conformance"]["results_path"])
e2r = expected["domain2"]["raw_fixture_conformance"]
assert_eq("domain2 raw status", d2r["status"], e2r["status"])
assert_eq("domain2 raw fixture_count", d2r["counts"]["fixture_count"], e2r["fixture_count"])
assert_eq("domain2 raw false_proceed_count", d2r["counts"]["false_proceed_count"], e2r["false_proceed_count"])

d2p = load_json(expected["domain2"]["production_alignment"]["results_path"])
assert_eq("domain2 production status", d2p["status"], expected["domain2"]["production_alignment"]["status"])
assert_eq("domain2 production conformance status", d2p["production_conformance_summary"]["status"], e2["status"])
assert_eq("domain2 production mutation passed", d2p["production_conformance_summary"]["mutation_pair_checks"]["passed"], e2["mutation_pairs"]["passed"])

d3 = load_json(expected["domain3"]["typed_conformance"]["results_path"])
e3 = expected["domain3"]["typed_conformance"]
assert_eq("domain3 typed status", d3["status"], e3["status"])
assert_eq("domain3 case_count", d3["case_count"], e3["case_count"])
assert_eq("domain3 case_pass_count", d3["case_pass_count"], e3["case_pass_count"])
assert_eq("domain3 mutation passed", d3["mutation_pair_checks"]["passed"], e3["mutation_pairs"]["passed"])
assert_eq("domain3 mutation total", d3["mutation_pair_checks"]["total"], e3["mutation_pairs"]["total"])
assert_empty("domain3 blocking_to_proceed_cases", d3["blocking_to_proceed_cases"])
assert_empty("domain3 not_evaluated_to_proceed_cases", d3["not_evaluated_to_proceed_cases"])

d3r = load_json(expected["domain3"]["raw_fixture_conformance"]["results_path"])
e3r = expected["domain3"]["raw_fixture_conformance"]
assert_eq("domain3 raw status", d3r["status"], e3r["status"])
assert_eq("domain3 raw fixture_count", d3r["counts"]["fixture_count"], e3r["fixture_count"])
assert_eq("domain3 raw false_proceed_count", d3r["counts"]["false_proceed_count"], e3r["false_proceed_count"])

d3p = load_json(expected["domain3"]["production_alignment"]["results_path"])
assert_eq("domain3 production status", d3p["status"], expected["domain3"]["production_alignment"]["status"])

for rel in ["research/formal_core", "formal/spira_formal_core_v1"]:
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (root / rel).rglob("*") if p.is_file())
    if re.search(r"(sk-[A-Za-z0-9]|api[_-]?key\s*=|password\s*=)", text, re.I):
        raise SystemExit(f"secret-like token detected under {rel}")
print("expected_status_and_secret_scan: PASS")
print("SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PASS")
'@ | python -
Assert-NativeSuccess "expected-results and secret scan"
'''


def verify_all_sh() -> str:
    return r'''#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."

echo "SPIRA Formal Core V1 external reproduction"

PYTHON_BIN="${PYTHON:-}"
if [[ -z "$PYTHON_BIN" ]]; then
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN=python3
  elif command -v python >/dev/null 2>&1; then
    PYTHON_BIN=python
  else
    echo "python3/python not found" >&2
    exit 1
  fi
fi

"$PYTHON_BIN" - <<'PY'
import hashlib, json, pathlib
root = pathlib.Path.cwd()
manifest = json.loads((root / "research/formal_core/external_reproduction_package/artifact_manifest.json").read_text(encoding="utf-8"))
for item in manifest["source_artifacts"]:
    data = (root / item["path"]).read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != item["sha256"]:
        raise SystemExit(f"hash mismatch: {item['path']}")
print("artifact_manifest_hashes: PASS")
PY

if command -v lake >/dev/null 2>&1; then
  (cd formal/spira_formal_core_v1 && lake build)
else
  echo "lake not found; install the Lean toolchain declared in formal/spira_formal_core_v1/lean-toolchain" >&2
  exit 1
fi

"$PYTHON_BIN" - <<'PY'
from pathlib import Path
root = Path.cwd()
tokens = ("sorry", "admit", "sorryAx", "axiom ")
matches = []
for path in sorted((root / "formal/spira_formal_core_v1").rglob("*.lean")):
    text = path.read_text(encoding="utf-8")
    for token in tokens:
        if token in text:
            matches.append((path.as_posix(), token))
if matches:
    raise SystemExit(f"forbidden Lean tokens: {matches}")
print("lean_no_sorry_no_admit_scan: PASS")
PY

"$PYTHON_BIN" -m pytest \
  tests/test_formal_core_v1_python_boundary.py \
  tests/test_unification_proof.py \
  tests/test_formal_core_v1_domain1_raw_adapter_conformance.py \
  tests/test_formal_core_v1_domain2_raw_adapter_conformance.py \
  tests/test_formal_core_v1_domain2_production_adapter_alignment.py \
  tests/test_formal_core_v1_domain3_raw_adapter_conformance.py \
  tests/test_formal_core_v1_domain3_production_adapter_alignment.py \
  tests/test_test_build_failure_producer.py \
  tests/test_test_build_failure_oracle_validator.py \
  tests/test_terraform_plan_producer.py \
  tests/test_terraform_plan_oracle_validator.py

"$PYTHON_BIN" -m pytest

"$PYTHON_BIN" - <<'PY'
import json, pathlib, re
root = pathlib.Path.cwd()
expected = json.loads((root / "research/formal_core/external_reproduction_package/expected_results.json").read_text(encoding="utf-8"))

def load_json(rel):
    return json.loads((root / rel).read_text(encoding="utf-8"))

def assert_eq(label, got, want):
    if got != want:
        raise SystemExit(f"{label}: got {got!r}, expected {want!r}")

def assert_empty(label, value):
    if value:
        raise SystemExit(f"{label}: expected empty, got {value!r}")

review_text = (root / expected["all_domain_alignment"]["review_path"]).read_text(encoding="utf-8")
if expected["all_domain_alignment"]["status"] not in review_text:
    raise SystemExit("all-domain alignment accepted status missing from review")

d1 = load_json(expected["domain1"]["typed_conformance"]["results_path"])
e1 = expected["domain1"]["typed_conformance"]
assert_eq("domain1 typed status", d1["status"], e1["status"])
assert_eq("domain1 record_count", d1["record_count"], e1["record_count"])
assert_eq("domain1 record_pass_count", d1["record_pass_count"], e1["record_pass_count"])
assert_eq("domain1 false_proceed_records", len(d1["false_proceed_records"]), e1["false_proceed_records"])
assert_eq("domain1 identity_drop_records", len(d1["identity_drop_records"]), e1["identity_drop_records"])
assert_eq("domain1 list_drop_records", len(d1["list_drop_records"]), e1["list_drop_records"])

d1r = load_json(expected["domain1"]["raw_fixture_conformance"]["results_path"])
e1r = expected["domain1"]["raw_fixture_conformance"]
assert_eq("domain1 raw status", d1r["status"], e1r["status"])
assert_eq("domain1 raw fixture_count", d1r["counts"]["fixture_count"], e1r["fixture_count"])
assert_eq("domain1 raw false_proceed_count", d1r["counts"]["false_proceed_count"], e1r["false_proceed_count"])
assert_eq("domain1 raw identity_hash_loss_count", d1r["counts"]["identity_hash_loss_count"], e1r["identity_hash_loss_count"])
assert_eq("domain1 raw unification_id_loss_count", d1r["counts"]["unification_id_loss_count"], e1r["unification_id_loss_count"])

d2 = load_json(expected["domain2"]["typed_conformance"]["results_path"])
e2 = expected["domain2"]["typed_conformance"]
assert_eq("domain2 typed status", d2["status"], e2["status"])
assert_eq("domain2 case_count", d2["case_count"], e2["case_count"])
assert_eq("domain2 case_pass_count", d2["case_pass_count"], e2["case_pass_count"])
assert_eq("domain2 mutation passed", d2["mutation_pair_checks"]["passed"], e2["mutation_pairs"]["passed"])
assert_eq("domain2 mutation total", d2["mutation_pair_checks"]["total"], e2["mutation_pairs"]["total"])
assert_empty("domain2 blocking_to_proceed_cases", d2["blocking_to_proceed_cases"])
assert_empty("domain2 not_evaluated_to_proceed_cases", d2["not_evaluated_to_proceed_cases"])

d2r = load_json(expected["domain2"]["raw_fixture_conformance"]["results_path"])
e2r = expected["domain2"]["raw_fixture_conformance"]
assert_eq("domain2 raw status", d2r["status"], e2r["status"])
assert_eq("domain2 raw fixture_count", d2r["counts"]["fixture_count"], e2r["fixture_count"])
assert_eq("domain2 raw false_proceed_count", d2r["counts"]["false_proceed_count"], e2r["false_proceed_count"])

d2p = load_json(expected["domain2"]["production_alignment"]["results_path"])
assert_eq("domain2 production status", d2p["status"], expected["domain2"]["production_alignment"]["status"])
assert_eq("domain2 production conformance status", d2p["production_conformance_summary"]["status"], e2["status"])
assert_eq("domain2 production mutation passed", d2p["production_conformance_summary"]["mutation_pair_checks"]["passed"], e2["mutation_pairs"]["passed"])

d3 = load_json(expected["domain3"]["typed_conformance"]["results_path"])
e3 = expected["domain3"]["typed_conformance"]
assert_eq("domain3 typed status", d3["status"], e3["status"])
assert_eq("domain3 case_count", d3["case_count"], e3["case_count"])
assert_eq("domain3 case_pass_count", d3["case_pass_count"], e3["case_pass_count"])
assert_eq("domain3 mutation passed", d3["mutation_pair_checks"]["passed"], e3["mutation_pairs"]["passed"])
assert_eq("domain3 mutation total", d3["mutation_pair_checks"]["total"], e3["mutation_pairs"]["total"])
assert_empty("domain3 blocking_to_proceed_cases", d3["blocking_to_proceed_cases"])
assert_empty("domain3 not_evaluated_to_proceed_cases", d3["not_evaluated_to_proceed_cases"])

d3r = load_json(expected["domain3"]["raw_fixture_conformance"]["results_path"])
e3r = expected["domain3"]["raw_fixture_conformance"]
assert_eq("domain3 raw status", d3r["status"], e3r["status"])
assert_eq("domain3 raw fixture_count", d3r["counts"]["fixture_count"], e3r["fixture_count"])
assert_eq("domain3 raw false_proceed_count", d3r["counts"]["false_proceed_count"], e3r["false_proceed_count"])

d3p = load_json(expected["domain3"]["production_alignment"]["results_path"])
assert_eq("domain3 production status", d3p["status"], expected["domain3"]["production_alignment"]["status"])

for rel in ["research/formal_core", "formal/spira_formal_core_v1"]:
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (root / rel).rglob("*") if p.is_file())
    if re.search(r"(sk-[A-Za-z0-9]|api[_-]?key\s*=|password\s*=)", text, re.I):
        raise SystemExit(f"secret-like token detected under {rel}")
print("expected_status_and_secret_scan: PASS")
print("SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PASS")
PY
'''


def package_files_for_sums() -> list[Path]:
    return sorted(
        [
            path
            for path in PACKAGE.glob("*")
            if path.is_file() and path.name != "SHA256SUMS"
        ],
        key=rel,
    )


def sha256sums(source_artifacts: list[dict[str, Any]], package_files: list[Path]) -> str:
    rows = []
    for item in source_artifacts:
        rows.append(f"{item['sha256']}  {item['path']}")
    for path in package_files:
        rows.append(f"{sha256_path(path)}  {rel(path)}")
    return "\n".join(rows) + "\n"


def build_results(
    source_artifacts: list[dict[str, Any]],
    proof_inventory: dict[str, Any],
    expected_results: dict[str, Any],
    artifact_manifest: dict[str, Any],
) -> dict[str, Any]:
    required_files = [
        "README_TASK.txt",
        "FORMAL_CLAIMS_AND_BOUNDARIES.md",
        "expected_results.json",
        "artifact_manifest.json",
        "SHA256SUMS",
        "verify_all.ps1",
        "verify_all.sh",
        "proof_and_axiom_inventory.json",
        "toolchain_lock.json",
        "COLD_EXTERNAL_REVIEW_TASK.md",
    ]
    package_presence = {name: (PACKAGE / name).exists() for name in required_files}
    gates = {
        "package_files_present": all(package_presence.values()),
        "source_artifacts_present": len(source_artifacts) > 100,
        "proof_inventory_no_forbidden_tokens": proof_inventory["no_forbidden_tokens"],
        "expected_results_include_domains_1_2_3": all(key in expected_results for key in ("domain1", "domain2", "domain3")),
        "artifact_manifest_has_hashes": all("sha256" in item for item in artifact_manifest["source_artifacts"]),
        "verify_scripts_no_live_agents": not any(
            token in (PACKAGE / name).read_text(encoding="utf-8").lower()
            for name in ("verify_all.ps1", "verify_all.sh")
            for token in ("claude", "codex primary", "deepseek")
        ),
    }
    status = (
        "SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PACKAGE_ACCEPTED"
        if all(gates.values())
        else "SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PACKAGE_NEEDS_REVISION"
    )
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PACKAGE_RESULTS",
        "schema_version": 1,
        "status": status,
        "authorization": rel(AUTHORIZATION),
        "package_root": rel(PACKAGE),
        "artifact_count": len(source_artifacts),
        "package_presence": package_presence,
        "gates": gates,
        "proof_inventory_summary": {
            "lean_file_count": proof_inventory["lean_file_count"],
            "definition_like_count": proof_inventory["definition_like_count"],
            "theorem_like_count": proof_inventory["theorem_like_count"],
            "forbidden_token_matches": proof_inventory["forbidden_token_matches"],
        },
        "claim_boundary": "external offline reproduction package only; no live agents, parser proof, production claim, or release",
    }


def report_markdown(results: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 External Reproduction Package Report",
            "",
            "Status:",
            "",
            "```text",
            results["status"],
            "```",
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(
                {
                    "artifact_count": results["artifact_count"],
                    "package_root": results["package_root"],
                    "gates": results["gates"],
                    "proof_inventory_summary": results["proof_inventory_summary"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "This package is offline-only and does not authorize live agents, benchmark execution, production claims, release, tag, or PyPI work.",
        ]
    ) + "\n"


def review_markdown(results: dict[str, Any]) -> str:
    accepted = results["status"].endswith("_ACCEPTED")
    return "\n".join(
        [
            "# SPIRA Formal Core V1 External Reproduction Package Review",
            "",
            "## Status",
            "",
            "```text",
            results["status"],
            "OFFLINE_REPRODUCTION_PACKAGE_READY" if accepted else "OFFLINE_REPRODUCTION_PACKAGE_NEEDS_REVISION",
            "LIVE_AGENT_SESSIONS_NOT_INCLUDED",
            "PARSER_PROOF_NOT_CLAIMED",
            "PRODUCTION_CLAIM_NOT_AUTHORIZED",
            "RELEASE_NOT_AUTHORIZED",
            "```",
            "",
            "## Decision",
            "",
            "The Formal Core V1 external reproduction package is accepted for cold external review."
            if accepted
            else "The Formal Core V1 external reproduction package needs revision.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps({"artifact_count": results["artifact_count"], "gates": results["gates"]}, indent=2, sort_keys=True),
            "```",
            "",
            "## Boundary",
            "",
            "The package enables offline reproduction of deterministic Formal Core V1 and all-domain adapter evidence. It does not prove arbitrary parsers, package safety, infrastructure correctness, production readiness, release readiness, or LLM/agent behavior.",
            "",
            "## Next Step",
            "",
            "```text",
            "COLD_EXTERNAL_REVIEW_REQUIRED",
            "```",
        ]
    ) + "\n"


def artifact_entry(path: Path) -> dict[str, Any]:
    return {
        "path": rel(path),
        "sha256": sha256_path(path),
        "bytes": path.stat().st_size,
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")


def write_text(path: Path, text: str) -> None:
    path.write_text(text.replace("\r\n", "\n").replace("\r", "\n"), encoding="utf-8", newline="\n")
    if path.suffix == ".sh":
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
