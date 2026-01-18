"""Concurrent Write Handling: Optimistic Locking (AC-DB-E05).

Prevents data loss from concurrent writes using optimistic locking with
version tracking. Detects conflicts and allows applications to retry with
latest version.

Strategy:
1. Version track: Each domain has monotonically increasing version number
2. On write: verify version hasn't changed since read
3. If changed: raise ConflictError (application retries)
4. If match: increment version, apply write atomically
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class VersionedDomain:
    """Domain with version tracking."""

    domain_id: str
    version: int = 1
    content: Dict[str, Any] = field(default_factory=dict)
    last_modified: datetime = field(default_factory=datetime.utcnow)
    modified_by: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain_id": self.domain_id,
            "version": self.version,
            "content": self.content,
            "last_modified": self.last_modified.isoformat(),
            "modified_by": self.modified_by,
        }


@dataclass
class WriteConflict:
    """Record of a write conflict."""

    domain_id: str
    expected_version: int
    actual_version: int
    detected_at: datetime = field(default_factory=datetime.utcnow)
    conflict_id: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "domain_id": self.domain_id,
            "expected_version": self.expected_version,
            "actual_version": self.actual_version,
            "detected_at": self.detected_at.isoformat(),
            "conflict_id": self.conflict_id,
        }


class ConflictError(Exception):
    """Raised when write conflict is detected."""

    def __init__(self, domain_id: str, expected: int, actual: int) -> None:
        """Initialize conflict error."""
        self.domain_id = domain_id
        self.expected_version = expected
        self.actual_version = actual
        super().__init__(
            f"Version conflict on {domain_id}: expected {expected}, found {actual}"
        )


class OptimisticLockManager:
    """Manages optimistic locking for concurrent writes.

    Uses version-based conflict detection:
    - Each domain has a version number (starts at 1)
    - On read: return current version
    - On write: check version matches, increment on success
    - If version mismatch: raise ConflictError
    """

    def __init__(self) -> None:
        """Initialize lock manager."""
        self.domains: Dict[str, VersionedDomain] = {}
        self.conflict_log: List[WriteConflict] = []
        self.write_attempts = 0
        self.write_conflicts = 0

    def create_domain(
        self, domain_id: str, content: Dict[str, Any] = None
    ) -> VersionedDomain:
        """Create new versioned domain.

        Args:
            domain_id: Domain ID
            content: Initial content

        Returns:
            VersionedDomain at version 1
        """
        domain = VersionedDomain(
            domain_id=domain_id,
            version=1,
            content=content or {},
            modified_by="system",
        )
        self.domains[domain_id] = domain
        return domain

    def read_domain(self, domain_id: str) -> Optional[VersionedDomain]:
        """Read domain (returns current version).

        Args:
            domain_id: Domain ID

        Returns:
            VersionedDomain or None if not found
        """
        return self.domains.get(domain_id)

    def write_domain(
        self,
        domain_id: str,
        new_content: Dict[str, Any],
        expected_version: int,
        modified_by: str = "system",
    ) -> VersionedDomain:
        """Write domain with optimistic locking.

        Args:
            domain_id: Domain ID
            new_content: New content
            expected_version: Version at time of read
            modified_by: User performing write

        Returns:
            Updated VersionedDomain

        Raises:
            ConflictError if version mismatch
        """
        self.write_attempts += 1

        if domain_id not in self.domains:
            # Create if doesn't exist
            if expected_version != 0:
                # Can't write with non-zero version if domain doesn't exist
                raise ConflictError(domain_id, expected_version, 0)
            return self.create_domain(domain_id, new_content)

        domain = self.domains[domain_id]

        # Check version match
        if domain.version != expected_version:
            self.write_conflicts += 1
            conflict = WriteConflict(
                domain_id=domain_id,
                expected_version=expected_version,
                actual_version=domain.version,
                conflict_id=f"wc_{len(self.conflict_log)}",
            )
            self.conflict_log.append(conflict)
            raise ConflictError(domain_id, expected_version, domain.version)

        # Version matches - apply write atomically
        domain.version += 1
        domain.content = new_content
        domain.last_modified = datetime.utcnow()
        domain.modified_by = modified_by

        return domain

    def get_conflict_log(self) -> List[Dict[str, Any]]:
        """Get conflict log.

        Returns:
            List of write conflicts
        """
        return [conflict.to_dict() for conflict in self.conflict_log]

    def get_conflict_rate(self) -> float:
        """Get write conflict rate.

        Returns:
            Percentage of writes that encountered conflicts
        """
        if self.write_attempts == 0:
            return 0.0
        return (self.write_conflicts / self.write_attempts) * 100

    def get_status(self) -> Dict[str, Any]:
        """Get lock manager status.

        Returns:
            Status dictionary
        """
        return {
            "total_domains": len(self.domains),
            "write_attempts": self.write_attempts,
            "write_conflicts": self.write_conflicts,
            "conflict_rate_percent": self.get_conflict_rate(),
        }

    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        self.domains.clear()
        self.conflict_log.clear()
        self.write_attempts = 0
        self.write_conflicts = 0
