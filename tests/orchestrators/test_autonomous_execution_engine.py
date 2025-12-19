"""
Tests for Autonomous Execution Engine (Phase 0.5)

Test Coverage:
- Execution modes (supervised, autonomous)
- Phase lifecycle (start, complete, fail)
- Self-healing strategies
- Validation gate integration
- Git automation
- Error escalation
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.autonomous_execution_engine import (
    AutonomousExecutionEngine,
    ExecutionMode,
    PhaseConfig,
    PhaseStatus,
    ValidationGateResult,
    SelfHealingResult
)
from src.orchestrators.base.base_orchestrator import OrchestratorStatus


@pytest.fixture
def mock_config():
    """Mock configuration."""
    return {
        "name": "AutonomousExecutionEngine",
        "version": "4.0.0",
        "workspace_root": "d:/PROJECTS/CORTEX",
        "autonomous_execution": {
            "max_retries": 3,
            "escalation_threshold": 3,
            "enable_git_automation": True
        }
    }


@pytest.fixture
def engine(mock_config):
    """Create autonomous execution engine."""
    return AutonomousExecutionEngine(mock_config)


def test_engine_initialization(engine):
    """Test engine initializes correctly."""
    assert engine.max_retry_attempts == 3
    assert engine.escalation_threshold == 3
    assert engine.enable_git_automation is True
    assert engine.execution_mode == ExecutionMode.SUPERVISED
    assert len(engine.phases) == 0


def test_validate_input_valid(engine):
    """Test input validation with valid parameters."""
    with patch("pathlib.Path.exists", return_value=True):
        result = engine.validate_input(
            plan_path="path/to/plan.md",
            mode="autonomous",
            from_phase=1,
            to_phase=3
        )
    
    assert result.valid is True
    assert len(result.errors) == 0


def test_validate_input_missing_plan(engine):
    """Test validation fails when plan path missing."""
    result = engine.validate_input(mode="autonomous")
    
    assert result.valid is False
    assert "plan_path is required" in result.errors


def test_validate_input_plan_not_found(engine):
    """Test validation fails when plan file doesn't exist."""
    with patch("pathlib.Path.exists", return_value=False):
        result = engine.validate_input(plan_path="nonexistent.md")
    
    assert result.valid is False
    assert "Plan file not found" in result.errors[0]


def test_validate_input_invalid_mode(engine):
    """Test validation fails with invalid execution mode."""
    with patch("pathlib.Path.exists", return_value=True):
        result = engine.validate_input(
            plan_path="plan.md",
            mode="invalid_mode"
        )
    
    assert result.valid is False
    assert "Invalid execution mode" in result.errors[0]


def test_validate_input_invalid_phase_range(engine):
    """Test validation fails with invalid phase range."""
    with patch("pathlib.Path.exists", return_value=True):
        result = engine.validate_input(
            plan_path="plan.md",
            from_phase=5,
            to_phase=3
        )
    
    assert result.valid is False
    assert "to_phase must be >= from_phase" in result.errors[0]


def test_execute_autonomous_mode_success(engine):
    """Test successful autonomous execution."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(engine, "_load_phases_from_plan") as mock_load:
            with patch.object(engine, "_execute_phase") as mock_execute:
                # Setup
                mock_load.return_value = [
                    PhaseConfig(1, "Phase 1", "Description 1"),
                    PhaseConfig(2, "Phase 2", "Description 2")
                ]
                mock_execute.return_value = ValidationGateResult(
                    passed=True,
                    message="Success",
                    test_count=10,
                    tests_passed=10
                )
                
                # Execute
                result = engine.execute(
                    plan_path="plan.md",
                    mode="autonomous"
                )
                
                # Verify
                assert result.success is True
                assert result.status == OrchestratorStatus.COMPLETED
                assert result.data["phases_completed"] == 2
                assert result.data["total_phases"] == 2
                assert result.data["is_complete"] is True


def test_execute_supervised_mode(engine):
    """Test supervised execution mode."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(engine, "_load_phases_from_plan") as mock_load:
            with patch.object(engine, "_execute_phase") as mock_execute:
                mock_load.return_value = [PhaseConfig(1, "Phase 1", "Description 1")]
                mock_execute.return_value = ValidationGateResult(passed=True, message="Success")
                
                result = engine.execute(
                    plan_path="plan.md",
                    mode="supervised"
                )
                
                assert result.success is True
                assert engine.execution_mode == ExecutionMode.SUPERVISED


