"""
Unit Tests for Registry Manager v3.0
=====================================

Purpose: Test registry.sqlite CRUD operations and bulk functions
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
Governance: CORE-008 (TDD), CORE-013 (no bare except)
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from cortex.visualization.registry_manager_v3 import (
    RegistryManagerV3,
    create_registry_manager,
)


@pytest.fixture
def temp_registry_path():
    """Create temporary registry path."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        registry_path = Path(f.name)
    yield registry_path
    # Cleanup
    if registry_path.exists():
        registry_path.unlink()
    backup_path = registry_path.with_suffix(".sqlite.backup")
    if backup_path.exists():
        backup_path.unlink()


@pytest.fixture
def manager(temp_registry_path):
    """Create registry manager instance."""
    return RegistryManagerV3(temp_registry_path)


@pytest.fixture
def sample_repo_data():
    """Sample repository data."""
    return {
        "slug": "cortex",
        "name": "CORTEX",
        "primary_language": "Python",
        "description": "AI Orchestration Platform",
        "health_score": 85,
        "total_loc": 45000,
    }


# =============================================================================
# INITIALIZATION TESTS
# =============================================================================


def test_manager_initialization(temp_registry_path):
    """Test manager creates database and schema."""
    manager = RegistryManagerV3(temp_registry_path)
    assert temp_registry_path.exists()

    # Verify schema
    conn = sqlite3.connect(str(temp_registry_path))
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    assert "repositories" in tables


def test_manager_creates_directory(tmp_path):
    """Test manager creates parent directories."""
    registry_path = tmp_path / "nested" / "path" / "registry.sqlite"
    manager = RegistryManagerV3(registry_path)
    assert registry_path.exists()
    assert registry_path.parent.exists()


def test_convenience_function():
    """Test create_registry_manager convenience function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_path = Path(tmpdir) / "registry.sqlite"
        manager = create_registry_manager(str(registry_path))
        assert isinstance(manager, RegistryManagerV3)
        assert registry_path.exists()


# =============================================================================
# CREATE OPERATION TESTS
# =============================================================================


def test_add_repository_minimal(manager, sample_repo_data):
    """Test adding repository with minimal fields."""
    success, error = manager.add_repository(
        slug=sample_repo_data["slug"],
        name=sample_repo_data["name"],
        primary_language=sample_repo_data["primary_language"],
    )

    assert success
    assert error is None

    # Verify added
    repo = manager.get_repository("cortex")
    assert repo is not None
    assert repo["name"] == "CORTEX"
    assert repo["primary_language"] == "Python"


def test_add_repository_complete(manager, sample_repo_data):
    """Test adding repository with all fields."""
    success, error = manager.add_repository(**sample_repo_data)

    assert success
    assert error is None

    repo = manager.get_repository("cortex")
    assert repo["slug"] == "cortex"
    assert repo["name"] == "CORTEX"
    assert repo["description"] == "AI Orchestration Platform"
    assert repo["health_score"] == 85
    assert repo["total_loc"] == 45000


def test_add_repository_default_dashboard_path(manager):
    """Test default dashboard_path is generated."""
    success, error = manager.add_repository(
        slug="test", name="Test", primary_language="Python"
    )

    assert success
    repo = manager.get_repository("test")
    assert repo["dashboard_path"] == "/spa/dashboard.html?repo=test"


def test_add_repository_custom_dashboard_path(manager):
    """Test custom dashboard_path is used."""
    success, error = manager.add_repository(
        slug="test",
        name="Test",
        primary_language="Python",
        dashboard_path="/custom/path.html",
    )

    assert success
    repo = manager.get_repository("test")
    assert repo["dashboard_path"] == "/custom/path.html"


def test_add_repository_duplicate_slug(manager):
    """Test adding duplicate slug fails."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    # Try adding again
    success, error = manager.add_repository(
        slug="cortex", name="CORTEX 2", primary_language="Python"
    )

    assert not success
    assert "already exists" in error


