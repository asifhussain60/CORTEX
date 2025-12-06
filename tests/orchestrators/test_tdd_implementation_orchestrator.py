"""
Unit Tests for TDD Implementation Orchestrator - Phase 1

Tests phase management, state tracking, and integration interfaces.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import subprocess
import tempfile
import json
from pathlib import Path
from datetime import datetime, timezone

from src.orchestrators.tdd_implementation_orchestrator import (
    TDDImplementationOrchestrator,
    TDDPhase,
    TDDSessionState
)


class TestTDDSessionState:
    """Test TDDSessionState class."""
    
    def test_init(self):
        """Test session state initialization."""
        state = TDDSessionState(
            session_id="test-session-001",
            feature_name="Test Feature",
            task_id="TASK-001"
        )
        
        assert state.session_id == "test-session-001"
        assert state.feature_name == "Test Feature"
        assert state.task_id == "TASK-001"
        assert state.current_phase == TDDPhase.NOT_STARTED
        assert len(state.phase_history) == 0
        assert len(state.checkpoints) == 0
    
    def test_transition_to(self):
        """Test phase transition."""
        state = TDDSessionState(
            session_id="test-session-001",
            feature_name="Test Feature"
        )
        
        state.transition_to(TDDPhase.RED, checkpoint_id="ckpt-001")
        
        assert state.current_phase == TDDPhase.RED
        assert len(state.phase_history) == 1
        assert state.phase_history[0]["from_phase"] == "not_started"
        assert state.phase_history[0]["to_phase"] == "red"
        assert state.phase_history[0]["checkpoint_id"] == "ckpt-001"
        assert "ckpt-001" in state.checkpoints
    
    def test_can_transition_to_valid_transitions(self):
        """Test valid phase transitions."""
        state = TDDSessionState(
            session_id="test-session-001",
            feature_name="Test Feature"
        )
        
        # NOT_STARTED -> RED (valid)
        allowed, reason = state.can_transition_to(TDDPhase.RED)
        assert allowed is True
        
        # RED -> GREEN (valid)
        state.current_phase = TDDPhase.RED
        allowed, reason = state.can_transition_to(TDDPhase.GREEN)
        assert allowed is True
        
        # GREEN -> REFACTOR (valid)
        state.current_phase = TDDPhase.GREEN
        allowed, reason = state.can_transition_to(TDDPhase.REFACTOR)
        assert allowed is True
        
        # REFACTOR -> COMPLETE (valid)
        state.current_phase = TDDPhase.REFACTOR
        allowed, reason = state.can_transition_to(TDDPhase.COMPLETE)
        assert allowed is True
    
    def test_can_transition_to_invalid_transitions(self):
        """Test invalid phase transitions are blocked."""
        state = TDDSessionState(
            session_id="test-session-001",
            feature_name="Test Feature"
        )
        
        # NOT_STARTED -> GREEN (invalid, must go through RED)
        allowed, reason = state.can_transition_to(TDDPhase.GREEN)
        assert allowed is False
        assert "Cannot transition" in reason
        
        # NOT_STARTED -> REFACTOR (invalid)
        allowed, reason = state.can_transition_to(TDDPhase.REFACTOR)
        assert allowed is False
        
        # RED -> REFACTOR (invalid, must go through GREEN)
        state.current_phase = TDDPhase.RED
        allowed, reason = state.can_transition_to(TDDPhase.REFACTOR)
        assert allowed is False
    
    def test_to_dict(self):
        """Test state serialization."""
        state = TDDSessionState(
            session_id="test-session-001",
            feature_name="Test Feature",
            task_id="TASK-001"
        )
        
        state.transition_to(TDDPhase.RED, checkpoint_id="ckpt-001")
        state.implementation_scope = [Path("/path/to/file.py")]
        state.metrics["duplicates_removed"] = 5
        
        data = state.to_dict()
        
        assert data["session_id"] == "test-session-001"
        assert data["feature_name"] == "Test Feature"
        assert data["task_id"] == "TASK-001"
        assert data["current_phase"] == "red"
        assert len(data["phase_history"]) == 1
        assert data["metrics"]["duplicates_removed"] == 5
        assert len(data["implementation_scope"]) == 1


class TestTDDImplementationOrchestrator:
    """Test TDDImplementationOrchestrator class."""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test-project"
            project_root.mkdir()
            
            # Create cortex-brain structure
            cortex_brain = project_root / "cortex-brain"
            cortex_brain.mkdir()
            
            yield project_root
    
    def test_init(self, temp_project):
        """Test orchestrator initialization."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        assert orchestrator.project_root == temp_project
        assert orchestrator.cortex_root == temp_project
        assert len(orchestrator.active_sessions) == 0
        assert orchestrator.sessions_dir.exists()
    
    def test_start_session(self, temp_project):
        """Test starting TDD session."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(
            feature_name="User Authentication",
            task_id="TASK-001"
        )
        
        assert result["success"] is True
        assert "session_id" in result
        assert result["feature_name"] == "User Authentication"
        assert result["current_phase"] == "not_started"
        
        # Verify session stored
        session_id = result["session_id"]
        assert session_id in orchestrator.active_sessions
        
        # Verify session file created
        session_file = orchestrator.sessions_dir / f"{session_id}.json"
        assert session_file.exists()
    
    def test_get_session(self, temp_project):
        """Test retrieving session."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Get session
        state = orchestrator.get_session(session_id)
        assert state is not None
        assert state.session_id == session_id
        assert state.feature_name == "Test Feature"
        
        # Get non-existent session
        state = orchestrator.get_session("invalid-session")
        assert state is None
    
    def test_validate_phase_transition_valid(self, temp_project):
        """Test valid phase transition validation."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Validate NOT_STARTED -> RED
        allowed, reason, state = orchestrator._validate_phase_transition(
            session_id, TDDPhase.RED
        )
        assert allowed is True
        assert state is not None
    
    def test_validate_phase_transition_invalid(self, temp_project):
        """Test invalid phase transition validation."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Try to skip to GREEN without RED
        allowed, reason, state = orchestrator._validate_phase_transition(
            session_id, TDDPhase.GREEN
        )
        assert allowed is False
        assert "Cannot transition" in reason
    
    def test_validate_phase_transition_invalid_session(self, temp_project):
        """Test phase transition with invalid session."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Try with non-existent session
        allowed, reason, state = orchestrator._validate_phase_transition(
            "invalid-session", TDDPhase.RED
        )
        assert allowed is False
        assert "not found" in reason
        assert state is None
    
    def test_execute_red_phase_valid_transition(self, temp_project):
        """Test RED phase execution with valid transition."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Execute RED phase
        red_result = orchestrator.execute_red_phase(session_id=session_id)
        
        # Phase 1: Implementation pending, but structure should work
        assert "phase" in red_result
        assert red_result["phase"] == "RED"
    
    def test_execute_red_phase_invalid_transition(self, temp_project):
        """Test RED phase execution blocks invalid transition."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Manually advance to GREEN (skip RED validation for test)
        state = orchestrator.get_session(session_id)
        state.current_phase = TDDPhase.GREEN
        
        # Try to execute RED again
        red_result = orchestrator.execute_red_phase(session_id=session_id)
        
        assert red_result["success"] is False
        assert "Cannot start RED phase" in red_result["message"]
    
    def test_execute_green_phase_valid_transition(self, temp_project):
        """Test GREEN phase execution with valid transition."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Advance to RED
        state = orchestrator.get_session(session_id)
        state.current_phase = TDDPhase.RED
        
        # Execute GREEN phase
        green_result = orchestrator.execute_green_phase(session_id=session_id)
        
        assert "phase" in green_result
        assert green_result["phase"] == "GREEN"
    
    def test_execute_refactor_phase_valid_transition(self, temp_project):
        """Test REFACTOR phase execution with valid transition."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Advance to GREEN
        state = orchestrator.get_session(session_id)
        state.current_phase = TDDPhase.GREEN
        
        # Execute REFACTOR phase
        refactor_result = orchestrator.execute_refactor_phase(session_id=session_id)
        
        assert "phase" in refactor_result
        assert refactor_result["phase"] == "REFACTOR"
    
    def test_complete_session(self, temp_project):
        """Test session completion."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Advance to REFACTOR
        state = orchestrator.get_session(session_id)
        state.current_phase = TDDPhase.REFACTOR
        
        # Complete session
        complete_result = orchestrator.complete_session(session_id=session_id)
        
        assert complete_result["success"] is True
        assert complete_result["feature_name"] == "Test Feature"
        assert "metrics" in complete_result
        assert "phase_history" in complete_result
        assert "duration_seconds" in complete_result
        
        # Verify removed from active sessions
        assert session_id not in orchestrator.active_sessions
    
    def test_complete_session_invalid_phase(self, temp_project):
        """Test session completion blocked in early phases."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Try to complete in NOT_STARTED phase
        complete_result = orchestrator.complete_session(session_id=session_id)
        
        assert complete_result["success"] is False
        assert "Cannot complete session" in complete_result["message"]
    
    def test_rollback_to_checkpoint(self, temp_project):
        """Test checkpoint rollback (structure only, implementation pending)."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        result = orchestrator.start_session(feature_name="Test Feature")
        session_id = result["session_id"]
        
        # Add checkpoint to state
        state = orchestrator.get_session(session_id)
        state.checkpoints.append("ckpt-001")
        
        # Rollback (now implemented)
        rollback_result = orchestrator.rollback_to_checkpoint(
            session_id=session_id,
            checkpoint_id="ckpt-001"
        )
        
        # Will fail without git history, but structure is correct
        assert "success" in rollback_result
        assert "message" in rollback_result


