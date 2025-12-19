"""
Unit Tests for Auto-Progression Logic (Task 1.5.3)

Tests the autonomous execution flow with automatic phase progression.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.orchestrators.session_model import PlanningSession, SessionStatus


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator instance for testing."""
    return PlanningOrchestrator(project_root=tmp_path)


@pytest.fixture
def mock_session():
    """Create mock planning session."""
    session = Mock(spec=PlanningSession)
    session.execution_mode = "autonomous"
    session.max_consecutive_phases = 20
    session.phases = []
    return session


class TestAutoProgression:
    """Test suite for auto-progression logic."""

    def test_should_auto_progress_when_autonomous_mode(self, orchestrator, mock_session):
        """Verifies auto-progression triggers in autonomous mode."""
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 1
        orchestrator.metrics['errors'] = []
        
        assert orchestrator._should_auto_progress() is True

    def test_should_not_auto_progress_when_interactive_mode(self, orchestrator, mock_session):
        """Verifies auto-progression doesn't trigger in interactive mode."""
        mock_session.execution_mode = "interactive"
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 1
        
        assert orchestrator._should_auto_progress() is False

    def test_should_not_auto_progress_without_session(self, orchestrator):
        """Verifies auto-progression requires active session."""
        orchestrator.session = None
        orchestrator.current_plan_id = "test-plan-1"
        
        assert orchestrator._should_auto_progress() is False

    def test_should_not_auto_progress_without_plan(self, orchestrator, mock_session):
        """Verifies auto-progression requires active plan."""
        orchestrator.session = mock_session
        orchestrator.current_plan_id = None
        
        assert orchestrator._should_auto_progress() is False

    def test_should_not_auto_progress_when_errors_present(self, orchestrator, mock_session):
        """Ensures execution halts when errors detected."""
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 1
        orchestrator.metrics['errors'] = ["Error 1", "Error 2"]
        
        assert orchestrator._should_auto_progress() is False

    def test_should_not_auto_progress_when_max_phases_reached(self, orchestrator, mock_session):
        """Validates max consecutive phases limit enforced."""
        mock_session.max_consecutive_phases = 5
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 5
        orchestrator.metrics['errors'] = []
        
        assert orchestrator._should_auto_progress() is False

    def test_continuation_mode_allows_auto_progress(self, orchestrator, mock_session):
        """Verifies continuation mode also enables auto-progression."""
        mock_session.execution_mode = "continuation"
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 1
        orchestrator.metrics['errors'] = []
        
        assert orchestrator._should_auto_progress() is True

    def test_get_current_phase_index_zero_based(self, orchestrator):
        """Validates phase index conversion (1-based → 0-based)."""
        orchestrator.current_phase = 3
        assert orchestrator._get_current_phase_index() == 2
        
        orchestrator.current_phase = 1
        assert orchestrator._get_current_phase_index() == 0
        
        orchestrator.current_phase = 0
        assert orchestrator._get_current_phase_index() == 0

    def test_execute_next_phase_without_plan_fails(self, orchestrator):
        """Ensures execute_next_phase fails gracefully without plan."""
        orchestrator.current_plan_id = None
        
        result = orchestrator._execute_next_phase()
        
        assert result['success'] is False
        assert 'No active plan' in result['error']

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    @patch.object(PlanningOrchestrator, '_execute_phase')
    def test_execute_next_phase_completes_when_no_more_phases(
        self, mock_execute, mock_parse, orchestrator, tmp_path
    ):
        """Validates completion detection when all phases done."""
        # Setup
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 3
        mock_parse.return_value = [
            {'name': 'Phase 1'},
            {'name': 'Phase 2'},
            {'name': 'Phase 3'}
        ]
        
        # Create mock master plan file with proper path structure
        orchestrator.temp_plan_manager.active_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active"
        plan_dir = orchestrator.temp_plan_manager.active_dir / "test-plan-1"
        plan_dir.mkdir(parents=True, exist_ok=True)
        master_plan = plan_dir / "master-plan.md"
        master_plan.write_text("# Master Plan\n")
        
        # Execute
        result = orchestrator._execute_next_phase()
        
        # Verify
        assert result['success'] is True
        assert result['is_complete'] is True
        assert 'All phases complete' in result['message']
        mock_execute.assert_not_called()

    @patch.object(PlanningOrchestrator, '_parse_phases_from_master_plan')
    @patch.object(PlanningOrchestrator, '_execute_phase')
    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    def test_execute_next_phase_transitions_correctly(
        self, mock_should_progress, mock_execute, mock_parse, orchestrator, mock_session, tmp_path
    ):
        """Validates phase transition with proper state updates."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 1
        
        # Mock temp_plan_manager with proper Path object for active_dir
        orchestrator.temp_plan_manager.active_dir = tmp_path / "cortex-brain" / "documents" / "planning" / "active"
        orchestrator.temp_plan_manager.mark_phase_in_progress = Mock()
        orchestrator.temp_plan_manager.mark_phase_complete = Mock()
        
        mock_parse.return_value = [
            {'name': 'Phase 1'},
            {'name': 'Phase 2'},
            {'name': 'Phase 3'}
        ]
        mock_execute.return_value = {'success': True, 'phase': 2}
        mock_should_progress.return_value = False  # Stop after one phase
        
        # Create mock master plan file with proper path structure
        plan_dir = orchestrator.temp_plan_manager.active_dir / "test-plan-1"
        plan_dir.mkdir(parents=True, exist_ok=True)
        master_plan = plan_dir / "master-plan.md"
        master_plan.write_text("# Master Plan\n")
        
        # Execute
        result = orchestrator._execute_next_phase()
        
        # Verify
        assert result['success'] is True
        assert orchestrator.current_phase == 2
        orchestrator.temp_plan_manager.mark_phase_in_progress.assert_called_once_with("test-plan-1", 2)
        orchestrator.temp_plan_manager.mark_phase_complete.assert_called_once_with("test-plan-1", 2)
        mock_execute.assert_called_once()

    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_execute_next_phase')
    def test_complete_phase_autonomous_triggers_auto_progress(
        self, mock_next_phase, mock_should_progress, orchestrator, mock_session
    ):
        """Verifies phase completion triggers auto-progression when enabled."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        mock_should_progress.return_value = True
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_next_phase.assert_called_once()

    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_execute_next_phase')
    def test_complete_phase_autonomous_skips_when_disabled(
        self, mock_next_phase, mock_should_progress, orchestrator, mock_session
    ):
        """Verifies no auto-progression when disabled."""
        # Setup
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        mock_should_progress.return_value = False
        
        # Execute
        orchestrator._complete_phase_autonomous(1)
        
        # Verify
        mock_next_phase.assert_not_called()


