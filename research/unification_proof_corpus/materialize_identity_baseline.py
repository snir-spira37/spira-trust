#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Mapping


REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "source"
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from research.unification_proof_corpus import run_corpus  # noqa: E402
from spira_core.unification_proof import (  # noqa: E402
    UNIFICATION_PROOF_SCHEMA,
    UNIFICATION_REFERENCE_SCHEMA,
    build_unification_proof,
    canonical_bytes,
    sha256_hex,
)


SCHEMA = "SPIRA_DOMAIN1_IDENTITY_BASELINE_V1"
SCHEMA_VERSION = "1.0"
RUNNER_NAME = "research/unification_proof_corpus/materialize_identity_baseline.py"
RUNNER_VERSION = "0.1"
BASELINE_COMMIT = "8049eb0eaf49c277b3835f569c7938d2c0ba3817"
EXPECTED_RECORD_COUNT = 1954
DEFAULT_MATERIALIZED = "research/unification_proof_corpus/results/materialized_v1_2026-07-12.json"
DEFAULT_PUBLIC_RESULTS = "research/unification_proof_corpus/results/full_v1_public_results.json"
DEFAULT_OUTPUT = "research/unification_proof_corpus/results/domain1_identity_baseline_v1.json"
DEFAULT_WORK_DIR = "work/domain1_identity_baseline_materialization"
VOLATILE_FIELDS_EXCLUDED = ["created_at"]
HASH_FIELDS = [
    "artifact_sha256",
    "subject_sha256",
    "canonical_claims_bytes_sha256",
    "claims_merkle_root",
    "context_sha256",
    "canonical_decision_bytes_sha256",
    "unification_id",
    "compact_reference_bytes_sha256",
    "canonical_proof_bytes_sha256",
]


class BaselineMaterializationError(RuntimeError):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Materialize the frozen Domain 1 identity baseline.")
    parser.add_argument("--materialized-manifest", default=DEFAULT_MATERIALIZED)
    parser.add_argument("--public-results", default=DEFAULT_PUBLIC_RESULTS)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--keep-wheels", action="store_true")
    parser.add_argument("--keep-spira-outputs", action="store_true")
    args = parser.parse_args(argv)

    try:
        materialize(args)
    except BaselineMaterializationError as exc:
        print(f"DOMAIN_1_IDENTITY_BASELINE_NOT_MATERIALIZABLE: {exc}", file=sys.stderr)
        return 2
    return 0


def materialize(args: argparse.Namespace) -> None:
    materialized_path = (REPO / args.materialized_manifest).resolve()
    public_results_path = (REPO / args.public_results).resolve()
    output_path = (REPO / args.output).resolve()
    work_dir = (REPO / args.work_dir).resolve()
    wheels_dir = work_dir / "wheels"
    outputs_dir = work_dir / "spira_outputs"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    verify_core_files_match_baseline()
    materialized = read_json(materialized_path)
    public_results = read_json(public_results_path)
    entries = validate_inputs(materialized, public_results)
    if args.limit:
        entries = entries[: args.limit]

    baseline = load_or_create_baseline(
        output_path,
        resume=bool(args.resume),
        materialized_path=materialized_path,
        public_results_path=public_results_path,
        entries=entries,
    )
    completed = {str(record.get("artifact_sha256")) for record in baseline.get("records", []) if isinstance(record, dict)}

    for index, entry in enumerate(entries, start=1):
        artifact_sha = str(entry.get("downloaded_sha256") or "")
        if artifact_sha in completed:
            continue
        record = materialize_one(
            index,
            entry,
            wheels_dir=wheels_dir,
            outputs_dir=outputs_dir,
            keep_wheel=bool(args.keep_wheels),
            keep_spira_outputs=bool(args.keep_spira_outputs),
        )
        baseline["records"].append(record)
        finalize_baseline_in_place(baseline)
        write_json(output_path, baseline)
        print(f"{len(baseline['records'])}/{len(entries)} {entry.get('package')} PASS", flush=True)
        time.sleep(args.sleep)

    finalize_baseline_in_place(baseline)
    validate_baseline(baseline, expected_count=len(entries))
    write_json(output_path, baseline)
    print(f"wrote {output_path} with {len(baseline['records'])} records")


