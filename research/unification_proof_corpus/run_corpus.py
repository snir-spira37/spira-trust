#!/usr/bin/env python3
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.request
import zipfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parents[2]
PEP770_TOOLS = REPO / "research" / "pep770_survey"
SOURCE = REPO / "source"
if str(PEP770_TOOLS) not in sys.path:
    sys.path.insert(0, str(PEP770_TOOLS))
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

import collect_corpus  # noqa: E402
from spira_core.unification_proof import (  # noqa: E402
    UnificationProofError,
    build_unification_proof,
    inclusion_proof,
    verify_inclusion,
)


DEFAULT_MANIFEST = "research/pep770_survey/results/snapshot_v3_2026-07-09_manifest.json"
DEFAULT_METHODOLOGY = "research/unification_proof_corpus_methodology.md"
SCHEMA_MATERIALIZED = "SPIRA_UNIFICATION_CORPUS_MATERIALIZED_WHEELS_V1"
SCHEMA_RAW_RESULTS = "SPIRA_UNIFICATION_CORPUS_RAW_RESULTS_V1"
SCHEMA_PUBLIC_RESULTS = "SPIRA_UNIFICATION_CORPUS_PUBLIC_RESULTS_V1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the SPIRA Unification Proof corpus experiment.")
    sub = parser.add_subparsers(dest="command", required=True)

    materialize_cmd = sub.add_parser("materialize", help="Freeze wheel downloads and SHA-256 records before evaluation.")
    materialize_cmd.add_argument("--manifest", default=DEFAULT_MANIFEST)
    materialize_cmd.add_argument("--methodology", default=DEFAULT_METHODOLOGY)
    materialize_cmd.add_argument("--work-dir", required=True)
    materialize_cmd.add_argument("--output", required=True)
    materialize_cmd.add_argument("--limit", type=int)
    materialize_cmd.add_argument("--sleep", type=float, default=0.2)
    materialize_cmd.add_argument("--resume", action="store_true")
    materialize_cmd.add_argument("--keep-wheels", action="store_true")

    evaluate_cmd = sub.add_parser("evaluate", help="Evaluate Unification Proof V1 against a frozen materialized manifest.")
    evaluate_cmd.add_argument("--materialized-manifest", required=True)
    evaluate_cmd.add_argument("--methodology", default=DEFAULT_METHODOLOGY)
    evaluate_cmd.add_argument("--work-dir", required=True)
    evaluate_cmd.add_argument("--raw-output", required=True)
    evaluate_cmd.add_argument("--public-output")
    evaluate_cmd.add_argument("--limit", type=int)
    evaluate_cmd.add_argument("--sleep", type=float, default=0.2)
    evaluate_cmd.add_argument("--resume", action="store_true")
    evaluate_cmd.add_argument("--keep-wheels", action="store_true")
    evaluate_cmd.add_argument("--keep-spira-outputs", action="store_true")

    args = parser.parse_args(argv)
    if args.command == "materialize":
        return materialize(args)
    if args.command == "evaluate":
        return evaluate(args)
    raise SystemExit(f"unknown command: {args.command}")


def materialize(args: argparse.Namespace) -> int:
    manifest_path = Path(args.manifest)
    work_dir = Path(args.work_dir)
    wheels_dir = work_dir / "wheels"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    output = Path(args.output)

    source_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    picks = selected_wheels(source_manifest)
    if args.limit:
        picks = picks[: args.limit]

    report = load_or_create_materialized(
        output,
        resume=args.resume,
        source_manifest=manifest_path,
        methodology=args.methodology,
        work_dir=work_dir,
        limit=args.limit,
        keep_wheels=bool(args.keep_wheels),
    )
    completed = {str(item.get("filename")) for item in report.get("entries", []) if isinstance(item, dict)}

    for index, pick in enumerate(picks, start=1):
        if str(pick.get("filename")) in completed:
            continue
        entry = materialize_one(index, pick, wheels_dir=wheels_dir, keep_wheel=bool(args.keep_wheels))
        report["entries"].append(entry)
        report["completed_at"] = now()
        report["summary"] = summarize_materialized(report["entries"])
        write_json(output, report)
        print(f"{len(report['entries'])}/{len(picks)} {pick['package']} {entry.get('download_status')}", flush=True)
        time.sleep(args.sleep)

    report["completed_at"] = now()
    report["summary"] = summarize_materialized(report["entries"])
    write_json(output, report)
    print(f"wrote {output} with {len(report['entries'])} materialized entries")
    return 0


