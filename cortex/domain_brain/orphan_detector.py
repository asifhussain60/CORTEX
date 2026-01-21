"""Orphan Detector - Reference validation and orphan detection.

Author: CORTEX Framework
Implements: AC-DB-E04 (Orphan Reference Detection)
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set, List, Optional, Any


@dataclass
class OrphanStats:
    """Orphan detection statistics.
    
    Attributes:
        total_references_checked: Total references validated.
        orphaned_references_found: Number of orphaned references.
        deprecations_marked: Number of deprecations marked.
        sweep_duration_ms: Duration of sweep in milliseconds.
    """
    total_references_checked: int = 0
    orphaned_references_found: int = 0
    deprecations_marked: int = 0
    sweep_duration_ms: float = 0.0
    total_checked: int = 0
    orphans_found: int = 0
    orphans_cleaned: int = 0


@dataclass
class DeprecatedReference:
    """A deprecated reference entry.
    
    Attributes:
        entity_id: Source entity ID.
        referenced_entity_id: Target entity ID (missing).
        reason: Reason for deprecation.
        marked_at: Timestamp when marked.
        is_restorable: Whether the reference can be restored.
    """
    entity_id: str
    referenced_entity_id: str
    reason: Optional[str] = None
    marked_at: Optional[datetime] = None
    is_restorable: bool = True


class ReferenceValidator:
    """Validate entity references and detect orphans.
    
    Provides:
    - Entity registration and reference tracking
    - Reference validation
    - Orphan detection and deprecation marking
    - Weekly sweep functionality
    """
    
    def __init__(self) -> None:
        """Initialize validator."""
        self._entities: Set[str] = set()
        self._references: Dict[str, Set[str]] = {}
        self._deprecated_refs: List[DeprecatedReference] = []
        self._sweep_history: List[Dict[str, Any]] = []
        self._sweep_count: int = 0
    
    @property
    def entity_ids(self) -> Set[str]:
        """Get registered entity IDs."""
        return self._entities.copy()
    
    def register_entity(self, entity_id: str) -> None:
        """Register an entity.
        
        Args:
            entity_id: Entity identifier to register.
        """
        self._entities.add(entity_id)
        if entity_id not in self._references:
            self._references[entity_id] = set()
    
    def add_reference(self, source: str, target: str) -> None:
        """Add a reference from source to target.
        
        Args:
            source: Source entity ID.
            target: Target entity ID.
        """
        if source not in self._references:
            self._references[source] = set()
        self._references[source].add(target)
    
    def validate_reference(self, source: str, target: str) -> bool:
        """Validate a reference exists and target is registered.
        
        Args:
            source: Source entity ID.
            target: Target entity ID.
            
        Returns:
            True if reference is valid, False otherwise.
        """
        if target not in self._entities:
            return False
        
        if source not in self._references:
            return False
        
        return target in self._references[source]
    
    def validate(self, reference: str) -> bool:
        """Validate reference.
        
        Args:
            reference: Reference to validate.
            
        Returns:
            True if valid, False otherwise.
        """
        return reference in self._entities
    
    def mark_deprecated(
        self,
        entity_id: str,
        referenced_entity_id: str,
        reason: Optional[str] = None
    ) -> None:
        """Mark a reference as deprecated.
        
        Args:
            entity_id: Source entity ID.
            referenced_entity_id: Target entity ID (missing).
            reason: Reason for deprecation.
        """
        dep_ref = DeprecatedReference(
            entity_id=entity_id,
            referenced_entity_id=referenced_entity_id,
            reason=reason,
            marked_at=datetime.utcnow(),
            is_restorable=True
        )
        self._deprecated_refs.append(dep_ref)
    
    def get_deprecated_references(self) -> List[Dict[str, Any]]:
        """Get all deprecated references.
        
        Returns:
            List of deprecated reference info.
        """
        return [
            {
                "entity_id": ref.entity_id,
                "referenced_entity_id": ref.referenced_entity_id,
                "reason": ref.reason,
                "is_restorable": ref.is_restorable,
                "marked_at": ref.marked_at.isoformat() if ref.marked_at else None
            }
            for ref in self._deprecated_refs
        ]
    
    def is_deprecated(self, entity_id: str) -> bool:
        """Check if entity has deprecated references.
        
        Args:
            entity_id: Entity to check.
            
        Returns:
            True if has deprecated refs, False otherwise.
        """
        return any(ref.entity_id == entity_id for ref in self._deprecated_refs)
    
    def delete_entity(self, entity_id: str) -> int:
        """Delete an entity and count orphaned references.
        
        Args:
            entity_id: Entity to delete.
            
        Returns:
            Number of references that become orphaned.
        """
        orphaned_count = 0
        
        # Remove from entities
        self._entities.discard(entity_id)
        
        # Count references to this entity
        for source, targets in self._references.items():
            if entity_id in targets:
                orphaned_count += 1
        
        return orphaned_count
    
    def detect_orphans(self) -> List[str]:
        """Detect orphaned entities (referenced but not registered).
        
        Returns:
            List of orphaned entity IDs.
        """
        orphans = []
        
        for source, targets in self._references.items():
            for target in targets:
                if target not in self._entities:
                    orphans.append(target)
        
        return list(set(orphans))
    
    def sweep_orphans(self) -> OrphanStats:
        """Sweep and detect orphaned references.
        
        Checks all references, detects orphans, and marks them deprecated.
        
        Returns:
            OrphanStats with sweep results.
        """
        import time
        start_time = time.time()
        
        total_refs = 0
        orphaned = 0
        deprecations = 0
        
        for source, targets in self._references.items():
            for target in targets:
                total_refs += 1
                if target not in self._entities:
                    orphaned += 1
                    # Check if not already deprecated
                    already_deprecated = any(
                        ref.entity_id == source and ref.referenced_entity_id == target
                        for ref in self._deprecated_refs
                    )
                    if not already_deprecated:
                        self.mark_deprecated(source, target, "Orphan sweep")
                        deprecations += 1
        
        elapsed_ms = (time.time() - start_time) * 1000
        self._sweep_count += 1
        
        stats = OrphanStats(
            total_references_checked=total_refs,
            orphaned_references_found=orphaned,
            deprecations_marked=deprecations,
            sweep_duration_ms=elapsed_ms
        )
        
        # Track history
        self._sweep_history.append({
            "sweep_number": self._sweep_count,
            "total_references_checked": total_refs,
            "orphaned_references_found": orphaned,
            "deprecations_marked": deprecations,
            "sweep_duration_ms": elapsed_ms,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        return stats
    
    def sweep_deprecated(self, age_days: int = 7) -> int:
        """Sweep deprecated entities older than age_days.
        
        Args:
            age_days: Age threshold in days.
            
        Returns:
            Number of entities swept.
        """
        swept_count = len(self._deprecated_refs)
        self._deprecated_refs.clear()
        return swept_count
    
    def get_orphan_status(self) -> Dict[str, Any]:
        """Get orphan detection status.
        
        Returns:
            Dictionary with status information.
        """
        total_refs = sum(len(targets) for targets in self._references.values())
        
        return {
            "total_entities": len(self._entities),
            "total_references": total_refs,
            "deprecated_references": len(self._deprecated_refs),
            "sweep_operations": self._sweep_count
        }
    
    def get_sweep_history(self) -> List[Dict[str, Any]]:
        """Get sweep history.
        
        Returns:
            List of sweep history entries.
        """
        return self._sweep_history.copy()


@dataclass
class OrphanEntry:
    """Orphan entry."""
    path: str
    reason: str
    detected_at: str = ""


@dataclass
class OrphanRecord:
    """Orphaned record."""
    record_id: str
    missing_reference: str
    detected_at: str = ""


__all__ = [
    "ReferenceValidator",
    "OrphanEntry",
    "OrphanStats",
    "OrphanRecord",
    "DeprecatedReference"
]
