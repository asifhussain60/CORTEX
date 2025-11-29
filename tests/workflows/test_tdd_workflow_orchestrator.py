"""
Tests for TDD Workflow Orchestrator (Milestone 3.1)

Validates end-to-end TDD workflow integration.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 3 - Milestone 3.1
"""

import pytest
import tempfile
from pathlib import Path
from src.workflows.tdd_workflow_orchestrator import (
    TDDWorkflowOrchestrator,
    TDDWorkflowConfig
)
from src.workflows.page_tracking import PageLocation


class TestTDDWorkflowOrchestrator:
    """Test complete TDD workflow orchestration."""
    
    def test_start_session(self):
        """Should start new TDD session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            session_id = orchestrator.start_session("test_feature")
            
            assert session_id is not None
            assert session_id.startswith("tdd_")
            assert orchestrator.current_session_id == session_id
    
    def test_generate_tests_red_phase(self):
        """Should generate tests in RED phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create sample source file
            source_file = Path(tmpdir) / "calculator.py"
            source_file.write_text("""
def add(a: int, b: int) -> int:
    '''Add two numbers.'''
    return a + b

def multiply(a: int, b: int) -> int:
    '''Multiply two numbers.'''
    return a * b
""")
            
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            orchestrator.start_session("calculator_tests")
            
            # Generate tests
            result = orchestrator.generate_tests(
                source_file=str(source_file),
                function_name="add"
            )
            
            assert result["phase"] == "RED"
            assert result["test_count"] > 0
            assert len(result["tests"]) > 0
            assert "test_code" in result["tests"][0]
    
    def test_verify_tests_pass_green_phase(self):
        """Should verify tests pass in GREEN phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "simple.py"
            source_file.write_text("def foo(): return True")
            
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            orchestrator.start_session("test_session")
            orchestrator.generate_tests(str(source_file))
            
            # Simulate passing tests
            test_results = {
                "passed": 5,
                "code_lines": 20
            }
            
            assert orchestrator.verify_tests_pass(test_results)
    
    def test_suggest_refactorings_refactor_phase(self):
        """Should suggest refactorings in REFACTOR phase."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create source with code smell
            source_file = Path(tmpdir) / "smelly.py"
            source_file.write_text("""
def long_method():
    # This method is very long
    line1 = 1
    line2 = 2
    line3 = 3
    line4 = 4
    line5 = 5
    line6 = 6
    line7 = 7
    line8 = 8
    line9 = 9
    line10 = 10
    line11 = 11
    line12 = 12
    line13 = 13
    line14 = 14
    line15 = 15
    line16 = 16
    line17 = 17
    line18 = 18
    line19 = 19
    line20 = 20
    line21 = 21
    line22 = 22
    line23 = 23
    line24 = 24
    line25 = 25
    line26 = 26
    line27 = 27
    line28 = 28
    line29 = 29
    line30 = 30
    line31 = 31
    line32 = 32
    return line1 + line32
""")
            
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            orchestrator.start_session("refactor_test")
            orchestrator.generate_tests(str(source_file))
            orchestrator.verify_tests_pass({"passed": 1, "code_lines": 10})
            
            # Get refactoring suggestions
            suggestions = orchestrator.suggest_refactorings(str(source_file))
            
            assert len(suggestions) > 0
            assert "type" in suggestions[0]
            assert "confidence" in suggestions[0]
    
    def test_complete_cycle(self):
        """Should complete full TDD cycle."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "test.py"
            source_file.write_text("def test_func(): return 42")
            
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            orchestrator.start_session("cycle_test")
            orchestrator.generate_tests(str(source_file))
            orchestrator.verify_tests_pass({"passed": 3, "code_lines": 15})
            orchestrator.complete_refactor_phase(lines_refactored=5, iterations=1)
            
            # Complete cycle
            metrics = orchestrator.complete_cycle()
            
            assert "cycle_number" in metrics
            assert metrics["tests_written"] == 3
            assert metrics["tests_passing"] == 3
    
    def test_save_and_resume_progress(self):
        """Should save progress and resume session."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "progress.py"
            source_file.write_text("def work(): pass")
            
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            # Start session and save progress
            orchestrator = TDDWorkflowOrchestrator(config)
            session_id = orchestrator.start_session("progress_test")
            orchestrator.generate_tests(str(source_file))
            
            location = PageLocation(
                filepath=str(source_file),
                line_number=1,
                column_offset=0,
                function_name="work"
            )
            
            assert orchestrator.save_progress(location, "Working on implementation")
            
            # Resume session
            resumed = orchestrator.resume_session(session_id)
            
            assert resumed["session_id"] == session_id
            assert resumed["feature_name"] == "progress_test"
            assert resumed["last_location"]["file"] == str(source_file)
            assert resumed["last_location"]["line"] == 1
    
    def test_get_session_summary(self):
        """Should get session summary with metrics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            source_file = Path(tmpdir) / "summary.py"
            source_file.write_text("def summary(): return 'test'")
            
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            orchestrator.start_session("summary_test")
            orchestrator.generate_tests(str(source_file))
            orchestrator.verify_tests_pass({"passed": 2, "code_lines": 10})
            orchestrator.complete_refactor_phase(lines_refactored=3)
            orchestrator.complete_cycle()
            
            summary = orchestrator.get_session_summary()
            
            assert "feature_name" in summary
            assert summary["total_cycles"] == 1
            assert summary["total_tests_written"] == 2
            assert summary["total_tests_passing"] == 2
    
    def test_list_active_sessions(self):
        """Should list all active sessions."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                session_storage=f"{tmpdir}/sessions.db"
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            
            # Create multiple sessions
            orchestrator.start_session("feature_1")
            orchestrator.save_progress(notes="Session 1")
            
            orchestrator.start_session("feature_2")
            orchestrator.save_progress(notes="Session 2")
            
            # List sessions
            sessions = orchestrator.list_active_sessions()
            
            assert len(sessions) >= 2
            assert all("session_id" in s for s in sessions)
            assert all("feature_name" in s for s in sessions)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
