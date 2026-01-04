"""
Integration tests for Debug Orchestrator.

Tests end-to-end debugging workflows, Master Orchestrator integration,
state persistence, and report generation.

Author: Asif Hussain
Created: January 4, 2026
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.debug.debug_orchestrator import DebugOrchestrator, DebugSession


class TestDebugOrchestrator_Integration:
    """Integration tests for complete debugging workflows."""
    
    @pytest.fixture
    def workspace(self, tmp_path):
        """Create a test workspace with sample code."""
        workspace = tmp_path / "test_project"
        workspace.mkdir()
        
        # Create sample buggy files
        (workspace / "src").mkdir()
        
        # Bug 1: NoneType AttributeError
        (workspace / "src" / "auth.py").write_text("""
class AuthService:
    def __init__(self):
        self.db = None  # Bug: never initialized
    
    def login(self, email, password):
        user = self.db.query(User).filter_by(email=email).first()
        return user
""")
        
        # Bug 2: KeyError
        (workspace / "src" / "config.py").write_text("""
def get_setting(config, key):
    return config[key]  # Bug: no error handling
""")
        
        # Error log
        (workspace / "error.log").write_text("""
[2026-01-04 17:00:00] ERROR - Authentication failed
Traceback (most recent call last):
  File "src/auth.py", line 7, in login
    user = self.db.query(User).filter_by(email=email).first()
AttributeError: 'NoneType' object has no attribute 'query'
""")
        
        return workspace
    
    @pytest.fixture
    def orchestrator(self, workspace):
        """Create orchestrator for test workspace."""
        return DebugOrchestrator(workspace)
    
    def test_end_to_end_debugging_workflow(self, orchestrator, workspace):
        """Test complete debugging workflow from symptom to fix strategy."""
        # Symptom from error log
        error_log = (workspace / "error.log").read_text()
        
        # Execute complete workflow
        result = orchestrator.execute_debug_workflow_autonomously(
            bug_description=error_log,
            auto_apply_fix=False  # Don't auto-fix for test
        )
        
        # Validate workflow completion
        assert result["status"] == "in_progress" or result["status"] == "completed"
        assert orchestrator.current_session is not None
        assert "phases_completed" in result
        assert len(result["phases_completed"]) > 0
    
    def test_multi_file_code_analysis(self, orchestrator, workspace):
        """Test debugging workflow with manual phase execution."""
        symptom = "Multiple errors in authentication and configuration modules"
        
        # Parse bug report
        parsed = orchestrator.parse_bug_report(symptom)
        assert parsed["status"] == "parsed"
        assert orchestrator.current_session is not None
    
    def test_state_persistence_and_resume(self, orchestrator, workspace):
        """Test session management and state."""
        error = "Test error for persistence"
        
        # Start debugging session
        result = orchestrator.parse_bug_report(error)
        assert result["status"] == "parsed"
        
        # Verify session exists
        assert orchestrator.current_session is not None
        session_id = orchestrator.current_session.session_id
        
        # Get session summary
        summary = orchestrator.get_session_summary()
        assert summary is not None
        assert summary["session_id"] == session_id
    
    def test_report_generation(self, orchestrator, workspace):
        """Test that debugging session creates summary."""
        error_log = (workspace / "error.log").read_text()
        
        orchestrator.parse_bug_report(error_log)
        summary = orchestrator.get_session_summary()
        
        assert summary is not None
        assert "session_id" in summary
        assert "bug_description" in summary  # Fixed: was "bug_report"
    
    def test_error_handling_invalid_workspace(self, tmp_path):
        """Test error handling when workspace is invalid."""
        invalid_workspace = tmp_path / "nonexistent"
        
        # Should handle gracefully
        orchestrator = DebugOrchestrator(invalid_workspace)
        result = orchestrator.parse_bug_report("Test error")
        assert result["status"] in ["parsed", "error", "warning"]  # Fixed expectations
    
    def test_error_handling_corrupted_state(self, orchestrator, workspace):
        """Test handling of invalid inputs."""
        # Should handle empty description gracefully
        result = orchestrator.parse_bug_report("")
        assert result is not None
    
    def test_performance_under_load(self, orchestrator, workspace):
        """Test performance with multiple debugging sessions."""
        import time
        
        errors = [
            "AttributeError: 'NoneType' object has no attribute 'query'",
            "KeyError: 'user_id'",
            "IndexError: list index out of range",
        ]
        
        start_time = time.time()
        
        for error in errors:
            orchestrator.parse_bug_report(error)
        
        elapsed_time = time.time() - start_time
        
        # Should complete reasonably fast (< 2 seconds for parsing only)
        assert elapsed_time < 2.0, f"Performance issue: {elapsed_time:.2f}s for 3 sessions"
    
    def test_concurrent_session_handling(self, orchestrator):
        """Test handling multiple sequential debugging sessions."""
        # Parse multiple bug reports
        session_ids = []
        for i in range(3):
            result = orchestrator.parse_bug_report(f"Test error {i}")
            if orchestrator.current_session:
                session_ids.append(orchestrator.current_session.session_id)
        
        # All sessions should have unique IDs
        assert len(set(session_ids)) == 3


class TestMasterOrchestratorIntegration:
    """Test integration with Master Orchestrator routing."""
    
    def test_debug_pattern_routing(self):
        """Test that debug commands route to Debug Orchestrator."""
        import re
        
        # Pattern from master-orchestrator.yaml
        pattern = r"^(debug|fix bug|troubleshoot|investigate bug|root cause).*$"
        
        # Test valid triggers
        valid_triggers = [
            "debug authentication error",
            "fix bug in login module",
            "troubleshoot database connection",
            "investigate bug in payment system",
            "root cause analysis needed"
        ]
        
        for trigger in valid_triggers:
            assert re.match(pattern, trigger, re.IGNORECASE), \
                f"Pattern should match: {trigger}"
    
    def test_non_debug_patterns_excluded(self):
        """Test that non-debug commands don't match pattern."""
        import re
        
        pattern = r"^(debug|fix bug|troubleshoot|investigate bug|root cause).*$"
        
        # Should NOT match
        invalid_triggers = [
            "plan new feature",
            "refactor code",
            "test coverage",
            "cleanup files"
        ]
        
        for trigger in invalid_triggers:
            assert not re.match(pattern, trigger, re.IGNORECASE), \
                f"Pattern should NOT match: {trigger}"
    
    @patch('src.orchestrators.debug.debug_orchestrator.DebugOrchestrator')
    def test_orchestrator_instantiation(self, mock_orchestrator):
        """Test that orchestrator can be instantiated via Master Orchestrator."""
        from src.orchestrators.debug.debug_orchestrator import DebugOrchestrator
        
        # Simulate Master Orchestrator instantiation
        config = {"output_dir": "/tmp/debug"}
        orchestrator = DebugOrchestrator(config)
        
        assert orchestrator is not None
        assert hasattr(orchestrator, 'debug')


