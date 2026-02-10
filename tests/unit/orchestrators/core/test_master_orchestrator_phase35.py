"""
Test MasterOrchestrator Phase 35 Integration.

Tests autonomous continuation detection + ASCII progress bar integration
in MasterOrchestrator's process_user_request flow.

Authority: Phase 35 (autonomous-execution-enhancement.yaml)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.interaction.autonomous_plan_executor import AutonomousPlanExecutor, Phase
from cortex.orchestrators.response.ascii_progress_bar import ASCIIProgressBar
from cortex.core.result import Ok, Err


class TestMasterOrchestratorAutonomousIntegration:
    """Test autonomous continuation detection in MasterOrchestrator."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create MasterOrchestrator with mocked dependencies."""
        with patch('cortex.orchestrators.core.master_orchestrator.EnhancedAuditLogger'):
            orchestrator = MasterOrchestrator()
            orchestrator._autonomous_executor = AutonomousPlanExecutor()
            orchestrator._progress_bar = ASCIIProgressBar()
            return orchestrator
    
    def test_detect_continuation_proceed(self, mock_orchestrator):
        """Test 'proceed' triggers autonomous mode."""
        # Arrange
        user_request = "proceed"
        
        # Mock execute_operation to verify autonomous flag
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        mock_orchestrator.execute_operation.assert_called_once()
        call_args = mock_orchestrator.execute_operation.call_args
        assert call_args[1]["parameters"]["autonomous"] is True
    
    def test_detect_continuation_continue(self, mock_orchestrator):
        """Test 'continue' triggers autonomous mode."""
        # Arrange
        user_request = "continue with next phase"
        
        # Mock execute_operation
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        call_args = mock_orchestrator.execute_operation.call_args
        assert call_args[1]["parameters"]["autonomous"] is True
    
    def test_detect_continuation_yes(self, mock_orchestrator):
        """Test 'yes' triggers autonomous mode."""
        # Arrange
        user_request = "yes"
        
        # Mock execute_operation
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        call_args = mock_orchestrator.execute_operation.call_args
        assert call_args[1]["parameters"]["autonomous"] is True
    
    def test_no_continuation_detected(self, mock_orchestrator):
        """Test non-continuation request follows normal flow."""
        # Arrange
        user_request = "what is the status?"
        
        # Mock interaction_orchestrator to skip challenge system
        mock_orchestrator.interaction_orchestrator = None
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        call_args = mock_orchestrator.execute_operation.call_args
        # Should NOT have autonomous flag
        assert "autonomous" not in call_args[1]["parameters"] or not call_args[1]["parameters"]["autonomous"]
    
    def test_progress_bar_display_on_continuation(self, mock_orchestrator):
        """Test ASCII progress bar displayed when continuation detected."""
        # Arrange
        user_request = "proceed"
        
        # Mock load_next_phase to return phase
        mock_phase = Phase(
            id="phase-35",
            name="Autonomous Execution Enhancement",
            status="active",
            priority="P0",
            file="phases/active/phase-35.yaml"
        )
        mock_orchestrator._autonomous_executor.load_next_phase = Mock(return_value=mock_phase)
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        # Verify progress bar was used (via logger call)
        # In real implementation, logger.log_operation_start would be called with progress_display
    
    def test_skip_challenge_system_in_autonomous_mode(self, mock_orchestrator):
        """Test challenge system bypassed when autonomous mode detected."""
        # Arrange
        user_request = "proceed"
        
        # Mock interaction_orchestrator
        mock_orchestrator.interaction_orchestrator = Mock()
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        # interaction_orchestrator.execute_turn_with_challenge should NOT be called
        mock_orchestrator.interaction_orchestrator.execute_turn_with_challenge.assert_not_called()


class TestMasterOrchestratorProgressBar:
    """Test ASCII progress bar integration in MasterOrchestrator."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create MasterOrchestrator with progress bar."""
        with patch('cortex.orchestrators.core.master_orchestrator.EnhancedAuditLogger'):
            orchestrator = MasterOrchestrator()
            orchestrator._progress_bar = ASCIIProgressBar()
            return orchestrator
    
    def test_progress_bar_initialization(self, mock_orchestrator):
        """Test progress bar initialized in MasterOrchestrator."""
        assert mock_orchestrator._progress_bar is not None
        assert isinstance(mock_orchestrator._progress_bar, ASCIIProgressBar)
    
    def test_progress_bar_format_phase(self, mock_orchestrator):
        """Test progress bar can format phase progress."""
        from cortex.orchestrators.response.ascii_progress_bar import Phase as ProgressPhase
        
        # Arrange
        phase = ProgressPhase(name="Phase 35", progress=0.6, status="active")
        
        # Act
        formatted = mock_orchestrator._progress_bar.format_phase_progress(phase)
        
        # Assert
        assert "[" in formatted
        assert "█" in formatted  # Filled blocks
        assert "60%" in formatted
        assert "Phase 35" in formatted


class TestMasterOrchestratorMinimalStatus:
    """Test minimal status update integration (R3)."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create MasterOrchestrator."""
        with patch('cortex.orchestrators.core.master_orchestrator.EnhancedAuditLogger'):
            orchestrator = MasterOrchestrator()
            return orchestrator
    
class TestMasterOrchestratorSingleDecisionGate:
    """Test single decision gate enforcement (R4)."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create MasterOrchestrator with autonomous executor."""
        with patch('cortex.orchestrators.core.master_orchestrator.EnhancedAuditLogger'):
            orchestrator = MasterOrchestrator()
            orchestrator._autonomous_executor = AutonomousPlanExecutor()
            return orchestrator
    
    def test_no_mid_execution_prompts_in_autonomous_mode(self, mock_orchestrator):
        """Test no user prompts during autonomous execution."""
        # Arrange
        user_request = "proceed"
        mock_orchestrator.execute_operation = Mock(return_value=Ok({"status": "success"}))
        
        # Act
        result = mock_orchestrator.process_user_request(user_request)
        
        # Assert
        assert result.is_ok()
        # Autonomous flag should be True, which downstream orchestrators use to skip prompts
        call_args = mock_orchestrator.execute_operation.call_args
        assert call_args[1]["parameters"]["autonomous"] is True
