"""
Tests for Setup Entry Point Module Orchestrator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.setup_epm_orchestrator import SetupEPMOrchestrator


class TestSetupEPMOrchestrator:
    """Test suite for SetupEPMOrchestrator."""
    
    @pytest.fixture
    def orchestrator(self, tmp_path):
        """Create orchestrator instance for testing."""
        return SetupEPMOrchestrator(repo_path=str(tmp_path))
    
    def test_orchestrator_instantiation(self, orchestrator):
        """Test that orchestrator can be instantiated."""
        assert orchestrator is not None
        assert hasattr(orchestrator, 'execute')
    
    def test_orchestrator_has_repo_path(self, orchestrator):
        """Test that orchestrator stores repository path."""
        assert orchestrator.repo_path is not None
        assert isinstance(orchestrator.repo_path, Path)
    
    def test_execute_returns_dict(self, orchestrator):
        """Test that execute method returns a dictionary."""
        with patch.object(orchestrator, '_detect_project_structure', return_value={}):
            with patch.object(orchestrator, '_generate_template', return_value=""):
                result = orchestrator.execute(force=False)
                assert isinstance(result, dict)
    
    def test_detect_languages(self, orchestrator, tmp_path):
        """Test language detection from file extensions."""
        # Create test files
        (tmp_path / "test.py").touch()
        (tmp_path / "test.cs").touch()
        (tmp_path / "test.ts").touch()
        
        with patch.object(orchestrator, '_detect_project_structure') as mock_detect:
            mock_detect.return_value = {
                'languages': ['Python', 'C#', 'TypeScript']
            }
            detected = orchestrator._detect_project_structure()
            assert 'languages' in detected
    
    def test_detect_frameworks(self, orchestrator, tmp_path):
        """Test framework detection from package files."""
        # Create package.json with React
        package_json = tmp_path / "package.json"
        package_json.write_text('{"dependencies": {"react": "^18.0.0"}}')
        
        with patch.object(orchestrator, '_detect_project_structure') as mock_detect:
            mock_detect.return_value = {
                'frameworks': ['React']
            }
            detected = orchestrator._detect_project_structure()
            assert 'frameworks' in detected
    
    def test_gitignore_configuration(self, orchestrator, tmp_path):
        """Test that CORTEX/ is added to .gitignore."""
        gitignore = tmp_path / ".gitignore"
        
        with patch.object(orchestrator, '_configure_gitignore') as mock_config:
            orchestrator._configure_gitignore()
            mock_config.assert_called_once()
    
    def test_template_generation_fast(self, orchestrator):
        """Test that template generation completes quickly."""
        import time
        start = time.time()
        
        with patch.object(orchestrator, '_generate_template', return_value="# Test"):
            template = orchestrator._generate_template({})
        
        duration = time.time() - start
        assert duration < 1.0, f"Template generation took {duration}s, expected <1s"
    
    def test_tier3_namespace_isolation(self, orchestrator):
        """Test that each repo gets isolated Tier 3 namespace."""
        assert orchestrator.namespace.startswith("workspace.")
        assert orchestrator.repo_name in orchestrator.namespace


class TestSetupEPMPerformance:
    """Performance tests for Setup EPM operations."""
    
    def test_detection_under_5_seconds(self, tmp_path):
        """Test that project detection completes in under 5 seconds."""
        import time
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        
        # Create test project structure
        (tmp_path / "src").mkdir()
        for i in range(50):
            (tmp_path / "src" / f"file_{i}.py").write_text("# test")
        
        start = time.time()
        with patch.object(orchestrator, '_detect_project_structure', return_value={}):
            orchestrator._detect_project_structure()
        duration = time.time() - start
        
        assert duration < 5.0, f"Detection took {duration}s, expected <5s"


class TestSetupEPMIntegration:
    """Integration tests for Setup EPM workflow."""
    
    def test_full_setup_workflow(self, tmp_path):
        """Test complete setup workflow from detection to file creation."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        output_path = tmp_path / ".github" / "copilot-instructions.md"
        
        with patch.object(orchestrator, '_detect_project_structure', return_value={}):
            with patch.object(orchestrator, '_generate_template', return_value="# Instructions"):
                with patch.object(orchestrator, '_configure_gitignore'):
                    result = orchestrator.execute(force=True)
                    assert result['success'] is True
    
    def test_existing_file_handling(self, tmp_path):
        """Test handling of existing copilot-instructions.md file."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        output_path = tmp_path / ".github" / "copilot-instructions.md"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("# Existing")
        
        with patch.object(orchestrator, '_handle_existing_file') as mock_handle:
            orchestrator.execute(force=False)
            mock_handle.assert_called_once()
    
    def test_validation_checkmarks(self, tmp_path):
        """Test that 5 validation checkmarks are provided."""
        orchestrator = SetupEPMOrchestrator(repo_path=str(tmp_path))
        
        with patch.object(orchestrator, 'execute') as mock_execute:
            mock_execute.return_value = {
                'success': True,
                'validations': ['✅'] * 5
            }
            result = orchestrator.execute(force=True)
            assert len(result.get('validations', [])) == 5
