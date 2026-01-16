"""Version Tracking & Safe Deletion (AC-DB-E06).

Prevents accidental data loss from subset re-uploads by tracking import
versions and requiring confirmation for deletions.

Strategy:
1. Track import version: Each domain import has unique version ID
2. On re-upload: compare with latest import
3. If subset: require confirmation before deletion
4. Delete only: marked entities, preserve history
"""

from typing import Dict, Any, Optional, List, Set
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class DeletionStatus(Enum):
    """Status of a deletion."""

    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    REVERTED = "REVERTED"


@dataclass
class ImportVersion:
    """Track of an import version."""

    import_id: str
    domain_id: str
    entity_ids: Set[str] = field(default_factory=set)
    import_time: datetime = field(default_factory=datetime.utcnow)
    import_size: int = 0
    previous_import_id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "import_id": self.import_id,
            "domain_id": self.domain_id,
            "entity_ids": list(self.entity_ids),
            "entity_count": len(self.entity_ids),
            "import_time": self.import_time.isoformat(),
            "import_size": self.import_size,
            "previous_import_id": self.previous_import_id,
        }


@dataclass
class DeletionRequest:
    """Request to delete entities."""

    request_id: str
    domain_id: str
    entities_to_delete: Set[str] = field(default_factory=set)
    reason: str = ""
    requested_at: datetime = field(default_factory=datetime.utcnow)
    status: DeletionStatus = DeletionStatus.PENDING
    confirmed_at: Optional[datetime] = None
    confirmed_by: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "request_id": self.request_id,
            "domain_id": self.domain_id,
            "entities_to_delete": list(self.entities_to_delete),
            "deletion_count": len(self.entities_to_delete),
            "reason": self.reason,
            "requested_at": self.requested_at.isoformat(),
            "status": self.status.value,
            "confirmed_at": self.confirmed_at.isoformat() if self.confirmed_at else None,
            "confirmed_by": self.confirmed_by,
        }


class VersionedDomainManager:
    """Manages domain versions and safe deletions.

    Prevents accidental data loss by tracking import versions and requiring
    confirmation for destructive operations.
    """

    def __init__(self) -> None:
        """Initialize manager."""
        self.current_versions: Dict[str, ImportVersion] = {}
        self.version_history: Dict[str, List[ImportVersion]] = {}
        self.deletion_requests: Dict[str, DeletionRequest] = {}
        self.deletion_history: List[DeletionRequest] = []

    def import_domain(
        self, import_id: str, domain_id: str, entity_ids: Set[str]
    ) -> ImportVersion:
        """Import a new version of domain.

        Args:
            import_id: Unique import ID
            domain_id: Domain ID
            entity_ids: Set of entity IDs in import

        Returns:
            ImportVersion
        """
        previous_import_id = None
        if domain_id in self.current_versions:
            previous_import_id = self.current_versions[domain_id].import_id

        version = ImportVersion(
            import_id=import_id,
            domain_id=domain_id,
            entity_ids=entity_ids,
            import_size=len(entity_ids),
            previous_import_id=previous_import_id,
        )

        # Store current version
        self.current_versions[domain_id] = version

        # Add to history
        if domain_id not in self.version_history:
            self.version_history[domain_id] = []
        self.version_history[domain_id].append(version)

        return version

    def get_current_version(self, domain_id: str) -> Optional[ImportVersion]:
        """Get current import version for domain.

        Args:
            domain_id: Domain ID

        Returns:
            Current ImportVersion or None
        """
        return self.current_versions.get(domain_id)

    def detect_subset_import(
        self, domain_id: str, new_entity_ids: Set[str]
    ) -> bool:
        """Detect if new import is a subset of current.

        Args:
            domain_id: Domain ID
            new_entity_ids: Entity IDs in new import

        Returns:
            True if subset (would require deletion), False otherwise
        """
        current = self.get_current_version(domain_id)

        if not current:
            return False

        # It's a subset if new entities < current entities AND new is subset of current
        return (
            len(new_entity_ids) < len(current.entity_ids)
            and new_entity_ids.issubset(current.entity_ids)
        )

    def request_deletion(
        self,
        request_id: str,
        domain_id: str,
        entities_to_delete: Set[str],
        reason: str = "Subset re-upload",
    ) -> DeletionRequest:
        """Request deletion of entities.

        Args:
            request_id: Unique request ID
            domain_id: Domain ID
            entities_to_delete: Entities to delete
            reason: Reason for deletion

        Returns:
            DeletionRequest
        """
        request = DeletionRequest(
            request_id=request_id,
            domain_id=domain_id,
            entities_to_delete=entities_to_delete,
            reason=reason,
        )

        self.deletion_requests[request_id] = request

        return request

    def confirm_deletion(
        self, request_id: str, confirmed_by: str = "admin"
    ) -> bool:
        """Confirm deletion request.

        Args:
            request_id: Request ID
            confirmed_by: User confirming deletion

        Returns:
            True if confirmed, False if request not found
        """
        if request_id not in self.deletion_requests:
            return False

        request = self.deletion_requests[request_id]
        request.status = DeletionStatus.CONFIRMED
        request.confirmed_at = datetime.utcnow()
        request.confirmed_by = confirmed_by

        return True

    def revert_deletion(self, request_id: str) -> bool:
        """Revert deletion request.

        Args:
            request_id: Request ID

        Returns:
            True if reverted, False if not found
        """
        if request_id not in self.deletion_requests:
            return False

        request = self.deletion_requests[request_id]

        if request.status == DeletionStatus.CONFIRMED:
            request.status = DeletionStatus.REVERTED
            return True

        return False

    def get_pending_deletions(self) -> List[Dict[str, Any]]:
        """Get pending deletion requests.

        Returns:
            List of pending deletion requests
        """
        pending = [
            r
            for r in self.deletion_requests.values()
            if r.status == DeletionStatus.PENDING
        ]
        return [r.to_dict() for r in pending]

    def get_version_history(self, domain_id: str) -> List[Dict[str, Any]]:
        """Get version history for domain.

        Args:
            domain_id: Domain ID

        Returns:
            List of import versions
        """
        versions = self.version_history.get(domain_id, [])
        return [v.to_dict() for v in versions]

    def get_status(self) -> Dict[str, Any]:
        """Get manager status.

        Returns:
            Status dictionary
        """
        return {
            "domains_tracked": len(self.current_versions),
            "total_imports": sum(len(h) for h in self.version_history.values()),
            "pending_deletions": len(self.get_pending_deletions()),
            "total_deletions_processed": len(self.deletion_history),
        }

    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        self.current_versions.clear()
        self.version_history.clear()
        self.deletion_requests.clear()
        self.deletion_history.clear()
