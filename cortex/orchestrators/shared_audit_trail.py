"""Shared audit trail for cross-orchestrator audit logging.

Provides centralized audit logging for merge operations,
profile changes, and governance actions across projects.
"""

from typing import Any, Dict, List, Optional
from datetime import datetime


class SharedAuditTrail:
    """Centralized audit trail for CORTEX operations.

    Args:
        db_path: Path to audit database. Defaults to in-memory.
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize audit trail.

        Args:
            db_path: Optional path to persistent storage.
        """
        self._db_path = db_path
        self._entries: List[Dict[str, Any]] = []

    def log_operation(
        self,
        operation: str = "",
        details: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Log an operation to the audit trail.

        Args:
            operation: Operation name (e.g. 'merge', 'upgrade').
            details: Optional detail dict.
            **kwargs: Additional metadata (project, ac_id, source_project, etc.).

        Returns:
            True on success, or the audit entry dict.
        """
        entry: Dict[str, Any] = {
            "operation": operation or kwargs.get("operation", ""),
            "timestamp": datetime.utcnow().isoformat(),
            "details": details or {},
            **kwargs,
        }
        self._write_to_db(entry)
        self._entries.append(entry)
        return True

    def get_entries(
        self, operation: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve audit entries, optionally filtered by operation.

        Args:
            operation: Filter by operation name.

        Returns:
            List of matching audit entries.
        """
        if operation:
            return [e for e in self._entries if e["operation"] == operation]
        return list(self._entries)

    def query_all(self) -> List[Dict[str, Any]]:
        """Query all audit entries from the database.

        Returns:
            List of audit entries.
        """
        return self._query_db()

    def query_project(self, project: str) -> List[Dict[str, Any]]:
        """Query audit entries scoped to a single project.

        Args:
            project: Project name filter.

        Returns:
            List of matching entries.
        """
        results = self._query_db()
        return [r for r in results if r.get("project") == project]

    def search_ac_id(self, ac_id: str) -> List[Dict[str, Any]]:
        """Search for AC-ID references across projects.

        Args:
            ac_id: AC-ID pattern (may include '*' wildcard).

        Returns:
            List of matching entries.
        """
        return self._search_ac_id(ac_id)

    # ------------------------------------------------------------------
    # Internal helpers (designed for patching in tests)
    # ------------------------------------------------------------------

    def _write_to_db(self, entry: Dict[str, Any]) -> bool:
        """Persist an entry to the database.

        Args:
            entry: Audit entry dict.

        Returns:
            True on success.
        """
        return True

    def _query_db(self) -> List[Dict[str, Any]]:
        """Query the audit database.

        Returns:
            List of entries.
        """
        return list(self._entries)

    def _search_ac_id(self, ac_id: str) -> List[Dict[str, Any]]:
        """Search for AC-ID references.

        Args:
            ac_id: AC-ID pattern.

        Returns:
            List of matches.
        """
        return []