class TestPhase2RedGreen:
    """Test Phase 2: RED and GREEN phase implementation."""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir) / "test-project"
            project_root.mkdir()
            
            # Create cortex-brain structure
            cortex_brain = project_root / "cortex-brain"
            cortex_brain.mkdir()
            
            # Initialize git repo
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            
            # Create initial commit
            (project_root / "README.md").write_text("# Test Project")
            subprocess.run(["git", "add", "."], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=project_root, check=True, capture_output=True)
            
            yield project_root
    
    def test_detect_test_command(self, temp_project):
        """Test test command auto-detection."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Create pytest.ini
        (temp_project / "pytest.ini").write_text("[pytest]\\n")
        
        command = orchestrator._detect_test_command()
        assert "pytest" in command
        
        command_with_cov = orchestrator._detect_test_command(with_coverage=True)
        assert "pytest" in command_with_cov
        assert "--cov" in command_with_cov
    
    def test_parse_test_output(self, temp_project):
        """Test parsing pytest output."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Test passed output
        output = "===== 18 passed in 0.30s ====="
        passed, failed, total = orchestrator._parse_test_output(output)
        assert passed == 18
        assert failed == 0
        assert total == 18
        
        # Test mixed output
        output = "===== 5 failed, 13 passed in 1.20s ====="
        passed, failed, total = orchestrator._parse_test_output(output)
        assert passed == 13
        assert failed == 5
        assert total == 18
    
    def test_extract_failing_tests(self, temp_project):
        """Test extracting failing test names."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        output = """
        tests/test_foo.py::TestFoo::test_bar FAILED
        tests/test_baz.py::test_qux FAILED
        tests/test_ok.py::test_passes PASSED
        """
        
        failing = orchestrator._extract_failing_tests(output)
        assert len(failing) == 2
        assert "tests/test_foo.py::TestFoo::test_bar" in failing
        assert "tests/test_baz.py::test_qux" in failing
    
    def test_extract_coverage(self, temp_project):
        """Test extracting coverage percentage."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Pytest-cov format - TOTAL with percentage
        output = "TOTAL                       80     15    81%"
        coverage = orchestrator._extract_coverage(output)
        assert coverage == 81.0
        
        # Alternative format
        output2 = "TOTAL  100%"
        coverage2 = orchestrator._extract_coverage(output2)
        assert coverage2 == 100.0
    
    def test_get_changed_files(self, temp_project):
        """Test getting changed files from git."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Create and modify file
        test_file = temp_project / "test.py"
        test_file.write_text("print('hello')")
        
        changed = orchestrator._get_changed_files()
        # Should detect unstaged change (if git tracks it)
        assert isinstance(changed, list)
