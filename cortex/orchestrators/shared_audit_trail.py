"""
SharedAuditTrail — unified governance audit trail across all repos.

Authority: CORE-035 (single canonical implementation)
AC-ID: AC-DEP-004-04
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional


class SharedAuditTrail:
    """Records and queries governance operations across multiple projects.

    All writes go to a shared database (patched in tests via
    :meth:`_write_to_db` / :meth:`_query_db` / :meth:`_search_ac_id`).
    """

    def __init__(self) -> None:
        """Initialise with an empty in-memory log."""
        self._log: List[Dict[str, Any]] = []

    # ── Write ────────────────────────────────────────────────────────

    def log_operation(
        self,
        project: str,
        ac_id: str,
        operation: str,
        **metadata: Any,
    ) -> bool:
        """Log a governance operation.

        Args:
            project: Project name (e.g. ``"KASHKOLE"``).
            ac_id: Acceptance-criteria identifier.
            operation: Operation type (``"CREATE"``, ``"UPDATE"``, …).
            **metadata: Additional fields to store.

        Returns:
            ``True`` on success.
        """
        entry: Dict[str, Any] = {
            "project": project,
            "ac_id": ac_id,
            "operation": operation,
            **metadata,
        }
        self._log.append(entry)
        return self._write_to_db(entry)

    def _write_to_db(self, entry: Dict[str, Any]) -> bool:  # noqa: ARG002
        """Persist entry to database (injectable in tests).

        Args:
            entry: Audit entry dict.

        Returns:
            ``True`` always (real implementation would return write result).
        """
        return True

    # ── Query ────────────────────────────────────────────────────────

    def query_all(self) -> List[Dict[str, Any]]:
        """Return all audit entries across all projects.

        Returns:
            List of audit entry dicts.
        """
        return self._query_db()

    def query_project(self, project: str) -> List[Dict[str, Any]]:
        """Return entries scoped to a single project.

        Args:
            project: Project name to filter by.

        Returns:
            Filtered list of audit entries.
        """
        all_entries = self._query_db()
        return [e for e in all_entries if e.get("project") == project]

    def search_ac_id(self, ac_pattern: str) -> List[Dict[str, Any]]:
        """Search for AC-ID references, supporting ``*`` wildcards.

        Args:
            ac_pattern: AC-ID pattern (e.g. ``"AC-FIN-*"``).

        Returns:
            Matching entries.
        """
        return self._search_ac_id(ac_pattern)

    def _query_db(self) -> List[Dict[str, Any]]:
        """Fetch all entries from the database (injectable in tests).

        Returns:
            All stored entries.
        """
        return list(self._log)

    def _search_ac_id(self, pattern: str) -> List[Dict[str, Any]]:
        """Search entries by AC-ID pattern (injectable in tests).

        Args:
            pattern: Pattern with optional ``*`` wildcard.

        Returns:
            Matching entries.
        """
        import fnmatch

        all_entries = self._query_db()
        return [e for e in all_entries if fnmatch.fnmatch(e.get("ac_id", ""), pattern)]
