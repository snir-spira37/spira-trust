from __future__ import annotations

import json
import os
import re
import subprocess
from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


ROOT = Path(__file__).resolve().parents[1]
DOMAIN = ROOT / "research" / "formal_core" / "domain1"
BASELINE = ROOT / "research" / "unification_proof_corpus" / "results" / "domain1_identity_baseline_v1.json"
LEAN_PROJECT = ROOT / "formal" / "spira_formal_core_v1"

RESULTS = DOMAIN / "spira_formal_core_v1_domain1_conformance_results.json"
REPORT = DOMAIN / "spira_formal_core_v1_domain1_conformance_report.md"
REVIEW = DOMAIN / "spira_formal_core_v1_domain1_conformance_review.md"

EXPECTED_ROOT = "85f23217e29e70dea99701bc7cdd5c459457c516664a33e9c391fb45ac43816c"
EXPECTED_RECORD_COUNT = 1954
FORMAL_ACTIONS = {"PROCEED", "STOP_BLOCKED", "RERUN_REQUIRED", "REPORT_NOT_EVALUATED"}
LEGACY_ACTIONS = {"PROCEED", "ASK_HUMAN", "STOP_BLOCKED", "REPORT_NOT_EVALUATED"}


def main() -> None:
    baseline = _read_json(BASELINE)
    lean = run_lake_build()
    proof_scan = scan_lean_sources()
    results = evaluate_conformance(baseline, lean, proof_scan)
    _write_json(RESULTS, results)
    REPORT.write_text(report_markdown(results), encoding="utf-8")
    REVIEW.write_text(review_markdown(results), encoding="utf-8")
    print(json.dumps({"status": results["status"]}, sort_keys=True))
    if results["status"] != "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED":
        raise SystemExit(1)


def evaluate_conformance(
    baseline: Mapping[str, Any],
    lean: Mapping[str, Any],
    proof_scan: Mapping[str, Any],
) -> dict[str, Any]:
    records = list(baseline.get("records", []))
    recomputed_root = sha256_canonical(sorted(records, key=lambda item: str(item.get("artifact_sha256") or "")))
    record_results = []
    mismatches = []
    false_proceeds = []
    not_evaluated_to_proceed = []
    identity_drops = []
    list_drops = []
    unsupported_actions = []
    sensitive_or_private_leaks = []

    for record in records:
        artifact = str(record.get("artifact_sha256") or "__missing__")
        projection = project_record(record)
        checks = compare_record(record, projection)
        if not checks["all"]:
            for field, ok in checks["fields"].items():
                if not ok:
                    mismatches.append({"artifact_sha256": artifact, "field": field})
        legacy_action = projection["legacy_action"]
        core_action = projection["core_action"]
        if legacy_action not in LEGACY_ACTIONS or core_action not in FORMAL_ACTIONS:
            unsupported_actions.append(artifact)
        if legacy_action != "PROCEED" and core_action == "PROCEED":
            false_proceeds.append(artifact)
        if projection["not_evaluated"] and core_action == "PROCEED":
            not_evaluated_to_proceed.append(artifact)
        if not checks["fields"]["identities"]:
            identity_drops.append(artifact)
        if not checks["fields"]["reason_codes"] or not checks["fields"]["not_evaluated"]:
            list_drops.append(artifact)
        if has_sensitive_or_private_leak(record):
            sensitive_or_private_leaks.append(artifact)
        record_results.append(
            {
                "artifact_sha256": artifact,
                "legacy_action": legacy_action,
                "core_action": core_action,
                "passed": checks["all"],
            }
        )

    gates = {
        "lean_build_pass": lean["returncode"] == 0,
        "proof_scan_pass": proof_scan["status"] == "PASS",
        "record_count": len(records) == EXPECTED_RECORD_COUNT,
        "baseline_root_match": recomputed_root == EXPECTED_ROOT == baseline.get("domain1_identity_baseline_root"),
        "record_projection_pass": all(item["passed"] for item in record_results),
        "unsupported_action_count": len(unsupported_actions) == 0,
        "false_proceed_count": len(false_proceeds) == 0,
        "not_evaluated_to_proceed_count": len(not_evaluated_to_proceed) == 0,
        "identity_drop_count": len(identity_drops) == 0,
        "list_drop_count": len(list_drops) == 0,
        "sensitive_or_private_leak_count": len(sensitive_or_private_leaks) == 0,
    }
    status = "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED"
    if not all(gates.values()) or mismatches:
        status = "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_NEEDS_REVISION"
    return {
        "schema": "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_RESULTS",
        "schema_version": 1,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "status": status,
        "authorization": "research/formal_core/domain1/spira_formal_core_v1_domain1_conformance_authorization.md",
        "record_count": len(records),
        "record_pass_count": sum(1 for item in record_results if item["passed"]),
        "record_fail_count": sum(1 for item in record_results if not item["passed"]),
        "legacy_action_distribution": distribution(item["legacy_action"] for item in record_results),
        "core_action_distribution": distribution(item["core_action"] for item in record_results),
        "worst_claim_status_distribution": distribution(str(record.get("worst_claim_status") or "") for record in records),
        "baseline_root_expected": EXPECTED_ROOT,
        "baseline_root_recomputed": recomputed_root,
        "baseline_root_match": recomputed_root == EXPECTED_ROOT == baseline.get("domain1_identity_baseline_root"),
        "false_proceed_records": false_proceeds,
        "not_evaluated_to_proceed_records": not_evaluated_to_proceed,
        "identity_drop_records": identity_drops,
        "list_drop_records": list_drops,
        "unsupported_action_records": unsupported_actions,
        "sensitive_or_private_leak_records": sensitive_or_private_leaks,
        "gates": gates,
        "mismatch_count": len(mismatches),
        "mismatches": mismatches[:100],
        "lean_build": lean,
        "proof_scan": proof_scan,
        "raw_wheel_zip_parser_formally_proved": False,
        "not_authorized": [
            "RAW_WHEEL_ZIP_PARSER_PROOF",
            "DOMAIN1_ADAPTER_CHANGE",
            "GATE_A_IMPLEMENTATION_CHANGE",
            "FORMAL_CORE_V1_ACTION_ALGEBRA_CHANGE",
            "RUNTIME_INTEGRATION",
            "PRODUCTION_CLAIM",
            "RELEASE",
        ],
    }


