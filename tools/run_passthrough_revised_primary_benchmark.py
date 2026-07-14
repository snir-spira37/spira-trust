from __future__ import annotations

import argparse
import json
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Mapping

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import run_passthrough_revised_readiness as readiness


ROOT = readiness.ROOT
BENCHMARK_ROOT = readiness.BENCHMARK_ROOT
CLAUDE_ROOT = readiness.CLAUDE_ROOT
CODEX_ROOT = readiness.CODEX_ROOT

AUTHORIZATION_PATH = BENCHMARK_ROOT / "machine_contract_passthrough_revised_primary_benchmark_authorization.md"
RANDOMIZATION_MANIFEST_PATH = BENCHMARK_ROOT / "randomization_manifest_v1.json"

AGENT_ORDER_PATH = BENCHMARK_ROOT / "machine_contract_passthrough_revised_primary_agent_order.json"
COMBINED_REPORT_PATH = BENCHMARK_ROOT / "machine_contract_passthrough_revised_primary_combined_report.md"
COMBINED_REVIEW_PATH = BENCHMARK_ROOT / "machine_contract_passthrough_revised_primary_combined_review.md"

MAX_INFRASTRUCTURE_RETRIES = 2
RESUMABLE_STATUSES = {"PENDING", "RUNNING", "RATE_LIMIT_BLOCKED"}
AGENT_ORDER = ["claude_native", "codex_native"]

