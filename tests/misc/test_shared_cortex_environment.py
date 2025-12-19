"""
Phase 1.1: Shared CORTEX Tooling Environment - Test Suite

Tests for shared ~/.cortex/venv/ environment with symlink-based project references.

CHALLENGE: Installing identical tooling 10 times is inefficient, but shared environments 
risk version conflicts. SOLUTION: Create ~/.cortex/venv/ as shared tooling environment 
with symlinks from each project. Project-specific dependencies stay isolated.

Acceptance Criteria:
1. Shared CORTEX venv created at ~/.cortex/venv/
2. Each project references shared environment via config
3. Project-specific dependencies installed separately
4. Setup time reduced from 10x to 1x + 10 symlinks

Test Strategy (TDD RED State):
- All tests must FAIL initially (no implementation yet)
- Tests define expected behavior as executable specification
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
import os


class TestSharedEnvironmentCreation:
    """Test creation of shared ~/.cortex/venv/ environment."""
    
    def test_shared_venv_created_at_home_directory(self, tmp_path):
        """Test that shared CORTEX venv is created at ~/.cortex/venv/."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        # Mock home directory
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        
        # Verify ~/.cortex/venv/ exists
        shared_venv = home_dir / ".cortex" / "venv"
        assert shared_venv.exists(), "Shared CORTEX venv not created"
        assert (shared_venv / "Scripts" / "python.exe").exists() or (shared_venv / "bin" / "python").exists(), "Python executable not found in shared venv"
    
    def test_shared_venv_contains_required_packages(self, tmp_path):
        """Test that shared venv contains CORTEX tooling packages."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        orchestrator.install_cortex_tooling()
        
        # Verify required packages installed
        shared_venv = home_dir / ".cortex" / "venv"
        
        # Check for marker file indicating tooling installed
        tooling_marker = shared_venv / ".cortex-tooling-installed"
        assert tooling_marker.exists(), "CORTEX tooling not installed in shared venv"
        
        # Verify marker contains package list
        packages = json.loads(tooling_marker.read_text())
        required = ["pytest", "pyyaml", "requests", "playwright"]
        for pkg in required:
            assert pkg in packages, f"Required package {pkg} not in shared venv"
    
    def test_shared_venv_isolated_from_system_python(self, tmp_path):
        """Test that shared venv is isolated from system Python."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        
        shared_venv = home_dir / ".cortex" / "venv"
        
        # Verify pyvenv.cfg exists (indicates proper venv)
        pyvenv_cfg = shared_venv / "pyvenv.cfg"
        assert pyvenv_cfg.exists(), "pyvenv.cfg missing (not proper venv)"
        
        config = pyvenv_cfg.read_text()
        assert "include-system-site-packages = false" in config, "Venv not isolated from system packages"


