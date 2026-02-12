"""
Repository Registry System for Multi-Repo Deployment.

Centralized registry for connected repositories with metadata,
type validation, path validation, and persistence to YAML.

Key components:
- RepositoryRegistryEntry: Single repository entry
- RepositoryRegistry: Singleton managing all registered repos
- Registry persistence (load/save from YAML)
- Search functionality and validation
"""

import logging
import os
import pathlib
from dataclasses import asdict, dataclass, field
from datetime import datetime
from threading import Lock
from typing import Any, Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


class DuplicateRepositoryError(Exception):
    """Raised when attempting to register duplicate repo_id."""

    pass


class InvalidRepositoryTypeError(Exception):
    """Raised when repository type is invalid."""

    pass


class InvalidRepositoryPathError(Exception):
    """Raised when repository path is invalid."""

    pass


VALID_REPO_TYPES = {"project", "library", "tool", "docs", "service", "infrastructure"}


@dataclass
class RepositoryRegistryEntry:
    """Single repository entry in the registry.

    Attributes:
        repo_id: Unique repository identifier
        repo_name: Human-readable repository name
        repo_type: Type of repository (project, library, tool, docs, etc.)
        repo_path: Absolute file system path to repository
        created_at: When repository was registered
        status: Registration status (active, inactive, pending)
        metadata: Arbitrary metadata dict for extensibility
    """

    repo_id: str
    repo_name: str
    repo_type: str
    repo_path: str
    created_at: datetime
    status: str = "active"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert entry to dict for serialization.

        Returns:
            Dict with all entry fields

        Example:
            >>> entry = RepositoryRegistryEntry(...)
            >>> entry_dict = entry.to_dict()
            >>> assert entry_dict["repo_id"] == entry.repo_id
        """
        return {
            "repo_id": self.repo_id,
            "repo_name": self.repo_name,
            "repo_type": self.repo_type,
            "repo_path": self.repo_path,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
            "metadata": self.metadata,
        }

    def is_active(self) -> bool:
        """Check if entry is active.

        Returns:
            bool: True if status is 'active'
        """
        return self.status == "active"


class RepositoryRegistry:
    """Singleton registry for connected repositories.

    Provides:
    - Repository registration with validation
    - Registry queries (by ID, by path, list all)
    - Repository status management
    - Registry persistence (load/save from YAML)
    - Search functionality
    - Thread-safe operations

    Example:
        >>> registry = RepositoryRegistry()
        >>> entry = registry.register_repository(
        ...     repo_id="repo-1",
        ...     repo_name="Main Repository",
        ...     repo_type="project",
        ...     repo_path="/path/to/repo"
        ... )
        >>> retrieved = registry.get_repository("repo-1")
        >>> assert retrieved.repo_id == "repo-1"
    """

    _instance: Optional["RepositoryRegistry"] = None
    _lock: Lock = Lock()

    def __new__(cls) -> "RepositoryRegistry":
        """Implement singleton pattern."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    instance = super().__new__(cls)
                    instance._initialized = False
                    cls._instance = instance
        return cls._instance

    def __init__(self):
        """Initialize registry (only once)."""
        if self._initialized:
            return

        self._entries: Dict[str, RepositoryRegistryEntry] = {}
        self._lock_table: Lock = Lock()
        self._initialized = True

    def register_repository(
        self,
        repo_id: str,
        repo_name: str,
        repo_type: str,
        repo_path: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> RepositoryRegistryEntry:
        """Register a repository in the registry.

        Args:
            repo_id: Unique repository identifier
            repo_name: Human-readable name
            repo_type: Type (must be in VALID_REPO_TYPES)
            repo_path: Absolute path to repository
            metadata: Optional metadata

        Returns:
            RepositoryRegistryEntry: The registered entry

        Raises:
            DuplicateRepositoryError: If repo_id already registered
            InvalidRepositoryTypeError: If type not valid
            InvalidRepositoryPathError: If path not absolute

        Example:
            >>> registry = RepositoryRegistry()
            >>> entry = registry.register_repository(
            ...     repo_id="repo-1",
            ...     repo_name="Repo 1",
            ...     repo_type="project",
            ...     repo_path="/path/to/repo"
            ... )
        """
        # Validation
        if repo_id in self._entries:
            raise DuplicateRepositoryError(
                f"Repository {repo_id} is already registered"
            )

        if repo_type not in VALID_REPO_TYPES:
            raise InvalidRepositoryTypeError(
                f"Repository type {repo_type} is not valid. "
                f"Must be one of: {VALID_REPO_TYPES}"
            )

        repo_path_obj = pathlib.Path(repo_path)
        if not repo_path_obj.is_absolute():
            raise InvalidRepositoryPathError(
                f"Repository path {repo_path} must be absolute"
            )

        # Create entry
        entry = RepositoryRegistryEntry(
            repo_id=repo_id,
            repo_name=repo_name,
            repo_type=repo_type,
            repo_path=str(repo_path_obj.resolve()),
            created_at=datetime.now(),
            metadata=metadata or {},
        )

        # Register
        with self._lock_table:
            self._entries[repo_id] = entry

        logger.info(f"Registered repository: {repo_id} ({repo_name}) at {repo_path}")
        return entry

    def get_repository(self, repo_id: str) -> Optional[RepositoryRegistryEntry]:
        """Retrieve repository by repo_id.

        Args:
            repo_id: Repository identifier

        Returns:
            RepositoryRegistryEntry if found, None otherwise

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("repo-1", "Repo 1", "project", "/path")
            >>> entry = registry.get_repository("repo-1")
            >>> assert entry is not None
        """
        with self._lock_table:
            return self._entries.get(repo_id)

    def get_repository_by_path(self, repo_path: str) -> Optional[RepositoryRegistryEntry]:
        """Retrieve repository by path.

        Args:
            repo_path: Repository file system path

        Returns:
            RepositoryRegistryEntry if found, None otherwise
        """
        repo_path_obj = pathlib.Path(repo_path).resolve()

        with self._lock_table:
            for entry in self._entries.values():
                if pathlib.Path(entry.repo_path).resolve() == repo_path_obj:
                    return entry

        return None

    def list_repositories(self) -> List[RepositoryRegistryEntry]:
        """List all registered repositories.

        Returns:
            List[RepositoryRegistryEntry]: All entries

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("repo-1", "Repo 1", "project", "/path/1")
            >>> registry.register_repository("repo-2", "Repo 2", "project", "/path/2")
            >>> repos = registry.list_repositories()
            >>> assert len(repos) >= 2
        """
        with self._lock_table:
            return list(self._entries.values())

    def unregister_repository(self, repo_id: str) -> bool:
        """Unregister a repository.

        Args:
            repo_id: Repository identifier

        Returns:
            bool: True if unregistered, False if not found

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("repo-1", "Repo 1", "project", "/path")
            >>> success = registry.unregister_repository("repo-1")
            >>> assert success is True
            >>> assert registry.get_repository("repo-1") is None
        """
        with self._lock_table:
            if repo_id in self._entries:
                del self._entries[repo_id]
                logger.info(f"Unregistered repository: {repo_id}")
                return True

        return False

    def mark_inactive(self, repo_id: str) -> bool:
        """Mark repository as inactive.

        Args:
            repo_id: Repository identifier

        Returns:
            bool: True if marked, False if not found
        """
        entry = self.get_repository(repo_id)
        if entry is None:
            return False

        with self._lock_table:
            entry.status = "inactive"

        logger.info(f"Marked repository inactive: {repo_id}")
        return True

    def mark_active(self, repo_id: str) -> bool:
        """Mark repository as active.

        Args:
            repo_id: Repository identifier

        Returns:
            bool: True if marked, False if not found
        """
        entry = self.get_repository(repo_id)
        if entry is None:
            return False

        with self._lock_table:
            entry.status = "active"

        logger.info(f"Marked repository active: {repo_id}")
        return True

    def cleanup_inactive_entries(self) -> int:
        """Remove all inactive entries from registry.

        Returns:
            int: Number of entries cleaned up

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("repo-1", "Repo 1", "project", "/path")
            >>> registry.mark_inactive("repo-1")
            >>> cleaned = registry.cleanup_inactive_entries()
            >>> assert cleaned >= 1
        """
        inactive_ids = []

        with self._lock_table:
            for repo_id, entry in self._entries.items():
                if entry.status == "inactive":
                    inactive_ids.append(repo_id)

            for repo_id in inactive_ids:
                del self._entries[repo_id]

        logger.info(f"Cleaned up {len(inactive_ids)} inactive entries")
        return len(inactive_ids)

    def search_by_type(self, repo_type: str) -> List[RepositoryRegistryEntry]:
        """Search repositories by type.

        Args:
            repo_type: Repository type to search for

        Returns:
            List[RepositoryRegistryEntry]: Matching entries

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("proj-1", "Proj", "project", "/path/1")
            >>> repos = registry.search_by_type("project")
            >>> assert any(r.repo_id == "proj-1" for r in repos)
        """
        with self._lock_table:
            return [e for e in self._entries.values() if e.repo_type == repo_type]

    def search_by_name_pattern(self, pattern: str) -> List[RepositoryRegistryEntry]:
        """Search repositories by name pattern.

        Args:
            pattern: Pattern to search for (case-insensitive substring)

        Returns:
            List[RepositoryRegistryEntry]: Matching entries
        """
        pattern_lower = pattern.lower()

        with self._lock_table:
            return [
                e
                for e in self._entries.values()
                if pattern_lower in e.repo_name.lower()
            ]

    def export_to_yaml(self) -> str:
        """Export registry to YAML format.

        Returns:
            str: YAML representation of registry

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("repo-1", "Repo", "project", "/path")
            >>> yaml_str = registry.export_to_yaml()
            >>> assert "repo-1" in yaml_str
        """
        with self._lock_table:
            data = {
                "repositories": [e.to_dict() for e in self._entries.values()],
                "exported_at": datetime.now().isoformat(),
                "total_repos": len(self._entries),
            }

        return yaml.dump(data, default_flow_style=False, sort_keys=False)

    def save_to_file(self, file_path: str) -> None:
        """Save registry to YAML file.

        Args:
            file_path: Path to save file

        Example:
            >>> registry = RepositoryRegistry()
            >>> registry.register_repository("repo-1", "Repo", "project", "/path")
            >>> registry.save_to_file("/path/to/registry.yaml")
        """
        yaml_content = self.export_to_yaml()

        os.makedirs(os.path.dirname(file_path) or ".", exist_ok=True)

        with open(file_path, "w") as f:
            f.write(yaml_content)

        logger.info(f"Saved registry to {file_path}")

    def load_from_file(self, file_path: str) -> int:
        """Load registry from YAML file.

        Args:
            file_path: Path to registry file

        Returns:
            int: Number of repositories loaded

        Raises:
            FileNotFoundError: If file does not exist
            yaml.YAMLError: If file is not valid YAML
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Registry file not found: {file_path}")

        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        if not data or "repositories" not in data:
            return 0

        loaded_count = 0

        with self._lock_table:
            for repo_data in data["repositories"]:
                # Skip if already registered
                if repo_data["repo_id"] in self._entries:
                    continue

                entry = RepositoryRegistryEntry(
                    repo_id=repo_data["repo_id"],
                    repo_name=repo_data["repo_name"],
                    repo_type=repo_data["repo_type"],
                    repo_path=repo_data["repo_path"],
                    created_at=datetime.fromisoformat(repo_data["created_at"]),
                    status=repo_data.get("status", "active"),
                    metadata=repo_data.get("metadata", {}),
                )

                self._entries[entry.repo_id] = entry
                loaded_count += 1

        logger.info(f"Loaded {loaded_count} repositories from {file_path}")
        return loaded_count

    def clear(self) -> None:
        """Clear all entries (for testing).

        Use with caution.
        """
        with self._lock_table:
            self._entries.clear()
