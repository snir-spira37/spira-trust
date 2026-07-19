from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPO_ROOT / "source"
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

from spira_core.nesira_domain4_v2_core import canonical_json
from spira_core.nesira_phase2_isolation_attestation_harness import run_isolation_attestation_harness


DEFAULT_OUTPUT = (
    REPO_ROOT
    / "research"
    / "nesira_policy_profile"
    / "nesira_phase2_isolation_attestation_adapter_results.json"
)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-results", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    repo_root = REPO_ROOT
    results = run_isolation_attestation_harness(repo_root)
    text = canonical_json(results)
    print(text)
    if args.write_results:
        output = args.output if args.output.is_absolute() else repo_root / args.output
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text + "\n", encoding="utf-8", newline="\n")
    return 0 if results["verdict"] == "NESIRA_PHASE2_ISOLATION_ATTESTATION_ADAPTER_ACCEPTED" else 1


if __name__ == "__main__":
    raise SystemExit(main())
