"""Shared Audit Trail - PHASE-DEPLOYMENT-004-multi-repo-gov.

Unified audit trail across multiple repositories.

Author: CORTEX Framework
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional


class SharedAuditTrail:
    """Unified audit trail across projects.

    Provides centralized audit logging and cross-repo search capabilities.
    """

    def __init__(self, db_path: str = "cortex_brain/state/governance.db"):
        """Initialize shared audit trail.

        Args:
            db_path: Path to unified governance database.
        """
        self.db_path = db_path
        self._ensure_db()

    def _ensure_db(self):
        """Ensure database and tables exist."""
        try:
            db_path = Path(self.db_path)
            db_path.parent.mkdir(parents=True, exist_ok=True)

            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project TEXT NOT NULL,
                    ac_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    source_project TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    details TEXT
                )
            """)

            conn.commit()
            conn.close()
        except Exception:
            pass

    def log_operation(
        self,
        project: str,
        ac_id: str,
        operation: str,
        source_project: Optional[str] = None,
        details: Optional[str] = None,
    ) -> bool:
        """Log an operation to the audit trail.

        Args:
            project: Project where operation occurred.
            ac_id: Acceptance criteria ID.
            operation: Operation type (CREATE, UPDATE, DELETE, etc.).
            source_project: Project that initiated the operation.
            details: Additional operation details.

        Returns:
            True if successful.
        """
        return self._write_to_db(
            project=project,
            ac_id=ac_id,
            operation=operation,
            source_project=source_project or project,
            details=details,
        )

    def _write_to_db(
        self,
        project: str,
        ac_id: str,
        operation: str,
        source_project: str,
        details: Optional[str] = None,
    ) -> bool:
        """Write entry to database.

        Args:
            project: Project name.
            ac_id: AC-ID.
            operation: Operation type.
            source_project: Source project.
            details: Additional details.

        Returns:
            True if successful.
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            cursor.execute(
                """INSERT INTO audit_log
                   (project, ac_id, operation, source_project, details, timestamp)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (project, ac_id, operation, source_project, details, datetime.now().isoformat())
            )

            conn.commit()
            conn.close()
            return True
        except Exception:
            return False

    def query_all(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Query all audit entries.

        Args:
            limit: Maximum entries to return.

        Returns:
            List of audit entries.
        """
        return self._query_db(limit=limit)

    def query_project(self, project: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Query audit entries for a specific project.

        Args:
            project: Project name.
            limit: Maximum entries to return.

        Returns:
            List of audit entries for the project.
        """
        return self._query_db(project=project, limit=limit)

    def _query_db(
        self,
        project: Optional[str] = None,
        ac_id: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Execute database query.

        Args:
            project: Filter by project.
            ac_id: Filter by AC-ID.
            limit: Result limit.

        Returns:
            Query results.
        """
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []

            if project:
                query += " AND project = ?"
                params.append(project)

            if ac_id:
                if "*" in ac_id:
                    query += " AND ac_id LIKE ?"
                    params.append(ac_id.replace("*", "%"))
                else:
                    query += " AND ac_id = ?"
                    params.append(ac_id)

            query += f" ORDER BY timestamp DESC LIMIT {limit}"

            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]
            conn.close()

            return results
        except Exception:
            return []

    def search_ac_id(self, ac_id: str) -> List[Dict[str, Any]]:
        """Search for AC-ID across all projects.

        Args:
            ac_id: AC-ID pattern (supports * wildcard).

        Returns:
            List of matching entries.
        """
        return self._search_ac_id(ac_id)

    def _search_ac_id(self, ac_id: str) -> List[Dict[str, Any]]:
        """Search AC-ID in database and files.

        Args:
            ac_id: AC-ID pattern.

        Returns:
            Search results.
        """
        # Search database
        db_results = self._query_db(ac_id=ac_id)

        # Add database source indicator
        for r in db_results:
            r["source"] = "database"

        return db_results

    def aggregate_stats(self) -> Dict[str, Any]:
        """Aggregate statistics across all projects.

        Returns:
            Aggregated statistics.
        """
        all_entries = self._query_db(limit=10000)

        by_project: Dict[str, int] = {}
        by_operation: Dict[str, int] = {}

        for entry in all_entries:
            project = entry.get("project", "unknown")
            operation = entry.get("operation", "unknown")

            by_project[project] = by_project.get(project, 0) + 1
            by_operation[operation] = by_operation.get(operation, 0) + 1

        return {
            "total_entries": len(all_entries),
            "by_project": by_project,
            "by_operation": by_operation,
            "unique_projects": len(by_project),
        }


__all__ = ["SharedAuditTrail"]
