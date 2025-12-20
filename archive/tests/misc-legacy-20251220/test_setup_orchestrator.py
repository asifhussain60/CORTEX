"""
Test suite for SetupOrchestrator (Phase 1.1)
RED state: These tests MUST fail before implementation validation
"""

import json
import pytest
import shutil
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestSharedEnvironmentCreation:
    """Test creation of shared CORTEX venv at ~/.cortex/venv"""
    
    def test_creates_shared_venv_directory(self, tmp_path):
        """RED: Should create ~/.cortex/venv directory"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        assert orchestrator.shared_venv_path.exists(), "Should create shared venv directory"
        assert (orchestrator.shared_venv_path / "pyvenv.cfg").exists(), "Should be valid venv"
    
    def test_installs_cortex_tooling_packages(self, tmp_path):
        """RED: Should install pytest, pyyaml, requests, playwright"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        orchestrator.install_cortex_tooling()
        
        # Check marker file exists
        marker = orchestrator.shared_venv_path / ".cortex-tooling-installed"
        assert marker.exists(), "Should create tooling marker file"
        
        # Verify package list
        marker_data = json.loads(marker.read_text())
        assert "pytest" in marker_data["packages"], "Should include pytest"
        assert "pyyaml" in marker_data["packages"], "Should include pyyaml"
    
    def test_gets_correct_python_path(self, tmp_path):
        """RED: Should return platform-specific Python executable path"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        python_path = orchestrator._get_python_path_in_venv(tmp_path / "test_venv")
        
        if sys.platform == "win32":
            assert "Scripts" in str(python_path), "Windows should use Scripts directory"
            assert str(python_path).endswith("python.exe"), "Windows should have .exe"
        else:
            assert "bin" in str(python_path), "Unix should use bin directory"


class TestProjectLinking:
    """Test linking projects to shared environment"""
    
    def test_updates_project_config_with_shared_venv(self, tmp_path):
        """RED: Should update cortex.config.json with shared venv path"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        orchestrator.link_project_to_shared_environment(project_dir)
        
        config_path = project_dir / "cortex.config.json"
        assert config_path.exists(), "Should create config file"
        
        config = json.loads(config_path.read_text())
        assert "shared_cortex_venv" in config, "Should have shared_cortex_venv key"
        assert str(orchestrator.shared_venv_path) in config["shared_cortex_venv"]
    
    def test_returns_performance_report(self, tmp_path):
        """RED: Should return time savings report when requested"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        report = orchestrator.link_project_to_shared_environment(
            project_dir, 
            return_report=True
        )
        
        assert report is not None, "Should return report"
        assert "time_savings" in report, "Should include time_savings"
        assert report["time_savings"]["estimated_savings_seconds"] > 0


class TestProjectDependencies:
    """Test project-specific dependency isolation"""
    
    def test_installs_project_dependencies_separately(self, tmp_path):
        """RED: Should install requirements.txt to .project-site-packages"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Create requirements.txt
        requirements_file = project_dir / "requirements.txt"
        requirements_file.write_text("requests\npytest")
        
        # Mock subprocess to avoid actual installation in tests
        with patch('subprocess.run') as mock_run:
            orchestrator.install_project_dependencies(project_dir)
        
        # Verify dependency tracking file created
        deps_file = project_dir / ".project-dependencies.json"
        assert deps_file.exists(), "Should create dependencies tracking file"
        
        deps_data = json.loads(deps_file.read_text())
        assert len(deps_data["packages"]) > 0, "Should track installed packages"
    
    def test_provides_pythonpath_for_project_deps(self, tmp_path):
        """RED: Should return PYTHONPATH with project site-packages"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Create project site-packages directory
        site_packages = project_dir / ".project-site-packages"
        site_packages.mkdir()
        
        env_vars = orchestrator.get_environment_variables(project_dir)
        
        assert "PYTHONPATH" in env_vars, "Should provide PYTHONPATH"
        assert str(site_packages) in env_vars["PYTHONPATH"]


class TestPythonExecutableAccess:
    """Test Python executable path retrieval"""
    
    def test_returns_shared_venv_python(self, tmp_path):
        """RED: Should return shared venv Python executable"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        python_path = orchestrator.get_python_executable(project_dir)
        
        assert orchestrator.shared_venv_path in python_path.parents, \
            "Should return Python from shared venv"
    
    def test_python_with_project_deps_returns_same(self, tmp_path):
        """RED: Should return same Python (env vars handle deps)"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        python1 = orchestrator.get_python_executable(project_dir)
        python2 = orchestrator.get_python_executable_with_project_deps(project_dir)
        
        assert python1 == python2, "Both methods should return same Python"


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_handles_existing_config_gracefully(self, tmp_path):
        """RED: Should update existing config without overwriting other keys"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        orchestrator.create_shared_environment()
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Create existing config with custom data
        config_path = project_dir / "cortex.config.json"
        existing_config = {"custom_key": "custom_value"}
        config_path.write_text(json.dumps(existing_config, indent=2))
        
        # Link project
        orchestrator.link_project_to_shared_environment(project_dir)
        
        # Verify custom key preserved
        config = json.loads(config_path.read_text())
        assert config["custom_key"] == "custom_value", "Should preserve existing keys"
        assert "shared_cortex_venv" in config, "Should add shared venv key"
    
    def test_handles_missing_requirements_file(self, tmp_path):
        """RED: Should handle missing requirements.txt gracefully"""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        orchestrator = SetupOrchestrator(home_dir=tmp_path)
        
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        
        # Should not raise error
        orchestrator.install_project_dependencies(project_dir)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
