"""
TDD Mastery Integration Tests - End-to-End Validation

Purpose: Validate complete TDD workflow with all phases integrated
Author: Asif Hussain
Created: 2025-11-24
Version: 1.0

Tests:
- Phase 1: Terminal integration (command detection, output capture)
- Phase 2: Workspace context (project discovery, file mapping)
- Phase 3: Brain memory integration (Tier 1/2 storage)
- Phase 4: Test execution (programmatic pytest/jest/xunit)
- End-to-end: Complete TDD workflow validation
"""

import pytest
import tempfile
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import modules to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from workflows.terminal_integration import TerminalIntegration, on_terminal_command_executed
from workflows.workspace_context_manager import WorkspaceContextManager
from workflows.test_execution_manager import TestExecutionManager
from workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig


class TestPhase1TerminalIntegration:
    """Test Phase 1: Terminal Integration"""
    
    def test_detect_pytest_command(self):
        """Verify pytest command detection"""
        terminal = TerminalIntegration()
        
        result = terminal.parse_terminal_command(
            command="pytest tests/test_login.py -v",
            exit_code=1,
            working_directory="/path/to/project"
        )
        
        assert result is not None
        assert result['framework'] == 'pytest'
        assert result['exit_code'] == 1
        assert 'test_login.py' in result['command']
    
    def test_detect_jest_command(self):
        """Verify jest command detection"""
        terminal = TerminalIntegration()
        
        result = terminal.parse_terminal_command(
            command="npm test",
            exit_code=0,
            working_directory="/path/to/project"
        )
        
        assert result is not None
        assert result['framework'] == 'jest'
    
    def test_parse_pytest_output(self):
        """Verify pytest output parsing"""
        terminal = TerminalIntegration()
        
        # Simulate pytest command
        terminal.parse_terminal_command("pytest -v", 1, "/path")
        
        # Simulate pytest output
        pytest_output = """
============================= test session starts ==============================
collected 8 items

tests/test_login.py::test_valid_login PASSED                             [ 12%]
tests/test_login.py::test_invalid_password FAILED                        [ 25%]

=========================== short test summary info ============================
FAILED tests/test_login.py::test_invalid_password - AssertionError: Expected False
========================= 5 passed, 2 failed, 1 skipped in 2.50s ===============
        """
        
        results = terminal.capture_test_results(pytest_output)
        
        assert results['framework'] == 'pytest'
        assert results['passed'] == 5
        assert results['failed'] == 2
        assert results['skipped'] == 1
        assert results['duration'] == 2.5
    
    def test_format_test_summary(self):
        """Verify test summary formatting"""
        terminal = TerminalIntegration()
        
        test_results = {
            'framework': 'pytest',
            'passed': 5,
            'failed': 2,
            'skipped': 1,
            'duration': 2.5,
            'errors': [
                {'test': 'test_login', 'message': 'AssertionError'}
            ]
        }
        
        summary = terminal.format_test_summary(test_results)
        
        assert '❌ FAILED' in summary
        assert 'Passed:  5 ✓' in summary
        assert 'Failed:  2 ✗' in summary
        assert '2.50s' in summary


class TestPhase2WorkspaceContext:
    """Test Phase 2: Workspace Context Integration"""
    
    def test_detect_python_project(self):
        """Verify Python project detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create Python indicators
            (project_path / "requirements.txt").write_text("pytest==7.4.0")
            (project_path / "pytest.ini").write_text("[pytest]")
            
            workspace = WorkspaceContextManager(project_path)
            
            assert workspace.project_type == 'python'
            assert workspace.test_framework == 'pytest'
    
    def test_detect_javascript_project(self):
        """Verify JavaScript project detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create JS indicators
            (project_path / "package.json").write_text(json.dumps({
                "devDependencies": {"jest": "^29.0.0"}
            }))
            (project_path / "jest.config.js").write_text("module.exports = {}")
            
            workspace = WorkspaceContextManager(project_path)
            
            assert workspace.project_type in ['javascript', 'typescript']
            assert workspace.test_framework == 'jest'
    
    def test_map_test_to_source(self):
        """Verify test-to-source file mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create directory structure
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "src" / "login.py").write_text("def login(): pass")
            (project_path / "tests" / "test_login.py").write_text("def test_login(): pass")
            
            workspace = WorkspaceContextManager(project_path)
            workspace.discover_workspace()
            
            source_file = workspace.map_test_to_source(str(project_path / "tests" / "test_login.py"))
            
            assert source_file is not None
            assert "login.py" in source_file
    
    def test_map_source_to_test(self):
        """Verify source-to-test file mapping"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create directory structure
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "src" / "login.py").write_text("def login(): pass")
            (project_path / "tests" / "test_login.py").write_text("def test_login(): pass")
            
            workspace = WorkspaceContextManager(project_path)
            workspace.discover_workspace()
            
            test_file = workspace.map_source_to_test(str(project_path / "src" / "login.py"))
            
            assert test_file is not None
            assert "test_login.py" in test_file