def evaluate(args: argparse.Namespace) -> int:
    manifest_path = Path(args.materialized_manifest)
    work_dir = Path(args.work_dir)
    wheels_dir = work_dir / "wheels"
    outputs_dir = work_dir / "spira_outputs"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    materialized = json.loads(manifest_path.read_text(encoding="utf-8"))
    entries = [item for item in materialized.get("entries") or [] if isinstance(item, dict)]
    if args.limit:
        entries = entries[: args.limit]

    raw_output = Path(args.raw_output)
    report = load_or_create_results(
        raw_output,
        resume=args.resume,
        materialized_manifest=manifest_path,
        methodology=args.methodology,
        work_dir=work_dir,
        limit=args.limit,
    )
    completed = {str(item.get("filename")) for item in report.get("results", []) if isinstance(item, dict)}

    for index, entry in enumerate(entries, start=1):
        if str(entry.get("filename")) in completed:
            continue
        result = evaluate_one(
            index,
            entry,
            wheels_dir=wheels_dir,
            outputs_dir=outputs_dir,
            keep_wheel=bool(args.keep_wheels),
            keep_spira_outputs=bool(args.keep_spira_outputs),
        )
        report["results"].append(result)
        report["completed_at"] = now()
        report["summary"] = summarize_results(report["results"])
        report["fixture_checks"] = fixture_checks()
        write_json(raw_output, report)
        if args.public_output:
            write_json(Path(args.public_output), public_report(report))
        print(f"{len(report['results'])}/{len(entries)} {entry.get('package')} {result.get('status')}", flush=True)
        time.sleep(args.sleep)

    report["completed_at"] = now()
    report["summary"] = summarize_results(report["results"])
    report["fixture_checks"] = fixture_checks()
    write_json(raw_output, report)
    if args.public_output:
        write_json(Path(args.public_output), public_report(report))
    print(f"wrote {raw_output} with {len(report['results'])} results")
    return 0


