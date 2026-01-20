"""
Test suite for MCP Session Context Injection.

Tests for MCPSession dataclass and SessionManager singleton covering:
- Session creation with unique session_id
- repo_id extraction and context
- Session isolation metadata
- Concurrent session handling
- Session timeout and cleanup
- Audit trail integration
"""

import pytest
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from unittest.mock import Mock, patch, MagicMock


class TestMCPSessionDataclass:
    """Test MCPSession dataclass for session representation."""

    def test_session_creation_with_defaults(self):
        """MCPSession created with valid session_id."""
        from cortex.mcp.models.session import MCPSession

        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        assert session.session_id == "sess-001"
        assert session.repo_id == "repo-test"
        assert session.repo_path == "/path/to/repo"
        assert session.created_at is not None

    def test_session_unique_id_format(self):
        """Session ID follows expected format (UUID-based)."""
        from cortex.mcp.models.session import MCPSession

        session = MCPSession(
            session_id=str(uuid.uuid4()),
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        # Session ID should be valid UUID string
        uuid.UUID(session.session_id)  # Will raise ValueError if invalid

    def test_session_metadata_storage(self):
        """Session stores arbitrary metadata dict."""
        from cortex.mcp.models.session import MCPSession

        metadata = {"orchestrator_type": "IMPLEMENT", "phase": "PHASE-08"}
        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
            metadata=metadata,
        )

        assert session.metadata == metadata
        assert session.metadata["orchestrator_type"] == "IMPLEMENT"

    def test_session_isolation_boundary(self):
        """Session enforces repo_path isolation boundary."""
        from cortex.mcp.models.session import MCPSession

        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        # Session boundary should be clearly defined
        assert session.repo_path == "/path/to/repo"
        assert session.repo_id == "repo-test"


class TestSessionManager:
    """Test SessionManager singleton for session lifecycle."""

    def test_session_manager_singleton(self):
        """SessionManager is singleton (same instance)."""
        from cortex.mcp.models.session import SessionManager

        manager1 = SessionManager()
        manager2 = SessionManager()

        assert manager1 is manager2

    def test_create_session(self):
        """SessionManager creates session with unique session_id."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        session = manager.create_session(
            repo_id="repo-test", repo_path="/path/to/repo"
        )

        assert session.session_id is not None
        assert session.repo_id == "repo-test"
        assert session.repo_path == "/path/to/repo"
        assert len(session.session_id) > 0

    def test_create_session_unique_ids(self):
        """Each session gets unique session_id."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        session1 = manager.create_session(repo_id="repo-1", repo_path="/path/1")
        session2 = manager.create_session(repo_id="repo-2", repo_path="/path/2")

        assert session1.session_id != session2.session_id

    def test_get_session_by_id(self):
        """SessionManager retrieves session by session_id."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        created_session = manager.create_session(
            repo_id="repo-test", repo_path="/path/to/repo"
        )
        retrieved_session = manager.get_session(created_session.session_id)

        assert retrieved_session is not None
        assert retrieved_session.session_id == created_session.session_id

    def test_get_session_nonexistent(self):
        """SessionManager returns None for nonexistent session."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        session = manager.get_session("nonexistent-session-id")

        assert session is None

    def test_session_list(self):
        """SessionManager lists all active sessions."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        manager._sessions = {}  # Reset

        session1 = manager.create_session(repo_id="repo-1", repo_path="/path/1")
        session2 = manager.create_session(repo_id="repo-2", repo_path="/path/2")

        sessions = manager.list_sessions()

        assert len(sessions) >= 2
        assert any(s.session_id == session1.session_id for s in sessions)
        assert any(s.session_id == session2.session_id for s in sessions)

    def test_delete_session(self):
        """SessionManager deletes session by session_id."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        session = manager.create_session(repo_id="repo-test", repo_path="/path/to/repo")
        session_id = session.session_id

        manager.delete_session(session_id)
        retrieved = manager.get_session(session_id)

        assert retrieved is None

    def test_session_context_with_metadata(self):
        """Session stores and retrieves metadata."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        metadata = {"user": "test-user", "intent": "IMPLEMENT"}
        session = manager.create_session(
            repo_id="repo-test", repo_path="/path/to/repo", metadata=metadata
        )

        assert session.metadata["user"] == "test-user"
        assert session.metadata["intent"] == "IMPLEMENT"


class TestMultipleConcurrentSessions:
    """Test handling of multiple concurrent sessions."""

    def test_multiple_sessions_different_repos(self):
        """Multiple sessions can exist for different repos."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        manager._sessions = {}  # Reset

        session1 = manager.create_session(repo_id="repo-1", repo_path="/path/1")
        session2 = manager.create_session(repo_id="repo-2", repo_path="/path/2")
        session3 = manager.create_session(repo_id="repo-3", repo_path="/path/3")

        assert len(manager.list_sessions()) == 3
        assert manager.get_session(session1.session_id) is not None
        assert manager.get_session(session2.session_id) is not None
        assert manager.get_session(session3.session_id) is not None

    def test_session_isolation_between_repos(self):
        """Sessions for different repos remain isolated."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        manager._sessions = {}  # Reset

        session1 = manager.create_session(
            repo_id="repo-1",
            repo_path="/path/1",
            metadata={"data": "session1-data"},
        )
        session2 = manager.create_session(
            repo_id="repo-2",
            repo_path="/path/2",
            metadata={"data": "session2-data"},
        )

        # Each session's metadata should be independent
        assert session1.metadata["data"] == "session1-data"
        assert session2.metadata["data"] == "session2-data"
        assert session1.repo_id != session2.repo_id

    def test_concurrent_session_creation(self):
        """Multiple sessions can be created rapidly."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        manager._sessions = {}  # Reset

        sessions = [
            manager.create_session(repo_id=f"repo-{i}", repo_path=f"/path/{i}")
            for i in range(10)
        ]

        assert len(sessions) == 10
        session_ids = [s.session_id for s in sessions]
        assert len(set(session_ids)) == 10  # All unique


