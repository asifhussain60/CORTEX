"""
CORTEX Schema Migration Runner

Executes database schema migrations and tracks versions.
Provides rollback capability for failed migrations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import re


class SchemaMigrator:
    """Manages database schema migrations for CORTEX."""
    
    def __init__(self, cortex_path: Path):
        """
        Initialize schema migrator.
        
        Args:
            cortex_path: Path to CORTEX installation
        """
        self.cortex_path = Path(cortex_path)
        self.migrations_dir = self.cortex_path / "cortex-brain" / "migrations"
        self.migrations_dir.mkdir(parents=True, exist_ok=True)
        
    def discover_migrations(self) -> List[Path]:
        """
        Discover migration files in migrations directory.
        
        Returns:
            Sorted list of migration file paths
        """
        migrations = sorted(self.migrations_dir.glob("*.sql"))
        return migrations
    
    def get_current_version(self, db_path: Path) -> int:
        """
        Get current schema version from database.
        
        Args:
            db_path: Path to SQLite database
            
        Returns:
            Current schema version number
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("PRAGMA user_version")
            version = cursor.fetchone()[0]
            conn.close()
            return version
        except sqlite3.Error as e:
            print(f"   ⚠️  Error reading version from {db_path.name}: {e}")
            return 0
    
    def set_version(self, db_path: Path, version: int) -> None:
        """
        Set schema version in database.
        
        Args:
            db_path: Path to SQLite database
            version: Version number to set
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA user_version = {version}")
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"   ❌ Error setting version in {db_path.name}: {e}")
            raise
    
    def apply_migration(
        self,
        db_path: Path,
        migration_file: Path,
        dry_run: bool = False
    ) -> bool:
        """
        Apply migration to database.
        
        Args:
            db_path: Path to SQLite database
            migration_file: Path to migration SQL file
            dry_run: If True, validate but don't execute
            
        Returns:
            True if successful
        """
        print(f"   🔧 Applying {migration_file.name} to {db_path.name}...")
        
        # Read migration SQL
        with open(migration_file, 'r', encoding='utf-8') as f:
            sql = f.read()
        
        if dry_run:
            print(f"      [DRY RUN] Would execute migration")
            return True
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Execute migration (should be wrapped in transaction)
            cursor.executescript(sql)
            
            conn.commit()
            conn.close()
            
            print(f"      ✅ Migration applied successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"      ❌ Migration failed: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False
    
    def migrate_database(
        self,
        db_path: Path,
        target_version: Optional[int] = None,
        dry_run: bool = False
    ) -> bool:
        """
        Migrate database to target version.
        
        Args:
            db_path: Path to SQLite database
            target_version: Version to migrate to, or None for latest
            dry_run: If True, validate but don't execute
            
        Returns:
            True if all migrations successful
        """
        if not db_path.exists():
            print(f"   ⚠️  Database not found: {db_path}")
            return True  # Not an error, just doesn't exist yet
        
        current_version = self.get_current_version(db_path)
        print(f"   📊 Current schema version: {current_version}")
        
        # Discover available migrations
        migrations = self.discover_migrations()
        
        if not migrations:
            print(f"   ℹ️  No migrations found")
            return True
        
        # Determine migrations to apply
        migrations_to_apply = []
        for migration in migrations:
            # Extract version from filename (e.g., "001_add_user_prefs.sql" -> 1)
            match = re.match(r'^(\d+)_', migration.name)
            if match:
                version = int(match.group(1))
                if version > current_version:
                    if target_version is None or version <= target_version:
                        migrations_to_apply.append((version, migration))
        
        if not migrations_to_apply:
            print(f"   ✅ Database already at latest version")
            return True
        
        print(f"   🔄 Applying {len(migrations_to_apply)} migrations...")
        
        # Apply migrations in order
        for version, migration_file in sorted(migrations_to_apply):
            success = self.apply_migration(db_path, migration_file, dry_run)
            if not success:
                print(f"   ❌ Migration failed, stopping")
                return False
        
        print(f"   ✅ All migrations applied successfully")
        return True
    
    def migrate_all_databases(
        self,
        target_version: Optional[int] = None,
        dry_run: bool = False
    ) -> Dict[str, bool]:
        """
        Migrate all CORTEX databases.
        
        Args:
            target_version: Version to migrate to, or None for latest
            dry_run: If True, validate but don't execute
            
        Returns:
            Dictionary of database names to success status
        """
        print(f"🔄 Migrating all CORTEX databases...")
        if dry_run:
            print(f"   🔍 DRY RUN MODE - No changes will be made")
        
        results = {}
        
        # Find all .db files in tiers
        db_paths = []
        for tier in ["tier1", "tier2", "tier3"]:
            tier_path = self.cortex_path / "cortex-brain" / tier
            if tier_path.exists():
                db_paths.extend(tier_path.glob("*.db"))
        
        for db_path in db_paths:
            success = self.migrate_database(db_path, target_version, dry_run)
            results[db_path.name] = success
        
        # Summary
        total = len(results)
        successful = sum(1 for v in results.values() if v)
        
        print(f"\n📊 Migration Summary:")
        print(f"   Total databases: {total}")
        print(f"   Successful: {successful}")
        print(f"   Failed: {total - successful}")
        
        return results
    
    def create_migration_template(
        self,
        description: str
    ) -> Path:
        """
        Create new migration file template.
        
        Args:
            description: Migration description (e.g., "add_user_preferences")
            
        Returns:
            Path to created migration file
        """
        # Find next migration number
        existing = self.discover_migrations()
        if existing:
            last_num = max(
                int(re.match(r'^(\d+)_', m.name).group(1))
                for m in existing
                if re.match(r'^(\d+)_', m.name)
            )
            next_num = last_num + 1
        else:
            next_num = 1
        
        # Create migration file
        filename = f"{next_num:03d}_{description}.sql"
        migration_path = self.migrations_dir / filename
        
        template = f"""-- Migration: {description}
