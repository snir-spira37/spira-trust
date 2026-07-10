from __future__ import annotations

import argparse
import json
import tempfile
import time
import zipfile
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from spira_core.agent_cache import build_agent_verdict_cache
from spira_core.agent_summary import write_agent_summary
from spira_core.decision_report import finalize_graph_outputs_for_decision, write_decision_report
from spira_core.rerun_planner import build_rerun_plan, context_from_agent_summary
from spira_core.trust_graph import graph_exit_code, run_trust_graph


SCHEMA = "SPIRA_AGENT_MEMORY_FLOW_REGRESSION_V1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="End-to-end SPIRA agent evidence memory regression.")
    parser.add_argument("--json-out", type=Path, default=Path("bench/results/agent_memory_flow_v1.json"))
    parser.add_argument("--summary-out", type=Path, default=Path("bench/results/agent_memory_flow_v1_summary.md"))
    args = parser.parse_args(argv)
    result = run_regression()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.summary_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    args.summary_out.write_text(markdown_summary(result), encoding="utf-8", newline="\n")
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0 if result["summary"]["all_cases_passed"] else 1


def run_regression() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="spira-agent-memory-flow-") as temp:
        root = Path(temp)
        wheel_dir = root / "dist"
        wheel_dir.mkdir()
        wheel = build_wheel(wheel_dir, payload=b"__version__ = '1.0.0'\n")
        out = root / "out"
        state = root / "state"

        cold_start = time.perf_counter()
        cold = run_cold(wheel_dir, out, state)
        cold_seconds = time.perf_counter() - cold_start
        previous_context = context_from_agent_summary(cold["summary"])
        cache_start = time.perf_counter()
        clean_cache = cache(wheel, cold, state)
        cache_seconds = time.perf_counter() - cache_start
        clean_plan = build_rerun_plan(previous_context, previous_context)

        cases = [
            case(
                "clean_cache_hit",
                cache_result=clean_cache,
                plan=clean_plan,
                expected_cache_hit=True,
                expected_plan_rerun=False,
                expected_cache_reason=None,
                expected_plan_reason=None,
            )
        ]

        changed_dir = root / "changed-dist"
        changed_dir.mkdir()
        changed_wheel = build_wheel(changed_dir, payload=b"changed\n")
        artifact_cache = cache(changed_wheel, cold, state)
        artifact_context = {**previous_context, "artifact_sha256": sha256(changed_wheel.read_bytes()).hexdigest()}
        cases.append(
            case(
                "artifact_mutation",
                cache_result=artifact_cache,
                plan=build_rerun_plan(artifact_context, previous_context),
                expected_cache_hit=False,
                expected_plan_rerun=True,
                expected_cache_reason="ARTIFACT_CHANGED_SINCE_CHECK",
                expected_plan_reason="ARTIFACT_CHANGED",
            )
        )

        cases.extend(
            [
                context_case("policy_mutation", wheel, cold, state, previous_context, "policy_sha256", "p" * 64, "CONTEXT_MISMATCH", "POLICY_CHANGED"),
                context_case("lockfile_mutation", wheel, cold, state, previous_context, "lockfile_sha256", "l" * 64, "CONTEXT_MISMATCH", "LOCKFILE_CHANGED", cache_command="changed-lock-command"),
                context_case("semantics_mutation", wheel, cold, state, previous_context, "decision_semantics_version", "SPIRA_DECISION_SEMANTICS_TEST", "CONTEXT_MISMATCH", "DECISION_SEMANTICS_CHANGED"),
                context_case("tool_version_mutation", wheel, cold, state, previous_context, "tool_version", "different-tool-version", "CONTEXT_MISMATCH", "TOOL_VERSION_CHANGED"),
            ]
        )

        cases.append(context_ambiguity_case(wheel, cold, state, previous_context))
        cases.append(result_conflict_case(wheel, cold, state, previous_context))
        cases.append(missing_summary_case(wheel, cold, root / "missing-state", previous_context))
        cases.append(corrupted_summary_case(wheel, cold, root / "corrupted-state", previous_context))
        cases.append(unsupported_schema_case(previous_context))

    return {
        "schema": SCHEMA,
        "created_at": utc(),
        "summary": {
            "cold_wall_seconds": cold_seconds,
            "warm_cache_wall_seconds": cache_seconds,
            "warm_cache_speedup_ratio": cold_seconds / cache_seconds if cache_seconds else None,
            "clean_cache_response_bytes": json_size(clean_cache),
            "clean_plan_response_bytes": json_size(clean_plan),
            "all_cases_passed": all(item["passed"] for item in cases),
        },
        "cases": cases,
        "not_claimed": [
            "does not execute planner-requested reruns",
            "does not measure CPU cycles, energy, or CO2",
            "does not measure live-agent token usage",
            "synthetic wheel regression, not ecosystem-wide performance data",
        ],
    }


