"""
Audit Trail Enhancement Module (OB-003-01).

This module provides searchable audit history with retention policies,
export functionality, and comprehensive audit tracking for CORTEX operations.

Key Components:
- AuditEntry: Individual audit log entries
- AuditTrail: Searchable audit log storage
- RetentionPolicy: Data retention and archival
- AuditExporter: Multi-format export (JSON, CSV)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from enum import Enum
import json
import csv
import io
import gzip
from cortex.models.canonical_enums import AuditAction




class EnforcementMode(str, Enum):
    """Retention policy enforcement modes."""

    DELETE = "DELETE"
    ARCHIVE = "ARCHIVE"
    MOVE_TO_COLD = "MOVE_TO_COLD"


@dataclass
class AuditEntry:
    """
    Represents a single audit trail entry.

    Attributes:
        event_type: Type of event (alert, metric, span, etc)
        resource_name: Name of resource affected
        actor: Component or service that triggered event
        action: Action performed (START, EXECUTE, COMPLETE, etc)
        details: Event-specific details dictionary
        timestamp: When event occurred (auto-set)
        status: Operation status (optional)
        metadata: Additional metadata (optional)
        entry_id: Unique identifier (auto-generated)
    """

    event_type: str
    resource_name: str
    actor: str
    action: str
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    status: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    entry_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Generate entry ID if not provided."""
        if self.entry_id is None:
            timestamp_str = self.timestamp.isoformat()
            self.entry_id = f"{self.event_type}_{self.resource_name}_{timestamp_str}"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert entry to dictionary.

        Returns:
            Dictionary representation of audit entry
        """
        return {
            "entry_id": self.entry_id,
            "event_type": self.event_type,
            "resource_name": self.resource_name,
            "actor": self.actor,
            "action": self.action,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
            "details": self.details,
            "metadata": self.metadata,
        }


@dataclass
class RetentionPolicy:
    """
    Configuration for audit entry retention.

    Attributes:
        retention_days: How many days to retain entries
        max_entries: Maximum number of entries to keep
        enforcement_mode: DELETE, ARCHIVE, or MOVE_TO_COLD
        archive_location: Path for archived entries (optional)
    """

    retention_days: int
    max_entries: Optional[int] = None
    enforcement_mode: str = "DELETE"
    archive_location: Optional[str] = None

    def should_remove_entry(self, entry: AuditEntry) -> bool:
        """
        Determine if entry should be removed based on policy.

        Args:
            entry: Audit entry to check

        Returns:
            True if entry exceeds retention period
        """
        age = datetime.now() - entry.timestamp
        return age > timedelta(days=self.retention_days)


class AuditTrail:
    """
    Searchable audit log storage for CORTEX operations.

    Maintains complete audit history with search, filter, export,
    and retention capabilities.
    """

    def __init__(self) -> None:
        """Initialize the audit trail."""
        self._entries: List[AuditEntry] = []
        self._entry_index: Dict[str, AuditEntry] = {}
        self._retention_policy: Optional[RetentionPolicy] = None

    def record(self, entry: AuditEntry) -> str:
        """
        Record an audit entry.

        Args:
            entry: Audit entry to record

        Returns:
            Entry ID of recorded entry
        """
        if entry.entry_id is None:
            entry.entry_id = self._generate_entry_id(entry)

        self._entries.append(entry)
        self._entry_index[entry.entry_id] = entry

        return entry.entry_id

    def _generate_entry_id(self, entry: AuditEntry) -> str:
        """
        Generate unique entry ID.

        Args:
            entry: Audit entry

        Returns:
            Unique entry ID
        """
        timestamp_str = entry.timestamp.isoformat().replace(".", "_").replace(":", "-")
        return (
            f"{entry.event_type}_{entry.resource_name}_{timestamp_str}_{len(self._entries)}"
        )

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """
        Retrieve specific audit entry by ID.

        Args:
            entry_id: Entry ID to retrieve

        Returns:
            Audit entry or None if not found
        """
        return self._entry_index.get(entry_id)

    def search(
        self,
        event_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        actor: Optional[str] = None,
        action: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        status: Optional[str] = None,
    ) -> List[AuditEntry]:
        """
        Search audit trail with multiple filter criteria.

        All criteria are combined with AND logic.

        Args:
            event_type: Filter by event type
            resource_name: Filter by resource name
            actor: Filter by actor
            action: Filter by action
            start_time: Filter entries after this time
            end_time: Filter entries before this time
            status: Filter by status

        Returns:
            List of matching audit entries
        """
        results = self._entries

        if event_type:
            results = [e for e in results if e.event_type == event_type]

        if resource_name:
            results = [e for e in results if e.resource_name == resource_name]

        if actor:
            results = [e for e in results if e.actor == actor]

        if action:
            results = [e for e in results if e.action == action]

        if start_time:
            results = [e for e in results if e.timestamp >= start_time]

        if end_time:
            results = [e for e in results if e.timestamp <= end_time]

        if status:
            results = [e for e in results if e.status == status]

        return results

    def apply_retention_policy(self, policy: RetentionPolicy) -> int:
        """
        Apply retention policy to audit trail.

        Removes or archives entries according to policy.

        Args:
            policy: Retention policy to apply

        Returns:
            Number of entries affected
        """
        self._retention_policy = policy

        affected_count = 0
        entries_to_keep = []

        for entry in self._entries:
            if policy.should_remove_entry(entry):
                affected_count += 1
                del self._entry_index[entry.entry_id]
            else:
                entries_to_keep.append(entry)

        self._entries = entries_to_keep

        return affected_count

    def get_entry_count(self) -> int:
        """
        Get total number of audit entries.

        Returns:
            Total entry count
        """
        return len(self._entries)

    def get_event_type_distribution(self) -> Dict[str, int]:
        """
        Get distribution of event types in audit trail.

        Returns:
            Dictionary with event type counts
        """
        distribution: Dict[str, int] = {}

        for entry in self._entries:
            if entry.event_type not in distribution:
                distribution[entry.event_type] = 0
            distribution[entry.event_type] += 1

        return distribution

    def get_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive audit trail statistics.

        Returns:
            Dictionary with audit statistics
        """
        if not self._entries:
            return {
                "total_entries": 0,
                "earliest_entry": None,
                "latest_entry": None,
                "event_distribution": {},
            }

        timestamps = [e.timestamp for e in self._entries]

        return {
            "total_entries": len(self._entries),
            "earliest_entry": min(timestamps).isoformat(),
            "latest_entry": max(timestamps).isoformat(),
            "event_distribution": self.get_event_type_distribution(),
            "unique_actors": len(set(e.actor for e in self._entries)),
            "unique_resources": len(set(e.resource_name for e in self._entries)),
        }

    def clear(self) -> None:
        """Clear all audit entries."""
        self._entries.clear()
        self._entry_index.clear()


