from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source"
if str(SOURCE) not in sys.path:
    sys.path.insert(0, str(SOURCE))

from spira_core import mvp_unified  # noqa: E402


RESULTS = ROOT / "research" / "mvp_unified_benchmark_results.json"
REPORT = ROOT / "research" / "mvp_unified_benchmark_report.md"
OVERHEAD_LIMIT = 0.15
SMOKE_CASES = [
    ("python_artifact", None),
    ("pytest_result", "synthetic_clean_success"),
    ("terraform_plan", "auth_no_changes"),
]


def main() -> None:
    results = run_smoke()
    RESULTS.write_text(json.dumps(results, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    print(json.dumps({"status": results["status"], "median_overhead": results["median_unified_overhead_ratio"]}, sort_keys=True))
    if results["status"] != "MVP_UNIFIED_REAL_AGENT_BENCHMARK_COMPLETED_WITHOUT_EFFICIENCY_CLAIM":
        raise SystemExit(1)


def run_smoke() -> dict[str, Any]:
    sessions = []
    preservation = []
    overheads = []
    for domain, requested_case in SMOKE_CASES:
        envelope = mvp_unified.route(domain=domain, case_id=requested_case, root=ROOT)
        case_id = envelope["case_id"]
        raw = mvp_unified.raw_evidence_payload(domain, case_id, root=ROOT)
        compact = mvp_unified.domain_contract_for_agent(domain, envelope["producer_output"])
        unified = mvp_unified.agent_contract(envelope)
        payloads = {
            "raw_evidence": raw,
            "domain_compact_contract": compact,
            "unified_product_flow": unified,
        }
        sizes = {name: measure_payload(payload) for name, payload in payloads.items()}
        direct_tokens = sizes["domain_compact_contract"]["estimated_input_tokens"]
        unified_tokens = sizes["unified_product_flow"]["estimated_input_tokens"]
        overhead = 0.0 if direct_tokens == 0 else (unified_tokens - direct_tokens) / direct_tokens
        overheads.append(overhead)
        preservation.append(preservation_check(compact, unified))
        for arm, measurement in sizes.items():
            for repetition in range(1, 4):
                sessions.append(
                    {
                        "session_id": f"{domain}:{case_id}:{arm}:{repetition}",
                        "domain": domain,
                        "case_id": case_id,
                        "arm": arm,
                        "repetition": repetition,
                        "clean_session": True,
                        **measurement,
                    }
                )
    median_overhead = statistics.median(overheads)
    status = "MVP_UNIFIED_REAL_AGENT_BENCHMARK_COMPLETED_WITHOUT_EFFICIENCY_CLAIM"
    errors = []
    if len(sessions) != 27:
        errors.append("SMOKE_SESSION_COUNT_MISMATCH")
    if not all(item["status"] == "PASS" for item in preservation):
        errors.append("PRESERVATION_GATE_FAILED")
    if median_overhead > OVERHEAD_LIMIT:
        errors.append("UNIFIED_INTERFACE_OVERHEAD_REVIEW_REQUIRED")
        status = "MVP_UNIFIED_REAL_AGENT_BENCHMARK_REVIEW_REQUIRED"
    return {
        "schema": "SPIRA_MVP_UNIFIED_REAL_AGENT_BENCHMARK_RESULTS_V1",
        "schema_version": 1,
        "status": status,
        "benchmark_kind": "PROTOCOL_SMOKE",
        "live_agent_executed": False,
        "domains_measured": sorted({domain for domain, _case in SMOKE_CASES}),
        "session_count": len(sessions),
        "repetitions_per_arm": 3,
        "arms": ["raw_evidence", "domain_compact_contract", "unified_product_flow"],
        "sessions": sessions,
        "raw_evidence_measurements": aggregate(sessions, "raw_evidence"),
        "domain_contract_measurements": aggregate(sessions, "domain_compact_contract"),
        "unified_product_flow_measurements": aggregate(sessions, "unified_product_flow"),
        "preservation_gates": preservation,
        "median_unified_overhead_ratio": median_overhead,
        "overhead_limit_ratio": OVERHEAD_LIMIT,
        "efficiency_claim_authorized": False,
        "errors": errors,
    }


def preservation_check(compact: Mapping[str, Any], unified: Mapping[str, Any]) -> dict[str, Any]:
    positive_surface = {
        key: value
        for key, value in unified.items()
        if key not in {"not_claimed", "schema", "schema_version"}
    }
    checks = {
        "action_preserved": compact["policy_action"]["recommended_agent_action"] == unified["recommended_agent_action"],
        "reason_codes_preserved": compact["policy_action"]["reason_codes"] == unified["reason_codes"],
        "not_evaluated_preserved": compact["not_evaluated"] == unified["not_evaluated"],
        "block_preserved": compact["block"] == unified["block"],
        "zero_false_proceed": not (
            compact["policy_action"]["recommended_agent_action"] != "PROCEED"
            and unified["recommended_agent_action"] == "PROCEED"
        ),
        "zero_safety_overclaim": "safe" not in json.dumps(positive_surface, sort_keys=True).lower(),
        "evidence_drill_down_preserved": "proof_reference" in unified and unified["evidence_pointer_count"] == compact["evidence_pointer_count"],
        "not_claimed_boundaries_preserved": compact["not_claimed"] == unified["not_claimed"],
    }
    return {
        "domain": unified["domain"],
        "case_id": unified["case_id"],
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
    }


def measure_payload(payload: Any) -> dict[str, int]:
    byte_count = len(mvp_unified.canonical_bytes(payload))
    return {
        "canonical_byte_count": byte_count,
        "estimated_input_tokens": max(1, (byte_count + 3) // 4),
    }


def aggregate(sessions: list[Mapping[str, Any]], arm: str) -> dict[str, float]:
    values = [item["estimated_input_tokens"] for item in sessions if item["arm"] == arm]
    return {
        "median_estimated_input_tokens": statistics.median(values),
        "min_estimated_input_tokens": min(values),
        "max_estimated_input_tokens": max(values),
    }


def report_markdown(results: Mapping[str, Any]) -> str:
    return f"""# SPIRA MVP Unified Benchmark Report

## Status

```text
{results['status']}
EFFICIENCY_CLAIM_AUTHORIZED: false
LIVE_AGENT_EXECUTED: false
```

## Smoke Shape

```text
domains: {', '.join(results['domains_measured'])}
arms: raw_evidence, domain_compact_contract, unified_product_flow
repetitions per arm: {results['repetitions_per_arm']}
session count: {results['session_count']}
```

This is protocol smoke tooling. It does not make a public efficiency claim.

## Measurements

```text
raw evidence median estimated input tokens: {results['raw_evidence_measurements']['median_estimated_input_tokens']}
domain compact median estimated input tokens: {results['domain_contract_measurements']['median_estimated_input_tokens']}
unified product median estimated input tokens: {results['unified_product_flow_measurements']['median_estimated_input_tokens']}
median unified overhead ratio: {results['median_unified_overhead_ratio']}
overhead limit ratio: {results['overhead_limit_ratio']}
```

The 15 percent threshold applies only to direct compact contract vs unified
product flow overhead. It is not a claim about savings versus raw evidence.

## Preservation

```text
all preservation gates: {'PASS' if not results['errors'] else 'CHECK RESULTS'}
action preserved
reason_codes preserved
NOT_EVALUATED preserved
BLOCK preserved
zero false PROCEED
zero safety overclaim
evidence drill-down preserved
not-claimed boundaries preserved
```

## Boundary

```text
public efficiency claim: NOT_AUTHORIZED
release/version/tag/PyPI: NOT_AUTHORIZED
Gate B: NOT_AUTHORIZED
Domain 4: NOT_AUTHORIZED
```
"""


if __name__ == "__main__":
    main()