AGENT_CONFIG = {
    "claude_native": {
        "root": CLAUDE_ROOT,
        "results": CLAUDE_ROOT / "passthrough_revised_primary_results.json",
        "report": CLAUDE_ROOT / "passthrough_revised_primary_report.md",
        "review": CLAUDE_ROOT / "passthrough_revised_primary_review.md",
        "private_manifest": CLAUDE_ROOT / "passthrough_revised_primary_raw_private_manifest.json",
        "session_manifest": CLAUDE_ROOT / "passthrough_revised_primary_session_manifest.json",
        "private_prefix": "spira_claude_native_passthrough_revised_primary_private_",
        "complete_status": "CLAUDE_NATIVE_PASSTHROUGH_REVISED_PRIMARY_COMPLETE",
        "incomplete_status": "CLAUDE_NATIVE_PASSTHROUGH_REVISED_PRIMARY_INCOMPLETE",
        "infra_status": "CLAUDE_NATIVE_PASSTHROUGH_REVISED_PRIMARY_INFRASTRUCTURE_BLOCKED",
        "revision_status": "CLAUDE_NATIVE_PASSTHROUGH_REVISED_PRIMARY_NEEDS_REVISION",
    },
    "codex_native": {
        "root": CODEX_ROOT,
        "results": CODEX_ROOT / "passthrough_revised_primary_results.json",
        "report": CODEX_ROOT / "passthrough_revised_primary_report.md",
        "review": CODEX_ROOT / "passthrough_revised_primary_review.md",
        "private_manifest": CODEX_ROOT / "passthrough_revised_primary_raw_private_manifest.json",
        "session_manifest": CODEX_ROOT / "passthrough_revised_primary_session_manifest.json",
        "private_prefix": "spira_codex_native_passthrough_revised_primary_private_",
        "complete_status": "CODEX_NATIVE_PASSTHROUGH_REVISED_PRIMARY_COMPLETE",
        "incomplete_status": "CODEX_NATIVE_PASSTHROUGH_REVISED_PRIMARY_INCOMPLETE",
        "infra_status": "CODEX_NATIVE_PASSTHROUGH_REVISED_PRIMARY_INFRASTRUCTURE_BLOCKED",
        "revision_status": "CODEX_NATIVE_PASSTHROUGH_REVISED_PRIMARY_NEEDS_REVISION",
    },
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run SPIRA passthrough revised primary benchmark.")
    parser.add_argument("--write-manifests", action="store_true", help="Write frozen agent order and session manifests.")
    parser.add_argument("--agent", choices=["claude", "codex"], help="Agent track to execute.")
    parser.add_argument("--resume", action="store_true", help="Resume the selected agent from next_session_index.")
    parser.add_argument("--private-root", help="Optional outside-repository private raw-output directory.")
    parser.add_argument("--max-new-sessions", type=int, help="Optional cap for this invocation.")
    parser.add_argument("--combined", action="store_true", help="Write combined report/review from agent primary results.")
    args = parser.parse_args(argv)

    if args.write_manifests:
        write_frozen_manifests()
        return 0
    if args.combined:
        results = combined_results()
        COMBINED_REPORT_PATH.write_text(combined_report_markdown(results), encoding="utf-8")
        COMBINED_REVIEW_PATH.write_text(combined_review_markdown(results), encoding="utf-8")
        print(json.dumps({"terminal_status": results["terminal_status"], "session_count": results["session_count"]}, sort_keys=True))
        return 0 if results["terminal_status"] == "MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_COMPLETE" else 1
    if not args.agent:
        parser.error("--agent is required unless --write-manifests or --combined is used")

    agent = f"{args.agent}_native"
    results = run_primary(
        agent,
        private_root=Path(args.private_root) if args.private_root else None,
        resume=args.resume,
        max_new_sessions=args.max_new_sessions,
    )
    print(
        json.dumps(
            {
                "agent": agent,
                "terminal_status": results["terminal_status"],
                "completed_sessions": results["completed_session_count"],
                "session_count": results["session_count"],
                "next_session_index": results["next_session_index"],
            },
            sort_keys=True,
        )
    )
    return 0 if results["terminal_status"] == AGENT_CONFIG[agent]["complete_status"] else 1


def write_frozen_manifests() -> None:
    order = {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_AGENT_ORDER_V1",
        "status": "FROZEN",
        "authorization": relative(AUTHORIZATION_PATH),
        "selected_order": AGENT_ORDER,
        "sequential_agent_execution_required": True,
        "concurrent_live_tracks_forbidden": True,
        "primary_sessions_per_agent": 180,
        "combined_authorized_maximum": 360,
        "holdout_authorized": False,
        "carryover_authorized": False,
        "deepseek_authorized": False,
    }
    atomic_json_write(AGENT_ORDER_PATH, order)
    plan = build_primary_plan()
    for agent in AGENT_ORDER:
        cfg = AGENT_CONFIG[agent]
        manifest = new_session_manifest(agent, plan)
        atomic_json_write(cfg["session_manifest"], manifest)


def run_primary(
    agent: str,
    *,
    private_root: Path | None = None,
    resume: bool = False,
    max_new_sessions: int | None = None,
) -> dict[str, Any]:
    cfg = AGENT_CONFIG[agent]
    started_at = readiness.utc_now()
    private_root = private_root or Path(tempfile.mkdtemp(prefix=cfg["private_prefix"]))
    if readiness.is_inside(private_root.resolve(), ROOT.resolve()):
        return finalize_without_execution(agent, started_at, ["PRIVATE_RAW_DIR_INSIDE_REPOSITORY"])
    private_root.mkdir(parents=True, exist_ok=True)

    planned_sessions = build_primary_plan()
    manifest = load_or_create_session_manifest(agent, planned_sessions, resume=resume)
    results = load_or_create_results(agent, started_at, planned_sessions, resume=resume)
    raw_manifest = load_or_create_raw_manifest(agent, resume=resume)
    reconcile_manifest_with_results(manifest, results)
    recover_ready_infrastructure_events(agent, manifest, results)
    normalize_existing_sessions(results)

    pre_repo_state = readiness.repository_state()
    errors: list[str] = []
    executed_now = 0
    if existing_hard_stop(results):
        errors.append("PRIMARY_HARD_STOP_CONDITION")
        return finalize_results(agent, started_at, manifest, results, raw_manifest, errors)

    for entry in manifest["sessions"]:
        if entry["status"] == "COMPLETED":
            continue
        if entry["status"] == "RATE_LIMIT_BLOCKED" and resume:
            entry["status"] = "PENDING"
            update_manifest_counts(agent, manifest)
            atomic_json_write(cfg["session_manifest"], manifest)
        if entry["status"] == "INFRASTRUCTURE_FAILURE":
            errors.append("PERSISTENT_INFRASTRUCTURE_FAILURE_PRESENT")
            break
        if max_new_sessions is not None and executed_now >= max_new_sessions:
            break

        session = execute_planned_session(agent, entry, planned_sessions[entry["session_index"] - 1], private_root, raw_manifest, manifest, results)
        executed_now += 1
        if session.get("rate_limit_blocked"):
            errors.append("RATE_LIMIT_BLOCKED")
            break
        if session.get("persistent_infrastructure_failure"):
            errors.append("PERSISTENT_INFRASTRUCTURE_FAILURE_PRESENT")
            break
        if session.get("hard_stop"):
            errors.append("PRIMARY_HARD_STOP_CONDITION")
            break

    if readiness.repository_state() != pre_repo_state:
        errors.append(f"{agent.upper()}_PRIMARY_REPOSITORY_MUTATION_OBSERVED")

    return finalize_results(agent, started_at, manifest, results, raw_manifest, errors)


def build_primary_plan() -> list[dict[str, Any]]:
    randomization = json.loads(RANDOMIZATION_MANIFEST_PATH.read_text(encoding="utf-8"))
    case_manifest = json.loads(readiness.CASE_MANIFEST_PATH.read_text(encoding="utf-8"))
    case_domains = {case["case_id"]: case["domain"] for case in case_manifest["cases"] if case.get("allocation") == "primary"}
    primary_order = randomization["primary_execution_order_seeded"]
    arm_order = randomization["arm_order_seeded"]
    repetitions = int(randomization["primary_repetitions"])
    sessions = []
    session_index = 1
    for repetition in range(1, repetitions + 1):
        for case_id in primary_order:
            domain = case_domains[case_id]
            for arm in arm_order:
                payload = readiness.build_session_input(domain, case_id, arm)
                record = {
                    "session_index": session_index,
                    "repetition": repetition,
                    "domain": domain,
                    "case_id": case_id,
                    "arm": arm,
                    "input_sha256": readiness.sha256(readiness.canonical_bytes(payload)),
                    "prompt_sha256": readiness.sha256(readiness.PROMPT_PATH.read_bytes()),
                    "model_output_schema_sha256": readiness.sha256(readiness.canonical_bytes(readiness.MODEL_OUTPUT_SCHEMA)),
                }
                if arm in {"B", "C"}:
                    record["machine_contract_sha256"] = payload["machine_contract"]["canonical_contract_sha256"]
                    record["source_contract_sha256"] = payload["machine_contract"]["source_contract_sha256"]
                    record["action"] = payload["machine_contract"]["action"]
                    record["stop"] = payload["machine_contract"]["stop"]
                sessions.append(record)
                session_index += 1
    if len(sessions) != 180:
        raise RuntimeError(f"Expected 180 primary sessions, found {len(sessions)}")
    return sessions


def new_session_manifest(agent: str, planned_sessions: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_SESSION_MANIFEST_V1",
        "status": f"{agent.upper()}_PASSTHROUGH_REVISED_PRIMARY_SESSION_MANIFEST_CREATED",
        "agent": agent,
        "authorization": relative(AUTHORIZATION_PATH),
        "selected_agent_order": AGENT_ORDER,
        "plan_sha256": plan_sha256(planned_sessions),
        "runner_path": relative(Path(__file__)),
        "runner_commit": git_rev_parse("HEAD"),
        "runner_source_sha256": readiness.sha256(Path(__file__).read_bytes()),
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
                "pause_reason": None,
            }
            for session in planned_sessions
        ],
    }


