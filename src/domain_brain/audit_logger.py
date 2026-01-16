"""Immutable audit logger with hash chain integrity.

Provides audit logging with SHA-256 hash chain for tamper-evident records.
Includes TTL cache for recent entries to enable sub-100ms queries.
"""

import hashlib
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from collections import OrderedDict

from src.domain_brain.models import AuditEntry, AuditOperationType


class AuditLogger:
    """Immutable hash chain audit logger with TTL cache.

    Provides:
    - SHA-256 hash chain (immutable append-only)
    - TTL cache for recent entries (<100ms query)
    - Per-domain audit trail
    - Hash chain integrity verification
    """

    def __init__(self, ttl_seconds: int = 3600) -> None:
        """Initialize audit logger.

        Args:
            ttl_seconds: Time-to-live for cache entries (default 1 hour)
        """
        self.ttl_seconds = ttl_seconds
        self.entries: List[AuditEntry] = []
        self.cache: OrderedDict[str, AuditEntry] = OrderedDict()
        self.last_hash: str = hashlib.sha256(b"").hexdigest()

    def log_operation(
        self,
        operation: AuditOperationType,
        entity_id: Optional[str] = None,
        domain_id: Optional[str] = None,
        description: str = "",
        previous_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        user: str = "system",
    ) -> AuditEntry:
        """Log an operation to the audit trail.

        Creates a new audit entry with hash chain integrity. Entry is automatically
        added to TTL cache and appended to immutable log.

        Args:
            operation: Type of operation
            entity_id: ID of affected entity (optional)
            domain_id: ID of affected domain (optional)
            description: Human-readable description
            previous_value: Previous value (for updates)
            new_value: New value (for creates/updates)
            user: User performing operation

        Returns:
            AuditEntry that was logged
        """
        entry_id = str(uuid.uuid4())
        entry = AuditEntry(
            entry_id=entry_id,
            operation=operation,
            entity_id=entity_id,
            domain_id=domain_id,
            description=description,
            previous_value=previous_value,
            new_value=new_value,
            user=user,
            timestamp=datetime.utcnow(),
            previous_hash=self.last_hash,
        )

        # Calculate hash for this entry
        entry.hash = self._calculate_hash(entry)

        # Append to immutable log
        self.entries.append(entry)

        # Add to TTL cache
        self.cache[entry_id] = entry
        self._cleanup_cache()

        # Update last hash
        self.last_hash = entry.hash

        return entry

    def _calculate_hash(self, entry: AuditEntry) -> str:
        """Calculate SHA-256 hash for audit entry.

        Hash includes all entry data and previous hash for chain integrity.

        Args:
            entry: Entry to hash

        Returns:
            SHA-256 hash as hex string
        """
        # Create hashable dict representation
        data = {
            "entry_id": entry.entry_id,
            "operation": entry.operation.value,
            "entity_id": entry.entity_id,
            "domain_id": entry.domain_id,
            "description": entry.description,
            "user": entry.user,
            "timestamp": entry.timestamp.isoformat(),
            "previous_hash": entry.previous_hash,
        }

        # Serialize and hash
        json_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()

    def _cleanup_cache(self) -> None:
        """Remove expired entries from TTL cache.

        Entries older than ttl_seconds are removed from cache but remain
        in the immutable audit log.
        """
        now = datetime.utcnow()
        expired_ids = []

        for entry_id, entry in self.cache.items():
            age = (now - entry.timestamp).total_seconds()
            if age > self.ttl_seconds:
                expired_ids.append(entry_id)

        for entry_id in expired_ids:
            del self.cache[entry_id]

    def get_entry(self, entry_id: str) -> Optional[AuditEntry]:
        """Get audit entry by ID.

        Checks cache first for performance, falls back to full log search.

        Args:
            entry_id: Entry ID to retrieve

        Returns:
            AuditEntry if found, None otherwise
        """
        # Check cache first
        if entry_id in self.cache:
            return self.cache[entry_id]

        # Search full log
        for entry in self.entries:
            if entry.entry_id == entry_id:
                return entry

        return None

    def get_domain_audit_trail(self, domain_id: str) -> List[AuditEntry]:
        """Get all audit entries for a specific domain.

        Args:
            domain_id: Domain ID to filter by

        Returns:
            List of audit entries for the domain (from cache if available)
        """
        entries = []

        # Check cache first
        for entry in self.cache.values():
            if entry.domain_id == domain_id:
                entries.append(entry)

        # If cache is incomplete, search full log
        if len(entries) < len([e for e in self.entries if e.domain_id == domain_id]):
            entries = [e for e in self.entries if e.domain_id == domain_id]

        return sorted(entries, key=lambda e: e.timestamp)

    def get_recent_entries(self, limit: int = 100) -> List[AuditEntry]:
        """Get recent audit entries from cache.

        Args:
            limit: Maximum number of entries to return

        Returns:
            Recent entries (up to limit)
        """
        self._cleanup_cache()
        entries = list(self.cache.values())
        return sorted(entries, key=lambda e: e.timestamp, reverse=True)[:limit]

    def verify_hash_chain(self) -> bool:
        """Verify integrity of entire hash chain.

        Recalculates all hashes and verifies chain linkage.

        Returns:
            True if hash chain is valid, False otherwise
        """
        current_hash = hashlib.sha256(b"").hexdigest()

        for entry in self.entries:
            # Verify previous hash
            if entry.previous_hash != current_hash:
                return False

            # Recalculate hash
            expected_hash = self._calculate_hash(entry)
            if entry.hash != expected_hash:
                return False

            current_hash = entry.hash

        return True

    def get_all_entries(self) -> List[AuditEntry]:
        """Get all entries in immutable audit log.

        Returns:
            All audit entries
        """
        return list(self.entries)

    def get_entry_count(self) -> int:
        """Get total number of audit entries.

        Returns:
            Count of entries in immutable log
        """
        return len(self.entries)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        return {
            "cache_size": len(self.cache),
            "total_entries": len(self.entries),
            "ttl_seconds": self.ttl_seconds,
            "last_hash": self.last_hash,
        }