def selected_wheels(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    picks = []
    for entry in manifest.get("packages") or []:
        if entry.get("selection_status") == "SELECTED" and entry.get("selected_wheel"):
            picks.append(dict(entry["selected_wheel"]))
    return picks


def load_or_create_materialized(
    path: Path,
    *,
    resume: bool,
    source_manifest: Path,
    methodology: str,
    work_dir: Path,
    limit: int | None,
    keep_wheels: bool,
) -> dict[str, Any]:
    if resume and path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing["resumed_at"] = now()
        return existing
    return {
        "schema": SCHEMA_MATERIALIZED,
        "started_at": now(),
        "completed_at": None,
        "methodology": portable_path(methodology),
        "source_manifest": portable_path(source_manifest),
        "work_dir": portable_path(work_dir),
        "limit": limit,
        "keep_wheels": keep_wheels,
        "entries": [],
        "summary": {},
        "not_claimed": [
            "download materialization freezes bytes and SHA-256 records before unification results are computed",
            "availability or download failure is not a package trust finding",
        ],
    }


def load_or_create_results(
    path: Path,
    *,
    resume: bool,
    materialized_manifest: Path,
    methodology: str,
    work_dir: Path,
    limit: int | None,
) -> dict[str, Any]:
    if resume and path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing["resumed_at"] = now()
        return existing
    return {
        "schema": SCHEMA_RAW_RESULTS,
        "started_at": now(),
        "completed_at": None,
        "methodology": portable_path(methodology),
        "materialized_manifest": portable_path(materialized_manifest),
        "work_dir": portable_path(work_dir),
        "limit": limit,
        "results": [],
        "summary": {},
        "fixture_checks": {},
        "not_claimed": not_claimed(),
    }


def materialize_one(index: int, pick: Mapping[str, Any], *, wheels_dir: Path, keep_wheel: bool) -> dict[str, Any]:
    filename = str(pick["filename"])
    target = wheels_dir / filename
    entry: dict[str, Any] = {
        "index": index,
        "package": pick.get("package"),
        "version": pick.get("version"),
        "filename": filename,
        "url": pick.get("url"),
        "expected_sha256": pick.get("sha256"),
        "expected_size": pick.get("size"),
        "downloaded_at": now(),
        "download_status": None,
        "retained": keep_wheel,
    }
    try:
        digest, size = download_to_path(str(pick["url"]), target)
        entry["downloaded_sha256"] = digest
        entry["downloaded_bytes"] = size
        entry["sha256_matches_expected"] = digest == pick.get("sha256")
        entry["size_matches_expected"] = size == pick.get("size")
        entry["download_status"] = "DOWNLOAD_OK" if entry["sha256_matches_expected"] else "SHA256_MISMATCH"
        if keep_wheel and entry["download_status"] == "DOWNLOAD_OK":
            entry["local_path"] = portable_path(target)
        if not keep_wheel and target.exists():
            target.unlink()
    except Exception as exc:
        entry["download_status"] = "DOWNLOAD_ERROR"
        entry["download_error"] = repr(exc)
        if target.exists():
            target.unlink()
    return entry


def evaluate_one(
    index: int,
    entry: Mapping[str, Any],
    *,
    wheels_dir: Path,
    outputs_dir: Path,
    keep_wheel: bool,
    keep_spira_outputs: bool,
) -> dict[str, Any]:
    result: dict[str, Any] = {
        "index": index,
        "package": entry.get("package"),
        "version": entry.get("version"),
        "filename": entry.get("filename"),
        "wheel_sha256": entry.get("downloaded_sha256"),
        "status": None,
    }
    if entry.get("download_status") != "DOWNLOAD_OK":
        result["status"] = "CORPUS_UNAVAILABLE"
        result["unavailable_reason"] = entry.get("download_status")
        return result

    filename = str(entry["filename"])
    wheel_path = wheels_dir / filename
    output_dir = outputs_dir / safe_dir_name(index, str(entry.get("package") or filename))
    try:
        ensure_wheel(entry, wheel_path)
        output_dir.mkdir(parents=True, exist_ok=True)
        result["spira"] = run_spira(wheel_path, output_dir)
        if result["spira"].get("tool_error"):
            result["status"] = "TOOL_ERROR"
            return result
        result.update(evaluate_unification_outputs(output_dir))
        result["status"] = "PASS" if result["correctness"]["all_passed"] else "UNIFICATION_CORPUS_FAIL"
    except Exception as exc:
        result["status"] = "TOOL_ERROR"
        result["tool_error"] = repr(exc)
    finally:
        if not keep_wheel and wheel_path.exists():
            wheel_path.unlink()
        if not keep_spira_outputs and output_dir.exists():
            shutil.rmtree(output_dir)
    return result


def ensure_wheel(entry: Mapping[str, Any], target: Path) -> None:
    expected_sha = str(entry.get("downloaded_sha256") or "")
    if target.exists() and sha256_file(target) == expected_sha:
        return
    digest, _size = download_to_path(str(entry["url"]), target)
    if digest != expected_sha:
        raise ValueError(f"downloaded wheel sha256 mismatch for {entry.get('filename')}: {digest} != {expected_sha}")


def run_spira(wheel_path: Path, output_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    env["PYTHONPATH"] = str(SOURCE) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    evidence_pack = output_dir / "evidence_pack.zip"
    command = [
        sys.executable,
        "-m",
        "spira_core.trust_cli",
        "graph",
        str(wheel_path),
        "--output-dir",
        str(output_dir),
        "--verify-embedded-sboms",
        "--evidence-pack",
        str(evidence_pack),
    ]
    completed = subprocess.run(command, cwd=REPO, env=env, text=True, capture_output=True, timeout=900)
    paths = find_output_paths(output_dir)
    payload: dict[str, Any] = {
        "command": portable_command(command),
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-1000:],
        "stderr_tail": completed.stderr[-1000:],
        **paths,
    }
    if completed.returncode not in {0, 1, 2, 3, 4, 5, 6} or not paths.get("agent_summary_path"):
        payload["tool_error"] = "spira command failed or agent_summary.json was not produced"
    return payload


def evaluate_unification_outputs(output_dir: Path) -> dict[str, Any]:
    summary_path = first_path(output_dir, "agent_summary.json")
    decision_path = first_path(output_dir, "spira-decision.json")
    proof_path = first_path(output_dir, "unification_proof.json")
    pack_path = first_path(output_dir, "evidence_pack.zip")
    if not summary_path or not decision_path or not proof_path:
        raise ValueError("missing required unification output")
    summary = read_json(summary_path)
    decision = read_json(decision_path)
    proof = read_json(proof_path)
    started = time.perf_counter()
    rebuilt_a = build_unification_proof(summary, decision)
    generation_time_ms = round((time.perf_counter() - started) * 1000, 3)
    rebuilt_b = build_unification_proof(copy.deepcopy(summary), copy.deepcopy(decision))
    selected_claim = select_claim(proof.get("claims") or [])
    selected_proof = inclusion_proof(proof.get("claims") or [], str(selected_claim["claim_id"]))
    tampered_claim = copy.deepcopy(selected_claim)
    tampered_claim["status"] = "BLOCK" if tampered_claim.get("status") != "BLOCK" else "OK"

    correctness = {
        "action_equivalence": action_equivalence(summary, proof),
        "reproducibility": reproducibility(rebuilt_a, rebuilt_b),
        "disk_matches_rebuilt": proof_identity(proof) == proof_identity(rebuilt_a),
        "inclusion_verifies": verify_inclusion(selected_claim, selected_proof),
        "inclusion_rejects_mutation": not verify_inclusion(tampered_claim, selected_proof),
        "not_evaluated_preserved": same_string_set(
            proof.get("decision", {}).get("not_evaluated"),
            summary.get("agent_action_contract", {}).get("not_evaluated"),
        ),
        "block_preserved": block_preserved(summary, proof),
        "mutation_changes_identity": mutation_changes_identity(summary, decision, proof),
    }
    correctness["all_passed"] = all(bool(value) for value in correctness.values())

    return {
        "combined_verdict": summary.get("combined_verdict"),
        "action_verdict": summary.get("action_verdict"),
        "stop": summary.get("stop"),
        "recommended_agent_action": summary.get("recommended_agent_action"),
        "reason_codes": summary.get("reason_codes") or [],
        "not_evaluated": summary.get("not_evaluated") or [],
        "proof_generated": True,
        "claim_count": len(proof.get("claims") or []),
        "worst_claim_status": (proof.get("coverage") or {}).get("worst_claim_status"),
        "claims_merkle_root": (proof.get("roots") or {}).get("claims_merkle_root"),
        "unification_id": proof.get("unification_id"),
        "compact_reference_bytes": len(json.dumps(summary.get("unification") or {}, separators=(",", ":")).encode("utf-8")),
        "agent_summary_bytes": summary_path.stat().st_size,
        "full_proof_bytes": proof_path.stat().st_size,
        "evidence_pack_bytes": pack_path.stat().st_size if pack_path else None,
        "evidence_pack_unification_entry": zip_entry_sizes(pack_path, "unification_proof.json") if pack_path else None,
        "generation_time_ms": generation_time_ms,
        "correctness": correctness,
    }


def action_equivalence(summary: Mapping[str, Any], proof: Mapping[str, Any]) -> bool:
    contract = summary.get("agent_action_contract", {}) or {}
    decision = proof.get("decision", {}) or {}
    return all(
        [
            decision.get("verdict") == contract.get("action_verdict"),
            decision.get("stop") == contract.get("stop"),
            decision.get("recommended_agent_action") == contract.get("recommended_agent_action"),
            same_string_set(decision.get("reason_codes"), contract.get("reason_codes")),
            same_string_set(decision.get("not_evaluated"), contract.get("not_evaluated")),
            decision.get("semantics_version") == contract.get("decision_semantics_version"),
        ]
    )


def reproducibility(first: Mapping[str, Any], second: Mapping[str, Any]) -> bool:
    return proof_identity(first) == proof_identity(second)


def proof_identity(proof: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "claims_merkle_root": (proof.get("roots") or {}).get("claims_merkle_root"),
        "unification_id": proof.get("unification_id"),
        "decision": proof.get("decision"),
        "coverage": proof.get("coverage"),
    }


def mutation_changes_identity(summary: Mapping[str, Any], decision: Mapping[str, Any], proof: Mapping[str, Any]) -> bool:
    mutated = copy.deepcopy(decision)
    layers = ((mutated.get("layers") or {}).get("per_layer") or [])
    if not layers:
        return False
    original_status = layers[0].get("status")
    layers[0]["status"] = "NOTE" if original_status != "NOTE" else "WARN"
    try:
        changed = build_unification_proof(summary, mutated)
    except UnificationProofError:
        return True
    return (
        changed.get("unification_id") != proof.get("unification_id")
        or (changed.get("roots") or {}).get("claims_merkle_root") != (proof.get("roots") or {}).get("claims_merkle_root")
    )


def block_preserved(summary: Mapping[str, Any], proof: Mapping[str, Any]) -> bool:
    action_verdict = str(summary.get("action_verdict") or "")
    if "BLOCK" not in action_verdict:
        return True
    return bool((proof.get("decision") or {}).get("stop"))


def select_claim(claims: list[Mapping[str, Any]]) -> Mapping[str, Any]:
    if not claims:
        raise ValueError("proof contains no claims")
    for status in ("BLOCK", "NOT_EVALUATED"):
        matches = [claim for claim in claims if claim.get("status") == status]
        if matches:
            return sorted(matches, key=lambda item: str(item.get("claim_id") or ""))[0]
    return sorted(claims, key=lambda item: str(item.get("claim_id") or ""))[0]


def fixture_checks() -> dict[str, Any]:
    summary, decision = fixture_summary_decision()
    checks: dict[str, bool] = {}
    unknown = copy.deepcopy(decision)
    unknown["layers"]["per_layer"][0]["status"] = "TYPO_OK"
    checks["unknown_claim_status_fail_closed"] = raises_unification_error(summary, unknown)
    missing_subject = copy.deepcopy(summary)
    missing_subject["agent_action_contract"]["artifact_sha256"] = None
    missing_subject["agent_action_contract"]["artifact_set_sha256"] = None
    checks["missing_subject_hash_fail_closed"] = raises_unification_error(missing_subject, decision)
    duplicate = copy.deepcopy(decision)
    duplicate["layers"]["per_layer"].append(copy.deepcopy(duplicate["layers"]["per_layer"][0]))
    checks["duplicate_claim_id_fail_closed"] = raises_unification_error(summary, duplicate)
    checks["all_passed"] = all(checks.values())
    return {
        "schema": "SPIRA_UNIFICATION_CORPUS_FIXTURE_CHECKS_V1",
        "checks": checks,
    }


def raises_unification_error(summary: Mapping[str, Any], decision: Mapping[str, Any]) -> bool:
    try:
        build_unification_proof(summary, decision)
    except UnificationProofError:
        return True
    return False


def fixture_summary_decision() -> tuple[dict[str, Any], dict[str, Any]]:
    return (
        {
            "schema": "SPIRA_AGENT_SUMMARY_V1",
            "tool": {"name": "spira-trust", "version": "source-tree"},
            "agent_action_contract": {
                "schema": "SPIRA_AGENT_ACTION_V1",
                "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
                "artifact_sha256": "a" * 64,
                "artifact_set_sha256": "f" * 64,
                "policy_sha256": None,
                "command_fingerprint": "1" * 64,
                "graph_verdict": "GRAPH_OK",
                "combined_verdict": "GRAPH_OK_WITH_NOTES",
                "action_verdict": "GRAPH_OK_WITH_NOTES",
                "stop": True,
                "recommended_agent_action": "REPORT_NOT_EVALUATED",
                "reason_codes": ["REPORT_NOT_EVALUATED"],
                "not_evaluated": ["pep740_offline_attestations"],
            },
            "summary_of": {
                "tool_version": "source-tree",
                "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
                "decision_sha256": "2" * 64,
                "graph_report_sha256": "3" * 64,
            },
        },
        {
            "layers": {
                "per_layer": [
                    {
                        "layer": "graph_core",
                        "status": "OK",
                        "evaluated": True,
                        "source_verdict": "GRAPH_OK",
                        "evidence_ref": "graph_report.json",
                        "finding_count": 0,
                    },
                    {
                        "layer": "pep740_offline_attestations",
                        "status": "NOT_EVALUATED",
                        "evaluated": False,
                        "source_verdict": "ATTESTATION_NOT_EVALUATED",
                        "evidence_ref": "graph_report.json",
                        "finding_count": 0,
                    },
                ]
            }
        },
    )


def find_output_paths(output_dir: Path) -> dict[str, str | None]:
    return {
        "graph_report_path": portable_path_or_none(first_path(output_dir, "graph_report.json")),
        "decision_path": portable_path_or_none(first_path(output_dir, "spira-decision.json")),
        "agent_summary_path": portable_path_or_none(first_path(output_dir, "agent_summary.json")),
        "unification_proof_path": portable_path_or_none(first_path(output_dir, "unification_proof.json")),
        "evidence_pack_path": portable_path_or_none(first_path(output_dir, "evidence_pack.zip")),
    }


def first_path(root: Path, name: str) -> Path | None:
    matches = list(root.rglob(name))
    return matches[0] if matches else None


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"expected object in {path}")
    return data


