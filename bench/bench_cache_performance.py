from __future__ import annotations

import argparse
import csv
import json
import statistics
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
from spira_core.trust_graph import graph_exit_code, run_trust_graph


SCHEMA = "SPIRA_CACHE_PERFORMANCE_BENCHMARK_V1"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Benchmark cold graph verification vs warm exact-context cache.")
    parser.add_argument("--repeat", type=int, default=20)
    parser.add_argument("--json-out", type=Path, default=Path("bench/results/cache_performance_v1.json"))
    parser.add_argument("--csv-out", type=Path, default=Path("bench/results/cache_performance_v1_runs.csv"))
    parser.add_argument("--summary-out", type=Path, default=Path("bench/results/cache_performance_v1_summary.md"))
    args = parser.parse_args(argv)

    if args.repeat < 1:
        raise SystemExit("--repeat must be >= 1")

    result = run_benchmark(args.repeat)
    write_outputs(result, args.json_out, args.csv_out, args.summary_out)
    print(json.dumps(result["summary"], ensure_ascii=False, indent=2))
    return 0


def run_benchmark(repeat: int) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    miss_matrix: dict[str, Any] = {}
    with tempfile.TemporaryDirectory(prefix="spira-cache-bench-") as temp:
        root = Path(temp)
        wheel_dir = root / "dist"
        wheel_dir.mkdir()
        wheel = build_wheel(wheel_dir, payload=b"print('cache benchmark')\n")

        last_cold: dict[str, Any] | None = None
        for index in range(repeat):
            out = root / f"out-{index:03d}"
            state = root / f"state-{index:03d}"
            cold_start = time.perf_counter()
            cold = run_cold(wheel_dir, out, state)
            cold_seconds = time.perf_counter() - cold_start

            warm_start = time.perf_counter()
            warm = build_agent_verdict_cache(
                wheel,
                command_fingerprint=cold["command_fingerprint"],
                policy_sha256=cold["policy_sha256"],
                decision_semantics_version=cold["decision_semantics_version"],
                tool_version=cold["tool_version"],
                state_dir=state,
            )
            warm_seconds = time.perf_counter() - warm_start
            rows.append(row(index, cold, warm, cold_seconds, warm_seconds, state))
            last_cold = {**cold, "state": state, "wheel": wheel}

        if last_cold is not None:
            miss_matrix = build_miss_matrix(last_cold)

    summary = summarize(rows, miss_matrix)
    return {
        "schema": SCHEMA,
        "created_at": utc(),
        "repeat": repeat,
        "benchmark": {
            "cold_path": "run_trust_graph + decision report + agent summary + state copy",
            "warm_path": "artifact re-hash + exact-context cache query",
            "files_opened_proxy": "deterministic file-touch proxy, not OS-level tracing",
        },
        "summary": summary,
        "rows": rows,
        "miss_matrix": miss_matrix,
        "not_claimed": [
            "does not measure CPU cycles",
            "does not measure energy or CO2",
            "does not measure live-agent token usage",
            "files_opened_proxy is not an OS syscall trace",
        ],
    }


def run_cold(wheel_dir: Path, out: Path, state: Path) -> dict[str, Any]:
    result = run_trust_graph([wheel_dir], out)
    exit_code = graph_exit_code(result)
    finalize_graph_outputs_for_decision(result, output_dir=out)
    decision = write_decision_report(result, exit_code=exit_code, output_dir=out)
    summary = write_agent_summary(result, decision, output_dir=out, state_dir=state)
    contract = summary["agent_action_contract"]
    return {
        "exit_code": exit_code,
        "verdict": result.get("verdict"),
        "combined_verdict": summary.get("combined_verdict"),
        "stop": summary.get("stop"),
        "recommended_agent_action": summary.get("recommended_agent_action"),
        "reason_codes": canonical_list(summary.get("reason_codes", [])),
        "command_fingerprint": summary["summary_of"]["command_fingerprint"],
        "policy_sha256": summary["summary_of"]["policy_sha256"],
        "decision_semantics_version": summary["decision_semantics_version"],
        "tool_version": summary["summary_of"]["tool_version"],
        "summary_bytes": json_size(summary),
        "decision_bytes": Path(decision["decision_json_path"]).stat().st_size,
        "output_bytes": json_size(summary),
        "files_touched_proxy": count_files(out) + count_files(state) + 1,
        "artifact_sha256": contract.get("artifact_sha256"),
    }