def test_add_repository_auto_timestamps(manager):
    """Test created_at and last_updated are set automatically."""
    success, error = manager.add_repository(
        slug="test", name="Test", primary_language="Python"
    )

    assert success
    repo = manager.get_repository("test")
    assert repo["created_at"] is not None
    assert repo["last_updated"] is not None

    # Parse ISO8601 timestamps
    created = datetime.fromisoformat(repo["created_at"])
    updated = datetime.fromisoformat(repo["last_updated"])
    assert isinstance(created, datetime)
    assert isinstance(updated, datetime)


# =============================================================================
# READ OPERATION TESTS
# =============================================================================


def test_get_repository_exists(manager, sample_repo_data):
    """Test getting existing repository."""
    manager.add_repository(**sample_repo_data)
    repo = manager.get_repository("cortex")

    assert repo is not None
    assert repo["slug"] == "cortex"
    assert repo["name"] == "CORTEX"


def test_get_repository_not_exists(manager):
    """Test getting non-existent repository."""
    repo = manager.get_repository("nonexistent")
    assert repo is None


def test_list_repositories_empty(manager):
    """Test listing repositories when empty."""
    repos = manager.list_repositories()
    assert repos == []


def test_list_repositories_multiple(manager):
    """Test listing multiple repositories."""
    manager.add_repository(slug="repo1", name="Repo 1", primary_language="Python")
    manager.add_repository(slug="repo2", name="Repo 2", primary_language="JavaScript")
    manager.add_repository(slug="repo3", name="Repo 3", primary_language="Go")

    repos = manager.list_repositories()
    assert len(repos) == 3


def test_list_repositories_sort_by_name(manager):
    """Test sorting repositories by name."""
    manager.add_repository(slug="c", name="Charlie", primary_language="Python")
    manager.add_repository(slug="a", name="Alice", primary_language="Python")
    manager.add_repository(slug="b", name="Bob", primary_language="Python")

    repos = manager.list_repositories(sort_by="name", order="ASC")
    assert repos[0]["name"] == "Alice"
    assert repos[1]["name"] == "Bob"
    assert repos[2]["name"] == "Charlie"


def test_list_repositories_sort_by_health_score(manager):
    """Test sorting repositories by health score."""
    manager.add_repository(
        slug="repo1", name="Repo 1", primary_language="Python", health_score=70
    )
    manager.add_repository(
        slug="repo2", name="Repo 2", primary_language="Python", health_score=90
    )
    manager.add_repository(
        slug="repo3", name="Repo 3", primary_language="Python", health_score=80
    )

    repos = manager.list_repositories(sort_by="health_score", order="DESC")
    assert repos[0]["health_score"] == 90
    assert repos[1]["health_score"] == 80
    assert repos[2]["health_score"] == 70


def test_list_repositories_limit(manager):
    """Test limiting results."""
    for i in range(10):
        manager.add_repository(
            slug=f"repo{i}", name=f"Repo {i}", primary_language="Python"
        )

    repos = manager.list_repositories(limit=5)
    assert len(repos) == 5


def test_search_repositories_by_name(manager):
    """Test searching repositories by name."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")
    manager.add_repository(
        slug="cortex-brain", name="CORTEX Brain", primary_language="Python"
    )
    manager.add_repository(slug="other", name="Other App", primary_language="Python")

    results = manager.search_repositories("cortex")
    assert len(results) == 2
    assert all("cortex" in r["name"].lower() for r in results)


def test_search_repositories_by_description(manager):
    """Test searching repositories by description."""
    manager.add_repository(
        slug="app1",
        name="App 1",
        primary_language="Python",
        description="AI-powered system",
    )
    manager.add_repository(
        slug="app2",
        name="App 2",
        primary_language="Python",
        description="Machine learning platform",
    )
    manager.add_repository(
        slug="app3", name="App 3", primary_language="Python", description="Web server"
    )

    results = manager.search_repositories("AI")
    assert len(results) == 1
    assert results[0]["slug"] == "app1"


def test_search_repositories_case_insensitive(manager):
    """Test search is case-insensitive."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    results = manager.search_repositories("cortex")
    assert len(results) == 1

    results = manager.search_repositories("CORTEX")
    assert len(results) == 1

    results = manager.search_repositories("CoRtEx")
    assert len(results) == 1