def download_to_path(url: str, target: Path) -> tuple[str, int]:
    request = urllib.request.Request(url, headers={"User-Agent": collect_corpus.USER_AGENT})
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_suffix(target.suffix + ".tmp")
    digest = hashlib.sha256()
    size = 0
    with urllib.request.urlopen(request, timeout=300) as response, tmp.open("wb") as handle:
        while True:
            chunk = response.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
            size += len(chunk)
            handle.write(chunk)
    tmp.replace(target)
    return digest.hexdigest(), size


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def zip_entry_sizes(path: Path | None, name: str) -> dict[str, int] | None:
    if not path or not path.is_file():
        return None
    with zipfile.ZipFile(path) as archive:
        try:
            info = archive.getinfo(name)
        except KeyError:
            return None
        return {"file_size": info.file_size, "compress_size": info.compress_size}


def summarize_materialized(entries: list[Mapping[str, Any]]) -> dict[str, Any]:
    counts = count_by(entries, "download_status")
    return {
        "entry_count": len(entries),
        "download_status_counts": counts,
        "download_ok_count": counts.get("DOWNLOAD_OK", 0),
        "download_error_count": counts.get("DOWNLOAD_ERROR", 0),
        "sha256_mismatch_count": counts.get("SHA256_MISMATCH", 0),
        "bytes_downloaded": sum(int(item.get("downloaded_bytes") or 0) for item in entries),
    }


