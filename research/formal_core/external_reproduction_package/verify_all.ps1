$ErrorActionPreference = "Stop"
$root = Resolve-Path (Join-Path $PSScriptRoot "..\..\..")
Set-Location $root

Write-Host "SPIRA Formal Core V1 external reproduction"

python - <<'PY'
import hashlib, json, pathlib, sys
root = pathlib.Path.cwd()
manifest = json.loads((root / "research/formal_core/external_reproduction_package/artifact_manifest.json").read_text(encoding="utf-8"))
for item in manifest["source_artifacts"]:
    data = (root / item["path"]).read_bytes()
    got = hashlib.sha256(data).hexdigest()
    if got != item["sha256"]:
        raise SystemExit(f"hash mismatch: {item['path']}")
print("artifact_manifest_hashes: PASS")
PY

if (Get-Command lake -ErrorAction SilentlyContinue) {
  Push-Location formal\spira_formal_core_v1
  lake build
  Pop-Location
} else {
  throw "lake not found; install the Lean toolchain declared in formal\spira_formal_core_v1\lean-toolchain"
}

python - <<'PY'
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

python -m pytest

python - <<'PY'
import json, pathlib, re
root = pathlib.Path.cwd()
expected = json.loads((root / "research/formal_core/external_reproduction_package/expected_results.json").read_text(encoding="utf-8"))
checks = [
    ("research/formal_core/spira_formal_core_v1_all_domain_adapter_alignment_review.md", expected["all_domain_alignment"]["status"]),
    ("research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_results.json", expected["domain1"]["typed_conformance"]["status"]),
    ("research/formal_core/domain1/spira_formal_core_v1_domain1_raw_adapter_conformance_results.json", expected["domain1"]["raw_fixture_conformance"]["status"]),
    ("research/formal_core/domain2/spira_formal_core_v1_domain2_conformance_results.json", expected["domain2"]["typed_conformance"]["status"]),
    ("research/formal_core/domain2/spira_formal_core_v1_domain2_raw_adapter_conformance_results.json", expected["domain2"]["raw_fixture_conformance"]["status"]),
    ("research/formal_core/domain2/spira_formal_core_v1_domain2_production_adapter_alignment_results.json", expected["domain2"]["production_alignment"]["status"]),
    ("research/formal_core/domain3/spira_formal_core_v1_domain3_conformance_results.json", expected["domain3"]["typed_conformance"]["status"]),
    ("research/formal_core/domain3/spira_formal_core_v1_domain3_raw_adapter_conformance_results.json", expected["domain3"]["raw_fixture_conformance"]["status"]),
    ("research/formal_core/domain3/spira_formal_core_v1_domain3_production_adapter_alignment_results.json", expected["domain3"]["production_alignment"]["status"]),
]
for rel, status in checks:
    text = (root / rel).read_text(encoding="utf-8")
    if status not in text:
        raise SystemExit(f"missing expected status {status} in {rel}")
for rel in ["research/formal_core", "formal/spira_formal_core_v1"]:
    text = "\n".join(p.read_text(encoding="utf-8", errors="ignore") for p in (root / rel).rglob("*") if p.is_file())
    if re.search(r"(sk-[A-Za-z0-9]|api[_-]?key\s*=|password\s*=)", text, re.I):
        raise SystemExit(f"secret-like token detected under {rel}")
print("expected_status_and_secret_scan: PASS")
print("SPIRA_FORMAL_CORE_V1_EXTERNAL_REPRODUCTION_PASS")
PY