def test_get_statistics_empty(manager):
    """Test statistics for empty registry."""
    stats = manager.get_statistics()
    assert stats["total_repos"] == 0
    assert stats["avg_health_score"] == 0
    assert stats["total_loc"] == 0
    assert stats["languages"] == {}


def test_get_statistics_multiple_repos(manager):
    """Test statistics with multiple repositories."""
    manager.add_repository(
        slug="repo1", name="Repo 1", primary_language="Python", health_score=80, total_loc=10000
    )
    manager.add_repository(
        slug="repo2", name="Repo 2", primary_language="Python", health_score=90, total_loc=20000
    )
    manager.add_repository(
        slug="repo3", name="Repo 3", primary_language="JavaScript", health_score=70, total_loc=15000
    )

    stats = manager.get_statistics()
    assert stats["total_repos"] == 3
    assert stats["avg_health_score"] == 80.0  # (80+90+70)/3
    assert stats["total_loc"] == 45000
    assert stats["languages"] == {"Python": 2, "JavaScript": 1}


# =============================================================================
# UPDATE OPERATION TESTS
# =============================================================================


def test_update_repository_single_field(manager):
    """Test updating single field."""
    manager.add_repository(
        slug="cortex", name="CORTEX", primary_language="Python", health_score=80
    )

    success, error = manager.update_repository("cortex", {"health_score": 90})

    assert success
    assert error is None

    repo = manager.get_repository("cortex")
    assert repo["health_score"] == 90


def test_update_repository_multiple_fields(manager):
    """Test updating multiple fields."""
    manager.add_repository(
        slug="cortex", name="CORTEX", primary_language="Python", health_score=80, total_loc=40000
    )

    success, error = manager.update_repository(
        "cortex", {"health_score": 85, "total_loc": 45000, "description": "Updated description"}
    )

    assert success
    repo = manager.get_repository("cortex")
    assert repo["health_score"] == 85
    assert repo["total_loc"] == 45000
    assert repo["description"] == "Updated description"


def test_update_repository_updates_timestamp(manager):
    """Test update modifies last_updated timestamp."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    repo_before = manager.get_repository("cortex")
    updated_before = repo_before["last_updated"]

    # Wait a moment and update
    import time

    time.sleep(0.01)

    manager.update_repository("cortex", {"health_score": 90})

    repo_after = manager.get_repository("cortex")
    updated_after = repo_after["last_updated"]

    assert updated_after > updated_before


def test_update_repository_not_exists(manager):
    """Test updating non-existent repository."""
    success, error = manager.update_repository("nonexistent", {"health_score": 90})

    assert not success
    assert "not found" in error


def test_update_repository_ignores_invalid_fields(manager):
    """Test update ignores invalid fields."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    success, error = manager.update_repository(
        "cortex", {"health_score": 90, "invalid_field": "should be ignored"}
    )

    assert success
    repo = manager.get_repository("cortex")
    assert repo["health_score"] == 90
    assert "invalid_field" not in repo


def test_update_repository_no_valid_fields(manager):
    """Test update with no valid fields."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    success, error = manager.update_repository("cortex", {"invalid_field": "value"})

    assert not success
    assert "No valid fields" in error


def test_update_repository_creates_backup(manager, temp_registry_path):
    """Test update creates backup when enabled."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    manager.update_repository("cortex", {"health_score": 90}, backup=True)

    backup_path = temp_registry_path.with_suffix(".sqlite.backup")
    assert backup_path.exists()


