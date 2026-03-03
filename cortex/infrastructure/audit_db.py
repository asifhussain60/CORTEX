"""
CortexAuditDB — SQLite WAL-mode unified audit database.

Provides centralized audit trail for all orchestrator operations.

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""
# noqa: CORE-035 — domain-scoped; class name appropriate for this module

import sqlite3
import json
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from enum import Enum
import logging


class EventType(Enum):
    """Types of audit events."""

    ORCHESTRATOR_START = "orchestrator_start"
    ORCHESTRATOR_END = "orchestrator_end"
    GOVERNANCE_CHECK = "governance_check"
    PHASE_COMPLETE = "phase_complete"
    ERROR_OCCURRED = "error_occurred"


# Phase 59-a: AuditEntry consolidated into cortex.core.audit_models (CORE-035)
from cortex.core.audit_models import AuditEntry  # noqa: F401 — re-export


class CortexAuditDB:
    """SQLite WAL-mode unified audit database."""

    def __init__(self, db_path: Union[str, Path] = Path(".cortex-runtime/audit.db")) -> None:
        """Initialize audit database.

        Args:
            db_path: Path to SQLite database file (str or Path).
        """
        self.db_path = Path(db_path) if isinstance(db_path, str) else db_path
        self.logger = logging.getLogger("cortex.audit")
        self._connection: Optional[sqlite3.Connection] = None
        self._initialize_db()

    def _initialize_db(self) -> None:
        """Initialize database with WAL mode and schema."""
        # Create parent directory if needed
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        conn = self._get_connection()
        cursor = conn.cursor()

        # Enable WAL mode for concurrent writes
        cursor.execute("PRAGMA journal_mode=WAL")

        # Create audit_events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                orchestrator_id TEXT NOT NULL,
                status TEXT NOT NULL,
                duration_ms INTEGER,
                error_message TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create orchestrator_traces table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orchestrator_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                orchestrator_id TEXT NOT NULL,
                phase_id TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                status TEXT,
                result_summary TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create governance_checks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS governance_checks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                rule_id TEXT NOT NULL,
                orchestrator_id TEXT NOT NULL,
                result TEXT,
                violation_details TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create phase_progress table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phase_progress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phase_id TEXT NOT NULL UNIQUE,
                status TEXT,
                started_at TEXT,
                completed_at TEXT,
                tests_passing INTEGER,
                tests_total INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_timestamp
            ON audit_events(timestamp)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_audit_orchestrator
            ON audit_events(orchestrator_id)
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_trace_orchestrator
            ON orchestrator_traces(orchestrator_id)
        """)

        conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """Get or create database connection.

        Returns:
            sqlite3.Connection: Active database connection.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self.db_path),
                timeout=30.0,
                check_same_thread=False,
            )
            # Enable foreign keys
            self._connection.execute("PRAGMA foreign_keys = ON")
        return self._connection

    def log_event(self, entry: AuditEntry) -> int:
        """Log an audit event.

        Args:
            entry: AuditEntry to log.

        Returns:
            Row ID of inserted event.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        metadata_json = json.dumps(entry.metadata) if entry.metadata else None

        cursor.execute("""
            INSERT INTO audit_events
            (timestamp, event_type, orchestrator_id, status, duration_ms, error_message, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            entry.timestamp.isoformat() if entry.timestamp else None,
            entry.event_type,
            entry.orchestrator_id,
            entry.status,
            entry.duration_ms,
            entry.error_message,
            metadata_json,
        ))

        conn.commit()
        return cursor.lastrowid

    def query_events(
        self,
        orchestrator_id: Optional[str] = None,
        event_type: Optional[str] = None,
        limit: int = 100,
    ) -> List[AuditEntry]:
        """Query audit events.

        Args:
            orchestrator_id: Filter by orchestrator ID.
            event_type: Filter by event type.
            limit: Maximum number of results.

        Returns:
            List of matching AuditEntry objects.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM audit_events WHERE 1=1"
        params = []

        if orchestrator_id:
            query += " AND orchestrator_id = ?"
            params.append(orchestrator_id)

        if event_type:
            query += " AND event_type = ?"
            params.append(event_type)

        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor.execute(query, params)
        results = cursor.fetchall()

        entries = []
        for row in results:
            entry = AuditEntry(
                entry_id=str(row[0]) if row[0] is not None else "",
                timestamp=datetime.fromisoformat(row[1]) if row[1] else None,
                operation=row[2],  # event_type → operation
                orchestrator_id=row[3],
                status=row[4],
                duration_ms=row[5],
                error_message=row[6],
                details=json.loads(row[7]) if row[7] else {},  # metadata → details
            )
            entries.append(entry)

        return entries

    def get_orchestrator_trace(self, orchestrator_id: str) -> List[Dict[str, Any]]:
        """Get execution trace for an orchestrator.

        Args:
            orchestrator_id: ID of orchestrator.

        Returns:
            List of trace entries.
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT orchestrator_id, phase_id, start_time, end_time, status, result_summary
            FROM orchestrator_traces
            WHERE orchestrator_id = ?
            ORDER BY start_time DESC
        """, (orchestrator_id,))

        results = cursor.fetchall()
        traces = []
        for row in results:
            traces.append({
                'orchestrator_id': row[0],
                'phase_id': row[1],
                'start_time': row[2],
                'end_time': row[3],
                'status': row[4],
                'result_summary': row[5],
            })

        return traces

    def close(self) -> None:
        """Close database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    def __del__(self) -> None:
        """Cleanup on deletion."""
        self.close()


# Singleton instance
_audit_db_instance: Optional[CortexAuditDB] = None


def get_audit_db(db_path: Optional[Path] = None) -> CortexAuditDB:
    """Get or create the singleton CortexAuditDB instance.

    Args:
        db_path: Optional path to database file.

    Returns:
        CortexAuditDB: The singleton instance.
    """
    global _audit_db_instance
    if _audit_db_instance is None:
        _audit_db_instance = CortexAuditDB(db_path or Path(".cortex-runtime/audit.db"))
    return _audit_db_instance