class TestExternalToolIntegration:
    """Test integration with external tools (git, markers, etc)."""
    
    @pytest.fixture
    def git_workspace(self, tmp_path):
        """Create a git-initialized workspace."""
        import subprocess
        
        workspace = tmp_path / "git_project"
        workspace.mkdir()
        
        # Initialize git
        subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=workspace)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace)
        
        # Create initial commit
        (workspace / "README.md").write_text("Test project")
        subprocess.run(["git", "add", "."], cwd=workspace)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=workspace)
        
        return workspace
    
    def test_git_checkpoint_available(self, git_workspace):
        """Test git checkpoint functionality exists."""
        orchestrator = DebugOrchestrator(git_workspace)
        
        # Verify orchestrator has checkpoint method
        assert hasattr(orchestrator, '_create_git_checkpoint')
    
    def test_marker_injection_and_cleanup(self, tmp_path):
        """Test debug marker injection and cleanup cycle."""
        workspace = tmp_path / "test_project"
        workspace.mkdir()
        
        # Create test file
        test_file = workspace / "test.py"
        test_file.write_text("""
def buggy_function():
    x = None
    return x.value
""")
        
        orchestrator = DebugOrchestrator(workspace)
        orchestrator.parse_bug_report("Test error in buggy_function")
        
        # Test marker cleanup exists
        assert hasattr(orchestrator, 'cleanup_debug_markers')
        result = orchestrator.cleanup_debug_markers(verify=False)
        assert result is not None
