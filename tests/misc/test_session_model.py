"""
Unit Tests for Session Model

Tests all session types from Phase 3: Unified Session Model.

Version: 1.0.0
Author: Asif Hussain
"""

import pytest
from datetime import datetime
from src.orchestrators.session_model import (
    SessionStatus,
    TDDPhase,
    ExecutionMode,
    BaseSession,
    TDDSession,
    PlanningSession,
    ExecutionSession,
    GitCheckpointSession,
    PhaseExecution,
    SessionFactory
)


# ============================================================================
# SessionStatus Tests
# ============================================================================

def test_session_status_is_active():
    """Test is_active() for various statuses."""
    assert SessionStatus.IN_PROGRESS.is_active() is True
    assert SessionStatus.AWAITING_APPROVAL.is_active() is True
    assert SessionStatus.COMPLETED.is_active() is False
    assert SessionStatus.FAILED.is_active() is False


def test_session_status_is_terminal():
    """Test is_terminal() for various statuses."""
    assert SessionStatus.COMPLETED.is_terminal() is True
    assert SessionStatus.FAILED.is_terminal() is True
    assert SessionStatus.CANCELLED.is_terminal() is True
    assert SessionStatus.IN_PROGRESS.is_terminal() is False


# ============================================================================
# BaseSession Tests
# ============================================================================

def test_base_session_creation():
    """Test BaseSession initialization."""
    session = BaseSession(
        session_id="test-123",
        session_type="test",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now()
    )
    
    assert session.session_id == "test-123"
    assert session.status == SessionStatus.IN_PROGRESS
    assert session.completed_at is None


def test_base_session_complete_success():
    """Test completing session successfully."""
    session = BaseSession(
        session_id="test-123",
        session_type="test",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now()
    )
    
    session.complete(success=True)
    
    assert session.status == SessionStatus.COMPLETED
    assert session.completed_at is not None


def test_base_session_complete_failure():
    """Test completing session with failure."""
    session = BaseSession(
        session_id="test-123",
        session_type="test",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now()
    )
    
    session.complete(success=False, error_message="Test error")
    
    assert session.status == SessionStatus.FAILED
    assert session.error_message == "Test error"


def test_base_session_serialization():
    """Test session to_dict() and to_json()."""
    session = BaseSession(
        session_id="test-123",
        session_type="test",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now()
    )
    
    session_dict = session.to_dict()
    assert session_dict["session_id"] == "test-123"
    assert session_dict["status"] == "in_progress"
    
    session_json = session.to_json()
    assert "test-123" in session_json


def test_base_session_pause_resume():
    """Test pause/resume functionality."""
    session = BaseSession(
        session_id="test-123",
        session_type="test",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now()
    )
    
    session.pause()
    assert session.status == SessionStatus.PAUSED
    assert "paused_at" in session.metadata
    
    session.resume()
    assert session.status == SessionStatus.IN_PROGRESS
    assert "resumed_at" in session.metadata


# ============================================================================
# TDDSession Tests
# ============================================================================

def test_tdd_session_creation():
    """Test TDDSession initialization."""
    session = TDDSession(
        session_id="tdd-123",
        session_type="tdd",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        feature_name="User Authentication"
    )
    
    assert session.feature_name == "User Authentication"
    assert session.current_phase == TDDPhase.NOT_STARTED
    assert session.auto_debug_enabled is True


def test_tdd_session_phase_transition():
    """Test TDD phase transitions."""
    session = TDDSession(
        session_id="tdd-123",
        session_type="tdd",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        feature_name="Test Feature"
    )
    
    session.transition_to_phase(TDDPhase.RED, checkpoint_id="chk-001")
    
    assert session.current_phase == TDDPhase.RED
    assert len(session.phase_history) == 1
    assert session.phase_history[0]["to_phase"] == "red"
    assert session.phase_history[0]["checkpoint_id"] == "chk-001"
    assert "chk-001" in session.checkpoints


def test_tdd_session_serialization():
    """Test TDDSession serialization."""
    session = TDDSession(
        session_id="tdd-123",
        session_type="tdd",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        feature_name="Test Feature"
    )
    
    session.transition_to_phase(TDDPhase.RED)
    
    session_dict = session.to_dict()
    assert session_dict["current_phase"] == "red"
    assert session_dict["feature_name"] == "Test Feature"


# ============================================================================
# PlanningSession Tests
# ============================================================================

def test_planning_session_creation():
    """Test PlanningSession initialization."""
    session = PlanningSession(
        session_id="plan-123",
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title="New Feature"
    )
    
    assert session.plan_title == "New Feature"
    assert session.planning_mode_active is False
    assert session.approved is False


def test_planning_session_add_phase():
    """Test adding phases to planning session."""
    session = PlanningSession(
        session_id="plan-123",
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title="New Feature"
    )
    
    session.add_phase("Implementation", [
        {"description": "Task 1"},
        {"description": "Task 2"}
    ])
    
    assert len(session.phases) == 1
    assert session.phases[0]["name"] == "Implementation"
    assert len(session.phases[0]["tasks"]) == 2


