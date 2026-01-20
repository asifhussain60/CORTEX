"""Conflict Resolver

Author: CORTEX Framework
"""

from enum import Enum

class ResolutionTier(str, Enum):
    """Resolution tiers."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    ESCALATED = "escalated"


class ReviewStatus(Enum):
    """Conflict review status."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"



class ConflictResolver:
    """Resolve domain conflicts."""
    
    def resolve(self, conflict_id: str, tier: ResolutionTier) -> bool:
        """Resolve conflict."""
        return True

__all__ = ["ResolutionTier", "ConflictResolver"]
