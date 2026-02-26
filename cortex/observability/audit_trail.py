"""audit_trail.py — Audit Trail.

Records audit events to the runtime trace store. Supports both in-memory
(legacy) and SQLite-backed persistence (GAP-84-18). When `db_path` is
provided, events are written to a SQLite database and survive process restart.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations

import datetime
import logging
import sqlite3
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class AuditTrail:
    """Records audit events to the runtime trace store.

    When constructed with a `db_path`, events are persisted to SQLite and
    survive re-instantiation. Without `db_path`, falls back to in-memory
    storage for backward compatibility.
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialise AuditTrail.

        Args:
            db_path: Optional path to the SQLite database file. Parent
                     directories are created automatically. If None, uses
                     in-memory storage.
        """
        self._events: list[dict[str, Any]] = []
        self._db_path: Optional[Path] = Path(db_path) if db_path else None
        if self._db_path:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            self._init_db()

    def record(self, event: str, metadata: dict[str, Any] | None = None) -> None:
        """Record an audit event.

        Args:
            event: Event name or description.
            metadata: Optional event metadata.
        """
        entry: dict[str, Any] = {
            "event": event,
            "timestamp": datetime.datetime.utcnow().isoformat(),
            "metadata": metadata or {},
        }
        self._events.append(entry)
        if self._db_path:
            self._persist(entry)

    def events(self) -> list[dict[str, Any]]:
        """Return all recorded events (from SQLite if db_path set, else memory).

        Returns:
            List of event dicts with "event", "timestamp", and "metadata" keys.
        """
        if self._db_path:
            return self._load_from_db()
        return list(self._events)

    def _init_db(self) -> None:
        """Create the audit_events table if it does not already exist."""
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_events (
                        id        INTEGER PRIMARY KEY AUTOINCREMENT,
                        event     TEXT NOT NULL,
                        timestamp TEXT NOT NULL,
                        metadata  TEXT NOT NULL DEFAULT "{}"
                    )
                    """
                )
                conn.commit()
        except Exception as exc:
            logger.warning("AuditTrail: DB init failed — %s", exc)

    def _persist(self, entry: dict[str, Any]) -> None:
        """Persist a single event entry to SQLite."""
        import json
        try:
            with sqlite3.connect(self._db_path) as conn:
                conn.execute(
                    "INSERT INTO audit_events (event, timestamp, metadata) VALUES (?, ?, ?)",
                    (entry["event"], entry["timestamp"], json.dumps(entry.get("metadata", {})))
                )
                conn.commit()
        except Exception as exc:
            logger.warning("AuditTrail: persist failed — %s", exc)

    def _load_from_db(self) -> list[dict[str, Any]]:
        """Load all events from SQLite database."""
        import json
        results: list[dict[str, Any]] = []
        try:
            with sqlite3.connect(self._db_path) as conn:
                rows = conn.execute(
                    "SELECT event, timestamp, metadata FROM audit_events ORDER BY id"
                ).fetchall()
            for row in rows:
                results.append({
                    "event": row[0],
                    "timestamp": row[1],
                    "metadata": json.loads(row[2]) if row[2] else {},
                })
        except Exception as exc:
            logger.warning("AuditTrail: load failed — %s", exc)
        return results
