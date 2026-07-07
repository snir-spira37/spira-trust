from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping


POLICY_SCHEMA = "SPIRA_LICENSE_POLICY_V1"
POLICY_SCHEMA_VERSION = "1.0"
MATCH_MODE = "case_insensitive_substring"


def load_license_policy(path: str | Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    policy_path = Path(path)
    payload = json.loads(policy_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("license policy must be a JSON object")
    schema = payload.get("schema", POLICY_SCHEMA)
    if schema != POLICY_SCHEMA:
        raise ValueError(f"unsupported license policy schema: {schema}")
    match_mode = payload.get("match_mode", MATCH_MODE)
    if match_mode != MATCH_MODE:
        raise ValueError(f"unsupported license policy match_mode: {match_mode}")
    return {
        "schema": POLICY_SCHEMA,
        "schema_version": str(payload.get("schema_version", POLICY_SCHEMA_VERSION)),
        "path": str(policy_path.resolve()),
        "sha256": sha256(policy_path.read_bytes()).hexdigest(),
        "match_mode": MATCH_MODE,
        "blocked_terms": _terms(payload.get("blocked_terms", [])),
        "warn_terms": _terms(payload.get("warn_terms", [])),
        "not_claimed": [
            "policy performs explicit local string screening only",
            "policy is not legal advice or legal compliance certification",
            "policy is not SPDX expression parsing",
        ],
    }


def evaluate_license_policy(bom: Mapping[str, Any], policy: Mapping[str, Any] | None) -> dict[str, Any]:
    if policy is None:
        return {
            "evaluated": False,
            "verdict": "LICENSE_POLICY_NOT_PROVIDED",
            "findings": [],
            "not_claimed": ["no user-provided license policy file was supplied"],
        }

    findings = []
    for artifact in bom.get("artifacts", []):
        if artifact.get("relationship") == "declared_missing":
            continue
        observed = _observed_license_strings(artifact)
        for severity, terms in (("BLOCK", policy.get("blocked_terms", [])), ("WARN", policy.get("warn_terms", []))):
            for term in terms:
                normalized_term = str(term).casefold()
                for source in observed:
                    value = str(source["value"])
                    if normalized_term and normalized_term in value.casefold():
                        findings.append(
                            {
                                "severity": severity,
                                "node_id": artifact.get("node_id"),
                                "name": artifact.get("name"),
                                "version": artifact.get("version"),
                                "relationship": artifact.get("relationship"),
                                "term": str(term),
                                "source_field": source["field"],
                                "observed_value": value,
                                "note": "matched explicit user-provided license policy term",
                            }
                        )

    verdict = "LICENSE_POLICY_PASS"
    if any(finding["severity"] == "BLOCK" for finding in findings):
        verdict = "LICENSE_POLICY_BLOCK"
    elif any(finding["severity"] == "WARN" for finding in findings):
        verdict = "LICENSE_POLICY_WARN"

    return {
        "evaluated": True,
        "schema": str(policy.get("schema", POLICY_SCHEMA)),
        "schema_version": str(policy.get("schema_version", POLICY_SCHEMA_VERSION)),
        "policy_ref": {
            "path": policy.get("path"),
            "sha256": policy.get("sha256"),
        },
        "match_mode": policy.get("match_mode", MATCH_MODE),
        "blocked_terms_count": len(policy.get("blocked_terms", [])),
        "warn_terms_count": len(policy.get("warn_terms", [])),
        "verdict": verdict,
        "findings": findings,
        "not_claimed": list(policy.get("not_claimed", [])),
    }


def _terms(value: Any) -> list[str]:
    if not isinstance(value, list):
        raise ValueError("license policy terms must be lists")
    terms = []
    for item in value:
        text = str(item).strip()
        if text:
            terms.append(text)
    return terms


def _observed_license_strings(artifact: Mapping[str, Any]) -> list[dict[str, str]]:
    visibility = artifact.get("license_visibility", {})
    observed: list[dict[str, str]] = []
    if visibility.get("metadata_license"):
        observed.append({"field": "metadata_license", "value": str(visibility["metadata_license"])})
    for classifier in visibility.get("license_classifiers", []):
        observed.append({"field": "license_classifier", "value": str(classifier)})
    for file in visibility.get("license_files", []):
        if file.get("path"):
            observed.append({"field": "license_file_path", "value": str(file["path"])})
        if file.get("text_sample"):
            observed.append({"field": "license_file_text_sample", "value": str(file["text_sample"])})
    return observed
