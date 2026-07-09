#!/usr/bin/env python3
"""
SPIRA agent-savings benchmark v2.

Measures how many bytes/estimated-tokens an agent must ingest to answer
common gate questions, comparing baseline flows (reading raw evidence files)
against SPIRA flows (agent_summary.json / real captured status output).

    python bench_agent_savings.py --evidence-dir path/to/evidence/graph \
        --status-json status.json --repeat 10 --json-out agent_savings_v1.json

Honesty rules of this script:
- Measured figures come from actual file sizes on disk.
- Modeled figures (baseline skim fraction, bytes-per-token) are explicitly
  labeled as assumptions and configurable.
- Q2 (already-checked flow) is reported ONLY when a real captured
  `spira-trust status --format json` output file is provided. No proxy.
- Invalid inputs fail loudly; nothing is silently clamped or corrected.
"""

import argparse
import json
import sys
from pathlib import Path

TOKEN_BYTES = 4  # modeled average bytes-per-token for JSON/English (assumption)


def est_tokens(n_bytes: int) -> int:
    return round(n_bytes / TOKEN_BYTES)


def file_size(path: Path) -> int:
    return path.stat().st_size if path.is_file() else 0


def find_first(directory: Path, names: list[str]) -> Path | None:
    for name in names:
        p = directory / name
        if p.is_file():
            return p
    for name in names:
        hits = sorted(directory.rglob(name))
        if hits:
            return hits[0]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--evidence-dir",
        type=Path,
        required=True,
        help="Directory containing graph_report.json, spira-decision.json, agent_summary.json, bill_of_materials.json",
    )
    ap.add_argument(
        "--status-json",
        type=Path,
        default=None,
        help="Captured output of: spira-trust status <artifact-dir> --format json",
    )
    ap.add_argument(
        "--report-skim-fraction",
        type=float,
        default=0.25,
        help="MODELED fraction of graph_report.json read by a realistic baseline agent (assumption, not measurement)",
    )
    ap.add_argument(
        "--repeat",
        type=int,
        default=10,
        help="How many times the question is asked across a session/CI (amortization factor)",
    )
    ap.add_argument("--json-out", type=Path, default=None)
    args = ap.parse_args()

    if args.repeat < 1:
        print("ERROR: --repeat must be >= 1", file=sys.stderr)
        return 1
    if not (0.0 <= args.report_skim_fraction <= 1.0):
        print("ERROR: --report-skim-fraction must be between 0 and 1", file=sys.stderr)
        return 1

    ev = args.evidence_dir
    if not ev.is_dir():
        print(f"ERROR: evidence dir not found: {ev}", file=sys.stderr)
        return 1

    graph_report = find_first(ev, ["graph_report.json"])
    decision = find_first(ev, ["spira-decision.json"])
    summary = find_first(ev, ["agent_summary.json"])
    bom = find_first(ev, ["bill_of_materials.json"])
    graph_txt = find_first(ev, ["graph_summary.txt"])

    missing = [
        n
        for n, p in [
            ("graph_report.json", graph_report),
            ("spira-decision.json", decision),
            ("agent_summary.json", summary),
        ]
        if p is None
    ]
    if missing:
        print(f"ERROR: missing required files in {ev}: {missing}", file=sys.stderr)
        return 1

    status_size = None
    if args.status_json is not None:
        if not args.status_json.is_file():
            print(f"ERROR: status json not found: {args.status_json}", file=sys.stderr)
            return 1
        status_size = file_size(args.status_json)

    sizes = {
        "graph_report.json": file_size(graph_report),
        "spira-decision.json": file_size(decision),
        "agent_summary.json": file_size(summary),
        "bill_of_materials.json": file_size(bom) if bom else 0,
        "graph_summary.txt": file_size(graph_txt) if graph_txt else 0,
        "status.json (real captured)": status_size if status_size is not None else "not provided",
    }

    skim = args.report_skim_fraction

    q1_base_pess = sizes["graph_report.json"] + sizes["spira-decision.json"] + sizes["bill_of_materials.json"]
    q1_base_real = sizes["spira-decision.json"] + round(skim * sizes["graph_report.json"])  # MODELED
    q1_base_min = sizes["spira-decision.json"]
    q1_spira = sizes["agent_summary.json"]

    r = args.repeat

    def line(name, base, spira):
        saved = base - spira
        pct = (saved / base * 100) if base else 0.0
        return {
            "flow": name,
            "baseline_bytes": base,
            "spira_bytes": spira,
            "saved_bytes": saved,
            "saved_pct": round(pct, 1),
            "baseline_tokens_est": est_tokens(base),
            "spira_tokens_est": est_tokens(spira),
            "saved_tokens_est": est_tokens(saved),
            "saved_tokens_est_x_repeat": est_tokens(saved) * r,
        }

    results = [
        line("Q1 verdict/stop - baseline pessimistic (full report+decision+BOM)", q1_base_pess, q1_spira),
        line(f"Q1 verdict/stop - baseline realistic (decision + MODELED {skim:.0%} report skim)", q1_base_real, q1_spira),
        line("Q1 verdict/stop - baseline minimal (decision only)", q1_base_min, q1_spira),
    ]

    if status_size is not None:
        q2_base_real = sizes["spira-decision.json"] + round(skim * sizes["graph_report.json"])  # MODELED
        q2_base_min = sizes["spira-decision.json"]
        results.append(line("Q2 already-checked - baseline realistic (MODELED skim)", q2_base_real, status_size))
        results.append(line("Q2 already-checked - baseline minimal (decision only)", q2_base_min, status_size))
    else:
        print(
            "NOTE: --status-json not provided; Q2 (already-checked flow) is NOT reported. "
            "Capture real output via: spira-trust status <dir> --format json > status.json",
            file=sys.stderr,
        )

    report = {
        "schema": "SPIRA_AGENT_SAVINGS_BENCH_V2",
        "inputs": {str(k): v for k, v in sizes.items()},
        "baseline_assumptions": {
            "token_estimate_method": f"bytes / {TOKEN_BYTES} (modeled average; real tokenizer counts vary)",
            "q1_realistic_report_skim_fraction": skim,
            "q1_realistic": "decision file + modeled fraction of graph_report.json (MODELED baseline)",
            "q1_minimal": "decision file only (measured)",
            "q1_pessimistic": "full report + decision + BOM (measured)",
            "q2_requires_status_json": "Q2 SPIRA flow is reported only when real captured status JSON is provided",
            "status_json_source": (
                "local captured output from spira-trust status; not included in release assets"
                if status_size is not None
                else "not provided"
            ),
        },
        "repeat_factor": r,
        "results": results,
        "not_claimed": [
            "This measures context-ingestion cost only, not correctness or safety.",
            "Token estimates are approximations; real tokenizer counts vary.",
            "No energy or CO2 claim is made.",
            "Baseline assumes the agent already knows where evidence files are; discovery cost is excluded, which favors the baseline.",
            "The 'realistic' baselines depend on a modeled skim fraction and are labeled as such.",
            "Savings depend on how often the question is asked; single-run savings may be small.",
        ],
    }

    print(f"\nSPIRA agent-savings benchmark v2 (modeled skim: {skim:.0%})\n")
    print("Input sizes: " + ", ".join(f"{k}={v}" + ("B" if isinstance(v, int) else "") for k, v in sizes.items()))
    print()
    flow_width = 92
    hdr = f"{'flow':{flow_width}} {'base':>8} {'spira':>7} {'saved':>7} {'pct':>6} {'tok saved':>10}"
    print(hdr)
    print("-" * len(hdr))
    for row in results:
        print(
            f"{row['flow'][:flow_width]:{flow_width}} {row['baseline_bytes']:>8} {row['spira_bytes']:>7} "
            f"{row['saved_bytes']:>7} {row['saved_pct']:>5}% {row['saved_tokens_est']:>10}"
        )
    print("\nMODELED ASSUMPTIONS: skim fraction, bytes-per-token. All other figures measured from disk.")
    print("\nNOT CLAIMED:")
    for nc in report["not_claimed"]:
        print(f"  - {nc}")

    if args.json_out:
        args.json_out.write_text(json.dumps(report, indent=2))
        print(f"\nJSON written: {args.json_out}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
