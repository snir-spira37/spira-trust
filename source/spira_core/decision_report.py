from __future__ import annotations

import json
import zipfile
from datetime import datetime, timezone
from hashlib import sha256
from importlib import metadata as importlib_metadata
from pathlib import Path
from typing import Any, Mapping


DECISION_SCHEMA = "SPIRA_DECISION_V1"
DECISION_SCHEMA_VERSION = "1.0"


EXIT_CODE_CONTRACT = {
    "0": "OK or OK_WITH_NOTES for the evaluated layers",
    "1": "BLOCK or clean input failure",
    "2": "WARN",
    "3": "DRIFT_DETECTED",
    "4": "BASELINE_UNTRUSTED",
    "5": "POLICY_UNTRUSTED",
    "6": "REBASELINE_REQUIRES_CONFIRMATION or SBOM export failure",
}


def write_decision_report(
    graph_result: Mapping[str, Any],
    *,
    exit_code: int,
    output_dir: str | Path,
    include_local_paths: bool = False,
) -> dict[str, Any]:
    output = Path(output_dir)
    bom = _load_json(graph_result.get("bill_of_materials_path"))
    decision = build_decision_report(
        graph_result,
        bom,
        exit_code=exit_code,
        output_dir=output,
        include_local_paths=include_local_paths,
    )
    json_path = output / "spira-decision.json"
    md_path = output / "spira-decision.md"
    json_path.write_text(json.dumps(decision, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    md_path.write_text(format_decision_markdown(decision), encoding="utf-8", newline="\n")
    decision["decision_json_path"] = str(json_path.resolve())
    decision["decision_markdown_path"] = str(md_path.resolve())
    return decision


def finalize_graph_outputs_for_decision(
    graph_result: dict[str, Any],
    *,
    output_dir: str | Path,
) -> None:
    """Write graph outputs to their final pre-decision bytes.

    Decision evidence hashes are a contract over files on disk. Keep every
    mutable graph output finalized before write_decision_report hashes it.
    """

    output = Path(output_dir)
    decision_json_path = output / "spira-decision.json"
    decision_markdown_path = output / "spira-decision.md"
    graph_result["decision_report_path"] = str(decision_json_path.resolve())
    graph_result["decision_markdown_path"] = str(decision_markdown_path.resolve())

    bom = _load_json(graph_result.get("bill_of_materials_path"))
    _attach_combined_decision_summary(graph_result, bom.get("combined_policy_verdict", {}) or {})

    if graph_result.get("summary_path"):
        Path(str(graph_result["summary_path"])).write_text(
            str(graph_result.get("summary_text") or ""),
            encoding="utf-8",
            newline="\n",
        )
    if graph_result.get("report_path"):
        Path(str(graph_result["report_path"])).write_text(
            json.dumps(graph_result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",
        )


def build_decision_report(
    graph_result: Mapping[str, Any],
    bom: Mapping[str, Any],
    *,
    exit_code: int,
    output_dir: str | Path | None = None,
    include_local_paths: bool = False,
) -> dict[str, Any]:
    combined = bom.get("combined_policy_verdict", {}) or graph_result.get("combined_policy_verdict", {}) or {}
    pep770 = graph_result.get("pep770_sbom_consistency") or bom.get("pep770_sbom_consistency") or {}
    pep740 = graph_result.get("pep740_offline_attestations") or bom.get("pep740_offline_attestations") or {}
    graph_pkg = graph_result.get("graph_evidence_package") or {}
    base_dir = Path(output_dir) if output_dir else None
    evidence_files = _evidence_files(graph_result, base_dir=base_dir, include_local_paths=include_local_paths)
    graph_pkg_ref = _file_record(
        "graph_evidence_package",
        graph_pkg.get("zip_path"),
        base_dir=base_dir,
        include_local_paths=include_local_paths,
        preferred_path=Path("governance") / Path(str(graph_pkg.get("zip_path") or "")).name if graph_pkg.get("zip_path") else None,
        included_in_pack=True,
    )
    if graph_pkg_ref:
        evidence_files.append(graph_pkg_ref)
    trust_root = pep740.get("trust_root")
    if isinstance(trust_root, Mapping):
        trust_root = dict(trust_root)
        if trust_root.get("path"):
            trust_root["path"] = _path_ref(trust_root.get("path"), base_dir=base_dir, include_local_paths=include_local_paths)
    return {
        "schema": DECISION_SCHEMA,
        "schema_version": DECISION_SCHEMA_VERSION,
        "created_at_utc": _utc(),
        "tool": {
            "name": "spira-trust",
            "version": _tool_version(),
        },
        "command": "graph",
        "decision": {
            "verdict": graph_result.get("verdict"),
            "combined_verdict": combined.get("combined_verdict"),
            "winning_status": combined.get("winning_status"),
            "exit_code": exit_code,
            "decided_by": combined.get("decided_by", []),
        },
        "layers": {
            "per_layer": combined.get("per_layer", []),
            "evaluated_layers": combined.get("evaluated_layers", []),
            "not_evaluated_layers": combined.get("not_evaluated_layers", []),
        },
        "standards": {
            "pep770_sbom_consistency": {
                "evaluated": bool(pep770.get("evaluated")),
                "status": pep770.get("status"),
                "result_count": pep770.get("result_count", 0),
            },
            "pep740_offline_attestations": {
                "status": pep740.get("status"),
                "attestation_path": _path_ref(pep740.get("attestation_path"), base_dir=base_dir, include_local_paths=include_local_paths),
                "attestation_sha256": pep740.get("attestation_sha256"),
                "identity_evaluated": bool(pep740.get("identity_evaluated")),
                "trust_root": trust_root,
                "finding_count": len(pep740.get("findings", []) or []),
            },
        },
        "evidence": {
            "graph_report_path": _path_ref(graph_result.get("report_path"), base_dir=base_dir, include_local_paths=include_local_paths),
            "graph_summary_path": _path_ref(graph_result.get("summary_path"), base_dir=base_dir, include_local_paths=include_local_paths),
            "bill_of_materials_path": _path_ref(graph_result.get("bill_of_materials_path"), base_dir=base_dir, include_local_paths=include_local_paths),
            "input_manifest_path": _path_ref(graph_result.get("input_manifest_path"), base_dir=base_dir, include_local_paths=include_local_paths),
            "graph_evidence_manifest_path": _path_ref(graph_result.get("graph_evidence_manifest_path"), base_dir=base_dir, include_local_paths=include_local_paths),
            "cyclonedx_sbom_path": _path_ref(graph_result.get("cyclonedx_sbom_path"), base_dir=base_dir, include_local_paths=include_local_paths),
            "graph_evidence_package_zip": graph_pkg_ref.get("path") if graph_pkg_ref else None,
            "graph_evidence_package_sha256": graph_pkg.get("zip_sha256"),
            "files": evidence_files,
        },
        "exit_code_contract": EXIT_CODE_CONTRACT,
        "not_claimed": [
            "decision report is an aggregator over SPIRA evidence outputs",
            "does not create new trust evidence",
            "does not replace graph_report.json or bill_of_materials.json",
            "does not perform full Sigstore cryptographic verification",
            "does not add network access, resolver behavior, install, import, or code execution",
            "GRAPH_OK reflects evaluated layers only; not-evaluated layers are listed explicitly",
        ],
    }


def format_decision_markdown(decision: Mapping[str, Any]) -> str:
    verdict = decision.get("decision", {})
    layers = decision.get("layers", {})
    lines = [
        "# SPIRA Decision",
        "",
        f"- Schema: `{decision.get('schema')}` `{decision.get('schema_version')}`",
        f"- Verdict: `{verdict.get('verdict')}`",
        f"- Combined verdict: `{verdict.get('combined_verdict')}`",
        f"- Winning status: `{verdict.get('winning_status')}`",
        f"- Exit code: `{verdict.get('exit_code')}`",
        f"- Decided by: `{', '.join(verdict.get('decided_by') or [])}`",
        "",
        "## Layers",
        "",
    ]
    for layer in layers.get("per_layer", []) or []:
        lines.append(f"- `{layer.get('layer')}`: `{layer.get('status')}` from `{layer.get('source_verdict')}`")
    lines.extend([
        "",
        "## Evaluated",
        "",
        f"- Evaluated layers: `{', '.join(layers.get('evaluated_layers') or [])}`",
        f"- Not evaluated layers: `{', '.join(layers.get('not_evaluated_layers') or [])}`",
        "",
        "## Boundaries",
        "",
    ])
    for item in decision.get("not_claimed", []) or []:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _attach_combined_decision_summary(graph_result: dict[str, Any], combined: Mapping[str, Any]) -> None:
    combined_verdict = combined.get("combined_verdict")
    winning = combined.get("winning_status")
    decided_by = ", ".join(combined.get("decided_by") or [])
    if not combined_verdict:
        return
    addition = (
        "\nDecision:\n"
        f"- Combined decision: {combined_verdict}"
        f" (winning_status={winning}, decided_by={decided_by or 'none'})\n"
    )
    text = str(graph_result.get("summary_text") or "")
    if "Combined decision:" not in text:
        graph_result["summary_text"] = text.rstrip() + "\n" + addition


def write_evidence_pack(
    graph_result: Mapping[str, Any],
    decision: Mapping[str, Any],
    output_zip: str | Path,
) -> dict[str, Any]:
    zip_path = Path(output_zip)
    zip_path.parent.mkdir(parents=True, exist_ok=True)
    entries: list[dict[str, Any]] = []
    candidates = [
        ("graph_report.json", graph_result.get("report_path")),
        ("graph_summary.txt", graph_result.get("summary_path")),
        ("bill_of_materials.json", graph_result.get("bill_of_materials_path")),
        ("input_manifest.json", graph_result.get("input_manifest_path")),
        ("graph_evidence_manifest.json", graph_result.get("graph_evidence_manifest_path")),
        ("spira-trust.cdx.json", graph_result.get("cyclonedx_sbom_path")),
        (f"governance/{Path(str((graph_result.get('graph_evidence_package') or {}).get('zip_path') or '')).name}", (graph_result.get("graph_evidence_package") or {}).get("zip_path")),
        ("spira-decision.json", decision.get("decision_json_path")),
        ("spira-decision.md", decision.get("decision_markdown_path")),
        ("agent_summary.json", graph_result.get("agent_summary_path")),
        ("unification_proof.json", graph_result.get("unification_proof_path")),
    ]
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for arcname, source in candidates:
            if not source:
                continue
            path = Path(str(source))
            if not path.is_file():
                continue
            data = path.read_bytes()
            archive.writestr(arcname, data)
            entries.append({"file": arcname, "sha256": sha256(data).hexdigest(), "bytes": len(data)})
        manifest = {
            "schema": "SPIRA_DECISION_EVIDENCE_PACK_V1",
            "schema_version": "1.0",
            "created_at_utc": _utc(),
            "entry_count": len(entries),
            "entries": entries,
            "not_claimed": [
                "evidence pack is a convenience archive of existing evidence outputs",
                "does not add cryptographic signing",
            ],
        }
        archive.writestr("manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    return {
        "path": str(zip_path.resolve()),
        "sha256": sha256(zip_path.read_bytes()).hexdigest(),
        "entry_count": len(entries) + 1,
    }


def _evidence_files(
    graph_result: Mapping[str, Any],
    *,
    base_dir: Path | None,
    include_local_paths: bool,
) -> list[dict[str, Any]]:
    records = []
    for label, value in [
        ("graph_report", graph_result.get("report_path")),
        ("graph_summary", graph_result.get("summary_path")),
        ("bill_of_materials", graph_result.get("bill_of_materials_path")),
        ("input_manifest", graph_result.get("input_manifest_path")),
        ("graph_evidence_manifest", graph_result.get("graph_evidence_manifest_path")),
        ("cyclonedx_sbom", graph_result.get("cyclonedx_sbom_path")),
    ]:
        record = _file_record(label, value, base_dir=base_dir, include_local_paths=include_local_paths)
        if record:
            records.append(record)
    return records


def _file_record(
    label: str,
    value: Any,
    *,
    base_dir: Path | None,
    include_local_paths: bool,
    preferred_path: Path | None = None,
    included_in_pack: bool = True,
) -> dict[str, Any] | None:
    if not value:
        return None
    path = Path(str(value))
    if not path.is_file():
        return None
    record: dict[str, Any] = {
        "label": label,
        "path": preferred_path.as_posix() if preferred_path else _path_ref(path, base_dir=base_dir, include_local_paths=False),
        "sha256": sha256(path.read_bytes()).hexdigest(),
        "bytes": path.stat().st_size,
        "included_in_pack": included_in_pack,
    }
    if include_local_paths:
        record["absolute_path"] = str(path.resolve())
    return record


def _path_ref(value: Any, *, base_dir: Path | None, include_local_paths: bool) -> str | None:
    if not value:
        return None
    path = Path(str(value))
    if include_local_paths:
        return str(path.resolve())
    if base_dir:
        try:
            return path.resolve().relative_to(base_dir.resolve()).as_posix()
        except ValueError:
            pass
    return path.name


def _load_json(path_value: Any) -> dict[str, Any]:
    if not path_value:
        return {}
    path = Path(str(path_value))
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _tool_version() -> str:
    try:
        return importlib_metadata.version("spira-trust")
    except importlib_metadata.PackageNotFoundError:
        return "source-tree"


def _utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