def test_planning_session_validation():
    """Test plan validation."""
    session = PlanningSession(
        session_id="plan-123",
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title=""  # Invalid: empty title
    )
    
    is_valid = session.validate_plan()
    
    assert is_valid is False
    assert len(session.validation_errors) > 0


def test_planning_session_approval():
    """Test plan approval."""
    session = PlanningSession(
        session_id="plan-123",
        session_type="planning",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_title="Valid Plan"
    )
    
    session.add_phase("Phase 1", [{"description": "Task 1"}])
    session.dor_items = ["DOR 1"]
    session.dod_items = ["DOD 1"]
    
    is_valid = session.validate_plan()
    assert is_valid is True
    
    session.approve()
    assert session.approved is True
    assert "approved_at" in session.metadata


# ============================================================================
# ExecutionSession Tests
# ============================================================================

def test_execution_session_creation():
    """Test ExecutionSession initialization."""
    session = ExecutionSession(
        session_id="exec-123",
        session_type="execution",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_path="/path/to/plan.yaml"
    )
    
    assert session.plan_path == "/path/to/plan.yaml"
    assert session.execution_mode == ExecutionMode.APPROVAL_GATED
    assert session.awaiting_approval is False


def test_execution_session_phase_execution():
    """Test phase execution tracking."""
    session = ExecutionSession(
        session_id="exec-123",
        session_type="execution",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_path="/path/to/plan.yaml",
        total_phases=3
    )
    
    # Start phase
    phase_exec = session.start_phase("Implementation")
    assert len(session.phases_executed) == 1
    assert phase_exec.status == SessionStatus.IN_PROGRESS
    
    # Complete phase
    phase_exec.tasks_completed = 5
    session.complete_phase(success=True)
    assert session.phases_executed[0].status == SessionStatus.COMPLETED
    assert session.total_tasks_completed == 5
    assert session.current_phase_index == 1


def test_execution_session_progress():
    """Test progress calculation."""
    session = ExecutionSession(
        session_id="exec-123",
        session_type="execution",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_path="/path/to/plan.yaml",
        total_phases=4
    )
    
    assert session.get_progress_percentage() == 0.0
    
    session.current_phase_index = 2
    assert session.get_progress_percentage() == 50.0
    
    session.current_phase_index = 4
    assert session.get_progress_percentage() == 100.0


def test_execution_session_approval_gate():
    """Test approval gating."""
    session = ExecutionSession(
        session_id="exec-123",
        session_type="execution",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        plan_path="/path/to/plan.yaml"
    )
    
    session.request_approval()
    assert session.awaiting_approval is True
    assert session.status == SessionStatus.AWAITING_APPROVAL
    
    session.grant_approval()
    assert session.awaiting_approval is False
    assert session.status == SessionStatus.IN_PROGRESS


# ============================================================================
# GitCheckpointSession Tests
# ============================================================================

def test_git_checkpoint_session_creation():
    """Test GitCheckpointSession initialization."""
    session = GitCheckpointSession(
        session_id="git-123",
        session_type="git_checkpoint",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        commit_message="Test commit"
    )
    
    assert session.commit_message == "Test commit"
    assert session.rollback_available is True


def test_git_checkpoint_record_commit():
    """Test recording commit."""
    session = GitCheckpointSession(
        session_id="git-123",
        session_type="git_checkpoint",
        status=SessionStatus.IN_PROGRESS,
        started_at=datetime.now(),
        commit_message="Test commit"
    )
    
    session.record_commit(
        commit_sha="abc123def456",
        files_changed=["file1.py", "file2.py"]
    )
    
    assert session.commit_sha == "abc123def456"
    assert len(session.files_changed) == 2
    assert "committed_at" in session.metadata


# ============================================================================
# SessionFactory Tests
# ============================================================================

def test_session_factory_tdd():
    """Test SessionFactory creates TDD session."""
    session = SessionFactory.create_tdd_session("Test Feature")
    
    assert isinstance(session, TDDSession)
    assert session.feature_name == "Test Feature"
    assert session.session_type == "tdd"
    assert len(session.session_id) > 0


def test_session_factory_planning():
    """Test SessionFactory creates planning session."""
    session = SessionFactory.create_planning_session("Test Plan")
    
    assert isinstance(session, PlanningSession)
    assert session.plan_title == "Test Plan"
    assert session.planning_mode_active is True


def test_session_factory_execution():
    """Test SessionFactory creates execution session."""
    session = SessionFactory.create_execution_session(
        "/path/to/plan.yaml",
        mode=ExecutionMode.AUTONOMOUS
    )
    
    assert isinstance(session, ExecutionSession)
    assert session.plan_path == "/path/to/plan.yaml"
    assert session.execution_mode == ExecutionMode.AUTONOMOUS


def test_session_factory_git_checkpoint():
    """Test SessionFactory creates git checkpoint session."""
    session = SessionFactory.create_git_checkpoint_session("Initial commit")
    
    assert isinstance(session, GitCheckpointSession)
    assert session.commit_message == "Initial commit"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
