"""
Tests for Cross-Session Context Middleware.

Part of CORTEX v5 Phase 4.5: Cross-session context awareness testing.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.orchestrators.context_middleware import CrossSessionContextMiddleware


class TestContinuationDetection:
    """Test continuation pattern matching."""
    
    def test_continuation_patterns(self):
        """Test all continuation patterns are detected."""
        middleware = CrossSessionContextMiddleware()
        
        # Should detect
        assert middleware._is_continuation("continue")
        assert middleware._is_continuation("resume")
        assert middleware._is_continuation("keep going")
        assert middleware._is_continuation("next phase")
        assert middleware._is_continuation("proceed")
        assert middleware._is_continuation("continue with the plan")
        assert middleware._is_continuation("resume execution")
        assert middleware._is_continuation("next")
        
        # Case insensitive
        assert middleware._is_continuation("CONTINUE")
        assert middleware._is_continuation("Resume")
        assert middleware._is_continuation("KEEP GOING")
    
    def test_non_continuation_patterns(self):
        """Test non-continuation inputs are not detected."""
        middleware = CrossSessionContextMiddleware()
        
        # Should NOT detect
        assert not middleware._is_continuation("plan user auth")
        assert not middleware._is_continuation("run tests")
        assert not middleware._is_continuation("ado story")
        assert not middleware._is_continuation("help")
        assert not middleware._is_continuation("create feature X")


class TestContextEnrichment:
    """Test context enrichment with Tier 1 data."""
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_enrichment_with_continuation(self, mock_session_mgr_class):
        """Test context enrichment when continuation detected."""
        mock_session_mgr = MagicMock()
        mock_session_mgr.get_recent_session_context.return_value = [
            {
                "session_id": "session-123",
                "orchestrator": "planning_v5",
                "intent": "plan user authentication",
                "artifacts": ["plan-001", "plan-002"],
                "timestamp": "2026-01-02T10:15:00Z"
            }
        ]
        
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        context = middleware.enrich_context("continue", {})
        
        # Verify enrichment
        assert "recent_activity" in context
        assert context["continuation_detected"] is True
        assert context["context_source"] == "tier1_working_memory"
        assert len(context["recent_activity"]) == 1
        assert context["recent_activity"][0]["orchestrator"] == "planning_v5"
        
        # Verify Tier 1 query
        mock_session_mgr.get_recent_session_context.assert_called_once_with(limit=3)
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_no_enrichment_without_continuation(self, mock_session_mgr_class):
        """Test context unchanged when no continuation detected."""
        mock_session_mgr = MagicMock()
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        original = {"existing": "data"}
        context = middleware.enrich_context("plan feature X", original)
        
        # Should be unchanged
        assert context == original
        assert "recent_activity" not in context
        
        # Tier 1 should not be queried
        mock_session_mgr.get_recent_session_context.assert_not_called()
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_enrichment_with_empty_sessions(self, mock_session_mgr_class):
        """Test enrichment when no recent sessions exist."""
        mock_session_mgr = MagicMock()
        mock_session_mgr.get_recent_session_context.return_value = []
        
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        context = middleware.enrich_context("continue", {})
        
        # Should not enrich if no sessions
        assert "recent_activity" not in context
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_enrichment_handles_tier1_errors(self, mock_session_mgr_class):
        """Test enrichment handles Tier 1 query errors gracefully."""
        mock_session_mgr = MagicMock()
        mock_session_mgr.get_recent_session_context.side_effect = Exception("DB error")
        
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        # Should not crash, returns context unchanged
        context = middleware.enrich_context("continue", {})
        assert "recent_activity" not in context


class TestLastOrchestratorRetrieval:
    """Test get_last_orchestrator convenience method."""
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_get_last_orchestrator_with_continuation(self, mock_session_mgr_class):
        """Test retrieving last orchestrator from recent sessions."""
        mock_session_mgr = MagicMock()
        mock_session_mgr.get_recent_session_context.return_value = [
            {
                "session_id": "session-456",
                "orchestrator": "ado_orchestrator",
                "intent": "ado story for API",
                "artifacts": ["story-001"],
                "timestamp": "2026-01-02T14:30:00Z"
            }
        ]
        
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        last_orch = middleware.get_last_orchestrator("resume")
        
        assert last_orch == "ado_orchestrator"
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_get_last_orchestrator_without_continuation(self, mock_session_mgr_class):
        """Test returns None when no continuation detected."""
        mock_session_mgr = MagicMock()
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        last_orch = middleware.get_last_orchestrator("plan database refactor")
        
        assert last_orch is None


class TestTokenEfficiency:
    """Test token counting for efficiency validation."""
    
    @patch('src.tier1.sessions.session_manager.SessionManager')
    def test_token_count_estimation(self, mock_session_mgr_class):
        """Test token count estimation for context."""
        mock_session_mgr = MagicMock()
        mock_session_mgr.get_recent_session_context.return_value = [
            {
                "session_id": "session-789",
                "orchestrator": "planning_v5",
                "intent": "plan user auth",
                "artifacts": ["plan-001"],
                "timestamp": "2026-01-02T10:00:00Z"
            },
            {
                "session_id": "session-788",
                "orchestrator": "ado_orchestrator",
                "intent": "ado story",
                "artifacts": ["story-001"],
                "timestamp": "2026-01-02T09:00:00Z"
            }
        ]
        
        middleware = CrossSessionContextMiddleware(session_manager=mock_session_mgr)
        
        context = middleware.enrich_context("continue", {})
        token_count = middleware.get_context_token_count(context)
        
        # Should be lightweight (<200 tokens)
        assert token_count > 0
        assert token_count < 200, f"Token count too high: {token_count}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
