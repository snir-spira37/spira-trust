from __future__ import annotations

import json
import sqlite3
import threading
import time
from typing import Any, Dict, Optional
from pathlib import Path


def ensure_json_safe(value: Any, path: str = "root") -> Any:
    """Return a JSON-serializable copy of value or raise TypeError."""
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [ensure_json_safe(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, tuple):
        return [ensure_json_safe(v, f"{path}[{i}]") for i, v in enumerate(value)]
    if isinstance(value, dict):
        if not all(isinstance(k, str) for k in value):
            raise TypeError(f"{path} contains non-string dict key")
        return {k: ensure_json_safe(v, f"{path}.{k}") for k, v in value.items()}
    raise TypeError(f"{path} is not JSON serializable: {type(value).__name__}")


class SpiraMemoryDB:
    def __init__(self, path: str = "spira_memory.db", log_batch_size: int = 50, max_logs: Optional[int] = None) -> None:
        self.path = path
        self.log_batch_size = max(1, int(log_batch_size))
        self.max_logs = None if max_logs is None else max(1, int(max_logs))
        self.lock = threading.RLock()
        db_parent = Path(path).expanduser().resolve().parent
        db_parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.pending_logs = 0
        with self.lock:
            self.conn.execute("PRAGMA journal_mode=WAL")
            self.conn.execute("PRAGMA synchronous=NORMAL")
            self.conn.execute("PRAGMA busy_timeout=3000")
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS kv (key TEXT PRIMARY KEY, value_json TEXT NOT NULL, updated_at REAL NOT NULL)"
            )
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS states (label TEXT PRIMARY KEY, state_json TEXT NOT NULL, updated_at REAL NOT NULL)"
            )
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL NOT NULL, line TEXT NOT NULL)"
            )
            self.conn.execute(
                "CREATE TABLE IF NOT EXISTS bridge_sessions (session_id TEXT PRIMARY KEY, context_json TEXT NOT NULL, state_json TEXT, created_at REAL NOT NULL, last_activity REAL NOT NULL, status TEXT NOT NULL)"
            )
            self._migrate_bridge_sessions_table()
            self.conn.commit()
            cur = self.conn.execute("PRAGMA table_info(logs)")
            log_field = "ts"
            for info in cur.fetchall():
                if info[1] == "timestamp":
                    log_field = "timestamp"
                    break
                if info[1] == "ts":
                    log_field = "ts"
            self._log_timestamp_field = log_field
            self._logging_enabled = True


    def _migrate_bridge_sessions_table(self) -> None:
        cur = self.conn.execute("PRAGMA table_info(bridge_sessions)")
        cols = {row[1] for row in cur.fetchall()}
        if "state_json" not in cols:
            self.conn.execute("ALTER TABLE bridge_sessions ADD COLUMN state_json TEXT")

    def flush(self) -> None:
        with self.lock:
            if self.max_logs is not None:
                self._prune_logs()
            self.conn.commit()
            self.pending_logs = 0

    def close(self) -> None:
        with self.lock:
            self.flush()
            self.conn.close()

    def put(self, key: str, value: Any) -> None:
        payload = json.dumps(ensure_json_safe(value, path=f"kv[{key}]"), ensure_ascii=False)
        with self.lock:
            self.conn.execute(
                "INSERT INTO kv(key, value_json, updated_at) VALUES(?,?,?) ON CONFLICT(key) DO UPDATE SET value_json=excluded.value_json, updated_at=excluded.updated_at",
                (key, payload, time.time()),
            )
            self.conn.commit()

    def get(self, key: str) -> Any:
        with self.lock:
            cur = self.conn.execute("SELECT value_json FROM kv WHERE key=?", (key,))
            row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def save_state(self, label: str, state: Dict[str, Any]) -> None:
        payload = json.dumps(ensure_json_safe(state, path=f"state[{label}]"), ensure_ascii=False)
        with self.lock:
            self.conn.execute(
                "INSERT INTO states(label, state_json, updated_at) VALUES(?,?,?) ON CONFLICT(label) DO UPDATE SET state_json=excluded.state_json, updated_at=excluded.updated_at",
                (label, payload, time.time()),
            )
            self.conn.commit()

    def load_state(self, label: str) -> Optional[Dict[str, Any]]:
        with self.lock:
            cur = self.conn.execute("SELECT state_json FROM states WHERE label=?", (label,))
            row = cur.fetchone()
        return json.loads(row[0]) if row else None

    def log(self, line: str) -> None:
        if not self._logging_enabled:
            return
        with self.lock:
            field = self._log_timestamp_field
            self.conn.execute(f"INSERT INTO logs({field}, line) VALUES(?, ?)", (time.time(), line))
            self.pending_logs += 1
            if self.pending_logs >= self.log_batch_size:
                if self.max_logs is not None:
                    self._prune_logs()
                self.conn.commit()
                self.pending_logs = 0

    def _prune_logs(self) -> None:
        if self.max_logs is None:
            return
        cur = self.conn.execute("SELECT id FROM logs ORDER BY id DESC LIMIT 1 OFFSET ?", (self.max_logs,))
        row = cur.fetchone()
        if row:
            self.conn.execute("DELETE FROM logs WHERE id <= ?", (int(row[0]),))

    def save_bridge_session(self, session_id: str, context: Dict[str, Any], created_at: float, last_activity: float, status: str = "active", state: Optional[Dict[str, Any]] = None) -> None:
        payload = json.dumps(ensure_json_safe(context, path=f"bridge_session[{session_id}]"), ensure_ascii=False)
        state_payload = None if state is None else json.dumps(ensure_json_safe(state, path=f"bridge_session_state[{session_id}]"), ensure_ascii=False)
        with self.lock:
            self.conn.execute(
                "INSERT INTO bridge_sessions(session_id, context_json, state_json, created_at, last_activity, status) VALUES(?,?,?,?,?,?) "
                "ON CONFLICT(session_id) DO UPDATE SET context_json=excluded.context_json, state_json=excluded.state_json, last_activity=excluded.last_activity, status=excluded.status",
                (session_id, payload, state_payload, created_at, last_activity, status),
            )
            self.conn.commit()

    def touch_bridge_session(self, session_id: str, last_activity: float) -> None:
        with self.lock:
            self.conn.execute("UPDATE bridge_sessions SET last_activity=? WHERE session_id=?", (last_activity, session_id))
            self.conn.commit()

    def delete_bridge_session(self, session_id: str) -> None:
        with self.lock:
            self.conn.execute("DELETE FROM bridge_sessions WHERE session_id=?", (session_id,))
            self.conn.commit()

    def count_bridge_sessions(self) -> int:
        with self.lock:
            cur = self.conn.execute("SELECT COUNT(*) FROM bridge_sessions")
            row = cur.fetchone()
        return int(row[0]) if row else 0

    def list_bridge_session_ids(self) -> list[str]:
        with self.lock:
            cur = self.conn.execute("SELECT session_id FROM bridge_sessions ORDER BY created_at ASC")
            rows = cur.fetchall()
        return [str(row[0]) for row in rows]

    def list_bridge_session_summaries(self) -> list[dict[str, Any]]:
        with self.lock:
            cur = self.conn.execute(
                "SELECT session_id, created_at, last_activity, status FROM bridge_sessions ORDER BY created_at ASC"
            )
            rows = cur.fetchall()
        return [
            {
                "session_id": sid,
                "created_at": created_at,
                "last_activity": last_activity,
                "status": status,
            }
            for sid, created_at, last_activity, status in rows
        ]

    def list_bridge_sessions(self) -> list[dict[str, Any]]:
        with self.lock:
            cur = self.conn.execute(
                "SELECT session_id, context_json, state_json, created_at, last_activity, status FROM bridge_sessions ORDER BY created_at ASC"
            )
            rows = cur.fetchall()
        out = []
        for sid, context_json, state_json, created_at, last_activity, status in rows:
            out.append(
                {
                    "session_id": sid,
                    "context": json.loads(context_json),
                    "state": json.loads(state_json) if state_json else None,
                    "created_at": created_at,
                    "last_activity": last_activity,
                    "status": status,
                }
            )
        return out

    def get_bridge_session(self, session_id: str) -> Optional[dict[str, Any]]:
        with self.lock:
            cur = self.conn.execute(
                "SELECT session_id, context_json, state_json, created_at, last_activity, status FROM bridge_sessions WHERE session_id=?",
                (session_id,),
            )
            row = cur.fetchone()
        if not row:
            return None
        sid, context_json, state_json, created_at, last_activity, status = row
        return {
            "session_id": sid,
            "context": json.loads(context_json),
            "state": json.loads(state_json) if state_json else None,
            "created_at": created_at,
            "last_activity": last_activity,
            "status": status,
        }
