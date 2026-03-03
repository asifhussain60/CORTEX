"""
RequestLogManager — Phase 113 Sub-phase A.

Persists every user request to SQLite BEFORE the request enters the orchestration
pipeline. Provides:
  - Pre-API audit trail (survives API timeout/failure)
  - Unique request_id for end-to-end correlation
  - Session-scoped 1-based sequence numbers
  - Chain linkage via parent_request_id FK
  - Status lifecycle: RECEIVED → PROCESSING → COMPLETED | FAILED
  - get_prior_requests() for InteractionOrchestrator context chain (Phase 113-C)

Database: .cortex-runtime/state/conversations.db  (shared with ConversationStateManager)
Table:    request_log
"""

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional
from uuid import uuid4

# Canonical runtime path — can be overridden in tests via `db_path` parameter
_DEFAULT_DB_PATH: Path = (
    Path(__file__).parent.parent.parent.parent
    / ".cortex-runtime"
    / "state"
    / "conversations.db"
)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS request_log (
    request_id        TEXT PRIMARY KEY,
    session_id        TEXT NOT NULL,
    sequence_number   INTEGER NOT NULL,
    user_request      TEXT NOT NULL,
    request_hash      TEXT NOT NULL,
    received_at       TEXT NOT NULL,
    completed_at      TEXT,
    duration_ms       REAL,
    intent_type       TEXT,
    orchestrator_chain TEXT,
    status            TEXT NOT NULL DEFAULT 'RECEIVED',
    error_summary     TEXT,
    context_snapshot  TEXT,
    parent_request_id TEXT,
    FOREIGN KEY (parent_request_id) REFERENCES request_log(request_id)
);
"""

_CREATE_INDEX_SESSION_SQL = """
CREATE INDEX IF NOT EXISTS idx_request_log_session
    ON request_log(session_id, sequence_number);
"""

_CREATE_INDEX_RECEIVED_SQL = """
CREATE INDEX IF NOT EXISTS idx_request_log_received
    ON request_log(received_at DESC);
"""

_CREATE_INDEX_STATUS_SQL = """
CREATE INDEX IF NOT EXISTS idx_request_log_status
    ON request_log(status);
