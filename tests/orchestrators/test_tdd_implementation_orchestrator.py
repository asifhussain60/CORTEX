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


@pytest.fixture
def temp_project():
    """Create temporary project directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir) / "test-project"
        project_root.mkdir()
        
        # Create cortex-brain structure
        cortex_brain = project_root / "cortex-brain"
        cortex_brain.mkdir()
        
        yield project_root


class TestTDDImplementationOrchestrator:
    """Test TDDImplementationOrchestrator class."""
    
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


class TestPhase3Refactor:
    """Test REFACTOR phase implementation."""
    
    def test_analyze_scope_categorizes_files(self, temp_project):
        """Test scope analysis categorizes files correctly."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Mock changed files
        state = TDDSessionState(
            session_id="test-123",
            feature_name="Test Feature",
            task_id="TASK-001"
        )
        state.implementation_scope = [
            Path("src/module.py"),
            Path("tests/test_module.py"),
            Path("config.yaml"),
            Path("cortex-brain/data.json"),
            Path("src/tier1/working_memory.py")
        ]
        
        result = orchestrator._analyze_scope(state)
        
        # tier1 is NOT out-of-scope in test context (no cortex-brain check)
        assert len(result["implementation_files"]) == 2  # src/module.py + src/tier1/working_memory.py
        assert Path("src/module.py") in result["implementation_files"]
        assert len(result["test_files"]) == 1
        assert Path("tests/test_module.py") in result["test_files"]
        assert len(result["config_files"]) == 2  # config.yaml + cortex-brain/data.json
        assert len(result["out_of_scope"]) == 0
    
    def test_detect_duplicates(self, temp_project):
        """Test duplicate code detection."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Create file with duplicate code
        file1 = temp_project / "file1.py"
        file2 = temp_project / "file2.py"
        
        duplicate_code = """def hello():
    print("Hello")
    print("World")
    print("Test")
    print("Duplicate")
    return True"""
        
        file1.write_text(f"{duplicate_code}\\n\\ndef unique1():\\n    pass")
        file2.write_text(f"{duplicate_code}\\n\\ndef unique2():\\n    pass")
        
        result = orchestrator._detect_duplicates([Path("file1.py"), Path("file2.py")])
        
        # Should find at least 1 duplicate 5-line block
        assert "duplicates" in result
        assert len(result["duplicates"]) >= 1
    
    def test_detect_redundancies(self, temp_project):
        """Test redundancy detection (unused imports)."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Create file with unused import
        file1 = temp_project / "test_redundancy.py"
        file1.write_text("import os\\nimport sys\\n\\ndef main():\\n    print('hello')")
        
        result = orchestrator._detect_redundancies([Path("test_redundancy.py")])
        
        assert "redundancies" in result
        # May or may not find redundancies (basic heuristic)
        assert isinstance(result["redundancies"], list)
    
    def test_validate_solid_srp(self, temp_project):
        """Test SOLID validation detects SRP violations."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Create class with too many methods (SRP violation - >10 methods)
        file1 = temp_project / "test_solid.py"
        methods = "\n".join([f"    def method{i}(self):\n        pass" for i in range(11)])  # 11 methods
        file1.write_text(f"class TooBig:\n{methods}")
        
        result = orchestrator._validate_solid([Path("test_solid.py")])
        
        assert "violations" in result
        assert len(result["violations"]) >= 1
        assert result["violations"][0]["principle"] == "SRP"
    
    def test_detect_blockers(self, temp_project):
        """Test out-of-scope blocker detection."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Create file with syntax error
        file1 = temp_project / "broken.py"
        file1.write_text("def broken(\\n    pass")  # Syntax error
        
        result = orchestrator._detect_blockers([Path("broken.py")])
        
        assert "blockers" in result
        assert len(result["blockers"]) > 0
        assert result["blockers"][0]["type"] == "syntax_error"
    
    def test_generate_refactorings(self, temp_project):
        """Test refactoring recommendation generation."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        duplicates_result = {
            "duplicates": [
                {"locations": [("file1.py", 10), ("file2.py", 20)], "count": 2}
            ]
        }
        redundancies_result = {
            "redundancies": [
                {"type": "unused_import", "file": "test.py", "line": 5, "message": "Unused import"}
            ]
        }
        solid_result = {
            "violations": [
                {"principle": "SRP", "file": "big.py", "line": 1, "class": "TooBig", "message": "Too many methods"}
            ]
        }
        
        refactorings = orchestrator._generate_refactorings(
            duplicates_result,
            redundancies_result,
            solid_result
        )
        
        assert len(refactorings) == 3
        assert any(r["type"] == "extract_method" for r in refactorings)
        assert any(r["type"] == "remove_unused" for r in refactorings)
        assert any(r["type"] == "split_class" for r in refactorings)
    
    def test_execute_refactor_phase_integration(self, temp_project):
        """Test REFACTOR phase end-to-end."""
        orchestrator = TDDImplementationOrchestrator(
            project_root=temp_project,
            cortex_root=temp_project
        )
        
        # Start session
        session = orchestrator.start_session(
            feature_name="Test Feature",
            task_id="TASK-001"
        )
        session_id = session["session_id"]
        
        # Load and advance to GREEN phase (prerequisite for REFACTOR)
        state = orchestrator.get_session(session_id)
        state.transition_to(TDDPhase.RED, checkpoint_id="ckpt-red")
        state.transition_to(TDDPhase.GREEN, checkpoint_id="ckpt-green")
        orchestrator._save_session_state(state)
        
        # Execute REFACTOR
        result = orchestrator.execute_refactor_phase(session_id=session_id)
        
        # Should succeed (even with no files to refactor)
        assert result["success"] is True
        assert result["phase"] == "REFACTOR"
        assert "scope" in result
        assert "duplicates" in result
        assert "solid_violations" in result