def test_execute_phase_range(engine):
    """Test execution with phase range (from_phase, to_phase)."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(engine, "_load_phases_from_plan") as mock_load:
            with patch.object(engine, "_execute_phase") as mock_execute:
                mock_load.return_value = [
                    PhaseConfig(1, "Phase 1", "Description 1"),
                    PhaseConfig(2, "Phase 2", "Description 2"),
                    PhaseConfig(3, "Phase 3", "Description 3")
                ]
                mock_execute.return_value = ValidationGateResult(passed=True, message="Success")
                
                result = engine.execute(
                    plan_path="plan.md",
                    mode="autonomous",
                    from_phase=2,
                    to_phase=2
                )
                
                assert result.success is True
                assert result.data["phases_completed"] == 1
                assert mock_execute.call_count == 1


def test_execute_phase_failure_stops_execution(engine):
    """Test execution stops on phase failure."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(engine, "_load_phases_from_plan") as mock_load:
            with patch.object(engine, "_execute_phase") as mock_execute:
                mock_load.return_value = [
                    PhaseConfig(1, "Phase 1", "Description 1"),
                    PhaseConfig(2, "Phase 2", "Description 2")
                ]
                # First phase passes, second fails
                mock_execute.side_effect = [
                    ValidationGateResult(passed=True, message="Success"),
                    ValidationGateResult(passed=False, message="Failed")
                ]
                
                result = engine.execute(
                    plan_path="plan.md",
                    mode="autonomous"
                )
                
                assert result.success is False
                assert result.status == OrchestratorStatus.FAILED
                assert result.data["phases_completed"] == 1
                assert "Phase 2 validation failed" in result.errors


def test_execute_phase_lifecycle(engine):
    """Test phase lifecycle methods are called."""
    phase = PhaseConfig(1, "Test Phase", "Description")
    
    with patch.object(engine, "_on_phase_start") as mock_start:
        with patch.object(engine, "_run_validation_gate") as mock_validate:
            with patch.object(engine, "_on_phase_complete") as mock_complete:
                mock_validate.return_value = ValidationGateResult(passed=True, message="Success")
                
                result = engine._execute_phase(phase)
                
                # Verify lifecycle methods called
                mock_start.assert_called_once_with(phase)
                mock_validate.assert_called()
                mock_complete.assert_called_once()
                assert result.passed is True


def test_execute_phase_self_healing_on_failure(engine):
    """Test self-healing is attempted on validation failure."""
    phase = PhaseConfig(1, "Test Phase", "Description")
    
    with patch.object(engine, "_on_phase_start"):
        with patch.object(engine, "_run_validation_gate") as mock_validate:
            with patch.object(engine, "_self_heal") as mock_heal:
                with patch.object(engine, "_on_validation_fail"):
                    # First validation fails, healing fails
                    mock_validate.return_value = ValidationGateResult(passed=False, message="Failed")
                    mock_heal.return_value = SelfHealingResult(
                        success=False,
                        strategy="retry_with_backoff",
                        attempt=1,
                        message="Healing failed"
                    )
                    
                    result = engine._execute_phase(phase)
                    
                    # Verify self-healing attempted
                    mock_heal.assert_called_once()
                    assert result.passed is False
                    assert phase.status == PhaseStatus.ESCALATED


def test_self_heal_retry_with_backoff(engine):
    """Test self-heal retry with backoff strategy."""
    phase = PhaseConfig(1, "Test Phase", "Description")
    error = ValidationGateResult(passed=False, message="Transient error")
    
    with patch("time.sleep"):  # Mock sleep to speed up test
        result = engine._self_heal(phase, error)
    
    assert result.strategy == "retry_with_backoff"
    assert phase.retry_count == 1


def test_self_heal_max_retries_exceeded(engine):
    """Test self-heal stops after max retries."""
    phase = PhaseConfig(1, "Test Phase", "Description", retry_count=3)
    error = ValidationGateResult(passed=False, message="Error")
    
    result = engine._self_heal(phase, error)
    
    assert result.success is False
    assert "Max retry attempts exceeded" in result.message


def test_checkpoint_creation(engine):
    """Test checkpoint creation."""
    checkpoint_id = engine._create_checkpoint("test_checkpoint")
    
    assert checkpoint_id.startswith("checkpoint_test_checkpoint_")
    assert "test_checkpoint" in engine.checkpoints


def test_rollback_to_checkpoint(engine):
    """Test rollback to checkpoint."""
    checkpoint_id = engine._create_checkpoint("test_checkpoint")
    
    # Rollback doesn't raise error
    engine._rollback_to_checkpoint(checkpoint_id)


def test_filter_phases(engine):
    """Test phase filtering by range."""
    phases = [
        PhaseConfig(1, "Phase 1", "Desc 1"),
        PhaseConfig(2, "Phase 2", "Desc 2"),
        PhaseConfig(3, "Phase 3", "Desc 3"),
        PhaseConfig(4, "Phase 4", "Desc 4")
    ]
    
    # Test from_phase only
    filtered = engine._filter_phases(phases, from_phase=2, to_phase=None)
    assert len(filtered) == 3
    assert filtered[0].number == 2
    
    # Test from_phase and to_phase
    filtered = engine._filter_phases(phases, from_phase=2, to_phase=3)
    assert len(filtered) == 2
    assert filtered[0].number == 2
    assert filtered[1].number == 3


