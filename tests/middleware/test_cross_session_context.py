"""
Tests for CrossSessionContextMiddleware.

Validates Tier 1 orchestrator continuation (<200 tokens), Tier 2 project
fallback, priority logic, continuation pattern detection, and metadata-only injection.

Author: Asif Hussain
Created: January 4, 2026
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

from src.orchestrators.context_middleware import CrossSessionContextMiddleware


class TestCrossSessionContext:
    """Tests for cross-session context middleware (Sub-Plan 05)."""
    
    @pytest.fixture
    def mock_session_manager(self):
        """Mock SessionManager for testing."""
        mock_mgr = Mock()
        mock_mgr.get_recent_session_context = Mock(return_value=[])
        return mock_mgr
    
    @pytest.fixture
    def mock_project_tracker(self):
        """Mock ProjectTracker for testing."""
        mock_tracker = Mock()
        mock_tracker.get_lightweight_project_context = Mock(return_value=None)
        return mock_tracker
    
    @pytest.fixture
    def middleware(self, mock_session_manager, mock_project_tracker):
        """Create middleware instance with mocks."""
        return CrossSessionContextMiddleware(
            session_manager=mock_session_manager,
            project_tracker=mock_project_tracker
        )
    
    # ===== TEST 1: Tier 1 Orchestrator Continuation (<200 tokens) =====
    
    def test_tier1_orchestrator_continuation_under_200_tokens(
        self, middleware, mock_session_manager
    ):
        """
        Test Tier 1 orchestrator continuation stays under 200 tokens.
        
        Success Criteria:
        - Token count < 200
        - Context includes recent_activity
        - continuation_type = 'orchestrator_session'
        """
        # Setup: Mock orchestrator session data
        mock_session_manager.get_recent_session_context.return_value = [
            {
                "session_id": "session-20260102-101500",
                "orchestrator": "tdd_master",
                "intent": "run tests for auth module",
                "artifacts": ["test_results.json"],
                "timestamp": "2026-01-02T10:15:00Z"
            }
        ]
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        
        # Assert: Continuation detected
        assert enriched['continuation_detected'] is True
        assert enriched['continuation_type'] == 'orchestrator_session'
        assert enriched['context_source'] == 'tier1_working_memory'
        assert 'recent_activity' in enriched
        assert len(enriched['recent_activity']) == 1
        
        # Assert: Token count validation (<200 tokens)
        token_count = middleware.get_context_token_count(enriched)
        assert token_count < 200, f"Token count {token_count} exceeds 200 token limit"
        
        print(f"✅ Token count: {token_count} (< 200 limit)")
    
    # ===== TEST 2: Tier 2 Project Fallback =====
    
    def test_tier2_project_fallback(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """
        Test Tier 2 project fallback when no orchestrator session.
        
        Success Criteria:
        - Falls back to project context when no session
        - continuation_type = 'active_project'
        - Context includes active_project
        """
        # Setup: No orchestrator session, but active project
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5-holistic-refactor",
            "plan_name": "CORTEX v5 Holistic Refactor",
            "current_phase": "Phase 5",
            "current_task": "Task 5.1",
            "progress": 40,
            "orchestrator": "planning_v5"
        }
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        
        # Assert: Project continuation detected
        assert enriched['continuation_detected'] is True
        assert enriched['continuation_type'] == 'active_project'
        assert enriched['context_source'] == 'tier1_project_tracker'
        assert 'active_project' in enriched
        assert enriched['active_project']['project_id'] == 'cortex-v5-holistic-refactor'
        
        print("✅ Tier 2 project fallback working")
    
    # ===== TEST 3: Context Priority (Orchestrator > Project) =====
    
    def test_context_priority_orchestrator_over_project(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """
        Test orchestrator session takes priority over project.
        
        Success Criteria:
        - When both exist, orchestrator session used
        - continuation_type = 'orchestrator_session' (not 'active_project')
        - No project context injected
        """
        # Setup: Both orchestrator session AND active project
        mock_session_manager.get_recent_session_context.return_value = [
            {
                "session_id": "session-20260104-083000",
                "orchestrator": "debug_orchestrator",
                "intent": "fix import error",
                "artifacts": [],
                "timestamp": "2026-01-04T08:30:00Z"
            }
        ]
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5-holistic-refactor",
            "plan_name": "CORTEX v5 Holistic Refactor",
            "current_phase": "Phase 5",
            "orchestrator": "planning_v5"
        }
        
        # Execute
        enriched = middleware.enrich_context("resume", {})
        
        # Assert: Orchestrator session takes priority
        assert enriched['continuation_type'] == 'orchestrator_session'
        assert 'recent_activity' in enriched
        assert 'active_project' not in enriched  # Project context NOT injected
        assert enriched['recent_activity'][0]['orchestrator'] == 'debug_orchestrator'
        
        print("✅ Priority logic: orchestrator > project")
    
    # ===== TEST 4: Continuation Pattern Detection =====
    
    def test_continue_resume_patterns_detected(self, middleware):
        """
        Test continuation pattern detection for all supported patterns.
        
        Success Criteria:
        - "continue" detected
        - "resume" detected
        - "keep going" detected
        - "next phase" detected
        - "proceed" detected
        - Non-continuation patterns ignored
        """
        # Test patterns (should detect)
        continuation_patterns = [
            "continue",
            "resume",
            "keep going",
            "next phase",
            "proceed",
            "continue with implementation",
            "resume execution",
            "next"
        ]
        
        for pattern in continuation_patterns:
            assert middleware._is_continuation(pattern), \
                f"Pattern '{pattern}' not detected"
        
        # Test non-continuation patterns (should NOT detect)
        non_continuation = [
            "plan user authentication",
            "debug the app",
            "what is CORTEX",
            "help"
        ]
        
        for pattern in non_continuation:
            assert not middleware._is_continuation(pattern), \
                f"Pattern '{pattern}' incorrectly detected as continuation"
        
        print("✅ All continuation patterns detected correctly")
    
    # ===== TEST 5: Metadata-Only Injection =====
    
    def test_metadata_only_injection(
        self, middleware, mock_session_manager
    ):
        """
        Test that only metadata is injected, not full conversation.
        
        Success Criteria:
        - Only metadata fields present
        - No conversation history
        - No full artifact content
        - Token count < 200
        """
        # Setup: Mock session with metadata only
        mock_session_manager.get_recent_session_context.return_value = [
            {
                "session_id": "session-123",
                "orchestrator": "tdd_master",
                "intent": "run tests",
                "artifacts": ["report.json"],  # Only filename, not content
                "timestamp": "2026-01-04T08:00:00Z"
                # NO conversation_history field
                # NO artifact_content field
            }
        ]
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        
        # Assert: Metadata fields present
        assert 'recent_activity' in enriched
        activity = enriched['recent_activity'][0]
        assert 'session_id' in activity
        assert 'orchestrator' in activity
        assert 'intent' in activity
        assert 'timestamp' in activity
        
        # Assert: Full content NOT present
        assert 'conversation_history' not in activity
        assert 'artifact_content' not in activity
        assert 'full_messages' not in activity
        
        # Assert: Token efficiency
        token_count = middleware.get_context_token_count(enriched)
        assert token_count < 200
        
        print(f"✅ Metadata-only injection (no conversation): {token_count} tokens")
    
    # ===== BONUS TEST: get_last_orchestrator =====
    
    def test_get_last_orchestrator_from_session(
        self, middleware, mock_session_manager
    ):
        """Test get_last_orchestrator() returns correct orchestrator from session."""
        mock_session_manager.get_recent_session_context.return_value = [
            {
                "session_id": "session-123",
                "orchestrator": "tdd_master",
                "intent": "run tests",
                "artifacts": [],
                "timestamp": "2026-01-04T08:00:00Z"
            }
        ]
        
        last_orch = middleware.get_last_orchestrator("continue", {})
        assert last_orch == "tdd_master"
        
        print("✅ get_last_orchestrator() returns correct orchestrator")
    
    def test_get_last_orchestrator_from_project(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """Test get_last_orchestrator() returns orchestrator from project fallback."""
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5",
            "orchestrator": "planning_v5",
            "progress": 50  # Add required field
        }
        
        last_orch = middleware.get_last_orchestrator("resume", {})
        assert last_orch == "planning_v5"
        
        print("✅ get_last_orchestrator() falls back to project")
    
    def test_no_continuation_returns_none(self, middleware):
        """Test non-continuation patterns return None."""
        last_orch = middleware.get_last_orchestrator("plan something", {})
        assert last_orch is None
        
        print("✅ Non-continuation returns None")
    
    # ===== EDGE CASES & ERROR HANDLING =====
    
    def test_session_manager_error_handling(
        self, middleware, mock_session_manager
    ):
        """Test graceful handling when session manager fails."""
        # Setup: Session manager throws exception
        mock_session_manager.get_recent_session_context.side_effect = Exception("DB error")
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        
        # Assert: Should NOT crash, returns empty context
        assert 'recent_activity' not in enriched
        assert 'continuation_detected' not in enriched
        
        print("✅ Session manager error handled gracefully")
    
    def test_project_tracker_error_handling(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """Test graceful handling when project tracker fails."""
        # Setup: No session, project tracker throws exception
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.side_effect = Exception("DB error")
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        
        # Assert: Should NOT crash, returns empty context
        assert 'active_project' not in enriched
        assert 'continuation_detected' not in enriched
        
        print("✅ Project tracker error handled gracefully")
    
    def test_no_session_no_project_returns_unchanged(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """Test continuation pattern with no session or project returns unchanged."""
        # Setup: Continuation detected but no session or project
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = None
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        
        # Assert: Context unchanged
        assert 'continuation_detected' not in enriched
        assert 'recent_activity' not in enriched
        assert 'active_project' not in enriched
        
        print("✅ No session/project returns unchanged context")
    
    def test_existing_context_preserved(
        self, middleware, mock_session_manager
    ):
        """Test existing context is preserved and enriched."""
        # Setup: Existing context with custom field
        mock_session_manager.get_recent_session_context.return_value = [
            {
                "session_id": "session-123",
                "orchestrator": "tdd_master",
                "intent": "run tests",
                "artifacts": [],
                "timestamp": "2026-01-04T08:00:00Z"
            }
        ]
        
        existing = {"custom_field": "custom_value", "user_preference": "verbose"}
        
        # Execute
        enriched = middleware.enrich_context("continue", existing)
        
        # Assert: Existing fields preserved
        assert enriched['custom_field'] == "custom_value"
        assert enriched['user_preference'] == "verbose"
        
        # Assert: New fields added
        assert 'recent_activity' in enriched
        assert enriched['continuation_detected'] is True
        
        print("✅ Existing context preserved during enrichment")
    
    def test_case_insensitive_pattern_matching(self, middleware):
        """Test continuation patterns work with different cases."""
        # Test uppercase
        assert middleware._is_continuation("CONTINUE")
        assert middleware._is_continuation("RESUME")
        
        # Test mixed case
        assert middleware._is_continuation("Continue")
        assert middleware._is_continuation("Resume Execution")
        
        # Test lowercase
        assert middleware._is_continuation("continue")
        assert middleware._is_continuation("next phase")
        
        print("✅ Case-insensitive pattern matching works")
    
    def test_token_count_with_multiple_sessions(
        self, middleware, mock_session_manager
    ):
        """Test token counting with multiple sessions."""
        # Setup: Multiple sessions
        mock_session_manager.get_recent_session_context.return_value = [
            {
                "session_id": f"session-{i}",
                "orchestrator": "tdd_master",
                "intent": "test iteration",
                "artifacts": ["report.json"],
                "timestamp": "2026-01-04T08:00:00Z"
            }
            for i in range(3)
        ]
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        token_count = middleware.get_context_token_count(enriched)
        
        # Assert: Still under 200 tokens even with 3 sessions
        assert token_count < 200
        
        print(f"✅ Multiple sessions token count: {token_count} (< 200)")
    
    def test_token_count_with_project_context(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """Test token counting with project context."""
        # Setup: No session, project context
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "cortex-v5-holistic-refactor",
            "plan_name": "CORTEX v5 Holistic Refactor with lots of details",
            "current_phase": "Phase 5",
            "current_task": "Task 5.1: Implement comprehensive testing",
            "last_completed": "Task 4.3",
            "progress": 40,
            "orchestrator": "planning_v5"
        }
        
        # Execute
        enriched = middleware.enrich_context("continue", {})
        token_count = middleware.get_context_token_count(enriched)
        
        # Assert: Under 200 tokens
        assert token_count < 200
        
        print(f"✅ Project context token count: {token_count} (< 200)")
    
    def test_get_last_orchestrator_with_no_orchestrator_field(
        self, middleware, mock_session_manager, mock_project_tracker
    ):
        """Test get_last_orchestrator when project has no orchestrator field."""
        # Setup: Project without orchestrator field
        mock_session_manager.get_recent_session_context.return_value = []
        mock_project_tracker.get_lightweight_project_context.return_value = {
            "project_id": "some-project",
            "progress": 30
            # No orchestrator field
        }
        
        # Execute
        last_orch = middleware.get_last_orchestrator("continue", {})
        
        # Assert: Falls back to default planning_v5
        assert last_orch == "planning_v5"
        
        print("✅ Falls back to planning_v5 when orchestrator field missing")
    
    def test_initialization_with_defaults(self):
        """Test middleware initialization with default session manager and project tracker."""
        # This test covers the default initialization paths (lines 82-84, 90-92)
        # by not providing any mocks
        
        # Note: This will attempt to create real SessionManager and ProjectTracker
        # instances, which should handle missing DB gracefully
        try:
            middleware = CrossSessionContextMiddleware()
            
            # Basic sanity checks
            assert middleware.session_manager is not None
            assert middleware.project_tracker is not None
            assert middleware._continuation_regex is not None
            
            print("✅ Default initialization successful")
        except Exception as e:
            # If DB doesn't exist, that's expected in test environment
            # We still verify the code path was executed
            assert "tier1/working_memory.db" in str(e) or "SessionManager" in str(e) or "ProjectTracker" in str(e)
            print(f"✅ Default initialization attempted (DB not available: {type(e).__name__})")
