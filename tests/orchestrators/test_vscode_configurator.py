"""Tests for VSCode configurator (PHASE-DEPLOYMENT-002 AC-DEP-002-02).

This module tests the VSCode workspace configuration generator.
"""

import json
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
    
    # Create basic structure
    (workspace / "cortex").mkdir()
    (workspace / "tests").mkdir()
    
    yield workspace


@pytest.fixture
def vscode_module():
    """Import the VSCode configurator module.
    
    Returns:
        The vscode_configurator module.
    """
    from cortex.orchestrators.onboarding import vscode_configurator
    return vscode_configurator


class TestDetectPythonInterpreter:
    """Tests for Python interpreter detection."""
    
    def test_detect_venv_interpreter(
        self, temp_workspace: Path, vscode_module
    ) -> None:
        """Detect Python interpreter in virtual environment.
        
        Args:
            temp_workspace: Path to temp workspace.
            vscode_module: The VSCode configurator module.
        """
        # Create venv structure
        venv = temp_workspace / ".venv"
        venv.mkdir()
        if Path("C:/").exists():  # Windows
            scripts = venv / "Scripts"
            scripts.mkdir()
            (scripts / "python.exe").write_text("")
        else:  # Unix
            bin_dir = venv / "bin"
            bin_dir.mkdir()
            (bin_dir / "python").write_text("")
        
        configurator = vscode_module.VSCodeConfigurator(temp_workspace)
        interpreter = configurator.detect_python_interpreter()
        
        assert interpreter is not None
        assert ".venv" in str(interpreter)


class TestGenerateSettingsJson:
    """Tests for settings.json generation."""
    
    def test_generate_settings_json(
        self, temp_workspace: Path, vscode_module
    ) -> None:
        """Generate .vscode/settings.json with correct structure.
        
        Args:
            temp_workspace: Path to temp workspace.
            vscode_module: The VSCode configurator module.
        """
        configurator = vscode_module.VSCodeConfigurator(temp_workspace)
        configurator.generate_settings()
        
        settings_path = temp_workspace / ".vscode" / "settings.json"
        assert settings_path.exists()
        
        settings = json.loads(settings_path.read_text())
        assert "python.defaultInterpreterPath" in settings or "python.pythonPath" in settings
    
    def test_settings_includes_linting(
        self, temp_workspace: Path, vscode_module
    ) -> None:
        """Settings include linting configuration.
        
        Args:
            temp_workspace: Path to temp workspace.
            vscode_module: The VSCode configurator module.
        """
        configurator = vscode_module.VSCodeConfigurator(temp_workspace)
        configurator.generate_settings()
        
        settings_path = temp_workspace / ".vscode" / "settings.json"
        settings = json.loads(settings_path.read_text())
        
        # Check for Python linting settings
        assert any("python" in key.lower() for key in settings.keys())


class TestGenerateExtensionsJson:
    """Tests for extensions.json generation."""
    
    def test_generate_extensions_json(
        self, temp_workspace: Path, vscode_module
    ) -> None:
        """Generate .vscode/extensions.json with recommendations.
        
        Args:
            temp_workspace: Path to temp workspace.
            vscode_module: The VSCode configurator module.
        """
        configurator = vscode_module.VSCodeConfigurator(temp_workspace)
        configurator.generate_extensions()
        
        extensions_path = temp_workspace / ".vscode" / "extensions.json"
        assert extensions_path.exists()
        
        extensions = json.loads(extensions_path.read_text())
        assert "recommendations" in extensions
        assert len(extensions["recommendations"]) > 0


class TestGenerateTasksJson:
    """Tests for tasks.json generation."""
    
    def test_generate_tasks_json(
        self, temp_workspace: Path, vscode_module
    ) -> None:
        """Generate .vscode/tasks.json with pytest and MCP tasks.
        
        Args:
            temp_workspace: Path to temp workspace.
            vscode_module: The VSCode configurator module.
        """
        configurator = vscode_module.VSCodeConfigurator(temp_workspace)
        configurator.generate_tasks()
        
        tasks_path = temp_workspace / ".vscode" / "tasks.json"
        assert tasks_path.exists()
        
        tasks = json.loads(tasks_path.read_text())
        assert "tasks" in tasks
        
        # Check for pytest task
        task_labels = [t.get("label", "") for t in tasks["tasks"]]
        assert any("pytest" in label.lower() or "test" in label.lower() for label in task_labels)
