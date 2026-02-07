"""
Tests for EnvironmentValidator - PRE-FLIGHT venv validation.

AC_START: AC-ENH053-005
Description: TDD for virtual environment validation
Author: Asif Hussain
Date: 2026-02-07
"""

import os
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from cortex.orchestrators.core.environment_validator import (
    EnvironmentValidator,
    VenvValidationResult,
)


class TestEnvironmentValidator:
    """Test virtual environment validation."""

    @pytest.fixture
    def validator(self):
        """Create EnvironmentValidator instance."""
        return EnvironmentValidator()

    @pytest.fixture
    def sample_repo_path(self, tmp_path):
        """Create sample repository with .venv."""
        repo_path = tmp_path / "sample_repo"
        repo_path.mkdir()
        venv_path = repo_path / ".venv"
        venv_path.mkdir()
        (venv_path / "bin").mkdir()
        return repo_path

    def test_validator_initialization(self, validator):
        """Test validator initializes correctly."""
        assert validator is not None
        assert hasattr(validator, "validate_venv")

    @patch("shutil.which")
    @patch.dict(os.environ, {"VIRTUAL_ENV": "/path/to/.venv"})
    def test_validate_venv_active(self, mock_which, validator, sample_repo_path):
        """Test validation when venv is active."""
        expected_venv = sample_repo_path / ".venv"
        mock_which.return_value = str(expected_venv / "bin" / "python3")
        
        # Update environment variable to match
        with patch.dict(os.environ, {"VIRTUAL_ENV": str(expected_venv)}):
            result = validator.validate_venv(sample_repo_path)
        
        assert result.is_active is True
        assert result.expected_path == expected_venv

    @patch("shutil.which")
    @patch.dict(os.environ, {}, clear=True)
    def test_validate_venv_not_active(self, mock_which, validator, sample_repo_path):
        """Test validation when venv is not active."""
        mock_which.return_value = "/usr/bin/python3"
        
        result = validator.validate_venv(sample_repo_path)
        
        assert result.is_active is False
        assert "source" in result.activation_command

    @patch("shutil.which")
    def test_validate_venv_wrong_path(self, mock_which, validator, sample_repo_path):
        """Test validation when wrong venv is active."""
        mock_which.return_value = "/other/venv/bin/python3"
        
        with patch.dict(os.environ, {"VIRTUAL_ENV": "/other/venv"}):
            result = validator.validate_venv(sample_repo_path)
        
        assert result.is_active is False
        assert result.current_path == Path("/other/venv/bin/python3")

    def test_get_activation_command_bash(self, validator, sample_repo_path):
        """Test getting activation command for bash/zsh."""
        expected_venv = sample_repo_path / ".venv"
        
        command = validator._get_activation_command(expected_venv)
        
        assert f"source {expected_venv}/bin/activate" == command

    @patch("shutil.which")
    def test_validate_venv_missing_directory(self, mock_which, validator, tmp_path):
        """Test validation when .venv directory doesn't exist."""
        mock_which.return_value = "/usr/bin/python3"
        repo_path = tmp_path / "repo_no_venv"
        repo_path.mkdir()
        
        result = validator.validate_venv(repo_path)
        
        assert result.is_active is False
        assert result.expected_path == repo_path / ".venv"

    @patch("shutil.which")
    def test_validate_python_version(self, mock_which, validator, sample_repo_path):
        """Test Python version validation."""
        expected_venv = sample_repo_path / ".venv"
        mock_which.return_value = str(expected_venv / "bin" / "python3")
        
        with patch.dict(os.environ, {"VIRTUAL_ENV": str(expected_venv)}):
            result = validator.validate_venv(sample_repo_path)
        
        assert result.python_executable is not None

    def test_venv_validation_result_to_dict(self):
        """Test converting VenvValidationResult to dictionary."""
        result = VenvValidationResult(
            is_active=True,
            expected_path=Path("/path/to/.venv"),
            current_path=Path("/path/to/.venv/bin/python3"),
            activation_command="source /path/to/.venv/bin/activate",
        )
        
        data = result.to_dict()
        
        assert data["is_active"] is True
        assert "expected_path" in data
        assert "activation_command" in data


class TestVenvValidationResult:
    """Test VenvValidationResult model."""

    def test_result_initialization(self):
        """Test result model initialization."""
        result = VenvValidationResult(
            is_active=True,
            expected_path=Path("/path/to/.venv"),
            current_path=Path("/path/to/.venv/bin/python3"),
            activation_command="source /path/to/.venv/bin/activate",
        )
        
        assert result.is_active is True
        assert result.expected_path == Path("/path/to/.venv")


# AC_COMPLETE: AC-ENH053-005 ✅ 8/8 tests defined (RED phase)
