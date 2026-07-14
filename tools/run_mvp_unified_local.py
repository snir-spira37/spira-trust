from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import mvp_unified  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the bounded local SPIRA MVP router.")
    parser.add_argument("--domain", choices=sorted(mvp_unified.SUPPORTED_DOMAINS), help="Explicit accepted evidence domain.")
    parser.add_argument("--case-id", help="Corpus case ID or Domain 1 artifact SHA.")
    parser.add_argument("--evidence-path", help="Optional evidence path for exact unambiguous domain detection.")
    parser.add_argument("--agent-contract", action="store_true", help="Emit the compact agent-facing contract.")
    parser.add_argument("--passthrough-envelope", action="store_true", help="Emit the machine-contract passthrough envelope.")
    parser.add_argument("--model-explanation", help="Optional non-authoritative explanation text for passthrough mode.")
    args = parser.parse_args()

    result = mvp_unified.route(domain=args.domain, evidence_path=args.evidence_path, case_id=args.case_id, root=ROOT)
    if args.passthrough_envelope:
        result = mvp_unified.passthrough_envelope(result, model_explanation_text=args.model_explanation)
    elif args.agent_contract:
        result = mvp_unified.agent_contract(result)
    print(json.dumps(result, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
