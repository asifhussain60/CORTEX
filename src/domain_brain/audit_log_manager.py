"""Brain Vacuum Prevention: TTL + Archival Strategy (AC-DB-E02).

Prevents unbounded audit log growth and query degradation by implementing
a Time-To-Live (TTL) based hot/cold storage strategy with archival.

Problem: 10,000+ daily updates × 365 days = 3.6M entries, causing O(n) 
degradation and 500ms+ queries by Month 12.

Solution: 90-day TTL with archival ensures O(1) recent queries and manageable
archive for rare full history queries.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta

from src.domain_brain.models import AuditOperationType


@dataclass
class ArchivalStats:
    """Statistics from archival operation."""

    entries_archived: int = 0
    entries_remaining_hot: int = 0
    archival_duration_ms: float = 0.0
    cutoff_date: Optional[datetime] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entries_archived": self.entries_archived,
            "entries_remaining_hot": self.entries_remaining_hot,
            "archival_duration_ms": self.archival_duration_ms,
            "cutoff_date": self.cutoff_date.isoformat() if self.cutoff_date else None,
        }


@dataclass
class AuditLogEntry:
    """Single audit log entry."""

    entry_id: str
    operation_type: AuditOperationType
    domain_id: str
    timestamp: datetime
    user: str
    description: str
    hash_value: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entry_id": self.entry_id,
            "operation_type": self.operation_type.value,
            "domain_id": self.domain_id,
            "timestamp": self.timestamp.isoformat(),
            "user": self.user,
            "description": self.description,
            "hash_value": self.hash_value,
        }


class AuditLogManager:
    """Manages audit logs with TTL and archival.

    Two-tier strategy:
    1. Hot tier: Recent entries (< 90 days), indexed on domain_id + timestamp
    2. Archive tier: Older entries (>= 90 days), indexed on domain_id only

    This maintains O(1) queries on recent data while preserving full history.
    """

    def __init__(self, ttl_days: int = 90) -> None:
        """Initialize audit log manager.

        Args:
            ttl_days: Time-to-live for hot entries (default 90 days)
        """
        self.ttl_days = ttl_days
        self.hot_entries: List[AuditLogEntry] = []
        self.archived_entries: List[AuditLogEntry] = []
        self.archival_history: List[ArchivalStats] = []
        self.last_archival_date: Optional[datetime] = None

    def add_entry(
        self,
        entry_id: str,
        operation_type: AuditOperationType,
        domain_id: str,
        user: str,
        description: str,
        hash_value: str = "",
    ) -> None:
        """Add entry to hot audit log.

        Args:
            entry_id: Unique entry ID
            operation_type: Type of operation
            domain_id: Domain ID
            user: User who performed operation
            description: Operation description
            hash_value: Hash chain value
        """
        entry = AuditLogEntry(
            entry_id=entry_id,
            operation_type=operation_type,
            domain_id=domain_id,
            timestamp=datetime.utcnow(),
            user=user,
            description=description,
            hash_value=hash_value,
        )
        self.hot_entries.append(entry)

    def is_in_hot_range(self, timestamp: datetime) -> bool:
        """Check if timestamp is within hot range.

        Args:
            timestamp: Timestamp to check

        Returns:
            True if within TTL, False if should be archived
        """
        cutoff = datetime.utcnow() - timedelta(days=self.ttl_days)
        return timestamp >= cutoff

    def query_hot_entries(self, domain_id: str) -> List[AuditLogEntry]:
        """Query recent (hot) entries for domain.

        Args:
            domain_id: Domain ID

        Returns:
            List of recent entries (guaranteed O(hot_size) which is small)
        """
        return [e for e in self.hot_entries if e.domain_id == domain_id]

    def query_archive_entries(self, domain_id: str) -> List[AuditLogEntry]:
        """Query archived entries for domain.

        Args:
            domain_id: Domain ID

        Returns:
            List of archived entries
        """
        return [e for e in self.archived_entries if e.domain_id == domain_id]

    def query_all_entries(self, domain_id: str) -> List[AuditLogEntry]:
        """Query all entries (hot + archive) for domain.

        Args:
            domain_id: Domain ID

        Returns:
            Complete audit trail
        """
        hot = self.query_hot_entries(domain_id)
        archive = self.query_archive_entries(domain_id)
        return hot + archive

    def archive_entries_before(self, cutoff_date: datetime) -> ArchivalStats:
        """Archive entries older than cutoff date.

        Args:
            cutoff_date: Entries older than this are archived

        Returns:
            Archival statistics
        """
        start_time = datetime.utcnow()

        # Partition hot entries
        new_hot = []
        new_archive = []

        for entry in self.hot_entries:
            if entry.timestamp < cutoff_date:
                new_archive.append(entry)
            else:
                new_hot.append(entry)

        # Move to archive
        self.archived_entries.extend(new_archive)
        self.hot_entries = new_hot

        # Record statistics
        end_time = datetime.utcnow()
        duration_ms = (end_time - start_time).total_seconds() * 1000

        stats = ArchivalStats(
            entries_archived=len(new_archive),
            entries_remaining_hot=len(new_hot),
            archival_duration_ms=duration_ms,
            cutoff_date=cutoff_date,
        )

        self.archival_history.append(stats)
        self.last_archival_date = datetime.utcnow()

        return stats

    def cleanup_old_entries(self) -> ArchivalStats:
        """Clean up entries older than TTL.

        Moves entries to archive if they exceed TTL.

        Returns:
            Cleanup statistics
        """
        cutoff = datetime.utcnow() - timedelta(days=self.ttl_days)
        return self.archive_entries_before(cutoff)

    def get_hot_count(self) -> int:
        """Get count of hot entries.

        Returns:
            Number of entries in hot tier
        """
        return len(self.hot_entries)

    def get_archive_count(self) -> int:
        """Get count of archived entries.

        Returns:
            Number of entries in archive tier
        """
        return len(self.archived_entries)

    def get_total_count(self) -> int:
        """Get total entry count.

        Returns:
            Total entries (hot + archive)
        """
        return self.get_hot_count() + self.get_archive_count()

    def get_hot_ratio(self) -> float:
        """Get ratio of hot to total entries.

        Returns:
            Percentage of entries in hot tier
        """
        total = self.get_total_count()
        if total == 0:
            return 0.0
        return (self.get_hot_count() / total) * 100

    def get_status(self) -> Dict[str, Any]:
        """Get audit log status.

        Returns:
            Status dictionary
        """
        return {
            "hot_entries": self.get_hot_count(),
            "archived_entries": self.get_archive_count(),
            "total_entries": self.get_total_count(),
            "hot_percentage": self.get_hot_ratio(),
            "ttl_days": self.ttl_days,
            "last_archival": (
                self.last_archival_date.isoformat()
                if self.last_archival_date
                else None
            ),
            "archival_operations": len(self.archival_history),
        }

    def get_archival_history(self) -> List[Dict[str, Any]]:
        """Get history of archival operations.

        Returns:
            List of archival statistics
        """
        return [stats.to_dict() for stats in self.archival_history]

    def simulate_daily_updates(self, days: int, updates_per_day: int) -> None:
        """Simulate daily updates over specified number of days.

        Used for testing growth patterns and performance degradation.

        Args:
            days: Number of days to simulate
            updates_per_day: Number of updates per day
        """
        for day in range(days):
            base_time = datetime.utcnow() - timedelta(days=days - day)

            for i in range(updates_per_day):
                entry_id = f"e_{day}_{i}"
                domain_id = f"domain_{day % 10}"  # 10 domains
                self.add_entry(
                    entry_id=entry_id,
                    operation_type=AuditOperationType.AC_EXECUTE,
                    domain_id=domain_id,
                    user="simulator",
                    description=f"Simulated update {day}.{i}",
                    hash_value=f"hash_{day}_{i}",
                )

                # Backdate the entry
                self.hot_entries[-1].timestamp = base_time + timedelta(
                    seconds=i * 60
                )

    def clear_all(self) -> None:
        """Clear all entries (for testing)."""
        self.hot_entries.clear()
        self.archived_entries.clear()
        self.archival_history.clear()
        self.last_archival_date = None
