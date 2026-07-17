from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from spira_core import nesira_policy_profile_validator as phase1
from spira_core.nesira_domain4_v2_core import python_core


CORE_STATUS_FOR_PHASE1 = {
    "VALID": "VALID_STRUCTURAL_ONLY",
    "INVALID": "INVALID",
    "RERUN_REQUIRED": "RERUN_REQUIRED",
    "NOT_EVALUATED": "NOT_EVALUATED",
    "TOOL_ERROR": "TOOL_ERROR",
}

PHASE1_STATUS_FOR_CORE = {value: key for key, value in CORE_STATUS_FOR_PHASE1.items()}
PHASE1_STATUS_FOR_CORE["VALID_STRUCTURAL_ONLY"] = "VALID"


@dataclass(frozen=True)
class Classification:
    artifact_kind: str
    execution_meta: str
    tuple: dict[str, str]
    reason_codes: list[str]
    phase1_result: dict[str, Any]

    @property
    def core_contract(self) -> dict[str, Any]:
        return python_core(self.artifact_kind, self.execution_meta, self.tuple)

    @property
    def phase1_contract_projection(self) -> dict[str, Any]:
        contract = self.core_contract
        return {
            "validation_status": PHASE1_STATUS_FOR_CORE[contract["status"]],
            "recommended_agent_action": contract["action"],
            "stop": contract["stop"],
        }


def default_tuple_for(artifact_kind: str) -> dict[str, str]:
    if artifact_kind == phase1.ARTIFACT_SEVERANCE:
        return {
            "schema": "SCHEMA_OK",
            "evidence": "EVIDENCE_NOT_APPLICABLE",
            "hash": "HASH_NOT_APPLICABLE",
            "path": "PATH_NOT_APPLICABLE",
            "symlink": "SYMLINK_NOT_APPLICABLE",
            "duplicate": "DUP_NOT_APPLICABLE",
            "directory": "DIR_NOT_APPLICABLE",
            "context": "CONTEXT_OK",
            "temporal": "TEMPORAL_OK",
        }
    if artifact_kind == phase1.ARTIFACT_ISOLATION:
        return {
            "schema": "SCHEMA_OK",
            "evidence": "EVIDENCE_OK",
            "hash": "HASH_OK",
            "path": "PATH_OK",
            "symlink": "SYMLINK_OK",
            "duplicate": "DUP_OK",
            "directory": "DIR_OK",
            "context": "CONTEXT_OK",
            "temporal": "TEMPORAL_NOT_APPLICABLE",
        }
    raise ValueError(f"unknown artifact kind: {artifact_kind}")


def classify_phase1_result(artifact_kind: str, result: Mapping[str, Any]) -> Classification:
    reason_codes = sorted(str(item) for item in result.get("reason_codes", []))
    tuple_ = default_tuple_for(artifact_kind)

    if result.get("validation_status") == "TOOL_ERROR":
        execution_meta = "TOOL_ERROR"
    elif "NESIRA_PHASE1_MALFORMED_JSON" in reason_codes:
        execution_meta = "INPUT_MALFORMED"
    else:
        execution_meta = "PARSED_OK"
        _apply_reason_codes(artifact_kind, tuple_, reason_codes)

    phase1_result = dict(result)
    return Classification(
        artifact_kind=artifact_kind,
        execution_meta=execution_meta,
        tuple=tuple_,
        reason_codes=reason_codes,
        phase1_result=phase1_result,
    )


