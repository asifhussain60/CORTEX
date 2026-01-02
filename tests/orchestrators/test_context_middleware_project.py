"""
Tests for CrossSessionContextMiddleware with Project Tracking (Option B).

Tests both orchestrator-level and project-level continuation detection.
"""

import pytest
from unittest.mock import Mock, MagicMock
from src.orchestrators.context_middleware import CrossSessionContextMiddleware


@pytest.fixture
def mock_session_manager():
    """Create mock SessionManager."""
    manager = Mock()
    manager.get_recent_session_context = Mock(return_value=[])
    return manager


@pytest.fixture
def mock_project_tracker():
    """Create mock ProjectTracker."""
    tracker = Mock()
    tracker.get_lightweight_project_context = Mock(return_value=None)
    return tracker


@pytest.fixture
def middleware(mock_session_manager, mock_project_tracker):
    """Create middleware with mocked dependencies."""
    return CrossSessionContextMiddleware(
        session_manager=mock_session_manager,
        project_tracker=mock_project_tracker
    )


class TestProjectLevelContinuation:
    """Test project-level continuation detection and context injection."""
    
    def test_continuation_with_active_project(self, middleware, mock_session_manager, mock_project_tracker):
        """Test continuation pattern triggers project context injection."""
        # No orchestrator sessions
        mock_session_manager.get_recent_session_context.return_value = []
        
        # Active project exists
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5-refactor",
            "plan_name": "CORTEX v5 Holistic Refactor",
            "current_phase": "Phase 5",
            "current_task": "Task 5.1",
            "last_completed": "Phase 5.1a",
            "progress": 40,
            "next_action": "/CORTEX Plan ADO Orchestrator v2 Migration",
            "orchestrator": "planning_v5"
        }
        
        context = middleware.enrich_context("continue", {})
        
        assert context['continuation_detected'] is True
        assert context['continuation_type'] == 'active_project'
        assert context['context_source'] == 'tier1_project_tracker'
        assert 'active_project' in context
        assert context['active_project']['project_id'] == "cortex-v5-refactor"
        assert context['active_project']['progress'] == 40
    
    def test_get_last_orchestrator_from_project(self, middleware, mock_session_manager, mock_project_tracker):
        """Test get_last_orchestrator returns orchestrator from active project."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "test-project",
            "plan_name": "Test",
            "progress": 50,
            "orchestrator": "planning_v5"
        }
        
        orchestrator = middleware.get_last_orchestrator("continue")
        
        assert orchestrator == "planning_v5"
    
    def test_continuation_project_multiple_patterns(self, middleware, mock_session_manager, mock_project_tracker):
        """Test project continuation works with all continuation patterns."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "test",
            "plan_name": "Test",
            "progress": 50,
            "orchestrator": "planning_v5"
        }
        
        patterns = [
            "continue",
            "resume",
            "keep going",
            "next phase",
            "proceed",
            "continue with",
            "resume execution",
            "next"
        ]
        
        for pattern in patterns:
            context = middleware.enrich_context(pattern, {})
            assert context['continuation_detected'] is True
            assert context['continuation_type'] == 'active_project'


class TestOrchestratorPriority:
    """Test that orchestrator sessions have priority over projects."""
    
    def test_orchestrator_session_overrides_project(self, middleware, mock_session_manager, mock_project_tracker):
        """Test orchestrator session takes priority when both exist."""
        # Both orchestrator session and active project exist
        mock_session_manager.get_recent_session_context.return_value = [{
            "session_id": "session-123",
            "orchestrator": "tdd_master",
            "intent": "run tests",
            "artifacts": ["test_results.json"],
            "timestamp": "2026-01-02T10:00:00Z"
        }]
        
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5-refactor",
            "plan_name": "CORTEX v5",
            "progress": 40,
            "orchestrator": "planning_v5"
        }
        
        context = middleware.enrich_context("continue", {})
        
        # Should use orchestrator session, not project
        assert context['continuation_type'] == 'orchestrator_session'
        assert 'recent_activity' in context
        assert 'active_project' not in context
    
    def test_get_last_orchestrator_prefers_session(self, middleware, mock_session_manager, mock_project_tracker):
        """Test get_last_orchestrator returns session orchestrator when both exist."""
        mock_session_manager.get_recent_session_context.return_value = [{
            "orchestrator": "tdd_master",
            "intent": "run tests"
        }]
        
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "orchestrator": "planning_v5"
        }
        
        orchestrator = middleware.get_last_orchestrator("continue")
        
        # Should return TDD, not Planning
        assert orchestrator == "tdd_master"


