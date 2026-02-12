"""Audit Log Manager - TTL-based Archival and Hot/Cold Storage.

Author: CORTEX Framework
Implements: AC-DB-E02 (Archival and Performance)
"""

import time as time_module
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


@dataclass
class AuditEntry:
    """Audit entry for tracking operations."""

    entry_id: str
    operation_type: str
    domain: str
    user: str
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ArchivalStats:
    """Archival statistics.

    Attributes:
        archived_count: Total entries in archive.
        total_size_bytes: Total size in bytes.
        entries_archived: Entries moved this operation.
        cutoff_date: TTL cutoff date used.
        archival_duration_ms: Time taken in milliseconds.
    """
    archived_count: int = 0
    total_size_bytes: int = 0
    entries_archived: int = 0
    cutoff_date: Optional[datetime] = None
    archival_duration_ms: float = 0.0


class AuditLogManager:
    """Manage audit logs with TTL-based hot/cold storage.

    Provides:
    - TTL-based archival (default 90 days)
    - Hot/archive query separation
    - Performance monitoring

    Attributes:
        ttl_days: Time-to-live in days for hot entries.
    """

    def __init__(self, ttl_days: int = 90) -> None:
        """Initialize manager.

        Args:
            ttl_days: Time-to-live in days for hot entries.
        """
        self.ttl_days = ttl_days
        self.hot_entries: List[AuditEntry] = []
        self.archive_entries: List[AuditEntry] = []
        self._archival_history: List[Dict[str, Any]] = []

    def add_entry(
        self,
        entry_id: str,
        operation_type: str,
        domain: str,
        user: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Add audit entry.

        Args:
            entry_id: Unique entry identifier.
            operation_type: Type of operation.
            domain: Domain name.
            user: User identifier.
            message: Entry message.
            metadata: Optional metadata dictionary.
        """
        entry = AuditEntry(
            entry_id=entry_id,
            operation_type=str(operation_type),
            domain=domain,
            user=user,
            message=message,
            metadata=metadata or {},
        )
        self.hot_entries.append(entry)

    def cleanup_old_entries(self) -> ArchivalStats:
        """Move entries older than TTL to archive.

        Returns:
            Statistics about archival operation.
        """
        start_time = time_module.time()
        cutoff_date = datetime.utcnow() - timedelta(days=self.ttl_days)
        archived = []
        remaining = []

        for entry in self.hot_entries:
            if entry.timestamp < cutoff_date:
                archived.append(entry)
            else:
                remaining.append(entry)

        self.archive_entries.extend(archived)
        self.hot_entries = remaining

        elapsed_ms = (time_module.time() - start_time) * 1000

        stats = ArchivalStats(
            entries_archived=len(archived),
            archived_count=len(self.archive_entries),
            cutoff_date=cutoff_date,
            archival_duration_ms=elapsed_ms,
        )

        # Track history
        self._archival_history.append({
            "entries_archived": len(archived),
            "archived_count": len(self.archive_entries),
            "cutoff_date": cutoff_date.isoformat(),
            "archival_duration_ms": elapsed_ms,
            "timestamp": datetime.utcnow().isoformat()
        })

        return stats

    def get_hot_count(self) -> int:
        """Get count of hot entries.

        Returns:
            Number of hot entries.
        """
        return len(self.hot_entries)

    def get_archive_count(self) -> int:
        """Get count of archived entries.

        Returns:
            Number of archived entries.
        """
        return len(self.archive_entries)

    def get_total_count(self) -> int:
        """Get total entry count.

        Returns:
            Total entries (hot + archived).
        """
        return len(self.hot_entries) + len(self.archive_entries)

    def query_hot_entries(self, domain: str) -> List[AuditEntry]:
        """Query hot entries by domain.

        Args:
            domain: Domain to filter.

        Returns:
            List of hot entries for domain.
        """
        return [e for e in self.hot_entries if e.domain == domain]

    def query_archive_entries(self, domain: str) -> List[AuditEntry]:
        """Query archive entries by domain.

        Args:
            domain: Domain to filter.

        Returns:
            List of archived entries for domain.
        """
        return [e for e in self.archive_entries if e.domain == domain]

    def query_all_entries(self, domain: str) -> List[AuditEntry]:
        """Query all entries (hot + archive) by domain.

        Args:
            domain: Domain to filter.

        Returns:
            List of all entries for domain.
        """
        hot = self.query_hot_entries(domain)
        archive = self.query_archive_entries(domain)
        return hot + archive

    def simulate_daily_updates(self, days: int, updates_per_day: int) -> None:
        """Simulate daily updates for testing.

        Args:
            days: Number of days to simulate.
            updates_per_day: Updates per day.
        """
        for day in range(days):
            date = datetime.utcnow() - timedelta(days=day)
            for update in range(updates_per_day):
                entry = AuditEntry(
                    entry_id=f"sim_{day}_{update}",
                    operation_type="AC_EXECUTE",
                    domain=f"domain_{day % 10}",
                    user="simulator",
                    message="Simulated update",
                    timestamp=date,
                )
                self.hot_entries.append(entry)

    def archive(self, log_id: str) -> ArchivalStats:
        """Archive logs.

        Args:
            log_id: Log identifier.

        Returns:
            Archival statistics.
        """
        return self.cleanup_old_entries()

    def get_stats(self) -> ArchivalStats:
        """Get archival stats.

        Returns:
            Current archival statistics.
        """
        return ArchivalStats(
            archived_count=len(self.archive_entries),
            entries_archived=len(self.archive_entries),
        )

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status.

        Returns:
            Dictionary with status information.
        """
        total = self.get_total_count()
        hot_pct = (len(self.hot_entries) / total * 100) if total > 0 else 0.0

        return {
            "hot_entries": len(self.hot_entries),
            "archived_entries": len(self.archive_entries),
            "total_entries": total,
            "hot_percentage": hot_pct,
            "ttl_days": self.ttl_days
        }

    def get_archival_history(self) -> List[Dict[str, Any]]:
        """Get archival operation history.

        Returns:
            List of archival operation records.
        """
        return self._archival_history.copy()

    def get_hot_ratio(self) -> float:
        """Get hot-to-total ratio as percentage.

        Returns:
            Percentage of entries that are hot.
        """
        total = self.get_total_count()
        if total == 0:
            return 100.0
        return (len(self.hot_entries) / total) * 100


__all__ = ["AuditEntry", "ArchivalStats", "AuditLogManager"]
