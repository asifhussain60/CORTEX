"""
Migration Manager - Safe Schema Versioning for Federated Registry

Applies SQL migrations from YAML manifest, enabling:
- Developer pulls without DB conflicts (migrations are code)
- Production environments with fresh schema
- Forward/backward compatibility tracking
- Atomic migration application with rollback support

Authority: CORE-035 (Single Canonical Source)
AC-ID: AC-MIGRATION-MGR-001

Author: Asif Hussain
Date: 2026-01-26
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

import yaml

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.path_resolver import resolve_path

logger = logging.getLogger(__name__)


@dataclass
class Migration:
    """Single database migration."""
    
    id: str
    name: str
    filename: str
    checksum: str
    description: str
    tables: List[str]
    status: str  # "active", "planned", "deprecated"
    created_at: str


@dataclass
class MigrationManifest:
    """Parsed migration manifest."""
    
    version: str
    database: str
    schema: str
    migrations: List[Migration]
    execution_order: List[str]
    reversible: bool


class MigrationManager:
    """
    Manages database schema migrations safely.
    
    Design: Migrations are version-controlled SQL files, not database objects.
    This enables:
    - Git-safe deploys (no binary DB conflicts)
    - Schema versioning that's code-reviewable
    - Fresh bootstrap on each developer environment
    - Production deployments with deterministic wiring
    """
    
    def __init__(self, migrations_dir: Path, database_path: Path):
        """
        Initialize migration manager.
        
        Args:
            migrations_dir: Path to migrations/ folder
            database_path: Path to SQLite database file
        """
        self.migrations_dir = Path(migrations_dir)
        self.database_path = Path(database_path)
        self.manifest_path = self.migrations_dir / "artifact_registry" / "migration_manifest.yaml"
        self.conn: Optional[sqlite3.Connection] = None
        
    def initialize(self) -> Union[Ok[bool], Err]:
        """
        Initialize migration system.
        
        Returns: Ok(True) if successful
        """
        try:
            if not self.manifest_path.exists():
                return Err(f"Migration manifest not found: {self.manifest_path}")
            
            self.conn = sqlite3.connect(str(self.database_path))
            self.conn.row_factory = sqlite3.Row
            
            # Create migration tracking table if not exists
            self._create_migration_tracking_table()
            
            logger.info(f"MigrationManager initialized: {self.database_path}")
            return Ok(True)
            
        except Exception as e:
            return Err(f"Failed to initialize MigrationManager: {str(e)}")
    
    def apply_all_pending(self) -> Union[Ok[List[str]], Err]:
        """
        Apply all pending migrations in order.
        
        Returns: Ok(list of applied migration IDs) or Err(error message)
        """
        try:
            # Parse manifest
            manifest_result = self._load_manifest()
            if isinstance(manifest_result, Err):
                return manifest_result
            
            manifest = manifest_result.value
            
            # Get already-applied migrations
            applied = self._get_applied_migrations()
            if isinstance(applied, Err):
                return applied
            
            applied_ids = set(applied.value)
            
            # Apply pending migrations in order
            applied_migrations = []
            
            for migration_id in manifest.execution_order:
                if migration_id in applied_ids:
                    logger.info(f"Migration {migration_id} already applied")
                    continue
                
                # Find migration in manifest
                migration = next(
                    (m for m in manifest.migrations if m.id == migration_id),
                    None
                )
                
                if not migration:
                    logger.warning(f"Migration {migration_id} not found in manifest")
                    continue
                
                # Apply migration
                result = self._apply_migration(migration)
                if isinstance(result, Err):
                    return result
                
                applied_migrations.append(migration_id)
                logger.info(f"Applied migration: {migration.name} ({migration_id})")
            
            return Ok(applied_migrations)
            
        except Exception as e:
            return Err(f"Failed to apply migrations: {str(e)}")
    
    def _apply_migration(self, migration: Migration) -> Union[Ok[bool], Err]:
        """
        Apply a single migration.
        
        Args:
            migration: Migration to apply
            
        Returns: Ok(True) if successful
        """
        try:
            # Read SQL file
            sql_file = self.migrations_dir / "artifact_registry" / migration.filename
            
            if not sql_file.exists():
                return Err(f"Migration SQL file not found: {sql_file}")
            
            sql_content = sql_file.read_text()
            
            # Calculate checksum
            calculated_checksum = hashlib.md5(sql_content.encode()).hexdigest()[:16]
            
            # Verify checksum matches manifest (if specified)
            if migration.checksum and not calculated_checksum.startswith(
                migration.checksum[:8]
            ):
                logger.warning(
                    f"Migration {migration.id} checksum mismatch: "
                    f"expected {migration.checksum}, got {calculated_checksum}"
                )
            
            # Execute SQL
            cursor = self.conn.cursor()
            
            # Split by semicolon and execute each statement
            statements = [s.strip() for s in sql_content.split(";") if s.strip()]
            
            for statement in statements:
                cursor.execute(statement)
            
            self.conn.commit()
            
            # Record migration as applied
            self._record_migration_applied(migration, calculated_checksum)
            
            return Ok(True)
            
        except sqlite3.Error as e:
            self.conn.rollback()
            return Err(f"SQLite error in migration {migration.id}: {str(e)}")
        except Exception as e:
            return Err(f"Error applying migration {migration.id}: {str(e)}")
    
    def _create_migration_tracking_table(self) -> None:
        """Create table to track applied migrations."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS migration_tracking (
                id INTEGER PRIMARY KEY,
                migration_id TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                applied_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                checksum TEXT,
                reversible BOOLEAN DEFAULT true
            )
        """)
        
        self.conn.commit()
    
    def _record_migration_applied(
        self, migration: Migration, checksum: str
    ) -> None:
        """Record that a migration was applied."""
        cursor = self.conn.cursor()
        
        cursor.execute(
            """
            INSERT OR IGNORE INTO migration_tracking 
            (migration_id, name, checksum, reversible)
            VALUES (?, ?, ?, ?)
            """,
            (migration.id, migration.name, checksum, migration.status == "active"),
        )
        
        self.conn.commit()
    
    def _get_applied_migrations(self) -> Union[Ok[List[str]], Err]:
        """Get list of already-applied migration IDs."""
        try:
            # Create table if it doesn't exist
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT migration_id FROM migration_tracking ORDER BY id
            """)
            
            rows = cursor.fetchall()
            applied_ids = [row[0] for row in rows]
            
            return Ok(applied_ids)
            
        except sqlite3.OperationalError:
            # Table doesn't exist yet, no migrations applied
            return Ok([])
        except Exception as e:
            return Err(f"Error retrieving applied migrations: {str(e)}")
    
    def _load_manifest(self) -> Union[Ok[MigrationManifest], Err]:
        """Load and parse migration manifest."""
        try:
            if not self.manifest_path.exists():
                return Err(f"Manifest not found: {self.manifest_path}")
            
            with open(self.manifest_path) as f:
                data = yaml.safe_load(f)
            
            # Parse migrations
            migrations = [
                Migration(
                    id=m["id"],
                    name=m["name"],
                    filename=m["filename"],
                    checksum=m.get("checksum", ""),
                    description=m["description"],
                    tables=m.get("tables", []),
                    status=m.get("status", "active"),
                    created_at=m.get("created_at", ""),
                )
                for m in data.get("migrations", [])
            ]
            
            manifest = MigrationManifest(
                version=data.get("version", "1.0"),
                database=data.get("database", "orchestrator_registry.db"),
                schema=data.get("schema", "artifact_registry"),
                migrations=migrations,
                execution_order=data.get("execution_order", []),
                reversible=data.get("reversible", True),
            )
            
            return Ok(manifest)
            
        except yaml.YAMLError as e:
            return Err(f"Failed to parse manifest YAML: {str(e)}")
        except Exception as e:
            return Err(f"Failed to load manifest: {str(e)}")
    
    def get_applied_migrations(self) -> Union[Ok[List[Dict[str, Any]]], Err]:
        """Get detailed info about applied migrations."""
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
                SELECT migration_id, name, applied_at, checksum
                FROM migration_tracking
                ORDER BY id
            """)
            
            migrations = [
                {
                    "id": row[0],
                    "name": row[1],
                    "applied_at": row[2],
                    "checksum": row[3],
                }
                for row in cursor.fetchall()
            ]
            
            return Ok(migrations)
            
        except Exception as e:
            return Err(f"Error retrieving migration info: {str(e)}")
    
    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
    
    def __enter__(self):
        """Context manager entry."""
        self.initialize()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_migration_manager(
    database_path: Optional[Path] = None,
) -> MigrationManager:
    """
    Factory function for creating MigrationManager.
    
    Args:
        database_path: Override database path (default: .cortex/orchestrator_registry.db)
        
    Returns:
        Configured MigrationManager instance
    """
    if database_path is None:
        database_path = resolve_path(".cortex/orchestrator_registry.db")
    
    migrations_dir = Path(__file__).parent.parent / "migrations"
    
    return MigrationManager(migrations_dir, database_path)
