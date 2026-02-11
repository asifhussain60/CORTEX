"""Shared Audit MCP Tool - PHASE-DEPLOYMENT-003-mcp-expansion.

Query unified governance.db across repositories.

Author: CORTEX Framework
"""

from typing import Any, Dict, List, Optional


class SharedAudit:
    """MCP tool for querying shared audit database.

    Provides unified view of governance audit across projects.
    """

    def __init__(self, db_path: str = "governance.db"):
        """Initialize shared audit.

        Args:
            db_path: Path to unified governance database.
        """
        self.db_path = db_path

    def query(
        self,
        ac_id_pattern: Optional[str] = None,
        project: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Query unified audit database.

        Args:
            ac_id_pattern: AC-ID pattern (supports * wildcard).
            project: Filter by project name.
            start_date: Filter by start date.
            end_date: Filter by end date.
            limit: Maximum results.

        Returns:
            List of matching audit entries.
        """
        return self._query_unified_db(
            ac_id_pattern=ac_id_pattern,
            project=project,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
        )

    def _query_unified_db(
        self,
        ac_id_pattern: Optional[str] = None,
        project: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Execute query against unified database.

        Args:
            ac_id_pattern: AC-ID pattern.
            project: Project filter.
            start_date: Start date filter.
            end_date: End date filter.
            limit: Result limit.

        Returns:
            Query results.
        """
        import sqlite3
        from pathlib import Path

        if not Path(self.db_path).exists():
            return []

        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            query = "SELECT * FROM audit_log WHERE 1=1"
            params = []

            if ac_id_pattern:
                if "*" in ac_id_pattern:
                    query += " AND ac_id LIKE ?"
                    params.append(ac_id_pattern.replace("*", "%"))
                else:
                    query += " AND ac_id = ?"
                    params.append(ac_id_pattern)

            if project:
                query += " AND source = ?"
                params.append(project)

            if start_date:
                query += " AND timestamp >= ?"
                params.append(start_date)

            if end_date:
                query += " AND timestamp <= ?"
                params.append(end_date)

            query += f" LIMIT {limit}"

            cursor.execute(query, params)
            results = [dict(row) for row in cursor.fetchall()]

            # Add project field if not present
            for r in results:
                if "project" not in r:
                    r["project"] = r.get("source", "unknown")

            conn.close()
            return results

        except Exception:
            return []

    def aggregate_stats(self) -> Dict[str, Any]:
        """Aggregate statistics across projects.

        Returns:
            Aggregated audit statistics.
        """
        all_entries = self._query_unified_db(limit=10000)

        by_project: Dict[str, int] = {}
        for entry in all_entries:
            project = entry.get("project", "unknown")
            by_project[project] = by_project.get(project, 0) + 1

        return {
            "total_entries": len(all_entries),
            "by_project": by_project,
            "unique_projects": len(by_project),
        }

    def get_project_summary(self, project: str) -> Dict[str, Any]:
        """Get audit summary for specific project.

        Args:
            project: Project name.

        Returns:
            Project audit summary.
        """
        entries = self._query_unified_db(project=project)

        return {
            "project": project,
            "total_entries": len(entries),
            "recent_entries": entries[:10],
        }


__all__ = ["SharedAudit"]
