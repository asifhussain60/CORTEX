"""
Tests for FileOrganizationValidator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.validation.file_organization_validator import (
    FileOrganizationValidator,
    OrganizationViolation
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace structure."""
    # Create CORTEX embedded structure
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # CORTEX structure
    (cortex_root / "cortex-brain").mkdir()
    (cortex_root / "src" / "agents").mkdir(parents=True)
    (cortex_root / "src" / "orchestrators").mkdir(parents=True)
    (cortex_root / "tests").mkdir()
    
    # Application structure
    (tmp_path / "tests").mkdir()
    (tmp_path / "src").mkdir()
    
    return tmp_path


@pytest.fixture
def standalone_cortex_workspace(tmp_path):
    """Create standalone CORTEX workspace structure."""
    (tmp_path / "cortex-brain").mkdir()
    (tmp_path / "src" / "agents").mkdir(parents=True)
    (tmp_path / "src" / "orchestrators").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    
    return tmp_path


class TestFileOrganizationValidator:
    """Tests for FileOrganizationValidator."""
    
    def test_initialization_embedded(self, temp_workspace):
        """Test validator initialization with embedded CORTEX."""
        validator = FileOrganizationValidator(temp_workspace)
        
        assert validator.workspace_root == temp_workspace
        assert validator.cortex_root == temp_workspace / "CORTEX"
        assert validator.violations == []
    
    def test_initialization_standalone(self, standalone_cortex_workspace):
        """Test validator initialization with standalone CORTEX."""
        validator = FileOrganizationValidator(standalone_cortex_workspace)
        
        assert validator.workspace_root == standalone_cortex_workspace
        assert validator.cortex_root == standalone_cortex_workspace
    
    def test_validate_clean_structure(self, temp_workspace):
        """Test validation of clean file organization."""
        # Create .gitignore with CORTEX/ exclusion
        gitignore = temp_workspace / ".gitignore"
        gitignore.write_text("# CORTEX AI Assistant\nCORTEX/\n")
        
        validator = FileOrganizationValidator(temp_workspace)
        results = validator.validate()
        
        assert results['status'] == 'pass'
        assert results['score'] >= 80
        assert results['critical_count'] == 0
        assert len(results['violations']) == 0
    
    def test_detect_cortex_leak(self, temp_workspace):
        """Test detection of CORTEX files leaked into application repo."""
        # Create leaked CORTEX file
        leaked_file = temp_workspace / "src" / "agents" / "test_agent.py"
        leaked_file.write_text("# CORTEX agent leaked to app")
        
        validator = FileOrganizationValidator(temp_workspace)
        results = validator.validate()
        
        assert results['status'] == 'fail'
        assert results['critical_count'] > 0
        
        # Check for cortex_leak violation
        leak_violations = [v for v in results['violations'] if v.violation_type == 'cortex_leak']
        assert len(leak_violations) > 0
        assert leak_violations[0].severity == 'critical'
    
    def test_detect_test_misplacement(self, temp_workspace):
        """Test detection of CORTEX tests in application test directory."""
        # Create CORTEX test in app tests
        app_test = temp_workspace / "tests" / "test_brain_ingestion.py"
        app_test.write_text("""
from src.agents.brain_ingestion_agent import BrainIngestionAgent

def test_ingestion():
    agent = BrainIngestionAgent()
    assert agent is not None
""")
        
        validator = FileOrganizationValidator(temp_workspace)
        results = validator.validate()
        
        # Check for test misplacement violation
        test_violations = [v for v in results['violations'] if v.violation_type == 'test_misplacement']
        assert len(test_violations) > 0
        assert test_violations[0].severity == 'warning'
        assert 'CORTEX' in str(test_violations[0].expected_location)
    
    def test_detect_missing_gitignore(self, temp_workspace):
        """Test detection of missing .gitignore."""
        validator = FileOrganizationValidator(temp_workspace)
        results = validator.validate()
        
        # Check for gitignore violation
        gitignore_violations = [v for v in results['violations'] if v.violation_type == 'gitignore_missing']
        assert len(gitignore_violations) > 0
        assert gitignore_violations[0].severity == 'critical'
    
    def test_detect_incomplete_gitignore(self, temp_workspace):
        """Test detection of .gitignore without CORTEX exclusion."""
        # Create incomplete .gitignore
        gitignore = temp_workspace / ".gitignore"
        gitignore.write_text("# Some other rules\n*.pyc\n")
        
        validator = FileOrganizationValidator(temp_workspace)
        results = validator.validate()
        
        # Check for gitignore violation
        gitignore_violations = [v for v in results['violations'] if v.violation_type == 'gitignore_missing']
        assert len(gitignore_violations) > 0
        assert 'CORTEX/' in gitignore_violations[0].remediation
    
    def test_is_within_cortex_boundary(self, temp_workspace):
        """Test CORTEX boundary detection."""
        validator = FileOrganizationValidator(temp_workspace)
        
        # Files within CORTEX boundary
        assert validator._is_within_cortex_boundary(temp_workspace / "CORTEX" / "src" / "agents" / "test.py")
        assert validator._is_within_cortex_boundary(temp_workspace / ".github" / "prompts" / "test.md")
        
        # Files outside CORTEX boundary
        assert not validator._is_within_cortex_boundary(temp_workspace / "src" / "app.py")
        assert not validator._is_within_cortex_boundary(temp_workspace / "tests" / "test_app.py")
    
    def test_is_cortex_test(self, temp_workspace):
        """Test CORTEX test identification."""
        validator = FileOrganizationValidator(temp_workspace)
        
        # Create CORTEX test file
        cortex_test = temp_workspace / "test_cortex.py"
        cortex_test.write_text("""
from src.orchestrators.tdd_workflow_orchestrator import TDDWorkflowOrchestrator

def test_tdd_workflow():
    orchestrator = TDDWorkflowOrchestrator()
    assert orchestrator is not None
""")
        
        # Create application test file
        app_test = temp_workspace / "test_app.py"
        app_test.write_text("""
from myapp.models import User

def test_user_creation():
    user = User()
    assert user is not None
""")
        
        assert validator._is_cortex_test(cortex_test)
        assert not validator._is_cortex_test(app_test)
    
    def test_generate_remediation_templates(self, temp_workspace):
        """Test auto-remediation template generation."""
        # Create violations
        leaked_file = temp_workspace / "src" / "agents" / "test_agent.py"
        leaked_file.write_text("# CORTEX agent leaked")
        
        validator = FileOrganizationValidator(temp_workspace)
        validator.validate()
        
        templates = validator.generate_remediation_templates()
        
        assert len(templates) > 0
        
        # Check file move template
        file_move_templates = [t for t in templates if t['type'] == 'file_move']
        assert len(file_move_templates) > 0
        assert 'git mv' in file_move_templates[0]['command']
        
        # Check gitignore template
        gitignore_templates = [t for t in templates if t['type'] == 'gitignore_update']
        assert len(gitignore_templates) > 0
        assert 'CORTEX/' in gitignore_templates[0]['content']
    
    def test_standalone_no_boundary_check(self, standalone_cortex_workspace):
        """Test that standalone CORTEX skips boundary check."""
        # Create file in standalone repo (should not be violation)
        test_file = standalone_cortex_workspace / "src" / "agents" / "test_agent.py"
        test_file.write_text("# CORTEX agent in standalone repo")
        
        validator = FileOrganizationValidator(standalone_cortex_workspace)
        results = validator.validate()
        
        # Should not have cortex_leak violations
        leak_violations = [v for v in results['violations'] if v.violation_type == 'cortex_leak']
        assert len(leak_violations) == 0
    
    def test_missing_cortex_test_directory(self, temp_workspace):
        """Test detection of missing CORTEX test directory."""
        # Remove CORTEX tests directory
        cortex_tests = temp_workspace / "CORTEX" / "tests"
        cortex_tests.rmdir()
        
        validator = FileOrganizationValidator(temp_workspace)
        results = validator.validate()
        
        # Check for warning about missing test directory
        test_violations = [v for v in results['violations'] if v.violation_type == 'test_misplacement']
        assert len(test_violations) > 0
        assert test_violations[0].severity == 'warning'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
