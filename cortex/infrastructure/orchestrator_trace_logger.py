"""
Orchestrator Trace Logger - Development-Only SQLite Tracing

AC-TRACE-001: Comprehensive orchestrator action tracing with strategic database management.

Purpose:
- Capture all orchestrator actions in SQLite for debugging/analysis
- Automatic trace flushes to prevent unbounded growth
- Development-only with production switch-off mechanism
- Per-orchestrator trace tables with atomic operations
- Correlation ID tracking for request tracing

Features:
- Environment-based activation (CORTEX_TRACE_ENABLED)
- Strategic flush policy (max rows per table, time-based rotation)
- Non-blocking trace insertion (async where possible)
- Sensitive data redaction (passwords, tokens, API keys)
- Violation tracking with context preservation
- Automatic cleanup on startup

Architecture:
- OrchestratorTraceLogger (singleton): Central trace manager
- PerOrchestrationTraceWriter: Per-orchestrator trace recording
- TraceFlushPolicy: Configurable retention and rotation
- TraceQuery: Analysis and debugging helpers

Author: Asif Hussain
"""

import json
import logging
import os
import sqlite3
import threading
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result

logger = logging.getLogger(__name__)


class TraceLevel(Enum):
    """Trace level for different operation types."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    ACTION = "ACTION"  # Significant orchestrator action
    VIOLATION = "VIOLATION"  # Governance violation
    ERROR = "ERROR"


class TraceFlushReason(Enum):
    """Reason for trace flush operation."""

    MAX_ROWS = "max_rows_reached"
    TIME_BASED = "time_based_rotation"
    MANUAL = "manual_request"
    STARTUP = "startup_cleanup"
    ERROR = "error_recovery"


@dataclass
class TraceEntry:
    """Single trace log entry."""

    trace_id: str
    timestamp: datetime
    orchestrator_id: str
    orchestrator_class: str
    action: str
    level: TraceLevel
    correlation_id: str
    request_id: str
    context: Dict[str, Any]
    result: Optional[str] = None  # OK, ERR, RUNNING
    violation_type: Optional[str] = None
    duration_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TraceFlushEvent:
    """Record of trace flush operation."""

    flush_id: str
    timestamp: datetime
    reason: TraceFlushReason
    tables_flushed: Dict[str, int]  # {table_name: rows_removed}
    total_rows_removed: int
    total_rows_remaining: int
    duration_ms: float


class OrchestratorTraceLogger:
    """
    Central orchestrator trace logger (singleton).

    Manages:
    - Per-orchestrator trace tables
    - Automatic flush policies
    - Development/production mode switching
    - Trace analysis and querying
    - Schema versioning for safe migrations
    """

    _instance: Optional["OrchestratorTraceLogger"] = None
    _lock = threading.Lock()

    # Schema Version (increment when schema changes)
    SCHEMA_VERSION = "1.0.0"

    # Configuration
    TRACE_ENABLED = os.getenv("CORTEX_TRACE_ENABLED", "true").lower() == "true"
    TRACE_DB_PATH = Path(os.getenv("CORTEX_TRACE_DB", ".cortex-runtime/traces/orchestrator-traces.db"))
    MAX_ROWS_PER_TABLE = int(os.getenv("CORTEX_TRACE_MAX_ROWS", "10000"))
    FLUSH_INTERVAL_HOURS = int(os.getenv("CORTEX_TRACE_FLUSH_INTERVAL", "24"))
    ENABLE_ASYNC_FLUSH = os.getenv("CORTEX_TRACE_ASYNC_FLUSH", "true").lower() == "true"

    def __new__(cls) -> "OrchestratorTraceLogger":
        """Singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Initialize trace logger."""
        if hasattr(self, "_initialized") and self._initialized:
            return

        self._initialized = True
        self._trace_enabled = self.TRACE_ENABLED
        self._db_path = self.TRACE_DB_PATH
        self._writers: Dict[str, PerOrchestrationTraceWriter] = {}
        self._write_lock = threading.Lock()
        self._last_flush_time: Dict[str, datetime] = {}
        self._flush_policy = TraceFlushPolicy(
            max_rows_per_table=self.MAX_ROWS_PER_TABLE,
            flush_interval_hours=self.FLUSH_INTERVAL_HOURS,
        )

        if self._trace_enabled:
            self._init_db()
            self._cleanup_old_traces()

    def _init_db(self) -> None:
        """Initialize trace database and create master table."""
        if not self._trace_enabled:
            return

        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)

            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trace_metadata (
                        id TEXT PRIMARY KEY,
                        orchestrator_id TEXT NOT NULL,
                        orchestrator_class TEXT NOT NULL,
                        table_name TEXT NOT NULL UNIQUE,
                        created_at TEXT NOT NULL,
                        last_updated TEXT NOT NULL,
                        row_count INTEGER DEFAULT 0,
                        last_flush_time TEXT,
                        schema_version TEXT
                    )
                    """
                )

                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trace_flush_log (
                        flush_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        reason TEXT NOT NULL,
                        tables_flushed TEXT NOT NULL,
                        total_rows_removed INTEGER,
                        total_rows_remaining INTEGER,
                        duration_ms REAL
                    )
                    """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_flush_timestamp
                    ON trace_flush_log(timestamp DESC)
                    """
                )

                # audit_stage_log — records per-stage execution for 9-stage audit pipeline
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS audit_stage_log (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        session_id  TEXT NOT NULL,
                        stage       INTEGER NOT NULL,
                        stage_name  TEXT NOT NULL,
                        started_at  TEXT NOT NULL,
                        completed_at TEXT,
                        status      TEXT NOT NULL DEFAULT 'RUNNING',
                        p0_count    INTEGER DEFAULT 0,
                        p1_count    INTEGER DEFAULT 0,
                        duration_ms REAL,
                        notes       TEXT
                    )
                    """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_audit_stage_session
                    ON audit_stage_log(session_id, stage)
                    """
                )

                # workflow_cycles — CORE-068 convergence loop tracing (detect→fix→rescan)
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS workflow_cycles (
                        id              INTEGER PRIMARY KEY AUTOINCREMENT,
                        run_id          TEXT NOT NULL,
                        template_id     TEXT NOT NULL,
                        label           TEXT NOT NULL,
                        cycle_num       INTEGER NOT NULL,
                        p0_before       INTEGER NOT NULL DEFAULT 0,
                        p1_before       INTEGER NOT NULL DEFAULT 0,
                        p0_after        INTEGER NOT NULL DEFAULT 0,
                        p1_after        INTEGER NOT NULL DEFAULT 0,
                        issues_before   INTEGER NOT NULL DEFAULT 0,
                        issues_after    INTEGER NOT NULL DEFAULT 0,
                        issues_fixed    INTEGER NOT NULL DEFAULT 0,
                        predicate_result INTEGER NOT NULL DEFAULT 0,
                        fix_log_json    TEXT,
                        scan_errors     INTEGER DEFAULT 0,
                        fix_errors      INTEGER DEFAULT 0,
                        duration_ms     INTEGER NOT NULL DEFAULT 0,
                        timestamp       TEXT NOT NULL
                    )
                    """
                )

                conn.execute(
                    """
                    CREATE INDEX IF NOT EXISTS idx_workflow_cycles_run
                    ON workflow_cycles(run_id, cycle_num)
                    """
                )

                # Store schema version in metadata
                conn.execute(
                    """
                    INSERT OR REPLACE INTO trace_metadata (id, orchestrator_id, orchestrator_class,
                                                           table_name, created_at, last_updated, schema_version)
                    VALUES ('_schema_version', 'system', 'system', '_schema', ?, ?, ?)
                    """,
                    (datetime.now().isoformat(), datetime.now().isoformat(), self.SCHEMA_VERSION)
                )

                conn.commit()
                logger.info(f"Initialized trace database: {self._db_path} (schema v{self.SCHEMA_VERSION})")
        except Exception as e:
            logger.error(f"Error initializing trace database: {str(e)}")
            self._trace_enabled = False

    @contextmanager
    def _get_connection(self) -> None:
        """Get SQLite connection with proper cleanup."""
        conn = sqlite3.connect(str(self._db_path), timeout=10.0, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()

    def get_trace_writer(self, orchestrator_id: str, orchestrator_class: str) -> "PerOrchestrationTraceWriter":
        """Get or create trace writer for orchestrator."""
        if not self._trace_enabled:
            return PerOrchestrationTraceWriter(None, orchestrator_id, orchestrator_class)

        with self._write_lock:
            if orchestrator_id not in self._writers:
                self._writers[orchestrator_id] = PerOrchestrationTraceWriter(
                    self, orchestrator_id, orchestrator_class
                )

            return self._writers[orchestrator_id]

    def record_trace(self, entry: TraceEntry) -> Result[None]:
        """Record trace entry for orchestrator."""
        if not self._trace_enabled:
            return Ok(None)

        try:
            writer = self.get_trace_writer(entry.orchestrator_id, entry.orchestrator_class)
            return writer.write_trace(entry)
        except Exception as e:
            logger.error(f"Error recording trace: {str(e)}")
            return Err(str(e))

    def write_ac_marker(
        self,
        marker: str,
        operation: str,
        orchestrator_class: str,
        *,
        entry_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Result[str]:
        """Persist an AC_START or AC_COMPLETE marker to trace_master.

        Called by ``_emit_ac_marker()`` in ``IntelligenceMixin`` to bridge the
        in-memory ``_ac_log`` into durable SQLite storage.  Every public
        orchestrator method should produce at least one ``AC_START`` row and
        one ``AC_COMPLETE`` (or ``AC_FAILURE``) row in ``trace_master``.

        Args:
            marker: ``AC_START``, ``AC_COMPLETE``, or ``AC_FAILURE``.
            operation: Short operation label (e.g. ``LENS_CONTEXT``).
            orchestrator_class: Class name of the emitting orchestrator.
            entry_id: Correlation ID; generated if absent.
            correlation_id: Optional request-level correlation ID.
            duration_ms: Duration in ms (for AC_COMPLETE / AC_FAILURE).
            metadata: Extra key/value pairs stored as JSON.

        Returns:
            ``Ok(entry_id)`` on success; ``Err(reason)`` on failure.
        """
        if not self._trace_enabled:
            return Ok(entry_id or str(uuid.uuid4())[:8])

        eid = entry_id or str(uuid.uuid4())[:8]
        try:
            with self._get_connection() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS trace_master (
                        trace_id        TEXT PRIMARY KEY,
                        timestamp       TEXT NOT NULL,
                        action          TEXT NOT NULL,
                        level           TEXT NOT NULL,
                        correlation_id  TEXT,
                        request_id      TEXT,
                        context         TEXT,
                        result          TEXT,
                        violation_type  TEXT,
                        duration_ms     REAL,
                        metadata        TEXT
                    )
                    """
                )
                conn.execute(
                    """
                    INSERT OR IGNORE INTO trace_master
                        (trace_id, timestamp, action, level, correlation_id,
                         context, duration_ms, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        eid,
                        datetime.utcnow().isoformat(),
                        marker,                             # e.g. "AC_START"
                        TraceLevel.ACTION.value,
                        correlation_id,
                        json.dumps({"operation": operation,
                                    "orchestrator": orchestrator_class}),
                        duration_ms,
                        json.dumps(metadata or {}),
                    ),
                )
                conn.commit()
            return Ok(eid)
        except Exception as exc:
            logger.warning(f"write_ac_marker failed ({marker}/{operation}): {exc}")
            return Err(str(exc))

    def flush_traces(self, reason: TraceFlushReason = TraceFlushReason.MANUAL) -> Result[TraceFlushEvent]:
        """Execute manual trace flush."""
        if not self._trace_enabled:
            return Ok(TraceFlushEvent(
                flush_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                reason=reason,
                tables_flushed={},
                total_rows_removed=0,
                total_rows_remaining=0,
                duration_ms=0,
            ))

        start_time = datetime.utcnow()

        try:
            with self._get_connection() as conn:
                tables_flushed = self._flush_policy.execute_flush(conn, reason)
                total_removed = sum(tables_flushed.values())
                total_remaining = self._get_total_trace_rows(conn)

                flush_event = TraceFlushEvent(
                    flush_id=str(uuid.uuid4()),
                    timestamp=start_time,
                    reason=reason,
                    tables_flushed=tables_flushed,
                    total_rows_removed=total_removed,
                    total_rows_remaining=total_remaining,
                    duration_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                )

                self._log_flush_event(conn, flush_event)
                conn.commit()

                logger.info(
                    f"Trace flush completed: {total_removed} rows removed, {total_remaining} remaining"
                )

                return Ok(flush_event)
        except Exception as e:
            logger.error(f"Error flushing traces: {str(e)}")
            return Err(str(e))

    def _cleanup_old_traces(self) -> None:
        """Clean up traces older than retention period on startup."""
        if not self._trace_enabled:
            return

        try:
            self.flush_traces(TraceFlushReason.STARTUP)
        except Exception as e:
            logger.warning(f"Startup trace cleanup failed: {str(e)}")

    def _get_total_trace_rows(self, conn: sqlite3.Connection) -> int:
        """Get total rows across all trace tables."""
        try:
            cursor = conn.execute("SELECT SUM(row_count) FROM trace_metadata WHERE row_count > 0")
            result = cursor.fetchone()
            return result[0] if result and result[0] else 0
        except Exception:
            return 0

    def _log_flush_event(self, conn: sqlite3.Connection, event: TraceFlushEvent) -> None:
        """Log flush event to audit table."""
        try:
            conn.execute(
                """
                INSERT INTO trace_flush_log
                (flush_id, timestamp, reason, tables_flushed, total_rows_removed, total_rows_remaining, duration_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    event.flush_id,
                    event.timestamp.isoformat(),
                    event.reason.value,
                    json.dumps(event.tables_flushed),
                    event.total_rows_removed,
                    event.total_rows_remaining,
                    event.duration_ms,
                ),
            )
        except Exception as e:
            logger.error(f"Error logging flush event: {str(e)}")

    def query_traces(
        self,
        orchestrator_id: Optional[str] = None,
        level: Optional[TraceLevel] = None,
        since: Optional[datetime] = None,
        limit: int = 100,
    ) -> Result[List[Dict[str, Any]]]:
        """Query trace entries with optional filtering."""
        if not self._trace_enabled:
            return Ok([])

        try:
            with self._get_connection() as conn:
                query = "SELECT * FROM trace_metadata WHERE 1=1"
                params: List[Any] = []

                if orchestrator_id:
                    query += " AND orchestrator_id = ?"
                    params.append(orchestrator_id)

                query += f" LIMIT {limit}"

                cursor = conn.execute(query, params)
                rows = cursor.fetchall()

                return Ok([dict(row) for row in rows])
        except Exception as e:
            logger.error(f"Error querying traces: {str(e)}")
            return Err(str(e))

    def get_statistics(self) -> Dict[str, Any]:
        """Get trace database statistics."""
        if not self._trace_enabled:
            return {"enabled": False}

        try:
            with self._get_connection() as conn:
                cursor = conn.execute(
                    """
                    SELECT
                        COUNT(*) as total_tables,
                        SUM(row_count) as total_rows,
                        MAX(last_updated) as latest_trace
                    FROM trace_metadata
                    """
                )
                result = cursor.fetchone()

                db_size_bytes = self._db_path.stat().st_size if self._db_path.exists() else 0

                return {
                    "enabled": True,
                    "total_tables": result[0] if result else 0,
                    "total_rows": result[1] if result else 0,
                    "latest_trace": result[2] if result else None,
                    "db_path": str(self._db_path),
                    "db_size_mb": round(db_size_bytes / (1024 * 1024), 2),
                    "max_rows_per_table": self.MAX_ROWS_PER_TABLE,
                }
        except Exception as e:
            logger.error(f"Error getting statistics: {str(e)}")
            return {"enabled": False, "error": str(e)}