class TestNoContinuationContext:
    """Test behavior when no continuation context exists."""
    
    def test_continuation_no_session_no_project(self, middleware, mock_session_manager, mock_project_tracker):
        """Test continuation pattern with no session or project returns empty context."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = None
        
        context = middleware.enrich_context("continue", {})
        
        # Should return empty context (no enrichment)
        assert 'continuation_detected' not in context
        assert 'recent_activity' not in context
        assert 'active_project' not in context
    
    def test_get_last_orchestrator_no_context(self, middleware, mock_session_manager, mock_project_tracker):
        """Test get_last_orchestrator returns None when no context."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = None
        
        orchestrator = middleware.get_last_orchestrator("continue")
        
        assert orchestrator is None
    
    def test_non_continuation_pattern_no_enrichment(self, middleware):
        """Test non-continuation patterns don't trigger enrichment."""
        context = middleware.enrich_context("plan user authentication", {})
        
        assert 'continuation_detected' not in context
        assert 'recent_activity' not in context
        assert 'active_project' not in context


class TestErrorHandling:
    """Test error handling for database failures."""
    
    def test_session_manager_error_fallback_to_project(self, middleware, mock_session_manager, mock_project_tracker):
        """Test that session manager error doesn't prevent project context."""
        # Session manager throws exception
        mock_session_manager.get_recent_session_context.side_effect = Exception("DB error")
        
        # But project tracker works
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "test",
            "plan_name": "Test",
            "progress": 50,
            "orchestrator": "planning_v5"
        }
        
        context = middleware.enrich_context("continue", {})
        
        # Should still get project context
        assert context['continuation_detected'] is True
        assert context['continuation_type'] == 'active_project'
    
    def test_project_tracker_error_graceful_failure(self, middleware, mock_session_manager, mock_project_tracker):
        """Test project tracker error returns empty context."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.side_effect = Exception("DB error")
        
        context = middleware.enrich_context("continue", {})
        
        # Should return empty context (no crash)
        assert 'continuation_detected' not in context
    
    def test_both_errors_graceful_failure(self, middleware, mock_session_manager, mock_project_tracker):
        """Test both errors still returns empty context without crashing."""
        mock_session_manager.get_recent_session_context.side_effect = Exception("Session DB error")
        mock_project_tracker.get_lightweight_project_context.side_effect = Exception("Project DB error")
        
        context = middleware.enrich_context("continue", {})
        
        # Should return empty context (no crash)
        assert 'continuation_detected' not in context


class TestTokenEfficiency:
    """Test token efficiency for project context."""
    
    def test_project_context_under_token_budget(self, middleware, mock_session_manager, mock_project_tracker):
        """Test project context stays under 200 token budget."""
        import json
        
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5-holistic-refactor-very-long-name",
            "plan_name": "CORTEX v5 Holistic Refactor with Extended Description",
            "current_phase": "Phase 5: Migration Planning",
            "current_task": "Task 5.1: Generate ADO Orchestrator v2 Migration Plan",
            "last_completed": "Phase 5.1a: ADO Conversational Wizard Enhancement",
            "progress": 40,
            "next_action": "/CORTEX Plan ADO Orchestrator v2 Migration with wizard architecture",
            "orchestrator": "planning_v5"
        }
        
        context = middleware.enrich_context("continue", {})
        
        # Estimate tokens in active_project
        project_json = json.dumps(context['active_project'])
        estimated_tokens = len(project_json) // 4  # 1 token ≈ 4 chars
        
        assert estimated_tokens < 200, f"Project context uses {estimated_tokens} tokens (budget: 200)"
    
    def test_get_context_token_count_project(self, middleware):
        """Test token counting includes project context."""
        context_with_project = {
            'active_project': {
                "project_id": "test",
                "plan_name": "Test Project",
                "progress": 50,
                "orchestrator": "planning_v5"
            }
        }
        
        token_count = middleware.get_context_token_count(context_with_project)
        
        # Should return estimated token count
        assert token_count > 0
        assert token_count < 100  # Should be well under budget


class TestExistingContextPreservation:
    """Test that existing context is preserved when enriching."""
    
    def test_project_context_preserves_existing(self, middleware, mock_session_manager, mock_project_tracker):
        """Test project enrichment preserves existing context keys."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "test",
            "plan_name": "Test",
            "progress": 50,
            "orchestrator": "planning_v5"
        }
        
        existing = {
            "user_workspace": "/workspace",
            "custom_flag": True
        }
        
        context = middleware.enrich_context("continue", existing)
        
        # Should preserve existing keys
        assert context['user_workspace'] == "/workspace"
        assert context['custom_flag'] is True
        
        # Should add new keys
        assert 'active_project' in context
        assert context['continuation_detected'] is True
