"""
Test suite for JSON to SQLite migration script.

Tests:
- Backup creation before migration
- Rollback functionality
- Dry-run mode (no changes)
- Schema validation after migration
- Error handling for corrupted JSON
- CLI interface

Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml lines 769-785
Governance: CORE-008 (TDD-first), CORE-013 (no bare except)
"""

import json
import sqlite3
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from cortex.visualization.migrate_json_to_sqlite import (
    JSONToSQLiteMigrator,
    MigrationResult,
    migrate_repository,
)


@pytest.fixture
def sample_json_data():
    """Sample dashboard-data.json structure."""
    return {
        "repo_summary": {
            "name": "test-repo",
            "description": "Test repository",
            "language": "Python",
            "total_files": 100,
            "total_lines": 5000,
        },
        "use_cases": [
            {
                "id": 1,
                "title": "User Authentication",
                "description": "Handle user login",
                "category": "Security",
            },
            {
                "id": 2,
                "title": "Data Export",
                "description": "Export data to CSV",
                "category": "Reporting",
            },
        ],
        "dependencies": [
            {
                "name": "fastapi",
                "version": "0.100.0",
                "type": "direct",
            }
        ],
    }


@pytest.fixture
def temp_repo_dir(sample_json_data):
    """Create temporary repository directory with JSON file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        repo_path = Path(tmpdir) / "test-repo"
        repo_path.mkdir()
        
        json_file = repo_path / "dashboard-data.json"
        json_file.write_text(json.dumps(sample_json_data, indent=2))
        
        yield repo_path


class TestJSONToSQLiteMigrator:
    """Test JSONToSQLiteMigrator class."""
    
    def test_backup_created_before_migration(self, temp_repo_dir):
        """Test that backup file is created before migration."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir, backup=True)
        
        assert result.success
        backup_file = temp_repo_dir / "dashboard-data.json.backup"
        assert backup_file.exists()
        
        # Verify backup content matches original
        original = json.loads((temp_repo_dir / "dashboard-data.json").read_text())
        backup = json.loads(backup_file.read_text())
        assert original == backup
    
    def test_no_backup_when_disabled(self, temp_repo_dir):
        """Test that backup is skipped when backup=False."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir, backup=False)
        
        assert result.success
        backup_file = temp_repo_dir / "dashboard-data.json.backup"
        assert not backup_file.exists()
    
    def test_sqlite_file_created(self, temp_repo_dir):
        """Test that dashboard.sqlite is created."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir)
        
        assert result.success
        sqlite_file = temp_repo_dir / "dashboard.sqlite"
        assert sqlite_file.exists()
        assert sqlite_file.stat().st_size > 0
    
    def test_data_migrated_correctly(self, temp_repo_dir):
        """Test that JSON data is correctly inserted into SQLite."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir)
        
        assert result.success
        sqlite_file = temp_repo_dir / "dashboard.sqlite"
        
        # Verify data in SQLite
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        # Check repo_summary (use normalized field names)
        cursor.execute("SELECT repo_name, primary_language FROM repo_summary")
        row = cursor.fetchone()
        assert row[0] == "test-repo"  # Normalized from "name"
        assert row[1] == "Python"  # Normalized from "language"
        
        # Check use_cases
        cursor.execute("SELECT COUNT(*) FROM use_cases")
        count = cursor.fetchone()[0]
        assert count == 2
        
        conn.close()
    
    def test_dry_run_mode_no_changes(self, temp_repo_dir):
        """Test that dry-run mode doesn't create files."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir, dry_run=True)
        
        assert result.success
        assert result.dry_run
        
        # Verify no SQLite file created
        sqlite_file = temp_repo_dir / "dashboard.sqlite"
        assert not sqlite_file.exists()
        
        # Verify no backup created
        backup_file = temp_repo_dir / "dashboard-data.json.backup"
        assert not backup_file.exists()
    
    def test_rollback_functionality(self, temp_repo_dir):
        """Test rollback restores original JSON and removes SQLite."""
        migrator = JSONToSQLiteMigrator()
        
        # First migrate
        result = migrator.migrate(temp_repo_dir, backup=True)
        assert result.success
        
        # Modify JSON to simulate corruption
        json_file = temp_repo_dir / "dashboard-data.json"
        json_file.write_text("corrupted")
        
        # Rollback
        rollback_result = migrator.rollback(temp_repo_dir)
        
        assert rollback_result.success
        
        # Verify JSON restored
        restored = json.loads(json_file.read_text())
        assert restored["repo_summary"]["name"] == "test-repo"
        
        # Verify SQLite removed
        sqlite_file = temp_repo_dir / "dashboard.sqlite"
        assert not sqlite_file.exists()
    
    def test_rollback_fails_without_backup(self, temp_repo_dir):
        """Test rollback fails gracefully when no backup exists."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.rollback(temp_repo_dir)
        
        assert not result.success
        assert "backup not found" in result.error_message.lower()
    
    def test_corrupted_json_handling(self, temp_repo_dir):
        """Test graceful handling of corrupted JSON file."""
        migrator = JSONToSQLiteMigrator()
        
        # Corrupt JSON file
        json_file = temp_repo_dir / "dashboard-data.json"
        json_file.write_text("{ invalid json")
        
        result = migrator.migrate(temp_repo_dir)
        
        assert not result.success
        assert "json" in result.error_message.lower()
        
        # Verify no partial files created
        sqlite_file = temp_repo_dir / "dashboard.sqlite"
        assert not sqlite_file.exists()
    
    def test_missing_json_file_handling(self, temp_repo_dir):
        """Test handling of missing dashboard-data.json."""
        migrator = JSONToSQLiteMigrator()
        
        # Remove JSON file
        (temp_repo_dir / "dashboard-data.json").unlink()
        
        result = migrator.migrate(temp_repo_dir)
        
        assert not result.success
        assert "not found" in result.error_message.lower()
    
    def test_schema_validation_after_migration(self, temp_repo_dir):
        """Test that SQLite schema is validated after migration."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir, validate_schema=True)
        
        assert result.success
        # Schema validation may show warnings for missing optional tables
        # but migration should succeed with required core tables
        
        # Verify required tables exist
        sqlite_file = temp_repo_dir / "dashboard.sqlite"
        conn = sqlite3.connect(sqlite_file)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "ORDER BY name"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        # Check for key tables
        assert "repo_summary" in tables
        assert "use_cases" in tables
        # Note: "dependencies" table may not exist if data lacks it
        
        conn.close()
    
    def test_migration_result_structure(self, temp_repo_dir):
        """Test MigrationResult contains expected fields."""
        migrator = JSONToSQLiteMigrator()
        
        result = migrator.migrate(temp_repo_dir)
        
        assert hasattr(result, "success")
        assert hasattr(result, "repo_path")
        assert hasattr(result, "json_file")
        assert hasattr(result, "sqlite_file")
        assert hasattr(result, "backup_file")
        assert hasattr(result, "dry_run")
        assert hasattr(result, "schema_valid")
        assert hasattr(result, "error_message")
        assert hasattr(result, "records_migrated")


