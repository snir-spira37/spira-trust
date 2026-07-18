#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spira_core.nesira_phase2_authority_harness import run_authority_harness


DEFAULT_RESULTS = REPO_ROOT / "research" / "nesira_policy_profile" / "nesira_phase2_authority_adapter_results.json"


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    write_results = "--write-results" in args
    args = [arg for arg in args if arg != "--write-results"]
    repo_root = Path(args[0]).resolve() if args else REPO_ROOT
    results = run_authority_harness(repo_root)
    output = json.dumps(results, sort_keys=True, indent=2) + "\n"
    if write_results:
        DEFAULT_RESULTS.write_text(output, encoding="utf-8", newline="\n")
    print(output, end="")
    return 0 if results["verdict"] == "NESIRA_PHASE2_AUTHORITY_ADAPTER_ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
