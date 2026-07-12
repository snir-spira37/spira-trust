#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
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

from research.unification_proof_corpus import materialize_identity_baseline as baseline  # noqa: E402
from research.unification_proof_corpus import run_corpus  # noqa: E402
from spira_core.unification_proof import assemble_unification_proof, canonical_bytes  # noqa: E402


SCHEMA = "SPIRA_GATE_A_RETRY_REGRESSION_V1"
RUNNER_VERSION = "0.1"
BASELINE_ROOT = "85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c"
DEFAULT_BASELINE = "research/unification_proof_corpus/results/domain1_identity_baseline_v1.json"
DEFAULT_MATERIALIZED = "research/unification_proof_corpus/results/materialized_v1_2026-07-12.json"
DEFAULT_OUTPUT = "research/unification_proof_corpus/results/gate_a_retry_regression_v1.json"
DEFAULT_WORK_DIR = "work/gate_a_retry_regression"

IDENTITY_FIELDS = [
    "canonical_claims_bytes_sha256",
    "claims_merkle_root",
    "context_sha256",
    "canonical_decision_bytes_sha256",
    "unification_id",
    "compact_reference_bytes_sha256",
    "canonical_proof_bytes_sha256",
    "stop",
    "recommended_agent_action",
    "reason_codes",
    "not_evaluated",
    "worst_claim_status",
]


class GateARegressionError(RuntimeError):
    pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Gate A isolated regression and legacy regeneration audit.")
    parser.add_argument("--baseline", default=DEFAULT_BASELINE)
    parser.add_argument("--materialized-manifest", default=DEFAULT_MATERIALIZED)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--sleep", type=float, default=0.05)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--keep-wheels", action="store_true")
    parser.add_argument("--keep-spira-outputs", action="store_true")
    args = parser.parse_args(argv)

    try:
        run(args)
    except GateARegressionError as exc:
        print(f"GATE_A_RETRY_REGRESSION_FAILED: {exc}", file=sys.stderr)
        return 2
    return 0


def run(args: argparse.Namespace) -> None:
    baseline_path = (REPO / args.baseline).resolve()
    materialized_path = (REPO / args.materialized_manifest).resolve()
    output_path = (REPO / args.output).resolve()
    work_dir = (REPO / args.work_dir).resolve()
    wheels_dir = work_dir / "wheels"
    outputs_dir = work_dir / "spira_outputs"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    accepted = read_json(baseline_path)
    materialized = read_json(materialized_path)
    expected_records = accepted_records(accepted)
    entries = [item for item in materialized.get("entries") or [] if isinstance(item, dict)]
    if args.limit:
        entries = entries[: args.limit]
        entry_hashes = {str(entry.get("downloaded_sha256") or "") for entry in entries}
        expected_records = {key: value for key, value in expected_records.items() if key in entry_hashes}
    if len(entries) != len(expected_records):
        raise GateARegressionError(f"entry count does not match baseline: {len(entries)} != {len(expected_records)}")

    report = load_or_create_report(
        output_path,
        resume=bool(args.resume),
        baseline_path=baseline_path,
        materialized_path=materialized_path,
        expected_count=len(entries),
    )
    completed = {str(item.get("artifact_sha256")) for item in report.get("results", []) if isinstance(item, dict)}

    for index, entry in enumerate(entries, start=1):
        artifact_sha = str(entry.get("downloaded_sha256") or "")
        if artifact_sha in completed:
            continue
        expected = expected_records.get(artifact_sha)
        if not expected:
            raise GateARegressionError(f"missing expected baseline record for {artifact_sha}")
        result = evaluate_one(
            index,
            entry,
            expected,
            wheels_dir=wheels_dir,
            outputs_dir=outputs_dir,
            keep_wheel=bool(args.keep_wheels),
            keep_spira_outputs=bool(args.keep_spira_outputs),
        )
        report["results"].append(result)
        finalize_report(report, expected_records=expected_records)
        write_json(output_path, report)
        print(
            f"{len(report['results'])}/{len(entries)} {entry.get('package')} "
            f"isolated={result['isolated_status']} legacy_drift={len(result['legacy_drift_fields'])}",
            flush=True,
        )
        time.sleep(args.sleep)

    finalize_report(report, expected_records=expected_records)
    validate_report(report, expected_count=len(entries))
    write_json(output_path, report)
    print(f"wrote {output_path} with {len(report['results'])} results")


