"""
Tests for System Integrity Orchestrator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import pytest

from src.orchestrators.system.system_integrity_orchestrator import (
    SystemIntegrityOrchestrator,
    IntegrityIssue,
    IntegrityReport
)


@pytest.fixture
def logger():
    """Create test logger"""
    return logging.getLogger('test_integrity')


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace structure"""
    workspace = tmp_path / "cortex"
    workspace.mkdir()
    
    # Create directory structure
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    (workspace / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0").mkdir(parents=True)
    (workspace / "cortex-brain" / "documents" / "reports").mkdir(parents=True)
    (workspace / "cortex-brain" / "manifests" / "operations").mkdir(parents=True)
    
    # Create master plan (using ASCII to avoid encoding issues)
    master_plan = workspace / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "00-MASTER-PLAN.md"
    master_plan.write_text(
        "# CORTEX 3.0 -> 4.0 Master Plan\n\n"
        "## Phase 1: Pre-Migration Cleanup (Week 0) - 100% COMPLETE\n"
        "## Phase 2: Autonomous Execution Framework (Week 1 Days 1-3) - 100% COMPLETE\n"
        "## Phase 3: Foundation (Weeks 1-3) - 100% COMPLETE\n",
        encoding='utf-8'
    )
    
    # Create manifest
    manifest = workspace / "cortex-brain" / "manifests" / "operations" / "cortex-operations.yaml"
    manifest.write_text("operations: {}", encoding='utf-8')
    
    return workspace


@pytest.fixture
def orchestrator(temp_workspace):
    """Create orchestrator instance"""
    config = {
        "workspace_root": str(temp_workspace),
        "log_level": "DEBUG"
    }
    with patch.object(Path, 'cwd', return_value=temp_workspace):
        orch = SystemIntegrityOrchestrator(config)
        orch.workspace_root = temp_workspace
        orch.master_plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0" / "00-MASTER-PLAN.md"
        return orch


class TestSystemIntegrityOrchestrator:
    """Test suite for SystemIntegrityOrchestrator"""
    
    def test_initialization(self, orchestrator):
        """Test orchestrator initialization"""
        assert orchestrator is not None
        assert orchestrator.report is not None
        assert orchestrator.workspace_root.exists()
    
    def test_setup(self, orchestrator):
        """Test setup phase"""
        context = {}
        orchestrator._setup(context)
        
        assert context['fix_mode'] is True
        assert context['run_tests'] is True
        assert context['generate_docs'] is True
        assert 'report' in context
    
    def test_parse_completed_phases(self, orchestrator):
        """Test parsing completed phases from master plan"""
        phases = orchestrator._parse_completed_phases()
        
        assert len(phases) == 3
        assert phases[0]['number'] == '1'
        assert phases[0]['name'] == 'Pre-Migration Cleanup (Week 0)'
        assert phases[0]['completion'] == 100
    
    def test_add_issue(self, orchestrator):
        """Test adding integrity issue"""
        orchestrator._add_issue(
            'tests', 'high',
            'Test failure detected',
            Path('/test/file.py'),
            auto_fixable=False
        )
        
        assert orchestrator.report.issues_found == 1
        assert orchestrator.report.issues_remaining == 1
        assert len(orchestrator.report.issues) == 1
        
        issue = orchestrator.report.issues[0]
        assert issue.category == 'tests'
        assert issue.severity == 'high'
        assert not issue.auto_fixable
    
    def test_mark_issue_fixed(self, orchestrator):
        """Test marking issue as fixed"""
        # Add issue first
        orchestrator._add_issue('docs', 'medium', 'Missing documentation')
        
        assert orchestrator.report.issues_fixed == 0
        assert orchestrator.report.issues_remaining == 1
        
        # Mark as fixed
        orchestrator._mark_issue_fixed('docs', 'Missing documentation')
        
        assert orchestrator.report.issues_fixed == 1
        assert orchestrator.report.issues_remaining == 0
        assert orchestrator.report.issues[0].fix_applied is True
    
    def test_phase_analyze(self, orchestrator):
        """Test analyze phase"""
        context = {'fix_mode': True}
        
        orchestrator._phase_analyze(context)
        
        # Should have parsed phases
        phases = orchestrator._parse_completed_phases()
        assert len(phases) > 0
    
    @patch('subprocess.run')
    def test_phase_validate_tests_success(self, mock_run, orchestrator):
        """Test validate tests phase - success case"""
        # Mock pytest output
        mock_result = Mock()
        mock_result.stdout = "10 passed"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        context = {}
        orchestrator._phase_validate_tests(context)
        
        assert orchestrator.report.tests_passed == 10
        assert orchestrator.report.tests_failed == 0
        assert orchestrator.report.tests_run == 10
    
    @patch('subprocess.run')
    def test_phase_validate_tests_failures(self, mock_run, orchestrator):
        """Test validate tests phase - failures"""
        # Mock pytest output with failures
        mock_result = Mock()
        mock_result.stdout = "5 passed, 2 failed"
        mock_result.stderr = ""
        mock_result.returncode = 1
        mock_run.return_value = mock_result
        
        context = {}
        orchestrator._phase_validate_tests(context)
        
        assert orchestrator.report.tests_passed == 5
        assert orchestrator.report.tests_failed == 2
        assert orchestrator.report.issues_found > 0
    
    def test_phase_check_docs(self, orchestrator, temp_workspace):
        """Test documentation completeness check"""
        context = {'fix_mode': True, 'generate_docs': True}
        
        orchestrator._phase_check_docs(context)
        
        # Should generate docs for completed phases
        assert orchestrator.report.docs_generated > 0
    
    def test_check_root_folder(self, orchestrator, temp_workspace):
        """Test root folder organization check"""
        # Create misplaced file
        misplaced = temp_workspace / "random_file.txt"
        misplaced.write_text("test content")
        
        context = {'fix_mode': False}
        orchestrator._check_root_folder(context)
        
        # Should detect misplaced file
        assert orchestrator.report.issues_found > 0
    
    def test_relocate_file(self, orchestrator, temp_workspace):
        """Test file relocation"""
        # Create file to relocate
        source = temp_workspace / "test_file.md"
        source.write_text("test")
        
        target_dir = temp_workspace / "cortex-brain" / "documents" / "reports"
        
        context = {}
        orchestrator._relocate_file(source, target_dir, context)
        
        # File should be moved
        assert not source.exists()
        assert (target_dir / "test_file.md").exists()
        assert orchestrator.report.files_relocated == 1
    
    def test_repair_links_in_file(self, orchestrator, temp_workspace):
        """Test link repair in markdown files"""
        # Create file with broken link
        doc = temp_workspace / "test.md"
        doc.write_text("[Link](old_location/file.md)")
        
        # Register file move
        old_path = temp_workspace / "old_location" / "file.md"
        new_path = temp_workspace / "new_location" / "file.md"
        new_path.parent.mkdir(parents=True)
        new_path.write_text("content")
        orchestrator.file_moves[old_path] = new_path
        
        context = {'fix_mode': True}
        orchestrator._repair_links_in_file(doc, context)
        
        # Link should be updated (note: actual fix depends on relative path calculation)
        content = doc.read_text()
        assert "old_location" not in content or "new_location" in content
    
    def test_is_excluded_path(self, orchestrator, temp_workspace):
        """Test path exclusion check"""
        assert orchestrator._is_excluded_path(temp_workspace / ".venv" / "lib")
        assert orchestrator._is_excluded_path(temp_workspace / "node_modules" / "pkg")
        assert not orchestrator._is_excluded_path(temp_workspace / "src" / "file.py")
    
    def test_build_report_content(self, orchestrator):
        """Test report content generation"""
        # Add some issues
        orchestrator._add_issue('tests', 'high', 'Test failure')
        orchestrator._mark_issue_fixed('tests', 'Test failure')
        
        orchestrator.report.tests_run = 100
        orchestrator.report.tests_passed = 95
        orchestrator.report.tests_failed = 5
        
        content = orchestrator._build_report_content()
        
        assert "CORTEX System Integrity Report" in content
        assert "Issues Found** | 1" in content or "**Issues Found** | 1" in content
        assert "Issues Fixed** | 1" in content or "**Issues Fixed** | 1" in content
        assert "Tests Run" in content or "Tests Passed" in content
    
    @patch('subprocess.run')
    def test_full_execution(self, mock_run, orchestrator):
        """Test full orchestrator execution"""
        # Mock pytest
        mock_result = Mock()
        mock_result.stdout = "10 passed"
        mock_result.stderr = ""
        mock_result.returncode = 0
        mock_run.return_value = mock_result
        
        context = {
            'fix_mode': True,
            'run_tests': True,
            'generate_docs': True,
            'cleanup_legacy': False,  # Skip for test
            'reorganize_files': False
        }
        
        result = orchestrator.execute(context)
        
        # Result is a dict with success key
        assert isinstance(result, dict)
        assert 'success' in result
        assert result['success'] is True
        # Check report exists in result
        assert 'report' in result
    
    def test_execution_with_errors(self, orchestrator):
        """Test execution with errors"""
        # Force error by removing master plan
        orchestrator.master_plan_path = Path("/nonexistent")
        
        result = orchestrator.execute({'fix_mode': False})
        
        # Should handle gracefully
        assert 'success' in result
        assert 'report' in result


class TestIntegrityIssue:
    """Test IntegrityIssue dataclass"""
    
    def test_issue_creation(self):
        """Test issue creation"""
        issue = IntegrityIssue(
            category='tests',
            severity='high',
            description='Test failure',
            location=Path('/test.py'),
            auto_fixable=True
        )
        
        assert issue.category == 'tests'
        assert issue.severity == 'high'
        assert not issue.fix_applied
        assert issue.fix_result is None


class TestIntegrityReport:
    """Test IntegrityReport dataclass"""
    
    def test_report_initialization(self):
        """Test report initialization"""
        report = IntegrityReport()
        
        assert report.issues_found == 0
        assert report.issues_fixed == 0
        assert report.issues_remaining == 0
        assert len(report.issues) == 0
    
    def test_report_tracking(self):
        """Test report metric tracking"""
        report = IntegrityReport()
        
        # Add metrics
        report.issues_found = 10
        report.issues_fixed = 8
        report.issues_remaining = 2
        report.tests_run = 100
        report.tests_passed = 95
        report.files_relocated = 5
        
        assert report.issues_found == 10
        assert report.issues_fixed == 8
        assert report.tests_run == 100


@pytest.mark.integration
class TestSystemIntegrityIntegration:
    """Integration tests requiring full environment"""
    
    @pytest.mark.skipif(not Path('tests').exists(), reason="Tests directory required")
    def test_real_test_execution(self):
        """Test with real test suite (if available)"""
        config = {'log_level': 'INFO'}
        orchestrator = SystemIntegrityOrchestrator(config)
        
        context = {
            'fix_mode': False,
            'run_tests': True,
            'generate_docs': False,
            'cleanup_legacy': False,
            'reorganize_files': False
        }
        
        result = orchestrator.execute(context)
        
        assert 'tests_run' in result
        assert result['tests_run'] >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