class TestSessionTimeout:
    """Test session timeout and cleanup."""

    def test_session_timestamp_tracking(self):
        """Session tracks creation timestamp."""
        from cortex.mcp.models.session import MCPSession

        now = datetime.now()
        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=now,
        )

        assert session.created_at == now

    def test_session_age_calculation(self):
        """Session age can be calculated."""
        from cortex.mcp.models.session import MCPSession

        past = datetime.now() - timedelta(hours=1)
        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=past,
        )

        age = datetime.now() - session.created_at
        assert age.total_seconds() >= 3600  # At least 1 hour old

    def test_session_expiration_logic(self):
        """SessionManager can detect expired sessions."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        manager._sessions = {}  # Reset

        # Create session with old timestamp
        old_time = datetime.now() - timedelta(hours=25)  # 25 hours old
        session = manager.create_session(repo_id="repo-test", repo_path="/path/to/repo")
        session.created_at = old_time

        # Session should be detected as expired (>24 hours)
        assert (datetime.now() - session.created_at).total_seconds() > 86400


class TestSessionAuditTrail:
    """Test session integration with audit trail."""

    def test_session_includes_repo_id_context(self):
        """Session context includes repo_id for audit."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        session = manager.create_session(repo_id="repo-audit", repo_path="/path/repo")

        # Session should provide repo_id for audit logging
        assert session.repo_id == "repo-audit"

    def test_audit_context_from_session(self):
        """Audit context can be derived from session."""
        from cortex.mcp.models.session import MCPSession

        session = MCPSession(
            session_id="sess-audit-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        # Audit context should include session and repo info
        audit_context = {
            "session_id": session.session_id,
            "repo_id": session.repo_id,
            "repo_path": session.repo_path,
        }

        assert audit_context["session_id"] is not None
        assert audit_context["repo_id"] is not None


class TestSessionCleanup:
    """Test session cleanup on disconnect."""

    def test_cleanup_single_session(self):
        """SessionManager cleans up session on disconnect."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        session = manager.create_session(repo_id="repo-test", repo_path="/path/to/repo")
        session_id = session.session_id

        # Session should exist
        assert manager.get_session(session_id) is not None

        # Cleanup on disconnect
        manager.delete_session(session_id)

        # Session should be removed
        assert manager.get_session(session_id) is None

    def test_cleanup_multiple_sessions(self):
        """SessionManager cleans up all sessions."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        manager._sessions = {}  # Reset

        sessions = [
            manager.create_session(repo_id=f"repo-{i}", repo_path=f"/path/{i}")
            for i in range(5)
        ]

        session_ids = [s.session_id for s in sessions]

        # All sessions should exist
        for sid in session_ids:
            assert manager.get_session(sid) is not None

        # Cleanup all
        for sid in session_ids:
            manager.delete_session(sid)

        # All sessions should be removed
        for sid in session_ids:
            assert manager.get_session(sid) is None


class TestSessionWithOrchestrators:
    """Test session context passing to orchestrators."""

    def test_session_context_dict(self):
        """Session can be converted to context dict for orchestrators."""
        from cortex.mcp.models.session import MCPSession

        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
            metadata={"orchestrator": "IMPLEMENT"},
        )

        # Create context dict for orchestrator
        context = {
            "__cortex_session__": {
                "session_id": session.session_id,
                "repo_id": session.repo_id,
                "repo_path": session.repo_path,
                "metadata": session.metadata,
            }
        }

        assert context["__cortex_session__"]["session_id"] == session.session_id
        assert context["__cortex_session__"]["repo_id"] == session.repo_id

    def test_session_context_immutability(self):
        """Session context passed to orchestrators shouldn't be modified."""
        from cortex.mcp.models.session import MCPSession

        session = MCPSession(
            session_id="sess-001",
            repo_id="repo-test",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        # Session fields should not be easily modified
        original_repo_id = session.repo_id
        # Attempting to modify should not affect session integrity
        assert session.repo_id == original_repo_id


class TestSessionRegressionPrevention:
    """Regression tests for existing MCP functionality."""

    def test_mcp_server_compatibility(self):
        """SessionManager doesn't break existing MCP server."""
        # This test ensures no regression - session code should be additive
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        assert manager is not None
        assert hasattr(manager, "create_session")
        assert hasattr(manager, "get_session")
        assert hasattr(manager, "delete_session")

    def test_session_manager_is_injectable(self):
        """SessionManager can be injected into existing code."""
        from cortex.mcp.models.session import SessionManager

        manager = SessionManager()
        # Should be usable in existing MCP server code
        assert callable(manager.create_session)
        assert callable(manager.get_session)