def row(index: int, cold: Mapping[str, Any], warm: Mapping[str, Any], cold_seconds: float, warm_seconds: float, state: Path) -> dict[str, Any]:
    warm_reason_codes = canonical_list(warm.get("reason_codes", []))
    return {
        "run": index,
        "cold_wall_seconds": cold_seconds,
        "warm_wall_seconds": warm_seconds,
        "speedup_ratio": cold_seconds / warm_seconds if warm_seconds else None,
        "cold_output_bytes": cold["output_bytes"],
        "warm_output_bytes": json_size(warm),
        "output_ratio": cold["output_bytes"] / json_size(warm),
        "cold_files_touched_proxy": cold["files_touched_proxy"],
        "warm_files_touched_proxy": 1 + count_files(state),
        "cold_exit_code": cold["exit_code"],
        "warm_exit_code": 0 if warm.get("cache_hit") else 2,
        "cold_stop": cold["stop"],
        "warm_stop": warm.get("stop"),
        "cold_action": cold["recommended_agent_action"],
        "warm_action": warm.get("recommended_agent_action"),
        "cold_reason_codes": cold["reason_codes"],
        "warm_reason_codes": warm_reason_codes,
        "cache_hit": warm.get("cache_hit"),
        "context_match": warm.get("context_match"),
        "decision_semantics_match": warm.get("decision_semantics_version") == cold["decision_semantics_version"],
        "action_equivalent": (
            warm.get("stop") == cold["stop"]
            and warm.get("recommended_agent_action") == cold["recommended_agent_action"]
            and warm_reason_codes == cold["reason_codes"]
        ),
    }


def build_miss_matrix(cold: Mapping[str, Any]) -> dict[str, Any]:
    wheel = Path(cold["wheel"])
    state = Path(cold["state"])
    cases = {
        "policy_changed": build_agent_verdict_cache(
            wheel,
            command_fingerprint=str(cold["command_fingerprint"]),
            policy_sha256="p" * 64,
            decision_semantics_version=str(cold["decision_semantics_version"]),
            tool_version=str(cold["tool_version"]),
            state_dir=state,
        ),
        "semantics_changed": build_agent_verdict_cache(
            wheel,
            command_fingerprint=str(cold["command_fingerprint"]),
            policy_sha256=cold["policy_sha256"],
            decision_semantics_version="SPIRA_DECISION_SEMANTICS_TEST_CHANGED",
            tool_version=str(cold["tool_version"]),
            state_dir=state,
        ),
        "tool_version_changed": build_agent_verdict_cache(
            wheel,
            command_fingerprint=str(cold["command_fingerprint"]),
            policy_sha256=cold["policy_sha256"],
            decision_semantics_version=str(cold["decision_semantics_version"]),
            tool_version="different-tool-version",
            state_dir=state,
        ),
    }
    changed = wheel.with_name("cache_bench_pkg-1.0.0-py3-none-any.whl")
    mutate_wheel(changed)
    cases["artifact_changed"] = build_agent_verdict_cache(
        changed,
        command_fingerprint=str(cold["command_fingerprint"]),
        policy_sha256=cold["policy_sha256"],
        decision_semantics_version=str(cold["decision_semantics_version"]),
        tool_version=str(cold["tool_version"]),
        state_dir=state,
    )
    return {
        name: {
            "cache_hit": result.get("cache_hit"),
            "context_match": result.get("context_match"),
            "recommended_agent_action": result.get("recommended_agent_action"),
            "reason_codes": result.get("reason_codes"),
            "passed": result.get("cache_hit") is False and result.get("recommended_agent_action") == "RERUN_REQUIRED",
        }
        for name, result in cases.items()
    }


