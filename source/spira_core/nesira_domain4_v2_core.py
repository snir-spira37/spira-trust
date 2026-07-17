from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from dataclasses import dataclass
from itertools import product
from pathlib import Path
from typing import Any, Iterable, Mapping


ARTIFACT_KINDS = ("SEVERANCE_AUTHORIZATION", "LEGACY_ISOLATION_RESULT")
EXECUTION_META = ("PARSED_OK", "INPUT_MALFORMED", "TOOL_ERROR")

SCHEMA_OUTCOMES = (
    "SCHEMA_OK",
    "SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION",
    "SCHEMA_STRUCTURAL_VIOLATION",
)
EVIDENCE_OUTCOMES = ("EVIDENCE_OK", "EVIDENCE_MISSING", "EVIDENCE_NOT_APPLICABLE")
HASH_OUTCOMES = ("HASH_OK", "HASH_MISMATCH", "HASH_NOT_APPLICABLE")
PATH_OUTCOMES = ("PATH_OK", "PATH_UNSAFE", "PATH_NOT_APPLICABLE")
SYMLINK_OUTCOMES = ("SYMLINK_OK", "SYMLINK_ESCAPE", "SYMLINK_NOT_APPLICABLE")
DUPLICATE_OUTCOMES = ("DUP_OK", "DUP_PRESENT", "DUP_NOT_APPLICABLE")
DIRECTORY_OUTCOMES = ("DIR_OK", "DIR_AS_FILE", "DIR_NOT_APPLICABLE")
CONTEXT_OUTCOMES = ("CONTEXT_OK", "CONTEXT_EXPECTED_MISSING", "CONTEXT_MISMATCH")
TEMPORAL_OUTCOMES = ("TEMPORAL_OK", "TEMPORAL_VIOLATION", "TEMPORAL_NOT_APPLICABLE")

OUTCOME_FIELDS = (
    "schema",
    "evidence",
    "hash",
    "path",
    "symlink",
    "duplicate",
    "directory",
    "context",
    "temporal",
)

OUTCOME_DOMAINS = (
    SCHEMA_OUTCOMES,
    EVIDENCE_OUTCOMES,
    HASH_OUTCOMES,
    PATH_OUTCOMES,
    SYMLINK_OUTCOMES,
    DUPLICATE_OUTCOMES,
    DIRECTORY_OUTCOMES,
    CONTEXT_OUTCOMES,
    TEMPORAL_OUTCOMES,
)

EXPECTED_CORE_SPACE_SIZE = 118_098


@dataclass(frozen=True)
class MachineContract:
    status: str
    action: str
    stop: bool = True

    def as_dict(self) -> dict[str, Any]:
        return {"action": self.action, "status": self.status, "stop": self.stop}


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def action_of(status: str) -> str:
    if status == "VALID_STRUCTURAL_ONLY":
        return "REPORT_NOT_EVALUATED"
    if status == "INVALID":
        return "STOP_BLOCKED"
    if status == "RERUN_REQUIRED":
        return "RERUN_REQUIRED"
    if status == "NOT_EVALUATED":
        return "REPORT_NOT_EVALUATED"
    if status == "TOOL_ERROR":
        return "STOP_BLOCKED"
    raise ValueError(f"unknown validation status: {status}")


def contract_of(status: str) -> MachineContract:
    return MachineContract(status=status, action=action_of(status), stop=True)


def severance_status(tuple_: Mapping[str, str]) -> str:
    schema = tuple_["schema"]
    if schema == "SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION":
        return "RERUN_REQUIRED"
    if schema == "SCHEMA_STRUCTURAL_VIOLATION":
        return "INVALID"
    if schema != "SCHEMA_OK":
        raise ValueError(f"unknown schema outcome: {schema}")

    context = tuple_["context"]
    if context == "CONTEXT_EXPECTED_MISSING":
        return "NOT_EVALUATED"
    if context == "CONTEXT_MISMATCH":
        return "RERUN_REQUIRED"
    if context != "CONTEXT_OK":
        raise ValueError(f"unknown context outcome: {context}")

    temporal = tuple_["temporal"]
    if temporal == "TEMPORAL_VIOLATION":
        return "RERUN_REQUIRED"
    if temporal in ("TEMPORAL_OK", "TEMPORAL_NOT_APPLICABLE"):
        return "VALID_STRUCTURAL_ONLY"
    raise ValueError(f"unknown temporal outcome: {temporal}")