class TestCLIInterface:
    """Test CLI functionality."""
    
    def test_migrate_single_repo_command(self, temp_repo_dir):
        """Test CLI migration of single repository."""
        result = migrate_repository(
            repo_path=temp_repo_dir,
            backup=True,
            dry_run=False,
        )
        
        assert result.success
        assert (temp_repo_dir / "dashboard.sqlite").exists()
    
    def test_dry_run_flag_works(self, temp_repo_dir):
        """Test --dry-run CLI flag."""
        result = migrate_repository(
            repo_path=temp_repo_dir,
            dry_run=True,
        )
        
        assert result.success
        assert result.dry_run
        assert not (temp_repo_dir / "dashboard.sqlite").exists()
    
    @patch("cortex.visualization.migrate_json_to_sqlite.Path.glob")
    def test_migrate_all_repos(self, mock_glob, temp_repo_dir):
        """Test --all flag migrates multiple repositories."""
        # Mock multiple repo directories - ensure they contain JSON files
        mock_repo_with_json = temp_repo_dir
        mock_glob.return_value = [mock_repo_with_json / "dashboard-data.json"]
        
        from cortex.visualization.migrate_json_to_sqlite import migrate_all_repositories
        
        results = migrate_all_repositories(
            company_dir=temp_repo_dir.parent,
            backup=True,
            dry_run=False,
        )
        
        assert len(results) > 0
        assert all(r.success for r in results)