def summarize_results(results: list[Mapping[str, Any]]) -> dict[str, Any]:
    counts = count_by(results, "status")
    evaluated = [item for item in results if item.get("status") in {"PASS", "UNIFICATION_CORPUS_FAIL"}]
    correctness_keys = [
        "action_equivalence",
        "reproducibility",
        "disk_matches_rebuilt",
        "inclusion_verifies",
        "inclusion_rejects_mutation",
        "not_evaluated_preserved",
        "block_preserved",
        "mutation_changes_identity",
    ]
    failures = {key: 0 for key in correctness_keys}
    for item in evaluated:
        correctness = item.get("correctness") or {}
        for key in correctness_keys:
            if correctness.get(key) is not True:
                failures[key] += 1
    return {
        "processed": len(results),
        "status_counts": counts,
        "evaluated_count": len(evaluated),
        "correctness_failures": failures,
        "compact_reference_bytes": describe_ints([int(item["compact_reference_bytes"]) for item in evaluated if isinstance(item.get("compact_reference_bytes"), int)]),
        "agent_summary_bytes": describe_ints([int(item["agent_summary_bytes"]) for item in evaluated if isinstance(item.get("agent_summary_bytes"), int)]),
        "full_proof_bytes": describe_ints([int(item["full_proof_bytes"]) for item in evaluated if isinstance(item.get("full_proof_bytes"), int)]),
        "evidence_pack_bytes": describe_ints([int(item["evidence_pack_bytes"]) for item in evaluated if isinstance(item.get("evidence_pack_bytes"), int)]),
        "generation_time_ms": describe_numbers(
            [float(item["generation_time_ms"]) for item in evaluated if isinstance(item.get("generation_time_ms"), (int, float))]
        ),
    }