-- Version: {next_num}
-- Created: {datetime.now().isoformat()}

BEGIN TRANSACTION;

-- Forward migration
-- TODO: Add your schema changes here
-- Example:
-- ALTER TABLE users ADD COLUMN preferences TEXT;

-- Update schema version
PRAGMA user_version = {next_num};

COMMIT;

-- Rollback SQL (in comments for manual recovery):
-- BEGIN TRANSACTION;
-- TODO: Add rollback statements here
-- Example:
-- ALTER TABLE users DROP COLUMN preferences;
-- PRAGMA user_version = {next_num - 1};
-- COMMIT;
"""
        
        with open(migration_path, 'w', encoding='utf-8') as f:
            f.write(template)
        
        print(f"✅ Created migration template: {migration_path}")
        return migration_path


def main():
    """CLI entry point for testing schema migrator."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python schema_migrator.py <command> [args]")
        print("\nCommands:")
        print("  migrate <cortex_path>              - Migrate all databases")
        print("  migrate-db <cortex_path> <db_file> - Migrate specific database")
        print("  version <cortex_path> <db_file>    - Get database version")
        print("  list <cortex_path>                 - List available migrations")
        print("  create <cortex_path> <description> - Create migration template")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "migrate":
        cortex_path = Path(sys.argv[2])
        migrator = SchemaMigrator(cortex_path)
        results = migrator.migrate_all_databases()
        
    elif command == "migrate-db":
        cortex_path = Path(sys.argv[2])
        db_file = Path(sys.argv[3])
        migrator = SchemaMigrator(cortex_path)
        success = migrator.migrate_database(db_file)
        
    elif command == "version":
        cortex_path = Path(sys.argv[2])
        db_file = Path(sys.argv[3])
        migrator = SchemaMigrator(cortex_path)
        version = migrator.get_current_version(db_file)
        print(f"Schema version: {version}")
        
    elif command == "list":
        cortex_path = Path(sys.argv[2])
        migrator = SchemaMigrator(cortex_path)
        migrations = migrator.discover_migrations()
        
        print(f"\n🔄 Available Migrations:\n")
        for migration in migrations:
            print(f"  • {migration.name}")
        
    elif command == "create":
        cortex_path = Path(sys.argv[2])
        description = sys.argv[3] if len(sys.argv) > 3 else "new_migration"
        migrator = SchemaMigrator(cortex_path)
        migrator.create_migration_template(description)
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
