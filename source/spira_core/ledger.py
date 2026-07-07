from __future__ import annotations

import json
from hashlib import sha256
from pathlib import Path
from typing import Any, Mapping

from .contracts import utc_now


def _hash_payload(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(encoded).hexdigest()


class SpiraCoreLedger:
    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.ledger_path = self.root / "spira_core_ledger.jsonl"

    def append(self, event: Mapping[str, Any]) -> dict[str, Any]:
        record = {
            "schema": "SPIRA_CORE_LEDGER_ENTRY_001",
            "created_at_utc": utc_now(),
            "previous_sha256": self.last_sha(),
            "event": dict(event),
        }
        record["entry_sha256"] = _hash_payload(record)
        with self.ledger_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        trace_id = str(event.get("trace_id", "unknown"))
        trace_dir = self.root / trace_id
        trace_dir.mkdir(parents=True, exist_ok=True)
        (trace_dir / "event.json").write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record

    def last_sha(self) -> str | None:
        if not self.ledger_path.is_file():
            return None
        last = None
        with self.ledger_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    last = json.loads(line)
        return last.get("entry_sha256") if last else None

    def read_trace(self, trace_id: str) -> dict[str, Any]:
        path = self.root / trace_id / "event.json"
        if not path.is_file():
            raise FileNotFoundError(f"SPIRA core trace not found: {trace_id}")
        return json.loads(path.read_text(encoding="utf-8"))
