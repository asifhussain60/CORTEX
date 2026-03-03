"""
Tests for Phase 113 Sub-phase final — GAP-05: challenge_decisions request_id FK.

Verifies that:
1. challenge_decisions table has a request_id column (backward-compatible add)
2. _log_challenge_decision() accepts and stores a request_id
3. user_request_hint column is still populated (backward compatibility)
4. request_id is None-safe (old rows without FK work fine)

TDD sequence (RED → GREEN → REFACTOR).
"""

import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest


def _make_orchestrator(tmp_db: str):
    """Return an InteractionOrchestrator wired to a temp trace DB."""
    from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
    mock_protocol = MagicMock()
    return InteractionOrchestrator(
        conversation_protocol=mock_protocol,
        enable_challenges=False,
        trace_db_path=tmp_db,
    )


class TestChallengeDecisionsRequestIdColumn:
    """challenge_decisions table must have request_id column after schema migration."""

    def test_request_id_column_exists_in_table(self, tmp_path: Path) -> None:
        """challenge_decisions table must have a request_id column."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        with sqlite3.connect(db) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(challenge_decisions)")}
        assert "request_id" in cols, (
            "challenge_decisions must have request_id column for Phase 113 FK linkage"
        )

    def test_request_id_column_is_nullable(self, tmp_path: Path) -> None:
        """request_id column must be nullable for backward compatibility with old rows."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        with sqlite3.connect(db) as conn:
            info = {row[1]: row for row in conn.execute("PRAGMA table_info(challenge_decisions)")}
        col = info.get("request_id")
        assert col is not None
        # notnull=0 means nullable
        assert col[3] == 0, "request_id must be nullable (notnull=0) for backward compatibility"

    def test_user_request_hint_column_still_exists(self, tmp_path: Path) -> None:
        """user_request_hint must still exist (backward compatibility)."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        with sqlite3.connect(db) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(challenge_decisions)")}
        assert "user_request_hint" in cols, "user_request_hint must be retained for backward compat"


class TestLogChallengeDecisionWithRequestId:
    """_log_challenge_decision() must store request_id when provided."""

    def test_log_challenge_decision_accepts_request_id(self, tmp_path: Path) -> None:
        """_log_challenge_decision() must not raise when request_id is passed."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        io.turn_number = 1

        challenge = {
            "user_request": "Build a login module",
            "category": "COMPLEXITY",
            "severity": "P1",
            "description": "Request is highly complex",
            "mitigation": "Break into smaller tasks",
        }

        # Must not raise
        io._log_challenge_decision(
            challenge=challenge,
            session_id="sess-001",
            request_id="test-rid-abc",
        )

    def test_log_challenge_decision_stores_request_id_in_db(self, tmp_path: Path) -> None:
        """request_id must be persisted to challenge_decisions.request_id column."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        io.turn_number = 1

        challenge = {
            "user_request": "Add password hashing",
            "category": "SECURITY",
            "severity": "P0",
            "description": "Security-critical change",
            "mitigation": "Use bcrypt",
        }
        rid = "canonical-request-id-phase113"

        io._log_challenge_decision(
            challenge=challenge,
            session_id="sess-002",
            request_id=rid,
        )

        with sqlite3.connect(db) as conn:
            row = conn.execute(
                "SELECT request_id FROM challenge_decisions WHERE request_id = ?", (rid,)
            ).fetchone()
        assert row is not None, "Row with request_id must be stored in DB"
        assert row[0] == rid

    def test_log_challenge_decision_user_request_hint_still_populated(self, tmp_path: Path) -> None:
        """user_request_hint must still be populated even when request_id is provided."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        io.turn_number = 1

        challenge = {
            "user_request": "Create auth service",
            "category": "COMPLEXITY",
            "severity": "P1",
            "description": "Complex auth",
            "mitigation": "Phase it",
        }

        io._log_challenge_decision(
            challenge=challenge,
            session_id="sess-003",
            request_id="rid-003",
        )

        with sqlite3.connect(db) as conn:
            hint = conn.execute(
                "SELECT user_request_hint FROM challenge_decisions WHERE request_id = 'rid-003'"
            ).fetchone()[0]
        assert hint is not None and len(hint) > 0, "user_request_hint must still be populated"

    def test_log_challenge_decision_none_request_id_is_backward_compatible(
        self, tmp_path: Path
    ) -> None:
        """_log_challenge_decision() with no request_id must still work (pre-Phase 113 calls)."""
        db = str(tmp_path / "trace.db")
        io = _make_orchestrator(db)
        io.turn_number = 1

        challenge = {
            "user_request": "Legacy call without request_id",
            "category": "STYLE",
            "severity": "P2",
            "description": "Old style",
            "mitigation": "Refactor",
        }

        # Original signature without request_id — must still work
        io._log_challenge_decision(challenge=challenge, session_id="sess-legacy")

        with sqlite3.connect(db) as conn:
            count = conn.execute("SELECT COUNT(*) FROM challenge_decisions").fetchone()[0]
        assert count == 1, "Row must be inserted even without request_id"