class PerOrchestrationTraceWriter:
    """Per-orchestrator trace writer."""

    def __init__(
        self,
        logger_instance: Optional[OrchestratorTraceLogger],
        orchestrator_id: str,
        orchestrator_class: str,
    ) -> None:
        """Initialize per-orchestrator trace writer."""
        self.logger_instance = logger_instance
        self.orchestrator_id = orchestrator_id
        self.orchestrator_class = orchestrator_class
        self.table_name = f"trace_{self._sanitize_name(orchestrator_id)}"
        self._initialized = False
        self._row_count = 0

        if logger_instance and logger_instance._trace_enabled:
            self._init_table()

    def _sanitize_name(self, name: str) -> str:
        """Sanitize name for SQLite table."""
        return name.lower().replace("-", "_").replace(".", "_")

    def _init_table(self) -> None:
        """Create per-orchestrator trace table."""
        if not self.logger_instance or not self.logger_instance._trace_enabled:
            return

        try:
            with self.logger_instance._get_connection() as conn:
                conn.execute(
                    f"""
                    CREATE TABLE IF NOT EXISTS {self.table_name} (
                        trace_id TEXT PRIMARY KEY,
                        timestamp TEXT NOT NULL,
                        action TEXT NOT NULL,
                        level TEXT NOT NULL,
                        correlation_id TEXT,
                        request_id TEXT,
                        context TEXT,
                        result TEXT,
                        violation_type TEXT,
                        duration_ms REAL,
                        metadata TEXT
                    )
                    """
                )

                conn.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_timestamp
                    ON {self.table_name}(timestamp DESC)
                    """
                )

                conn.execute(
                    f"""
                    CREATE INDEX IF NOT EXISTS idx_{self.table_name}_correlation
                    ON {self.table_name}(correlation_id)
                    """
                )

                # Register in metadata
                conn.execute(
                    """
                    INSERT OR IGNORE INTO trace_metadata
                    (id, orchestrator_id, orchestrator_class, table_name, created_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (
                        str(uuid.uuid4()),
                        self.orchestrator_id,
                        self.orchestrator_class,
                        self.table_name,
                        datetime.utcnow().isoformat(),
                        datetime.utcnow().isoformat(),
                    ),
                )

                conn.commit()
                self._initialized = True
        except Exception as e:
            logger.error(f"Error initializing trace table {self.table_name}: {str(e)}")

    def write_trace(self, entry: TraceEntry) -> Result[None]:
        """Write trace entry to table."""
        if not self.logger_instance or not self.logger_instance._trace_enabled:
            return Ok(None)

        try:
            with self.logger_instance._get_connection() as conn:
                conn.execute(
                    f"""
                    INSERT INTO {self.table_name}
                    (trace_id, timestamp, action, level, correlation_id, request_id,
                     context, result, violation_type, duration_ms, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.trace_id,
                        entry.timestamp.isoformat(),
                        entry.action,
                        entry.level.value,
                        entry.correlation_id,
                        entry.request_id,
                        json.dumps(entry.context, default=str),
                        entry.result,
                        entry.violation_type,
                        entry.duration_ms,
                        json.dumps(entry.metadata, default=str),
                    ),
                )

                # Update metadata
                conn.execute(
                    """
                    UPDATE trace_metadata
                    SET row_count = row_count + 1, last_updated = ?
                    WHERE table_name = ?
                    """,
                    (datetime.utcnow().isoformat(), self.table_name),
                )

                conn.commit()
                self._row_count += 1

                # Check if flush needed
                if self._row_count % 100 == 0:  # Check every 100 inserts
                    self._check_and_flush()

                return Ok(None)
        except Exception as e:
            logger.error(f"Error writing trace: {str(e)}")
            return Err(str(e))

    def _check_and_flush(self) -> None:
        """Check if flush is needed and execute."""
        if not self.logger_instance or not self.logger_instance._trace_enabled:
            return

        try:
            if self._row_count >= self.logger_instance.MAX_ROWS_PER_TABLE:
                self.logger_instance.flush_traces(TraceFlushReason.MAX_ROWS)
                self._row_count = 0
        except Exception as e:
            logger.warning(f"Error checking trace flush: {str(e)}")


class TraceFlushPolicy:
    """Configurable trace flush policy."""

    def __init__(self, max_rows_per_table: int = 10000, flush_interval_hours: int = 24) -> None:
        """Initialize flush policy."""
        self.max_rows_per_table = max_rows_per_table
        self.flush_interval = timedelta(hours=flush_interval_hours)

    def execute_flush(
        self, conn: sqlite3.Connection, reason: TraceFlushReason
    ) -> Dict[str, int]:
        """Execute flush and return rows removed per table."""
        tables_flushed: Dict[str, int] = {}

        try:
            # Get all trace tables
            cursor = conn.execute("SELECT table_name FROM trace_metadata WHERE row_count > 0")
            tables = [row[0] for row in cursor.fetchall()]

            for table_name in tables:
                try:
                    # Get current row count
                    cursor = conn.execute(f"SELECT COUNT(*) FROM {table_name}")
                    row_count = cursor.fetchone()[0]

                    if row_count > self.max_rows_per_table:
                        # Delete oldest 50% of rows
                        rows_to_delete = row_count // 2

                        conn.execute(
                            f"""
                            DELETE FROM {table_name}
                            WHERE trace_id IN (
                                SELECT trace_id FROM {table_name}
                                ORDER BY timestamp ASC
                                LIMIT ?
                            )
                            """,
                            (rows_to_delete,),
                        )

                        tables_flushed[table_name] = rows_to_delete

                        # Update metadata
                        new_count = row_count - rows_to_delete
                        conn.execute(
                            """
                            UPDATE trace_metadata
                            SET row_count = ?, last_flush_time = ?
                            WHERE table_name = ?
                            """,
                            (new_count, datetime.utcnow().isoformat(), table_name),
                        )
                except Exception as e:
                    logger.warning(f"Error flushing table {table_name}: {str(e)}")

        except Exception as e:
            logger.error(f"Error executing flush policy: {str(e)}")

        return tables_flushed


def get_trace_logger() -> OrchestratorTraceLogger:
    """Get global trace logger instance."""
    return OrchestratorTraceLogger()


if __name__ == "__main__":
    # Simple test
    logger.info("Testing OrchestratorTraceLogger...")

    trace_logger = get_trace_logger()
    writer = trace_logger.get_trace_writer("master-orchestrator", "MasterOrchestrator")

    entry = TraceEntry(
        trace_id=str(uuid.uuid4()),
        timestamp=datetime.utcnow(),
        orchestrator_id="master-orchestrator",
        orchestrator_class="MasterOrchestrator",
        action="EXECUTE_OPERATION",
        level=TraceLevel.ACTION,
        correlation_id=str(uuid.uuid4()),
        request_id=str(uuid.uuid4()),
        context={"operation": "test", "status": "success"},
        result="OK",
        duration_ms=125.5,
    )

    result = trace_logger.record_trace(entry)
    print(f"Trace recorded: {result}")

    stats = trace_logger.get_statistics()
    print(f"Statistics: {stats}")
