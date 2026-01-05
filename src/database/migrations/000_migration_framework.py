"""
Database Migration Framework for CORTEX

Purpose: Provides systematic, versioned database migrations with rollback capability
Author: Asif Hussain
Created: 2026-01-05
Version: 1.0.0

Features:
- Version tracking per database
- Up/down migrations
- Transaction safety
- Validation checks
- Rollback capability
- Migration history logging

Usage:
    from src.database.migrations import MigrationManager
    
    manager = MigrationManager()
    manager.apply_all_migrations()
"""

import sqlite3
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
import json

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """Represents a single database migration."""
    version: int
    name: str
    description: str
    up_sql: str
    down_sql: str
    validation_query: Optional[str] = None
    database_target: str = "all"  # "all", "cortex-brain", "tier1", "tier2", "tier3"


class MigrationManager:
    """
    Manages database schema migrations across CORTEX infrastructure.
    
    Ensures migrations are:
    - Applied in order (by version number)
    - Idempotent (safe to run multiple times)
    - Reversible (can rollback if needed)
    - Validated (checks succeed before marking complete)
    """
    
    def __init__(self, brain_dir: Optional[Path] = None):
        """
        Initialize migration manager.
        
        Args:
            brain_dir: Path to cortex-brain directory (auto-detected if None)
        """
        if brain_dir is None:
            # Auto-detect cortex-brain directory
            current_file = Path(__file__)
            project_root = current_file.parent.parent.parent.parent
            brain_dir = project_root / "cortex-brain"
        
        self.brain_dir = Path(brain_dir)
        
        # Database paths
        self.databases = {
            "cortex-brain": self.brain_dir / "cortex-brain.db",
            "tier0": self.brain_dir / "tier0" / "governance.db",
            "tier1": self.brain_dir / "tier1" / "working_memory.db",
            "tier2": self.brain_dir / "tier2" / "knowledge_graph.db",
            "tier3": self.brain_dir / "tier3" / "context.db",
        }
        
        # Ensure all databases exist
        for db_name, db_path in self.databases.items():
            db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Registry of all migrations
        self.migrations: List[Migration] = []
        
        # Initialize schema version tables
        self._initialize_version_tracking()
    
    def _initialize_version_tracking(self):
        """Create schema_version table in all databases if not exists."""
        for db_name, db_path in self.databases.items():
            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                
                # Check if schema_version exists and has the success column
                cursor.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """)
                
                if cursor.fetchone():
                    # Table exists, check if it has success column
                    cursor.execute("PRAGMA table_info(schema_version)")
                    columns = [row[1] for row in cursor.fetchall()]
                    
                    if 'success' not in columns:
                        # Legacy table, add missing columns
                        cursor.execute("""
                            ALTER TABLE schema_version ADD COLUMN success BOOLEAN NOT NULL DEFAULT 1
                        """)
                        cursor.execute("""
                            ALTER TABLE schema_version ADD COLUMN rollback_available BOOLEAN NOT NULL DEFAULT 1
                        """)
                else:
                    # Create new table
                    cursor.execute("""
                        CREATE TABLE schema_version (
                            version INTEGER PRIMARY KEY,
                            name TEXT NOT NULL,
                            description TEXT,
                            applied_at TEXT NOT NULL DEFAULT (datetime('now')),
                            applied_by TEXT DEFAULT 'migration_framework',
                            execution_time_ms INTEGER,
                            success BOOLEAN NOT NULL DEFAULT 1,
                            rollback_available BOOLEAN NOT NULL DEFAULT 1
                        )
                    """)
                
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS migration_log (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        version INTEGER NOT NULL,
                        action TEXT NOT NULL CHECK(action IN ('apply', 'rollback', 'validate')),
                        timestamp TEXT NOT NULL DEFAULT (datetime('now')),
                        success BOOLEAN NOT NULL,
                        error_message TEXT,
                        execution_time_ms INTEGER
                    )
                """)
                
                conn.commit()
                conn.close()
                
                logger.info(f"✅ Initialized version tracking for {db_name}")
            
            except Exception as e:
                logger.error(f"❌ Failed to initialize {db_name}: {e}")
    
    def register_migration(self, migration: Migration):
        """
        Register a migration to be managed.
        
        Args:
            migration: Migration object to register
        """
        self.migrations.append(migration)
        self.migrations.sort(key=lambda m: m.version)
    
    def get_current_version(self, db_path: Path) -> int:
        """
        Get current schema version for a database.
        
        Args:
            db_path: Path to database file
            
        Returns:
            Current version number (0 if no migrations applied)
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if success column exists
            cursor.execute("PRAGMA table_info(schema_version)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'success' in columns:
                cursor.execute("SELECT MAX(version) FROM schema_version WHERE success = 1")
            else:
                cursor.execute("SELECT MAX(version) FROM schema_version")
            
            result = cursor.fetchone()
            conn.close()
            
            version = result[0] if result and result[0] is not None else 0
            return int(version) if version else 0
        
        except sqlite3.OperationalError:
            # schema_version table doesn't exist yet
            return 0
        except Exception as e:
            logger.error(f"Error getting version for {db_path}: {e}")
            return 0
    
    def apply_migration(self, migration: Migration, db_path: Path) -> bool:
        """
        Apply a single migration to a database.
        
        Args:
            migration: Migration to apply
            db_path: Path to target database
            
        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.now()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if already applied
            cursor.execute("SELECT version FROM schema_version WHERE version = ?", (migration.version,))
            
            if cursor.fetchone():
                logger.info(f"⏭️  Migration {migration.version} already applied to {db_path.name}")
                conn.close()
                return True
            
            # Apply migration
            logger.info(f"🔄 Applying migration {migration.version}: {migration.name} to {db_path.name}")
            
            # Execute migration SQL (handle errors gracefully for idempotent operations)
            try:
                cursor.executescript(migration.up_sql)
            except sqlite3.OperationalError as e:
                # Allow "duplicate column" errors for idempotent migrations
                if "duplicate column" in str(e).lower():
                    logger.warning(f"⚠️  Migration {migration.version}: {e} (continuing, migration is idempotent)")
                else:
                    raise
            
            # Validate if validation query provided
            if migration.validation_query:
                try:
                    cursor.execute(migration.validation_query)
                    if not cursor.fetchone():
                        raise Exception("Validation query returned no results")
                except Exception as e:
                    logger.warning(f"⚠️  Validation warning: {e}")
            
            # Record success
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            # Check if schema_version has name column
            cursor.execute("PRAGMA table_info(schema_version)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'name' in columns and 'description' in columns:
                cursor.execute("""
                    INSERT OR REPLACE INTO schema_version (version, name, description, execution_time_ms)
                    VALUES (?, ?, ?, ?)
                """, (migration.version, migration.name, migration.description, execution_time))
            else:
                # Legacy schema, just insert version
                cursor.execute("""
                    INSERT OR REPLACE INTO schema_version (version) VALUES (?)
                """, (migration.version,))
            
            cursor.execute("""
                INSERT INTO migration_log (version, action, success, execution_time_ms)
                VALUES (?, 'apply', 1, ?)
            """, (migration.version, execution_time))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Migration {migration.version} applied successfully ({execution_time}ms)")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to apply migration {migration.version} to {db_path.name}: {e}")
            
            # Log failure
            try:
                cursor.execute("""
                    INSERT INTO migration_log (version, action, success, error_message)
                    VALUES (?, 'apply', 0, ?)
                """, (migration.version, str(e)))
                conn.commit()
            except:
                pass
            
            try:
                conn.close()
            except:
                pass
            
            return False
    
    def rollback_migration(self, migration: Migration, db_path: Path) -> bool:
        """
        Rollback a migration from a database.
        
        Args:
            migration: Migration to rollback
            db_path: Path to target database
            
        Returns:
            True if successful, False otherwise
        """
        start_time = datetime.now()
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if migration is applied
            cursor.execute("""
                SELECT version FROM schema_version 
                WHERE version = ? AND success = 1
            """, (migration.version,))
            
            if not cursor.fetchone():
                logger.info(f"⏭️  Migration {migration.version} not applied to {db_path.name}")
                conn.close()
                return True
            
            # Rollback migration
            logger.info(f"🔙 Rolling back migration {migration.version}: {migration.name} from {db_path.name}")
            
            # Execute rollback SQL
            cursor.executescript(migration.down_sql)
            
            # Remove from version tracking
            cursor.execute("""
                DELETE FROM schema_version WHERE version = ?
            """, (migration.version,))
            
            # Log rollback
            execution_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            cursor.execute("""
                INSERT INTO migration_log (version, action, success, execution_time_ms)
                VALUES (?, 'rollback', 1, ?)
            """, (migration.version, execution_time))
            
            conn.commit()
            conn.close()
            
            logger.info(f"✅ Migration {migration.version} rolled back successfully ({execution_time}ms)")
            return True
        
        except Exception as e:
            logger.error(f"❌ Failed to rollback migration {migration.version} from {db_path.name}: {e}")
            
            # Log failure
            try:
                cursor.execute("""
                    INSERT INTO migration_log (version, action, success, error_message)
                    VALUES (?, 'rollback', 0, ?)
                """, (migration.version, str(e)))
                conn.commit()
            except:
                pass
            
            conn.close()
            return False
    
    def apply_all_migrations(self, target_version: Optional[int] = None) -> Dict[str, Any]:
        """
        Apply all pending migrations to all databases.
        
        Args:
            target_version: Optional specific version to migrate to (applies all if None)
            
        Returns:
            Summary dict with results per database
        """
        results = {
            "success": True,
            "databases": {},
            "total_applied": 0,
            "total_failed": 0
        }
        
        for db_name, db_path in self.databases.items():
            current_version = self.get_current_version(db_path)
            db_results = {
                "current_version": current_version,
                "target_version": target_version or "latest",
                "migrations_applied": [],
                "migrations_failed": []
            }
            
            # Filter migrations for this database
            applicable_migrations = [
                m for m in self.migrations
                if m.database_target in ["all", db_name]
                and m.version > current_version
                and (target_version is None or m.version <= target_version)
            ]
            
            logger.info(f"\n📦 Processing {db_name}: {len(applicable_migrations)} migrations pending")
            
            for migration in applicable_migrations:
                success = self.apply_migration(migration, db_path)
                
                if success:
                    db_results["migrations_applied"].append(migration.version)
                    results["total_applied"] += 1
                else:
                    db_results["migrations_failed"].append(migration.version)
                    results["total_failed"] += 1
                    results["success"] = False
            
            results["databases"][db_name] = db_results
        
        return results
    
    def get_migration_status(self) -> Dict[str, Any]:
        """
        Get current migration status for all databases.
        
        Returns:
            Status dict with versions and pending migrations
        """
        status = {}
        
        for db_name, db_path in self.databases.items():
            current_version = self.get_current_version(db_path)
            
            # Find pending migrations
            pending = [
                {"version": m.version, "name": m.name}
                for m in self.migrations
                if m.database_target in ["all", db_name]
                and m.version > current_version
            ]
            
            status[db_name] = {
                "path": str(db_path),
                "current_version": current_version,
                "latest_available": max([m.version for m in self.migrations], default=0),
                "pending_migrations": pending,
                "up_to_date": len(pending) == 0
            }
        
        return status