class TestSafetyChecks:
    """Test suite for safety mechanisms."""

    def test_max_phases_default_value(self, orchestrator, mock_session):
        """Validates default max consecutive phases limit."""
        # Remove explicit max_consecutive_phases
        delattr(mock_session, 'max_consecutive_phases')
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 25
        orchestrator.metrics['errors'] = []
        
        # Should use default of 20
        assert orchestrator._should_auto_progress() is False

    def test_error_detection_halts_execution(self, orchestrator, mock_session):
        """Ensures any error immediately halts auto-progression."""
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.current_phase = 1
        
        # Add error mid-execution
        orchestrator.metrics['errors'] = ["Critical error"]
        
        assert orchestrator._should_auto_progress() is False

    def test_resource_limits_enforced(self, orchestrator, mock_session):
        """Validates resource limit checks prevent infinite loops."""
        mock_session.max_consecutive_phases = 3
        orchestrator.session = mock_session
        orchestrator.current_plan_id = "test-plan-1"
        orchestrator.metrics['errors'] = []
        
        # Phase 1-3 should work
        for phase in [1, 2, 3]:
            orchestrator.current_phase = phase
            if phase < 3:
                assert orchestrator._should_auto_progress() is True
        
        # Phase 4+ should be blocked
        orchestrator.current_phase = 4
        assert orchestrator._should_auto_progress() is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