def test_update_repository_no_backup(manager, temp_registry_path):
    """Test update skips backup when disabled."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    # Clear any existing backup
    backup_path = temp_registry_path.with_suffix(".sqlite.backup")
    if backup_path.exists():
        backup_path.unlink()

    manager.update_repository("cortex", {"health_score": 90}, backup=False)

    assert not backup_path.exists()


# =============================================================================
# DELETE OPERATION TESTS
# =============================================================================


def test_delete_repository_exists(manager):
    """Test deleting existing repository."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    success, error = manager.delete_repository("cortex")

    assert success
    assert error is None

    # Verify deleted
    repo = manager.get_repository("cortex")
    assert repo is None


def test_delete_repository_not_exists(manager):
    """Test deleting non-existent repository."""
    success, error = manager.delete_repository("nonexistent")

    assert not success
    assert "not found" in error


def test_delete_repository_creates_backup(manager, temp_registry_path):
    """Test delete creates backup when enabled."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    manager.delete_repository("cortex", backup=True)

    backup_path = temp_registry_path.with_suffix(".sqlite.backup")
    assert backup_path.exists()


# =============================================================================
# BACKUP OPERATION TESTS
# =============================================================================


def test_backup_creates_file(manager, temp_registry_path):
    """Test backup creates .backup file."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    manager._backup()

    backup_path = temp_registry_path.with_suffix(".sqlite.backup")
    assert backup_path.exists()


def test_restore_from_backup(manager, temp_registry_path):
    """Test restoring from backup."""
    # Add initial data
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")
    manager._backup()

    # Modify data
    manager.update_repository("cortex", {"health_score": 90}, backup=False)

    # Restore backup
    success, error = manager.restore_from_backup()
    assert success

    # Verify original data restored
    repo = manager.get_repository("cortex")
    assert repo["health_score"] == 0  # Original value


def test_restore_from_backup_no_backup(manager):
    """Test restore fails when no backup exists."""
    success, error = manager.restore_from_backup()

    assert not success
    assert "No backup file" in error


# =============================================================================
# SYNC FROM DASHBOARD TESTS
# =============================================================================


def test_sync_from_dashboard_updates_registry(manager, tmp_path):
    """Test syncing from dashboard.sqlite updates registry."""
    # Create dashboard.sqlite
    dashboard_path = tmp_path / "dashboard.sqlite"
    conn = sqlite3.connect(str(dashboard_path))
    conn.execute(
        """
        CREATE TABLE repo_summary (
            id INTEGER PRIMARY KEY,
            repo_name TEXT,
            repo_slug TEXT,
            description TEXT,
            primary_language TEXT,
            health_score INTEGER,
            total_loc INTEGER,
            tech_stack TEXT,
            file_count INTEGER,
            contributor_count INTEGER,
            last_commit_date TEXT,
            created_at TEXT,
            llm_overview TEXT
        )
        """
    )
    conn.execute(
        """
        INSERT INTO repo_summary VALUES (
            1, 'CORTEX Updated', 'cortex', 'Updated description',
            'Python', 95, 50000, '[]', 100, 5, '2026-02-03', '2026-02-03', NULL
        )
        """
    )
    conn.commit()
    conn.close()

    # Add initial registry entry
    manager.add_repository(
        slug="cortex", name="CORTEX", primary_language="Python", health_score=80
    )

    # Sync from dashboard
    success, error = manager.sync_from_dashboard("cortex", dashboard_path)

    assert success
    assert error is None

    # Verify updated
    repo = manager.get_repository("cortex")
    assert repo["name"] == "CORTEX Updated"
    assert repo["description"] == "Updated description"
    assert repo["health_score"] == 95
    assert repo["total_loc"] == 50000