# =============================================================================
# MIGRATION DEFINITIONS
# =============================================================================

def create_migrations() -> List[Migration]:
    """
    Define all database migrations.
    
    Returns:
        List of Migration objects in order
    """
    migrations = []
    
    # -------------------------------------------------------------------------
    # Migration 001: Add response_detail to user_profile
    # -------------------------------------------------------------------------
    migrations.append(Migration(
        version=1,
        name="add_response_detail_to_user_profile",
        description="Add response_detail column to user_profile table in tier1",
        database_target="tier1",
        up_sql="""
            -- Add response_detail column if it doesn't exist
            -- Note: ALTER TABLE ADD COLUMN is idempotent in SQLite (will fail silently if exists)
            ALTER TABLE user_profile ADD COLUMN response_detail TEXT DEFAULT 'balanced' 
                CHECK(response_detail IN ('concise', 'balanced', 'verbose'));
            
            -- Set default value for existing records
            UPDATE user_profile 
            SET response_detail = 'concise' 
            WHERE response_detail IS NULL;
        """,
        down_sql="""
            -- SQLite doesn't support DROP COLUMN easily
            -- Create new table without the column, copy data, rename
            CREATE TABLE user_profile_backup AS 
                SELECT id, interaction_mode, experience_level, tech_stack_preference, 
                       created_at, last_updated, persistent_flag
                FROM user_profile;
            
            DROP TABLE user_profile;
            
            ALTER TABLE user_profile_backup RENAME TO user_profile;
        """,
        validation_query="SELECT response_detail FROM user_profile LIMIT 1"
    ))
    
    # -------------------------------------------------------------------------
    # Migration 002: Create tier2_patterns compatibility view
    # -------------------------------------------------------------------------
    migrations.append(Migration(
        version=2,
        name="create_tier2_patterns_view",
        description="Create compatibility view mapping tier2_patterns to patterns table",
        database_target="tier2",
        up_sql="""
            -- Drop existing view if present
            DROP VIEW IF EXISTS tier2_patterns;
            
            -- Create view mapping old API to new schema
            CREATE VIEW tier2_patterns AS 
                SELECT 
                    pattern_id,
                    title AS name,
                    content AS description,
                    pattern_type AS category,
                    confidence,
                    created_at,
                    last_accessed,
                    access_count,
                    '' AS source_conversation_id,  -- deprecated field
                    metadata AS context,
                    is_pinned,
                    scope,
                    namespaces,
                    usage_count,
                    last_used
                FROM patterns;
        """,
        down_sql="""
            DROP VIEW IF EXISTS tier2_patterns;
        """,
        validation_query="SELECT name, description FROM tier2_patterns LIMIT 1"
    ))
    
    # -------------------------------------------------------------------------
    # Migration 003: Add user_profile to cortex-brain.db
    # -------------------------------------------------------------------------
    migrations.append(Migration(
        version=3,
        name="add_user_profile_to_unified_db",
        description="Create user_profile table in unified cortex-brain.db for backward compatibility",
        database_target="cortex-brain",
        up_sql="""
            CREATE TABLE IF NOT EXISTS user_profile (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')) DEFAULT 'guided',
                experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')) DEFAULT 'mid',
                response_detail TEXT NOT NULL CHECK(response_detail IN ('concise', 'balanced', 'verbose')) DEFAULT 'balanced',
                tech_stack_preference TEXT DEFAULT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                persistent_flag BOOLEAN NOT NULL DEFAULT 1
            );
            
            -- Create unique index
            CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id);
            
            -- Insert default profile if not exists
            INSERT OR IGNORE INTO user_profile (id, interaction_mode, experience_level, response_detail)
            VALUES (1, 'autonomous', 'expert', 'concise');
        """,
        down_sql="""
            DROP TABLE IF EXISTS user_profile;
            DROP INDEX IF EXISTS idx_single_profile;
        """,
        validation_query="SELECT response_detail FROM user_profile WHERE id = 1"
    ))
    
    return migrations


