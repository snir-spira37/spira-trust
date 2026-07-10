#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import statistics
import time
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import run_pilot


DEFAULT_METHODOLOGY = "research/pep770_survey/methodology.v5.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the PEP 770 full survey with streaming wheel downloads.")
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--raw-output", required=True)
    parser.add_argument("--public-output")
    parser.add_argument("--methodology", default=DEFAULT_METHODOLOGY)
    parser.add_argument("--sleep", type=float, default=0.2)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--keep-wheels", action="store_true", help="Keep downloaded wheels under work-dir/wheels.")
    parser.add_argument("--keep-spira-outputs", action="store_true", help="Keep per-wheel SPIRA evidence directories.")
    args = parser.parse_args(argv)

    manifest_path = Path(args.manifest)
    work_dir = Path(args.work_dir)
    wheels_dir = work_dir / "wheels"
    outputs_dir = work_dir / "spira_outputs"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    picks = selected_wheels(json.loads(manifest_path.read_text(encoding="utf-8")))
    if args.limit:
        picks = picks[: args.limit]

    raw_output = Path(args.raw_output)
    report = load_or_create_report(
        raw_output,
        resume=args.resume,
        manifest_path=manifest_path,
        work_dir=work_dir,
        methodology=args.methodology,
    )
    completed = {str(item.get("filename")) for item in report.get("results", []) if isinstance(item, dict)}

    for index, pick in enumerate(picks, start=1):
        if str(pick.get("filename")) in completed:
            continue
        result = run_pilot.run_one(index, pick, wheels_dir=wheels_dir, outputs_dir=outputs_dir)
        if result.get("download", {}).get("sha256_matches_pypi") is False:
            result["survey_category"] = "TOOL_ERROR"
            result["tool_error"] = "downloaded wheel sha256 did not match PyPI digest"
        result["wheel_retained"] = bool(args.keep_wheels)
        result["spira_output_retained"] = bool(args.keep_spira_outputs)
        if not args.keep_wheels:
            wheel_path = wheels_dir / str(pick["filename"])
            if wheel_path.exists():
                wheel_path.unlink()
        if not args.keep_spira_outputs:
            output_dir = outputs_dir / run_pilot.safe_dir_name(index, str(pick["package"]))
            if output_dir.exists():
                shutil.rmtree(output_dir)
        report["results"].append(result)
        report["completed_at"] = now()
        report["summary"] = summarize_public(report["results"])
        write_json(raw_output, report)
        if args.public_output:
            write_json(Path(args.public_output), public_report(report, public_output=True))
        print(f"{len(report['results'])}/{len(picks)} {pick['package']} {result.get('survey_category')}", flush=True)
        time.sleep(args.sleep)

    report["completed_at"] = now()
    report["summary"] = summarize_public(report["results"])
    write_json(raw_output, report)
    if args.public_output:
        write_json(Path(args.public_output), public_report(report, public_output=True))
    print(f"wrote {raw_output} with {len(report['results'])} results")
    return 0


def selected_wheels(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    picks = []
    for entry in manifest.get("packages") or []:
        if entry.get("selection_status") == "SELECTED" and entry.get("selected_wheel"):
            picks.append(entry["selected_wheel"])
    return picks


def load_or_create_report(
    path: Path,
    *,
    resume: bool,
    manifest_path: Path,
    work_dir: Path,
    methodology: str,
) -> dict[str, Any]:
    if resume and path.exists():
        existing = json.loads(path.read_text(encoding="utf-8"))
        existing["resumed_at"] = now()
        return existing
    return {
        "schema": "SPIRA_PEP770_SURVEY_FULL_RAW_RESULTS_V1",
        "started_at": now(),
        "completed_at": None,
        "methodology": methodology,
        "manifest": run_pilot.portable_path(manifest_path),
        "work_dir": run_pilot.portable_path(work_dir),
        "results": [],
        "summary": {},
        "not_claimed": not_claimed(),
    }


def public_report(report: dict[str, Any], *, public_output: bool) -> dict[str, Any]:
    return {
        "schema": "SPIRA_PEP770_SURVEY_FULL_PUBLIC_RESULTS_V1",
        "started_at": report.get("started_at"),
        "completed_at": report.get("completed_at"),
        "methodology": report.get("methodology"),
        "manifest": report.get("manifest"),
        "public_scope": "aggregate full-corpus V4 results only",
        "summary": summarize_public(report.get("results") or []),
        "redaction": [
            "Named packages with SBOM_INCONSISTENT, SBOM_INVALID, or TOOL_ERROR outcomes are withheld from public results pending maintainer review.",
            "Raw per-package results are kept locally under work/ and are not committed.",
        ],
        "not_claimed": not_claimed(),
    }


def summarize_public(results: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts: dict[str, int] = {}
    generator_counts: dict[str, int] = {}
    ratios = []
    sbom_bytes = []
    summary_bytes = []
    for item in results:
        category = str(item.get("survey_category"))
        category_counts[category] = category_counts.get(category, 0) + 1
        for family in ((item.get("sbom_generators") or {}).get("families") or ["UNKNOWN"]):
            generator_counts[str(family)] = generator_counts.get(str(family), 0) + 1
        if isinstance(item.get("context_tax_ratio"), (int, float)):
            ratios.append(float(item["context_tax_ratio"]))
        if isinstance(item.get("sbom_total_bytes"), int):
            sbom_bytes.append(int(item["sbom_total_bytes"]))
        if isinstance(item.get("agent_summary_bytes"), int):
            summary_bytes.append(int(item["agent_summary_bytes"]))
    return {
        "processed": len(results),
        "category_counts": dict(sorted(category_counts.items())),
        "generator_family_multilabel_counts": dict(sorted(generator_counts.items())),
        "tool_error_count": category_counts.get("TOOL_ERROR", 0),
        "withheld_named_findings_count": sum(
            category_counts.get(category, 0)
            for category in ("SBOM_INCONSISTENT", "SBOM_INVALID", "TOOL_ERROR")
        ),
        "context_tax": {
            "sbom_total_bytes": describe_ints(sbom_bytes),
            "agent_summary_bytes": describe_ints(summary_bytes),
            "ratio_sbom_bytes_to_agent_summary_bytes": describe_floats(ratios),
        },
    }


def describe_ints(values: list[int]) -> dict[str, int | None]:
    if not values:
        return {"count": 0, "median": None, "p90": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "median": int(statistics.median(ordered)),
        "p90": ordered[p90_index(len(ordered))],
        "max": ordered[-1],
    }


def describe_floats(values: list[float]) -> dict[str, float | int | None]:
    if not values:
        return {"count": 0, "median": None, "p90": None, "max": None}
    ordered = sorted(values)
    return {
        "count": len(ordered),
        "median": round(float(statistics.median(ordered)), 4),
        "p90": round(ordered[p90_index(len(ordered))], 4),
        "max": round(ordered[-1], 4),
    }


def p90_index(length: int) -> int:
    return min(length - 1, int(length * 0.9))


def not_claimed() -> list[str]:
    return [
        "aggregate static consistency survey, not a security audit",
        "SPIRA PEP 770 V1 is a narrow wheel metadata/component consistency check, not full SBOM validation",
        "context-tax measurements are static byte counts only; no live-agent token, latency, energy, or CO2 claim",
        "one selected x86_64/amd64 or py3-none-any wheel per PyPI project",
    ]


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(path)


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