def context_case(
    name: str,
    wheel: Path,
    cold: Mapping[str, Any],
    state: Path,
    previous_context: Mapping[str, Any],
    field: str,
    value: Any,
    expected_cache_reason: str,
    expected_plan_reason: str,
    *,
    cache_command: str | None = None,
) -> dict[str, Any]:
    current = {**previous_context, field: value}
    cache_result = build_agent_verdict_cache(
        wheel,
        command_fingerprint=cache_command or str(current["command_fingerprint"]),
        policy_sha256=current["policy_sha256"],
        decision_semantics_version=current["decision_semantics_version"],
        tool_version=current["tool_version"],
        state_dir=state,
    )
    return case(
        name,
        cache_result=cache_result,
        plan=build_rerun_plan(current, previous_context),
        expected_cache_hit=False,
        expected_plan_rerun=True,
        expected_cache_reason=expected_cache_reason,
        expected_plan_reason=expected_plan_reason,
    )


def context_ambiguity_case(wheel: Path, cold: Mapping[str, Any], state: Path, previous_context: Mapping[str, Any]) -> dict[str, Any]:
    source = next(state.glob("*.agent_summary.json"))
    data = json.loads(source.read_text(encoding="utf-8"))
    data["summary_of"]["command_fingerprint"] = "1" * 64
    data["agent_action_contract"]["command_fingerprint"] = "1" * 64
    (state / "second-context.agent_summary.json").write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    cache_result = build_agent_verdict_cache(wheel, command_fingerprint="2" * 64, state_dir=state)
    current = {**previous_context, "context_ambiguous": True}
    return case(
        "context_ambiguity",
        cache_result=cache_result,
        plan=build_rerun_plan(current, previous_context),
        expected_cache_hit=False,
        expected_plan_rerun=True,
        expected_cache_reason="CONTEXT_AMBIGUOUS",
        expected_plan_reason="CONTEXT_AMBIGUOUS",
    )


def result_conflict_case(wheel: Path, cold: Mapping[str, Any], state: Path, previous_context: Mapping[str, Any]) -> dict[str, Any]:
    source = next(path for path in state.glob("*.agent_summary.json") if path.name != "second-context.agent_summary.json")
    data = json.loads(source.read_text(encoding="utf-8"))
    data["stop"] = False
    data["recommended_agent_action"] = "PROCEED"
    data["reason_codes"] = []
    data["agent_action_contract"]["stop"] = False
    data["agent_action_contract"]["recommended_agent_action"] = "PROCEED"
    data["agent_action_contract"]["reason_codes"] = []
    (state / "conflicting-result.agent_summary.json").write_text(json.dumps(data, separators=(",", ":")) + "\n", encoding="utf-8", newline="\n")
    cache_result = cache(wheel, cold, state)
    current = {**previous_context, "result_conflict": True}
    return case(
        "exact_context_result_conflict",
        cache_result=cache_result,
        plan=build_rerun_plan(current, previous_context),
        expected_cache_hit=False,
        expected_plan_rerun=True,
        expected_cache_reason="EXACT_CONTEXT_RESULT_CONFLICT",
        expected_plan_reason="EXACT_CONTEXT_RESULT_CONFLICT",
    )


def missing_summary_case(wheel: Path, cold: Mapping[str, Any], state: Path, previous_context: Mapping[str, Any]) -> dict[str, Any]:
    state.mkdir()
    cache_result = cache(wheel, cold, state)
    current = dict(previous_context)
    del current["lockfile_sha256"]
    return case(
        "missing_summary_or_context",
        cache_result=cache_result,
        plan=build_rerun_plan(current, previous_context),
        expected_cache_hit=False,
        expected_plan_rerun=True,
        expected_cache_reason="ARTIFACT_NOT_CHECKED",
        expected_plan_reason="CURRENT_MISSING_CONTEXT_FIELDS",
    )


def corrupted_summary_case(wheel: Path, cold: Mapping[str, Any], state: Path, previous_context: Mapping[str, Any]) -> dict[str, Any]:
    state.mkdir()
    (state / "corrupted.agent_summary.json").write_text("{not-json", encoding="utf-8")
    cache_result = cache(wheel, cold, state)
    current = {**previous_context, "unsupported_context": True}
    return case(
        "corrupted_summary",
        cache_result=cache_result,
        plan=build_rerun_plan(current, previous_context),
        expected_cache_hit=False,
        expected_plan_rerun=True,
        expected_cache_reason="ARTIFACT_NOT_CHECKED",
        expected_plan_reason="CURRENT_UNSUPPORTED_CONTEXT",
    )