def test_load_phases_from_plan(engine):
    """Test loading phases from master plan."""
    phases = engine._load_phases_from_plan("dummy_plan.md")
    
    # Should return placeholder phases
    assert len(phases) == 3
    assert phases[0].number == 1
    assert phases[0].name == "Foundation"


def test_format_commit_message(engine):
    """Test auto-commit message formatting."""
    phase = PhaseConfig(1, "Test Phase", "Description")
    validation = ValidationGateResult(
        passed=True,
        message="Success",
        test_count=10,
        tests_passed=10,
        coverage_percentage=85.5
    )
    
    message = engine._format_commit_message(phase, validation)
    
    assert "Phase 1" in message
    assert "Test Phase" in message
    assert "PASSED" in message
    assert "10/10" in message
    assert "100.0%" in message
    assert "85.5%" in message


def test_escalate_to_user(engine, caplog):
    """Test escalation creates proper notification."""
    import logging
    phase = PhaseConfig(1, "Test Phase", "Description", retry_count=3)
    error = ValidationGateResult(passed=False, message="Critical error")
    
    # Capture log output
    with caplog.at_level(logging.ERROR):
        engine._escalate_to_user(phase, error)
    
    # Verify error log contains escalation notification
    assert any("AUTONOMOUS EXECUTION PAUSED" in record.message for record in caplog.records)
    assert any("Test Phase" in record.message for record in caplog.records)


def test_validation_gate_result_pass_rate():
    """Test ValidationGateResult pass rate calculation."""
    result = ValidationGateResult(
        passed=True,
        message="Success",
        test_count=10,
        tests_passed=8
    )
    
    assert result.pass_rate == 80.0
    
    # Test zero division
    result_zero = ValidationGateResult(passed=False, message="No tests", test_count=0)
    assert result_zero.pass_rate == 0.0


def test_phase_config_defaults():
    """Test PhaseConfig default values."""
    phase = PhaseConfig(1, "Test", "Description")
    
    assert phase.status == PhaseStatus.PENDING
    assert phase.start_time is None
    assert phase.end_time is None
    assert phase.retry_count == 0
    assert phase.checkpoint_id is None
    assert phase.critical is False


# ===== Integration Tests =====

def test_full_autonomous_execution_flow(engine):
    """Integration test: Full autonomous execution flow."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(engine, "_load_phases_from_plan") as mock_load:
            with patch.object(engine, "_run_validation_gate") as mock_validate:
                with patch.object(engine, "_auto_commit") as mock_commit:
                    # Setup 2 phases, both pass
                    mock_load.return_value = [
                        PhaseConfig(1, "Phase 1", "Setup"),
                        PhaseConfig(2, "Phase 2", "Implementation")
                    ]
                    mock_validate.return_value = ValidationGateResult(
                        passed=True,
                        message="All tests passed",
                        test_count=10,
                        tests_passed=10,
                        coverage_percentage=90.0
                    )
                    
                    # Execute autonomous mode
                    result = engine.execute(
                        plan_path="plan.md",
                        mode="autonomous"
                    )
                    
                    # Verify complete execution
                    assert result.success is True
                    assert result.data["phases_completed"] == 2
                    assert result.data["is_complete"] is True
                    
                    # Verify auto-commit called (autonomous mode)
                    assert mock_commit.call_count == 2


def test_full_execution_with_recovery(engine):
    """Integration test: Execution with successful recovery."""
    with patch("pathlib.Path.exists", return_value=True):
        with patch.object(engine, "_load_phases_from_plan") as mock_load:
            with patch.object(engine, "_run_validation_gate") as mock_validate:
                with patch.object(engine, "_self_heal") as mock_heal:
                    mock_load.return_value = [PhaseConfig(1, "Phase 1", "Test")]
                    
                    # First validation fails, second passes after healing
                    mock_validate.side_effect = [
                        ValidationGateResult(passed=False, message="Failed"),
                        ValidationGateResult(passed=True, message="Success")
                    ]
                    mock_heal.return_value = SelfHealingResult(
                        success=True,
                        strategy="retry_with_backoff",
                        attempt=1,
                        message="Recovered"
                    )
                    
                    result = engine.execute(
                        plan_path="plan.md",
                        mode="autonomous"
                    )
                    
                    assert result.success is True
                    assert result.data["phases_completed"] == 1
                    mock_heal.assert_called_once()
