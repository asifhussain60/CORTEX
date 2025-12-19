"""
CORTEX 4.0 PhaseManagerIntegration Tests

Purpose: Comprehensive unit tests for PhaseManagerIntegration class
Coverage Target: 85%+
Test Strategy: Mock BaseOrchestrator, validation handlers, file I/O
Version: 4.0.0
Author: CORTEX Development Team
Created: 2025-12-19 (Week 8 Day 4)

Test Categories:
- Initialization tests
- Phase lifecycle tests (begin/complete/fail)
- Progress tracking tests
- State persistence tests
- Validation handler tests
- Error handling tests
"""

import json
import logging
import pytest
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
from unittest.mock import Mock, MagicMock, patch, mock_open

from src.orchestrators.planning.phase_manager_integration import (
    PhaseManagerIntegration,
    PhaseTransition,
    PhaseProgress,
    PhaseValidationType,
)
from src.orchestrators.base.base_orchestrator import (
    OrchestratorStatus
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Create temporary workspace root."""
    return tmp_path / "workspace"


@pytest.fixture
def mock_orchestrator():
    """Create mock BaseOrchestrator instance."""
    orchestrator = Mock()
    orchestrator.current_phase = "INITIALIZATION"
    orchestrator.status = OrchestratorStatus.NOT_STARTED
    return orchestrator


@pytest.fixture
def mock_logger():
    """Create mock logger."""
    return Mock(spec=logging.Logger)


@pytest.fixture
def phase_manager_integration(workspace_root, mock_orchestrator, mock_logger):
    """Create PhaseManagerIntegration instance."""
    return PhaseManagerIntegration(
        orchestrator=mock_orchestrator,
        workspace_root=workspace_root,
        logger_instance=mock_logger
    )


# ============================================================================
# Initialization Tests
# ============================================================================

def test_phase_manager_integration_init(phase_manager_integration, mock_orchestrator, workspace_root, mock_logger):
    """Test PhaseManagerIntegration initialization."""
    assert phase_manager_integration.orchestrator == mock_orchestrator
    assert phase_manager_integration.workspace_root == Path(workspace_root)
    assert phase_manager_integration.logger == mock_logger
    assert phase_manager_integration.phase_history == []
    assert phase_manager_integration.current_progress == {}
    assert phase_manager_integration.state_file == Path(workspace_root) / ".cortex" / "phase_state.json"


def test_phase_manager_integration_init_default_logger(workspace_root, mock_orchestrator):
    """Test PhaseManagerIntegration initialization with default logger."""
    integration = PhaseManagerIntegration(
        orchestrator=mock_orchestrator,
        workspace_root=workspace_root
    )
    
    assert integration.logger is not None


# ============================================================================
# Phase Lifecycle Tests - begin_phase
# ============================================================================

def test_begin_phase_success_no_validation(phase_manager_integration, mock_orchestrator, mock_logger):
    """Test begin_phase without validation handler."""
    result = phase_manager_integration.begin_phase("DISCOVERY")
    
    assert result is True
    assert mock_orchestrator.current_phase == "DISCOVERY"
    assert mock_orchestrator.status == OrchestratorStatus.RUNNING
    assert "DISCOVERY" in phase_manager_integration.current_progress
    
    progress = phase_manager_integration.current_progress["DISCOVERY"]
    assert progress.phase_name == "DISCOVERY"
    assert progress.status == OrchestratorStatus.RUNNING
    assert progress.start_time is not None
    
    assert len(phase_manager_integration.phase_history) == 1
    transition = phase_manager_integration.phase_history[0]
    assert transition.from_phase == "INITIALIZATION"
    assert transition.to_phase == "DISCOVERY"
    assert transition.success is True


def test_begin_phase_success_with_validation(phase_manager_integration, mock_orchestrator):
    """Test begin_phase with successful DoR validation."""
    # Validation handler that returns True
    validation_handler = Mock(return_value=True)
    
    result = phase_manager_integration.begin_phase("PLANNING", validation_handler=validation_handler)
    
    assert result is True
    assert mock_orchestrator.current_phase == "PLANNING"
    assert mock_orchestrator.status == OrchestratorStatus.RUNNING
    
    # Verify validation handler was called with correct context
    validation_handler.assert_called_once()
    call_args = validation_handler.call_args[0][0]
    assert call_args["phase_name"] == "PLANNING"
    assert call_args["orchestrator_status"] == OrchestratorStatus.NOT_STARTED


def test_begin_phase_failure_validation(phase_manager_integration, mock_orchestrator, mock_logger):
    """Test begin_phase with failed DoR validation."""
    # Validation handler that returns False
    validation_handler = Mock(return_value=False)
    
    result = phase_manager_integration.begin_phase("IMPLEMENTATION", validation_handler=validation_handler)
    
    assert result is False
    # Orchestrator should still be in previous phase
    assert mock_orchestrator.current_phase == "INITIALIZATION"
    # No phase progress created
    assert "IMPLEMENTATION" not in phase_manager_integration.current_progress
    # No transition recorded
    assert len(phase_manager_integration.phase_history) == 0


def test_begin_phase_exception_handling(phase_manager_integration, mock_orchestrator, mock_logger):
    """Test begin_phase exception handling."""
    # Validation handler that raises exception
    validation_handler = Mock(side_effect=ValueError("Validation error"))
    
    result = phase_manager_integration.begin_phase("VALIDATION", validation_handler=validation_handler)
    
    assert result is False
    mock_logger.error.assert_called()


# ============================================================================
# Phase Lifecycle Tests - complete_phase
# ============================================================================

def test_complete_phase_success_no_validation(phase_manager_integration, mock_orchestrator):
    """Test complete_phase without validation handler."""
    # First begin a phase
    phase_manager_integration.begin_phase("DISCOVERY")
    
    # Complete the phase
    metrics = {"lines_analyzed": 1000, "complexity_score": 7.5}
    result = phase_manager_integration.complete_phase("DISCOVERY", phase_metrics=metrics)
    
    assert result is True
    
    progress = phase_manager_integration.current_progress["DISCOVERY"]
    assert progress.status == OrchestratorStatus.COMPLETED
    assert progress.end_time is not None
    assert progress.progress_percent == 100.0
    assert progress.metrics["lines_analyzed"] == 1000
    assert progress.metrics["complexity_score"] == 7.5
    assert "duration_seconds" in progress.metrics


def test_complete_phase_success_with_validation(phase_manager_integration):
    """Test complete_phase with successful DoD validation."""
    # Begin phase first
    phase_manager_integration.begin_phase("PLANNING")
    
    # Validation handler that returns True
    validation_handler = Mock(return_value=True)
    metrics = {"tests_created": 15, "coverage_percent": 88.5}
    
    result = phase_manager_integration.complete_phase(
        "PLANNING",
        validation_handler=validation_handler,
        phase_metrics=metrics
    )
    
    assert result is True
    
    # Verify validation handler was called
    validation_handler.assert_called_once()
    call_args = validation_handler.call_args[0][0]
    assert call_args["phase_name"] == "PLANNING"
    assert call_args["phase_metrics"]["tests_created"] == 15


def test_complete_phase_failure_validation(phase_manager_integration, mock_logger):
    """Test complete_phase with failed DoD validation."""
    # Begin phase first
    phase_manager_integration.begin_phase("IMPLEMENTATION")
    
    # Validation handler that returns False
    validation_handler = Mock(return_value=False)
    
    result = phase_manager_integration.complete_phase(
        "IMPLEMENTATION",
        validation_handler=validation_handler
    )
    
    assert result is False
    
    # Progress should still be RUNNING (not completed)
    progress = phase_manager_integration.current_progress["IMPLEMENTATION"]
    assert progress.status == OrchestratorStatus.RUNNING


def test_complete_phase_without_begin(phase_manager_integration, mock_logger):
    """Test complete_phase for phase that wasn't begun."""
    result = phase_manager_integration.complete_phase("VALIDATION")
    
    # Should still return True (no error), but no progress update
    assert result is True
    assert "VALIDATION" not in phase_manager_integration.current_progress


def test_complete_phase_exception_handling(phase_manager_integration, mock_logger):
    """Test complete_phase exception handling."""
    # Begin phase
    phase_manager_integration.begin_phase("COMPLETION")
    
    # Validation handler that raises exception
    validation_handler = Mock(side_effect=RuntimeError("DoD validation error"))
    
    result = phase_manager_integration.complete_phase(
        "COMPLETION",
        validation_handler=validation_handler
    )
    
    assert result is False
    mock_logger.error.assert_called()


# ============================================================================
# Phase Lifecycle Tests - fail_phase
# ============================================================================

def test_fail_phase_with_errors_list(phase_manager_integration, mock_orchestrator):
    """Test fail_phase with list of errors."""
    # Begin phase first
    phase_manager_integration.begin_phase("IMPLEMENTATION")
    
    errors = ["Compilation failed", "Test suite failed", "Linting errors"]
    phase_manager_integration.fail_phase("IMPLEMENTATION", "Build failed", errors=errors)
    
    # Check progress status
    progress = phase_manager_integration.current_progress["IMPLEMENTATION"]
    assert progress.status == OrchestratorStatus.FAILED
    assert progress.end_time is not None
    assert progress.metrics["errors"] == errors
    
    # Check orchestrator status
    assert mock_orchestrator.status == OrchestratorStatus.FAILED


def test_fail_phase_without_errors_list(phase_manager_integration, mock_orchestrator):
    """Test fail_phase without errors list."""
    # Begin phase first
    phase_manager_integration.begin_phase("VALIDATION")
    
    error_message = "Critical validation failure"
    phase_manager_integration.fail_phase("VALIDATION", error_message)
    
    # Check progress has error message
    progress = phase_manager_integration.current_progress["VALIDATION"]
    assert progress.status == OrchestratorStatus.FAILED
    assert progress.metrics["errors"] == [error_message]


def test_fail_phase_without_begin(phase_manager_integration, mock_orchestrator):
    """Test fail_phase for phase that wasn't begun."""
    # Should not raise error, just update orchestrator status
    phase_manager_integration.fail_phase("COMPLETION", "Unknown failure")
    
    assert mock_orchestrator.status == OrchestratorStatus.FAILED
    assert "COMPLETION" not in phase_manager_integration.current_progress


# ============================================================================
# Progress Tracking Tests
# ============================================================================

def test_update_progress_success(phase_manager_integration):
    """Test update_progress for existing phase."""
    # Begin phase
    phase_manager_integration.begin_phase("DISCOVERY")
    
    # Update progress
    metrics = {"files_scanned": 50, "current_file": "main.py"}
    phase_manager_integration.update_progress("DISCOVERY", 45.5, metrics=metrics)
    
    progress = phase_manager_integration.current_progress["DISCOVERY"]
    assert progress.progress_percent == 45.5
    assert progress.metrics["files_scanned"] == 50
    assert progress.metrics["current_file"] == "main.py"


def test_update_progress_clamps_values(phase_manager_integration):
    """Test update_progress clamps percentage to 0-100 range."""
    # Begin phase
    phase_manager_integration.begin_phase("PLANNING")
    
    # Test over 100%
    phase_manager_integration.update_progress("PLANNING", 150.0)
    assert phase_manager_integration.current_progress["PLANNING"].progress_percent == 100.0
    
    # Test under 0%
    phase_manager_integration.update_progress("PLANNING", -25.0)
    assert phase_manager_integration.current_progress["PLANNING"].progress_percent == 0.0


def test_update_progress_nonexistent_phase(phase_manager_integration, mock_logger):
    """Test update_progress for nonexistent phase."""
    phase_manager_integration.update_progress("NONEXISTENT", 50.0)
    
    # Should log warning, no error
    mock_logger.warning.assert_called_once()


def test_get_phase_progress_existing(phase_manager_integration):
    """Test get_phase_progress for existing phase."""
    # Begin phase
    phase_manager_integration.begin_phase("IMPLEMENTATION")
    
    progress = phase_manager_integration.get_phase_progress("IMPLEMENTATION")
    
    assert progress is not None
    assert progress.phase_name == "IMPLEMENTATION"
    assert progress.status == OrchestratorStatus.RUNNING


def test_get_phase_progress_nonexistent(phase_manager_integration):
    """Test get_phase_progress for nonexistent phase."""
    progress = phase_manager_integration.get_phase_progress("NONEXISTENT")
    
    assert progress is None


def test_get_all_progress(phase_manager_integration):
    """Test get_all_progress returns all phases."""
    # Begin multiple phases
    phase_manager_integration.begin_phase("DISCOVERY")
    phase_manager_integration.complete_phase("DISCOVERY")
    phase_manager_integration.begin_phase("PLANNING")
    
    all_progress = phase_manager_integration.get_all_progress()
    
    assert len(all_progress) == 2
    assert "DISCOVERY" in all_progress
    assert "PLANNING" in all_progress
    assert all_progress["DISCOVERY"].status == OrchestratorStatus.COMPLETED
    assert all_progress["PLANNING"].status == OrchestratorStatus.RUNNING


def test_get_phase_history(phase_manager_integration):
    """Test get_phase_history returns transition history."""
    # Multiple phase transitions
    phase_manager_integration.begin_phase("DISCOVERY")
    phase_manager_integration.complete_phase("DISCOVERY")
    phase_manager_integration.begin_phase("PLANNING")
    
    history = phase_manager_integration.get_phase_history()
    
    assert len(history) == 2
    assert history[0].to_phase == "DISCOVERY"
    assert history[1].to_phase == "PLANNING"


# ============================================================================
# State Persistence Tests
# ============================================================================

def test_persist_state_creates_directory(phase_manager_integration, workspace_root):
    """Test _persist_state creates .cortex directory."""
    phase_manager_integration.begin_phase("DISCOVERY")
    
    # State file should exist
    assert phase_manager_integration.state_file.exists()
    assert phase_manager_integration.state_file.parent.name == ".cortex"


def test_persist_state_json_format(phase_manager_integration, workspace_root):
    """Test _persist_state creates valid JSON."""
    # Create some state
    phase_manager_integration.begin_phase("PLANNING")
    phase_manager_integration.update_progress("PLANNING", 75.0, {"test_metric": 123})
    
    # Read state file
    state_data = json.loads(phase_manager_integration.state_file.read_text())
    
    assert "current_phase" in state_data
    assert "orchestrator_status" in state_data
    assert "phase_history" in state_data
    assert "current_progress" in state_data
    
    assert state_data["current_phase"] == "PLANNING"
    assert "PLANNING" in state_data["current_progress"]
    assert state_data["current_progress"]["PLANNING"]["progress_percent"] == 75.0


def test_restore_state_success(phase_manager_integration, mock_orchestrator, workspace_root):
    """Test restore_state from valid state file."""
    # Create state
    phase_manager_integration.begin_phase("IMPLEMENTATION")
    phase_manager_integration.update_progress("IMPLEMENTATION", 50.0)
    
    # Create new integration instance
    new_integration = PhaseManagerIntegration(
        orchestrator=mock_orchestrator,
        workspace_root=workspace_root
    )
    
    # Restore state
    result = new_integration.restore_state()
    
    assert result is True
    assert mock_orchestrator.current_phase == "IMPLEMENTATION"
    assert "IMPLEMENTATION" in new_integration.current_progress
    assert new_integration.current_progress["IMPLEMENTATION"].progress_percent == 50.0


def test_restore_state_no_file(phase_manager_integration, workspace_root, mock_logger):
    """Test restore_state when no state file exists."""
    # Remove state file if exists
    if phase_manager_integration.state_file.exists():
        phase_manager_integration.state_file.unlink()
    
    result = phase_manager_integration.restore_state()
    
    assert result is False


def test_restore_state_corrupted_json(phase_manager_integration, workspace_root, mock_logger):
    """Test restore_state with corrupted JSON file."""
    # Create corrupted state file
    phase_manager_integration.state_file.parent.mkdir(parents=True, exist_ok=True)
    phase_manager_integration.state_file.write_text("{ invalid json }")
    
    result = phase_manager_integration.restore_state()
    
    assert result is False
    mock_logger.error.assert_called()


def test_clear_state(phase_manager_integration, workspace_root):
    """Test clear_state removes state data."""
    # Create state
    phase_manager_integration.begin_phase("COMPLETION")
    phase_manager_integration.complete_phase("COMPLETION")
    
    assert len(phase_manager_integration.phase_history) > 0
    assert len(phase_manager_integration.current_progress) > 0
    assert phase_manager_integration.state_file.exists()
    
    # Clear state
    phase_manager_integration.clear_state()
    
    assert len(phase_manager_integration.phase_history) == 0
    assert len(phase_manager_integration.current_progress) == 0
    assert not phase_manager_integration.state_file.exists()


# ============================================================================
# Integration Tests - Full Phase Lifecycle
# ============================================================================

def test_full_phase_lifecycle_success(phase_manager_integration, mock_orchestrator):
    """Test complete phase lifecycle: begin → update → complete."""
    # Begin phase
    assert phase_manager_integration.begin_phase("DISCOVERY") is True
    
    # Update progress multiple times
    phase_manager_integration.update_progress("DISCOVERY", 25.0, {"files_scanned": 10})
    phase_manager_integration.update_progress("DISCOVERY", 50.0, {"files_scanned": 20})
    phase_manager_integration.update_progress("DISCOVERY", 75.0, {"files_scanned": 30})
    
    # Complete phase
    final_metrics = {"files_scanned": 40, "total_lines": 5000}
    assert phase_manager_integration.complete_phase("DISCOVERY", phase_metrics=final_metrics) is True
    
    # Verify final state
    progress = phase_manager_integration.current_progress["DISCOVERY"]
    assert progress.status == OrchestratorStatus.COMPLETED
    assert progress.progress_percent == 100.0
    assert progress.metrics["total_lines"] == 5000


def test_full_phase_lifecycle_with_failure(phase_manager_integration, mock_orchestrator):
    """Test phase lifecycle ending in failure."""
    # Begin phase
    phase_manager_integration.begin_phase("IMPLEMENTATION")
    
    # Update progress
    phase_manager_integration.update_progress("IMPLEMENTATION", 60.0)
    
    # Fail phase
    phase_manager_integration.fail_phase(
        "IMPLEMENTATION",
        "Build failed",
        errors=["Syntax error in main.py", "Test suite timeout"]
    )
    
    # Verify failure state
    progress = phase_manager_integration.current_progress["IMPLEMENTATION"]
    assert progress.status == OrchestratorStatus.FAILED
    assert len(progress.metrics["errors"]) == 2
    assert mock_orchestrator.status == OrchestratorStatus.FAILED


def test_multiple_phases_sequential(phase_manager_integration):
    """Test multiple phases executed sequentially."""
    phases = ["DISCOVERY", "PLANNING", "IMPLEMENTATION", "VALIDATION", "COMPLETION"]
    
    for phase in phases:
        assert phase_manager_integration.begin_phase(phase) is True
        phase_manager_integration.update_progress(phase, 100.0)
        assert phase_manager_integration.complete_phase(phase) is True
    
    # Verify all phases in history
    history = phase_manager_integration.get_phase_history()
    assert len(history) == 5
    
    # Verify all phases completed
    all_progress = phase_manager_integration.get_all_progress()
    for phase in phases:
        assert all_progress[phase].status == OrchestratorStatus.COMPLETED


# ============================================================================
# Domain Model Tests
# ============================================================================

def test_phase_transition_creation():
    """Test PhaseTransition dataclass creation."""
    transition = PhaseTransition(
        from_phase="DISCOVERY",
        to_phase="PLANNING",
        success=True
    )
    
    assert transition.from_phase == "DISCOVERY"
    assert transition.to_phase == "PLANNING"
    assert transition.success is True
    assert transition.timestamp is not None
    assert transition.errors == []


def test_phase_progress_creation():
    """Test PhaseProgress dataclass creation."""
    progress = PhaseProgress(
        phase_name="IMPLEMENTATION",
        status=OrchestratorStatus.RUNNING
    )
    
    assert progress.phase_name == "IMPLEMENTATION"
    assert progress.status == OrchestratorStatus.RUNNING
    assert progress.progress_percent == 0.0
    assert progress.metrics == {}


def test_phase_validation_type_enum():
    """Test PhaseValidationType enum values."""
    assert PhaseValidationType.DOR.value == "definition_of_ready"
    assert PhaseValidationType.DOD.value == "definition_of_done"
    assert PhaseValidationType.QUALITY_GATE.value == "quality_gate"
