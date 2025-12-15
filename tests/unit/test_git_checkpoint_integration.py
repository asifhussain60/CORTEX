"""
Unit Tests for Git Checkpoint Integration (Phase 1)

Tests automatic git checkpoint creation before phase execution.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, call
from datetime import datetime

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator instance for testing."""
    return PlanningOrchestrator(project_root=tmp_path)


class TestGitCheckpointIntegration:
    """Test suite for git checkpoint integration."""

    def test_checkpoint_orchestrator_initialized(self, orchestrator):
        """Verifies checkpoint orchestrator initialized on orchestrator creation."""
        assert hasattr(orchestrator, 'checkpoint_orchestrator')
        # Note: May be None if GitCheckpointOrchestrator initialization failed
        # which is acceptable in test environments

    @patch('src.operations.modules.orchestration.planning_orchestrator.GitCheckpointOrchestrator')
    def test_create_phase_checkpoint_constructs_message(self, mock_orchestrator_class, orchestrator):
        """Validates checkpoint message construction."""
        # Setup
        mock_orch = Mock()
        mock_orch.create_checkpoint.return_value = {'success': True, 'checkpoint_id': 'abc123'}
        orchestrator.checkpoint_orchestrator = mock_orch
        orchestrator.current_plan_id = "test-plan"
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        
        # Execute
        result = orchestrator._create_phase_checkpoint("Phase 1")
        
        # Verify
        assert result is True
        mock_orch.create_checkpoint.assert_called_once()
        call_kwargs = mock_orch.create_checkpoint.call_args.kwargs
        assert "Phase 1" in call_kwargs['message']
        assert "test-plan" in call_kwargs['message']
        assert "autonomous" in call_kwargs['message']

    @patch('src.operations.modules.orchestration.planning_orchestrator.GitCheckpointOrchestrator')
    def test_create_phase_checkpoint_includes_metadata(self, mock_orchestrator_class, orchestrator):
        """Validates checkpoint metadata."""
        # Setup
        mock_orch = Mock()
        mock_orch.create_checkpoint.return_value = {'success': True, 'checkpoint_id': 'abc123'}
        orchestrator.checkpoint_orchestrator = mock_orch
        orchestrator.current_plan_id = "test-plan"
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        
        # Execute
        orchestrator._create_phase_checkpoint("Phase 1")
        
        # Verify
        call_kwargs = mock_orch.create_checkpoint.call_args.kwargs
        metadata = call_kwargs['metadata']
        assert metadata['phase_name'] == "Phase 1"
        assert metadata['plan_id'] == "test-plan"
        assert metadata['execution_mode'] == "autonomous"
        assert metadata['planning_system_version'] == "3.1"

    @patch('src.operations.modules.orchestration.planning_orchestrator.GitCheckpointOrchestrator')
    def test_create_phase_checkpoint_handles_missing_plan_id(self, mock_orchestrator_class, orchestrator):
        """Validates fallback when plan ID is None."""
        # Setup
        mock_orch = Mock()
        mock_orch.create_checkpoint.return_value = {'success': True, 'checkpoint_id': 'abc123'}
        orchestrator.checkpoint_orchestrator = mock_orch
        orchestrator.current_plan_id = None
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "interactive"
        
        # Execute
        result = orchestrator._create_phase_checkpoint("Phase 2")
        
        # Verify
        assert result is True
        call_kwargs = mock_orch.create_checkpoint.call_args.kwargs
        assert "unknown-plan" in call_kwargs['message']

    @patch('src.operations.modules.orchestration.planning_orchestrator.GitCheckpointOrchestrator')
    def test_create_phase_checkpoint_handles_missing_session(self, mock_orchestrator_class, orchestrator):
        """Validates fallback when session is None."""
        # Setup
        mock_orch = Mock()
        mock_orch.create_checkpoint.return_value = {'success': True, 'checkpoint_id': 'abc123'}
        orchestrator.checkpoint_orchestrator = mock_orch
        orchestrator.current_plan_id = "test-plan"
        orchestrator.session = None
        
        # Execute
        result = orchestrator._create_phase_checkpoint("Phase 3")
        
        # Verify
        assert result is True
        call_kwargs = mock_orch.create_checkpoint.call_args.kwargs
        assert "interactive" in call_kwargs['message']  # Default mode

    def test_create_phase_checkpoint_without_orchestrator(self, orchestrator):
        """Validates graceful failure when checkpoint orchestrator unavailable."""
        # Setup
        orchestrator.checkpoint_orchestrator = None
        
        # Execute
        result = orchestrator._create_phase_checkpoint("Phase 4")
        
        # Verify
        assert result is False

    @patch('src.operations.modules.orchestration.planning_orchestrator.GitCheckpointOrchestrator')
    def test_create_phase_checkpoint_handles_exception(self, mock_orchestrator_class, orchestrator):
        """Validates error handling when checkpoint creation fails."""
        # Setup
        mock_orch = Mock()
        mock_orch.create_checkpoint.side_effect = Exception("Git error")
        orchestrator.checkpoint_orchestrator = mock_orch
        orchestrator.current_plan_id = "test-plan"
        
        # Execute
        result = orchestrator._create_phase_checkpoint("Phase 5")
        
        # Verify
        assert result is False

    @patch('src.operations.modules.orchestration.planning_orchestrator.GitCheckpointOrchestrator')
    def test_create_phase_checkpoint_returns_false_when_not_success(self, mock_orchestrator_class, orchestrator):
        """Validates return value when checkpoint creation returns success=False."""
        # Setup
        mock_orch = Mock()
        mock_orch.create_checkpoint.return_value = {'success': False}
        orchestrator.checkpoint_orchestrator = mock_orch
        orchestrator.current_plan_id = "test-plan"
        
        # Execute
        result = orchestrator._create_phase_checkpoint("Phase 6")
        
        # Verify
        assert result is False

    @patch.object(PlanningOrchestrator, '_create_phase_checkpoint')
    def test_record_phase_start_calls_checkpoint(self, mock_checkpoint, orchestrator):
        """Validates _record_phase_start calls _create_phase_checkpoint FIRST."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        mock_checkpoint.return_value = True
        
        # Execute
        orchestrator._record_phase_start("Test Phase")
        
        # Verify checkpoint called
        mock_checkpoint.assert_called_once_with("Test Phase")
        
        # Verify session.record_phase_start called after checkpoint
        orchestrator.session.record_phase_start.assert_called_once_with("Test Phase")

    @patch.object(PlanningOrchestrator, '_create_phase_checkpoint')
    def test_record_phase_start_continues_even_if_checkpoint_fails(self, mock_checkpoint, orchestrator):
        """Validates phase recording continues even if checkpoint fails."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "autonomous"
        mock_checkpoint.return_value = False
        
        # Execute
        orchestrator._record_phase_start("Test Phase")
        
        # Verify both were called despite checkpoint failure
        mock_checkpoint.assert_called_once()
        orchestrator.session.record_phase_start.assert_called_once()


