"""
Tests for ApprovalSessionManager - Stateful DoR approval across MCP calls.

AC-ID: AC-PHASE41-S1-001
Purpose: Enable multi-turn DoR approval workflow with session persistence

Test Coverage:
1. Session creation and storage
2. Session retrieval by ID
3. Session expiration and cleanup
4. Approval state persistence
5. Concurrent session management
6. Session deletion
7. Gate state serialization/deserialization
8. Error handling

Governance: CORE-008 (TDD-first), CORE-011 (type hints)
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch

from cortex.brain.state.approval_session_manager import (
    ApprovalSessionManager,
    ApprovalSession,
    SessionNotFoundError,
    SessionExpiredError,
)
from cortex.orchestrators.core.dor_approval_gate import (
    DoRApprovalGate,
    IntentReflection,
    ApprovalDecision,
)
from cortex.models.canonical_enums import ApprovalStatus


class TestApprovalSessionCreation:
    """Tests for creating and storing approval sessions."""

    def setup_method(self) -> None:
        """Clear singleton state before each test."""
        manager = ApprovalSessionManager()
        manager.clear_all()

    def test_create_session_generates_unique_id(self) -> None:
        """Session creation generates unique session ID."""
        manager = ApprovalSessionManager()
        
        gate = DoRApprovalGate()
        session1 = manager.create_session(gate, user_id="user1")
        session2 = manager.create_session(gate, user_id="user1")
        
        assert session1.session_id != session2.session_id
        assert len(session1.session_id) == 36  # UUID format

    def test_create_session_stores_gate_state(self) -> None:
        """Session stores complete DoR gate state."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        # Classify intent to populate gate state
        with patch('cortex.orchestrators.core.dor_approval_gate.IntentRouter'):
            gate.classify_and_reflect("Implement auth", {})
        
        session = manager.create_session(gate, user_id="user1")
        
        assert session.gate_state is not None
        assert "current_reflection" in session.gate_state  # Fixed: current_reflection, not intent_reflection
        assert session.user_id == "user1"

    def test_create_session_with_metadata(self) -> None:
        """Session stores optional metadata."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        metadata = {"context": "test", "priority": "high"}
        session = manager.create_session(gate, user_id="user1", metadata=metadata)
        
        assert session.metadata == metadata

    def test_session_tracks_creation_time(self) -> None:
        """Session records creation timestamp."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        before = datetime.now()
        session = manager.create_session(gate, user_id="user1")
        after = datetime.now()
        
        assert before <= session.created_at <= after


class TestApprovalSessionRetrieval:
    """Tests for retrieving approval sessions."""

    def setup_method(self) -> None:
        """Clear singleton state before each test."""
        manager = ApprovalSessionManager()
        manager.clear_all()

    def test_get_session_by_id(self) -> None:
        """Retrieve session by session_id."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        session = manager.create_session(gate, user_id="user1")
        retrieved = manager.get_session(session.session_id)
        
        assert retrieved is not None
        assert retrieved.session_id == session.session_id
        assert retrieved.user_id == "user1"

    def test_get_nonexistent_session_returns_none(self) -> None:
        """Getting non-existent session returns None."""
        manager = ApprovalSessionManager()
        
        result = manager.get_session("nonexistent-id")
        
        assert result is None

    def test_restore_gate_from_session(self) -> None:
        """Restore DoR gate state from session."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        # Classify and approve
        with patch('cortex.orchestrators.core.dor_approval_gate.IntentRouter'):
            gate.classify_and_reflect("Implement feature", {})
            gate.approve()
        
        session = manager.create_session(gate, user_id="user1")
        
        # Restore gate from session
        restored_gate = manager.restore_gate(session.session_id)
        
        assert restored_gate is not None
        assert restored_gate.is_approved
        assert restored_gate._pending_text == gate._pending_text


