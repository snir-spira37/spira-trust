#!/usr/bin/env python3
"""Run SPIRA Trust against a release wheel and write release evidence."""

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any
import zipfile


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--wheel", required=True)
    parser.add_argument("--output-dir", required=True)
    parser.add_argument("--spira-command", default="spira-trust")
    parser.add_argument("--bundle-sha256", default=None)
    parser.add_argument("--verify-embedded-sboms", action="store_true")
    args = parser.parse_args()

    wheel = Path(args.wheel)
    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    trust_dir = output / "trust"
    graph_dir = output / "graph"
    evidence_pack = output / "spira-release-evidence.zip"
    log_dir = output / "logs"

    spira_command = shlex.split(args.spira_command)
    trust_cmd = [*spira_command, "trust", str(wheel), "--output-dir", str(trust_dir), "--format", "json"]
    graph_cmd = [
        *spira_command,
        "graph",
        str(wheel),
        "--output-dir",
        str(graph_dir),
        "--sbom",
        "cyclonedx-json",
        "--evidence-pack",
        str(evidence_pack),
    ]
    if args.bundle_sha256:
        graph_cmd.extend(["--bundle-sha256", args.bundle_sha256])
    if args.verify_embedded_sboms:
        graph_cmd.append("--verify-embedded-sboms")

    trust = _run(trust_cmd, log_dir)
    graph = _run(graph_cmd, log_dir)
    decision_path = graph_dir / "spira-decision.json"
    decision = _load_json(decision_path)
    hash_contract = _verify_decision_hash_contract(graph_dir, decision, evidence_pack)
    schema_validation = _validate_decision_contract(decision, Path("schemas") / "spira_decision_v1.json")

    manifest = {
        "schema": "SPIRA_RELEASE_SELF_EVIDENCE_V1",
        "schema_version": "1.0",
        "created_at_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "wheel": {
            "path": _portable_path(wheel, output),
            "sha256": sha256(wheel.read_bytes()).hexdigest(),
            "bytes": wheel.stat().st_size,
        },
        "trust": {
            "exit_code": trust["exit_code"],
            "stdout_path": _portable_path(trust["stdout_path"], output),
            "stderr_path": _portable_path(trust["stderr_path"], output),
        },
        "graph": {
            "exit_code": graph["exit_code"],
            "stdout_path": _portable_path(graph["stdout_path"], output),
            "stderr_path": _portable_path(graph["stderr_path"], output),
            "decision_json": _portable_path(decision_path, output),
            "evidence_pack": _portable_path(evidence_pack, output),
            "evidence_pack_sha256": sha256(evidence_pack.read_bytes()).hexdigest() if evidence_pack.is_file() else None,
        },
        "decision": decision.get("decision", {}),
        "standards": decision.get("standards", {}),
        "hash_contract": hash_contract,
        "schema_validation": schema_validation,
        "local_paths_included": False,
        "not_claimed": [
            "self-evidence flow does not publish to PyPI or TestPyPI",
            "self-evidence flow does not cryptographically sign artifacts",
            "evidence.zip is a release artifact, not a Python package distribution",
        ],
    }
    manifest_path = output / "release_self_evidence_manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    if trust["exit_code"] != 0 or graph["exit_code"] != 0 or not hash_contract["pass"] or not schema_validation["pass"]:
        return 1
    return 0


def _run(cmd: list[str], log_dir: Path) -> dict[str, Any]:
    name = cmd[1] if len(cmd) > 1 else "command"
    log_dir.mkdir(parents=True, exist_ok=True)
    stamp = sha256(" ".join(cmd).encode("utf-8")).hexdigest()[:12]
    stdout_path = log_dir / f"{name}_{stamp}.stdout"
    stderr_path = log_dir / f"{name}_{stamp}.stderr"
    run = subprocess.run(cmd, text=True, capture_output=True)
    stdout_path.write_text(run.stdout, encoding="utf-8", newline="\n")
    stderr_path.write_text(run.stderr, encoding="utf-8", newline="\n")
    return {"exit_code": run.returncode, "stdout_path": stdout_path, "stderr_path": stderr_path}


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _portable_path(path: Path, base: Path) -> str:
    resolved_path = path.resolve()
    resolved_base = base.resolve()
    try:
        return resolved_path.relative_to(resolved_base).as_posix()
    except ValueError:
        return path.name