def test_sync_from_dashboard_file_not_found(manager):
    """Test sync fails when dashboard file not found."""
    manager.add_repository(slug="cortex", name="CORTEX", primary_language="Python")

    success, error = manager.sync_from_dashboard("cortex", "/nonexistent/dashboard.sqlite")

    assert not success
    assert "not found" in error


# =============================================================================
# BULK OPERATION TESTS
# =============================================================================


def test_bulk_add_repositories_success(manager):
    """Test bulk adding multiple repositories."""
    repos = [
        {"slug": "repo1", "name": "Repo 1", "primary_language": "Python"},
        {"slug": "repo2", "name": "Repo 2", "primary_language": "JavaScript"},
        {"slug": "repo3", "name": "Repo 3", "primary_language": "Go"},
    ]

    results = manager.bulk_add_repositories(repos)

    assert results["success"] == 3
    assert results["failed"] == 0
    assert len(results["errors"]) == 0

    # Verify all added
    assert manager.get_repository("repo1") is not None
    assert manager.get_repository("repo2") is not None
    assert manager.get_repository("repo3") is not None


def test_bulk_add_repositories_partial_failure(manager):
    """Test bulk add with some failures."""
    # Add one repo first to cause duplicate
    manager.add_repository(slug="repo1", name="Repo 1", primary_language="Python")

    repos = [
        {"slug": "repo1", "name": "Repo 1 Duplicate", "primary_language": "Python"},  # Duplicate
        {"slug": "repo2", "name": "Repo 2", "primary_language": "JavaScript"},
        {"slug": "repo3", "name": "Repo 3", "primary_language": "Go"},
    ]

    results = manager.bulk_add_repositories(repos)

    assert results["success"] == 2
    assert results["failed"] == 1
    assert len(results["errors"]) == 1
    assert "repo1" in results["errors"][0]


def test_bulk_sync_from_dashboards(manager, tmp_path):
    """Test bulk syncing from multiple dashboard files."""
    # Create dashboard files
    dashboards_path = tmp_path / "repos"
    dashboards_path.mkdir()

    for slug in ["repo1", "repo2"]:
        repo_dir = dashboards_path / slug
        repo_dir.mkdir()
        dashboard_path = repo_dir / "dashboard.sqlite"

        conn = sqlite3.connect(str(dashboard_path))
        conn.execute(
            """
            CREATE TABLE repo_summary (
                id INTEGER, repo_name TEXT, repo_slug TEXT, description TEXT,
                primary_language TEXT, health_score INTEGER, total_loc INTEGER,
                tech_stack TEXT, file_count INTEGER, contributor_count INTEGER,
                last_commit_date TEXT, created_at TEXT, llm_overview TEXT
            )
            """
        )
        conn.execute(
            f"""
            INSERT INTO repo_summary VALUES (
                1, '{slug.upper()}', '{slug}', 'Description', 'Python',
                85, 10000, '[]', 50, 2, '2026-02-03', '2026-02-03', NULL
            )
            """
        )
        conn.commit()
        conn.close()

        # Add to registry
        manager.add_repository(slug=slug, name=slug, primary_language="Python")

    # Bulk sync
    results = manager.bulk_sync_from_dashboards(dashboards_path)

    assert results["success"] == 2
    assert results["failed"] == 0


# =============================================================================
# EXPORT/IMPORT TESTS
# =============================================================================


def test_export_to_json(manager, tmp_path):
    """Test exporting registry to JSON."""
    manager.add_repository(slug="repo1", name="Repo 1", primary_language="Python")
    manager.add_repository(slug="repo2", name="Repo 2", primary_language="JavaScript")

    json_path = tmp_path / "registry.json"
    success, error = manager.export_to_json(json_path)

    assert success
    assert error is None
    assert json_path.exists()

    # Verify JSON content
    with open(json_path, "r") as f:
        data = json.load(f)

    assert len(data) == 2
    assert data[0]["slug"] == "repo1"