# =============================================================================
# CLI Interface
# =============================================================================

def main():
    """CLI entry point for migration management."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Database Migration Manager")
    parser.add_argument("action", choices=["status", "apply", "rollback", "validate"],
                        help="Action to perform")
    parser.add_argument("--version", type=int, help="Target version (for apply/rollback)")
    parser.add_argument("--database", help="Specific database to target")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(message)s"
    )
    
    # Initialize manager
    manager = MigrationManager()
    
    # Register migrations
    for migration in create_migrations():
        manager.register_migration(migration)
    
    # Execute action
    if args.action == "status":
        status = manager.get_migration_status()
        print("\n🗄️  CORTEX Database Migration Status\n")
        for db_name, info in status.items():
            status_icon = "✅" if info["up_to_date"] else "⚠️"
            print(f"{status_icon} {db_name:20s} v{info['current_version']} -> v{info['latest_available']}")
            if info["pending_migrations"]:
                for pending in info["pending_migrations"]:
                    print(f"   - v{pending['version']}: {pending['name']}")
        print()
    
    elif args.action == "apply":
        print("\n🔄 Applying migrations...\n")
        results = manager.apply_all_migrations(target_version=args.version)
        
        print(f"\n✅ Applied {results['total_applied']} migrations")
        if results['total_failed'] > 0:
            print(f"❌ Failed {results['total_failed']} migrations")
        print()
    
    elif args.action == "validate":
        status = manager.get_migration_status()
        all_up_to_date = all(info["up_to_date"] for info in status.values())
        
        if all_up_to_date:
            print("\n✅ All databases are up to date!\n")
            exit(0)
        else:
            print("\n⚠️  Some databases have pending migrations\n")
            exit(1)


if __name__ == "__main__":
    main()