class TestSessionExpiration:
    """Tests for session expiration and cleanup."""

    def setup_method(self) -> None:
        """Clear singleton state before each test."""
        manager = ApprovalSessionManager()
        manager.clear_all()

    def test_session_expires_after_ttl(self) -> None:
        """Session expires after TTL seconds."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        # Create session with backdated timestamp
        session = manager.create_session(gate, user_id="user1")
        session.created_at = datetime.now() - timedelta(seconds=400)
        
        assert session.is_expired(ttl_seconds=300)

    def test_cleanup_expired_sessions(self) -> None:
        """Cleanup removes expired sessions."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        # Create expired and active sessions
        session1 = manager.create_session(gate, user_id="user1")
        session1.created_at = datetime.now() - timedelta(seconds=400)
        
        session2 = manager.create_session(gate, user_id="user2")
        
        # Cleanup with 300s TTL
        removed = manager.cleanup_expired_sessions(ttl_seconds=300)
        
        assert removed == 1
        assert manager.get_session(session1.session_id) is None
        assert manager.get_session(session2.session_id) is not None

    def test_get_expired_session_raises_error(self) -> None:
        """Getting expired session with enforce=True raises error."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        session = manager.create_session(gate, user_id="user1")
        session.created_at = datetime.now() - timedelta(seconds=400)
        
        with pytest.raises(SessionExpiredError):
            manager.get_session(session.session_id, enforce_ttl=True, ttl_seconds=300)


class TestSessionDeletion:
    """Tests for deleting sessions."""

    def setup_method(self) -> None:
        """Clear singleton state before each test."""
        manager = ApprovalSessionManager()
        manager.clear_all()

    def test_delete_session_removes_from_store(self) -> None:
        """Delete session removes it from storage."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        session = manager.create_session(gate, user_id="user1")
        deleted = manager.delete_session(session.session_id)
        
        assert deleted is True
        assert manager.get_session(session.session_id) is None

    def test_delete_nonexistent_session_returns_false(self) -> None:
        """Deleting non-existent session returns False."""
        manager = ApprovalSessionManager()
        
        result = manager.delete_session("nonexistent-id")
        
        assert result is False


class TestConcurrentSessionManagement:
    """Tests for managing multiple concurrent sessions."""

    def setup_method(self) -> None:
        """Clear singleton state before each test."""
        manager = ApprovalSessionManager()
        manager.clear_all()

    def test_multiple_sessions_per_user(self) -> None:
        """User can have multiple concurrent sessions."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        session1 = manager.create_session(gate, user_id="user1")
        session2 = manager.create_session(gate, user_id="user1")
        
        assert session1.session_id != session2.session_id
        assert manager.get_session(session1.session_id) is not None
        assert manager.get_session(session2.session_id) is not None

    def test_list_sessions_by_user(self) -> None:
        """List all sessions for a specific user."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        session1 = manager.create_session(gate, user_id="user1")
        session2 = manager.create_session(gate, user_id="user1")
        manager.create_session(gate, user_id="user2")
        
        user1_sessions = manager.list_sessions_by_user("user1")
        
        assert len(user1_sessions) == 2
        session_ids = [s.session_id for s in user1_sessions]
        assert session1.session_id in session_ids
        assert session2.session_id in session_ids


class TestApprovalStatePersistence:
    """Tests for persisting approval state across calls."""

    def setup_method(self) -> None:
        """Clear singleton state before each test."""
        manager = ApprovalSessionManager()
        manager.clear_all()

    def test_pending_approval_persists(self) -> None:
        """Pending approval state persists in session."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        # Classify (pending approval)
        with patch('cortex.orchestrators.core.dor_approval_gate.IntentRouter'):
            gate.classify_and_reflect("Implement feature", {})
        
        session = manager.create_session(gate, user_id="user1")
        restored = manager.restore_gate(session.session_id)
        
        assert restored.is_pending
        assert not restored.is_approved

    def test_approved_state_persists(self) -> None:
        """Approved state persists in session."""
        manager = ApprovalSessionManager()
        gate = DoRApprovalGate()
        
        # Classify and approve
        with patch('cortex.orchestrators.core.dor_approval_gate.IntentRouter'):
            gate.classify_and_reflect("Implement feature", {})
            gate.approve()
        
        session = manager.create_session(gate, user_id="user1")
        restored = manager.restore_gate(session.session_id)
        
        assert restored.is_approved
        assert restored._approval_decision.status == ApprovalStatus.APPROVED
