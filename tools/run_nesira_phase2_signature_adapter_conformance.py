#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spira_core.nesira_phase2_signature_harness import run_signature_harness


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    repo_root = Path(args[0]).resolve() if args else REPO_ROOT
    results = run_signature_harness(repo_root)
    print(json.dumps(results, sort_keys=True, indent=2))
    return 0 if results["verdict"] == "NESIRA_PHASE2_SIGNATURE_ADAPTER_ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