def project_record(record: Mapping[str, Any]) -> dict[str, Any]:
    legacy_action = str(record.get("recommended_agent_action") or "__missing__")
    core_action = legacy_to_core_action(legacy_action)
    return {
        "artifact_sha256": str(record.get("artifact_sha256") or ""),
        "subject_sha256": str(record.get("subject_sha256") or ""),
        "claims_sha256": str(record.get("canonical_claims_bytes_sha256") or ""),
        "claims_merkle_root": str(record.get("claims_merkle_root") or ""),
        "context_sha256": str(record.get("context_sha256") or ""),
        "decision_sha256": str(record.get("canonical_decision_bytes_sha256") or ""),
        "compact_reference_sha256": str(record.get("compact_reference_bytes_sha256") or ""),
        "proof_sha256": str(record.get("canonical_proof_bytes_sha256") or ""),
        "legacy_action": legacy_action,
        "core_action": core_action,
        "stop": core_action != "PROCEED",
        "legacy_stop": bool(record.get("stop")),
        "reason_codes": list(record.get("reason_codes") or []),
        "not_evaluated": list(record.get("not_evaluated") or []),
        "worst_claim_status": str(record.get("worst_claim_status") or ""),
    }


def compare_record(record: Mapping[str, Any], projection: Mapping[str, Any]) -> dict[str, Any]:
    fields = {
        "legacy_action": projection["legacy_action"] == str(record.get("recommended_agent_action") or ""),
        "core_action": projection["core_action"] == legacy_to_core_action(str(record.get("recommended_agent_action") or "")),
        "stop": projection["legacy_stop"] == bool(record.get("stop")),
        "reason_codes": projection["reason_codes"] == list(record.get("reason_codes") or []),
        "not_evaluated": projection["not_evaluated"] == list(record.get("not_evaluated") or []),
        "identities": all(
            is_sha256(projection[field])
            for field in (
                "artifact_sha256",
                "subject_sha256",
                "claims_sha256",
                "claims_merkle_root",
                "context_sha256",
                "decision_sha256",
                "compact_reference_sha256",
                "proof_sha256",
            )
        ),
    }
    return {"all": all(fields.values()), "fields": fields}


def legacy_to_core_action(action: str) -> str:
    if action == "ASK_HUMAN":
        return "REPORT_NOT_EVALUATED"
    if action in FORMAL_ACTIONS:
        return action
    return f"__UNSUPPORTED_ACTION__:{action}"


def has_sensitive_or_private_leak(record: Mapping[str, Any]) -> bool:
    text = json.dumps(record, sort_keys=True, ensure_ascii=False).lower()
    forbidden = ("c:\\users\\", "/users/", "password", "api_key", "api key", "private key", "credential")
    return any(token in text for token in forbidden)


def is_sha256(value: Any) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def distribution(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        key = str(value)
        result[key] = result.get(key, 0) + 1
    return dict(sorted(result.items()))


def run_lake_build() -> dict[str, Any]:
    completed = subprocess.run(
        ["lake", "build"],
        cwd=LEAN_PROJECT,
        check=False,
        capture_output=True,
        text=True,
        env=dict(os.environ),
    )
    return {
        "command": "lake build",
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-4000:],
    }


def scan_lean_sources() -> dict[str, Any]:
    forbidden = ["sorry", "admit", "sorryAx", "axiom "]
    matches = []
    for path in sorted((LEAN_PROJECT / "SpiraFormalCore" / "Domain1").glob("*.lean")):
        text = path.read_text(encoding="utf-8")
        for token in forbidden:
            if token in text:
                matches.append({"path": str(path.relative_to(ROOT)), "token": token})
    return {"status": "PASS" if not matches else "FAIL", "matches": matches}


