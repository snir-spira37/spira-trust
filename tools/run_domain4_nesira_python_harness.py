from __future__ import annotations

import argparse
import json
from pathlib import Path

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_domain4_v2_harness import run_harness


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the Domain 4 / Nesira V2 Python harness.")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--output", default=None, help="Optional results JSON path")
    parser.add_argument("--lake-exe", default=None, help="Optional explicit lake executable")
    parser.add_argument("--no-wheel", action="store_true", help="Skip public wheel exclusion check")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    results = run_harness(repo_root, build_wheel=not args.no_wheel, lake_exe=args.lake_exe)
    text = canonical_json(results) + "\n"
    if args.output:
        Path(args.output).write_text(text, encoding="utf-8")
    else:
        print(json.dumps(results, indent=2, sort_keys=True, ensure_ascii=False))
    return 0 if results["verdict"] == "DOMAIN4_NESIRA_PYTHON_HARNESS_ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
