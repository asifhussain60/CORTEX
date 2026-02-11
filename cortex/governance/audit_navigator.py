"""Audit Navigator for querying audit trails."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class AuditEntry:
    """Audit entry for the navigator (distinct from EnhancedAuditLogger's AuditEntry)."""
    timestamp: str
    entity_type: str
    entity_id: str
    action: str
    actor: str


class AuditNavigator:
    """Navigates and queries audit trail."""

    def __init__(self) -> None:
        """Initialize navigator."""
        self.audit_log: List[AuditEntry] = []

    def log_entry(
        self,
        entity_type: str,
        entity_id: str,
        action: str,
        actor: str
    ) -> None:
        """Log an audit entry.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier
            action: Action performed
            actor: Actor performing action
        """
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            actor=actor
        )
        self.audit_log.append(entry)

    def query_by_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> List[AuditEntry]:
        """Query audit trail by entity.

        Args:
            entity_type: Type of entity
            entity_id: Entity identifier

        Returns:
            List of matching audit entries
        """
        return [
            entry for entry in self.audit_log
            if entry.entity_type == entity_type and entry.entity_id == entity_id
        ]

    def query_by_time_range(
        self,
        start_time: datetime,
        end_time: datetime
    ) -> List[AuditEntry]:
        """Query audit trail by time range.

        Args:
            start_time: Start of time range
            end_time: End of time range

        Returns:
            List of matching audit entries
        """
        results = []
        for entry in self.audit_log:
            entry_time = datetime.fromisoformat(entry.timestamp)
            if start_time <= entry_time <= end_time:
                results.append(entry)
        return results

    def query_by_action(self, action: str) -> List[AuditEntry]:
        """Query audit trail by action.

        Args:
            action: Action to search for

        Returns:
            List of matching audit entries
        """
        return [
            entry for entry in self.audit_log
            if entry.action == action
        ]

    def get_recent_entries(self, limit: int = 50) -> List[AuditEntry]:
        """Get recent audit entries.

        Args:
            limit: Maximum entries to return

        Returns:
            List of recent entries
        """
        return self.audit_log[-limit:]