def _apply_reason_codes(artifact_kind: str, tuple_: dict[str, str], reason_codes: list[str]) -> None:
    reasons = set(reason_codes)
    if artifact_kind == phase1.ARTIFACT_SEVERANCE:
        if reasons & {
            "NESIRA_PHASE1_MALFORMED_DSSE_ENVELOPE",
            "DSSE_PAYLOAD_TYPE_INVALID",
            "DSSE_PAYLOAD_MISSING",
            "DSSE_PAYLOAD_BASE64_INVALID",
            "DSSE_PAYLOAD_UTF8_INVALID",
            "DSSE_PAYLOAD_JSON_INVALID",
            "SEVERANCE_SCHEMA_VERSION_UNSUPPORTED",
        }:
            tuple_["schema"] = "SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION"
        elif "SEVERANCE_SCHEMA_INVALID" in reasons:
            tuple_["schema"] = "SCHEMA_STRUCTURAL_VIOLATION"

        if "SEVERANCE_EXPECTED_CONTEXT_MISSING" in reasons:
            tuple_["context"] = "CONTEXT_EXPECTED_MISSING"
        elif any(reason.startswith("SEVERANCE_") and reason.endswith("_MISMATCH") for reason in reasons):
            tuple_["context"] = "CONTEXT_MISMATCH"

        if reasons & {
            "SEVERANCE_TEMPORAL_BINDING_INVALID",
            "SEVERANCE_ISSUED_AT_IN_FUTURE",
            "SEVERANCE_EXPIRED",
        }:
            tuple_["temporal"] = "TEMPORAL_VIOLATION"
        return

    if artifact_kind != phase1.ARTIFACT_ISOLATION:
        raise ValueError(f"unknown artifact kind: {artifact_kind}")

    if reasons & {
        "LEGACY_ISOLATION_SCHEMA_VERSION_UNSUPPORTED",
        "LEGACY_ISOLATION_PROFILE_VERSION_UNSUPPORTED",
    }:
        tuple_["schema"] = "SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION"
    elif reasons & {
        "LEGACY_ISOLATION_RESULT_SCHEMA_INVALID",
        "LEGACY_ISOLATION_EVIDENCE_SCHEMA_INVALID",
    }:
        tuple_["schema"] = "SCHEMA_STRUCTURAL_VIOLATION"

    if "LEGACY_ISOLATION_EXPECTED_CONTEXT_MISSING" in reasons:
        tuple_["context"] = "CONTEXT_EXPECTED_MISSING"
    elif "LEGACY_ISOLATION_PROFILE_MISMATCH" in reasons or reasons.intersection(
        {
            "LEGACY_ISOLATION_PROFILE_ID_MISMATCH",
            "LEGACY_ISOLATION_ENVIRONMENT_ID_MISMATCH",
            "LEGACY_ISOLATION_CANDIDATE_SHA256_MISMATCH",
            "LEGACY_ISOLATION_LEGACY_DEPENDENCY_ID_MISMATCH",
        }
    ):
        tuple_["context"] = "CONTEXT_MISMATCH"

    if "LEGACY_ISOLATION_UNSAFE_EVIDENCE_PATH" in reasons:
        tuple_["path"] = "PATH_UNSAFE"
    if "LEGACY_ISOLATION_EVIDENCE_FILE_MISSING" in reasons:
        tuple_["evidence"] = "EVIDENCE_MISSING"
    if "LEGACY_ISOLATION_SYMLINK_ESCAPE" in reasons:
        tuple_["symlink"] = "SYMLINK_ESCAPE"
    if "LEGACY_ISOLATION_EVIDENCE_NOT_REGULAR_FILE" in reasons:
        tuple_["directory"] = "DIR_AS_FILE"
    if "LEGACY_ISOLATION_DUPLICATE_EVIDENCE_PATH" in reasons:
        tuple_["duplicate"] = "DUP_PRESENT"
    if "LEGACY_ISOLATION_EVIDENCE_HASH_MISMATCH" in reasons:
        tuple_["hash"] = "HASH_MISMATCH"


def classify_severance_fixture(
    repo_root: Path,
    fixture_name: str,
    *,
    expected_context: Mapping[str, Any],
    now_utc: datetime,
    as_bytes: bool = False,
) -> Classification:
    path = repo_root / "tests" / "fixtures" / "nesira_policy_profile" / "severance" / f"{fixture_name}.json"
    if as_bytes:
        result = phase1.validate_severance_authorization_bytes(
            path.read_bytes(),
            expected_context=expected_context,
            now_utc=now_utc,
        )
    else:
        result = phase1.validate_severance_authorization(
            json.loads(path.read_text(encoding="utf-8")),
            expected_context=expected_context,
            now_utc=now_utc,
        )
    return classify_phase1_result(phase1.ARTIFACT_SEVERANCE, result)


def classify_isolation_fixture(
    repo_root: Path,
    fixture_name: str,
    *,
    profile: Mapping[str, Any],
    evidence_root: Path,
    current_context: Mapping[str, Any],
    as_bytes: bool = False,
) -> Classification:
    path = repo_root / "tests" / "fixtures" / "nesira_policy_profile" / "isolation" / f"{fixture_name}.json"
    if as_bytes:
        result = phase1.validate_legacy_isolation_result_bytes(
            path.read_bytes(),
            profile=profile,
            evidence_root=evidence_root,
            current_context=current_context,
        )
    else:
        result = phase1.validate_legacy_isolation_result(
            json.loads(path.read_text(encoding="utf-8")),
            profile=profile,
            evidence_root=evidence_root,
            current_context=current_context,
        )
    return classify_phase1_result(phase1.ARTIFACT_ISOLATION, result)


def classify_tool_error(artifact_kind: str) -> Classification:
    if artifact_kind == phase1.ARTIFACT_SEVERANCE:
        not_claimed = phase1.SEVERANCE_NOT_CLAIMED
        scope = phase1.SCOPE_STRUCTURE_BINDING
    elif artifact_kind == phase1.ARTIFACT_ISOLATION:
        not_claimed = phase1.ISOLATION_NOT_CLAIMED
        scope = phase1.SCOPE_STRUCTURE_EVIDENCE
    else:
        raise ValueError(f"unknown artifact kind: {artifact_kind}")
    result = phase1._tool_error(artifact_kind, scope, "synthetic harness tool error", not_claimed)
    return classify_phase1_result(artifact_kind, result)
