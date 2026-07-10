#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
import urllib.request
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import collect_corpus


USER_AGENT = collect_corpus.USER_AGENT


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the predeclared PEP 770 pilot selection through SPIRA.")
    parser.add_argument("--selection", required=True)
    parser.add_argument("--work-dir", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--sleep", type=float, default=0.2)
    args = parser.parse_args(argv)

    selection_path = Path(args.selection)
    work_dir = Path(args.work_dir)
    wheels_dir = work_dir / "wheels"
    outputs_dir = work_dir / "spira_outputs"
    wheels_dir.mkdir(parents=True, exist_ok=True)
    outputs_dir.mkdir(parents=True, exist_ok=True)

    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    results = []
    started_at = now()
    for index, pick in enumerate(selection.get("picks", []), start=1):
        results.append(run_one(index, pick, wheels_dir=wheels_dir, outputs_dir=outputs_dir))
        time.sleep(args.sleep)

    report = {
        "schema": "SPIRA_PEP770_SURVEY_PILOT_RESULTS_V1",
        "started_at": started_at,
        "completed_at": now(),
        "selection": portable_path(selection_path),
        "work_dir": portable_path(work_dir),
        "results": results,
        "summary": summarize(results),
        "not_claimed": [
            "pilot is edge-case discovery, not a statistical sample",
            "pilot results are not full-corpus statistics",
            "SPIRA PEP 770 V1 is a narrow consistency check, not full SBOM validation"
        ],
    }
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {output} with {len(results)} pilot results")
    return 0


def run_one(index: int, pick: dict[str, Any], *, wheels_dir: Path, outputs_dir: Path) -> dict[str, Any]:
    package = str(pick["package"])
    filename = str(pick["filename"])
    wheel_path = wheels_dir / filename
    result: dict[str, Any] = {
        "index": index,
        "package": package,
        "version": pick.get("version"),
        "filename": filename,
        "selection_reason": pick.get("selection_reason"),
        "expected_sha256": pick.get("sha256"),
        "size": pick.get("size"),
        "download": {},
        "spira": {},
    }
    try:
        data = download(pick["url"])
        wheel_path.write_bytes(data)
        digest = hashlib.sha256(data).hexdigest()
        result["download"] = {
            "path": portable_path(wheel_path),
            "bytes": len(data),
            "sha256": digest,
            "sha256_matches_pypi": digest == pick.get("sha256"),
        }
        sboms = collect_corpus.embedded_sbom_records(wheel_path)
        result["embedded_sboms"] = sboms
        result["sbom_total_bytes"] = sum(int(item.get("bytes") or 0) for item in sboms)
        result["sbom_generators"] = collect_corpus.summarize_generators(sboms)
        output_dir = outputs_dir / safe_dir_name(index, package)
        output_dir.mkdir(parents=True, exist_ok=True)
        result["spira"] = run_spira(wheel_path, output_dir)
        result["agent_summary_bytes"] = file_size_or_none(result["spira"].get("agent_summary_path"))
        if result.get("agent_summary_bytes"):
            result["context_tax_ratio"] = result["sbom_total_bytes"] / result["agent_summary_bytes"]
        result["survey_category"] = survey_category(result["spira"])
    except Exception as exc:
        result["survey_category"] = "TOOL_ERROR"
        result["tool_error"] = repr(exc)
    return result


def download(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


def run_spira(wheel_path: Path, output_dir: Path) -> dict[str, Any]:
    env = os.environ.copy()
    repo = Path(__file__).resolve().parents[2]
    source = str(repo / "source")
    env["PYTHONPATH"] = source + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    command = [
        sys.executable,
        "-m",
        "spira_core.trust_cli",
        "graph",
        str(wheel_path),
        "--output-dir",
        str(output_dir),
        "--verify-embedded-sboms",
    ]
    completed = subprocess.run(command, cwd=repo, env=env, text=True, capture_output=True, timeout=600)
    paths = find_output_paths(output_dir)
    payload: dict[str, Any] = {
        "command": portable_command(command),
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
        **paths,
    }
    graph_report = read_json(paths.get("graph_report_path"))
    decision = read_json(paths.get("decision_path"))
    agent_summary = read_json(paths.get("agent_summary_path"))
    payload["graph_verdict"] = graph_report.get("verdict") if graph_report else None
    payload["pep770_status"] = (graph_report.get("pep770_sbom_consistency") or {}).get("status") if graph_report else None
    payload["decision_verdict"] = decision.get("verdict") if decision else None
    payload["agent_summary_stop"] = agent_summary.get("stop") if agent_summary else None
    payload["agent_summary_verdict"] = agent_summary.get("verdict") if agent_summary else None
    if completed.returncode not in {0, 1, 2} or not graph_report:
        payload["tool_error"] = "spira command failed or graph_report.json was not produced"
    return payload


def find_output_paths(output_dir: Path) -> dict[str, str | None]:
    return {
        "graph_report_path": first_path(output_dir, "graph_report.json"),
        "decision_path": first_path(output_dir, "spira-decision.json"),
        "agent_summary_path": first_path(output_dir, "agent_summary.json"),
    }


def first_path(root: Path, name: str) -> str | None:
    matches = list(root.rglob(name))
    return portable_path(matches[0]) if matches else None


def read_json(path: str | None) -> dict[str, Any] | None:
    if not path:
        return None
    return json.loads(resolve_portable_path(path).read_text(encoding="utf-8"))


def file_size_or_none(path: str | None) -> int | None:
    return resolve_portable_path(path).stat().st_size if path else None


def portable_command(command: list[str]) -> list[str]:
    portable = command[:]
    if portable:
        portable[0] = Path(portable[0]).name
    return [portable_path(item) if "\\" in item or "/" in item else item for item in portable]


def portable_path(path: str | Path) -> str:
    raw = Path(path)
    repo = Path(__file__).resolve().parents[2]
    try:
        return str(raw.resolve().relative_to(repo)).replace("\\", "/")
    except ValueError:
        return str(raw).replace("\\", "/")


def resolve_portable_path(path: str) -> Path:
    raw = Path(path)
    if raw.is_absolute():
        return raw
    return Path(__file__).resolve().parents[2] / raw


def survey_category(spira: dict[str, Any]) -> str:
    if spira.get("tool_error"):
        return "TOOL_ERROR"
    status = spira.get("pep770_status")
    if status == "VERIFIED_OK":
        return "SBOM_CONSISTENT"
    if status == "CONTRADICTION":
        return "SBOM_INCONSISTENT"
    if status in {"UNVERIFIED", "NOT_EVALUATED", None}:
        return "NOT_EVALUATED"
    return "NOT_EVALUATED"


def summarize(results: list[dict[str, Any]]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    generator_counts: dict[str, int] = {}
    for item in results:
        counts[str(item.get("survey_category"))] = counts.get(str(item.get("survey_category")), 0) + 1
        for family in ((item.get("sbom_generators") or {}).get("families") or ["UNKNOWN"]):
            generator_counts[str(family)] = generator_counts.get(str(family), 0) + 1
    return {
        "category_counts": counts,
        "generator_family_multilabel_counts": generator_counts,
        "tool_error_count": counts.get("TOOL_ERROR", 0),
    }


def safe_dir_name(index: int, package: str) -> str:
    cleaned = "".join(char if char.isalnum() or char in "-_" else "_" for char in package)
    return f"{index:02d}_{cleaned}"


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


if __name__ == "__main__":
    raise SystemExit(main())