def isolation_status(tuple_: Mapping[str, str]) -> str:
    schema = tuple_["schema"]
    if schema == "SCHEMA_STRUCTURAL_VIOLATION":
        return "INVALID"
    if schema == "SCHEMA_MALFORMED_OR_UNSUPPORTED_VERSION":
        return "RERUN_REQUIRED"
    if schema != "SCHEMA_OK":
        raise ValueError(f"unknown schema outcome: {schema}")

    context = tuple_["context"]
    if context == "CONTEXT_MISMATCH":
        return "RERUN_REQUIRED"
    if context == "CONTEXT_EXPECTED_MISSING":
        return "NOT_EVALUATED"
    if context != "CONTEXT_OK":
        raise ValueError(f"unknown context outcome: {context}")

    path = tuple_["path"]
    if path == "PATH_UNSAFE":
        return "INVALID"
    if path not in ("PATH_OK", "PATH_NOT_APPLICABLE"):
        raise ValueError(f"unknown path outcome: {path}")

    evidence = tuple_["evidence"]
    if evidence == "EVIDENCE_MISSING":
        return "NOT_EVALUATED"
    if evidence not in ("EVIDENCE_OK", "EVIDENCE_NOT_APPLICABLE"):
        raise ValueError(f"unknown evidence outcome: {evidence}")

    symlink = tuple_["symlink"]
    if symlink == "SYMLINK_ESCAPE":
        return "INVALID"
    if symlink not in ("SYMLINK_OK", "SYMLINK_NOT_APPLICABLE"):
        raise ValueError(f"unknown symlink outcome: {symlink}")

    directory = tuple_["directory"]
    if directory == "DIR_AS_FILE":
        return "INVALID"
    if directory not in ("DIR_OK", "DIR_NOT_APPLICABLE"):
        raise ValueError(f"unknown directory outcome: {directory}")

    duplicate = tuple_["duplicate"]
    if duplicate == "DUP_PRESENT":
        return "INVALID"
    if duplicate not in ("DUP_OK", "DUP_NOT_APPLICABLE"):
        raise ValueError(f"unknown duplicate outcome: {duplicate}")

    hash_ = tuple_["hash"]
    if hash_ == "HASH_MISMATCH":
        return "INVALID"
    if hash_ in ("HASH_OK", "HASH_NOT_APPLICABLE"):
        return "VALID_STRUCTURAL_ONLY"
    raise ValueError(f"unknown hash outcome: {hash_}")


def python_core(artifact_kind: str, execution_meta: str, tuple_: Mapping[str, str]) -> dict[str, Any]:
    if artifact_kind not in ARTIFACT_KINDS:
        raise ValueError(f"unknown artifact kind: {artifact_kind}")
    if execution_meta == "TOOL_ERROR":
        return contract_of("TOOL_ERROR").as_dict()
    if execution_meta == "INPUT_MALFORMED":
        return contract_of("RERUN_REQUIRED").as_dict()
    if execution_meta != "PARSED_OK":
        raise ValueError(f"unknown execution meta: {execution_meta}")
    missing = [field for field in OUTCOME_FIELDS if field not in tuple_]
    if missing:
        raise ValueError(f"missing outcome fields: {missing}")
    if artifact_kind == "SEVERANCE_AUTHORIZATION":
        return contract_of(severance_status(tuple_)).as_dict()
    return contract_of(isolation_status(tuple_)).as_dict()


def all_outcome_tuples() -> Iterable[dict[str, str]]:
    for values in product(*OUTCOME_DOMAINS):
        yield dict(zip(OUTCOME_FIELDS, values, strict=True))


def all_core_inputs() -> Iterable[dict[str, Any]]:
    for artifact_kind in ARTIFACT_KINDS:
        for execution_meta in EXECUTION_META:
            for tuple_ in all_outcome_tuples():
                yield {
                    "artifact_kind": artifact_kind,
                    "execution_meta": execution_meta,
                    "tuple": tuple_,
                }


def python_dump_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for item in all_core_inputs():
        records.append(
            {
                **item,
                "contract": python_core(
                    item["artifact_kind"],
                    item["execution_meta"],
                    item["tuple"],
                ),
            }
        )
    return records


def find_lake_executable() -> str:
    found = shutil.which("lake")
    if found:
        return found
    local = Path.home() / ".local" / "lean" / "lean-4.32.0-windows" / "bin" / "lake.exe"
    if local.exists():
        return str(local)
    raise RuntimeError("lake executable not found")


def run_lean_dump(repo_root: Path, *, lake_exe: str | None = None) -> list[dict[str, Any]]:
    formal_root = repo_root / "formal" / "spira_formal_core_v1"
    if not formal_root.exists():
        raise FileNotFoundError(f"formal root not found: {formal_root}")
    lake = lake_exe or find_lake_executable()
    subprocess.run(
        [lake, "build", "SpiraFormalCoreDomain4"],
        cwd=formal_root,
        check=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    with tempfile.NamedTemporaryFile("w", suffix=".lean", delete=False, encoding="utf-8") as handle:
        temp_path = Path(handle.name)
        handle.write("import SpiraFormalCore.Domain4.Main\n\n")
        handle.write("def main : IO Unit := SpiraFormalCore.Domain4.main\n")
    try:
        completed = subprocess.run(
            [lake, "env", "lean", "--run", str(temp_path)],
            cwd=formal_root,
            check=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    finally:
        temp_path.unlink(missing_ok=True)
    records = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
    return records


def compare_python_to_lean_dump(repo_root: Path, *, lake_exe: str | None = None) -> dict[str, Any]:
    python_records = python_dump_records()
    lean_records = run_lean_dump(repo_root, lake_exe=lake_exe)
    if len(python_records) != EXPECTED_CORE_SPACE_SIZE:
        raise AssertionError(f"unexpected Python core space size: {len(python_records)}")
    if len(lean_records) != EXPECTED_CORE_SPACE_SIZE:
        raise AssertionError(f"unexpected Lean dump size: {len(lean_records)}")

    disagreements: list[dict[str, Any]] = []
    for index, (python_record, lean_record) in enumerate(zip(python_records, lean_records, strict=True)):
        if canonical_json(python_record) != canonical_json(lean_record):
            disagreements.append(
                {
                    "index": index,
                    "python": python_record,
                    "lean": lean_record,
                }
            )
            if len(disagreements) >= 10:
                break

    return {
        "core_agreement_total_tuples": EXPECTED_CORE_SPACE_SIZE,
        "python_record_count": len(python_records),
        "lean_record_count": len(lean_records),
        "core_agreement_disagreements": len(disagreements),
        "sample_disagreements": disagreements,
    }
