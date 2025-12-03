"""
CORTEX Tier 1: Schema Migration System
Zero-downtime schema evolution with version tracking

Author: Asif Hussain
Created: December 2, 2025
Phase: 7.1 - Tier 1 Schema Completion
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Any
from datetime import datetime
from contextlib import contextmanager
from dataclasses import dataclass


@dataclass
class SchemaMigration:
    """Represents a single schema migration"""
    version: str  # e.g., "001", "002"
    name: str  # e.g., "add_working_memory_table"
    up_sql: str  # SQL to apply migration
    down_sql: str  # SQL to rollback migration
    description: Optional[str] = None


class MigrationManager:
    """
    Manages schema migrations for Tier 1 database
    
    Features:
    - Version tracking
    - Forward migrations (up)
    - Rollback migrations (down)
    - Zero-downtime evolution
    - Migration history
    
    Usage:
        manager = MigrationManager(db_path="cortex-brain/tier1/working_memory.db")
        
        # Register migration
        migration = SchemaMigration(
            version="001",
            name="add_working_memory",
            up_sql="CREATE TABLE working_memory (...)",
            down_sql="DROP TABLE working_memory"
        )
        manager.register_migration(migration)
        
        # Apply migration
        manager.apply_migration("001")
        
        # Rollback if needed
        manager.rollback_migration("001")
    """
    
    def __init__(self, db_path: Path):
        """
        Initialize migration manager
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.migrations: Dict[str, SchemaMigration] = {}
        
        self._initialize_migration_tracking()
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with context management"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _initialize_migration_tracking(self):
        """Create schema_migrations table if it doesn't exist"""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS schema_migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT NOT NULL CHECK(status IN ('applied', 'rolled_back', 'failed')),
                    error_message TEXT,
                    execution_time_ms INTEGER
                )
            """)
            
            # Index for fast version lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_migrations_version 
                ON schema_migrations(version)
            """)
            
            # Index for status queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_migrations_status 
                ON schema_migrations(status)
            """)
    
    def register_migration(self, migration: SchemaMigration):
        """
        Register a migration for tracking
        
        Args:
            migration: SchemaMigration object to register
        """
        self.migrations[migration.version] = migration
    
    def apply_migration(self, version: str) -> bool:
        """
        Apply a migration (forward)
        
        Args:
            version: Migration version to apply
            
        Returns:
            True if successful, False if already applied or failed
        """
        if version not in self.migrations:
            raise ValueError(f"Migration {version} not registered")
        
        # Check if already applied
        if self._is_migration_applied(version):
            print(f"Migration {version} already applied, skipping")
            return False
        
        migration = self.migrations[version]
        start_time = datetime.now()
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute up SQL
                cursor.executescript(migration.up_sql)
                
                # Record successful migration
                execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
                cursor.execute("""
                    INSERT INTO schema_migrations (version, name, status, execution_time_ms)
                    VALUES (?, ?, 'applied', ?)
                """, (version, migration.name, execution_time))
                
            print(f"✅ Applied migration {version}: {migration.name} ({execution_time}ms)")
            return True
            
        except Exception as e:
            # Record failed migration
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO schema_migrations (version, name, status, error_message)
                    VALUES (?, ?, 'failed', ?)
                """, (version, migration.name, str(e)))
            
            print(f"❌ Failed to apply migration {version}: {e}")
            return False
    
    def rollback_migration(self, version: str) -> bool:
        """
        Rollback a migration (reverse)
        
        Args:
            version: Migration version to rollback
            
        Returns:
            True if successful, False otherwise
        """
        if version not in self.migrations:
            raise ValueError(f"Migration {version} not registered")
        
        # Check if migration is applied
        if not self._is_migration_applied(version):
            print(f"Migration {version} not applied, nothing to rollback")
            return False
        
        migration = self.migrations[version]
        
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Execute down SQL
                cursor.executescript(migration.down_sql)
                
                # Update migration status
                cursor.execute("""
                    UPDATE schema_migrations 
                    SET status = 'rolled_back'
                    WHERE version = ?
                """, (version,))
                
            print(f"✅ Rolled back migration {version}: {migration.name}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to rollback migration {version}: {e}")
            return False
    
    def _is_migration_applied(self, version: str) -> bool:
        """
        Check if migration is already applied
        
        Args:
            version: Migration version to check
            
        Returns:
            True if applied, False otherwise
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT status FROM schema_migrations 
                WHERE version = ? AND status = 'applied'
            """, (version,))
            return cursor.fetchone() is not None
    
    def get_current_version(self) -> str:
        """
        Get current schema version (highest applied migration)
        
        Returns:
            Version string (e.g., "003") or "000" if no migrations applied
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version FROM schema_migrations 
                WHERE status = 'applied'
                ORDER BY version DESC 
                LIMIT 1
            """)
            result = cursor.fetchone()
            return result[0] if result else "000"
    
    def list_applied_migrations(self) -> List[Dict[str, Any]]:
        """
        List all applied migrations
        
        Returns:
            List of migration records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, name, applied_at, status, execution_time_ms
                FROM schema_migrations 
                WHERE status = 'applied'
                ORDER BY version ASC
            """)
            
            return [
                {
                    "version": row[0],
                    "name": row[1],
                    "applied_at": row[2],
                    "status": row[3],
                    "execution_time_ms": row[4]
                }
                for row in cursor.fetchall()
            ]
    
    def list_pending_migrations(self) -> List[SchemaMigration]:
        """
        List all registered but not yet applied migrations
        
        Returns:
            List of pending SchemaMigration objects
        """
        pending = []
        
        for version, migration in sorted(self.migrations.items()):
            if not self._is_migration_applied(version):
                pending.append(migration)
        
        return pending
    
    def apply_all_pending(self) -> Dict[str, bool]:
        """
        Apply all pending migrations in order
        
        Returns:
            Dictionary of {version: success_status}
        """
        results = {}
        pending = self.list_pending_migrations()
        
        print(f"Applying {len(pending)} pending migrations...")
        
        for migration in pending:
            results[migration.version] = self.apply_migration(migration.version)
        
        return results
    
    def get_migration_history(self) -> List[Dict[str, Any]]:
        """
        Get complete migration history including failures
        
        Returns:
            List of all migration records
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT version, name, applied_at, status, error_message, execution_time_ms
                FROM schema_migrations 
                ORDER BY applied_at DESC
            """)
            
            return [
                {
                    "version": row[0],
                    "name": row[1],
                    "applied_at": row[2],
                    "status": row[3],
                    "error_message": row[4],
                    "execution_time_ms": row[5]
                }
                for row in cursor.fetchall()
            ]
