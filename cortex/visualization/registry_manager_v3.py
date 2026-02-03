"""
Registry Manager v3.0 - Landing Page Repository Registry
=========================================================

Purpose: Manage registry.sqlite for dashboard landing page
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
Governance: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)

Architecture:
- Single registry.sqlite database for all repositories
- CRUD operations with atomic writes
- Auto-backup before updates
- Quick metrics extraction from dashboard.sqlite files
- Thread-safe operations

Database: company/dashboards/registry.sqlite
Table: repositories (landing page tiles)
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from cortex.models.dashboard_schema_v3 import RepositoryRegistry


class RegistryManagerV3:
    """
    Manage registry.sqlite for landing page repository catalog.

    Features:
    - CRUD operations for repository entries
    - Atomic writes with backup
    - Quick metrics sync from dashboard.sqlite
    - Search and filtering
    - Health score aggregation

    Example:
        manager = RegistryManagerV3("company/dashboards/registry.sqlite")
        manager.add_repository(
            slug="cortex",
            name="CORTEX",
            description="AI Orchestration Platform",
            health_score=85,
            primary_language="Python",
            total_loc=45000
        )
    """

    def __init__(self, registry_path: Union[str, Path]):
        """
        Initialize registry manager.

        Args:
            registry_path: Path to registry.sqlite file
        """
        self.registry_path = Path(registry_path)
        self._ensure_schema()

    def _ensure_schema(self):
        """Create registry database and schema if not exists."""
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        conn = sqlite3.connect(str(self.registry_path))
        try:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS repositories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    slug TEXT NOT NULL UNIQUE,
                    name TEXT NOT NULL,
                    description TEXT,
                    health_score INTEGER DEFAULT 0 CHECK (health_score BETWEEN 0 AND 100),
                    primary_language TEXT NOT NULL,
                    total_loc INTEGER DEFAULT 0,
                    last_updated TEXT NOT NULL,
                    dashboard_path TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_slug ON repositories(slug)")
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_health ON repositories(health_score DESC)"
            )
            conn.commit()
        finally:
            conn.close()

    # =========================================================================
    # CREATE OPERATIONS
    # =========================================================================

    def add_repository(
        self,
        slug: str,
        name: str,
        primary_language: str,
        description: Optional[str] = None,
        health_score: int = 0,
        total_loc: int = 0,
        dashboard_path: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """
        Add new repository to registry.

        Args:
            slug: URL-safe identifier (unique)
            name: Display name
            primary_language: Primary programming language
            description: Optional description
            health_score: Health score 0-100
            total_loc: Total lines of code
            dashboard_path: Path to dashboard (default: /spa/dashboard.html?repo={slug})

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = manager.add_repository(
                slug="cortex",
                name="CORTEX",
                primary_language="Python",
                health_score=85
            )
        """
        if dashboard_path is None:
            dashboard_path = f"/spa/dashboard.html?repo={slug}"

        try:
            conn = sqlite3.connect(str(self.registry_path))
            now = datetime.utcnow().isoformat()

            conn.execute(
                """
                INSERT INTO repositories (
                    slug, name, description, health_score, primary_language,
                    total_loc, last_updated, dashboard_path, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    slug,
                    name,
                    description,
                    health_score,
                    primary_language,
                    total_loc,
                    now,
                    dashboard_path,
                    now,
                ),
            )
            conn.commit()
            conn.close()

            return True, None

        except sqlite3.IntegrityError as e:
            return False, f"Repository '{slug}' already exists"
        except Exception as e:
            return False, f"Failed to add repository: {str(e)}"

    # =========================================================================
    # READ OPERATIONS
    # =========================================================================

    def get_repository(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get repository by slug.

        Args:
            slug: Repository slug

        Returns:
            Repository dictionary or None if not found

        Example:
            repo = manager.get_repository("cortex")
            if repo:
                print(repo["name"], repo["health_score"])
        """
        conn = sqlite3.connect(str(self.registry_path))
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.execute(
                "SELECT * FROM repositories WHERE slug = ?", (slug,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        finally:
            conn.close()

    def list_repositories(
        self,
        sort_by: str = "last_updated",
        order: str = "DESC",
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """
        List all repositories with sorting.

        Args:
            sort_by: Column to sort by (default: last_updated)
            order: Sort order ASC or DESC (default: DESC)
            limit: Optional row limit

        Returns:
            List of repository dictionaries

        Example:
            # Get all repos sorted by health score
            repos = manager.list_repositories(sort_by="health_score", order="DESC")

            # Get top 10 recently updated
            recent = manager.list_repositories(limit=10)
        """
        conn = sqlite3.connect(str(self.registry_path))
        conn.row_factory = sqlite3.Row

        try:
            query = f"SELECT * FROM repositories ORDER BY {sort_by} {order}"
            if limit:
                query += f" LIMIT {limit}"

            cursor = conn.execute(query)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def search_repositories(self, query: str) -> List[Dict[str, Any]]:
        """
        Search repositories by name or description.

        Args:
            query: Search query string

        Returns:
            List of matching repositories

        Example:
            results = manager.search_repositories("cortex")
        """
        conn = sqlite3.connect(str(self.registry_path))
        conn.row_factory = sqlite3.Row

        try:
            cursor = conn.execute(
                """
                SELECT * FROM repositories 
                WHERE name LIKE ? OR description LIKE ?
                ORDER BY health_score DESC
                """,
                (f"%{query}%", f"%{query}%"),
            )
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        finally:
            conn.close()

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get registry statistics.

        Returns:
            Dictionary with aggregate statistics

        Example:
            stats = manager.get_statistics()
            # {
            #   "total_repos": 25,
            #   "avg_health_score": 78.5,
            #   "total_loc": 1250000,
            #   "languages": {"Python": 15, "JavaScript": 8, "Go": 2}
            # }
        """
        conn = sqlite3.connect(str(self.registry_path))
        conn.row_factory = sqlite3.Row

        try:
            # Total repos
            cursor = conn.execute("SELECT COUNT(*) as count FROM repositories")
            total_repos = cursor.fetchone()["count"]

            # Average health score
            cursor = conn.execute("SELECT AVG(health_score) as avg FROM repositories")
            avg_health = cursor.fetchone()["avg"] or 0

            # Total LOC
            cursor = conn.execute("SELECT SUM(total_loc) as total FROM repositories")
            total_loc = cursor.fetchone()["total"] or 0

            # Language distribution
            cursor = conn.execute(
                """
                SELECT primary_language, COUNT(*) as count 
                FROM repositories 
                GROUP BY primary_language
                ORDER BY count DESC
                """
            )
            languages = {row["primary_language"]: row["count"] for row in cursor}

            return {
                "total_repos": total_repos,
                "avg_health_score": round(avg_health, 2),
                "total_loc": total_loc,
                "languages": languages,
            }
        finally:
            conn.close()

    # =========================================================================
    # UPDATE OPERATIONS
    # =========================================================================

    def update_repository(
        self, slug: str, updates: Dict[str, Any], backup: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Update repository fields.

        Args:
            slug: Repository slug
            updates: Dictionary of field updates
            backup: Whether to backup before update (default True)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = manager.update_repository(
                "cortex",
                {"health_score": 90, "total_loc": 50000}
            )
        """
        if backup:
            self._backup()

        # Build UPDATE query dynamically
        allowed_fields = {
            "name",
            "description",
            "health_score",
            "primary_language",
            "total_loc",
            "dashboard_path",
        }
        update_fields = {k: v for k, v in updates.items() if k in allowed_fields}

        if not update_fields:
            return False, "No valid fields to update"

        # Add last_updated timestamp
        update_fields["last_updated"] = datetime.utcnow().isoformat()

        set_clause = ", ".join(f"{k} = ?" for k in update_fields.keys())
        values = list(update_fields.values())
        values.append(slug)  # For WHERE clause

        try:
            conn = sqlite3.connect(str(self.registry_path))
            cursor = conn.execute(
                f"UPDATE repositories SET {set_clause} WHERE slug = ?", values
            )
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected == 0:
                return False, f"Repository '{slug}' not found"

            return True, None

        except Exception as e:
            return False, f"Update failed: {str(e)}"

    def sync_from_dashboard(
        self, slug: str, dashboard_path: Union[str, Path]
    ) -> tuple[bool, Optional[str]]:
        """
        Sync registry metrics from dashboard.sqlite.

        Args:
            slug: Repository slug
            dashboard_path: Path to dashboard.sqlite file

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = manager.sync_from_dashboard(
                "cortex",
                "company/dashboards/repos/cortex/dashboard.sqlite"
            )
        """
        dashboard_path = Path(dashboard_path)
        if not dashboard_path.exists():
            return False, f"Dashboard file not found: {dashboard_path}"

        try:
            # Extract metrics from dashboard.sqlite
            conn = sqlite3.connect(str(dashboard_path))
            conn.row_factory = sqlite3.Row

            cursor = conn.execute("SELECT * FROM repo_summary WHERE id = 1")
            row = cursor.fetchone()
            conn.close()

            if not row:
                return False, "No repo_summary data in dashboard"

            # Update registry
            updates = {
                "name": row["repo_name"],
                "description": row["description"],
                "health_score": row["health_score"],
                "primary_language": row["primary_language"],
                "total_loc": row["total_loc"],
            }

            return self.update_repository(slug, updates)

        except Exception as e:
            return False, f"Sync failed: {str(e)}"

    # =========================================================================
    # DELETE OPERATIONS
    # =========================================================================

    def delete_repository(
        self, slug: str, backup: bool = True
    ) -> tuple[bool, Optional[str]]:
        """
        Delete repository from registry.

        Args:
            slug: Repository slug
            backup: Whether to backup before delete (default True)

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = manager.delete_repository("old-repo")
        """
        if backup:
            self._backup()

        try:
            conn = sqlite3.connect(str(self.registry_path))
            cursor = conn.execute("DELETE FROM repositories WHERE slug = ?", (slug,))
            conn.commit()
            rows_affected = cursor.rowcount
            conn.close()

            if rows_affected == 0:
                return False, f"Repository '{slug}' not found"

            return True, None

        except Exception as e:
            return False, f"Delete failed: {str(e)}"

    # =========================================================================
    # BACKUP OPERATIONS
    # =========================================================================

    def _backup(self):
        """Create backup of registry.sqlite."""
        if self.registry_path.exists():
            backup_path = self.registry_path.with_suffix(".sqlite.backup")
            backup_path.write_bytes(self.registry_path.read_bytes())

    def restore_from_backup(self) -> tuple[bool, Optional[str]]:
        """
        Restore registry from backup.

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = manager.restore_from_backup()
        """
        backup_path = self.registry_path.with_suffix(".sqlite.backup")
        if not backup_path.exists():
            return False, "No backup file found"

        try:
            self.registry_path.write_bytes(backup_path.read_bytes())
            return True, None
        except Exception as e:
            return False, f"Restore failed: {str(e)}"

    # =========================================================================
    # BULK OPERATIONS
    # =========================================================================

    def bulk_add_repositories(
        self, repositories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add multiple repositories in single transaction.

        Args:
            repositories: List of repository dictionaries

        Returns:
            Dictionary with success/failure counts and errors

        Example:
            results = manager.bulk_add_repositories([
                {"slug": "repo1", "name": "Repo 1", "primary_language": "Python"},
                {"slug": "repo2", "name": "Repo 2", "primary_language": "JavaScript"},
            ])
            # {"success": 2, "failed": 0, "errors": []}
        """
        results = {"success": 0, "failed": 0, "errors": []}

        conn = sqlite3.connect(str(self.registry_path))
        try:
            conn.execute("BEGIN")

            for repo in repositories:
                try:
                    now = datetime.utcnow().isoformat()
                    dashboard_path = repo.get(
                        "dashboard_path", f"/spa/dashboard.html?repo={repo['slug']}"
                    )

                    conn.execute(
                        """
                        INSERT INTO repositories (
                            slug, name, description, health_score, primary_language,
                            total_loc, last_updated, dashboard_path, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (
                            repo["slug"],
                            repo["name"],
                            repo.get("description"),
                            repo.get("health_score", 0),
                            repo["primary_language"],
                            repo.get("total_loc", 0),
                            now,
                            dashboard_path,
                            now,
                        ),
                    )
                    results["success"] += 1

                except Exception as e:
                    results["failed"] += 1
                    results["errors"].append(f"{repo['slug']}: {str(e)}")

            conn.commit()

        except Exception as e:
            conn.rollback()
            results["errors"].append(f"Transaction failed: {str(e)}")

        finally:
            conn.close()

        return results

    def bulk_sync_from_dashboards(
        self, dashboard_base_path: Union[str, Path]
    ) -> Dict[str, Any]:
        """
        Sync all repositories from their dashboard.sqlite files.

        Args:
            dashboard_base_path: Base path to repos/ directory

        Returns:
            Dictionary with success/failure counts

        Example:
            results = manager.bulk_sync_from_dashboards(
                "company/dashboards/repos"
            )
        """
        dashboard_base_path = Path(dashboard_base_path)
        results = {"success": 0, "failed": 0, "errors": []}

        repos = self.list_repositories()
        for repo in repos:
            slug = repo["slug"]
            dashboard_path = dashboard_base_path / slug / "dashboard.sqlite"

            if dashboard_path.exists():
                success, error = self.sync_from_dashboard(slug, dashboard_path)
                if success:
                    results["success"] += 1
                else:
                    results["failed"] += 1
                    results["errors"].append(f"{slug}: {error}")
            else:
                results["failed"] += 1
                results["errors"].append(f"{slug}: dashboard.sqlite not found")

        return results

    # =========================================================================
    # EXPORT OPERATIONS
    # =========================================================================

    def export_to_json(self, output_path: Union[str, Path]) -> tuple[bool, Optional[str]]:
        """
        Export registry to JSON file (for backward compatibility).

        Args:
            output_path: Path to output JSON file

        Returns:
            Tuple of (success: bool, error_message: Optional[str])

        Example:
            success, error = manager.export_to_json(
                "company/dashboards/registry.json"
            )
        """
        try:
            repos = self.list_repositories(sort_by="name", order="ASC")
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(repos, f, indent=2, ensure_ascii=False)

            return True, None

        except Exception as e:
            return False, f"Export failed: {str(e)}"

    def import_from_json(
        self, json_path: Union[str, Path], merge: bool = False
    ) -> Dict[str, Any]:
        """
        Import repositories from JSON file.

        Args:
            json_path: Path to JSON file
            merge: If True, update existing repos; if False, skip (default False)

        Returns:
            Dictionary with import results

        Example:
            results = manager.import_from_json(
                "company/dashboards/registry.json",
                merge=True
            )
        """
        results = {"added": 0, "updated": 0, "skipped": 0, "errors": []}

        try:
            json_path = Path(json_path)
            with open(json_path, "r", encoding="utf-8") as f:
                repos = json.load(f)

            for repo in repos:
                slug = repo.get("slug")
                if not slug:
                    results["skipped"] += 1
                    results["errors"].append("Repository missing slug")
                    continue

                # Check if exists
                existing = self.get_repository(slug)

                if existing:
                    if merge:
                        success, error = self.update_repository(slug, repo)
                        if success:
                            results["updated"] += 1
                        else:
                            results["errors"].append(f"{slug}: {error}")
                    else:
                        results["skipped"] += 1
                else:
                    success, error = self.add_repository(
                        slug=slug,
                        name=repo["name"],
                        primary_language=repo["primary_language"],
                        description=repo.get("description"),
                        health_score=repo.get("health_score", 0),
                        total_loc=repo.get("total_loc", 0),
                        dashboard_path=repo.get("dashboard_path"),
                    )
                    if success:
                        results["added"] += 1
                    else:
                        results["errors"].append(f"{slug}: {error}")

        except Exception as e:
            results["errors"].append(f"Import failed: {str(e)}")

        return results


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================


def create_registry_manager(
    registry_path: str = "company/dashboards/registry.sqlite",
) -> RegistryManagerV3:
    """
    Create registry manager with default path.

    Args:
        registry_path: Path to registry.sqlite (default: company/dashboards/registry.sqlite)

    Returns:
        RegistryManagerV3 instance

    Example:
        manager = create_registry_manager()
        manager.add_repository(...)
    """
    return RegistryManagerV3(registry_path)