def test_import_from_json_new_repos(manager, tmp_path):
    """Test importing new repositories from JSON."""
    # Create JSON file
    json_path = tmp_path / "registry.json"
    data = [
        {
            "slug": "repo1",
            "name": "Repo 1",
            "primary_language": "Python",
            "health_score": 80,
            "total_loc": 10000,
        },
        {
            "slug": "repo2",
            "name": "Repo 2",
            "primary_language": "JavaScript",
            "health_score": 75,
            "total_loc": 8000,
        },
    ]

    with open(json_path, "w") as f:
        json.dump(data, f)

    # Import
    results = manager.import_from_json(json_path, merge=False)

    assert results["added"] == 2
    assert results["updated"] == 0
    assert results["skipped"] == 0

    # Verify imported
    assert manager.get_repository("repo1") is not None
    assert manager.get_repository("repo2") is not None


def test_import_from_json_merge_existing(manager, tmp_path):
    """Test importing with merge updates existing repos."""
    # Add initial repo
    manager.add_repository(
        slug="repo1", name="Repo 1", primary_language="Python", health_score=70
    )

    # Create JSON with updated data
    json_path = tmp_path / "registry.json"
    data = [
        {
            "slug": "repo1",
            "name": "Repo 1 Updated",
            "primary_language": "Python",
            "health_score": 90,
        }
    ]

    with open(json_path, "w") as f:
        json.dump(data, f)

    # Import with merge
    results = manager.import_from_json(json_path, merge=True)

    assert results["added"] == 0
    assert results["updated"] == 1
    assert results["skipped"] == 0

    # Verify updated
    repo = manager.get_repository("repo1")
    assert repo["name"] == "Repo 1 Updated"
    assert repo["health_score"] == 90


def test_import_from_json_skip_existing(manager, tmp_path):
    """Test importing without merge skips existing repos."""
    # Add initial repo
    manager.add_repository(slug="repo1", name="Repo 1", primary_language="Python")

    # Create JSON
    json_path = tmp_path / "registry.json"
    data = [{"slug": "repo1", "name": "Repo 1 Updated", "primary_language": "Python"}]

    with open(json_path, "w") as f:
        json.dump(data, f)

    # Import without merge
    results = manager.import_from_json(json_path, merge=False)

    assert results["added"] == 0
    assert results["updated"] == 0
    assert results["skipped"] == 1


# =============================================================================
# EDGE CASE TESTS
# =============================================================================


def test_health_score_validation(manager):
    """Test health_score is constrained to 0-100."""
    # Valid health scores
    manager.add_repository(
        slug="repo1", name="Repo 1", primary_language="Python", health_score=0
    )
    manager.add_repository(
        slug="repo2", name="Repo 2", primary_language="Python", health_score=100
    )

    assert manager.get_repository("repo1")["health_score"] == 0
    assert manager.get_repository("repo2")["health_score"] == 100


def test_unicode_handling(manager):
    """Test Unicode characters in names and descriptions."""
    success, error = manager.add_repository(
        slug="unicode-test",
        name="测试 Test 🚀",
        primary_language="Python",
        description="Description with émojis 🎉 and spëcial çharacters",
    )

    assert success
    repo = manager.get_repository("unicode-test")
    assert repo["name"] == "测试 Test 🚀"
    assert "émojis 🎉" in repo["description"]


def test_empty_list_operations(manager):
    """Test operations on empty registry."""
    repos = manager.list_repositories()
    assert repos == []

    results = manager.search_repositories("query")
    assert results == []

    stats = manager.get_statistics()
    assert stats["total_repos"] == 0


def test_concurrent_operations(manager):
    """Test multiple operations in sequence."""
    # Add
    manager.add_repository(slug="test", name="Test", primary_language="Python")

    # Update
    manager.update_repository("test", {"health_score": 85})

    # Get
    repo = manager.get_repository("test")
    assert repo["health_score"] == 85

    # Delete
    manager.delete_repository("test")

    # Verify deleted
    assert manager.get_repository("test") is None
