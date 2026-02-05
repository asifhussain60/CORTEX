"""
Tests for AC-PHASE24-007: TDDOrchestrator + PhaseCompletionOrchestrator Integration.

Verifies that TDD execution automatically triggers phase completion hook.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
from cortex.orchestrators.support.phase_completion_orchestrator import (
    PhaseCompletionOrchestrator,
    PhaseCompletionResult
)


@pytest.fixture
def mock_phase_completion_orchestrator():
    """Mock PhaseCompletionOrchestrator for testing."""
    mock = Mock(spec=PhaseCompletionOrchestrator)
    mock.complete_phase = MagicMock(
        return_value=PhaseCompletionResult(
            success=True,
            phase_updated=True,
            dashboard_regenerated=True,
            registry_synced=True,
            enhancement_updated=False
        )
    )
    return mock


def test_phase_completion_hook_called_on_success(mock_phase_completion_orchestrator):
    """Test that phase completion hook is called after successful TDD execution."""
    # Arrange
    orchestrator = TDDOrchestrator()
    orchestrator._phase_completion_orchestrator = mock_phase_completion_orchestrator
    
    context = {
        "phase_file": "/path/to/phase-24.yaml",
        "phase_key": "phase_24_3",
        "enhancement_id": "ENH-039"
    }
    
    execution_result = {
        "phase": "GREEN",
        "tests_passed": True
    }
    
    # Act
    orchestrator._run_phase_completion_hook(context, execution_result)
    
    # Assert
    mock_phase_completion_orchestrator.complete_phase.assert_called_once_with(
        phase_file=Path("/path/to/phase-24.yaml"),
        phase_key="phase_24_3",
        enhancement_id="ENH-039"
    )


def test_phase_completion_hook_skipped_without_phase_info():
    """Test that hook is skipped if context lacks phase information."""
    # Arrange
    orchestrator = TDDOrchestrator()
    mock_orchestrator = Mock(spec=PhaseCompletionOrchestrator)
    orchestrator._phase_completion_orchestrator = mock_orchestrator
    
    context = {}  # No phase_file or phase_key
    execution_result = {"phase": "GREEN"}
    
    # Act
    orchestrator._run_phase_completion_hook(context, execution_result)
    
    # Assert
    mock_orchestrator.complete_phase.assert_not_called()


def test_phase_completion_hook_handles_failure_gracefully():
    """Test that hook failures don't crash TDD execution."""
    # Arrange
    orchestrator = TDDOrchestrator()
    mock_orchestrator = Mock(spec=PhaseCompletionOrchestrator)
    mock_orchestrator.complete_phase = MagicMock(
        return_value=PhaseCompletionResult(
            success=False,
            error="Dashboard regeneration failed"
        )
    )
    orchestrator._phase_completion_orchestrator = mock_orchestrator
    
    context = {
        "phase_file": "/path/to/phase.yaml",
        "phase_key": "phase_24_3"
    }
    execution_result = {"phase": "GREEN"}
    
    # Act (should not raise exception)
    orchestrator._run_phase_completion_hook(context, execution_result)
    
    # Assert - called but failure logged (non-blocking)
    mock_orchestrator.complete_phase.assert_called_once()


def test_phase_completion_hook_not_initialized():
    """Test that hook is safely skipped if orchestrator not initialized."""
    # Arrange
    orchestrator = TDDOrchestrator()
    orchestrator._phase_completion_orchestrator = None  # Not initialized
    
    context = {
        "phase_file": "/path/to/phase.yaml",
        "phase_key": "phase_24_3"
    }
    execution_result = {"phase": "GREEN"}
    
    # Act (should not raise exception)
    orchestrator._run_phase_completion_hook(context, execution_result)
    
    # Assert - no error raised, hook simply skipped


def test_phase_completion_hook_with_optional_enhancement_id():
    """Test hook with optional enhancement_id parameter."""
    # Arrange
    orchestrator = TDDOrchestrator()
    mock_orchestrator = Mock(spec=PhaseCompletionOrchestrator)
    mock_orchestrator.complete_phase = MagicMock(
        return_value=PhaseCompletionResult(success=True)
    )
    orchestrator._phase_completion_orchestrator = mock_orchestrator
    
    context = {
        "phase_file": "/path/to/phase.yaml",
        "phase_key": "phase_24_4"
        # No enhancement_id - should be None
    }
    execution_result = {"phase": "GREEN"}
    
    # Act
    orchestrator._run_phase_completion_hook(context, execution_result)
    
    # Assert
    mock_orchestrator.complete_phase.assert_called_once_with(
        phase_file=Path("/path/to/phase.yaml"),
        phase_key="phase_24_4",
        enhancement_id=None
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