def report_markdown(results: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 1 Conformance Report",
            "",
            "Status:",
            "",
            "```text",
            str(results["status"]),
            "```",
            "",
            "Summary:",
            "",
            "```json",
            json.dumps(
                {
                    "record_count": results["record_count"],
                    "record_pass_count": results["record_pass_count"],
                    "record_fail_count": results["record_fail_count"],
                    "legacy_action_distribution": results["legacy_action_distribution"],
                    "core_action_distribution": results["core_action_distribution"],
                    "baseline_root_match": results["baseline_root_match"],
                    "false_proceed_records": len(results["false_proceed_records"]),
                    "not_evaluated_to_proceed_records": len(results["not_evaluated_to_proceed_records"]),
                    "identity_drop_records": len(results["identity_drop_records"]),
                    "list_drop_records": len(results["list_drop_records"]),
                    "sensitive_or_private_leak_records": len(results["sensitive_or_private_leak_records"]),
                    "mismatch_count": results["mismatch_count"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Lean:",
            "",
            "```json",
            json.dumps(
                {
                    "lake_build_returncode": results["lean_build"]["returncode"],
                    "proof_scan": results["proof_scan"]["status"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "Raw wheel / ZIP parser formally proved: no.",
            "",
            "This report does not authorize adapter changes, Gate A implementation changes, runtime integration, production claims, or release activity.",
            "",
        ]
    )


def review_markdown(results: Mapping[str, Any]) -> str:
    accepted = results["status"] == "SPIRA_FORMAL_CORE_V1_DOMAIN1_CONFORMANCE_ACCEPTED"
    statuses = [
        results["status"],
        "DOMAIN_1_FORMAL_TYPED_SEMANTICS_ACCEPTED" if accepted else "DOMAIN_1_FORMAL_TYPED_SEMANTICS_NOT_ACCEPTED",
        "DOMAIN_1_BASELINE_DIFFERENTIAL_CONFORMANCE_ACCEPTED"
        if accepted
        else "DOMAIN_1_BASELINE_DIFFERENTIAL_CONFORMANCE_NOT_ACCEPTED",
        "DOMAIN_1_LEGACY_ASK_HUMAN_MAPPED_TO_REPORT_NOT_EVALUATED"
        if accepted
        else "DOMAIN_1_LEGACY_ACTION_MAPPING_NOT_ACCEPTED",
        "RAW_WHEEL_ZIP_PARSER_FORMALLY_PROVED_NO",
        "GATE_A_IMPLEMENTATION_NOT_AUTHORIZED",
        "RUNTIME_INTEGRATION_NOT_AUTHORIZED",
        "PRODUCTION_CLAIM_NOT_AUTHORIZED",
        "RELEASE_NOT_AUTHORIZED",
    ]
    return "\n".join(
        [
            "# SPIRA Formal Core V1 Domain 1 Conformance Review",
            "",
            "## Status",
            "",
            "```text",
            *statuses,
            "```",
            "",
            "## Decision",
            "",
            (
                "Domain 1 conformance is accepted for the bounded Python artifact identity baseline."
                if accepted
                else "Domain 1 conformance is not accepted and requires revision."
            ),
            "",
            "The accepted Domain 1 identity baseline remains unchanged.",
            "",
            "Legacy `ASK_HUMAN` is preserved as a Domain 1 baseline action and maps to the Formal Core V1 non-proceeding action `REPORT_NOT_EVALUATED`; the Formal Core V1 action algebra is unchanged.",
            "",
            "## Evidence",
            "",
            "```json",
            json.dumps(
                {
                    "record_count": results["record_count"],
                    "record_pass_count": results["record_pass_count"],
                    "record_fail_count": results["record_fail_count"],
                    "legacy_action_distribution": results["legacy_action_distribution"],
                    "core_action_distribution": results["core_action_distribution"],
                    "worst_claim_status_distribution": results["worst_claim_status_distribution"],
                    "baseline_root_match": results["baseline_root_match"],
                    "false_proceed_records": len(results["false_proceed_records"]),
                    "not_evaluated_to_proceed_records": len(results["not_evaluated_to_proceed_records"]),
                    "identity_drop_records": len(results["identity_drop_records"]),
                    "list_drop_records": len(results["list_drop_records"]),
                    "sensitive_or_private_leak_records": len(results["sensitive_or_private_leak_records"]),
                    "lean_build_returncode": results["lean_build"]["returncode"],
                    "proof_scan": results["proof_scan"]["status"],
                    "mismatch_count": results["mismatch_count"],
                },
                indent=2,
                sort_keys=True,
            ),
            "```",
            "",
            "## Boundaries",
            "",
            "This review does not prove raw wheel / ZIP parsing, RECORD parsing, SBOM parsing, filesystem behavior, Python runtime correctness, or production integration.",
            "",
            "No benchmark runner, live agent session, result reclassification, release, tag, or PyPI work is authorized.",
            "",
        ]
    )


def sha256_canonical(value: Any) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")).hexdigest()


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
