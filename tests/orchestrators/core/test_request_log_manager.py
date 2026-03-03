"""
Tests for RequestLogManager — Phase 113 Sub-phase A.

Verifies pre-API request persistence, session-scoped sequence numbers,
chain linkage via parent_request_id, and status lifecycle transitions.

TDD sequence (RED → GREEN → REFACTOR):
  RED: all tests written first; run must show ALL FAIL before implementation.
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest


# ─── Fixtures ────────────────────────────────────────────────────────────────

@pytest.fixture()
def tmp_db(tmp_path: Path) -> Path:
    """Return a temporary SQLite database path."""
    return tmp_path / "test_request_log.db"


@pytest.fixture()
def manager(tmp_db: Path):
    """Return a RequestLogManager wired to a temp database."""
    from cortex.orchestrators.core.request_log_manager import RequestLogManager
    return RequestLogManager(db_path=tmp_db)


# ─── Schema & Init ───────────────────────────────────────────────────────────

class TestRequestLogManagerInit:
    """Verify schema is created on init."""

    def test_db_file_created_on_init(self, tmp_db: Path) -> None:
        """Database file must be created when RequestLogManager is instantiated."""
        from cortex.orchestrators.core.request_log_manager import RequestLogManager
        RequestLogManager(db_path=tmp_db)
        assert tmp_db.exists(), "DB file must be created on init"

    def test_request_log_table_exists(self, manager) -> None:
        """request_log table must exist after init."""
        import sqlite3
        with sqlite3.connect(manager.db_path) as conn:
            tables = {r[0] for r in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )}
        assert "request_log" in tables

    def test_request_log_has_required_columns(self, manager) -> None:
        """request_log must have all required columns."""
        import sqlite3
        with sqlite3.connect(manager.db_path) as conn:
            cols = {row[1] for row in conn.execute("PRAGMA table_info(request_log)")}
        required = {
            "request_id", "session_id", "sequence_number", "user_request",
            "request_hash", "received_at", "completed_at", "duration_ms",
            "intent_type", "orchestrator_chain", "status",
            "error_summary", "context_snapshot", "parent_request_id",
        }
        assert required.issubset(cols), f"Missing columns: {required - cols}"

    def test_default_db_path_is_in_cortex_runtime(self, tmp_path: Path) -> None:
        """Default db_path must resolve inside .cortex-runtime/."""
        from cortex.orchestrators.core.request_log_manager import RequestLogManager
        # Patch the canonical runtime dir so test is hermetic
        fake_runtime = tmp_path / ".cortex-runtime" / "state"
        fake_runtime.mkdir(parents=True)
        with patch(
            "cortex.orchestrators.core.request_log_manager._DEFAULT_DB_PATH",
            fake_runtime / "conversations.db",
        ):
            mgr = RequestLogManager()
        assert ".cortex-runtime" in str(mgr.db_path)


# ─── log_request ─────────────────────────────────────────────────────────────

class TestLogRequest:
    """Verify log_request() persists a row with status=RECEIVED."""

    def test_log_request_returns_request_id(self, manager) -> None:
        """log_request() must return a non-empty request_id string."""
        rid = manager.log_request(
            session_id="sess-001",
            user_request="Create a user module",
        )
        assert isinstance(rid, str) and len(rid) > 0

    def test_log_request_persists_row(self, manager) -> None:
        """Row must exist in request_log after log_request()."""
        rid = manager.log_request(session_id="sess-001", user_request="Build auth")
        with sqlite3.connect(manager.db_path) as conn:
            row = conn.execute(
                "SELECT request_id, status FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()
        assert row is not None, "Row must be in DB"
        assert row[0] == rid

    def test_log_request_initial_status_is_received(self, manager) -> None:
        """Initial status must be RECEIVED."""
        rid = manager.log_request(session_id="sess-001", user_request="Hello")
        with sqlite3.connect(manager.db_path) as conn:
            status = conn.execute(
                "SELECT status FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert status == "RECEIVED"

    def test_log_request_stores_full_user_request(self, manager) -> None:
        """Full (non-truncated) user request text must be stored."""
        long_request = "x" * 500
        rid = manager.log_request(session_id="sess-001", user_request=long_request)
        with sqlite3.connect(manager.db_path) as conn:
            text = conn.execute(
                "SELECT user_request FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert text == long_request, "Full request text must be stored without truncation"

    def test_log_request_stores_request_hash(self, manager) -> None:
        """SHA-256 hash of user_request must be stored for dedup."""
        import hashlib
        req = "Create a user module"
        rid = manager.log_request(session_id="sess-001", user_request=req)
        expected_hash = hashlib.sha256(req.encode()).hexdigest()
        with sqlite3.connect(manager.db_path) as conn:
            actual_hash = conn.execute(
                "SELECT request_hash FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert actual_hash == expected_hash

    def test_log_request_sequence_number_increments_per_session(self, manager) -> None:
        """sequence_number must be 1-based and auto-increment per session."""
        rid1 = manager.log_request(session_id="sess-A", user_request="First")
        rid2 = manager.log_request(session_id="sess-A", user_request="Second")
        rid3 = manager.log_request(session_id="sess-A", user_request="Third")
        with sqlite3.connect(manager.db_path) as conn:
            nums = [
                conn.execute(
                    "SELECT sequence_number FROM request_log WHERE request_id=?", (r,)
                ).fetchone()[0]
                for r in (rid1, rid2, rid3)
            ]
        assert nums == [1, 2, 3], f"Expected [1,2,3], got {nums}"

    def test_log_request_sequence_resets_across_sessions(self, manager) -> None:
        """sequence_number resets to 1 for a new session_id."""
        manager.log_request(session_id="sess-A", user_request="First in A")
        manager.log_request(session_id="sess-A", user_request="Second in A")
        rid_b = manager.log_request(session_id="sess-B", user_request="First in B")
        with sqlite3.connect(manager.db_path) as conn:
            seq = conn.execute(
                "SELECT sequence_number FROM request_log WHERE request_id=?", (rid_b,)
            ).fetchone()[0]
        assert seq == 1, f"Session B must start at seq=1, got {seq}"

    def test_log_request_chains_parent_request_id(self, manager) -> None:
        """parent_request_id of request N+1 must equal request_id of request N."""
        rid1 = manager.log_request(session_id="sess-chain", user_request="Turn 1")
        rid2 = manager.log_request(session_id="sess-chain", user_request="Turn 2")
        with sqlite3.connect(manager.db_path) as conn:
            parent = conn.execute(
                "SELECT parent_request_id FROM request_log WHERE request_id=?", (rid2,)
            ).fetchone()[0]
        assert parent == rid1, f"Turn 2's parent must be turn 1's id ({rid1}), got {parent}"

    def test_log_request_first_in_session_has_no_parent(self, manager) -> None:
        """First request in a session must have parent_request_id=NULL."""
        rid = manager.log_request(session_id="sess-new", user_request="Only request")
        with sqlite3.connect(manager.db_path) as conn:
            parent = conn.execute(
                "SELECT parent_request_id FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert parent is None


# ─── update_status ───────────────────────────────────────────────────────────

class TestUpdateStatus:
    """Verify update_status() drives the lifecycle state machine."""

    def test_update_status_processing(self, manager) -> None:
        """Status transitions from RECEIVED → PROCESSING."""
        rid = manager.log_request(session_id="sess-s", user_request="Work")
        manager.update_status(rid, "PROCESSING")
        with sqlite3.connect(manager.db_path) as conn:
            status = conn.execute(
                "SELECT status FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert status == "PROCESSING"

    def test_update_status_completed_with_timing(self, manager) -> None:
        """COMPLETED status must write completed_at and duration_ms."""
        rid = manager.log_request(session_id="sess-s", user_request="Work")
        manager.update_status(rid, "COMPLETED", duration_ms=123.4)
        with sqlite3.connect(manager.db_path) as conn:
            row = conn.execute(
                "SELECT status, completed_at, duration_ms FROM request_log WHERE request_id=?",
                (rid,),
            ).fetchone()
        assert row[0] == "COMPLETED"
        assert row[1] is not None, "completed_at must be set"
        assert abs(row[2] - 123.4) < 0.01

    def test_update_status_failed_with_error(self, manager) -> None:
        """FAILED status must store error_summary."""
        rid = manager.log_request(session_id="sess-s", user_request="Work")
        manager.update_status(rid, "FAILED", error_summary="Timeout after 30s")
        with sqlite3.connect(manager.db_path) as conn:
            row = conn.execute(
                "SELECT status, error_summary FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()
        assert row[0] == "FAILED"
        assert row[1] == "Timeout after 30s"

    def test_update_status_sets_intent_type(self, manager) -> None:
        """intent_type must be updateable post-routing."""
        rid = manager.log_request(session_id="sess-s", user_request="Fix the bug")
        manager.update_status(rid, "PROCESSING", intent_type="FIX")
        with sqlite3.connect(manager.db_path) as conn:
            intent = conn.execute(
                "SELECT intent_type FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert intent == "FIX"

    def test_update_status_stores_orchestrator_chain(self, manager) -> None:
        """orchestrator_chain must be stored as JSON."""
        rid = manager.log_request(session_id="sess-s", user_request="Build X")
        chain = ["Classifier", "TDD Builder"]
        manager.update_status(rid, "COMPLETED", orchestrator_chain=chain)
        with sqlite3.connect(manager.db_path) as conn:
            raw = conn.execute(
                "SELECT orchestrator_chain FROM request_log WHERE request_id=?", (rid,)
            ).fetchone()[0]
        assert json.loads(raw) == chain


# ─── get_prior_requests ───────────────────────────────────────────────────────

class TestGetPriorRequests:
    """Verify get_prior_requests() returns ordered history for session context."""

    def test_get_prior_requests_returns_ordered_list(self, manager) -> None:
        """Returns last N requests, newest-first, for the session."""
        for i in range(5):
            manager.log_request(session_id="sess-ctx", user_request=f"Request {i+1}")
        results = manager.get_prior_requests(session_id="sess-ctx", limit=3)
        assert len(results) == 3
        # Newest first — sequence_number should be 5, 4, 3
        seqs = [r["sequence_number"] for r in results]
        assert seqs == sorted(seqs, reverse=True), "Results must be newest-first"

    def test_get_prior_requests_empty_session(self, manager) -> None:
        """Returns empty list for a session with no history."""
        results = manager.get_prior_requests(session_id="sess-empty", limit=5)
        assert results == []

    def test_get_prior_requests_respects_limit(self, manager) -> None:
        """Respects limit even when session has more entries."""
        for i in range(10):
            manager.log_request(session_id="sess-lim", user_request=f"Turn {i+1}")
        results = manager.get_prior_requests(session_id="sess-lim", limit=3)
        assert len(results) == 3

    def test_get_prior_requests_contains_required_fields(self, manager) -> None:
        """Each result dict must contain request_id, user_request, sequence_number, intent_type."""
        manager.log_request(session_id="sess-fields", user_request="Build auth")
        results = manager.get_prior_requests(session_id="sess-fields", limit=1)
        assert len(results) == 1
        rec = results[0]
        for field in ("request_id", "user_request", "sequence_number", "intent_type"):
            assert field in rec, f"Field '{field}' missing from result"

    def test_get_prior_requests_does_not_include_current(self, manager) -> None:
        """get_prior_requests(exclude_id=X) must not include request X itself."""
        rid1 = manager.log_request(session_id="sess-ex", user_request="First")
        rid2 = manager.log_request(session_id="sess-ex", user_request="Second")
        results = manager.get_prior_requests(
            session_id="sess-ex", limit=5, exclude_id=rid2
        )
        result_ids = [r["request_id"] for r in results]
        assert rid2 not in result_ids, "Current request must not appear in prior requests"
        assert rid1 in result_ids
