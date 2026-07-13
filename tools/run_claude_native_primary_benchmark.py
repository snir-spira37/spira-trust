from __future__ import annotations

import argparse
import json
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping

import run_claude_native_readiness as readiness


ROOT = Path(__file__).resolve().parents[1]
BENCHMARK_ROOT = ROOT / "research" / "multi_agent_benchmark"
TRACK_ROOT = BENCHMARK_ROOT / "claude_native"

AUTHORIZATION_PATH = TRACK_ROOT / "claude_native_primary_benchmark_authorization.md"
RESULTS_PATH = TRACK_ROOT / "claude_native_primary_results.json"
REPORT_PATH = TRACK_ROOT / "claude_native_primary_report.md"
PRIVATE_MANIFEST_PATH = TRACK_ROOT / "claude_native_primary_raw_private_manifest.json"
SESSION_MANIFEST_PATH = TRACK_ROOT / "claude_native_primary_session_manifest.json"

INPUT_MANIFEST_PATH = BENCHMARK_ROOT / "frozen_input_manifest.json"
CASE_MANIFEST_PATH = BENCHMARK_ROOT / "case_manifest.json"
RANDOMIZATION_MANIFEST_PATH = BENCHMARK_ROOT / "randomization_manifest_v1.json"
OUTPUT_SCHEMA_PATH = BENCHMARK_ROOT / "agent_output.schema.json"

PRIMARY_STATUS_COMPLETE = "CLAUDE_NATIVE_PRIMARY_BENCHMARK_COMPLETE"
PRIMARY_STATUS_INCOMPLETE = "CLAUDE_NATIVE_PRIMARY_BENCHMARK_INCOMPLETE"
PRIMARY_STATUS_INFRASTRUCTURE_BLOCKED = "CLAUDE_NATIVE_PRIMARY_BENCHMARK_INFRASTRUCTURE_BLOCKED"
PRIMARY_STATUS_AUTHORIZATION_REVISION_REQUIRED = "CLAUDE_NATIVE_PRIMARY_BENCHMARK_AUTHORIZATION_REVISION_REQUIRED"

PRIVATE_ROOT_PREFIX = "spira_claude_native_primary_private_"
MAX_INFRASTRUCTURE_RETRIES = 2


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Claude native 180-session primary benchmark with checkpoint/resume.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    parser.add_argument("--resume", action="store_true", help="Resume from the first unfinished frozen session.")
    parser.add_argument("--max-new-sessions", type=int, help="Optional operator cap for this invocation; leaves run INCOMPLETE.")
    args = parser.parse_args(argv)

    results = run_primary(
        private_root=Path(args.private_root) if args.private_root else None,
        resume=args.resume,
        max_new_sessions=args.max_new_sessions,
    )
    print(
        json.dumps(
            {
                "terminal_status": results["terminal_status"],
                "completed_sessions": results["completed_session_count"],
                "total_sessions": results["session_count"],
                "next_session_index": results["next_session_index"],
            },
            sort_keys=True,
        )
    )
    return 0 if results["terminal_status"] == PRIMARY_STATUS_COMPLETE else 1


