"""
Database Migration Runner.

Manages database schema migrations with version tracking and rollback support.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple, Optional


logger = logging.getLogger(__name__)


class MigrationRunner:
    """
    Database migration management system.
    
    Tracks applied migrations and executes new migrations in order.
    Supports idempotent migrations and validation.
    """
    
    def __init__(self, db_path: str, migrations_dir: Optional[str] = None):
        """
        Initialize migration runner.
        
        Args:
            db_path: Path to SQLite database
            migrations_dir: Directory containing migration SQL files
        """
        self.db_path = db_path
        
        if migrations_dir:
            self.migrations_dir = Path(migrations_dir)
        else:
            self.migrations_dir = Path(__file__).parent / "migrations"
        
        self._conn: Optional[sqlite3.Connection] = None
    
    def connect(self) -> None:
        """Establish database connection."""
        if self._conn is None:
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA foreign_keys = ON")
    
    def close(self) -> None:
        """Close database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def _ensure_migrations_table(self) -> None:
        """Create schema_migrations table if it doesn't exist."""
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS schema_migrations (
                version INTEGER PRIMARY KEY,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description TEXT NOT NULL
            )
        """)
        self._conn.commit()
    
    def _get_applied_versions(self) -> List[int]:
        """Get list of applied migration versions."""
        cursor = self._conn.execute("""
            SELECT version FROM schema_migrations ORDER BY version
        """)
        return [row["version"] for row in cursor.fetchall()]
    
    def _get_pending_migrations(self) -> List[Tuple[int, Path]]:
        """
        Get list of pending migrations to apply.
        
        Returns:
            List of (version, migration_file_path) tuples
        """
        if not self.migrations_dir.exists():
            logger.warning(f"Migrations directory not found: {self.migrations_dir}")
            return []
        
        applied_versions = set(self._get_applied_versions())
        pending = []
        
        # Find all .sql files in migrations directory
        for migration_file in sorted(self.migrations_dir.glob("*.sql")):
            # Extract version from filename (e.g., "001_initial_schema.sql" → 1)
            try:
                version_str = migration_file.stem.split("_")[0]
                version = int(version_str)
                
                if version not in applied_versions:
                    pending.append((version, migration_file))
                    
            except (ValueError, IndexError):
                logger.warning(f"Invalid migration filename format: {migration_file.name}")
                continue
        
        return sorted(pending, key=lambda x: x[0])
    
    def _apply_migration(self, version: int, migration_file: Path) -> bool:
        """
        Apply a single migration.
        
        Args:
            version: Migration version number
            migration_file: Path to migration SQL file
        
        Returns:
            True if migration applied successfully
        """
        try:
            logger.info(f"Applying migration {version}: {migration_file.name}")
            
            with open(migration_file, 'r') as f:
                migration_sql = f.read()
            
            # Execute migration in transaction
            self._conn.execute("BEGIN")
            
            try:
                # Execute migration SQL
                self._conn.executescript(migration_sql)
                
                # Record migration in schema_migrations
                # (Skip if initial schema already created the table)
                try:
                    self._conn.execute("""
                        INSERT OR IGNORE INTO schema_migrations (version, description)
                        VALUES (?, ?)
                    """, (version, migration_file.stem))
                except sqlite3.OperationalError:
                    # Table might not exist yet (initial migration)
                    pass
                
                self._conn.execute("COMMIT")
                logger.info(f"Migration {version} applied successfully")
                return True
                
            except Exception as e:
                self._conn.execute("ROLLBACK")
                logger.error(f"Migration {version} failed: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error applying migration {version}: {e}")
            return False
    
    def run_migrations(self) -> Tuple[int, int]:
        """
        Run all pending migrations.
        
        Returns:
            Tuple of (applied_count, failed_count)
        """
        self.connect()
        self._ensure_migrations_table()
        
        pending = self._get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return (0, 0)
        
        logger.info(f"Found {len(pending)} pending migrations")
        
        applied_count = 0
        failed_count = 0
        
        for version, migration_file in pending:
            if self._apply_migration(version, migration_file):
                applied_count += 1
            else:
                failed_count += 1
                # Stop on first failure
                break
        
        return (applied_count, failed_count)
    
    def validate_migrations(self) -> bool:
        """
        Validate migration files without applying them.
        
        Checks:
        - All migration files are readable
        - Version numbers are sequential
        - No duplicate versions
        
        Returns:
            True if all migrations are valid
        """
        if not self.migrations_dir.exists():
            logger.error(f"Migrations directory not found: {self.migrations_dir}")
            return False
        
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        if not migration_files:
            logger.warning("No migration files found")
            return True
        
        versions = []
        
        for migration_file in migration_files:
            # Check file is readable
            if not migration_file.is_file():
                logger.error(f"Migration file not readable: {migration_file}")
                return False
            
            # Extract and validate version
            try:
                version_str = migration_file.stem.split("_")[0]
                version = int(version_str)
                versions.append(version)
            except (ValueError, IndexError):
                logger.error(f"Invalid migration filename format: {migration_file.name}")
                return False
        
        # Check for duplicates
        if len(versions) != len(set(versions)):
            logger.error("Duplicate migration versions found")
            return False
        
        # Check versions are sequential (starting from 1)
        expected = list(range(1, len(versions) + 1))
        if sorted(versions) != expected:
            logger.warning(
                f"Migration versions not sequential. "
                f"Found: {sorted(versions)}, Expected: {expected}"
            )
        
        logger.info(f"All {len(versions)} migrations are valid")
        return True
    
    def get_current_version(self) -> int:
        """Get current schema version (latest applied migration)."""
        self.connect()
        self._ensure_migrations_table()
        
        cursor = self._conn.execute("""
            SELECT MAX(version) as current_version FROM schema_migrations
        """)
        
        row = cursor.fetchone()
        return row["current_version"] or 0
    
    def get_migration_status(self) -> dict:
        """
        Get migration system status.
        
        Returns:
            Dictionary with migration status information
        """
        self.connect()
        self._ensure_migrations_table()
        
        applied_versions = self._get_applied_versions()
        pending = self._get_pending_migrations()
        
        return {
            "current_version": self.get_current_version(),
            "applied_count": len(applied_versions),
            "pending_count": len(pending),
            "applied_versions": applied_versions,
            "pending_migrations": [
                {"version": v, "file": str(f.name)}
                for v, f in pending
            ]
        }
