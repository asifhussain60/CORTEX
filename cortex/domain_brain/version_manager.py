"""Version Manager - Import Versioning and Safe Deletion.

Author: CORTEX Framework
Implements: AC-DB-E06 (Version Tracking & Safe Deletion)
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set


class DeletionStatus(Enum):
    """Version deletion status."""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REVERTED = "reverted"
    DELETED = "deleted"
    ARCHIVED = "archived"
    FAILED = "failed"


@dataclass
class ImportVersion:
    """Represents a single domain import version.

    Attributes:
        import_id: Unique import identifier.
        domain_id: The domain this import belongs to.
        entity_ids: Set of entity IDs in this import.
        import_size: Number of entities.
        previous_import_id: ID of previous import (if any).
        created_at: Timestamp of import.
    """
    import_id: str
    domain_id: str
    entity_ids: Set[str]
    import_size: int
    previous_import_id: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()


@dataclass
class DeletionRequest:
    """Represents a deletion request for safe deletion workflow.

    Attributes:
        request_id: Unique request identifier.
        domain_id: The domain to delete from.
        entities_to_delete: Set of entity IDs to delete.
        reason: Reason for deletion.
        status: Current status of the request.
        confirmed_by: Who confirmed the deletion.
        created_at: When request was created.
    """
    request_id: str
    domain_id: str
    entities_to_delete: Set[str]
    reason: Optional[str] = None
    status: DeletionStatus = DeletionStatus.PENDING
    confirmed_by: Optional[str] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        """Initialize timestamp if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()


class VersionedDomainManager:
    """Manage versioned domain imports and safe deletion workflows.

    Provides:
    - Import versioning with history tracking
    - Subset detection for re-uploads
    - Safe deletion with confirmation workflow

    Attributes:
        current_version: Manager version string.
    """

    def __init__(self, current_version: str = "1.0.0") -> None:
        """Initialize the versioned domain manager.

        Args:
            current_version: Version string for the manager.
        """
        self.current_version = current_version
        self._imports: Dict[str, ImportVersion] = {}
        self._domain_imports: Dict[str, List[str]] = {}  # domain_id -> [import_ids]
        self.deletion_requests: Dict[str, DeletionRequest] = {}

    def import_domain(
        self,
        import_id: str,
        domain_id: str,
        entity_ids: Set[str]
    ) -> ImportVersion:
        """Import a domain with entity tracking.

        Args:
            import_id: Unique identifier for this import.
            domain_id: The domain being imported.
            entity_ids: Set of entity IDs in this import.

        Returns:
            The created ImportVersion.
        """
        # Get previous import ID for this domain
        previous_import_id: Optional[str] = None
        if domain_id in self._domain_imports and self._domain_imports[domain_id]:
            previous_import_id = self._domain_imports[domain_id][-1]

        # Create import version
        version = ImportVersion(
            import_id=import_id,
            domain_id=domain_id,
            entity_ids=entity_ids.copy(),
            import_size=len(entity_ids),
            previous_import_id=previous_import_id,
            created_at=datetime.utcnow()
        )

        # Store import
        self._imports[import_id] = version

        # Track domain imports
        if domain_id not in self._domain_imports:
            self._domain_imports[domain_id] = []
        self._domain_imports[domain_id].append(import_id)

        return version

    def get_version_history(self, domain_id: str) -> List[Dict[str, Any]]:
        """Get version history for a domain.

        Args:
            domain_id: The domain to get history for.

        Returns:
            List of version history entries.
        """
        if domain_id not in self._domain_imports:
            return []

        history = []
        for import_id in self._domain_imports[domain_id]:
            version = self._imports[import_id]
            history.append({
                "import_id": version.import_id,
                "domain_id": version.domain_id,
                "entity_count": version.import_size,
                "previous_import_id": version.previous_import_id,
                "created_at": version.created_at.isoformat() if version.created_at else None
            })

        return history

    def detect_subset_import(
        self,
        domain_id: str,
        new_entities: Set[str]
    ) -> bool:
        """Detect if new import is a subset of previous import.

        Args:
            domain_id: The domain to check.
            new_entities: The entities in the new import.

        Returns:
            True if new_entities is a strict subset of previous import.
        """
        if domain_id not in self._domain_imports or not self._domain_imports[domain_id]:
            return False

        # Get latest import
        latest_import_id = self._domain_imports[domain_id][-1]
        latest_version = self._imports[latest_import_id]

        # Check if new entities is a strict subset
        return new_entities < latest_version.entity_ids

    def request_deletion(
        self,
        request_id: str,
        domain_id: str,
        entities_to_delete: Set[str],
        reason: Optional[str] = None
    ) -> DeletionRequest:
        """Request deletion of entities (starts confirmation workflow).

        Args:
            request_id: Unique request identifier.
            domain_id: The domain to delete from.
            entities_to_delete: Set of entity IDs to delete.
            reason: Optional reason for deletion.

        Returns:
            The created DeletionRequest in PENDING status.
        """
        request = DeletionRequest(
            request_id=request_id,
            domain_id=domain_id,
            entities_to_delete=entities_to_delete.copy(),
            reason=reason,
            status=DeletionStatus.PENDING,
            created_at=datetime.utcnow()
        )
        self.deletion_requests[request_id] = request
        return request

    def confirm_deletion(
        self,
        request_id: str,
        confirmed_by: Optional[str] = None
    ) -> bool:
        """Confirm a pending deletion request.

        Args:
            request_id: The request to confirm.
            confirmed_by: Who is confirming the deletion.

        Returns:
            True if confirmation succeeded, False otherwise.
        """
        if request_id not in self.deletion_requests:
            return False

        request = self.deletion_requests[request_id]
        request.status = DeletionStatus.CONFIRMED
        request.confirmed_by = confirmed_by
        return True

    def revert_deletion(self, request_id: str) -> bool:
        """Revert a deletion request.

        Args:
            request_id: The request to revert.

        Returns:
            True if revert succeeded, False otherwise.
        """
        if request_id not in self.deletion_requests:
            return False

        request = self.deletion_requests[request_id]
        request.status = DeletionStatus.REVERTED
        return True

    def get_pending_deletions(self) -> List[Dict[str, Any]]:
        """Get all pending deletion requests.

        Returns:
            List of pending deletion requests.
        """
        pending = []
        for request_id, request in self.deletion_requests.items():
            if request.status == DeletionStatus.PENDING:
                pending.append({
                    "request_id": request.request_id,
                    "domain_id": request.domain_id,
                    "entities_count": len(request.entities_to_delete),
                    "reason": request.reason,
                    "created_at": request.created_at.isoformat() if request.created_at else None
                })
        return pending

    def get_status(self) -> Dict[str, Any]:
        """Get manager status.

        Returns:
            Dictionary with status information.
        """
        pending_count = sum(
            1 for r in self.deletion_requests.values()
            if r.status == DeletionStatus.PENDING
        )

        return {
            "domains_tracked": len(self._domain_imports),
            "total_imports": len(self._imports),
            "pending_deletions": pending_count,
            "version": self.current_version
        }


class VersionHistory:
    """Version history tracker."""

    def __init__(self) -> None:
        """Initialize version history."""
        self._history: Dict[str, List[str]] = {}

    def get_history(self, domain_id: str) -> List[str]:
        """Get version history.

        Args:
            domain_id: The domain to get history for.

        Returns:
            List of version strings.
        """
        return self._history.get(domain_id, [])


__all__ = [
    "VersionedDomainManager",
    "VersionHistory",
    "DeletionStatus",
    "ImportVersion",
    "DeletionRequest"
]
