"""
Registry SQLite Migration Script
=================================

Purpose: Convert registry.json to registry.sqlite for landing page
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml lines 324-334
Governance: CORE-011 (type hints), CORE-012 (docstrings), CORE-013 (no bare except)

Features:
- Migrate registry.json → registry.sqlite
- Backward compatibility (read both formats)
- Schema with FTS5 search
- Dashboard tile metadata

Schema:
    CREATE TABLE repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_slug TEXT NOT NULL UNIQUE,
        repo_name TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT '📁',
        health_status TEXT CHECK (health_status IN ('healthy', 'warning', 'critical')),
        health_score INTEGER CHECK (health_score BETWEEN 0 AND 100),
        last_updated TEXT NOT NULL,
        dashboard_path TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    
Usage:
    python -m cortex.visualization.registry_sqlite_migrator --migrate
"""

import argparse
import json
import logging
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@dataclass
class RegistryEntry:
    """Repository registry entry."""
    
    repo_slug: str
    repo_name: str
    description: Optional[str] = None
    icon: str = "📁"
    health_status: str = "healthy"
    health_score: int = 100
    last_updated: str = ""
    dashboard_path: str = ""
    created_at: str = ""


class RegistrySQLiteMigrator:
    """
    Migrate registry.json to registry.sqlite.
    
    Example:
        migrator = RegistrySQLiteMigrator()
        result = migrator.migrate(
            json_path=Path("company/dashboards/registry.json"),
            sqlite_path=Path("company/dashboards/registry.sqlite")
        )
    """
    
    REGISTRY_SCHEMA = """
    -- Registry database for landing page hub
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repo_slug TEXT NOT NULL UNIQUE,
        repo_name TEXT NOT NULL,
        description TEXT,
        icon TEXT DEFAULT '📁',
        health_status TEXT CHECK (health_status IN ('healthy', 'warning', 'critical')),
        health_score INTEGER CHECK (health_score BETWEEN 0 AND 100),
        last_updated TEXT NOT NULL,
        dashboard_path TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    
    CREATE INDEX IF NOT EXISTS idx_repo_slug ON repositories(repo_slug);
    CREATE INDEX IF NOT EXISTS idx_health_status ON repositories(health_status);
    CREATE INDEX IF NOT EXISTS idx_last_updated ON repositories(last_updated DESC);
    
    -- Full-text search for repositories
    CREATE VIRTUAL TABLE IF NOT EXISTS repositories_fts USING fts5(
        repo_name, description, content=repositories, content_rowid=id
    );
    
    -- View for landing page tiles
    CREATE VIEW IF NOT EXISTS landing_page_tiles AS
    SELECT 
        repo_slug,
        repo_name,
        description,
        icon,
        health_status,
        health_score,
        dashboard_path,
        last_updated
    FROM repositories
    ORDER BY last_updated DESC;
    """
    
    def migrate(
        self,
        json_path: Path,
        sqlite_path: Path,
        backup: bool = True
    ) -> bool:
        """
        Migrate registry.json to registry.sqlite.
        
        Args:
            json_path: Path to registry.json
            sqlite_path: Path to output registry.sqlite
            backup: Whether to backup existing files
            
        Returns:
            True if successful
        """
        try:
            # Backup existing files
            if backup:
                if json_path.exists():
                    backup_json = json_path.with_suffix(".json.backup")
                    backup_json.write_text(json_path.read_text())
                    logger.info(f"Backed up JSON: {backup_json}")
                
                if sqlite_path.exists():
                    backup_sqlite = sqlite_path.with_suffix(".sqlite.backup")
                    backup_sqlite.write_bytes(sqlite_path.read_bytes())
                    logger.info(f"Backed up SQLite: {backup_sqlite}")
            
            # Load JSON data
            if not json_path.exists():
                logger.warning(f"JSON file not found: {json_path}, creating empty registry")
                entries = []
            else:
                with open(json_path, "r") as f:
                    data = json.load(f)
                entries = self._parse_json_entries(data)
            
            logger.info(f"Loaded {len(entries)} registry entries from JSON")
            
            # Create SQLite database
            self._create_sqlite_database(sqlite_path, entries)
            
            logger.info(f"✅ Migration complete: {sqlite_path}")
            return True
            
        except Exception as e:
            logger.error(f"Migration failed: {e}", exc_info=True)
            return False
    
    def _parse_json_entries(self, data: dict) -> List[RegistryEntry]:
        """Parse JSON registry data into entries."""
        entries = []
        
        # Handle different JSON formats
        repositories = data.get("repositories", [])
        if not isinstance(repositories, list):
            repositories = list(repositories.values()) if isinstance(repositories, dict) else []
        
        for repo in repositories:
            entry = RegistryEntry(
                repo_slug=repo.get("slug", repo.get("repo_slug", "unknown")),
                repo_name=repo.get("name", repo.get("repo_name", "Unknown")),
                description=repo.get("description"),
                icon=repo.get("icon", "📁"),
                health_status=repo.get("health_status", "healthy"),
                health_score=repo.get("health_score", 100),
                last_updated=repo.get("last_updated", datetime.now().isoformat()),
                dashboard_path=repo.get("dashboard_path", f"repos/{repo.get('slug', 'unknown')}/dashboard.html"),
                created_at=repo.get("created_at", datetime.now().isoformat())
            )
            entries.append(entry)
        
        return entries
    
    def _create_sqlite_database(self, sqlite_path: Path, entries: List[RegistryEntry]):
        """Create registry.sqlite with entries."""
        conn = sqlite3.connect(sqlite_path)
        
        try:
            # Create schema
            conn.executescript(self.REGISTRY_SCHEMA)
            
            # Insert entries
            for entry in entries:
                conn.execute(
                    """
                    INSERT INTO repositories (
                        repo_slug, repo_name, description, icon,
                        health_status, health_score, last_updated,
                        dashboard_path, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        entry.repo_slug,
                        entry.repo_name,
                        entry.description,
                        entry.icon,
                        entry.health_status,
                        entry.health_score,
                        entry.last_updated,
                        entry.dashboard_path,
                        entry.created_at
                    )
                )
            
            # Populate FTS5
            conn.execute(
                """
                INSERT INTO repositories_fts(repositories_fts)
                VALUES('rebuild')
                """
            )
            
            conn.commit()
            logger.info(f"Inserted {len(entries)} entries into SQLite")
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def read_registry(self, registry_path: Path) -> List[RegistryEntry]:
        """
        Read registry from either JSON or SQLite (backward compatible).
        
        Args:
            registry_path: Path to registry file (json or sqlite)
            
        Returns:
            List of registry entries
        """
        if registry_path.suffix == ".json":
            with open(registry_path, "r") as f:
                data = json.load(f)
            return self._parse_json_entries(data)
        
        elif registry_path.suffix == ".sqlite":
            conn = sqlite3.connect(registry_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute(
                """
                SELECT 
                    repo_slug, repo_name, description, icon,
                    health_status, health_score, last_updated,
                    dashboard_path, created_at
                FROM repositories
                ORDER BY last_updated DESC
                """
            )
            
            entries = []
            for row in cursor.fetchall():
                entry = RegistryEntry(
                    repo_slug=row["repo_slug"],
                    repo_name=row["repo_name"],
                    description=row["description"],
                    icon=row["icon"],
                    health_status=row["health_status"],
                    health_score=row["health_score"],
                    last_updated=row["last_updated"],
                    dashboard_path=row["dashboard_path"],
                    created_at=row["created_at"]
                )
                entries.append(entry)
            
            conn.close()
            return entries
        
        else:
            raise ValueError(f"Unsupported registry format: {registry_path.suffix}")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate registry.json to registry.sqlite"
    )
    
    parser.add_argument(
        "--json-path",
        type=Path,
        default=Path("company/dashboards/registry.json"),
        help="Path to registry.json"
    )
    parser.add_argument(
        "--sqlite-path",
        type=Path,
        default=Path("company/dashboards/registry.sqlite"),
        help="Path to output registry.sqlite"
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="Skip backup of existing files"
    )
    parser.add_argument(
        "--migrate",
        action="store_true",
        help="Perform migration"
    )
    
    args = parser.parse_args()
    
    if not args.migrate:
        parser.error("--migrate flag required")
    
    migrator = RegistrySQLiteMigrator()
    success = migrator.migrate(
        json_path=args.json_path,
        sqlite_path=args.sqlite_path,
        backup=not args.no_backup
    )
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