def run_primary(*, private_root: Path | None = None, resume: bool = False, max_new_sessions: int | None = None) -> dict[str, Any]:
    started_at = readiness.utc_now()
    private_root = private_root or Path(tempfile.mkdtemp(prefix=PRIVATE_ROOT_PREFIX))
    if readiness._is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize_without_execution(started_at, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    planned_sessions = build_primary_plan()
    expected = readiness.expected_by_case()
    schema = json.loads(OUTPUT_SCHEMA_PATH.read_text(encoding="utf-8"))
    transport_schema = readiness.claude_transport_schema(schema)

    manifest = load_or_create_session_manifest(planned_sessions, resume=resume)
    results = load_or_create_results(started_at, planned_sessions, resume=resume)
    raw_manifest = load_or_create_raw_manifest(resume=resume)
    reconcile_manifest_with_results(manifest, results)

    pre_repo_state = readiness.repository_state()
    errors: list[str] = []
    executed_now = 0

    for entry in manifest["sessions"]:
        if entry["status"] == "COMPLETED":
            continue
        if entry["status"] == "INFRASTRUCTURE_FAILURE":
            errors.append("PERSISTENT_INFRASTRUCTURE_FAILURE_PRESENT")
            break
        if max_new_sessions is not None and executed_now >= max_new_sessions:
            break

        result = execute_planned_session(
            entry,
            planned_sessions[entry["session_index"] - 1],
            expected,
            schema,
            transport_schema,
            private_root,
            raw_manifest,
            manifest,
            results,
        )
        executed_now += 1
        if result.get("persistent_infrastructure_failure"):
            errors.append("PERSISTENT_INFRASTRUCTURE_FAILURE_PRESENT")
            break

    if readiness.repository_state() != pre_repo_state:
        errors.append("CLAUDE_NATIVE_PRIMARY_REPOSITORY_MUTATION_OBSERVED")

    return finalize_results(started_at, manifest, results, raw_manifest, errors)


def build_primary_plan() -> list[dict[str, Any]]:
    input_manifest = json.loads(INPUT_MANIFEST_PATH.read_text(encoding="utf-8"))
    randomization = json.loads(RANDOMIZATION_MANIFEST_PATH.read_text(encoding="utf-8"))

    inputs = {
        (item["domain"], item["case_id"], item["arm"]): item
        for item in input_manifest["inputs"]
        if item.get("allocation") == "primary"
    }

    case_manifest = json.loads(CASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    case_domains = {
        case["case_id"]: case["domain"]
        for case in case_manifest["cases"]
        if case.get("allocation") == "primary"
    }

    primary_order = randomization["primary_execution_order_seeded"]
    arm_order = randomization["arm_order_seeded"]
    repetitions = int(randomization["primary_repetitions"])

    sessions: list[dict[str, Any]] = []
    session_index = 1
    for repetition in range(1, repetitions + 1):
        for case_id in primary_order:
            domain = case_domains[case_id]
            for arm in arm_order:
                item = inputs[(domain, case_id, arm)]
                sessions.append(
                    {
                        "session_index": session_index,
                        "repetition": repetition,
                        "domain": domain,
                        "case_id": case_id,
                        "arm": arm,
                        "input_path": item["path"],
                        "input_sha256": item["input_sha256"],
                        "prompt_sha256": item["prompt_sha256"],
                    }
                )
                session_index += 1

    if len(sessions) != 180:
        raise RuntimeError(f"Expected 180 primary sessions, found {len(sessions)}")
    return sessions


def load_or_create_session_manifest(planned_sessions: list[dict[str, Any]], *, resume: bool) -> dict[str, Any]:
    plan_hash = plan_sha256(planned_sessions)
    if SESSION_MANIFEST_PATH.exists():
        manifest = json.loads(SESSION_MANIFEST_PATH.read_text(encoding="utf-8"))
        if manifest.get("plan_sha256") != plan_hash:
            raise RuntimeError("Existing session manifest plan hash does not match frozen primary plan")
        existing_plan = [strip_runtime_fields(item) for item in manifest["sessions"]]
        if existing_plan != planned_sessions:
            raise RuntimeError("Existing session manifest sessions do not match frozen primary plan")
        if not resume and any(item["status"] != "PENDING" for item in manifest["sessions"]):
            raise RuntimeError("Existing primary manifest is partially executed; rerun with --resume")
        return manifest

    manifest = {
        "schema": "SPIRA_CLAUDE_NATIVE_PRIMARY_SESSION_MANIFEST_V1",
        "status": "CLAUDE_NATIVE_PRIMARY_SESSION_MANIFEST_CREATED",
        "authorization": AUTHORIZATION_PATH.as_posix().replace("\\", "/"),
        "plan_sha256": plan_hash,
        "session_count": len(planned_sessions),
        "created_at_utc": readiness.utc_now(),
        "updated_at_utc": readiness.utc_now(),
        "completed_session_count": 0,
        "next_session_index": 1,
        "sessions": [
            {
                **session,
                "status": "PENDING",
                "attempt_count": 0,
                "attempts": [],
                "completed_at_utc": None,
                "result_recorded": False,
            }
            for session in planned_sessions
        ],
    }
    atomic_json_write(SESSION_MANIFEST_PATH, manifest)
    return manifest


def load_or_create_results(started_at: str, planned_sessions: list[dict[str, Any]], *, resume: bool) -> dict[str, Any]:
    if RESULTS_PATH.exists():
        results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
        if not resume and results.get("sessions"):
            raise RuntimeError("Existing primary results are partially executed; rerun with --resume")
        return results
    results = {
        "schema": "SPIRA_CLAUDE_NATIVE_PRIMARY_RESULTS_V1",
        "terminal_status": PRIMARY_STATUS_INCOMPLETE,
        "started_at_utc": started_at,
        "completed_at_utc": None,
        "authorization": AUTHORIZATION_PATH.as_posix().replace("\\", "/"),
        "plan_sha256": plan_sha256(planned_sessions),
        "session_count": len(planned_sessions),
        "completed_session_count": 0,
        "next_session_index": 1,
        "primary_sessions_started": 0,
        "holdout_sessions_started": 0,
        "carryover_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "sessions": [],
        "errors": [],
    }
    atomic_json_write(RESULTS_PATH, results)
    return results


def load_or_create_raw_manifest(*, resume: bool) -> list[dict[str, Any]]:
    if PRIVATE_MANIFEST_PATH.exists():
        data = json.loads(PRIVATE_MANIFEST_PATH.read_text(encoding="utf-8"))
        if isinstance(data, Mapping) and isinstance(data.get("raw_files"), list):
            return list(data["raw_files"])
        if isinstance(data, list):
            return list(data)
        if not resume:
            raise RuntimeError("Existing raw manifest has unexpected format")
    return []


def reconcile_manifest_with_results(manifest: dict[str, Any], results: dict[str, Any]) -> None:
    completed_indexes = {session["session_index"] for session in results.get("sessions", [])}
    changed = False
    for entry in manifest["sessions"]:
        if entry["session_index"] in completed_indexes and entry["status"] != "COMPLETED":
            entry["status"] = "COMPLETED"
            entry["result_recorded"] = True
            entry["completed_at_utc"] = entry.get("completed_at_utc") or readiness.utc_now()
            changed = True
        elif entry["status"] == "RUNNING" and entry["session_index"] not in completed_indexes:
            entry["status"] = "PENDING"
            changed = True
    if changed:
        update_manifest_counts(manifest)
        atomic_json_write(SESSION_MANIFEST_PATH, manifest)


def execute_planned_session(
    manifest_entry: dict[str, Any],
    planned: Mapping[str, Any],
    expected: Mapping[tuple[str, str], Mapping[str, Any]],
    schema: Mapping[str, Any],
    transport_schema: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
    manifest: dict[str, Any],
    results: dict[str, Any],
) -> dict[str, Any]:
    attempts: list[dict[str, Any]] = []
    final_session: dict[str, Any] | None = None
    max_attempts = MAX_INFRASTRUCTURE_RETRIES + 1

    for attempt_number in range(1, max_attempts + 1):
        manifest_entry["status"] = "RUNNING"
        manifest_entry["attempt_count"] = attempt_number
        manifest_entry["attempts"].append({"attempt": attempt_number, "started_at_utc": readiness.utc_now(), "status": "RUNNING"})
        update_manifest_counts(manifest)
        atomic_json_write(SESSION_MANIFEST_PATH, manifest)

        item = item_for_readiness_runner(planned)
        session = run_primary_session(
            item,
            expected[(planned["domain"], planned["case_id"])],
            schema,
            transport_schema,
            private_root,
            raw_manifest,
            repetition=int(planned["repetition"]),
            session_index=int(planned["session_index"]),
            attempt_number=attempt_number,
        )
        attempts.append(attempt_summary(session, attempt_number))
        manifest_entry["attempts"][-1] = attempts[-1]

        if not is_infrastructure_failure(session):
            final_session = session
            break
        if attempt_number >= max_attempts:
            final_session = session
            break

    assert final_session is not None
    persistent_infra = is_infrastructure_failure(final_session)
    final_session["persistent_infrastructure_failure"] = persistent_infra
    final_session["attempts"] = attempts
    results["sessions"].append(final_session)

    manifest_entry["status"] = "INFRASTRUCTURE_FAILURE" if persistent_infra else "COMPLETED"
    manifest_entry["completed_at_utc"] = readiness.utc_now()
    manifest_entry["result_recorded"] = True
    update_manifest_counts(manifest)
    update_results_counts(results, manifest)

    atomic_json_write(PRIVATE_MANIFEST_PATH, raw_manifest_payload(raw_manifest))
    atomic_json_write(RESULTS_PATH, results)
    atomic_json_write(SESSION_MANIFEST_PATH, manifest)
    REPORT_PATH.write_text(report_markdown(results, manifest), encoding="utf-8")
    return final_session


def run_primary_session(
    item: Mapping[str, Any],
    expected: Mapping[str, Any],
    schema: Mapping[str, Any],
    transport_schema: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
    *,
    repetition: int,
    session_index: int,
    attempt_number: int,
) -> dict[str, Any]:
    raw_start = len(raw_manifest)
    session = readiness.run_session(item, expected, schema, transport_schema, private_root, raw_manifest)
    for raw_item in raw_manifest[raw_start:]:
        raw_item["classification"] = str(raw_item.get("classification", "")).replace("READINESS", "PRIMARY")
    session["session_index"] = session_index
    session["repetition"] = repetition
    session["attempt_number"] = attempt_number
    session["phase"] = "PRIMARY"
    session["primary_scored"] = True
    session["arm_a_policy"] = "RAW_EVIDENCE_BASELINE_WITH_SAFETY_FLOOR"
    session["arm_a_operational_pass"] = arm_a_operational_pass(session) if session["arm"] == "A" else None
    session["strict_fidelity_pass"] = bool(session["comparison"].get("pass"))
    return session


def item_for_readiness_runner(planned: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "domain": planned["domain"],
        "case_id": planned["case_id"],
        "arm": planned["arm"],
        "path": planned["input_path"],
        "input_sha256": planned["input_sha256"],
        "prompt_sha256": planned["prompt_sha256"],
    }


def is_infrastructure_failure(session: Mapping[str, Any]) -> bool:
    usage = session.get("usage") if isinstance(session.get("usage"), Mapping) else {}
    return bool(
        session.get("returncode") != 0
        or not session.get("result_envelope_present")
        or not session.get("structured_output_present")
        or not usage.get("input_total_available")
    )


def arm_a_operational_pass(session: Mapping[str, Any]) -> bool:
    comparison = session.get("comparison") if isinstance(session.get("comparison"), Mapping) else {}
    checks = comparison.get("checks") if isinstance(comparison.get("checks"), Mapping) else {}
    usage = session.get("usage") if isinstance(session.get("usage"), Mapping) else {}
    return bool(
        session.get("schema_valid")
        and usage.get("input_total_available")
        and checks.get("gate")
        and checks.get("recommended_agent_action")
        and not comparison.get("false_proceed")
        and not session.get("workspace_mutated")
        and session.get("forbidden_tool_count") == 0
    )


def attempt_summary(session: Mapping[str, Any], attempt_number: int) -> dict[str, Any]:
    return {
        "attempt": attempt_number,
        "completed_at_utc": readiness.utc_now(),
        "status": "INFRASTRUCTURE_FAILURE" if is_infrastructure_failure(session) else "COMPLETED",
        "returncode": session.get("returncode"),
        "result_envelope_present": session.get("result_envelope_present"),
        "structured_output_present": session.get("structured_output_present"),
        "usage_available": usage_available(session),
        "raw_private_id": session.get("raw_private_id"),
    }


def update_manifest_counts(manifest: dict[str, Any]) -> None:
    completed = sum(1 for item in manifest["sessions"] if item["status"] == "COMPLETED")
    manifest["completed_session_count"] = completed
    manifest["next_session_index"] = next((item["session_index"] for item in manifest["sessions"] if item["status"] in {"PENDING", "RUNNING"}), None)
    manifest["updated_at_utc"] = readiness.utc_now()
    if completed == manifest["session_count"]:
        manifest["status"] = "CLAUDE_NATIVE_PRIMARY_SESSION_MANIFEST_COMPLETE"
    else:
        manifest["status"] = "CLAUDE_NATIVE_PRIMARY_SESSION_MANIFEST_IN_PROGRESS"


def update_results_counts(results: dict[str, Any], manifest: Mapping[str, Any]) -> None:
    sessions = results["sessions"]
    results["completed_session_count"] = len(sessions)
    results["primary_sessions_started"] = len(sessions)
    results["next_session_index"] = manifest.get("next_session_index")
    results["schema_valid_count"] = sum(1 for item in sessions if item.get("schema_valid"))
    results["result_envelope_count"] = sum(1 for item in sessions if item.get("result_envelope_present"))
    results["structured_output_count"] = sum(1 for item in sessions if item.get("structured_output_present"))
    results["usage_available_count"] = sum(1 for item in sessions if usage_available(item))
    results["false_proceed_count"] = sum(1 for item in sessions if false_proceed(item))
    results["forbidden_tool_count"] = sum(int(item.get("forbidden_tool_count") or 0) for item in sessions)
    results["workspace_mutation_count"] = sum(1 for item in sessions if item.get("workspace_mutated"))
    results["strict_fidelity_count"] = sum(1 for item in sessions if item.get("strict_fidelity_pass"))
    results["arm_b_strict_fidelity_count"] = sum(1 for item in sessions if item.get("arm") == "B" and item.get("strict_fidelity_pass"))
    results["arm_c_strict_fidelity_count"] = sum(1 for item in sessions if item.get("arm") == "C" and item.get("strict_fidelity_pass"))
    results["arm_a_operational_pass_count"] = sum(1 for item in sessions if item.get("arm") == "A" and item.get("arm_a_operational_pass"))
    results["persistent_infrastructure_failure_count"] = sum(1 for item in sessions if item.get("persistent_infrastructure_failure"))


def usage_available(session: Mapping[str, Any]) -> bool:
    usage = session.get("usage")
    return isinstance(usage, Mapping) and bool(usage.get("input_total_available"))


def false_proceed(session: Mapping[str, Any]) -> bool:
    comparison = session.get("comparison")
    return isinstance(comparison, Mapping) and bool(comparison.get("false_proceed"))


def finalize_results(
    started_at: str,
    manifest: dict[str, Any],
    results: dict[str, Any],
    raw_manifest: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    update_manifest_counts(manifest)
    update_results_counts(results, manifest)
    if errors:
        terminal = PRIMARY_STATUS_INFRASTRUCTURE_BLOCKED if "PERSISTENT_INFRASTRUCTURE_FAILURE_PRESENT" in errors else PRIMARY_STATUS_AUTHORIZATION_REVISION_REQUIRED
    elif results["completed_session_count"] == results["session_count"]:
        terminal = PRIMARY_STATUS_COMPLETE
    else:
        terminal = PRIMARY_STATUS_INCOMPLETE
    results["terminal_status"] = terminal
    results["errors"] = sorted(set(errors))
    results["completed_at_utc"] = readiness.utc_now()
    results["started_at_utc"] = results.get("started_at_utc") or started_at
    results["raw_private_manifest"] = raw_manifest_payload(raw_manifest)
    atomic_json_write(PRIVATE_MANIFEST_PATH, results["raw_private_manifest"])
    atomic_json_write(RESULTS_PATH, results)
    atomic_json_write(SESSION_MANIFEST_PATH, manifest)
    REPORT_PATH.write_text(report_markdown(results, manifest), encoding="utf-8")
    return results


def finalize_without_execution(started_at: str, errors: list[str]) -> dict[str, Any]:
    planned = build_primary_plan()
    results = {
        "schema": "SPIRA_CLAUDE_NATIVE_PRIMARY_RESULTS_V1",
        "terminal_status": PRIMARY_STATUS_AUTHORIZATION_REVISION_REQUIRED,
        "started_at_utc": started_at,
        "completed_at_utc": readiness.utc_now(),
        "authorization": AUTHORIZATION_PATH.as_posix().replace("\\", "/"),
        "plan_sha256": plan_sha256(planned),
        "session_count": len(planned),
        "completed_session_count": 0,
        "next_session_index": 1,
        "primary_sessions_started": 0,
        "holdout_sessions_started": 0,
        "carryover_sessions_started": 0,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
        "sessions": [],
        "errors": errors,
    }
    return results


def raw_manifest_payload(raw_files: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED",
        "raw_file_count": len(raw_files),
        "raw_files": raw_files,
    }


def report_markdown(results: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    sessions = results.get("sessions", [])
    return f"""# Claude Native Primary Benchmark Report

## Status

```text
{results.get("terminal_status", PRIMARY_STATUS_INCOMPLETE)}
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Summary

```text
session count:
{results.get("session_count")}

completed sessions:
{results.get("completed_session_count")}

next session index:
{results.get("next_session_index")}

schema valid:
{results.get("schema_valid_count", 0)} / {len(sessions)}

JSON result envelope:
{results.get("result_envelope_count", 0)} / {len(sessions)}

structured_output:
{results.get("structured_output_count", 0)} / {len(sessions)}

usage available:
{results.get("usage_available_count", 0)} / {len(sessions)}

strict fidelity:
{results.get("strict_fidelity_count", 0)} / {len(sessions)}

Arm B strict fidelity:
{results.get("arm_b_strict_fidelity_count", 0)}

Arm C strict fidelity:
{results.get("arm_c_strict_fidelity_count", 0)}

Arm A operational pass:
{results.get("arm_a_operational_pass_count", 0)}

false PROCEED:
{results.get("false_proceed_count", 0)}

workspace mutations:
{results.get("workspace_mutation_count", 0)}

forbidden tool calls:
{results.get("forbidden_tool_count", 0)}

persistent infrastructure failures:
{results.get("persistent_infrastructure_failure_count", 0)}
```

## Resume State

```text
manifest:
research/multi_agent_benchmark/claude_native/claude_native_primary_session_manifest.json

plan_sha256:
{manifest.get("plan_sha256")}

completed_session_count:
{manifest.get("completed_session_count")}

next_session_index:
{manifest.get("next_session_index")}
```

If interrupted, rerun the primary runner with `--resume`. The runner skips only
sessions marked `COMPLETED` in the manifest and resumes at `next_session_index`.

## Boundary

```text
Holdout:
NOT_STARTED

Carryover:
NOT_STARTED

Codex / DeepSeek tracks:
NOT_STARTED

Efficiency claim:
NOT_AUTHORIZED

Release / version / tag / PyPI:
NOT_AUTHORIZED
```
"""


def strip_runtime_fields(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "session_index": item["session_index"],
        "repetition": item["repetition"],
        "domain": item["domain"],
        "case_id": item["case_id"],
        "arm": item["arm"],
        "input_path": item["input_path"],
        "input_sha256": item["input_sha256"],
        "prompt_sha256": item["prompt_sha256"],
    }


def plan_sha256(planned_sessions: list[dict[str, Any]]) -> str:
    return readiness.sha256(readiness.canonical_json(planned_sessions).encode("utf-8"))


def atomic_json_write(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(f".{path.name}.{readiness.uuid.uuid4().hex}.tmp")
    tmp.write_text(json.dumps(value, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    last_error: PermissionError | None = None
    for attempt in range(20):
        try:
            tmp.replace(path)
            return
        except PermissionError as exc:
            last_error = exc
            time.sleep(0.1 * (attempt + 1))
    try:
        tmp.unlink(missing_ok=True)
    finally:
        if last_error is not None:
            raise last_error


if __name__ == "__main__":
    raise SystemExit(main())
