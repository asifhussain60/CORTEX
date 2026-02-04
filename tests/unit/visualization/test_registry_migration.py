"""
Test suite for Registry SQLite migration.

Tests:
- Migrate registry.json → registry.sqlite
- Backward compatibility (read both formats)
- Schema validation
- FTS5 search

Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml lines 324-334
Governance: CORE-008 (TDD-first)
"""

import json
import sqlite3
import tempfile
from pathlib import Path

import pytest

from cortex.visualization.registry_sqlite_migrator import (
    RegistryEntry,
    RegistrySQLiteMigrator,
)


@pytest.fixture
def sample_registry_json():
    """Sample registry.json data."""
    return {
        "repositories": [
            {
                "slug": "cortex",
                "name": "CORTEX",
                "description": "AI-powered repository intelligence",
                "icon": "🧠",
                "health_status": "healthy",
                "health_score": 95,
                "last_updated": "2026-02-03T10:00:00Z",
                "dashboard_path": "repos/cortex/dashboard.html",
                "created_at": "2026-01-01T00:00:00Z"
            },
            {
                "slug": "kashkole",
                "name": "Kashkole",
                "description": "Knowledge management system",
                "icon": "💼",
                "health_status": "warning",
                "health_score": 75,
                "last_updated": "2026-02-02T10:00:00Z",
                "dashboard_path": "repos/kashkole/dashboard.html",
                "created_at": "2026-01-15T00:00:00Z"
            }
        ]
    }


@pytest.fixture
def temp_registry_dir(sample_registry_json):
    """Create temporary directory with registry.json."""
    with tempfile.TemporaryDirectory() as tmpdir:
        registry_dir = Path(tmpdir)
        
        json_file = registry_dir / "registry.json"
        json_file.write_text(json.dumps(sample_registry_json, indent=2))
        
        yield registry_dir


class TestRegistrySQLiteMigrator:
    """Test registry migration functionality."""
    
    def test_migration_creates_sqlite_file(self, temp_registry_dir):
        """Test that migration creates registry.sqlite."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        sqlite_path = temp_registry_dir / "registry.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=False)
        
        assert success
        assert sqlite_path.exists()
        assert sqlite_path.stat().st_size > 0
    
    def test_migration_preserves_data(self, temp_registry_dir):
        """Test that all JSON data is migrated to SQLite."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        sqlite_path = temp_registry_dir / "registry.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=False)
        assert success
        
        # Verify data in SQLite
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM repositories")
        count = cursor.fetchone()[0]
        assert count == 2
        
        cursor.execute("SELECT repo_slug, repo_name, health_score FROM repositories ORDER BY repo_slug")
        rows = cursor.fetchall()
        
        assert rows[0][0] == "cortex"
        assert rows[0][1] == "CORTEX"
        assert rows[0][2] == 95
        
        assert rows[1][0] == "kashkole"
        assert rows[1][1] == "Kashkole"
        assert rows[1][2] == 75
        
        conn.close()
    
    def test_migration_creates_backup(self, temp_registry_dir):
        """Test that backup files are created."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        sqlite_path = temp_registry_dir / "registry.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=True)
        assert success
        
        backup_json = temp_registry_dir / "registry.json.backup"
        assert backup_json.exists()
    
    def test_migration_creates_schema(self, temp_registry_dir):
        """Test that SQLite schema is created with tables and indexes."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        sqlite_path = temp_registry_dir / "registry.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=False)
        assert success
        
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Check tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = {row[0] for row in cursor.fetchall()}
        
        assert "repositories" in tables
        assert "repositories_fts" in tables
        
        # Check indexes
        cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}
        
        assert "idx_repo_slug" in indexes
        assert "idx_health_status" in indexes
        
        # Check view
        cursor.execute("SELECT name FROM sqlite_master WHERE type='view'")
        views = {row[0] for row in cursor.fetchall()}
        
        assert "landing_page_tiles" in views
        
        conn.close()
    
    def test_fts5_search_works(self, temp_registry_dir):
        """Test that FTS5 full-text search is functional."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        sqlite_path = temp_registry_dir / "registry.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=False)
        assert success
        
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        # Search for "intelligence"
        cursor.execute(
            """
            SELECT repo_name FROM repositories
            WHERE id IN (
                SELECT rowid FROM repositories_fts WHERE repositories_fts MATCH 'intelligence'
            )
            """
        )
        results = [row[0] for row in cursor.fetchall()]
        
        assert "CORTEX" in results
        
        conn.close()
    
    def test_backward_compatibility_read_json(self, temp_registry_dir):
        """Test reading registry.json (backward compatibility)."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        entries = migrator.read_registry(json_path)
        
        assert len(entries) == 2
        assert entries[0].repo_slug == "cortex"
        assert entries[1].repo_slug == "kashkole"
    
    def test_backward_compatibility_read_sqlite(self, temp_registry_dir):
        """Test reading registry.sqlite."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "registry.json"
        sqlite_path = temp_registry_dir / "registry.sqlite"
        
        # Migrate first
        migrator.migrate(json_path, sqlite_path, backup=False)
        
        # Read from SQLite
        entries = migrator.read_registry(sqlite_path)
        
        assert len(entries) == 2
        assert entries[0].repo_slug in ["cortex", "kashkole"]
    
    def test_empty_registry_creates_valid_database(self, temp_registry_dir):
        """Test that migration works with empty registry."""
        migrator = RegistrySQLiteMigrator()
        
        # Create empty JSON
        json_path = temp_registry_dir / "empty.json"
        json_path.write_text('{"repositories": []}')
        
        sqlite_path = temp_registry_dir / "empty.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=False)
        assert success
        
        # Verify schema exists
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM repositories")
        count = cursor.fetchone()[0]
        assert count == 0
        
        conn.close()
    
    def test_missing_json_creates_empty_registry(self, temp_registry_dir):
        """Test that missing JSON creates empty SQLite registry."""
        migrator = RegistrySQLiteMigrator()
        
        json_path = temp_registry_dir / "nonexistent.json"
        sqlite_path = temp_registry_dir / "new.sqlite"
        
        success = migrator.migrate(json_path, sqlite_path, backup=False)
        assert success
        
        # Verify empty but valid database
        conn = sqlite3.connect(sqlite_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM repositories")
        count = cursor.fetchone()[0]
        assert count == 0
        
        conn.close()