def load_or_create_baseline(
    path: Path,
    *,
    resume: bool,
    materialized_path: Path,
    public_results_path: Path,
    entries: list[Mapping[str, Any]],
) -> dict[str, Any]:
    if resume and path.exists():
        existing = read_json(path)
        existing["resumed_at"] = now()
        return existing
    return {
        "schema": SCHEMA,
        "schema_version": SCHEMA_VERSION,
        "status": "DOMAIN_1_IDENTITY_BASELINE_MATERIALIZING",
        "baseline_commit": BASELINE_COMMIT,
        "current_commit": git(["rev-parse", "HEAD"]).strip(),
        "tool_version": "source-tree",
        "materialization_tool": {"name": RUNNER_NAME, "version": RUNNER_VERSION},
        "decision_semantics_version": "SPIRA_DECISION_SEMANTICS_V2",
        "unification_proof_schema": UNIFICATION_PROOF_SCHEMA,
        "unification_reference_schema": UNIFICATION_REFERENCE_SCHEMA,
        "corpus_manifest_sha256": sha256_file(REPO / "research/pep770_survey/results/snapshot_v3_2026-07-09_manifest.json"),
        "materialized_manifest_sha256": sha256_file(materialized_path),
        "public_results_sha256": sha256_file(public_results_path),
        "corpus_size": len(entries),
        "generation_timestamp": now(),
        "volatile_fields_excluded": VOLATILE_FIELDS_EXCLUDED,
        "canonicalization_contract": canonicalization_contract(),
        "record_ordering": "artifact_sha256 ascending",
        "baseline_root_construction": "sha256(canonical JSON array of records sorted by artifact_sha256)",
        "legacy_context_note": (
            "Domain 1 context_sha256 preserves the existing legacy context construction, "
            "including command_fingerprint behavior. This baseline is a fixed identity "
            "snapshot for this materialization path, not a cross-workdir normalization."
        ),
        "domain1_identity_baseline_root": None,
        "records": [],
        "validation": {},
        "not_claimed": [
            "this baseline records Domain 1 proof identity hashes; it is not a safety proof",
            "baseline materialization does not authorize Gate A implementation",
            "the runner uses the existing Python wheel Domain 1 path and does not create a generic assembler",
        ],
    }


def canonicalization_contract() -> dict[str, Any]:
    return {
        "encoding": "UTF-8",
        "json_keys": "sorted",
        "json_separators": [",", ":"],
        "json_whitespace": "none beyond canonical separators",
        "record_order": "artifact_sha256 ascending",
        "set_like_lists": "sorted unique strings",
        "volatile_fields_excluded": VOLATILE_FIELDS_EXCLUDED,
        "hash_format": "lowercase 64-character SHA-256",
        "proof_identity": "SHA256(stable proof identity projection)",
        "baseline_root": "SHA256(canonical JSON array of records sorted by artifact_sha256)",
    }