"""


class RequestLogManager:
    """
    Manages pre-API request persistence in the request_log SQLite table.

    Every call to :meth:`log_request` is executed **before** the request enters
    the orchestration pipeline, guaranteeing an audit trail even if the pipeline
    crashes or times out.

    Args:
        db_path: Path to the SQLite database.  Defaults to
            ``.cortex-runtime/state/conversations.db`` (shared with
            ``ConversationStateManager``).
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize the manager and create the schema if it does not exist."""
        self.db_path: Path = Path(db_path) if db_path is not None else _DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    # ── Schema ────────────────────────────────────────────────────────────────

    def _init_schema(self) -> None:
        """Create the request_log table and indexes if they do not exist."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(_CREATE_TABLE_SQL)
            conn.execute(_CREATE_INDEX_SESSION_SQL)
            conn.execute(_CREATE_INDEX_RECEIVED_SQL)
            conn.execute(_CREATE_INDEX_STATUS_SQL)
            conn.commit()

    # ── Public API ────────────────────────────────────────────────────────────

    def log_request(
        self,
        session_id: str,
        user_request: str,
        context_snapshot: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Persist a new user request BEFORE it enters the orchestration pipeline.

        Assigns a unique ``request_id``, computes a SHA-256 hash for dedup,
        auto-increments the per-session ``sequence_number``, and links
        ``parent_request_id`` to the previous request in the same session.

        Args:
            session_id: Identifier for the current conversation session.
            user_request: The full, untruncated user request text.
            context_snapshot: Optional dict of ambient context at request time.

        Returns:
            The generated ``request_id`` (UUID string).
        """
        request_id = str(uuid4())
        request_hash = hashlib.sha256(user_request.encode("utf-8")).hexdigest()
        received_at = datetime.now(timezone.utc).isoformat()
        context_json = json.dumps(context_snapshot) if context_snapshot else None

        with sqlite3.connect(self.db_path) as conn:
            # Determine sequence number and parent_request_id in one query
            row = conn.execute(
                """
                SELECT sequence_number, request_id
                FROM request_log
                WHERE session_id = ?
                ORDER BY sequence_number DESC
                LIMIT 1
                """,
                (session_id,),
            ).fetchone()

            if row is None:
                sequence_number = 1
                parent_request_id = None
            else:
                sequence_number = row[0] + 1
                parent_request_id = row[1]

            conn.execute(
                """
                INSERT INTO request_log (
                    request_id, session_id, sequence_number, user_request,
                    request_hash, received_at, status, context_snapshot,
                    parent_request_id
                ) VALUES (?, ?, ?, ?, ?, ?, 'RECEIVED', ?, ?)
                """,
                (
                    request_id,
                    session_id,
                    sequence_number,
                    user_request,
                    request_hash,
                    received_at,
                    context_json,
                    parent_request_id,
                ),
            )
            conn.commit()

        return request_id

    def update_status(
        self,
        request_id: str,
        status: str,
        *,
        duration_ms: Optional[float] = None,
        error_summary: Optional[str] = None,
        intent_type: Optional[str] = None,
        orchestrator_chain: Optional[List[str]] = None,
    ) -> None:
        """
        Update the lifecycle status of a persisted request.

        Called at multiple points during orchestration:
        - ``PROCESSING``  — immediately after ``log_request``, before API call
        - ``COMPLETED``   — after the orchestration pipeline finishes
        - ``FAILED``      — if the pipeline raises an unhandled exception

        Args:
            request_id: The UUID returned by :meth:`log_request`.
            status: New status string (``RECEIVED`` | ``PROCESSING`` |
                ``COMPLETED`` | ``FAILED``).
            duration_ms: Total processing time in milliseconds (set on COMPLETED).
            error_summary: Error message (set on FAILED).
            intent_type: Classified intent type (set post-routing).
            orchestrator_chain: List of orchestrator display names (set on COMPLETED).
        """
        updates: List[str] = ["status = ?"]
        params: List[Any] = [status]

        if status in ("COMPLETED", "FAILED"):
            updates.append("completed_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())

        if duration_ms is not None:
            updates.append("duration_ms = ?")
            params.append(duration_ms)

        if error_summary is not None:
            updates.append("error_summary = ?")
            params.append(error_summary)

        if intent_type is not None:
            updates.append("intent_type = ?")
            params.append(intent_type)

        if orchestrator_chain is not None:
            updates.append("orchestrator_chain = ?")
            params.append(json.dumps(orchestrator_chain))

        params.append(request_id)

        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                f"UPDATE request_log SET {', '.join(updates)} WHERE request_id = ?",
                params,
            )
            conn.commit()

    def get_prior_requests(
        self,
        session_id: str,
        limit: int = 5,
        exclude_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Return the most recent prior requests for a session, newest first.

        Used by ``InteractionOrchestrator`` (Phase 113-C) to build a cumulative
        context summary for the current turn's LENS analysis.

        Args:
            session_id: Session to query.
            limit: Maximum number of records to return.
            exclude_id: Optional ``request_id`` to exclude (e.g., the current
                request so it does not appear in its own prior context).

        Returns:
            List of dicts, each containing:
            ``request_id``, ``user_request``, ``sequence_number``,
            ``intent_type``, ``received_at``, ``status``.
            Ordered newest-first (highest ``sequence_number`` first).
        """
        sql = """
            SELECT request_id, user_request, sequence_number,
                   intent_type, received_at, status
            FROM request_log
            WHERE session_id = ?
        """
        params: List[Any] = [session_id]

        if exclude_id is not None:
            sql += " AND request_id != ?"
            params.append(exclude_id)

        sql += " ORDER BY sequence_number DESC LIMIT ?"
        params.append(limit)

        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(sql, params).fetchall()

        return [
            {
                "request_id": row[0],
                "user_request": row[1],
                "sequence_number": row[2],
                "intent_type": row[3],
                "received_at": row[4],
                "status": row[5],
            }
            for row in rows
        ]
