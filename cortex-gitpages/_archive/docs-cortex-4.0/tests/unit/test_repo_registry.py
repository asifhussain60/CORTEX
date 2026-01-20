"""
Test suite for Repository Registry System.

Tests for centralized registry of connected repositories:
- Repository registration with metadata
- Registry lookup by repo_id
- Type validation
- Path validation
- Duplicate detection
- Stale entry cleanup
- Schema validation
"""

import pytest
import tempfile
import yaml
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from unittest.mock import Mock, patch, MagicMock


class TestRepoRegistryEntry:
    """Test repository registry entry dataclass."""

    def test_entry_creation(self):
        """Registry entry is created with valid data."""
        from cortex.core.registry.repo_registry import RepositoryRegistryEntry

        entry = RepositoryRegistryEntry(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        assert entry.repo_id == "repo-1"
        assert entry.repo_name == "Test Repository"
        assert entry.repo_type == "project"
        assert entry.repo_path == "/path/to/repo"

    def test_entry_with_metadata(self):
        """Registry entry stores arbitrary metadata."""
        from cortex.core.registry.repo_registry import RepositoryRegistryEntry

        metadata = {"owner": "test-user", "team": "platform"}
        entry = RepositoryRegistryEntry(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
            metadata=metadata,
        )

        assert entry.metadata["owner"] == "test-user"
        assert entry.metadata["team"] == "platform"

    def test_entry_status_tracking(self):
        """Registry entry tracks registration status."""
        from cortex.core.registry.repo_registry import RepositoryRegistryEntry

        entry = RepositoryRegistryEntry(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
            status="active",
        )

        assert entry.status in ["active", "inactive", "pending"]
        assert entry.status == "active"

    def test_entry_to_dict(self):
        """Registry entry converts to dict for serialization."""
        from cortex.core.registry.repo_registry import RepositoryRegistryEntry

        entry = RepositoryRegistryEntry(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
            created_at=datetime.now(),
        )

        entry_dict = entry.to_dict()
        assert entry_dict["repo_id"] == "repo-1"
        assert entry_dict["repo_name"] == "Test Repository"


class TestRepositoryRegistry:
    """Test RepositoryRegistry singleton."""

    def test_registry_singleton(self):
        """Registry is singleton."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        reg1 = RepositoryRegistry()
        reg2 = RepositoryRegistry()

        assert reg1 is reg2

    def test_register_repository(self):
        """Repository is registered in registry."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        entry = registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        assert entry.repo_id == "repo-1"
        assert registry.get_repository("repo-1") is not None

    def test_register_repository_duplicate_rejected(self):
        """Duplicate repo_id is rejected."""
        from cortex.core.registry.repo_registry import (
            RepositoryRegistry,
            DuplicateRepositoryError,
        )

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository 1",
            repo_type="project",
            repo_path="/path/to/repo-1",
        )

        with pytest.raises(DuplicateRepositoryError):
            registry.register_repository(
                repo_id="repo-1",
                repo_name="Test Repository 2",
                repo_type="project",
                repo_path="/path/to/repo-2",
            )

    def test_get_repository_by_id(self):
        """Repository is retrieved by repo_id."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        entry = registry.get_repository("repo-1")

        assert entry is not None
        assert entry.repo_id == "repo-1"

    def test_get_nonexistent_repository(self):
        """Get returns None for nonexistent repo."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        entry = registry.get_repository("nonexistent")

        assert entry is None

    def test_get_repository_by_path(self):
        """Repository is retrieved by repo_path."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        entry = registry.get_repository_by_path("/path/to/repo")

        assert entry is not None
        assert entry.repo_id == "repo-1"

    def test_list_repositories(self):
        """List all registered repositories."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Repo 1",
            repo_type="project",
            repo_path="/path/1",
        )
        registry.register_repository(
            repo_id="repo-2",
            repo_name="Repo 2",
            repo_type="project",
            repo_path="/path/2",
        )

        repos = registry.list_repositories()

        assert len(repos) == 2
        assert any(r.repo_id == "repo-1" for r in repos)
        assert any(r.repo_id == "repo-2" for r in repos)

    def test_unregister_repository(self):
        """Repository is unregistered from registry."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        success = registry.unregister_repository("repo-1")

        assert success is True
        assert registry.get_repository("repo-1") is None

    def test_unregister_nonexistent_repository(self):
        """Unregister returns False for nonexistent repo."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        success = registry.unregister_repository("nonexistent")

        assert success is False


