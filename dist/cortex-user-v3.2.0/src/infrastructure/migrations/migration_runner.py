"""
Database Migration Runner
Manages schema migrations for CORTEX database
"""

import aiosqlite
from pathlib import Path
from typing import List
import logging

logger = logging.getLogger(__name__)


class MigrationRunner:
    """
    Manages database schema migrations.
    
    Applies SQL migration files in order and tracks applied migrations.
    """
    
    def __init__(self, database_path: str, migrations_dir: str = None):
        """
        Initialize migration runner.
        
        Args:
            database_path: Path to SQLite database
            migrations_dir: Directory containing migration SQL files
        """
        self.database_path = database_path
        
        if migrations_dir is None:
            # Default to migrations directory relative to this file
            self.migrations_dir = Path(__file__).parent / "migrations"
        else:
            self.migrations_dir = Path(migrations_dir)
    
    async def get_applied_migrations(self) -> List[int]:
        """
        Get list of applied migration versions.
        
        Returns:
            List of migration version numbers
        """
        async with aiosqlite.connect(self.database_path) as db:
            # Check if schema_migrations table exists
            cursor = await db.execute(
                """
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='schema_migrations'
                """
            )
            table_exists = await cursor.fetchone()
            
            if not table_exists:
                return []
            
            # Get applied migrations
            cursor = await db.execute(
                "SELECT version FROM schema_migrations ORDER BY version"
            )
            rows = await cursor.fetchall()
            return [row[0] for row in rows]
    
    async def get_pending_migrations(self) -> List[Path]:
        """
        Get list of pending migration files.
        
        Returns:
            List of migration file paths to apply
        """
        applied = await self.get_applied_migrations()
        
        # Get all SQL migration files
        migration_files = sorted(self.migrations_dir.glob("*.sql"))
        
        # Filter to only pending migrations
        pending = []
        for migration_file in migration_files:
            # Extract version from filename (e.g., "001_initial_schema.sql" -> 1)
            version_str = migration_file.stem.split('_')[0]
            try:
                version = int(version_str)
                if version not in applied:
                    pending.append(migration_file)
            except ValueError:
                logger.warning(f"Skipping invalid migration file: {migration_file}")
        
        return pending
    
    async def apply_migration(self, migration_file: Path) -> None:
        """
        Apply a single migration file.
        
        Args:
            migration_file: Path to SQL migration file
        """
        logger.info(f"Applying migration: {migration_file.name}")
        
        # Read migration SQL
        sql_content = migration_file.read_text()
        
        async with aiosqlite.connect(self.database_path) as db:
            # Enable foreign keys
            await db.execute("PRAGMA foreign_keys = ON")
            
            # Execute migration SQL
            await db.executescript(sql_content)
            
            await db.commit()
        
        logger.info(f"Migration applied successfully: {migration_file.name}")
    
    async def migrate(self) -> int:
        """
        Apply all pending migrations.
        
        Returns:
            Number of migrations applied
        """
        pending = await self.get_pending_migrations()
        
        if not pending:
            logger.info("No pending migrations")
            return 0
        
        logger.info(f"Found {len(pending)} pending migration(s)")
        
        for migration_file in pending:
            await self.apply_migration(migration_file)
        
        logger.info(f"Applied {len(pending)} migration(s) successfully")
        return len(pending)
    
    async def reset(self) -> None:
        """
        Reset database by dropping all tables.
        
        WARNING: This will delete all data!
        """
        logger.warning("Resetting database - all data will be lost!")
        
        async with aiosqlite.connect(self.database_path) as db:
            # Get all tables
            cursor = await db.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = await cursor.fetchall()
            
            # Drop each table
            for table in tables:
                table_name = table[0]
                if table_name != 'sqlite_sequence':  # Skip SQLite internal table
                    logger.info(f"Dropping table: {table_name}")
                    await db.execute(f"DROP TABLE IF EXISTS {table_name}")
            
            await db.commit()
        
        logger.info("Database reset complete")


async def run_migrations(database_path: str) -> None:
    """
    Run all pending migrations.
    
    Args:
        database_path: Path to SQLite database
    """
    runner = MigrationRunner(database_path)
    count = await runner.migrate()
    print(f"Applied {count} migration(s)")
