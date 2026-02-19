"""ProjectDiscoverer — Scan directories and register projects.

Discovers project directories, detects CORTEX configuration,
infers project types, and registers projects to a database.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional


_FINOPS_INDICATORS = {"financial", "payment", "invoice", "accounting", "finops"}
_AUTH_INDICATORS = {"session", "auth", "login", "jwt", "oauth"}
_ML_INDICATORS = {"model", "training", "inference", "ml", "ai"}


class ProjectDiscoverer:
    """Discover and register projects."""

    def scan(self, base_path: str = ".") -> List[Dict[str, Any]]:
        """Scan a directory for project folders.

        Args:
            base_path: Root directory to scan.

        Returns:
            List of project metadata dicts.
        """
        dirs = self._list_directories(base_path)
        projects: List[Dict[str, Any]] = []
        for name in dirs:
            if name.startswith("."):
                continue
            metadata = self._analyze_project(name, base_path)
            projects.append(metadata)
        return projects

    def has_cortex_config(self, project_path: str) -> bool:
        """Check if a project has .cortex-config.yaml.

        Args:
            project_path: Path to the project root.

        Returns:
            True if configuration file exists.
        """
        return Path(project_path).joinpath(".cortex-config.yaml").exists()

    def infer_project_type(
        self, project_name: str, indicators: Optional[List[str]] = None
    ) -> str:
        """Infer project type from name and indicators.

        Args:
            project_name: Name of the project.
            indicators: Keyword indicators for classification.

        Returns:
            Project type string.
        """
        indicator_set = set(i.lower() for i in (indicators or []))
        if indicator_set & _FINOPS_INDICATORS:
            return "finops"
        if indicator_set & _AUTH_INDICATORS:
            return "auth"
        if indicator_set & _ML_INDICATORS:
            return "ml"
        return "general"

    def register_project(
        self, project_data: Dict[str, Any], update_existing: bool = False
    ) -> bool:
        """Register a project in the database.

        Args:
            project_data: Project metadata dict.
            update_existing: Upsert if True.

        Returns:
            True on success.
        """
        if update_existing:
            return self._db_upsert(project_data)
        return self._db_insert(project_data)

    # ------------------------------------------------------------------
    # Internal helpers (designed for patching)
    # ------------------------------------------------------------------

    def _list_directories(self, base_path: str) -> List[str]:
        """List directories at base_path.

        Args:
            base_path: Root directory.

        Returns:
            List of directory names.
        """
        root = Path(base_path)
        if not root.exists():
            return []
        return [p.name for p in root.iterdir() if p.is_dir()]

    def _analyze_project(
        self, name: str, base_path: str
    ) -> Dict[str, Any]:
        """Analyze a project directory.

        Args:
            name: Project directory name.
            base_path: Parent directory.

        Returns:
            Project metadata dict.
        """
        return {
            "name": name,
            "path": f"{base_path}/{name}",
            "type": "general",
            "has_cortex_config": False,
        }

    def _db_insert(self, data: Dict[str, Any]) -> bool:
        """Insert into database (stub).

        Args:
            data: Data to insert.

        Returns:
            True on success.
        """
        return True

    def _db_upsert(self, data: Dict[str, Any]) -> bool:
        """Upsert into database (stub).

        Args:
            data: Data to upsert.

        Returns:
            True on success.
        """
        return True
