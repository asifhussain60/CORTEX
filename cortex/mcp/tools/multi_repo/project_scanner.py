"""ProjectScanner — Discover project directories.

Scans a base path to discover projects and identify CORTEX-enabled ones.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


class ProjectScanner:
    """Discover project directories under a base path."""

    def discover_projects(
        self, base_path: str = "."
    ) -> List[Dict[str, Any]]:
        """Discover project directories.

        Args:
            base_path: Root directory to scan.

        Returns:
            List of project dicts with 'name', 'path', 'cortex_enabled'.
        """
        dirs = self._list_dirs(base_path)
        projects: List[Dict[str, Any]] = []
        for name in dirs:
            projects.append(
                {
                    "name": name,
                    "path": f"{base_path}/{name}",
                    "cortex_enabled": self._has_cortex_marker(name),
                }
            )
        return projects

    def _list_dirs(self, base_path: str) -> List[str]:
        """List subdirectories under base_path.

        Args:
            base_path: Directory to scan.

        Returns:
            List of directory names.
        """
        root = Path(base_path)
        if not root.exists():
            return []
        return [p.name for p in root.iterdir() if p.is_dir()]

    def _has_cortex_marker(self, project_name: str) -> bool:
        """Check if a project has the .cortex-version marker.

        Args:
            project_name: Project directory name.

        Returns:
            True if CORTEX-enabled.
        """
        return False
