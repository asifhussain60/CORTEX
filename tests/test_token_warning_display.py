"""
Tests for user-facing token warning display functionality.

Tests both BaseOrchestrator v4.0 and v4.1 implementations of check_token_usage()
with user_message support.

Author: Asif Hussain
Created: 2026-01-02
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from orchestration_4_0.base.base_orchestrator import BaseOrchestrator
from orchestration_4_0.base.phase_manager import PhaseManager
from orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from database.planning_state_db import PlanningStateDB


class TestTokenWarningDisplayV40:
    """Test token warning display in BaseOrchestrator v4.0."""
    
    def test_check_token_usage_below_threshold(self):
        """Test token check when below threshold - no warning."""
        
        class MockOrch(BaseOrchestrator):
            def execute(self, user_request: str, **kwargs):
                pass
            def _setup(self, context: dict):
                pass
            def _teardown(self):
                pass
            def _register_phases(self):
                pass
            def _execute_phase(self, phase_name: str, context: dict):
                pass
        
        orch = MockOrch(
            name="test_orch",
            config={"token_warning_threshold": 80000}
        )
        
        # Add 2 phases (2000 tokens < 80000 threshold)
        orch.phase_manager.register_phase("Phase 1", "Phase 1 description")
        orch.phase_manager.start_phase("Phase 1")
        orch.phase_manager.complete_phase("Phase 1")
        
        orch.phase_manager.register_phase("Phase 2", "Phase 2 description")
        orch.phase_manager.start_phase("Phase 2")
        orch.phase_manager.complete_phase("Phase 2")
        
        # Check token usage
        result = orch.check_token_usage()
        
        # Assertions
        assert result['estimated_tokens'] == 2000
        assert result['threshold'] == 80000
        assert result['should_warn'] is False
        assert result['percentage'] == 2.5
        assert result['user_message'] is None
    
    def test_check_token_usage_at_threshold(self):
        """Test token check when at threshold - warning displayed."""
        
        class MockOrch(BaseOrchestrator):
            def execute(self, user_request: str, **kwargs):
                pass
            def _setup(self, context: dict):
                pass
            def _teardown(self):
                pass
            def _register_phases(self):
                pass
            def _execute_phase(self, phase_name: str, context: dict):
                pass
        
        orch = MockOrch(
            name="test_orch",
            config={"token_warning_threshold": 5000}
        )
        
        # Add 5 phases (5000 tokens = 5000 threshold)
        for i in range(5):
            phase_name = f"Phase {i+1}"
            orch.phase_manager.register_phase(phase_name, f"Description for Phase {i+1}")
            orch.phase_manager.start_phase(phase_name)
            orch.phase_manager.complete_phase(phase_name)
        
        # Check token usage
        result = orch.check_token_usage()
        
        # Assertions
        assert result['estimated_tokens'] == 5000
        assert result['threshold'] == 5000
        assert result['should_warn'] is True
        assert result['percentage'] == 100.0
        assert result['user_message'] is not None
        
        # Verify user message content
        user_msg = result['user_message']
        assert '⚠️ **TOKEN WARNING**' in user_msg
        assert '5,000 tokens' in user_msg
        assert '100.0%' in user_msg
        assert 'tracking/CONTINUATION-PROMPT.md' in user_msg
        assert 'session handoff' in user_msg
    
    def test_check_token_usage_above_threshold(self):
        """Test token check when exceeding threshold."""
        
        class MockOrch(BaseOrchestrator):
            def execute(self, user_request: str, **kwargs):
                pass
            def _setup(self, context: dict):
                pass
            def _teardown(self):
                pass
            def _register_phases(self):
                pass
            def _execute_phase(self, phase_name: str, context: dict):
                pass
        
        orch = MockOrch(
            name="test_orch",
            config={"token_warning_threshold": 3000}
        )
        
        # Add 5 phases (5000 tokens > 3000 threshold)
        for i in range(5):
            phase_name = f"Phase {i+1}"
            orch.phase_manager.register_phase(phase_name, f"Description for Phase {i+1}")
            orch.phase_manager.start_phase(phase_name)
            orch.phase_manager.complete_phase(phase_name)
        
        # Check token usage
        result = orch.check_token_usage()
        
        # Assertions
        assert result['estimated_tokens'] == 5000
        assert result['threshold'] == 3000
        assert result['should_warn'] is True
        assert result['percentage'] == 166.7
        assert result['user_message'] is not None


class TestTokenWarningDisplayV41:
    """Test token warning display in BaseOrchestrator v4.1."""
    
    def test_check_token_usage_no_plan(self):
        """Test token check when no plan context available."""
        
        class MockOrch(BaseOrchestratorV4_1):
            def execute(self, user_request: str, **kwargs):
                pass
        
        # Create mock database
        mock_db = Mock(spec=PlanningStateDB)
        
        # Create orchestrator without plan_id
        config_path = Path(__file__).parent.parent / "cortex-brain" / "manifests" / "orchestrators" / "planning-system-5.0-manifest.yaml"
        
        # Skip if manifest doesn't exist
        if not config_path.exists():
            pytest.skip("Manifest not found")
        
        orch = MockOrch(
            config_path=str(config_path),
            state_db=mock_db,
            plan_id=None
        )
        
        # Check token usage
        result = orch.check_token_usage()
        
        # Assertions
        assert result['estimated_tokens'] == 0
        assert result['should_warn'] is False
        assert result['user_message'] is None
    
    def test_check_token_usage_with_completed_phases(self):
        """Test token check with completed phases from database."""
        
        class MockOrch(BaseOrchestratorV4_1):
            def execute(self, user_request: str, **kwargs):
                pass
        
        # Create mock database
        mock_db = Mock(spec=PlanningStateDB)
        
        # Mock get_plan_progress to return completed phases
        mock_db.get_plan_progress.return_value = [
            {'phase_id': 'phase_1', 'status': 'completed'},
            {'phase_id': 'phase_2', 'status': 'completed'},
            {'phase_id': 'phase_3', 'status': 'in_progress'},
        ]
        
        config_path = Path(__file__).parent.parent / "cortex-brain" / "manifests" / "orchestrators" / "planning-system-5.0-manifest.yaml"
        
        if not config_path.exists():
            pytest.skip("Manifest not found")
        
        orch = MockOrch(
            config_path=str(config_path),
            state_db=mock_db,
            plan_id="test_plan_123"
        )
        
        # Set low threshold for testing
        orch.token_warning_threshold = 1500
        
        # Check token usage
        result = orch.check_token_usage()
        
        # Assertions (2 completed phases × 1000 = 2000 tokens)
        assert result['estimated_tokens'] == 2000
        assert result['threshold'] == 1500
        assert result['should_warn'] is True
        assert result['percentage'] == 133.3
        assert result['user_message'] is not None
    
    def test_user_message_formatting(self):
        """Test user message has proper formatting with emojis and markdown."""
        
        class MockOrch(BaseOrchestratorV4_1):
            def execute(self, user_request: str, **kwargs):
                pass
        
        mock_db = Mock(spec=PlanningStateDB)
        
        # Mock 10 completed phases to exceed threshold
        mock_db.get_plan_progress.return_value = [
            {'phase_id': f'phase_{i}', 'status': 'completed'}
            for i in range(10)
        ]
        
        config_path = Path(__file__).parent.parent / "cortex-brain" / "manifests" / "orchestrators" / "planning-system-5.0-manifest.yaml"
        
        if not config_path.exists():
            pytest.skip("Manifest not found")
        
        orch = MockOrch(
            config_path=str(config_path),
            state_db=mock_db,
            plan_id="test_plan_456"
        )
        
        orch.token_warning_threshold = 8000
        
        # Check token usage
        result = orch.check_token_usage()
        
        # Verify message structure
        user_msg = result['user_message']
        
        assert '⚠️ **TOKEN WARNING**' in user_msg
        assert '10,000 tokens' in user_msg  # Formatted with comma
        assert '8,000 threshold' in user_msg  # Formatted with comma
        assert '125.0%' in user_msg
        assert '📋 **Continuation prompt updated**' in user_msg
        assert '💡 **Recommendation**' in user_msg
        assert '`tracking/CONTINUATION-PROMPT.md`' in user_msg
        assert 'session handoff' in user_msg


class TestTokenWarningIntegration:
    """Integration tests for token warning in orchestrator execution."""
    
    def test_planning_orchestrator_includes_token_warning(self):
        """Test that PlanningOrchestratorV5 includes token warning in result."""
        
        from orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
        
        # Create mock database
        mock_db = Mock(spec=PlanningStateDB)
        mock_db.create_plan.return_value = "test_plan_789"
        mock_db.get_plan_progress.return_value = [
            {'phase_id': f'phase_{i}', 'status': 'completed'}
            for i in range(100)  # Simulate many phases
        ]
        
        config_path = Path(__file__).parent.parent / "cortex-brain" / "manifests" / "orchestrators" / "planning-system-5.0-manifest.yaml"
        
        if not config_path.exists():
            pytest.skip("Manifest not found")
        
        # Create orchestrator with low threshold
        orch = PlanningOrchestratorV5(
            config_path=str(config_path),
            state_db=mock_db
        )
        orch.token_warning_threshold = 5000
        
        # Mock phase execution to prevent actual work
        orch._discover_context = Mock(return_value=[])
        orch._analyze_architecture = Mock(return_value=[])
        orch._generate_plan = Mock(return_value=[])
        orch._create_folder_structure = Mock(return_value=[])
        orch._validate_plan = Mock(return_value=[])
        
        # Execute
        result = orch.execute("create a plan for user auth")
        
        # Verify token warning in result message
        assert result.success
        assert 'token_status' in result.data
        
        # If warning triggered, message should contain it
        token_status = result.data['token_status']
        if token_status['should_warn']:
            assert '⚠️ **TOKEN WARNING**' in result.message


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
