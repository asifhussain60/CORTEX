"""
Environment Validator - PRE-FLIGHT venv validation.

Validates virtual environment activation before operations.

AC_START: AC-ENH053-006
Description: Virtual environment validation implementation
Author: Asif Hussain
Date: 2026-02-07
"""

import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class VenvValidationResult:
    """Result of virtual environment validation."""

    is_active: bool
    expected_path: Path
    current_path: Optional[Path]
    activation_command: str
    python_executable: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert result to dictionary for JSON serialization."""
        return {
            "is_active": self.is_active,
            "expected_path": str(self.expected_path),
            "current_path": str(self.current_path) if self.current_path else None,
            "activation_command": self.activation_command,
            "python_executable": self.python_executable,
        }


class EnvironmentValidator:
    """
    Validates virtual environment activation.

    PRE-FLIGHT Check:
    - Checks if python3 matches expected venv path
    - Validates VIRTUAL_ENV environment variable
    - Provides activation command if not active
    """

    def __init__(self):
        """Initialize environment validator."""
        pass

    def validate_venv(self, repo_path: Path) -> VenvValidationResult:
        """
        Validate virtual environment activation.

        Args:
            repo_path: Path to repository root

        Returns:
            VenvValidationResult with validation status
        """
        expected_venv = repo_path / ".venv"
        current_python_str = shutil.which("python3")
        current_python = Path(current_python_str) if current_python_str else None

        # Check if venv is active
        is_venv_active = self._is_venv_active(expected_venv, current_python)

        return VenvValidationResult(
            is_active=is_venv_active,
            expected_path=expected_venv,
            current_path=current_python,
            activation_command=self._get_activation_command(expected_venv),
            python_executable=current_python_str,
        )

    def _is_venv_active(self, expected_venv: Path, current_python: Optional[Path]) -> bool:
        """
        Check if expected venv is currently active.

        Args:
            expected_venv: Expected venv path
            current_python: Current python executable path

        Returns:
            True if venv is active
        """
        if not current_python:
            return False

        # Check if python executable is in expected venv
        python_in_venv = str(current_python).startswith(str(expected_venv))

        # Check VIRTUAL_ENV environment variable
        virtual_env = os.environ.get("VIRTUAL_ENV")
        env_matches = virtual_env == str(expected_venv)

        return python_in_venv and env_matches

    def _get_activation_command(self, venv_path: Path) -> str:
        """
        Get activation command for venv.

        Args:
            venv_path: Path to venv

        Returns:
            Activation command string
        """
        return f"source {venv_path}/bin/activate"


# AC_COMPLETE: AC-ENH053-006 ✅ Implementation complete