def public_report(report: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema": SCHEMA_PUBLIC_RESULTS,
        "started_at": report.get("started_at"),
        "completed_at": report.get("completed_at"),
        "methodology": report.get("methodology"),
        "materialized_manifest": report.get("materialized_manifest"),
        "public_scope": "aggregate unification proof corpus results only",
        "summary": summarize_results(report.get("results") or []),
        "fixture_checks": report.get("fixture_checks"),
        "redaction": [
            "Raw per-package results are kept under work/ and are not committed by default.",
            "Named package findings are not public package defects without manual review.",
        ],
        "not_claimed": not_claimed(),
    }


def count_by(items: list[Mapping[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(item.get(key))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def describe_ints(values: list[int]) -> dict[str, int | None]:
    if not values:
        return {"count": 0, "median": None, "p90": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "median": ordered[len(ordered) // 2],
        "p90": ordered[min(len(ordered) - 1, int(len(ordered) * 0.9))],
        "max": ordered[-1],
    }


def describe_numbers(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "median": None, "p90": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "median": round(ordered[len(ordered) // 2], 3),
        "p90": round(ordered[min(len(ordered) - 1, int(len(ordered) * 0.9))], 3),
        "max": round(ordered[-1], 3),
    }


def list_or_empty(value: Any) -> list[Any]:
    return list(value or [])


def same_string_set(left: Any, right: Any) -> bool:
    return sorted(dict.fromkeys(str(item) for item in list_or_empty(left))) == sorted(
        dict.fromkeys(str(item) for item in list_or_empty(right))
    )


def safe_dir_name(index: int, package: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "-_" else "_" for char in package)
    return f"{index:05d}_{cleaned}"


def portable_command(command: list[str]) -> list[str]:
    portable = command[:]
    if portable:
        portable[0] = Path(portable[0]).name
    return [portable_path(item) if "\\" in item or "/" in item else item for item in portable]


def portable_path_or_none(path: Path | None) -> str | None:
    return portable_path(path) if path else None


def portable_path(path: str | Path) -> str:
    raw = Path(path)
    try:
        return raw.resolve().relative_to(REPO).as_posix()
    except (OSError, ValueError):
        return str(raw).replace("\\", "/")


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def not_claimed() -> list[str]:
    return [
        "unification proof binds typed claims, policy/context roots, and action; it is not a safety proof",
        "this experiment does not prove SBOM correctness or package safety",
        "size metrics are byte counts, not live-agent token, latency, energy, or CO2 claims",
        "the experiment covers one existing Python wheel evidence domain, not a universal Context Firewall",
    ]


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
