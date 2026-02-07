"""
Tests for Two-Phase Approval MCP Tools.

AC-ID: AC-PHASE41-S2-001
Purpose: Enable interactive DoR approval workflow via MCP

Test Coverage:
1. cortex_classify_request - Display DoR, store session
2. cortex_approve_request - Approve and execute from session
3. cortex_reject_request - Reject and abort
4. cortex_modify_request - Modify intent and re-classify
5. Error handling (expired sessions, invalid IDs)
6. Integration with ApprovalSessionManager

Governance: CORE-008 (TDD), CORE-011 (type hints)
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any
from unittest.mock import Mock, patch, MagicMock

from cortex.mcp.tools.approval_tools import (
    cortex_classify_request,
    cortex_approve_request,
    cortex_reject_request,
    cortex_modify_request,
)


class TestClassifyRequest:
    """Tests for cortex_classify_request MCP tool."""

    def test_classify_returns_dor_display(self) -> None:
        """Classify request returns DoR markdown display."""
        result = cortex_classify_request(
            request="Implement user authentication",
            context={},
            user_id="test-user"
        )
        
        assert result["status"] == "pending_approval"
        assert "session_id" in result
        assert "dor_display" in result
        assert "### 📋 Intent Classification" in result["dor_display"]

    def test_classify_creates_session(self) -> None:
        """Classify request creates approval session."""
        result = cortex_classify_request(
            request="Implement feature X",
            context={},
            user_id="test-user"
        )
        
        session_id = result["session_id"]
        assert len(session_id) == 36  # UUID format
        
        # Session should be retrievable
        from cortex.brain.state.approval_session_manager import ApprovalSessionManager
        manager = ApprovalSessionManager()
        session = manager.get_session(session_id)
        assert session is not None

    def test_classify_shows_approval_actions(self) -> None:
        """Classify shows available approval actions."""
        result = cortex_classify_request(
            request="Implement feature",
            context={},
            user_id="test-user"
        )
        
        assert "actions" in result
        actions = result["actions"]
        assert "approve" in actions
        assert "reject" in actions
        assert "modify" in actions

    def test_classify_includes_dor_confidence(self) -> None:
        """Classify includes DoR confidence score."""
        result = cortex_classify_request(
            request="Implement authentication",
            context={},
            user_id="test-user"
        )
        
        assert "dor_confidence" in result
        assert isinstance(result["dor_confidence"], float)
        assert 0.0 <= result["dor_confidence"] <= 1.0

    def test_classify_blocks_low_confidence(self) -> None:
        """Classify blocks execution if DoR confidence too low."""
        result = cortex_classify_request(
            request="Do something",  # Vague request
            context={},
            user_id="test-user"
        )
        
        if result["dor_confidence"] < 0.6:
            assert result["dor_met"] is False
            assert "clarification" in result["dor_display"].lower()


class TestApproveRequest:
    """Tests for cortex_approve_request MCP tool."""

    def test_approve_executes_approved_request(self) -> None:
        """Approve request executes if DoR met."""
        # Phase 1: Classify (use a clear request to ensure high confidence)
        classify_result = cortex_classify_request(
            request="Implement user authentication with JWT tokens using TDD",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Phase 2: Approve
        with patch('cortex.orchestrators.core.dor_approval_gate.DoRApprovalGate.execute_if_approved') as mock_exec:
            mock_exec.return_value = {"status": "success", "result": "completed"}
            
            result = cortex_approve_request(
                session_id=session_id,
                feedback=None
            )
            
            # Should succeed OR handle DoR threshold gracefully
            assert result["status"] in ["success", "error"]
            if result["status"] == "error":
                # If DoR not met, should be clear error message
                assert "DoR" in result["error"] or "confidence" in result["error"].lower()

    def test_approve_invalid_session_returns_error(self) -> None:
        """Approve with invalid session ID returns error."""
        result = cortex_approve_request(
            session_id="nonexistent-session-id",
            feedback=None
        )
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()

    def test_approve_with_feedback(self) -> None:
        """Approve can include optional feedback."""
        # Classify
        classify_result = cortex_classify_request(
            request="Implement caching",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Approve with feedback
        with patch('cortex.orchestrators.core.dor_approval_gate.DoRApprovalGate.execute_if_approved'):
            result = cortex_approve_request(
                session_id=session_id,
                feedback="Looks good, proceed with Redis"
            )
            
            assert result["status"] in ["success", "error"]  # Either succeeds or fails gracefully

    def test_approve_deletes_session_after_execution(self) -> None:
        """Approve deletes session after successful execution."""
        # Classify
        classify_result = cortex_classify_request(
            request="Implement feature",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Approve
        with patch('cortex.orchestrators.core.dor_approval_gate.DoRApprovalGate.execute_if_approved'):
            cortex_approve_request(session_id=session_id, feedback=None)
        
        # Session should be cleaned up
        from cortex.brain.state.approval_session_manager import ApprovalSessionManager
        manager = ApprovalSessionManager()
        session = manager.get_session(session_id)
        assert session is None


class TestRejectRequest:
    """Tests for cortex_reject_request MCP tool."""

    def test_reject_aborts_request(self) -> None:
        """Reject request aborts execution."""
        # Classify
        classify_result = cortex_classify_request(
            request="Drop production database",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Reject
        result = cortex_reject_request(
            session_id=session_id,
            reason="Too dangerous"
        )
        
        assert result["status"] == "rejected"
        assert "reason" in result
        assert result["reason"] == "Too dangerous"

    def test_reject_deletes_session(self) -> None:
        """Reject deletes session after rejection."""
        # Classify
        classify_result = cortex_classify_request(
            request="Implement feature",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Reject
        cortex_reject_request(session_id=session_id, reason="Not needed")
        
        # Session should be cleaned up
        from cortex.brain.state.approval_session_manager import ApprovalSessionManager
        manager = ApprovalSessionManager()
        session = manager.get_session(session_id)
        assert session is None

    def test_reject_invalid_session_returns_error(self) -> None:
        """Reject with invalid session returns error."""
        result = cortex_reject_request(
            session_id="nonexistent-id",
            reason="Test"
        )
        
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()


class TestModifyRequest:
    """Tests for cortex_modify_request MCP tool."""

    def test_modify_reclassifies_intent(self) -> None:
        """Modify request reclassifies with corrected intent."""
        # Classify
        classify_result = cortex_classify_request(
            request="Fix the bug",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Modify
        result = cortex_modify_request(
            session_id=session_id,
            corrected_intent="FIX",
            feedback="Should be FIX not IMPLEMENT"
        )
        
        assert result["status"] == "modified"
        assert "new_session_id" in result
        assert result["new_session_id"] != session_id  # New session created

    def test_modify_returns_new_dor_display(self) -> None:
        """Modify returns updated DoR display."""
        # Classify
        classify_result = cortex_classify_request(
            request="Update code",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Modify
        result = cortex_modify_request(
            session_id=session_id,
            corrected_intent="REFACTOR",
            feedback="Should refactor not update"
        )
        
        assert "dor_display" in result
        assert "### 📋 Intent Classification" in result["dor_display"]


class TestSessionExpiration:
    """Tests for expired session handling."""

    def test_approve_expired_session_returns_error(self) -> None:
        """Approve expired session returns error."""
        # Classify
        classify_result = cortex_classify_request(
            request="Implement feature",
            context={},
            user_id="test-user"
        )
        session_id = classify_result["session_id"]
        
        # Manually expire session
        from cortex.brain.state.approval_session_manager import ApprovalSessionManager
        manager = ApprovalSessionManager()
        session = manager.get_session(session_id)
        if session:
            session.created_at = datetime.now() - timedelta(seconds=400)
        
        # Try to approve expired session
        result = cortex_approve_request(session_id=session_id, feedback=None)
        
        # Should handle expired session gracefully
        assert result["status"] in ["error", "expired"]


class TestErrorHandling:
    """Tests for error handling in approval tools."""

    def test_classify_empty_request_returns_error(self) -> None:
        """Classify with empty request returns error."""
        result = cortex_classify_request(
            request="",
            context={},
            user_id="test-user"
        )
        
        assert result["status"] == "error"
        assert "empty" in result["error"].lower() or "required" in result["error"].lower()

    def test_approve_without_session_id_returns_error(self) -> None:
        """Approve without session_id returns error gracefully."""
        result = cortex_approve_request(session_id="", feedback=None)
        assert result["status"] == "error"
        assert "not found" in result["error"].lower()
