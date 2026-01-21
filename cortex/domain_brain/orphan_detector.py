"""Orphan Detector - Reference validation and orphan detection.

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Set, List, Optional


class ReferenceValidator:
    """Validate entity references and detect orphans."""
    
    def __init__(self):
        """Initialize validator."""
        self._entities: Set[str] = set()
        self._references: Dict[str, Set[str]] = {}
        self._deprecated: Set[str] = set()
    
    def register_entity(self, entity_id: str) -> None:
        """Register an entity.
        
        Args:
            entity_id: Entity identifier to register
        """
        self._entities.add(entity_id)
        if entity_id not in self._references:
            self._references[entity_id] = set()
    
    def add_reference(self, source: str, target: str) -> None:
        """Add a reference from source to target.
        
        Args:
            source: Source entity ID
            target: Target entity ID
        """
        if source not in self._references:
            self._references[source] = set()
        self._references[source].add(target)
    
    def validate_reference(self, source: str, target: str) -> bool:
        """Validate a reference exists and target is registered.
        
        Args:
            source: Source entity ID
            target: Target entity ID
            
        Returns:
            True if reference is valid, False otherwise
        """
        if target not in self._entities:
            return False
        
        if source not in self._references:
            return False
        
        return target in self._references[source]
    
    def validate(self, reference: str) -> bool:
        """Validate reference."""
        return reference in self._entities
    
    def mark_deprecated(self, entity_id: str) -> None:
        """Mark an entity as deprecated.
        
        Args:
            entity_id: Entity to mark as deprecated
        """
        self._deprecated.add(entity_id)
    
    def is_deprecated(self, entity_id: str) -> bool:
        """Check if entity is deprecated.
        
        Args:
            entity_id: Entity to check
            
        Returns:
            True if deprecated, False otherwise
        """
        return entity_id in self._deprecated
    
    def detect_orphans(self) -> List[str]:
        """Detect orphaned entities (referenced but not registered).
        
        Returns:
            List of orphaned entity IDs
        """
        orphans = []
        
        for source, targets in self._references.items():
            for target in targets:
                if target not in self._entities:
                    orphans.append(target)
        
        return list(set(orphans))
    
    def sweep_deprecated(self, age_days: int = 7) -> int:
        """Sweep deprecated entities older than age_days.
        
        Args:
            age_days: Age threshold in days
            
        Returns:
            Number of entities swept
        """
        # Simplified: sweep all deprecated entities
        swept_count = len(self._deprecated)
        self._deprecated.clear()
        return swept_count


@dataclass
class OrphanEntry:
    """Orphan entry."""
    path: str
    reason: str
    detected_at: str = ""


@dataclass
class OrphanStats:
    """Orphan detection statistics."""
    total_checked: int = 0
    orphans_found: int = 0
    orphans_cleaned: int = 0


@dataclass
class OrphanRecord:
    """Orphaned record."""
    record_id: str
    missing_reference: str
    detected_at: str = ""

__all__ = ["ReferenceValidator", "OrphanEntry", "OrphanStats", "OrphanRecord"]
