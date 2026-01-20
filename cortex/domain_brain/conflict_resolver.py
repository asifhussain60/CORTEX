"""Conflict Resolver

Author: CORTEX Framework
"""

from enum import Enum

class ResolutionTier(str, Enum):
    """Resolution tiers."""
    AUTOMATIC = "automatic"
    MANUAL = "manual"
    ESCALATED = "escalated"

__all__ = ["ResolutionTier"]
