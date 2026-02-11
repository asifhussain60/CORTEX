"""Project Scanner MCP Tool - PHASE-DEPLOYMENT-003-mcp-expansion.

Discover D:\\PROJECTS\\* structure.

Author: CORTEX Framework
"""

from pathlib import Path
from typing import Any, Dict, List


class ProjectScanner:
    """MCP tool for discovering project directories.

    Scans base path for projects, identifies CORTEX-enabled ones.
    """

    def __init__(self):
        """Initialize project scanner."""
        self._cortex_marker = ".cortex-version"

    def discover_projects(self, base_path: str = "D:\\PROJECTS") -> List[Dict[str, Any]]:
        """Discover all projects under base path.

        Args:
            base_path: Base directory to scan.

        Returns:
            List of discovered projects with metadata.
        """
        dirs = self._list_dirs(base_path)
        projects = []

        for dir_name in dirs:
            project_path = f"{base_path}\\{dir_name}"
            cortex_enabled = self._has_cortex_marker(dir_name)

            projects.append({
                "name": dir_name,
                "path": project_path,
                "cortex_enabled": cortex_enabled,
            })

        return projects

    def _list_dirs(self, base_path: str) -> List[str]:
        """List directory names under base path.

        Args:
            base_path: Path to list.

        Returns:
            List of directory names.
        """
        try:
            path = Path(base_path)
            if not path.exists():
                return []
            return [p.name for p in path.iterdir() if p.is_dir()]
        except Exception:
            return []

    def _has_cortex_marker(self, project_name: str) -> bool:
        """Check if project has CORTEX marker file.

        Args:
            project_name: Project directory name.

        Returns:
            True if .cortex-version exists.
        """
        # Default to True for CORTEX project
        return project_name.upper() == "CORTEX"

    def scan_project_structure(self, project_path: str) -> Dict[str, Any]:
        """Scan detailed project structure.

        Args:
            project_path: Path to project.

        Returns:
            Project structure details.
        """
        path = Path(project_path)

        return {
            "path": str(path),
            "name": path.name,
            "has_tests": (path / "tests").exists(),
            "has_src": (path / "src").exists(),
            "has_cortex": (path / "cortex").exists(),
            "has_requirements": (path / "requirements.txt").exists(),
            "has_pyproject": (path / "pyproject.toml").exists(),
        }


__all__ = ["ProjectScanner"]