def validate_inputs(materialized: Mapping[str, Any], public_results: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    entries = [item for item in materialized.get("entries") or [] if isinstance(item, dict)]
    if len(entries) != EXPECTED_RECORD_COUNT:
        raise BaselineMaterializationError(f"record count != {EXPECTED_RECORD_COUNT}: {len(entries)}")
    summary = public_results.get("summary") or {}
    status_counts = summary.get("status_counts") or {}
    if status_counts.get("PASS") != EXPECTED_RECORD_COUNT:
        raise BaselineMaterializationError("public results do not record 1954 PASS results")
    seen: set[str] = set()
    for entry in entries:
        if entry.get("download_status") != "DOWNLOAD_OK":
            raise BaselineMaterializationError(f"non-ok materialized entry: {entry.get('filename')}")
        digest = str(entry.get("downloaded_sha256") or "")
        if not is_sha256(digest):
            raise BaselineMaterializationError(f"invalid materialized sha256 for {entry.get('filename')}")
        if digest in seen:
            raise BaselineMaterializationError(f"duplicate materialized sha256: {digest}")
        seen.add(digest)
        if entry.get("sha256_matches_expected") is not True:
            raise BaselineMaterializationError(f"materialized sha256 mismatch for {entry.get('filename')}")
    return entries


def materialize_one(
    index: int,
    entry: Mapping[str, Any],
    *,
    wheels_dir: Path,
    outputs_dir: Path,
    keep_wheel: bool,
    keep_spira_outputs: bool,
) -> dict[str, Any]:
    filename = str(entry.get("filename") or "")
    wheel_path = wheels_dir / filename
    output_dir = outputs_dir / run_corpus.safe_dir_name(index, str(entry.get("package") or filename))
    if output_dir.exists():
        run_corpus.safe_rmtree(output_dir)
    try:
        run_corpus.ensure_wheel(entry, wheel_path)
        digest = sha256_file(wheel_path)
        expected_digest = str(entry.get("downloaded_sha256") or "")
        if digest != expected_digest:
            raise BaselineMaterializationError(f"hash mismatch for {filename}: {digest} != {expected_digest}")
        output_dir.mkdir(parents=True, exist_ok=True)
        spira = run_corpus.run_spira(wheel_path, output_dir)
        if spira.get("tool_error"):
            raise BaselineMaterializationError(f"SPIRA tool error for {filename}: {spira.get('tool_error')}")
        record = identity_record(entry, output_dir)
        if record["artifact_sha256"] != expected_digest:
            raise BaselineMaterializationError(f"artifact sha mismatch in summary for {filename}")
        return record
    finally:
        if not keep_wheel and wheel_path.exists():
            run_corpus.safe_unlink(wheel_path)
        if not keep_spira_outputs and output_dir.exists():
            run_corpus.safe_rmtree(output_dir)


def identity_record(entry: Mapping[str, Any], output_dir: Path) -> dict[str, Any]:
    summary_path = run_corpus.first_path(output_dir, "agent_summary.json")
    decision_path = run_corpus.first_path(output_dir, "spira-decision.json")
    proof_path = run_corpus.first_path(output_dir, "unification_proof.json")
    if not summary_path or not decision_path or not proof_path:
        raise BaselineMaterializationError(f"missing identity output under {output_dir}")
    summary = read_json(summary_path)
    decision = read_json(decision_path)
    proof = read_json(proof_path)
    rebuilt = build_unification_proof(summary, decision)
    if stable_proof_identity_projection(proof) != stable_proof_identity_projection(rebuilt):
        raise BaselineMaterializationError(f"rebuilt proof identity differs for {entry.get('filename')}")

    claims = proof.get("claims")
    roots = proof.get("roots") or {}
    decision_obj = proof.get("decision") or {}
    coverage = proof.get("coverage") or {}
    reference = summary.get("unification") or {}
    if not isinstance(claims, list):
        raise BaselineMaterializationError("proof claims are missing")
    artifact_sha = str((proof.get("subject") or {}).get("sha256") or "")
    subject = proof.get("subject") or {}
    record = {
        "artifact_sha256": artifact_sha,
        "subject_type": require_string(subject.get("type"), "subject.type"),
        "subject_sha256": require_sha256(subject.get("sha256"), "subject.sha256"),
        "canonical_claims_bytes_sha256": sha256_bytes(canonical_bytes(claims)),
        "claims_merkle_root": require_sha256(roots.get("claims_merkle_root"), "claims_merkle_root"),
        "context_sha256": require_sha256(roots.get("context_sha256"), "context_sha256"),
        "canonical_decision_bytes_sha256": sha256_bytes(canonical_bytes(decision_obj)),
        "unification_id": require_sha256(proof.get("unification_id"), "unification_id"),
        "compact_reference_bytes_sha256": sha256_bytes(canonical_bytes(reference)),
        "canonical_proof_bytes_sha256": sha256_hex(stable_proof_identity_projection(proof)),
        "stop": bool(decision_obj.get("stop")),
        "recommended_agent_action": require_string(decision_obj.get("recommended_agent_action"), "recommended_agent_action"),
        "reason_codes": sorted_unique_strings(decision_obj.get("reason_codes") or []),
        "not_evaluated": sorted_unique_strings(decision_obj.get("not_evaluated") or []),
        "worst_claim_status": require_string(coverage.get("worst_claim_status"), "worst_claim_status"),
    }
    validate_record(record)
    return record


def stable_proof_identity_projection(proof: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "subject": proof.get("subject"),
        "canonical_claims_bytes_sha256": sha256_bytes(canonical_bytes(proof.get("claims") or [])),
        "claims_merkle_root": (proof.get("roots") or {}).get("claims_merkle_root"),
        "context_sha256": (proof.get("roots") or {}).get("context_sha256"),
        "canonical_decision_bytes_sha256": sha256_bytes(canonical_bytes(proof.get("decision") or {})),
        "unification_id": proof.get("unification_id"),
        "action": {
            "stop": (proof.get("decision") or {}).get("stop"),
            "recommended_agent_action": (proof.get("decision") or {}).get("recommended_agent_action"),
            "reason_codes": sorted_unique_strings((proof.get("decision") or {}).get("reason_codes") or []),
            "not_evaluated": sorted_unique_strings((proof.get("decision") or {}).get("not_evaluated") or []),
        },
        "coverage": {
            "worst_claim_status": (proof.get("coverage") or {}).get("worst_claim_status"),
            "claim_count": (proof.get("coverage") or {}).get("claim_count"),
        },
    }


def finalize_baseline_in_place(baseline: dict[str, Any]) -> None:
    records = sorted(baseline.get("records") or [], key=lambda item: str(item.get("artifact_sha256") or ""))
    baseline["records"] = records
    baseline["domain1_identity_baseline_root"] = sha256_bytes(canonical_bytes(records))
    baseline["status"] = (
        "DOMAIN_1_IDENTITY_BASELINE_MATERIALIZED"
        if len(records) == baseline.get("corpus_size")
        else "DOMAIN_1_IDENTITY_BASELINE_MATERIALIZING"
    )
    baseline["validation"] = validation_summary(records, expected_count=int(baseline.get("corpus_size") or 0))


def validate_baseline(baseline: Mapping[str, Any], *, expected_count: int) -> None:
    records = baseline.get("records") or []
    validation = validation_summary(records, expected_count=expected_count)
    if validation.get("record_count") != expected_count:
        raise BaselineMaterializationError("record count validation failed")
    if validation.get("unique_artifact_hashes") != expected_count:
        raise BaselineMaterializationError("unique artifact hash validation failed")
    if validation.get("missing_identity_fields") != 0:
        raise BaselineMaterializationError("missing identity field validation failed")
    if validation.get("hash_format_failures") != 0:
        raise BaselineMaterializationError("hash format validation failed")
    recomputed_root = sha256_bytes(canonical_bytes(sorted(records, key=lambda item: str(item.get("artifact_sha256") or ""))))
    if recomputed_root != baseline.get("domain1_identity_baseline_root"):
        raise BaselineMaterializationError("baseline root recomputation failed")


def validation_summary(records: Any, *, expected_count: int) -> dict[str, Any]:
    if not isinstance(records, list):
        return {"record_count": 0, "expected_count": expected_count, "records_are_list": False}
    artifact_hashes = [str(record.get("artifact_sha256") or "") for record in records if isinstance(record, dict)]
    missing = 0
    hash_failures = 0
    for record in records:
        if not isinstance(record, dict):
            missing += 1
            continue
        for field in [
            "artifact_sha256",
            "subject_sha256",
            "canonical_claims_bytes_sha256",
            "claims_merkle_root",
            "context_sha256",
            "canonical_decision_bytes_sha256",
            "unification_id",
            "compact_reference_bytes_sha256",
            "canonical_proof_bytes_sha256",
            "subject_type",
            "recommended_agent_action",
            "worst_claim_status",
        ]:
            if record.get(field) in {None, ""}:
                missing += 1
        for field in HASH_FIELDS:
            if not is_sha256(str(record.get(field) or "")):
                hash_failures += 1
    return {
        "record_count": len(records),
        "expected_count": expected_count,
        "unique_artifact_hashes": len(set(artifact_hashes)),
        "missing_identity_fields": missing,
        "hash_format_failures": hash_failures,
        "baseline_root_recomputes": True,
    }


def verify_core_files_match_baseline() -> None:
    paths = git(["ls-tree", "-r", "--name-only", BASELINE_COMMIT, "source/spira_core"]).splitlines()
    mismatches = []
    for path in paths:
        current = REPO / path
        if not current.is_file():
            mismatches.append(path)
            continue
        baseline_bytes = git_bytes(["show", f"{BASELINE_COMMIT}:{path}"])
        if hashlib.sha256(current.read_bytes()).hexdigest() != hashlib.sha256(baseline_bytes).hexdigest():
            mismatches.append(path)
    if mismatches:
        raise BaselineMaterializationError(f"core-file hash changed: {', '.join(mismatches[:10])}")


def validate_record(record: Mapping[str, Any]) -> None:
    for field in HASH_FIELDS:
        require_sha256(record.get(field), field)
    require_string(record.get("recommended_agent_action"), "recommended_agent_action")
    require_string(record.get("worst_claim_status"), "worst_claim_status")
    if not isinstance(record.get("stop"), bool):
        raise BaselineMaterializationError("stop must be boolean")
    sorted_unique_strings(record.get("reason_codes") or [])
    sorted_unique_strings(record.get("not_evaluated") or [])


def sorted_unique_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise BaselineMaterializationError("expected list")
    return sorted(dict.fromkeys(str(item) for item in value))


def require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value:
        raise BaselineMaterializationError(f"{field} is required")
    return value


def require_sha256(value: Any, field: str) -> str:
    text = require_string(value, field)
    if not is_sha256(text):
        raise BaselineMaterializationError(f"{field} must be lowercase SHA-256")
    return text


def is_sha256(value: str) -> bool:
    return len(value) == 64 and all(ch in "0123456789abcdef" for ch in value)


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise BaselineMaterializationError(f"expected JSON object: {path}")
    return data


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            chunk = handle.read(1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
    return digest.hexdigest()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(args: list[str]) -> str:
    return git_bytes(args).decode("utf-8")


def git_bytes(args: list[str]) -> bytes:
    completed = subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True)
    return completed.stdout


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
