"""Optimistic Lock - Concurrent Write Handling for Domain Brain.

Author: CORTEX Framework
Implements: AC-DB-E05 (Optimistic Locking with Version Tracking)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional


class ConflictError(Exception):
    """Raised when optimistic lock conflict occurs.

    Attributes:
        domain_id: The domain where conflict occurred.
        expected_version: The version the client expected.
        actual_version: The actual current version.
    """

    def __init__(
        self,
        domain_id: str,
        expected_version: int,
        actual_version: int,
        message: Optional[str] = None
    ) -> None:
        """Initialize conflict error.

        Args:
            domain_id: The domain identifier.
            expected_version: Version client expected.
            actual_version: Current version in store.
            message: Optional error message.
        """
        self.domain_id = domain_id
        self.expected_version = expected_version
        self.actual_version = actual_version
        msg = message or (
            f"Version conflict for domain '{domain_id}': "
            f"expected {expected_version}, actual {actual_version}"
        )
        super().__init__(msg)


@dataclass
class VersionedDomain:
    """Versioned domain entity with optimistic locking support.

    Attributes:
        domain_id: Unique domain identifier.
        version: Current version number (starts at 1).
        content: Domain content/data.
        created_at: Creation timestamp.
        updated_at: Last update timestamp.
        modified_by: Last modifier identifier.
    """
    domain_id: str
    version: int
    content: Dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    modified_by: Optional[str] = None

    def __post_init__(self) -> None:
        """Initialize timestamps if not set."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = self.created_at


@dataclass
class LockToken:
    """Optimistic lock token for tracking versions.

    Attributes:
        token_id: Unique token identifier.
        version: Version at time of token creation.
        expires_at: Token expiration time.
    """
    token_id: str
    version: int
    expires_at: str = ""


class OptimisticLockManager:
    """Manage optimistic locks for concurrent domain writes.

    Implements version-based optimistic locking to detect and prevent
    concurrent write conflicts. All writes must specify expected version.

    Attributes:
        lock_timeout_ms: Lock timeout in milliseconds.
    """

    def __init__(self, lock_timeout_ms: int = 5000) -> None:
        """Initialize the optimistic lock manager.

        Args:
            lock_timeout_ms: Timeout for locks in milliseconds.
        """
        self.lock_timeout_ms = lock_timeout_ms
        self._domains: Dict[str, VersionedDomain] = {}
        self._write_attempts: int = 0
        self._write_conflicts: int = 0
        self._conflict_log: List[Dict[str, Any]] = []

    def create_domain(
        self,
        domain_id: str,
        content: Optional[Dict[str, Any]] = None
    ) -> VersionedDomain:
        """Create a new domain with version 1.

        Args:
            domain_id: Unique identifier for the domain.
            content: Initial content for the domain.

        Returns:
            The created VersionedDomain at version 1.
        """
        domain = VersionedDomain(
            domain_id=domain_id,
            version=1,
            content=content or {},
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        self._domains[domain_id] = domain
        return domain

    def read_domain(self, domain_id: str) -> VersionedDomain:
        """Read domain by ID.

        Args:
            domain_id: The domain to read.

        Returns:
            The domain with current version.

        Raises:
            KeyError: If domain does not exist.
        """
        if domain_id not in self._domains:
            raise KeyError(f"Domain '{domain_id}' not found")
        return self._domains[domain_id]

    def write_domain(
        self,
        domain_id: str,
        content: Dict[str, Any],
        expected_version: int,
        modified_by: Optional[str] = None
    ) -> VersionedDomain:
        """Write domain content with optimistic lock check.

        Args:
            domain_id: The domain to update.
            content: New content to write.
            expected_version: Expected current version (for conflict detection).
            modified_by: Identifier of modifier.

        Returns:
            Updated VersionedDomain with incremented version.

        Raises:
            ConflictError: If expected_version doesn't match current version.
        """
        self._write_attempts += 1

        # Handle new domain creation (expected_version=0)
        if domain_id not in self._domains:
            if expected_version != 0:
                self._write_conflicts += 1
                self._conflict_log.append({
                    "domain_id": domain_id,
                    "expected_version": expected_version,
                    "actual_version": 0,
                    "timestamp": datetime.utcnow().isoformat()
                })
                raise ConflictError(
                    domain_id=domain_id,
                    expected_version=expected_version,
                    actual_version=0
                )
            # Create new domain
            return self.create_domain(domain_id, content)

        current = self._domains[domain_id]

        # Check for version conflict
        if current.version != expected_version:
            self._write_conflicts += 1
            self._conflict_log.append({
                "domain_id": domain_id,
                "expected_version": expected_version,
                "actual_version": current.version,
                "timestamp": datetime.utcnow().isoformat()
            })
            raise ConflictError(
                domain_id=domain_id,
                expected_version=expected_version,
                actual_version=current.version
            )

        # Update domain with new version
        updated = VersionedDomain(
            domain_id=domain_id,
            version=current.version + 1,
            content=content,
            created_at=current.created_at,
            updated_at=datetime.utcnow(),
            modified_by=modified_by
        )
        self._domains[domain_id] = updated
        return updated

    def get_status(self) -> Dict[str, Any]:
        """Get manager status including conflict statistics.

        Returns:
            Dictionary with status information.
        """
        return {
            "total_domains": len(self._domains),
            "write_attempts": self._write_attempts,
            "write_conflicts": self._write_conflicts,
            "conflict_rate": (
                self._write_conflicts / self._write_attempts
                if self._write_attempts > 0 else 0.0
            )
        }

    def get_conflict_log(self) -> List[Dict[str, Any]]:
        """Get log of all conflicts.

        Returns:
            List of conflict entries.
        """
        return self._conflict_log.copy()


__all__ = [
    "OptimisticLockManager",
    "LockToken",
    "VersionedDomain",
    "ConflictError"
]
