"""
Unit tests for PlanExecutor (Week 8 Day 4).

Tests:
- execute_plan workflow (5 phases: Discovery→Planning→Implementation→Validation→Completion)
- Execution modes (AUTONOMOUS, SUPERVISED, HUMAN_IN_LOOP)
- Phase progression and transitions
- Error handling and rollback scenarios
- DoR/DoD validation
- Session resumption (resume_from_phase)

Coverage target: 85%+
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import execution engine modules
from src.orchestrators.planning.plan_executor import (
    PlanExecutor,
    ExecutionMode,
    ExecutionPhase,
    ExecutionStatus,
    ExecutionContext,
    PhaseExecutionResult,
    ExecutionResult,
    PhaseExecutor
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def workspace_root(tmp_path):
    """Temporary workspace directory."""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    return str(workspace)


@pytest.fixture
def output_dir(tmp_path):
    """Temporary output directory."""
    output = tmp_path / "test_output"
    output.mkdir()
    return str(output)


@pytest.fixture
def mock_logger():
    """Mock logger instance."""
    logger = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    return logger


@pytest.fixture
def sample_plan_data():
    """Sample plan data for testing."""
    return {
        "plan_metadata": {
            "title": "Test Plan",
            "complexity": "MEDIUM",
            "tdd_required": True
        },
        "phases": {
            "discovery": {"tasks": ["analyze requirements"]},
            "planning": {"tasks": ["design architecture"]},
            "implementation": {"tasks": ["write code"]},
            "validation": {"tasks": ["run tests"]},
            "completion": {"tasks": ["generate report"]}
        }
    }


@pytest.fixture
def plan_path(tmp_path):
    """Sample plan file path."""
    return str(tmp_path / "test_plan.yaml")


@pytest.fixture
def plan_executor(workspace_root, output_dir, mock_logger):
    """PlanExecutor instance with mocked dependencies."""
    return PlanExecutor(
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        logger_instance=mock_logger
    )


def mock_phase_result_success_factory(phase: ExecutionPhase):
    """Factory for mock successful phase result."""
    return PhaseExecutionResult(
        phase=phase,
        status=ExecutionStatus.COMPLETED,
        success=True,
        message=f"Phase {phase.value} completed successfully",
        data={"result": "success"},
        execution_time_seconds=1.5,
        errors=[],
        warnings=[]
    )


@pytest.fixture
def mock_phase_result_failure():
    """Mock failed phase result."""
    return PhaseExecutionResult(
        phase=ExecutionPhase.IMPLEMENTATION,
        status=ExecutionStatus.FAILED,
        success=False,
        message="Phase failed due to error",
        data={},
        execution_time_seconds=0.8,
        errors=["Test error message"],
        warnings=[]
    )


# ============================================================================
# PlanExecutor Initialization Tests
# ============================================================================

def test_plan_executor_init(workspace_root, output_dir, mock_logger):
    """Test PlanExecutor initialization."""
    executor = PlanExecutor(
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.SUPERVISED,
        logger_instance=mock_logger
    )
    
    assert executor.workspace_root == str(workspace_root)
    assert executor.output_dir == str(output_dir)
    assert executor.execution_mode == ExecutionMode.SUPERVISED
    assert executor.logger == mock_logger
    assert executor._phase_executors == {}


def test_plan_executor_init_default_mode(workspace_root, output_dir, mock_logger):
    """Test PlanExecutor initialization with default AUTONOMOUS mode."""
    executor = PlanExecutor(
        workspace_root=workspace_root,
        output_dir=output_dir,
        logger_instance=mock_logger
    )
    
    assert executor.execution_mode == ExecutionMode.AUTONOMOUS


# ============================================================================
# execute_plan Tests - Success Path
# ============================================================================

@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_success_all_phases(
    mock_phase_executor_class,
    plan_executor,
    sample_plan_data,
    plan_path
):
    """Test successful execution of all 5 phases."""
    # Create a mock that returns different phase results based on the phase
    mock_executor_instance = Mock()
    
    # Track which phases are called
    phases_executed = []
    
    def execute_side_effect(context):
        # Get the current phase from context
        phase = context.current_phase
        phases_executed.append(phase)
        return mock_phase_result_success_factory(phase)
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Execute plan
    result = plan_executor.execute_plan(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        auto_checkpoint=False  # Disable checkpoints for simpler test
    )
    
    # Assertions
    assert result.success is True
    assert result.status == ExecutionStatus.COMPLETED
    assert "completed successfully" in result.message.lower()
    assert len(result.phase_results) == 5  # All 5 phases executed
    assert result.total_execution_time_seconds > 0
    
    # Verify all phases were executed
    executed_phases = [pr.phase for pr in result.phase_results]
    assert ExecutionPhase.DISCOVERY in executed_phases
    assert ExecutionPhase.PLANNING in executed_phases
    assert ExecutionPhase.IMPLEMENTATION in executed_phases
    assert ExecutionPhase.VALIDATION in executed_phases
    assert ExecutionPhase.COMPLETION in executed_phases


@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_with_checkpoints(
    mock_phase_executor_class,
    plan_executor,
    sample_plan_data,
    plan_path
):
    """Test execution with auto_checkpoint=True."""
    # Mock PhaseExecutor
    mock_executor_instance = Mock()
    
    def execute_side_effect(context):
        return mock_phase_result_success_factory(context.current_phase)
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Execute with checkpoints
    result = plan_executor.execute_plan(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        auto_checkpoint=True
    )
    
    # Assertions
    assert result.success is True
    assert result.checkpoint_created is not None
    assert result.rollback_available is True
    assert len(result.execution_context.checkpoints) > 0


@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_resume_from_phase(
    mock_phase_executor_class,
    plan_executor,
    sample_plan_data,
    plan_path
):
    """Test resuming execution from specific phase."""
    # Mock PhaseExecutor
    mock_executor_instance = Mock()
    
    def execute_side_effect(context):
        return mock_phase_result_success_factory(context.current_phase)
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Resume from IMPLEMENTATION phase
    result = plan_executor.execute_plan(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        resume_from_phase=ExecutionPhase.IMPLEMENTATION,
        auto_checkpoint=False
    )
    
    # Assertions
    assert result.success is True
    assert len(result.phase_results) == 3  # Only IMPLEMENTATION, VALIDATION, COMPLETION
    
    # Verify correct phases executed
    executed_phases = [pr.phase for pr in result.phase_results]
    assert ExecutionPhase.IMPLEMENTATION in executed_phases
    assert ExecutionPhase.VALIDATION in executed_phases
    assert ExecutionPhase.COMPLETION in executed_phases
    assert ExecutionPhase.DISCOVERY not in executed_phases
    assert ExecutionPhase.PLANNING not in executed_phases


# ============================================================================
# execute_plan Tests - Error Handling
# ============================================================================

@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_phase_failure_no_rollback(
    mock_phase_executor_class,
    plan_executor,
    sample_plan_data,
    plan_path,
    mock_phase_result_failure
):
    """Test execution failure at IMPLEMENTATION phase without checkpoints."""
    # Mock PhaseExecutor: succeed for DISCOVERY/PLANNING, fail at IMPLEMENTATION
    mock_executor_instance = Mock()
    
    call_count = [0]
    
    def execute_side_effect(context):
        call_count[0] += 1
        if call_count[0] <= 2:
            # DISCOVERY and PLANNING succeed
            return mock_phase_result_success_factory(context.current_phase)
        else:
            # IMPLEMENTATION fails
            return mock_phase_result_failure
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Execute without checkpoints
    result = plan_executor.execute_plan(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        auto_checkpoint=False
    )
    
    # Assertions
    assert result.success is False
    assert result.status == ExecutionStatus.FAILED
    assert "failed at phase implementation" in result.message.lower()
    assert result.rollback_available is False
    assert len(result.phase_results) == 3  # Only 3 phases executed before failure


@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_phase_failure_with_rollback(
    mock_phase_executor_class,
    plan_executor,
    sample_plan_data,
    plan_path,
    mock_phase_result_failure
):
    """Test execution failure with rollback to checkpoint."""
    # Mock PhaseExecutor: succeed for DISCOVERY/PLANNING, fail at IMPLEMENTATION
    mock_executor_instance = Mock()
    
    call_count = [0]
    
    def execute_side_effect(context):
        call_count[0] += 1
        if call_count[0] <= 2:
            # DISCOVERY and PLANNING succeed
            return mock_phase_result_success_factory(context.current_phase)
        else:
            # IMPLEMENTATION fails
            return mock_phase_result_failure
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Execute with checkpoints
    result = plan_executor.execute_plan(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        auto_checkpoint=True
    )
    
    # Assertions
    assert result.success is False
    assert result.status == ExecutionStatus.ROLLED_BACK
    assert "failed at phase implementation" in result.message.lower()
    assert result.rollback_available is True


@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_exception_handling(
    mock_phase_executor_class,
    plan_executor,
    sample_plan_data,
    plan_path
):
    """Test exception handling during phase execution."""
    # Mock PhaseExecutor to raise exception
    mock_executor_instance = Mock()
    mock_executor_instance.execute.side_effect = RuntimeError("Critical error")
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Execute plan
    result = plan_executor.execute_plan(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        auto_checkpoint=False
    )
    
    # Assertions
    assert result.success is False
    assert result.status == ExecutionStatus.FAILED
    assert len(result.phase_results) == 1  # Only first phase attempted
    assert result.phase_results[0].success is False
    assert "critical error" in result.phase_results[0].message.lower()


# ============================================================================
# Execution Mode Tests
# ============================================================================

def test_execution_mode_autonomous(workspace_root, output_dir, mock_logger):
    """Test AUTONOMOUS execution mode."""
    executor = PlanExecutor(
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        logger_instance=mock_logger
    )
    
    assert executor.execution_mode == ExecutionMode.AUTONOMOUS


def test_execution_mode_supervised(workspace_root, output_dir, mock_logger):
    """Test SUPERVISED execution mode."""
    executor = PlanExecutor(
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.SUPERVISED,
        logger_instance=mock_logger
    )
    
    assert executor.execution_mode == ExecutionMode.SUPERVISED


def test_execution_mode_human_in_loop(workspace_root, output_dir, mock_logger):
    """Test HUMAN_IN_LOOP execution mode."""
    executor = PlanExecutor(
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.HUMAN_IN_LOOP,
        logger_instance=mock_logger
    )
    
    assert executor.execution_mode == ExecutionMode.HUMAN_IN_LOOP


# ============================================================================
# ExecutionContext Tests
# ============================================================================

def test_execution_context_initialization(
    plan_executor,
    sample_plan_data,
    plan_path,
    workspace_root,
    output_dir
):
    """Test ExecutionContext initialization."""
    context = ExecutionContext(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        current_phase=ExecutionPhase.DISCOVERY
    )
    
    assert context.plan_data == sample_plan_data
    assert context.plan_path == plan_path
    assert context.workspace_root == workspace_root
    assert context.output_dir == output_dir
    assert context.execution_mode == ExecutionMode.AUTONOMOUS
    assert context.current_phase == ExecutionPhase.DISCOVERY
    assert isinstance(context.start_time, datetime)
    assert context.checkpoints == []
    assert context.phase_results == {}
    assert context.errors == []
    assert context.warnings == []


def test_execution_context_resume_from_phase(
    plan_executor,
    sample_plan_data,
    plan_path,
    workspace_root,
    output_dir
):
    """Test ExecutionContext with resume_from_phase."""
    context = ExecutionContext(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        current_phase=ExecutionPhase.VALIDATION  # Resume from VALIDATION
    )
    
    assert context.current_phase == ExecutionPhase.VALIDATION


# ============================================================================
# Phase Progression Tests
# ============================================================================

def test_get_phases_to_execute_all(plan_executor):
    """Test _get_phases_to_execute returns all phases when resume_from=None."""
    phases = plan_executor._get_phases_to_execute(resume_from=None)
    
    assert len(phases) == 5
    assert phases == [
        ExecutionPhase.DISCOVERY,
        ExecutionPhase.PLANNING,
        ExecutionPhase.IMPLEMENTATION,
        ExecutionPhase.VALIDATION,
        ExecutionPhase.COMPLETION
    ]


def test_get_phases_to_execute_from_implementation(plan_executor):
    """Test _get_phases_to_execute with resume_from=IMPLEMENTATION."""
    phases = plan_executor._get_phases_to_execute(resume_from=ExecutionPhase.IMPLEMENTATION)
    
    assert len(phases) == 3
    assert phases == [
        ExecutionPhase.IMPLEMENTATION,
        ExecutionPhase.VALIDATION,
        ExecutionPhase.COMPLETION
    ]


def test_get_phases_to_execute_from_completion(plan_executor):
    """Test _get_phases_to_execute with resume_from=COMPLETION."""
    phases = plan_executor._get_phases_to_execute(resume_from=ExecutionPhase.COMPLETION)
    
    assert len(phases) == 1
    assert phases == [ExecutionPhase.COMPLETION]


# ============================================================================
# PhaseExecutor Tests
# ============================================================================

def test_phase_executor_initialization(mock_logger):
    """Test PhaseExecutor initialization."""
    executor = PhaseExecutor(
        phase=ExecutionPhase.DISCOVERY,
        logger_instance=mock_logger
    )
    
    assert executor.phase == ExecutionPhase.DISCOVERY
    assert executor.logger == mock_logger


@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_get_phase_executor_lazy_initialization(
    mock_phase_executor_class,
    plan_executor
):
    """Test lazy initialization of phase executors."""
    # First call - creates executor
    executor1 = plan_executor._get_phase_executor(ExecutionPhase.DISCOVERY)
    assert ExecutionPhase.DISCOVERY in plan_executor._phase_executors
    
    # Second call - reuses executor
    executor2 = plan_executor._get_phase_executor(ExecutionPhase.DISCOVERY)
    assert executor1 is executor2  # Same instance


# ============================================================================
# Checkpoint Tests (Placeholder)
# ============================================================================

def test_create_checkpoint_placeholder(plan_executor, sample_plan_data, plan_path):
    """Test checkpoint creation (placeholder implementation)."""
    context = ExecutionContext(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        workspace_root=plan_executor.workspace_root,
        output_dir=plan_executor.output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        current_phase=ExecutionPhase.DISCOVERY
    )
    
    checkpoint_id = plan_executor._create_checkpoint(context, "Test checkpoint")
    
    assert checkpoint_id is not None
    assert checkpoint_id.startswith("checkpoint_")


def test_rollback_to_checkpoint_placeholder(plan_executor, sample_plan_data, plan_path):
    """Test rollback to checkpoint (placeholder implementation)."""
    context = ExecutionContext(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        workspace_root=plan_executor.workspace_root,
        output_dir=plan_executor.output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        current_phase=ExecutionPhase.DISCOVERY
    )
    
    result = plan_executor._rollback_to_checkpoint(context, "checkpoint_test")
    
    # Placeholder returns False
    assert result is False


# ============================================================================
# ExecutionResult Tests
# ============================================================================

def test_execution_result_success(
    sample_plan_data,
    plan_path,
    workspace_root,
    output_dir
):
    """Test ExecutionResult for successful execution."""
    context = ExecutionContext(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        current_phase=ExecutionPhase.DISCOVERY
    )
    
    phase_results = [
        PhaseExecutionResult(
            phase=ExecutionPhase.DISCOVERY,
            status=ExecutionStatus.COMPLETED,
            success=True,
            message="Discovery complete",
            execution_time_seconds=1.0
        )
    ]
    
    result = ExecutionResult(
        success=True,
        status=ExecutionStatus.COMPLETED,
        message="All phases complete",
        execution_context=context,
        phase_results=phase_results,
        total_execution_time_seconds=5.0,
        checkpoint_created="checkpoint_123",
        rollback_available=True
    )
    
    assert result.success is True
    assert result.status == ExecutionStatus.COMPLETED
    assert result.checkpoint_created == "checkpoint_123"
    assert result.rollback_available is True
    assert result.total_execution_time_seconds == 5.0


def test_execution_result_failure(
    sample_plan_data,
    plan_path,
    workspace_root,
    output_dir
):
    """Test ExecutionResult for failed execution."""
    context = ExecutionContext(
        plan_data=sample_plan_data,
        plan_path=plan_path,
        workspace_root=workspace_root,
        output_dir=output_dir,
        execution_mode=ExecutionMode.AUTONOMOUS,
        current_phase=ExecutionPhase.IMPLEMENTATION
    )
    
    phase_results = [
        PhaseExecutionResult(
            phase=ExecutionPhase.IMPLEMENTATION,
            status=ExecutionStatus.FAILED,
            success=False,
            message="Implementation failed",
            execution_time_seconds=2.0,
            errors=["Test error"]
        )
    ]
    
    result = ExecutionResult(
        success=False,
        status=ExecutionStatus.FAILED,
        message="Execution failed at IMPLEMENTATION",
        execution_context=context,
        phase_results=phase_results,
        total_execution_time_seconds=3.0,
        rollback_available=False
    )
    
    assert result.success is False
    assert result.status == ExecutionStatus.FAILED
    assert result.rollback_available is False


# ============================================================================
# Edge Cases
# ============================================================================

@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_empty_plan_data(
    mock_phase_executor_class,
    plan_executor,
    plan_path
):
    """Test execution with empty plan data."""
    empty_plan = {}
    
    # Mock PhaseExecutor
    mock_executor_instance = Mock()
    
    def execute_side_effect(context):
        return mock_phase_result_success_factory(context.current_phase)
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    # Should not crash, may fail gracefully
    result = plan_executor.execute_plan(
        plan_data=empty_plan,
        plan_path=plan_path,
        auto_checkpoint=False
    )
    
    # Result should exist (success/failure depends on implementation)
    assert result is not None
    assert isinstance(result, ExecutionResult)


@patch('src.orchestrators.planning.plan_executor.PhaseExecutor')
def test_execute_plan_missing_phases(
    mock_phase_executor_class,
    plan_executor,
    plan_path
):
    """Test execution with missing phases in plan data."""
    incomplete_plan = {
        "plan_metadata": {"title": "Incomplete Plan"},
        # Missing "phases" key
    }
    
    # Mock PhaseExecutor
    mock_executor_instance = Mock()
    
    def execute_side_effect(context):
        return mock_phase_result_success_factory(context.current_phase)
    
    mock_executor_instance.execute.side_effect = execute_side_effect
    mock_phase_executor_class.return_value = mock_executor_instance
    
    result = plan_executor.execute_plan(
        plan_data=incomplete_plan,
        plan_path=plan_path,
        auto_checkpoint=False
    )
    
    assert result is not None
    assert isinstance(result, ExecutionResult)
