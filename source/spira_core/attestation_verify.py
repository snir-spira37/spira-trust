from __future__ import annotations

import json
from json import JSONDecodeError
from hashlib import sha256
from pathlib import Path
from typing import Any, Iterable, Mapping


ATTESTATION_SCHEMA = "SPIRA_PEP740_OFFLINE_ATTESTATION_METADATA_V1"


def evaluate_attestations(
    artifacts: Iterable[Mapping[str, Any]],
    *,
    attestation_path: str | Path | None,
    trust_root_path: str | Path | None,
    trust_root_sha256: str | None = None,
) -> dict[str, Any]:
    """Evaluate a narrow offline attestation metadata subset.

    This is intentionally not a full Sigstore verifier. It checks that detached
    attestation records name a local artifact digest and that the declared
    identity is allowed by an explicit local trust root.
    """

    if not attestation_path:
        return {
            "schema": ATTESTATION_SCHEMA,
            "status": "ATTESTATION_NOT_EVALUATED",
            "evaluated": False,
            "findings": [],
            "not_claimed": _not_claimed(),
        }
    attestation_file = Path(attestation_path)
    if not attestation_file.is_file():
        return _input_error(
            "ATTESTATION_INPUT_ERROR",
            "attestation file does not exist",
            attestation_path=attestation_file,
            trust_root_path=trust_root_path,
        )
    trust_root: dict[str, Any] = {}
    trust_root_ref: dict[str, Any] | None = None
    trust_root_missing = not trust_root_path
    if trust_root_path:
        trust_root_file = Path(trust_root_path)
        if not trust_root_file.is_file():
            return _input_error(
                "ATTESTATION_TRUST_ROOT_MISSING",
                "attestation trust root file does not exist",
                attestation_path=attestation_file,
                trust_root_path=trust_root_file,
            )
        actual_root_sha = _hash_file(trust_root_file)
        if not trust_root_sha256:
            return {
                "schema": ATTESTATION_SCHEMA,
                "status": "ATTESTATION_TRUST_ROOT_SHA_MISSING",
                "evaluated": False,
                "findings": [],
                "attestation_path": str(attestation_file.resolve()),
                "trust_root_path": str(trust_root_file.resolve()),
                "actual_trust_root_sha256": actual_root_sha,
                "reason": "attestation trust root was supplied without --attestation-trust-root-sha256",
                "not_claimed": _not_claimed(),
            }
        if trust_root_sha256 and actual_root_sha.lower() != trust_root_sha256.lower():
            return {
                "schema": ATTESTATION_SCHEMA,
                "status": "ATTESTATION_TRUST_ROOT_UNTRUSTED",
                "evaluated": False,
                "findings": [],
                "attestation_path": str(Path(attestation_path).resolve()),
                "trust_root_path": str(Path(trust_root_path).resolve()),
                "expected_trust_root_sha256": trust_root_sha256,
                "actual_trust_root_sha256": actual_root_sha,
                "not_claimed": _not_claimed(),
            }
        try:
            trust_root = _load_json(trust_root_file)
        except (OSError, JSONDecodeError, ValueError) as error:
            return _input_error(
                "ATTESTATION_INPUT_ERROR",
                f"attestation trust root could not be read: {error}",
                attestation_path=attestation_file,
                trust_root_path=trust_root_file,
            )
        trust_root_ref = {
            "path": str(trust_root_file.resolve()),
            "sha256": actual_root_sha,
            "pinned": bool(trust_root_sha256),
        }
    try:
        bundle = _load_json(attestation_file)
    except (OSError, JSONDecodeError, ValueError) as error:
        return _input_error(
            "ATTESTATION_INPUT_ERROR",
            f"attestation file could not be read: {error}",
            attestation_path=attestation_file,
            trust_root_path=trust_root_path,
        )
    allowed = set(str(item) for item in trust_root.get("allowed_identities", []) or [])
    require_index_verified = bool(trust_root.get("require_index_verified", False))
    records = bundle.get("attestations", []) if isinstance(bundle, dict) else []
    if not isinstance(records, list):
        records = []
    by_filename = {Path(str(item.get("path") or "")).name: item for item in artifacts}
    findings: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            findings.append({"status": "CONTRADICTION", "reason": "attestation record is not an object"})
            continue
        filename = str(record.get("filename") or "")
        local = by_filename.get(filename)
        if not local:
            findings.append({"status": "UNVERIFIED", "filename": filename, "reason": "attestation references no provided local artifact"})
            continue
        expected = str(record.get("sha256") or record.get("subject", {}).get("sha256") or "")
        actual = str(local.get("sha256") or "")
        if expected != actual:
            findings.append({
                "status": "ATTESTATION_DIGEST_MISMATCH",
                "filename": filename,
                "reason": "attestation subject sha256 does not match local wheel sha256",
                "expected": expected,
                "actual": actual,
            })
            continue
        if trust_root_missing:
            findings.append({
                "status": "ATTESTATION_IDENTITY_NOT_EVALUATED",
                "filename": filename,
                "reason": "attestation digest matches local wheel but identity was not evaluated because trust root was not supplied",
            })
            continue
        identity = str(record.get("identity") or record.get("publisher") or "")
        if allowed and identity not in allowed:
            findings.append({"status": "ATTESTATION_IDENTITY_NOT_ALLOWED", "filename": filename, "reason": "attestation identity is not allowed by trust root", "identity": identity})
            continue
        if require_index_verified and record.get("index_verified") is not True:
            findings.append({"status": "ATTESTATION_INDEX_UNVERIFIED", "filename": filename, "reason": "trust root requires index_verified=true but record does not assert it"})
            continue
        findings.append({"status": "ATTESTATION_VERIFIED", "filename": filename, "identity": identity, "reason": "attestation metadata matches local artifact digest and trust root identity"})
    status_values = [item["status"] for item in findings]
    if "ATTESTATION_DIGEST_MISMATCH" in status_values:
        status = "ATTESTATION_DIGEST_MISMATCH"
    elif "ATTESTATION_IDENTITY_NOT_ALLOWED" in status_values:
        status = "ATTESTATION_IDENTITY_NOT_ALLOWED"
    elif "CONTRADICTION" in status_values:
        status = "ATTESTATION_CONTRADICTION"
    elif any(status in {"UNVERIFIED", "ATTESTATION_IDENTITY_NOT_EVALUATED", "ATTESTATION_INDEX_UNVERIFIED"} for status in status_values):
        status = "ATTESTATION_UNVERIFIED"
    elif findings:
        status = "ATTESTATION_VERIFIED"
    else:
        status = "ATTESTATION_UNVERIFIED"
    return {
        "schema": ATTESTATION_SCHEMA,
        "status": status,
        "evaluated": True,
        "attestation_path": str(attestation_file.resolve()),
        "attestation_sha256": _hash_file(attestation_file),
        "trust_root": trust_root_ref,
        "identity_evaluated": not trust_root_missing,
        "findings": findings,
        "not_claimed": _not_claimed(),
    }


def _load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    if not isinstance(data, dict):
        raise ValueError(f"expected JSON object: {path}")
    return data


def _hash_file(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def _input_error(
    status: str,
    reason: str,
    *,
    attestation_path: Path,
    trust_root_path: str | Path | None,
) -> dict[str, Any]:
    report: dict[str, Any] = {
        "schema": ATTESTATION_SCHEMA,
        "status": status,
        "evaluated": False,
        "findings": [],
        "attestation_path": str(attestation_path),
        "reason": reason,
        "not_claimed": _not_claimed(),
    }
    if trust_root_path:
        report["trust_root_path"] = str(trust_root_path)
    return report


def _not_claimed() -> list[str]:
    return [
        "does not perform full Sigstore cryptographic verification",
        "does not contact PyPI or any transparency log",
        "does not trust attestation contents without an explicit local trust root",
        "verifies local artifact digest and declared identity fields only for the supported V1 subset",
    ]
