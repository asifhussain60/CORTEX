"""Tests for toolchain validator (PHASE-DEPLOYMENT-002 AC-DEP-002-03).

This module tests the toolchain health check functionality.
"""

from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def temp_workspace(tmp_path: Path) -> Generator[Path, None, None]:
    """Create a temporary workspace.
    
    Args:
        tmp_path: Pytest temp path fixture.
        
    Yields:
        Path to the temporary workspace.
    """
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    yield workspace


@pytest.fixture
def toolchain_module():
    """Import the toolchain validator module.
    
    Returns:
        The toolchain_validator module.
    """
    from cortex.orchestrators.onboarding import toolchain_validator
    return toolchain_validator


class TestValidatePytest:
    """Tests for pytest validation."""
    
    def test_validate_pytest_available(
        self, temp_workspace: Path, toolchain_module
    ) -> None:
        """Validate pytest is available and working.
        
        Args:
            temp_workspace: Path to temp workspace.
            toolchain_module: The toolchain validator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="pytest 7.0.0"
            )
            
            validator = toolchain_module.ToolchainValidator(temp_workspace)
            result = validator.validate_pytest()
            
            assert result.available is True
            assert result.version is not None


class TestValidateMypy:
    """Tests for mypy validation."""
    
    def test_validate_mypy_available(
        self, temp_workspace: Path, toolchain_module
    ) -> None:
        """Validate mypy is available and working.
        
        Args:
            temp_workspace: Path to temp workspace.
            toolchain_module: The toolchain validator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="mypy 1.8.0"
            )
            
            validator = toolchain_module.ToolchainValidator(temp_workspace)
            result = validator.validate_mypy()
            
            assert result.available is True


class TestValidateRuff:
    """Tests for ruff validation."""
    
    def test_validate_ruff_available(
        self, temp_workspace: Path, toolchain_module
    ) -> None:
        """Validate ruff is available and working.
        
        Args:
            temp_workspace: Path to temp workspace.
            toolchain_module: The toolchain validator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="ruff 0.1.9"
            )
            
            validator = toolchain_module.ToolchainValidator(temp_workspace)
            result = validator.validate_ruff()
            
            assert result.available is True


class TestValidateGit:
    """Tests for git validation."""
    
    def test_validate_git_available(
        self, temp_workspace: Path, toolchain_module
    ) -> None:
        """Validate git is available and repo is valid.
        
        Args:
            temp_workspace: Path to temp workspace.
            toolchain_module: The toolchain validator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="git version 2.40.0"
            )
            
            validator = toolchain_module.ToolchainValidator(temp_workspace)
            result = validator.validate_git()
            
            assert result.available is True


class TestGenerateHealthReport:
    """Tests for health report generation."""
    
    def test_generate_health_report(
        self, temp_workspace: Path, toolchain_module
    ) -> None:
        """Generate tool_health.yaml report.
        
        Args:
            temp_workspace: Path to temp workspace.
            toolchain_module: The toolchain validator module.
        """
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(
                returncode=0,
                stdout="version 1.0.0"
            )
            
            validator = toolchain_module.ToolchainValidator(temp_workspace)
            report = validator.generate_health_report()
            
            assert report is not None
            assert hasattr(report, 'tools') or isinstance(report, dict)