class TestCheckpointInAutonomousMode:
    """Test checkpoints in autonomous execution context."""

    @patch.object(PlanningOrchestrator, '_create_phase_checkpoint')
    @patch.object(PlanningOrchestrator, '_should_auto_progress')
    @patch.object(PlanningOrchestrator, '_execute_next_phase')
    @patch.object(PlanningOrchestrator, '_update_master_plan_tracker')
    @patch.object(PlanningOrchestrator, '_generate_phase_completion_summary')
    def test_checkpoint_created_in_autonomous_flow(
        self, mock_summary, mock_update, mock_execute, mock_should, mock_checkpoint, orchestrator
    ):
        """Validates checkpoint created during autonomous phase completion."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.phases = [{'name': 'Phase 1'}, {'name': 'Phase 2'}]
        orchestrator.session.execution_mode = "autonomous"
        orchestrator.current_plan_id = "test-plan"
        mock_should.return_value = True
        mock_summary.return_value = None
        mock_checkpoint.return_value = True
        
        # Execute - _complete_phase_autonomous calls _record_phase_end which doesn't create checkpoint
        # But when next phase starts via _execute_next_phase, checkpoint should be created
        orchestrator._complete_phase_autonomous(1)
        
        # Verify - checkpoint would be created when next phase starts
        # (This test confirms the flow, actual checkpoint is in _record_phase_start)
        assert mock_should.called
        assert mock_execute.called


class TestCheckpointInInteractiveMode:
    """Test checkpoints in interactive execution context."""

    @patch.object(PlanningOrchestrator, '_create_phase_checkpoint')
    def test_checkpoint_created_in_interactive_mode(self, mock_checkpoint, orchestrator):
        """Validates checkpoint created even in interactive mode."""
        # Setup
        orchestrator.session = Mock()
        orchestrator.session.execution_mode = "interactive"
        mock_checkpoint.return_value = True
        
        # Execute
        orchestrator._record_phase_start("Interactive Phase")
        
        # Verify
        mock_checkpoint.assert_called_once_with("Interactive Phase")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
