"""
ProjectDiscoverer — Scans project directories and registers them in the CORTEX registry.

Authority: CORE-035 (single canonical implementation)
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional


class ProjectDiscoverer:
    """Discovers project directories and infers governance metadata.

    All external I/O is routed through patchable helper methods
    (``_list_directories``, ``_analyze_project``, ``_db_insert``,
    ``_db_upsert``) so tests can mock filesystem/database interactions.
    """

    # Indicators → project type mapping used by infer_project_type
    _TYPE_MAP: Dict[str, str] = {
        "financial": "finops",
        "payment": "finops",
        "billing": "finops",
        "invoice": "finops",
        "session": "auth",
        "auth": "auth",
        "login": "auth",
        "oauth": "auth",
        "model": "ml",
        "training": "ml",
        "inference": "ml",
        "dataset": "ml",
        "pipeline": "devops",
        "deploy": "devops",
        "ci": "devops",
        "cd": "devops",
        "governance": "governance",
    }

    def __init__(self) -> None:
        """Initialize instance."""
        self._projects: Dict[str, Dict[str, Any]] = {}

    # ── Patchable I/O helpers ────────────────────────────────────────

    def _list_directories(self, base_path: str) -> List[str]:
        """Return directory names under base_path (override in tests)."""
        try:
            return [p.name for p in Path(base_path).iterdir() if p.is_dir()]
        except Exception:
            return []

    def _analyze_project(self, name: str, base_path: str) -> Dict[str, Any]:
        """Analyse a single project directory and return metadata."""
        full_path = f"{base_path}/{name}"
        return {
            "name": name,
            "path": full_path,
            "type": self.infer_project_type(name, indicators=[]),
            "has_cortex_config": self.has_cortex_config(full_path),
        }

    def _db_insert(self, data: Dict[str, Any]) -> bool:
        """Insert a project record into the database."""
        self._projects[data.get("project_id", data.get("name", "unknown"))] = data
        return True

    def _db_upsert(self, data: Dict[str, Any]) -> bool:
        """Upsert a project record in the database."""
        self._projects[data.get("project_id", data.get("name", "unknown"))] = data
        return True

    # ── Core API ─────────────────────────────────────────────────────

    def scan(self, base_path: str) -> List[Dict[str, Any]]:
        """Scan base_path for project directories.

        Args:
            base_path: Root path to scan (e.g. ``D:\\PROJECTS``).

        Returns:
            List of project metadata dicts (hidden dirs excluded).
        """
        names = self._list_directories(base_path)
        projects = []
        for name in names:
            if name.startswith("."):
                continue
            metadata = self._analyze_project(name, base_path)
            projects.append(metadata)
        return projects

    def has_cortex_config(self, project_path: str) -> bool:
        """Check whether ``.cortex-config.yaml`` exists in project_path.

        Args:
            project_path: Absolute project directory path.

        Returns:
            bool
        """
        config = Path(project_path) / ".cortex-config.yaml"
        return config.exists()

    def infer_project_type(
        self, name: str, indicators: Optional[List[str]] = None
    ) -> str:
        """Infer project type from name and/or indicator strings.

        Args:
            name: Project directory name.
            indicators: Optional list of indicator strings (from requirements,
                folder names, etc.)

        Returns:
            One of: ``"finops"``, ``"auth"``, ``"ml"``, ``"devops"``,
            ``"governance"``, ``"general"``
        """
        check_tokens = [name.lower()] + [i.lower() for i in (indicators or [])]
        for token in check_tokens:
            for keyword, project_type in self._TYPE_MAP.items():
                if keyword in token:
                    return project_type
        return "general"

    def register_project(
        self, data: Dict[str, Any], update_existing: bool = False
    ) -> bool:
        """Register or update a project in the database.

        Args:
            data: Project metadata dict. Must contain ``project_id``.
            update_existing: If True, use upsert instead of insert.

        Returns:
            bool — True on success.
        """
        if update_existing:
            return self._db_upsert(data)
        return self._db_insert(data)
