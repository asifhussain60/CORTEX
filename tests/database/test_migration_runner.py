"""
Tests for Migration Runner.

Tests cover migration execution, validation, version tracking,
and rollback behavior.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import sqlite3
from pathlib import Path
from src.database.migration_runner import MigrationRunner


class TestMigrationRunner:
    """Test migration runner functionality."""
    
    @pytest.fixture
    def db_path(self, tmp_path):
        """Create temporary database path."""
        return tmp_path / "test.db"
    
    @pytest.fixture
    def migrations_dir(self, tmp_path):
        """Create temporary migrations directory."""
        migrations = tmp_path / "migrations"
        migrations.mkdir()
        return migrations
    
    @pytest.fixture
    def runner(self, db_path, migrations_dir):
        """Create migration runner instance."""
        return MigrationRunner(
            db_path=str(db_path),
            migrations_dir=str(migrations_dir)
        )
    
    def test_initialization(self, runner, db_path):
        """Test migration runner initialization."""
        assert runner.db_path == str(db_path)
        assert Path(runner.migrations_dir).name == "migrations"
    
    def test_schema_migrations_table_created(self, runner, db_path):
        """Verify schema_migrations table is created."""
        # Run migrations (should create table even with no migrations)
        runner.run_migrations()
        
        # Check table exists
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='schema_migrations'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
    
    def test_get_current_version_empty(self, runner):
        """Get current version when no migrations applied."""
        version = runner.get_current_version()
        assert version == 0
    
    def test_single_migration(self, runner, migrations_dir, db_path):
        """Run a single migration."""
        # Create migration file
        migration_file = migrations_dir / "001_create_users.sql"
        migration_file.write_text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                email TEXT NOT NULL
            );
        """)
        
        # Run migrations
        runner.run_migrations()
        
        # Verify table created
        conn = sqlite3.connect(str(db_path))
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users'
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        assert result is not None
        
        # Verify version recorded
        assert runner.get_current_version() == 1
    
    def test_multiple_migrations(self, runner, migrations_dir, db_path):
        """Run multiple migrations in sequence."""
        # Create first migration
        (migrations_dir / "001_create_users.sql").write_text("""
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL
            );
        """)
        
        # Create second migration
        (migrations_dir / "002_create_posts.sql").write_text("""
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER,
                title TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        
        # Run migrations
        runner.run_migrations()
        
        # Verify both tables created
        conn = sqlite3.connect(str(db_path))
        
        cursor = conn.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name IN ('users', 'posts')
            ORDER BY name
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert "users" in tables
        assert "posts" in tables
        
        # Verify version
        assert runner.get_current_version() == 2
    
    def test_skip_applied_migrations(self, runner, migrations_dir):
        """Skip migrations that were already applied."""
        # Create migration
        (migrations_dir / "001_create_users.sql").write_text("""
            CREATE TABLE users (id INTEGER PRIMARY KEY);
        """)
        
        # Run migrations first time
        runner.run_migrations()
        assert runner.get_current_version() == 1
        
        # Run migrations again (should skip)
        runner.run_migrations()
        assert runner.get_current_version() == 1
    
    def test_incremental_migrations(self, runner, migrations_dir):
        """Apply new migrations incrementally."""
        # Create and run first migration
        (migrations_dir / "001_create_users.sql").write_text("""
            CREATE TABLE users (id INTEGER PRIMARY KEY);
        """)
        
        runner.run_migrations()
        assert runner.get_current_version() == 1
        
        # Add second migration
        (migrations_dir / "002_create_posts.sql").write_text("""
            CREATE TABLE posts (id INTEGER PRIMARY KEY);
        """)
        
        # Run migrations again (should only run migration 002)
        runner.run_migrations()
        assert runner.get_current_version() == 2
    
    def test_migration_status(self, runner, migrations_dir):
        """Get migration status report."""
        # Create migrations
        (migrations_dir / "001_create_users.sql").write_text("CREATE TABLE users (id INTEGER);")
        (migrations_dir / "002_create_posts.sql").write_text("CREATE TABLE posts (id INTEGER);")
        (migrations_dir / "003_create_comments.sql").write_text("CREATE TABLE comments (id INTEGER);")
        
        # Run first two migrations
        runner.run_migrations()
        
        # Manually update version to 2 (simulate partial application)
        conn = sqlite3.connect(runner.db_path)
        conn.execute("DELETE FROM schema_migrations WHERE version = 3")
        conn.commit()
        conn.close()
        
        # Get status (manually check version since we modified it)
        status = runner.get_migration_status()
        
        # Verify structure of status report
        assert "current_version" in status
        assert "applied_count" in status
        assert "pending_migrations" in status
    
    def test_validate_migrations(self, runner, migrations_dir):
        """Validate migration files."""
        # Create valid migrations
        (migrations_dir / "001_create_users.sql").write_text("CREATE TABLE users (id INTEGER);")
        (migrations_dir / "002_create_posts.sql").write_text("CREATE TABLE posts (id INTEGER);")
        
        # Validation should pass
        runner.validate_migrations()  # Should not raise
    
    def test_validate_missing_migration(self, runner, migrations_dir):
        """Validation warns about gap in version sequence."""
        # Create migrations with gap (missing 002)
        (migrations_dir / "001_create_users.sql").write_text("CREATE TABLE users (id INTEGER);")
        (migrations_dir / "003_create_posts.sql").write_text("CREATE TABLE posts (id INTEGER);")
        
        # Validation should complete but log warning (not raise)
        result = runner.validate_migrations()
        assert result is True  # Still valid, just non-sequential
    
    def test_validate_duplicate_version(self, runner, migrations_dir):
        """Validation fails with duplicate version."""
        # Create duplicate version
        (migrations_dir / "001_create_users.sql").write_text("CREATE TABLE users (id INTEGER);")
        (migrations_dir / "001_create_profiles.sql").write_text("CREATE TABLE profiles (id INTEGER);")
        
        # Validation should fail
        result = runner.validate_migrations()
        assert result is False
    
    def test_migration_rollback_on_error(self, runner, migrations_dir, db_path):
        """Migration failure handling."""
        # Create valid first migration
        (migrations_dir / "001_create_users.sql").write_text("""
            CREATE TABLE users (id INTEGER PRIMARY KEY);
        """)
        
        # Run first migration
        runner.run_migrations()
        assert runner.get_current_version() == 1
        
        # Create invalid second migration (SQL syntax error)
        (migrations_dir / "002_invalid.sql").write_text("""
            CREATE INVALID SYNTAX HERE;
        """)
        
        # Run migrations - should fail on 002, error logged but returned
        runner.run_migrations()  # Will log error but continue
        
        # Verify first migration is still applied, second is not
        version = runner.get_current_version()
        assert version == 1  # Should still be 1, not 2
    
    def test_idempotent_migrations(self, runner, migrations_dir):
        """Migrations can be safely rerun."""
        # Create idempotent migration
        (migrations_dir / "001_create_users.sql").write_text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL
            );
        """)
        
        # Run migrations twice
        runner.run_migrations()
        runner.run_migrations()
        
        # Should succeed both times
        assert runner.get_current_version() == 1
    
    def test_foreign_key_enforcement(self, runner, migrations_dir, db_path):
        """Foreign key constraints enforced during migrations."""
        # Create migrations with foreign keys
        (migrations_dir / "001_create_users.sql").write_text("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE users (
                id INTEGER PRIMARY KEY,
                username TEXT NOT NULL
            );
        """)
        
        (migrations_dir / "002_create_posts.sql").write_text("""
            PRAGMA foreign_keys = ON;
            CREATE TABLE posts (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(id)
            );
        """)
        
        # Run migrations
        runner.run_migrations()
        
        # Verify foreign key constraint works
        conn = sqlite3.connect(str(db_path))
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Try to insert post with invalid user_id (should fail)
        with pytest.raises(sqlite3.IntegrityError):
            conn.execute("INSERT INTO posts (user_id) VALUES (999)")
        
        conn.close()