def evaluate_one(
    index: int,
    entry: Mapping[str, Any],
    expected: Mapping[str, Any],
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
        if baseline.sha256_file(wheel_path) != entry.get("downloaded_sha256"):
            raise GateARegressionError(f"wheel hash mismatch for {filename}")
        output_dir.mkdir(parents=True, exist_ok=True)
        spira = run_corpus.run_spira(wheel_path, output_dir)
        if spira.get("tool_error"):
            raise GateARegressionError(f"SPIRA tool error for {filename}: {spira.get('tool_error')}")

        current_legacy = baseline.identity_record(entry, output_dir)
        isolated = isolated_record(output_dir, expected)
        return {
            "artifact_sha256": expected["artifact_sha256"],
            "isolated_status": "MATCH" if records_match(isolated, expected) else "MISMATCH",
            "isolated_mismatched_fields": mismatched_fields(isolated, expected),
            "legacy_drift_fields": mismatched_fields(current_legacy, expected),
            "legacy_claims_equivalent": current_legacy.get("canonical_claims_bytes_sha256")
            == expected.get("canonical_claims_bytes_sha256"),
            "legacy_decision_equivalent": current_legacy.get("canonical_decision_bytes_sha256")
            == expected.get("canonical_decision_bytes_sha256"),
            "legacy_action_equivalent": action_equivalent(current_legacy, expected),
        }
    finally:
        if not keep_wheel and wheel_path.exists():
            run_corpus.safe_unlink(wheel_path)
        if not keep_spira_outputs and output_dir.exists():
            run_corpus.safe_rmtree(output_dir)


def isolated_record(output_dir: Path, expected: Mapping[str, Any]) -> dict[str, Any]:
    summary_path = run_corpus.first_path(output_dir, "agent_summary.json")
    proof_path = run_corpus.first_path(output_dir, "unification_proof.json")
    if not summary_path or not proof_path:
        raise GateARegressionError(f"missing SPIRA output under {output_dir}")
    summary = read_json(summary_path)
    proof = read_json(proof_path)
    claims = proof.get("claims") or []
    decision = proof.get("decision") or {}
    claims_hash = sha256_bytes(canonical_bytes(claims))
    decision_hash = sha256_bytes(canonical_bytes(decision))
    if claims_hash != expected.get("canonical_claims_bytes_sha256"):
        raise GateARegressionError(f"regenerated claims differ for {expected.get('artifact_sha256')}")
    if decision_hash != expected.get("canonical_decision_bytes_sha256"):
        raise GateARegressionError(f"regenerated decision differs for {expected.get('artifact_sha256')}")

    assembled = assemble_unification_proof(
        subject=proof["subject"],
        claims=claims,
        context={
            "policy_sha256": (proof.get("roots") or {}).get("policy_sha256"),
            "context_sha256": expected["context_sha256"],
        },
        decision=decision,
    )
    reference = dict(summary.get("unification") or {})
    reference["id"] = assembled["unification_id"]
    reference["root"] = assembled["roots"]["claims_merkle_root"]
    return {
        "artifact_sha256": assembled["subject"]["sha256"],
        "subject_type": assembled["subject"]["type"],
        "subject_sha256": assembled["subject"]["sha256"],
        "canonical_claims_bytes_sha256": sha256_bytes(canonical_bytes(assembled["claims"])),
        "claims_merkle_root": assembled["roots"]["claims_merkle_root"],
        "context_sha256": assembled["roots"]["context_sha256"],
        "canonical_decision_bytes_sha256": sha256_bytes(canonical_bytes(assembled["decision"])),
        "unification_id": assembled["unification_id"],
        "compact_reference_bytes_sha256": sha256_bytes(canonical_bytes(reference)),
        "canonical_proof_bytes_sha256": baseline.sha256_hex(baseline.stable_proof_identity_projection(assembled)),
        "stop": bool(assembled["decision"]["stop"]),
        "recommended_agent_action": assembled["decision"]["recommended_agent_action"],
        "reason_codes": sorted_unique_strings(assembled["decision"].get("reason_codes") or []),
        "not_evaluated": sorted_unique_strings(assembled["decision"].get("not_evaluated") or []),
        "worst_claim_status": assembled["coverage"]["worst_claim_status"],
    }


def records_match(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return not mismatched_fields(left, right)


def mismatched_fields(left: Mapping[str, Any], right: Mapping[str, Any]) -> list[str]:
    return [field for field in IDENTITY_FIELDS if left.get(field) != right.get(field)]


def action_equivalent(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
    return all(
        [
            left.get("stop") == right.get("stop"),
            left.get("recommended_agent_action") == right.get("recommended_agent_action"),
            left.get("reason_codes") == right.get("reason_codes"),
            left.get("not_evaluated") == right.get("not_evaluated"),
            left.get("worst_claim_status") == right.get("worst_claim_status"),
        ]
    )


def accepted_records(accepted: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    if accepted.get("domain1_identity_baseline_root") != BASELINE_ROOT:
        raise GateARegressionError("baseline root does not match accepted Gate A root")
    records = accepted.get("records") or []
    if not isinstance(records, list) or len(records) != baseline.EXPECTED_RECORD_COUNT:
        raise GateARegressionError("accepted baseline record count mismatch")
    return {str(record["artifact_sha256"]): record for record in records}


def load_or_create_report(
    path: Path,
    *,
    resume: bool,
    baseline_path: Path,
    materialized_path: Path,
    expected_count: int,
) -> dict[str, Any]:
    if resume and path.exists():
        existing = read_json(path)
        existing["resumed_at"] = now()
        return existing
    return {
        "schema": SCHEMA,
        "runner_version": RUNNER_VERSION,
        "started_at": now(),
        "completed_at": None,
        "implementation_commit": git(["rev-parse", "HEAD"]).strip(),
        "baseline_path": portable_path(baseline_path),
        "baseline_sha256": baseline.sha256_file(baseline_path),
        "accepted_baseline_root": BASELINE_ROOT,
        "materialized_manifest": portable_path(materialized_path),
        "materialized_manifest_sha256": baseline.sha256_file(materialized_path),
        "expected_count": expected_count,
        "results": [],
        "summary": {},
        "final_status": "GATE_A_RETRY_REGRESSION_RUNNING",
    }


def finalize_report(report: dict[str, Any], *, expected_records: Mapping[str, Mapping[str, Any]]) -> None:
    results = report.get("results") or []
    isolated_matches = [item for item in results if item.get("isolated_status") == "MATCH"]
    isolated_mismatches = [item for item in results if item.get("isolated_status") == "MISMATCH"]
    legacy_drift = [item for item in results if item.get("legacy_drift_fields")]
    legacy_claim_drift = [item for item in results if item.get("legacy_claims_equivalent") is not True]
    legacy_decision_drift = [item for item in results if item.get("legacy_decision_equivalent") is not True]
    legacy_action_drift = [item for item in results if item.get("legacy_action_equivalent") is not True]
    matched_records = [expected_records[str(item["artifact_sha256"])] for item in sorted(isolated_matches, key=lambda value: value["artifact_sha256"])]
    isolated_root = sha256_bytes(canonical_bytes(matched_records))
    expected_count = int(report.get("expected_count") or 0)
    report["completed_at"] = now()
    report["summary"] = {
        "expected_count": expected_count,
        "compared_count": len(results),
        "isolated_identity_match_count": len(isolated_matches),
        "isolated_identity_mismatch_count": len(isolated_mismatches),
        "isolated_identity_root": isolated_root,
        "isolated_identity_root_matches_baseline": isolated_root == BASELINE_ROOT
        and len(isolated_matches) == baseline.EXPECTED_RECORD_COUNT,
        "legacy_drift_count": len(legacy_drift),
        "legacy_claim_drift_count": len(legacy_claim_drift),
        "legacy_decision_drift_count": len(legacy_decision_drift),
        "legacy_action_drift_count": len(legacy_action_drift),
        "unique_artifact_hashes": len({str(item.get("artifact_sha256")) for item in results}),
    }
    report["final_status"] = (
        "GATE_A_ISOLATED_ASSEMBLY_REGRESSION_PASS"
        if len(isolated_matches) == expected_count
        and not isolated_mismatches
        and (expected_count != baseline.EXPECTED_RECORD_COUNT or isolated_root == BASELINE_ROOT)
        else "GATE_A_RETRY_REGRESSION_RUNNING"
    )


def validate_report(report: Mapping[str, Any], *, expected_count: int) -> None:
    summary = report.get("summary") or {}
    if summary.get("compared_count") != expected_count:
        raise GateARegressionError("regression did not compare every expected record")
    if summary.get("isolated_identity_match_count") != expected_count:
        raise GateARegressionError("isolated identity match count did not reach expected count")
    if summary.get("isolated_identity_mismatch_count") != 0:
        raise GateARegressionError("isolated identity mismatch detected")
    if expected_count == baseline.EXPECTED_RECORD_COUNT and summary.get("isolated_identity_root") != BASELINE_ROOT:
        raise GateARegressionError("isolated identity root changed")
    if summary.get("unique_artifact_hashes") != expected_count:
        raise GateARegressionError("unique artifact hash count mismatch")


def sorted_unique_strings(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise GateARegressionError("expected list")
    return sorted(dict.fromkeys(str(item) for item in value))


def read_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise GateARegressionError(f"expected JSON object: {path}")
    return data


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def git(args: list[str]) -> str:
    return subprocess.run(["git", *args], cwd=REPO, check=True, capture_output=True).stdout.decode("utf-8")


def portable_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO).as_posix()
    except (OSError, ValueError):
        return str(path).replace("\\", "/")


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
