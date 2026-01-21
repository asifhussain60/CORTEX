"""Tests for setup orchestrator (PHASE-DEPLOYMENT-002 AC-DEP-002-01).

This module tests the automated setup orchestrator that handles
requirements validation and auto-installation.
"""

import json
import subprocess
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary workspace with requirements.txt.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary workspace.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create requirements.txt
    requirements = workspace / "requirements.txt"
    requirements.write_text("""
pytest>=7.0.0
pyyaml>=6.0
requests>=2.28.0
numpy>=1.24.0
pandas>=2.0.0
""".strip())
    
    yield workspace


@pytest.fixture
def multi_repo_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a multi-repo workspace structure.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the PROJECTS root.
    """
    projects = tmp_path / "PROJECTS"
    projects.mkdir()
    
    # CORTEX
    cortex = projects / "CORTEX"
    cortex.mkdir()
    (cortex / "requirements.txt").write_text("pandas>=2.0.0\nrequests>=2.28.0")
    
    # KASHKOLE
    kashkole = projects / "KASHKOLE"
    kashkole.mkdir()
    (kashkole / "requirements.txt").write_text("pandas>=1.5.0\nnumpy>=1.24.0")  # Version conflict
    
    # KSESSIONS
    ksessions = projects / "KSESSIONS"
    ksessions.mkdir()
    (ksessions / "requirements.txt").write_text("fastapi>=0.100.0\npydantic>=2.0.0")
    
    yield projects


@pytest.fixture
def setup_module():
    """Import the setup orchestrator module.
    
    Returns:
        The setup_orchestrator module.
    """
    from cortex.orchestrators.onboarding import setup_orchestrator
    return setup_orchestrator


class TestParseRequirementsDetectsConflicts:
    """Tests for requirements parsing and conflict detection."""
    
    def test_parse_requirements_valid(
        self, temp_workspace: Path, setup_module
    ) -> None:
        """Parse valid requirements.txt successfully.
        
        Args:
            temp_workspace: Path to temp workspace.
            setup_module: The setup orchestrator module.
        """
        orchestrator = setup_module.SetupOrchestrator(temp_workspace)
        requirements = orchestrator.parse_requirements()
        
        assert len(requirements) >= 5
        assert any(r.name == "pytest" for r in requirements)
        assert any(r.name == "pandas" for r in requirements)
    
    def test_parse_requirements_detects_version(
        self, temp_workspace: Path, setup_module
    ) -> None:
        """Parse version specifiers correctly.
        
        Args:
            temp_workspace: Path to temp workspace.
            setup_module: The setup orchestrator module.
        """
        orchestrator = setup_module.SetupOrchestrator(temp_workspace)
        requirements = orchestrator.parse_requirements()
        
        pandas_req = next(r for r in requirements if r.name == "pandas")
        assert pandas_req.version_spec == ">=2.0.0"


class TestScanMultiRepoDependencies:
    """Tests for multi-repo dependency scanning."""
    
    def test_scan_multi_repo_requirements(
        self, multi_repo_workspace: Path, setup_module
    ) -> None:
        """Scan multiple repos for requirements.txt files.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            setup_module: The setup orchestrator module.
        """
        orchestrator = setup_module.SetupOrchestrator(
            multi_repo_workspace / "CORTEX",
            projects_root=multi_repo_workspace
        )
        repos = orchestrator.scan_multi_repo_requirements()
        
        assert len(repos) >= 3
        assert "CORTEX" in repos
        assert "KASHKOLE" in repos
        assert "KSESSIONS" in repos


class TestResolveVersionConflicts:
    """Tests for version conflict resolution."""
    
    def test_detect_version_conflicts(
        self, multi_repo_workspace: Path, setup_module
    ) -> None:
        """Detect version conflicts across repos.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            setup_module: The setup orchestrator module.
        """
        orchestrator = setup_module.SetupOrchestrator(
            multi_repo_workspace / "CORTEX",
            projects_root=multi_repo_workspace
        )
        conflicts = orchestrator.detect_version_conflicts()
        
        # pandas has conflict: CORTEX needs >=2.0.0, KASHKOLE needs >=1.5.0
        assert len(conflicts) >= 1
        assert any(c.package == "pandas" for c in conflicts)
    
    def test_resolve_version_conflicts(
        self, multi_repo_workspace: Path, setup_module
    ) -> None:
        """Suggest resolution for version conflicts.
        
        Args:
            multi_repo_workspace: Path to multi-repo workspace.
            setup_module: The setup orchestrator module.
        """
        orchestrator = setup_module.SetupOrchestrator(
            multi_repo_workspace / "CORTEX",
            projects_root=multi_repo_workspace
        )
        resolutions = orchestrator.resolve_version_conflicts()
        
        # Should suggest unified version or isolated venv
        assert len(resolutions) >= 1
        pandas_resolution = next(r for r in resolutions if r.package == "pandas")
        assert pandas_resolution.strategy in ["unified", "isolated"]


class TestAutoInstallAllPackages:
    """Tests for automated package installation."""
    
    def test_auto_install_dry_run(
        self, temp_workspace: Path, setup_module
    ) -> None:
        """Auto-install in dry-run mode lists packages.
        
        Args:
            temp_workspace: Path to temp workspace.
            setup_module: The setup orchestrator module.
        """
        orchestrator = setup_module.SetupOrchestrator(temp_workspace)
        result = orchestrator.auto_install(dry_run=True)
        
        assert result.success is True
        assert len(result.packages_to_install) >= 5
        assert result.actually_installed == 0
    
    def test_auto_install_with_progress(
        self, temp_workspace: Path, setup_module
    ) -> None:
        """Auto-install reports progress.
        
        Args:
            temp_workspace: Path to temp workspace.
            setup_module: The setup orchestrator module.
        """
        with patch.object(setup_module, 'subprocess') as mock_subprocess:
            mock_subprocess.run.return_value = MagicMock(returncode=0)
            
            orchestrator = setup_module.SetupOrchestrator(temp_workspace)
            result = orchestrator.auto_install(dry_run=False)
            
            assert hasattr(result, 'progress_reported')


class TestPipAuditSecurityScan:
    """Tests for pip-audit security scanning."""
    
    def test_pip_audit_security_scan(
        self, temp_workspace: Path, setup_module
    ) -> None:
        """Run pip-audit for CVE scanning.
        
        Args:
            temp_workspace: Path to temp workspace.
            setup_module: The setup orchestrator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout='[]'  # No vulnerabilities
            )
            
            orchestrator = setup_module.SetupOrchestrator(temp_workspace)
            result = orchestrator.run_security_scan()
            
            assert result.vulnerabilities == 0
            assert result.scan_completed is True
