"""
Infrastructure Layer - SqliteAppRepository Tests (RED Phase)

Tests for SQLite-based application registry persistence.
Uses tmp_path fixtures for isolated database testing.

Author: Asif Hussain
"""
import pytest
from datetime import datetime, timedelta
from pathlib import Path


def test_sqlite_repo_save_application(tmp_path):
    """Test saving application to SQLite database"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    app = Application(
        app_id="cortex",
        app_name="CORTEX",
        app_type="internal",
        data_path="/cortex-brain/dashboards/cortex",
        last_scan=datetime.now()
    )
    
    # Act
    repo.save(app)
    
    # Assert - Database and table should exist
    assert db_path.exists()


def test_sqlite_repo_get_by_id_existing(tmp_path):
    """Test loading existing application from database"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange - Save application first
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    original = Application(
        app_id="cortex",
        app_name="CORTEX",
        app_type="internal",
        data_path="/cortex-brain/dashboards/cortex",
        last_scan=datetime(2025, 12, 4, 10, 30, 0)
    )
    repo.save(original)
    
    # Act
    loaded = repo.get_by_id("cortex")
    
    # Assert
    assert loaded.app_id == "cortex"
    assert loaded.app_name == "CORTEX"
    assert loaded.app_type == "internal"
    assert loaded.last_scan.year == 2025


def test_sqlite_repo_get_by_id_not_found(tmp_path):
    """Test loading non-existent application raises error"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    
    # Arrange
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    # Act & Assert
    with pytest.raises(FileNotFoundError, match="Application not found"):
        repo.get_by_id("nonexistent")


def test_sqlite_repo_get_all_applications(tmp_path):
    """Test retrieving all applications"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange - Save multiple applications
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    app1 = Application(app_id="cortex", app_name="CORTEX", app_type="internal", data_path="/path1", last_scan=datetime.now())
    app2 = Application(app_id="user-app", app_name="User App", app_type="external", data_path="/path2", last_scan=datetime.now())
    
    repo.save(app1)
    repo.save(app2)
    
    # Act
    all_apps = repo.get_all()
    
    # Assert
    assert len(all_apps) == 2
    app_ids = [app.app_id for app in all_apps]
    assert "cortex" in app_ids
    assert "user-app" in app_ids


def test_sqlite_repo_update_existing_application(tmp_path):
    """Test updating existing application (upsert behavior)"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    original = Application(
        app_id="cortex",
        app_name="CORTEX",
        app_type="internal",
        data_path="/path1",
        last_scan=datetime(2025, 12, 1, 10, 0, 0)
    )
    repo.save(original)
    
    # Act - Update with new scan time
    updated = Application(
        app_id="cortex",
        app_name="CORTEX Updated",
        app_type="internal",
        data_path="/path1",
        last_scan=datetime(2025, 12, 4, 15, 30, 0)
    )
    repo.save(updated)
    
    # Assert - Should have updated, not created duplicate
    loaded = repo.get_by_id("cortex")
    assert loaded.last_scan.day == 4  # Updated scan time
    
    all_apps = repo.get_all()
    assert len(all_apps) == 1  # No duplicate


def test_sqlite_repo_exists_true(tmp_path):
    """Test exists() returns True for existing application"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    app = Application(app_id="cortex", app_name="CORTEX", app_type="internal", data_path="/path", last_scan=datetime.now())
    repo.save(app)
    
    # Act
    result = repo.exists("cortex")
    
    # Assert
    assert result is True


def test_sqlite_repo_exists_false(tmp_path):
    """Test exists() returns False for non-existent application"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    
    # Arrange
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    # Act
    result = repo.exists("nonexistent")
    
    # Assert
    assert result is False


def test_sqlite_repo_creates_database_automatically(tmp_path):
    """Test repository creates database file automatically"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    
    # Arrange
    db_path = tmp_path / "subdir" / "apps.db"
    assert not db_path.exists()
    
    # Act
    repo = SqliteAppRepository(db_path=db_path)
    
    # Assert - Database file created
    assert db_path.exists()


def test_sqlite_repo_handles_special_characters_in_app_id(tmp_path):
    """Test repository handles app_id with hyphens and underscores"""
    from src.dashboard.infrastructure.repositories.sqlite_app_repository import SqliteAppRepository
    from src.dashboard.domain.entities.application import Application
    
    # Arrange
    db_path = tmp_path / "apps.db"
    repo = SqliteAppRepository(db_path=db_path)
    
    app = Application(
        app_id="my-app_v2",
        app_name="My App v2",
        app_type="user",
        data_path="/path",
        last_scan=datetime.now()
    )
    
    # Act
    repo.save(app)
    loaded = repo.get_by_id("my-app_v2")
    
    # Assert
    assert loaded.app_id == "my-app_v2"