class AuditExporter:
    """
    Export audit trail in multiple formats.

    Supports JSON, CSV, and compressed formats with optional filtering.
    """

    def __init__(self, audit_trail: AuditTrail) -> None:
        """
        Initialize the exporter.

        Args:
            audit_trail: AuditTrail instance to export
        """
        self._trail = audit_trail

    def to_json(
        self,
        event_type: Optional[str] = None,
        resource_name: Optional[str] = None,
        actor: Optional[str] = None,
    ) -> str:
        """
        Export audit trail to JSON format.

        Args:
            event_type: Optional filter by event type
            resource_name: Optional filter by resource
            actor: Optional filter by actor

        Returns:
            JSON string representation
        """
        entries = self._trail.search(
            event_type=event_type, resource_name=resource_name, actor=actor
        )

        data = [entry.to_dict() for entry in entries]

        return json.dumps(data, indent=2)

    def to_csv(
        self,
        event_type: Optional[str] = None,
        resource_name: Optional[str] = None,
    ) -> str:
        """
        Export audit trail to CSV format.

        Args:
            event_type: Optional filter by event type
            resource_name: Optional filter by resource

        Returns:
            CSV string representation
        """
        entries = self._trail.search(
            event_type=event_type, resource_name=resource_name
        )

        output = io.StringIO()
        if not entries:
            return ""

        fieldnames = [
            "entry_id",
            "event_type",
            "resource_name",
            "actor",
            "action",
            "timestamp",
            "status",
        ]

        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()

        for entry in entries:
            row = {
                "entry_id": entry.entry_id,
                "event_type": entry.event_type,
                "resource_name": entry.resource_name,
                "actor": entry.actor,
                "action": entry.action,
                "timestamp": entry.timestamp.isoformat(),
                "status": entry.status or "",
            }
            writer.writerow(row)

        return output.getvalue()

    def to_json_compressed(
        self,
        event_type: Optional[str] = None,
    ) -> bytes:
        """
        Export audit trail to compressed JSON format.

        Args:
            event_type: Optional filter by event type

        Returns:
            Gzip-compressed JSON bytes
        """
        json_data = self.to_json(event_type=event_type)
        compressed = gzip.compress(json_data.encode("utf-8"))

        return compressed

    def to_dict(self) -> Dict[str, Any]:
        """
        Export audit trail as dictionary.

        Returns:
            Dictionary representation with metadata
        """
        entries = self._trail.search()

        return {
            "export_timestamp": datetime.now().isoformat(),
            "total_entries": len(entries),
            "entries": [entry.to_dict() for entry in entries],
            "stats": self._trail.get_stats(),
        }