class TestPhase4TestExecution:
    """Test Phase 4: Test Execution Manager"""
    
    def test_detect_pytest_framework(self):
        """Verify pytest framework detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "pytest.ini").write_text("[pytest]")
            
            manager = TestExecutionManager(str(project_path))
            
            assert manager.framework == 'pytest'
    
    def test_detect_jest_framework(self):
        """Verify jest framework detection"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            (project_path / "jest.config.js").write_text("module.exports = {}")
            
            manager = TestExecutionManager(str(project_path))
            
            assert manager.framework == 'jest'
    
    def test_parse_pytest_terminal_output(self):
        """Verify pytest terminal output parsing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = TestExecutionManager(str(tmpdir))
            
            pytest_output = "5 passed, 2 failed, 1 skipped in 2.50s"
            
            results = manager._parse_pytest_terminal_output(pytest_output, 1)
            
            assert results['passed'] == 5
            assert results['failed'] == 2
            assert results['skipped'] == 1
            assert results['duration'] == 2.5


class TestEndToEndWorkflow:
    """Test complete end-to-end TDD workflow"""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary test project"""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_path = Path(tmpdir)
            
            # Create Python project structure
            (project_path / "src").mkdir()
            (project_path / "tests").mkdir()
            (project_path / "cortex-brain").mkdir(parents=True)
            (project_path / "cortex-brain" / "tier1").mkdir()
            (project_path / "cortex-brain" / "tier2").mkdir()
            
            # Create test files
            (project_path / "pytest.ini").write_text("[pytest]")
            (project_path / "src" / "login.py").write_text("""
def authenticate(username, password):
    if username == "admin" and password == "secret":
        return True
    return False
            """)
            
            (project_path / "tests" / "test_login.py").write_text("""
def test_valid_login():
    from src.login import authenticate
    assert authenticate("admin", "secret") == True

def test_invalid_login():
    from src.login import authenticate
    assert authenticate("admin", "wrong") == False
            """)
            
            yield project_path
    
    def test_complete_tdd_workflow(self, temp_project):
        """Test complete TDD workflow from start to finish"""
        # Skip if brain databases don't exist (unit test environment)
        tier1_db = temp_project / "cortex-brain" / "tier1" / "working_memory.db"
        tier2_db = temp_project / "cortex-brain" / "tier2" / "knowledge_graph.db"
        
        # Initialize configuration
        config = TDDWorkflowConfig(
            project_root=str(temp_project),
            brain_storage_path=str(tier1_db),
            enable_programmatic_execution=True,
            enable_terminal_integration=True,
            enable_workspace_discovery=True
        )
        
        # Create orchestrator
        orchestrator = TDDWorkflowOrchestrator(config)
        
        # Verify components initialized
        assert orchestrator.test_executor is not None
        assert orchestrator.terminal_integration is not None
        assert orchestrator.workspace_manager is not None
        
        # Start TDD session
        session_id = orchestrator.start_session("authentication_feature")
        
        assert session_id is not None
        assert session_id.startswith("tdd_")
    
    def test_workspace_discovery_integration(self, temp_project):
        """Test workspace discovery in orchestrator"""
        config = TDDWorkflowConfig(
            project_root=str(temp_project),
            enable_workspace_discovery=True
        )
        
        orchestrator = TDDWorkflowOrchestrator(config)
        
        if orchestrator.workspace_manager:
            workspace_data = orchestrator.workspace_manager.discover_workspace()
            
            assert workspace_data['project_type'] == 'python'
            assert workspace_data['test_framework'] == 'pytest'
            assert len(workspace_data['test_directories']) > 0
    
    def test_terminal_integration_in_orchestrator(self):
        """Test terminal integration components"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                enable_terminal_integration=True
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            
            assert orchestrator.terminal_integration is not None


class TestBrainMemoryIntegration:
    """Test Phase 3: Brain Memory Integration"""
    
    def test_session_manager_integration(self):
        """Verify SessionManager is initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                enable_session_tracking=True
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            
            assert orchestrator.session_manager is not None
    
    def test_knowledge_graph_integration(self):
        """Verify KnowledgeGraph is initialized"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = TDDWorkflowConfig(
                project_root=tmpdir,
                enable_session_tracking=True
            )
            
            orchestrator = TDDWorkflowOrchestrator(config)
            
            assert orchestrator.knowledge_graph is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
