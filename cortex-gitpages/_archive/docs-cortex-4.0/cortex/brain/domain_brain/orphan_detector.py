"""Orphan Reference Detection: Stale Link Handling (AC-DB-E04).

Prevents visibility of deprecated/stale entity references by detecting orphaned
links and marking them as deprecated rather than deleting (preserving audit trail).

Mark-and-sweep approach:
1. Validate references: check if referenced entity still exists
2. If missing: mark reference as deprecated (NOT deleted)
3. Queries return: {entity, deprecated: true}
4. Weekly sweep: identify fully-orphaned subtrees
5. Audit trail: document all orphan events
"""

from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class OrphanEntry:
    """Record of an orphaned reference."""

    entity_id: str
    referenced_entity_id: str
    deprecation_date: datetime = field(default_factory=datetime.utcnow)
    reason: str = ""
    is_restorable: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entity_id": self.entity_id,
            "referenced_entity_id": self.referenced_entity_id,
            "deprecation_date": self.deprecation_date.isoformat(),
            "reason": self.reason,
            "is_restorable": self.is_restorable,
        }


@dataclass
class OrphanStats:
    """Statistics from orphan detection sweep."""

    total_references_checked: int = 0
    orphaned_references_found: int = 0
    fully_orphaned_subtrees: int = 0
    deprecations_marked: int = 0
    sweep_duration_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_references_checked": self.total_references_checked,
            "orphaned_references_found": self.orphaned_references_found,
            "fully_orphaned_subtrees": self.fully_orphaned_subtrees,
            "deprecations_marked": self.deprecations_marked,
            "sweep_duration_ms": self.sweep_duration_ms,
        }


class ReferenceValidator:
    """Validates entity references and detects orphans.

    Mark-and-sweep approach:
    - Maintain map of entity_id -> referenced_entity_ids
    - Track which entities exist
    - Detect missing references
    - Mark as deprecated (not deleted)
    - Preserve audit trail
    """

    def __init__(self) -> None:
        """Initialize reference validator."""
        self.entity_ids: Set[str] = set()  # All existing entities
        self.references: Dict[str, Set[str]] = {}  # entity_id -> {referenced_ids}
        self.deprecated_references: Dict[str, OrphanEntry] = {}
        self.orphan_sweep_history: List[OrphanStats] = []

    def register_entity(self, entity_id: str) -> None:
        """Register an entity as existing.

        Args:
            entity_id: Entity ID to register
        """
        self.entity_ids.add(entity_id)

    def add_reference(self, from_entity_id: str, to_entity_id: str) -> None:
        """Add a reference from one entity to another.

        Args:
            from_entity_id: Referencing entity ID
            to_entity_id: Referenced entity ID
        """
        if from_entity_id not in self.references:
            self.references[from_entity_id] = set()

        self.references[from_entity_id].add(to_entity_id)

    def validate_reference(
        self, from_entity_id: str, to_entity_id: str
    ) -> bool:
        """Validate a single reference.

        Args:
            from_entity_id: Referencing entity ID
            to_entity_id: Referenced entity ID

        Returns:
            True if valid, False if orphaned
        """
        return to_entity_id in self.entity_ids

    def mark_deprecated(
        self,
        from_entity_id: str,
        to_entity_id: str,
        reason: str = "Referenced entity not found",
    ) -> None:
        """Mark a reference as deprecated.

        Args:
            from_entity_id: Referencing entity ID
            to_entity_id: Referenced entity ID
            reason: Reason for deprecation
        """
        key = f"{from_entity_id}->{to_entity_id}"
        entry = OrphanEntry(
            entity_id=from_entity_id,
            referenced_entity_id=to_entity_id,
            reason=reason,
        )
        self.deprecated_references[key] = entry

    def is_orphaned(self, from_entity_id: str, to_entity_id: str) -> bool:
        """Check if reference is orphaned.

        Args:
            from_entity_id: Referencing entity ID
            to_entity_id: Referenced entity ID

        Returns:
            True if orphaned, False if valid
        """
        return not self.validate_reference(from_entity_id, to_entity_id)

    def sweep_orphans(self) -> OrphanStats:
        """Perform orphan sweep across all references.

        Returns:
            Sweep statistics
        """
        import time

        start_time = time.time()
        stats = OrphanStats()

        # Check all references
        for from_id, to_ids in self.references.items():
            for to_id in to_ids:
                stats.total_references_checked += 1

                # Check if referenced entity exists
                if to_id not in self.entity_ids:
                    stats.orphaned_references_found += 1
                    self.mark_deprecated(from_id, to_id)
                    stats.deprecations_marked += 1

        # Count fully orphaned subtrees (entities with all refs orphaned)
        for from_id, to_ids in self.references.items():
            if from_id not in self.entity_ids and len(to_ids) > 0:
                stats.fully_orphaned_subtrees += 1

        elapsed = time.time() - start_time
        stats.sweep_duration_ms = elapsed * 1000

        self.orphan_sweep_history.append(stats)

        return stats

    def get_deprecated_references(self) -> List[Dict[str, Any]]:
        """Get all deprecated references.

        Returns:
            List of deprecated reference entries
        """
        return [entry.to_dict() for entry in self.deprecated_references.values()]

    def get_orphan_status(self) -> Dict[str, Any]:
        """Get orphan detection status.

        Returns:
            Status dictionary
        """
        return {
            "total_entities": len(self.entity_ids),
            "total_references": sum(len(refs) for refs in self.references.values()),
            "deprecated_references": len(self.deprecated_references),
            "sweep_operations": len(self.orphan_sweep_history),
        }

    def get_sweep_history(self) -> List[Dict[str, Any]]:
        """Get sweep history.

        Returns:
            List of sweep statistics
        """
        return [stats.to_dict() for stats in self.orphan_sweep_history]

    def delete_entity(self, entity_id: str) -> int:
        """Delete entity and mark its references as orphaned.

        Args:
            entity_id: Entity to delete

        Returns:
            Number of orphaned references created
        """
        orphaned_count = 0

        # Find all references to this entity
        for from_id, to_ids in list(self.references.items()):
            if entity_id in to_ids:
                self.mark_deprecated(from_id, entity_id, "Referenced entity was deleted")
                orphaned_count += 1

        # Remove entity
        self.entity_ids.discard(entity_id)

        return orphaned_count

    def clear_all(self) -> None:
        """Clear all data (for testing)."""
        self.entity_ids.clear()
        self.references.clear()
        self.deprecated_references.clear()
        self.orphan_sweep_history.clear()
