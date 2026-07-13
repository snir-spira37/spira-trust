from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import terraform_plan_oracle_validator as validator  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a Domain 3 Terraform Plan oracle document.")
    parser.add_argument("oracle", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    report = validator.validate_oracle_file(args.oracle)
    text = json.dumps(report, sort_keys=True, indent=2)
    if args.output:
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if report["verdict"] != "PASS":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