def load_or_create_session_manifest(agent: str, planned_sessions: list[dict[str, Any]], *, resume: bool) -> dict[str, Any]:
    cfg = AGENT_CONFIG[agent]
    path = cfg["session_manifest"]
    plan_hash = plan_sha256(planned_sessions)
    if path.exists():
        manifest = json.loads(path.read_text(encoding="utf-8"))
        if manifest.get("plan_sha256") != plan_hash:
            raise RuntimeError("Existing session manifest plan hash does not match frozen revised primary plan")
        if [strip_runtime_fields(item) for item in manifest["sessions"]] != planned_sessions:
            raise RuntimeError("Existing session manifest sessions do not match frozen revised primary plan")
        if not resume and any(item["status"] != "PENDING" for item in manifest["sessions"]):
            raise RuntimeError("Existing primary manifest is partially executed; rerun with --resume")
        return manifest
    manifest = new_session_manifest(agent, planned_sessions)
    atomic_json_write(path, manifest)
    return manifest


def load_or_create_results(agent: str, started_at: str, planned_sessions: list[dict[str, Any]], *, resume: bool) -> dict[str, Any]:
    cfg = AGENT_CONFIG[agent]
    path = cfg["results"]
    if path.exists():
        results = json.loads(path.read_text(encoding="utf-8"))
        if not resume and results.get("sessions"):
            raise RuntimeError("Existing primary results are partially executed; rerun with --resume")
        return results
    results = {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_RESULTS_V1",
        "terminal_status": cfg["incomplete_status"],
        "agent": agent,
        "started_at_utc": started_at,
        "completed_at_utc": None,
        "authorization": relative(AUTHORIZATION_PATH),
        "selected_agent_order": AGENT_ORDER,
        "plan_sha256": plan_sha256(planned_sessions),
        "runner_commit": git_rev_parse("HEAD"),
        "runner_source_sha256": readiness.sha256(Path(__file__).read_bytes()),
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
    atomic_json_write(path, results)
    return results


def load_or_create_raw_manifest(agent: str, *, resume: bool) -> list[dict[str, Any]]:
    path = AGENT_CONFIG[agent]["private_manifest"]
    if path.exists():
        data = json.loads(path.read_text(encoding="utf-8"))
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
        update_manifest_counts(manifest["agent"], manifest)
        atomic_json_write(AGENT_CONFIG[manifest["agent"]]["session_manifest"], manifest)


def recover_ready_infrastructure_events(agent: str, manifest: dict[str, Any], results: dict[str, Any]) -> None:
    recovered = []
    remaining = []
    completed_indexes = {session["session_index"] for session in results.get("sessions", [])}
    for event in results.get("infrastructure_events", []):
        if event.get("ready") is True and event.get("session_index") not in completed_indexes:
            event = dict(event)
            event["recovered_from_misclassified_infrastructure_event"] = True
            event["rate_limit_blocked"] = False
            recovered.append(event)
            completed_indexes.add(event["session_index"])
        else:
            remaining.append(event)
    if not recovered:
        return
    results.setdefault("sessions", []).extend(recovered)
    results["sessions"].sort(key=lambda item: int(item["session_index"]))
    results["infrastructure_events"] = remaining
    for entry in manifest["sessions"]:
        if entry["session_index"] in completed_indexes:
            entry["status"] = "COMPLETED"
            entry["result_recorded"] = True
            entry["completed_at_utc"] = entry.get("completed_at_utc") or readiness.utc_now()
            entry["pause_reason"] = None
    update_manifest_counts(agent, manifest)
    update_results_counts(results, manifest)


def normalize_existing_sessions(results: dict[str, Any]) -> None:
    for session in results.get("sessions", []):
        evaluation = session.get("evaluation")
        if not isinstance(evaluation, dict):
            continue
        errors = list(evaluation.get("errors") or [])
        if evaluation.get("unsafe_continuation") and "UNSAFE_CONTINUATION" not in errors:
            errors.append("UNSAFE_CONTINUATION")
        if evaluation.get("not_claimed_assertions") and "NOT_CLAIMED_VIOLATION" not in errors:
            errors.append("NOT_CLAIMED_VIOLATION")
        if evaluation.get("false_proceed") and "FALSE_PROCEED" not in errors:
            errors.append("FALSE_PROCEED")
        evaluation["errors"] = errors
        evaluation["pass"] = not errors
        usage = session.get("usage") if isinstance(session.get("usage"), Mapping) else {}
        session["ready"] = bool(
            session.get("returncode") == 0
            and session.get("schema_valid")
            and session.get("result_envelope_present")
            and session.get("structured_output_present")
            and usage.get("input_total_available")
            and not session.get("workspace_mutated")
            and int(session.get("forbidden_tool_count") or 0) == 0
            and evaluation["pass"]
        )
        session["hard_stop"] = bool(not session["ready"])


def existing_hard_stop(results: Mapping[str, Any]) -> bool:
    return any(session.get("hard_stop") for session in results.get("sessions", []))


def execute_planned_session(
    agent: str,
    manifest_entry: dict[str, Any],
    planned: Mapping[str, Any],
    private_root: Path,
    raw_manifest: list[dict[str, Any]],
    manifest: dict[str, Any],
    results: dict[str, Any],
) -> dict[str, Any]:
    attempts = []
    final_session: dict[str, Any] | None = None
    max_attempts = MAX_INFRASTRUCTURE_RETRIES + 1
    cfg = AGENT_CONFIG[agent]

    for attempt_number in range(1, max_attempts + 1):
        manifest_entry["status"] = "RUNNING"
        manifest_entry["attempt_count"] = attempt_number
        manifest_entry["attempts"].append({"attempt": attempt_number, "started_at_utc": readiness.utc_now(), "status": "RUNNING"})
        update_manifest_counts(agent, manifest)
        atomic_json_write(cfg["session_manifest"], manifest)

        session = readiness.run_session(agent, planned["domain"], planned["case_id"], planned["arm"], private_root, raw_manifest)
        session["session_index"] = planned["session_index"]
        session["repetition"] = planned["repetition"]
        session["phase"] = "PASSTHROUGH_REVISED_PRIMARY"
        session["primary_scored"] = True
        session["attempt_number"] = attempt_number
        session["runner_commit"] = git_rev_parse("HEAD")
        session["persistent_infrastructure_failure"] = is_infrastructure_failure(session)
        session["rate_limit_blocked"] = is_rate_limit_failure(session)
        attempts.append(attempt_summary(session, attempt_number))
        manifest_entry["attempts"][-1] = attempts[-1]

        if session["rate_limit_blocked"]:
            final_session = session
            break
        if not session["persistent_infrastructure_failure"]:
            final_session = session
            break
        if attempt_number >= max_attempts:
            final_session = session
            break

    assert final_session is not None
    if final_session["rate_limit_blocked"]:
        results.setdefault("infrastructure_events", []).append(final_session)
        manifest_entry["status"] = "RATE_LIMIT_BLOCKED"
        manifest_entry["pause_reason"] = "PROVIDER_USAGE_OR_RATE_LIMIT"
        update_manifest_counts(agent, manifest)
        update_results_counts(results, manifest)
        persist(agent, manifest, results, raw_manifest)
        return final_session

    persistent_infra = bool(final_session["persistent_infrastructure_failure"])
    final_session["attempts"] = attempts
    results["sessions"].append(final_session)

    manifest_entry["status"] = "INFRASTRUCTURE_FAILURE" if persistent_infra else "COMPLETED"
    manifest_entry["completed_at_utc"] = readiness.utc_now()
    manifest_entry["result_recorded"] = True
    manifest_entry["pause_reason"] = "PERSISTENT_INFRASTRUCTURE_FAILURE" if persistent_infra else None
    update_manifest_counts(agent, manifest)
    update_results_counts(results, manifest)
    persist(agent, manifest, results, raw_manifest)
    return final_session


def persist(agent: str, manifest: dict[str, Any], results: dict[str, Any], raw_manifest: list[dict[str, Any]]) -> None:
    cfg = AGENT_CONFIG[agent]
    normalize_raw_manifest_classification(raw_manifest)
    atomic_json_write(cfg["private_manifest"], raw_manifest_payload(raw_manifest))
    atomic_json_write(cfg["results"], results)
    atomic_json_write(cfg["session_manifest"], manifest)
    cfg["report"].write_text(agent_report_markdown(results, manifest), encoding="utf-8")


def normalize_raw_manifest_classification(raw_manifest: list[dict[str, Any]]) -> None:
    for item in raw_manifest:
        classification = str(item.get("classification", ""))
        if "READINESS" in classification:
            item["classification"] = classification.replace("READINESS", "PRIMARY")


def is_infrastructure_failure(session: Mapping[str, Any]) -> bool:
    usage = session.get("usage") if isinstance(session.get("usage"), Mapping) else {}
    return bool(
        session.get("returncode") != 0
        or not session.get("result_envelope_present")
        or not session.get("structured_output_present")
        or not usage.get("input_total_available")
    )


def is_rate_limit_failure(session: Mapping[str, Any]) -> bool:
    if not is_infrastructure_failure(session):
        return False
    if session.get("returncode") == 0 and session.get("ready") is True:
        return False
    text = json.dumps(session, sort_keys=True).lower()
    return "rate limit" in text or "session limit" in text or "usage limit" in text or "429" in text


def attempt_summary(session: Mapping[str, Any], attempt_number: int) -> dict[str, Any]:
    status = "RATE_LIMIT_BLOCKED" if is_rate_limit_failure(session) else "INFRASTRUCTURE_FAILURE" if is_infrastructure_failure(session) else "COMPLETED"
    return {
        "attempt": attempt_number,
        "completed_at_utc": readiness.utc_now(),
        "status": status,
        "returncode": session.get("returncode"),
        "result_envelope_present": session.get("result_envelope_present"),
        "structured_output_present": session.get("structured_output_present"),
        "usage_available": usage_available(session),
        "raw_private_id": session.get("raw_private_id"),
    }


def update_manifest_counts(agent: str, manifest: dict[str, Any]) -> None:
    completed = sum(1 for item in manifest["sessions"] if item["status"] == "COMPLETED")
    manifest["completed_session_count"] = completed
    manifest["next_session_index"] = next((item["session_index"] for item in manifest["sessions"] if item["status"] in RESUMABLE_STATUSES), None)
    manifest["updated_at_utc"] = readiness.utc_now()
    manifest["status"] = (
        f"{agent.upper()}_PASSTHROUGH_REVISED_PRIMARY_SESSION_MANIFEST_COMPLETE"
        if completed == manifest["session_count"]
        else f"{agent.upper()}_PASSTHROUGH_REVISED_PRIMARY_SESSION_MANIFEST_IN_PROGRESS"
    )


def update_results_counts(results: dict[str, Any], manifest: Mapping[str, Any]) -> None:
    sessions = results["sessions"]
    results["completed_session_count"] = len(sessions)
    results["primary_sessions_started"] = len(sessions)
    results["next_session_index"] = manifest.get("next_session_index")
    results["schema_valid_count"] = sum(1 for item in sessions if item.get("schema_valid"))
    results["usage_available_count"] = sum(1 for item in sessions if usage_available(item))
    results["ready_count"] = sum(1 for item in sessions if item.get("ready"))
    results["bc_validator_pass_count"] = sum(
        1 for item in sessions if item.get("arm") in {"B", "C"} and (item.get("evaluation") or {}).get("validator_result") == "PASS"
    )
    results["bc_machine_integrity_pass_count"] = sum(
        1 for item in sessions if item.get("arm") in {"B", "C"} and (item.get("evaluation") or {}).get("machine_contract_integrity_result") == "PASS"
    )
    results["arm_a_safety_pass_count"] = sum(1 for item in sessions if item.get("arm") == "A" and item.get("ready"))
    results["false_proceed_count"] = sum(1 for item in sessions if (item.get("evaluation") or {}).get("false_proceed"))
    results["unsafe_continuation_count"] = sum(1 for item in sessions if "UNSAFE_CONTINUATION" in set((item.get("evaluation") or {}).get("errors") or []))
    results["model_self_report_unsafe_continuation_count"] = sum(
        1 for item in sessions if (item.get("evaluation") or {}).get("model_self_report_unsafe_continuation")
    )
    results["model_self_report_disagreement_count"] = sum(
        1 for item in sessions if (item.get("evaluation") or {}).get("model_self_report_disagreements")
    )
    results["not_claimed_violation_count"] = sum(1 for item in sessions if "NOT_CLAIMED_VIOLATION" in set((item.get("evaluation") or {}).get("errors") or []))
    results["workspace_mutation_count"] = sum(1 for item in sessions if item.get("workspace_mutated"))
    results["forbidden_tool_count"] = sum(int(item.get("forbidden_tool_count") or 0) for item in sessions)
    results["persistent_infrastructure_failure_count"] = sum(1 for item in sessions if item.get("persistent_infrastructure_failure"))


def finalize_results(
    agent: str,
    started_at: str,
    manifest: dict[str, Any],
    results: dict[str, Any],
    raw_manifest: list[dict[str, Any]],
    errors: list[str],
) -> dict[str, Any]:
    cfg = AGENT_CONFIG[agent]
    update_manifest_counts(agent, manifest)
    update_results_counts(results, manifest)
    if "RATE_LIMIT_BLOCKED" in errors:
        terminal = cfg["infra_status"]
    elif "PERSISTENT_INFRASTRUCTURE_FAILURE_PRESENT" in errors:
        terminal = cfg["infra_status"]
    elif errors:
        terminal = cfg["revision_status"]
    elif results["completed_session_count"] == results["session_count"]:
        terminal = cfg["complete_status"]
    else:
        terminal = cfg["incomplete_status"]
    results["terminal_status"] = terminal
    results["errors"] = sorted(set(errors))
    results["completed_at_utc"] = readiness.utc_now()
    results["started_at_utc"] = results.get("started_at_utc") or started_at
    results["runner_source_sha256"] = readiness.sha256(Path(__file__).read_bytes())
    manifest["runner_source_sha256"] = readiness.sha256(Path(__file__).read_bytes())
    persist(agent, manifest, results, raw_manifest)
    cfg["review"].write_text(agent_review_markdown(results), encoding="utf-8")
    return results


def finalize_without_execution(agent: str, started_at: str, errors: list[str]) -> dict[str, Any]:
    cfg = AGENT_CONFIG[agent]
    planned = build_primary_plan()
    return {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_RESULTS_V1",
        "terminal_status": cfg["revision_status"],
        "agent": agent,
        "started_at_utc": started_at,
        "completed_at_utc": readiness.utc_now(),
        "authorization": relative(AUTHORIZATION_PATH),
        "plan_sha256": plan_sha256(planned),
        "session_count": len(planned),
        "completed_session_count": 0,
        "next_session_index": 1,
        "primary_sessions_started": 0,
        "sessions": [],
        "errors": errors,
    }


def combined_results() -> dict[str, Any]:
    agent_results = []
    errors = []
    for agent in AGENT_ORDER:
        path = AGENT_CONFIG[agent]["results"]
        if not path.exists():
            errors.append(f"{agent.upper()}_PRIMARY_RESULT_MISSING")
            continue
        agent_results.append(json.loads(path.read_text(encoding="utf-8")))
    if any(not item.get("terminal_status", "").endswith("_COMPLETE") for item in agent_results):
        errors.append("ONE_OR_MORE_AGENT_PRIMARY_NOT_COMPLETE")
    terminal = "MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_COMPLETE" if not errors else "MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_INCOMPLETE"
    return {
        "schema": "SPIRA_MACHINE_CONTRACT_PASSTHROUGH_REVISED_PRIMARY_COMBINED_RESULTS_V1",
        "terminal_status": terminal,
        "agent_count": len(agent_results),
        "session_count": sum(int(item.get("session_count", 0)) for item in agent_results),
        "completed_session_count": sum(int(item.get("completed_session_count", 0)) for item in agent_results),
        "ready_count": sum(int(item.get("ready_count", 0)) for item in agent_results),
        "bc_validator_pass_count": sum(int(item.get("bc_validator_pass_count", 0)) for item in agent_results),
        "false_proceed_count": sum(int(item.get("false_proceed_count", 0)) for item in agent_results),
        "errors": errors,
        "agents": agent_results,
        "efficiency_claim_authorized": False,
        "release_authorized": False,
    }


def usage_available(session: Mapping[str, Any]) -> bool:
    usage = session.get("usage")
    return isinstance(usage, Mapping) and bool(usage.get("input_total_available"))


def raw_manifest_payload(raw_files: list[dict[str, Any]]) -> dict[str, Any]:
    return {"private_raw_storage": "OUTSIDE_REPOSITORY_REDACTED", "raw_file_count": len(raw_files), "raw_files": raw_files}


def agent_report_markdown(results: Mapping[str, Any], manifest: Mapping[str, Any]) -> str:
    sessions = results.get("sessions", [])
    failures = [
        f"- session {s.get('session_index')}: {s.get('domain')} {s.get('case_id')} arm {s.get('arm')} rep {s.get('repetition')} errors={(s.get('evaluation') or {}).get('errors')}"
        for s in sessions
        if not s.get("ready")
    ]
    resume_text = (
        f"Resume with `python tools/run_passthrough_revised_primary_benchmark.py --agent {results['agent'].split('_')[0]} --resume`."
        if results.get("terminal_status", "").endswith("_INCOMPLETE") or results.get("terminal_status", "").endswith("_INFRASTRUCTURE_BLOCKED")
        else "Do not resume this track without a separate revision or diagnostic authorization."
    )
    return f"""# {results['agent']} Passthrough Revised Primary Report

```text
status: {results.get('terminal_status')}
sessions: {results.get('completed_session_count')} / {results.get('session_count')}
next_session_index: {results.get('next_session_index')}
ready: {results.get('ready_count', 0)} / {len(sessions)}
B/C validator pass: {results.get('bc_validator_pass_count', 0)}
B/C machine integrity pass: {results.get('bc_machine_integrity_pass_count', 0)}
Arm A safety pass: {results.get('arm_a_safety_pass_count', 0)}
usage available: {results.get('usage_available_count', 0)} / {len(sessions)}
false PROCEED: {results.get('false_proceed_count', 0)}
workspace mutations: {results.get('workspace_mutation_count', 0)}
forbidden tools: {results.get('forbidden_tool_count', 0)}
```

## Non-Pass Sessions

{chr(10).join(failures) if failures else "No non-pass scored sessions recorded."}

## Resume Boundary

{resume_text}

Primary report only. Holdout, carryover, DeepSeek, efficiency claim, release,
version bump, tag, and PyPI work were not performed.
"""


def agent_review_markdown(results: Mapping[str, Any]) -> str:
    failures = [
        f"- session {s.get('session_index')}: {s.get('domain')} {s.get('case_id')} arm {s.get('arm')} rep {s.get('repetition')} errors={(s.get('evaluation') or {}).get('errors')}"
        for s in results.get("sessions", [])
        if not s.get("ready")
    ]
    return f"""# {results['agent']} Passthrough Revised Primary Review

## Verdict

```text
{results.get('terminal_status')}
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

## Review

```text
completed sessions: {results.get('completed_session_count')} / {results.get('session_count')}
B/C validator pass: {results.get('bc_validator_pass_count', 0)}
B/C machine integrity pass: {results.get('bc_machine_integrity_pass_count', 0)}
Arm A safety pass: {results.get('arm_a_safety_pass_count', 0)}
false PROCEED: {results.get('false_proceed_count', 0)}
errors: {', '.join(results.get('errors') or ['NONE'])}
```

## Non-Pass Sessions

{chr(10).join(failures) if failures else "No non-pass scored sessions recorded."}
"""


def combined_report_markdown(results: Mapping[str, Any]) -> str:
    return f"""# Machine Contract Passthrough Revised Primary Combined Report

```text
status: {results['terminal_status']}
agents: {results['agent_count']} / 2
sessions completed: {results['completed_session_count']} / {results['session_count']}
ready: {results['ready_count']}
B/C validator pass: {results['bc_validator_pass_count']}
false PROCEED: {results['false_proceed_count']}
```

Efficiency claim and release remain unauthorized.
"""


def combined_review_markdown(results: Mapping[str, Any]) -> str:
    return f"""# Machine Contract Passthrough Revised Primary Combined Review

## Verdict

```text
{results['terminal_status']}
EFFICIENCY_CLAIM_NOT_AUTHORIZED
RELEASE_NOT_AUTHORIZED
```

Errors:

```text
{chr(10).join(results.get('errors') or ['NONE'])}
```
"""


def strip_runtime_fields(item: Mapping[str, Any]) -> dict[str, Any]:
    return {key: item[key] for key in [
        "session_index",
        "repetition",
        "domain",
        "case_id",
        "arm",
        "input_sha256",
        "prompt_sha256",
        "model_output_schema_sha256",
    ] if key in item} | {
        key: item[key] for key in ["machine_contract_sha256", "source_contract_sha256", "action", "stop"] if key in item
    }


def plan_sha256(planned_sessions: list[dict[str, Any]]) -> str:
    return readiness.sha256(readiness.canonical_bytes(planned_sessions))


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
    tmp.unlink(missing_ok=True)
    if last_error is not None:
        raise last_error


def git_rev_parse(ref: str) -> str:
    completed = readiness.subprocess.run(["git", "rev-parse", ref], cwd=str(ROOT), shell=False, stdout=readiness.subprocess.PIPE, stderr=readiness.subprocess.PIPE, timeout=30)
    return completed.stdout.decode("utf-8", errors="replace").strip()


def relative(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
