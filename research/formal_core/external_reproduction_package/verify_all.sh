#!/usr/bin/env bash
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
  (cd formal/spira_formal_core_v1 && lake build SpiraFormalCore)
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

"$PYTHON_BIN" -m pytest tests/test_formal_core_v1_external_reproduction_package.py
echo "v1_external_reproduction_package_pytest: PASS"

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
