"""
DepthManager agent for depth override management with TTL.

Manages session-based depth overrides with turn-based expiration.

AC_START: AC-PHASE37.2-007
"""

from typing import Optional
from dataclasses import dataclass


@dataclass
class DepthOverride:
    """Depth override configuration."""
    
    depth_id: str
    turns_remaining: Optional[int]  # None = sticky (permanent)
    sticky: bool = False


class DepthManager:
    """Manage depth overrides with TTL."""
    
    def __init__(self):
        """Initialize depth manager."""
        self._override: Optional[DepthOverride] = None
        self._persona_default: Optional[str] = None
    
    def set_override(self, depth_id: str, turns: Optional[int] = None, sticky: bool = False) -> None:
        """Set depth override for session.
        
        Args:
            depth_id: Depth level ID (executive, standard, detailed, full)
            turns: Number of turns override lasts (None = 1 turn, unless sticky)
            sticky: If True, override persists across all future turns
        """
        if sticky:
            self._override = DepthOverride(
                depth_id=depth_id,
                turns_remaining=None,
                sticky=True
            )
        else:
            turns_remaining = turns if turns is not None else 1
            self._override = DepthOverride(
                depth_id=depth_id,
                turns_remaining=turns_remaining,
                sticky=False
            )
    
    def get_current_depth(self) -> Optional[str]:
        """Get current active depth level.
        
        Returns:
            Depth ID if override active, persona default, or None
        """
        if self._override:
            return self._override.depth_id
        
        return self._persona_default
    
    def consume_turn(self) -> None:
        """Decrement TTL after turn completes."""
        if not self._override:
            return
        
        # Sticky overrides never expire
        if self._override.sticky:
            return
        
        # Decrement turns
        if self._override.turns_remaining is not None:
            self._override.turns_remaining -= 1
            
            # Remove override if expired
            if self._override.turns_remaining <= 0:
                self._override = None
    
    def clear_override(self) -> None:
        """Clear depth override manually."""
        self._override = None
    
    def set_persona_default(self, depth_id: str) -> None:
        """Set persona's default depth level (fallback).
        
        Args:
            depth_id: Default depth for current persona
        """
        self._persona_default = depth_id
    
    def has_active_override(self) -> bool:
        """Check if override is currently active.
        
        Returns:
            True if override active
        """
        return self._override is not None


# AC_COMPLETE: AC-PHASE37.2-007 ✅ DepthManager with TTL and sticky overrides