def _validate_decision_contract(decision: dict[str, Any], schema_path: Path) -> dict[str, Any]:
    errors: list[str] = []
    if not schema_path.is_file():
        errors.append(f"schema file missing: {schema_path.as_posix()}")
        return {"pass": False, "schema_path": schema_path.as_posix(), "errors": errors}
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    for field in schema.get("required", []):
        if field not in decision:
            errors.append(f"missing required field: {field}")
    if decision.get("schema") != "SPIRA_DECISION_V1":
        errors.append("schema must be SPIRA_DECISION_V1")
    if decision.get("schema_version") != "1.0":
        errors.append("schema_version must be 1.0")
    if decision.get("tool", {}).get("name") != "spira-trust":
        errors.append("tool.name must be spira-trust")
    if decision.get("command") != "graph":
        errors.append("command must be graph")
    graph_verdicts = set(schema["$defs"]["graphVerdict"]["enum"])
    layer_statuses = set(schema["$defs"]["layerStatus"]["enum"])
    pep740_statuses = set(schema["$defs"]["pep740Status"]["enum"])
    pep770_statuses = set(schema["$defs"]["pep770Status"]["enum"])
    decision_block = decision.get("decision", {})
    for key in ("verdict", "combined_verdict"):
        if decision_block.get(key) not in graph_verdicts:
            errors.append(f"decision.{key} is outside SPIRA_DECISION_V1")
    if decision_block.get("winning_status") not in layer_statuses:
        errors.append("decision.winning_status is outside SPIRA_DECISION_V1")
    if decision_block.get("exit_code") not in {0, 1, 2, 3, 4, 5, 6}:
        errors.append("decision.exit_code is outside SPIRA_DECISION_V1")
    layers = decision.get("layers", {})
    if not isinstance(layers.get("per_layer"), list) or not layers.get("per_layer"):
        errors.append("layers.per_layer must be a non-empty array")
    else:
        for index, layer in enumerate(layers["per_layer"]):
            for field in ("layer", "status", "evaluated", "source_verdict", "evidence_ref", "finding_count"):
                if field not in layer:
                    errors.append(f"layers.per_layer[{index}] missing {field}")
            if layer.get("status") not in layer_statuses:
                errors.append(f"layers.per_layer[{index}].status is outside SPIRA_DECISION_V1")
    standards = decision.get("standards", {})
    pep770 = standards.get("pep770_sbom_consistency", {})
    pep740 = standards.get("pep740_offline_attestations", {})
    if pep770.get("status") not in pep770_statuses:
        errors.append("standards.pep770_sbom_consistency.status is outside SPIRA_DECISION_V1")
    if pep740.get("status") not in pep740_statuses:
        errors.append("standards.pep740_offline_attestations.status is outside SPIRA_DECISION_V1")
    evidence = decision.get("evidence", {})
    if not isinstance(evidence.get("files"), list):
        errors.append("evidence.files must be an array")
    return {
        "pass": not errors,
        "schema_path": schema_path.as_posix(),
        "schema_sha256": sha256(schema_path.read_bytes()).hexdigest(),
        "errors": errors,
    }


def _verify_decision_hash_contract(output_dir: Path, decision: dict[str, Any], evidence_pack: Path) -> dict[str, Any]:
    disk_bad: list[str] = []
    for item in decision.get("evidence", {}).get("files", []) or []:
        path = output_dir / str(item.get("path"))
        data = path.read_bytes()
        if sha256(data).hexdigest() != item.get("sha256") or len(data) != item.get("bytes"):
            disk_bad.append(str(item.get("path")))
    pack_bad: list[str] = []
    manifest_bad: list[str] = []
    if evidence_pack.is_file():
        with zipfile.ZipFile(evidence_pack) as archive:
            packed_decision = json.loads(archive.read("spira-decision.json").decode("utf-8"))
            manifest = json.loads(archive.read("manifest.json").decode("utf-8"))
            entries = {entry["file"]: entry for entry in manifest.get("entries", [])}
            for item in packed_decision.get("evidence", {}).get("files", []) or []:
                data = archive.read(str(item.get("path")))
                if sha256(data).hexdigest() != item.get("sha256") or len(data) != item.get("bytes"):
                    pack_bad.append(str(item.get("path")))
                entry = entries.get(str(item.get("path")))
                if not entry or entry.get("sha256") != item.get("sha256") or entry.get("bytes") != item.get("bytes"):
                    manifest_bad.append(str(item.get("path")))
    return {
        "pass": not disk_bad and not pack_bad and not manifest_bad,
        "disk_mismatches": disk_bad,
        "pack_mismatches": pack_bad,
        "pack_manifest_mismatches": manifest_bad,
    }


if __name__ == "__main__":
    raise SystemExit(main())
