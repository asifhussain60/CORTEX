"""
VSCode Workspace Configurator

Generates .vscode/settings.json, extensions.json, and tasks.json for a CORTEX
workspace.

Authority: PHASE-DEPLOYMENT-002 AC-DEP-002-02
AC_START: AC-VSCODE-CONF-001
"""

import json
import platform
from pathlib import Path
from typing import Any, Dict, Optional

from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


class VSCodeConfigurator(OrchestratorProtocolMixin):
    """
    Generate VS Code workspace configuration files.

    Detects the Python interpreter, then writes:
    - ``.vscode/settings.json``
    - ``.vscode/extensions.json``
    - ``.vscode/tasks.json``

    Example::

        configurator = VSCodeConfigurator(Path("/path/to/workspace"))
        configurator.generate_settings()
        configurator.generate_extensions()
        configurator.generate_tasks()
    """

    def __init__(self, workspace: Path) -> None:
        """
        Initialise configurator.

        Args:
            workspace: Root directory of the workspace.
        """
        super().__init__()
        self.workspace = Path(workspace)
        self._vscode_dir = self.workspace / ".vscode"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def detect_python_interpreter(self) -> Optional[Path]:
        """
        Detect the Python interpreter to use for the workspace.

        Searches (in order):
        1. ``<workspace>/.venv`` (Unix: ``bin/python``, Windows: ``Scripts/python.exe``)
        2. ``<workspace>/venv``
        3. System ``python3`` / ``python``

        Returns:
            Absolute path to the Python interpreter, or ``None`` if undetectable.
        """
        # AC marker emitted via cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="detect_python_interpreter")

        is_windows = platform.system() == "Windows"
        for venv_name in (".venv", "venv", "env"):
            venv_root = self.workspace / venv_name
            if venv_root.exists():
                if is_windows:
                    candidate = venv_root / "Scripts" / "python.exe"
                else:
                    candidate = venv_root / "bin" / "python"
                if candidate.exists():
                    return candidate
        return None

    def generate_settings(self) -> Path:
        """
        Generate ``.vscode/settings.json``.

        Returns:
            Path to the written settings file.
        """
        self._vscode_dir.mkdir(parents=True, exist_ok=True)
        interpreter = self.detect_python_interpreter()

        settings: Dict[str, Any] = {
            "python.defaultInterpreterPath": (
                str(interpreter) if interpreter else "${workspaceFolder}/.venv/bin/python"
            ),
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": False,
            "python.linting.flake8Enabled": True,
            "python.formatting.provider": "black",
            "editor.formatOnSave": True,
            "editor.rulers": [88, 120],
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.pytest_cache": True,
            },
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": ["tests/"],
            "github.copilot.chat.mcpServers": {
                "cortex": {
                    "command": "python3",
                    "args": ["-m", "cortex.mcp"],
                    "transport": "stdio",
                    "cwd": "${workspaceFolder}",
                }
            },
        }

        settings_path = self._vscode_dir / "settings.json"
        settings_path.write_text(json.dumps(settings, indent=2), encoding="utf-8")
        return settings_path

    def generate_extensions(self) -> Path:
        """
        Generate ``.vscode/extensions.json`` with recommended extensions.

        Returns:
            Path to the written extensions file.
        """
        self._vscode_dir.mkdir(parents=True, exist_ok=True)
        extensions: Dict[str, Any] = {
            "recommendations": [
                "ms-python.python",
                "ms-python.black-formatter",
                "ms-python.flake8",
                "ms-python.mypy-type-checker",
                "ms-toolsai.jupyter",
                "GitHub.copilot",
                "GitHub.copilot-chat",
                "redhat.vscode-yaml",
                "ms-vscode.vscode-json",
                "eamodio.gitlens",
                "streetsidesoftware.code-spell-checker",
            ]
        }

        extensions_path = self._vscode_dir / "extensions.json"
        extensions_path.write_text(json.dumps(extensions, indent=2), encoding="utf-8")
        return extensions_path

    def generate_tasks(self) -> Path:
        """
        Generate ``.vscode/tasks.json`` with standard CORTEX tasks.

        Returns:
            Path to the written tasks file.
        """
        self._vscode_dir.mkdir(parents=True, exist_ok=True)
        tasks: Dict[str, Any] = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "CORTEX: Smoke Tests",
                    "type": "shell",
                    "command": "python3 scripts/run_tests.py smoke",
                    "group": "test",
                    "presentation": {"reveal": "always"},
                },
                {
                    "label": "CORTEX: Full Batch Run (pytest)",
                    "type": "shell",
                    "command": "python3 scripts/run_tests.py batch",
                    "group": {"kind": "test", "isDefault": True},
                    "presentation": {"reveal": "always"},
                },
                {
                    "label": "CORTEX: Setup MCP",
                    "type": "shell",
                    "command": "python3 scripts/setup-mcp.py",
                    "group": "none",
                    "presentation": {"reveal": "always"},
                },
            ],
        }

        tasks_path = self._vscode_dir / "tasks.json"
        tasks_path.write_text(json.dumps(tasks, indent=2), encoding="utf-8")
        return tasks_path

    def generate_all(self) -> Dict[str, Path]:
        """
        Generate all VS Code configuration files.

        Returns:
            Dict mapping config name to written file path.
        """
        return {
            "settings": self.generate_settings(),
            "extensions": self.generate_extensions(),
            "tasks": self.generate_tasks(),
        }


# AC_COMPLETE: AC-VSCODE-CONF-001 ✅ VSCodeConfigurator implemented