class TestProjectReferencesSharedEnvironment:
    """Test that projects reference shared environment via config."""
    
    def test_project_config_references_shared_venv(self, tmp_path):
        """Test that project cortex.config.json references shared venv."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        project_dir = tmp_path / "project1"
        project_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        orchestrator.link_project_to_shared_environment(project_dir)
        
        # Verify project config references shared venv
        project_config = project_dir / "CORTEX" / "cortex.config.json"
        assert project_config.exists(), "Project config not created"
        
        config = json.loads(project_config.read_text())
        assert "shared_cortex_venv" in config, "Config missing shared venv reference"
        assert config["shared_cortex_venv"] == str(home_dir / ".cortex" / "venv"), "Config references wrong venv path"
    
    def test_project_uses_shared_venv_python(self, tmp_path):
        """Test that project uses Python from shared venv."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        project_dir = tmp_path / "project1"
        project_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        orchestrator.link_project_to_shared_environment(project_dir)
        
        # Get Python executable path for project
        python_path = orchestrator.get_python_executable(project_dir)
        
        shared_venv = home_dir / ".cortex" / "venv"
        expected_python = shared_venv / "Scripts" / "python.exe" if os.name == "nt" else shared_venv / "bin" / "python"
        
        assert python_path == expected_python, f"Project using wrong Python: {python_path} vs {expected_python}"
    
    def test_multiple_projects_reference_same_shared_venv(self, tmp_path):
        """Test that multiple projects can reference the same shared venv."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        
        project1 = tmp_path / "project1"
        project1.mkdir()
        project2 = tmp_path / "project2"
        project2.mkdir()
        project3 = tmp_path / "project3"
        project3.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        orchestrator.link_project_to_shared_environment(project1)
        orchestrator.link_project_to_shared_environment(project2)
        orchestrator.link_project_to_shared_environment(project3)
        
        # Verify all projects reference same shared venv
        shared_venv_path = str(home_dir / ".cortex" / "venv")
        
        for project in [project1, project2, project3]:
            config_path = project / "CORTEX" / "cortex.config.json"
            config = json.loads(config_path.read_text())
            assert config["shared_cortex_venv"] == shared_venv_path, f"{project.name} references wrong venv"


class TestProjectSpecificDependenciesIsolated:
    """Test that project-specific dependencies stay isolated."""
    
    def test_project_specific_deps_installed_separately(self, tmp_path):
        """Test that project-specific dependencies don't pollute shared venv."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        project_dir = tmp_path / "project1"
        project_dir.mkdir()
        
        # Create project requirements.txt
        (project_dir / "requirements.txt").write_text("flask==2.3.0\nnumpy==1.24.0")
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        orchestrator.link_project_to_shared_environment(project_dir)
        orchestrator.install_project_dependencies(project_dir)
        
        # Verify project-specific deps NOT in shared venv
        shared_venv = home_dir / ".cortex" / "venv"
        tooling_marker = shared_venv / ".cortex-tooling-installed"
        packages = json.loads(tooling_marker.read_text())
        
        assert "flask" not in packages, "Project-specific package polluted shared venv"
        assert "numpy" not in packages, "Project-specific package polluted shared venv"
        
        # Verify project-specific deps in project's local cache
        project_deps = project_dir / "CORTEX" / ".project-dependencies.json"
        assert project_deps.exists(), "Project dependencies not tracked"
        
        deps = json.loads(project_deps.read_text())
        assert "flask" in deps, "flask not in project deps"
        assert "numpy" in deps, "numpy not in project deps"
    
    def test_project_specific_deps_available_at_runtime(self, tmp_path):
        """Test that project-specific deps are available when running CORTEX."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        project_dir = tmp_path / "project1"
        project_dir.mkdir()
        
        (project_dir / "requirements.txt").write_text("requests==2.31.0")
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        orchestrator.link_project_to_shared_environment(project_dir)
        orchestrator.install_project_dependencies(project_dir)
        
        # Get Python path with project deps included
        python_path = orchestrator.get_python_executable_with_project_deps(project_dir)
        
        # Verify PYTHONPATH includes project deps
        env_vars = orchestrator.get_environment_variables(project_dir)
        assert "PYTHONPATH" in env_vars, "PYTHONPATH not set for project deps"
        
        project_deps_path = project_dir / "CORTEX" / ".project-site-packages"
        assert str(project_deps_path) in env_vars["PYTHONPATH"], "Project deps path not in PYTHONPATH"
    
    def test_conflicting_versions_between_projects_handled(self, tmp_path):
        """Test that different projects can have conflicting dependency versions."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        
        project1 = tmp_path / "project1"
        project1.mkdir()
        (project1 / "requirements.txt").write_text("requests==2.28.0")
        
        project2 = tmp_path / "project2"
        project2.mkdir()
        (project2 / "requirements.txt").write_text("requests==2.31.0")
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        
        # Install conflicting versions
        orchestrator.link_project_to_shared_environment(project1)
        orchestrator.install_project_dependencies(project1)
        
        orchestrator.link_project_to_shared_environment(project2)
        orchestrator.install_project_dependencies(project2)
        
        # Verify each project has correct version
        deps1 = json.loads((project1 / "CORTEX" / ".project-dependencies.json").read_text())
        assert deps1["requests"] == "2.28.0", "Project 1 has wrong requests version"
        
        deps2 = json.loads((project2 / "CORTEX" / ".project-dependencies.json").read_text())
        assert deps2["requests"] == "2.31.0", "Project 2 has wrong requests version"


class TestSetupTimeReduction:
    """Test that setup time is reduced from 10x to 1x + 10 symlinks."""
    
    def test_setup_time_with_shared_venv_faster(self, tmp_path):
        """Test that shared venv setup is significantly faster than per-project setup."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        import time
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        
        # Time shared venv creation (should be ~1x tooling install)
        start = time.time()
        orchestrator.create_shared_environment()
        orchestrator.install_cortex_tooling()
        shared_setup_time = time.time() - start
        
        # Time linking 10 projects (should be fast symlink operations)
        projects = [tmp_path / f"project{i}" for i in range(10)]
        for p in projects:
            p.mkdir()
        
        start = time.time()
        for project in projects:
            orchestrator.link_project_to_shared_environment(project)
        linking_time = time.time() - start
        
        # Total time should be ~shared_setup_time + fast_linking_time
        total_time = shared_setup_time + linking_time
        
        # Verify linking is fast (< 1 second for 10 projects)
        assert linking_time < 1.0, f"Linking too slow: {linking_time}s for 10 projects"
        
        # Log times for comparison
        print(f"Shared setup: {shared_setup_time:.2f}s, Linking 10 projects: {linking_time:.2f}s, Total: {total_time:.2f}s")
    
    def test_setup_reports_time_savings(self, tmp_path):
        """Test that setup orchestrator reports time savings to user."""
        from src.orchestrators.setup_orchestrator import SetupOrchestrator
        
        home_dir = tmp_path / "home"
        home_dir.mkdir()
        project_dir = tmp_path / "project1"
        project_dir.mkdir()
        
        orchestrator = SetupOrchestrator(home_dir=home_dir)
        orchestrator.create_shared_environment()
        
        # Link project and get report
        report = orchestrator.link_project_to_shared_environment(project_dir, return_report=True)
        
        assert "time_savings" in report, "Report missing time savings"
        assert report["time_savings"]["enabled"] is True, "Time savings not enabled"
        assert "estimated_savings_seconds" in report["time_savings"], "Report missing time estimate"
        assert report["time_savings"]["estimated_savings_seconds"] > 0, "No time savings reported"
        
        # Verify user-friendly message
        assert "message" in report["time_savings"], "Report missing user message"
        assert "faster" in report["time_savings"]["message"].lower(), "Message doesn't mention speed improvement"