def unsupported_schema_case(previous_context: Mapping[str, Any]) -> dict[str, Any]:
    current = {**previous_context, "unsupported_context": True}
    plan = build_rerun_plan(current, previous_context)
    return {
        "name": "unsupported_schema",
        "cache_hit": None,
        "planner_rerun_required": plan["rerun_required"],
        "cache_reason_codes": [],
        "planner_reason_codes": plan["reason_codes"],
        "cache_response_bytes": None,
        "planner_response_bytes": json_size(plan),
        "passed": plan["rerun_required"] is True and "CURRENT_UNSUPPORTED_CONTEXT" in plan["reason_codes"],
    }


def case(
    name: str,
    *,
    cache_result: Mapping[str, Any],
    plan: Mapping[str, Any],
    expected_cache_hit: bool,
    expected_plan_rerun: bool,
    expected_cache_reason: str | None,
    expected_plan_reason: str | None,
) -> dict[str, Any]:
    cache_reasons = list(cache_result.get("reason_codes") or [])
    plan_reasons = list(plan.get("reason_codes") or [])
    passed = (
        cache_result.get("cache_hit") is expected_cache_hit
        and plan.get("rerun_required") is expected_plan_rerun
        and (expected_cache_reason is None or expected_cache_reason in cache_reasons)
        and (expected_plan_reason is None or expected_plan_reason in plan_reasons)
    )
    return {
        "name": name,
        "cache_hit": cache_result.get("cache_hit"),
        "planner_rerun_required": plan.get("rerun_required"),
        "cache_reason_codes": cache_reasons,
        "planner_reason_codes": plan_reasons,
        "cache_response_bytes": json_size(cache_result),
        "planner_response_bytes": json_size(plan),
        "passed": passed,
    }


def run_cold(wheel_dir: Path, out: Path, state: Path) -> dict[str, Any]:
    result = run_trust_graph([wheel_dir], out)
    exit_code = graph_exit_code(result)
    finalize_graph_outputs_for_decision(result, output_dir=out)
    decision = write_decision_report(result, exit_code=exit_code, output_dir=out)
    summary = write_agent_summary(result, decision, output_dir=out, state_dir=state)
    return {
        "summary": summary,
        "command_fingerprint": summary["summary_of"]["command_fingerprint"],
        "policy_sha256": summary["summary_of"]["policy_sha256"],
        "decision_semantics_version": summary["decision_semantics_version"],
        "tool_version": summary["summary_of"]["tool_version"],
    }


def cache(wheel: Path, cold: Mapping[str, Any], state: Path) -> dict[str, Any]:
    return build_agent_verdict_cache(
        wheel,
        command_fingerprint=str(cold["command_fingerprint"]),
        policy_sha256=cold["policy_sha256"],
        decision_semantics_version=str(cold["decision_semantics_version"]),
        tool_version=str(cold["tool_version"]),
        state_dir=state,
    )


def build_wheel(wheel_dir: Path, *, payload: bytes) -> Path:
    wheel = wheel_dir / "agent_memory_pkg-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as zf:
        zf.writestr("agent_memory_pkg/__init__.py", payload)
        zf.writestr(
            "agent_memory_pkg-1.0.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: agent-memory-pkg\nVersion: 1.0.0\n",
        )
        zf.writestr(
            "agent_memory_pkg-1.0.0.dist-info/WHEEL",
            "Wheel-Version: 1.0\nGenerator: spira-agent-memory-flow\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        zf.writestr("agent_memory_pkg-1.0.0.dist-info/RECORD", "")
    return wheel


def markdown_summary(result: Mapping[str, Any]) -> str:
    summary = result["summary"]
    lines = [
        "# Agent Evidence Memory Flow Regression v1",
        "",
        f"Created: {result['created_at']}",
        "",
        "```text",
        f"cold wall seconds: {summary['cold_wall_seconds']:.6f}",
        f"warm cache wall seconds: {summary['warm_cache_wall_seconds']:.6f}",
        f"warm cache speedup ratio: {summary['warm_cache_speedup_ratio']:.2f}x",
        f"clean cache response bytes: {summary['clean_cache_response_bytes']}",
        f"clean plan response bytes: {summary['clean_plan_response_bytes']}",
        f"all cases passed: {summary['all_cases_passed']}",
        "```",
        "",
        "Cases:",
        "",
    ]
    for item in result["cases"]:
        lines.append(f"- {item['name']}: passed={item['passed']}")
    lines.extend(["", "Not claimed: CPU cycles, energy, CO2, or live-agent token savings.", ""])
    return "\n".join(lines)


def json_size(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