class TestRepositoryTypeValidation:
    """Test repository type validation."""

    def test_valid_repo_types(self):
        """Valid repository types are accepted."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        for repo_type in ["project", "library", "tool", "docs"]:
            entry = registry.register_repository(
                repo_id=f"repo-{repo_type}",
                repo_name=f"Repo {repo_type}",
                repo_type=repo_type,
                repo_path=f"/path/{repo_type}",
            )

            assert entry.repo_type == repo_type

    def test_invalid_repo_type_rejected(self):
        """Invalid repository types are rejected."""
        from cortex.core.registry.repo_registry import (
            RepositoryRegistry,
            InvalidRepositoryTypeError,
        )

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        with pytest.raises(InvalidRepositoryTypeError):
            registry.register_repository(
                repo_id="repo-bad",
                repo_name="Bad Repository",
                repo_type="invalid_type",
                repo_path="/path/bad",
            )


class TestRepositoryPathValidation:
    """Test repository path validation."""

    def test_absolute_path_required(self):
        """Absolute paths are required."""
        from cortex.core.registry.repo_registry import (
            RepositoryRegistry,
            InvalidRepositoryPathError,
        )

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        with pytest.raises(InvalidRepositoryPathError):
            registry.register_repository(
                repo_id="repo-bad",
                repo_name="Bad Repository",
                repo_type="project",
                repo_path="relative/path",  # Relative path
            )

    def test_nonexistent_path_warning(self):
        """Nonexistent paths trigger warning."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        # Should not raise, but may log warning
        entry = registry.register_repository(
            repo_id="repo-nonexist",
            repo_name="Nonexistent Repo",
            repo_type="project",
            repo_path="/nonexistent/path",
        )

        assert entry is not None


class TestRegistryPersistence:
    """Test registry persistence to YAML."""

    def test_export_to_yaml(self):
        """Registry exports to YAML format."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        yaml_data = registry.export_to_yaml()

        assert isinstance(yaml_data, str)
        assert "repo-1" in yaml_data
        assert "Test Repository" in yaml_data

    def test_save_to_file(self):
        """Registry saves to file."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        registry.save_to_file(temp_path)

        # Verify file exists and contains data
        import os

        assert os.path.exists(temp_path)
        with open(temp_path, "r") as f:
            content = f.read()
            assert "repo-1" in content

        os.unlink(temp_path)

    def test_load_from_file(self):
        """Registry loads from file."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            temp_path = f.name

        registry.save_to_file(temp_path)

        # Load into new registry
        new_registry = RepositoryRegistry()
        new_registry._entries = {}  # Reset

        new_registry.load_from_file(temp_path)

        # Verify loaded data
        entry = new_registry.get_repository("repo-1")
        assert entry is not None
        assert entry.repo_name == "Test Repository"

        import os

        os.unlink(temp_path)


class TestStaleEntryCleanup:
    """Test cleanup of stale registry entries."""

    def test_mark_inactive(self):
        """Repository can be marked inactive."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        registry.mark_inactive("repo-1")

        entry = registry.get_repository("repo-1")
        assert entry.status == "inactive"

    def test_cleanup_inactive_entries(self):
        """Inactive entries can be cleaned up."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Repo 1",
            repo_type="project",
            repo_path="/path/1",
        )
        registry.register_repository(
            repo_id="repo-2",
            repo_name="Repo 2",
            repo_type="project",
            repo_path="/path/2",
        )

        registry.mark_inactive("repo-1")

        cleaned = registry.cleanup_inactive_entries()

        assert cleaned >= 1
        assert registry.get_repository("repo-1") is None
        assert registry.get_repository("repo-2") is not None


class TestRegistrySearch:
    """Test registry search functionality."""

    def test_search_by_type(self):
        """Search repositories by type."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="proj-1",
            repo_name="Project 1",
            repo_type="project",
            repo_path="/path/1",
        )
        registry.register_repository(
            repo_id="lib-1",
            repo_name="Library 1",
            repo_type="library",
            repo_path="/path/2",
        )

        projects = registry.search_by_type("project")

        assert len(projects) >= 1
        assert any(r.repo_id == "proj-1" for r in projects)

    def test_search_by_name_pattern(self):
        """Search repositories by name pattern."""
        from cortex.core.registry.repo_registry import RepositoryRegistry

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-test-1",
            repo_name="Test Repository 1",
            repo_type="project",
            repo_path="/path/1",
        )
        registry.register_repository(
            repo_id="repo-prod-1",
            repo_name="Prod Repository 1",
            repo_type="project",
            repo_path="/path/2",
        )

        results = registry.search_by_name_pattern("Test")

        assert len(results) >= 1
        assert any(r.repo_id == "repo-test-1" for r in results)


class TestRegistryThreadSafety:
    """Test thread safety of registry operations."""

    def test_concurrent_registration(self):
        """Multiple concurrent registrations work correctly."""
        from cortex.core.registry.repo_registry import RepositoryRegistry
        import threading

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        def register(repo_id: str):
            registry.register_repository(
                repo_id=repo_id,
                repo_name=f"Repo {repo_id}",
                repo_type="project",
                repo_path=f"/path/{repo_id}",
            )

        threads = [
            threading.Thread(target=register, args=(f"repo-{i}",))
            for i in range(5)
        ]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(registry.list_repositories()) >= 5

    def test_concurrent_reads(self):
        """Multiple concurrent reads work correctly."""
        from cortex.core.registry.repo_registry import RepositoryRegistry
        import threading

        registry = RepositoryRegistry()
        registry._entries = {}  # Reset

        registry.register_repository(
            repo_id="repo-1",
            repo_name="Test Repository",
            repo_type="project",
            repo_path="/path/to/repo",
        )

        results = []

        def read_repo(repo_id: str):
            entry = registry.get_repository(repo_id)
            if entry:
                results.append(entry)

        threads = [threading.Thread(target=read_repo, args=("repo-1",)) for _ in range(5)]

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(results) == 5
