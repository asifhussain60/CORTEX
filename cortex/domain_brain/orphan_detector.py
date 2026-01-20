"""Orphan Detector

Author: CORTEX Framework
"""

from dataclasses import dataclass

@dataclass
class ReferenceValidator:
    """Validate references."""
    
    def validate(self, reference: str) -> bool:
        """Validate reference."""
        return True


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

__all__ = ["ReferenceValidator", "OrphanEntry", "OrphanRecord"]