def summarize(rows: list[Mapping[str, Any]], miss_matrix: Mapping[str, Any]) -> dict[str, Any]:
    cold_times = [float(row["cold_wall_seconds"]) for row in rows]
    warm_times = [float(row["warm_wall_seconds"]) for row in rows]
    speedups = [float(row["speedup_ratio"]) for row in rows if row["speedup_ratio"] is not None]
    warm_bytes = [int(row["warm_output_bytes"]) for row in rows]
    cold_bytes = [int(row["cold_output_bytes"]) for row in rows]
    return {
        "runs": len(rows),
        "cold_wall_seconds": stats(cold_times),
        "warm_wall_seconds": stats(warm_times),
        "speedup_ratio": stats(speedups),
        "cold_output_bytes": stats(cold_bytes),
        "warm_output_bytes": stats(warm_bytes),
        "all_cache_hits": all(row["cache_hit"] is True for row in rows),
        "all_context_matches": all(row["context_match"] is True for row in rows),
        "all_actions_equivalent": all(row["action_equivalent"] is True for row in rows),
        "all_miss_cases_fail_closed": all(item.get("passed") is True for item in miss_matrix.values()),
    }


def write_outputs(result: Mapping[str, Any], json_out: Path, csv_out: Path, summary_out: Path) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    csv_out.parent.mkdir(parents=True, exist_ok=True)
    summary_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    with csv_out.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(result["rows"][0].keys()))
        writer.writeheader()
        writer.writerows(result["rows"])
    summary_out.write_text(markdown_summary(result), encoding="utf-8", newline="\n")


def markdown_summary(result: Mapping[str, Any]) -> str:
    summary = result["summary"]
    return "\n".join(
        [
            "# Cache Performance Benchmark v1",
            "",
            f"Created: {result['created_at']}",
            "",
            "Cold path: full graph verification, decision, agent summary, state copy.",
            "Warm path: artifact re-hash and exact-context cache query.",
            "",
            "```text",
            f"runs: {summary['runs']}",
            f"cold median seconds: {summary['cold_wall_seconds']['median']:.6f}",
            f"warm median seconds: {summary['warm_wall_seconds']['median']:.6f}",
            f"median speedup ratio: {summary['speedup_ratio']['median']:.2f}x",
            f"cold median output bytes: {summary['cold_output_bytes']['median']}",
            f"warm median output bytes: {summary['warm_output_bytes']['median']}",
            f"all cache hits: {summary['all_cache_hits']}",
            f"all actions equivalent: {summary['all_actions_equivalent']}",
            f"all miss cases fail closed: {summary['all_miss_cases_fail_closed']}",
            "```",
            "",
            "Not claimed: CPU cycles, energy, CO2, live-agent token savings, or OS-level file-open tracing.",
            "",
        ]
    )


def build_wheel(wheel_dir: Path, *, payload: bytes) -> Path:
    wheel = wheel_dir / "cache_bench_pkg-1.0.0-py3-none-any.whl"
    with zipfile.ZipFile(wheel, "w") as zf:
        zf.writestr("cache_bench_pkg/__init__.py", payload)
        zf.writestr(
            "cache_bench_pkg-1.0.0.dist-info/METADATA",
            "Metadata-Version: 2.1\nName: cache-bench-pkg\nVersion: 1.0.0\n",
        )
        zf.writestr(
            "cache_bench_pkg-1.0.0.dist-info/WHEEL",
            "Wheel-Version: 1.0\nGenerator: spira-cache-benchmark\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
        zf.writestr("cache_bench_pkg-1.0.0.dist-info/RECORD", "")
    return wheel


def mutate_wheel(wheel: Path) -> None:
    build_wheel(wheel.parent, payload=b"print('changed')\n")


def count_files(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for item in path.rglob("*") if item.is_file())


def json_size(payload: Any) -> int:
    return len(json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def canonical_list(values: Any) -> list[str]:
    if not isinstance(values, list):
        return []
    return sorted({str(value) for value in values})


def stats(values: list[float | int]) -> dict[str, float | int]:
    ordered = sorted(values)
    p90_index = min(len(ordered) - 1, int(0.9 * (len(ordered) - 1)))
    return {
        "min": ordered[0],
        "median": statistics.median(ordered),
        "p90": ordered[p90_index],
        "max": ordered[-1],
    }


def utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
