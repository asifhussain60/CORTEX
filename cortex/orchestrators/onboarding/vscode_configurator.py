"""VSCode workspace configurator.

This module provides the VSCodeConfigurator class that generates
.vscode configuration files for the workspace.

PHASE-DEPLOYMENT-002: AC-DEP-002-02
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


class VSCodeConfigurator:
    """Generates VSCode workspace configuration files.

    Creates .vscode/settings.json, extensions.json, and tasks.json
    for optimal Python development experience.

    Attributes:
        workspace: Path to the workspace root.
    """

    # Recommended VSCode extensions
    RECOMMENDED_EXTENSIONS = [
        "ms-python.python",
        "ms-python.vscode-pylance",
        "charliermarsh.ruff",
        "ms-python.debugpy",
        "njpwerner.autodocstring",
        "eamodio.gitlens",
        "gruntfuggly.todo-tree",
        "redhat.vscode-yaml",
    ]

    def __init__(self, workspace: Path) -> None:
        """Initialize the configurator.

        Args:
            workspace: Path to the workspace root.
        """
        self.workspace = Path(workspace)
        self._vscode_dir = self.workspace / ".vscode"

    def detect_python_interpreter(self) -> Optional[Path]:
        """Detect the Python interpreter path.

        Searches for virtual environments in common locations.

        Returns:
            Path to Python interpreter or None if not found.
        """
        # Check for virtual environments
        venv_locations = [
            self.workspace / ".venv",
            self.workspace / "venv",
            self.workspace / ".virtualenv",
            self.workspace / "env",
        ]

        for venv in venv_locations:
            if venv.exists():
                # Windows
                python_exe = venv / "Scripts" / "python.exe"
                if python_exe.exists():
                    return python_exe

                # Unix
                python_bin = venv / "bin" / "python"
                if python_bin.exists():
                    return python_bin

        # Fall back to system Python
        return Path(sys.executable)

    def generate_settings(self) -> Path:
        """Generate .vscode/settings.json.

        Returns:
            Path to the generated settings file.
        """
        self._vscode_dir.mkdir(exist_ok=True)

        python_path = self.detect_python_interpreter()

        settings: Dict[str, Any] = {
            "python.defaultInterpreterPath": str(python_path) if python_path else "${workspaceFolder}/.venv/Scripts/python.exe",
            "python.analysis.typeCheckingMode": "basic",
            "python.analysis.autoImportCompletions": True,
            "python.analysis.diagnosticMode": "workspace",
            "python.testing.pytestEnabled": True,
            "python.testing.pytestArgs": [
                "tests",
                "-v",
                "--tb=short"
            ],
            "editor.formatOnSave": True,
            "editor.codeActionsOnSave": {
                "source.organizeImports": "explicit"
            },
            "[python]": {
                "editor.defaultFormatter": "charliermarsh.ruff",
                "editor.formatOnSave": True
            },
            "ruff.enable": True,
            "ruff.lint.run": "onSave",
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/.pytest_cache": True,
                "**/.mypy_cache": True,
                "**/.ruff_cache": True,
            },
            "yaml.schemas": {
                "https://json.schemastore.org/pre-commit-config.json": ".pre-commit-config.yaml"
            }
        }

        settings_path = self._vscode_dir / "settings.json"
        settings_path.write_text(json.dumps(settings, indent=2))

        return settings_path

    def generate_extensions(self) -> Path:
        """Generate .vscode/extensions.json.

        Returns:
            Path to the generated extensions file.
        """
        self._vscode_dir.mkdir(exist_ok=True)

        extensions = {
            "recommendations": self.RECOMMENDED_EXTENSIONS,
            "unwantedRecommendations": []
        }

        extensions_path = self._vscode_dir / "extensions.json"
        extensions_path.write_text(json.dumps(extensions, indent=2))

        return extensions_path

    def generate_tasks(self) -> Path:
        """Generate .vscode/tasks.json.

        Returns:
            Path to the generated tasks file.
        """
        self._vscode_dir.mkdir(exist_ok=True)

        tasks = {
            "version": "2.0.0",
            "tasks": [
                {
                    "label": "Run pytest",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest", "tests/", "-v", "--tb=short"],
                    "group": {
                        "kind": "test",
                        "isDefault": True
                    },
                    "problemMatcher": ["$python"],
                    "presentation": {
                        "reveal": "always",
                        "panel": "new"
                    }
                },
                {
                    "label": "Run pytest with coverage",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "pytest", "tests/", "-v", "--cov=cortex", "--cov-report=html"],
                    "group": "test",
                    "problemMatcher": ["$python"]
                },
                {
                    "label": "Start MCP Server",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "cortex.mcp.server"],
                    "group": "none",
                    "isBackground": True,
                    "problemMatcher": []
                },
                {
                    "label": "Run type check (mypy)",
                    "type": "shell",
                    "command": "python",
                    "args": ["-m", "mypy", "cortex/", "--ignore-missing-imports"],
                    "group": "build",
                    "problemMatcher": ["$python"]
                },
                {
                    "label": "Run linter (ruff)",
                    "type": "shell",
                    "command": "ruff",
                    "args": ["check", "cortex/", "--fix"],
                    "group": "build",
                    "problemMatcher": []
                },
                {
                    "label": "Setup orchestrator (dry-run)",
                    "type": "shell",
                    "command": "python",
                    "args": ["cortex/orchestrators/onboarding/setup_orchestrator.py", "--dry-run"],
                    "group": "none",
                    "problemMatcher": []
                }
            ]
        }

        tasks_path = self._vscode_dir / "tasks.json"
        tasks_path.write_text(json.dumps(tasks, indent=2))

        return tasks_path

    def generate_all(self) -> List[Path]:
        """Generate all VSCode configuration files.

        Returns:
            List of paths to generated files.
        """
        return [
            self.generate_settings(),
            self.generate_extensions(),
            self.generate_tasks(),
        ]


def main() -> int:
    """CLI entry point for VSCode configurator.

    Returns:
        Exit code.
    """
    workspace = Path.cwd()

    configurator = VSCodeConfigurator(workspace)
    paths = configurator.generate_all()

    print("Generated VSCode configuration files:")
    for path in paths:
        print(f"  - {path}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
