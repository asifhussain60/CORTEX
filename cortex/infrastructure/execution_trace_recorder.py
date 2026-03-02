"""Execution Trace Recorder — Unified SQLite timeline for orchestrator invocations.

Records orchestrator invocations, template selections, and tool engagements
to `.cortex-runtime/traces/orchestrator-traces.db` for timeline reconstruction.

Phase 89-d: GAP-89-10, GAP-89-11, GAP-89-12
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any


class ExecutionTraceRecorder:
    """Records execution traces to SQLite for timeline reconstruction.

    Thread-safe SQLite recorder that captures orchestrator invocations,
    template selections, and tool engagements. Enforces 30-day retention.
    """

    def __init__(self, db_path: str | None = None) -> None:
        """Initialize ExecutionTraceRecorder with SQLite database.

        Args:
            db_path: Path to SQLite database. Defaults to .cortex-runtime/traces/orchestrator-traces.db
        """
        if db_path is None:
            db_path = ".cortex-runtime/traces/orchestrator-traces.db"

        self.db_path = db_path
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        """Create execution_traces table if it doesn't exist."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS execution_traces (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                session_id TEXT,
                orchestrator TEXT,
                operation TEXT,
                template_id TEXT,
                tool TEXT,
                command TEXT,
                exit_code INTEGER,
                file_path TEXT,
                issues_found INTEGER,
                issues_fixed INTEGER,
                duration_ms INTEGER,
                status TEXT,
                rationale TEXT
            )
        """)

        # Create index on timestamp for retention cleanup
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_execution_traces_timestamp
            ON execution_traces(timestamp)
        """)

        conn.commit()
        conn.close()

    def record_orchestrator_invocation(
        self,
        orchestrator: str,
        operation: str,
        status: str,
        duration_ms: int,
        session_id: str | None = None,
    ) -> None:
        """Record an orchestrator invocation.

        Args:
            orchestrator: Orchestrator class name
            operation: Operation type (implement, refactor, audit, etc.)
            status: Execution status (success, error)
            duration_ms: Execution duration in milliseconds
            session_id: Optional session identifier for filtering
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO execution_traces
                (session_id, orchestrator, operation, status, duration_ms)
            VALUES (?, ?, ?, ?, ?)
            """,
            (session_id, orchestrator, operation, status, duration_ms),
        )

        conn.commit()
        conn.close()

    def record_template_selection(
        self,
        template_id: str,
        orchestrator: str,
        rationale: str,
        session_id: str | None = None,
    ) -> None:
        """Record a workflow template selection.

        Args:
            template_id: Template path (e.g., 'frontend/html-refactor-validation')
            orchestrator: Orchestrator that selected the template
            rationale: Reason for template selection
            session_id: Optional session identifier
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO execution_traces
                (session_id, orchestrator, template_id, rationale, status)
            VALUES (?, ?, ?, ?, 'template_selected')
            """,
            (session_id, orchestrator, template_id, rationale),
        )

        conn.commit()
        conn.close()

    def record_tool_engagement(
        self,
        tool: str,
        command: str,
        exit_code: int,
        duration_ms: int,
        session_id: str | None = None,
    ) -> None:
        """Record a tool engagement (linter, formatter, external command).

        Args:
            tool: Tool name (ruff, eslint, dotnet format, etc.)
            command: Full command executed
            exit_code: Process exit code
            duration_ms: Execution duration in milliseconds
            session_id: Optional session identifier
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO execution_traces
                (session_id, tool, command, exit_code, duration_ms, status)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                tool,
                command,
                exit_code,
                duration_ms,
                "success" if exit_code == 0 else "error",
            ),
        )

        conn.commit()
        conn.close()

    def record_lint_result(
        self,
        linter: str,
        file_path: str,
        issues_found: int,
        issues_fixed: int,
        duration_ms: int,
        session_id: str | None = None,
    ) -> None:
        """Record a linter execution result.

        Args:
            linter: Linter name (ruff, eslint, stylelint, etc.)
            file_path: File that was linted
            issues_found: Number of issues detected
            issues_fixed: Number of issues auto-fixed
            duration_ms: Execution duration in milliseconds
            session_id: Optional session identifier
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO execution_traces
                (session_id, tool, file_path, issues_found, issues_fixed, duration_ms, status)
            VALUES (?, ?, ?, ?, ?, ?, 'lint_complete')
            """,
            (session_id, linter, file_path, issues_found, issues_fixed, duration_ms),
        )

        conn.commit()
        conn.close()

    def get_timeline(self, session_id: str | None = None) -> list[dict[str, Any]]:
        """Retrieve chronological timeline of all execution events.

        Args:
            session_id: Optional filter by session ID

        Returns:
            List of event dictionaries in chronological order
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if session_id is not None:
            cursor.execute(
                "SELECT * FROM execution_traces WHERE session_id=? ORDER BY timestamp ASC",
                (session_id,),
            )
        else:
            cursor.execute("SELECT * FROM execution_traces ORDER BY timestamp ASC")

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def cleanup_old_traces(self, retention_days: int = 30) -> int:
        """Remove traces older than retention period.

        Args:
            retention_days: Number of days to retain (default: 30)

        Returns:
            Number of rows deleted
        """
        cutoff = datetime.now() - timedelta(days=retention_days)
        cutoff_str = cutoff.strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM execution_traces WHERE timestamp < ?", (cutoff_str,))
        deleted = cursor.rowcount

        conn.commit()
        conn.close()

        return deleted
