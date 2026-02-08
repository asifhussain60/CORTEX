"""
SessionContext: Manage session state and user preferences

Authority: Phase 37 S3, CORE-008 (TDD-first)

Manages:
- User persona and depth settings per session
- Cross-turn tracking of persona switches
- Persistent user preferences
- Session-specific overrides
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from dataclasses import dataclass, field

from cortex.orchestrators.persona.models import PersonaId, DepthLevel


@dataclass
class PersonaSwitch:
    """Record of a persona change"""
    timestamp: str
    from_persona: PersonaId
    to_persona: PersonaId
    confidence: float
    trigger: str  # "explicit_keyword", "context_signal", "command", etc.


@dataclass
class DepthOverride:
    """Active depth override with TTL"""
    level: DepthLevel
    set_at: str
    ttl_turns: int  # Expires after N turns (-1 = permanent)
    turns_elapsed: int = 0


class SessionContext:
    """
    Manage in-session persona and depth state.
    
    Attributes:
        user_id: Unique identifier for user
        primary_persona: Current active persona
        active_depth: Current active depth level
        depth_override: Active temporary depth override
        switch_history: List of persona switches in session
    """

    def __init__(self, user_id: str):
        """
        Initialize session context.
        
        Args:
            user_id: Unique identifier for user
        """
        self.user_id = user_id
        self.primary_persona = PersonaId.UNKNOWN
        self.active_depth = DepthLevel.STANDARD  # Primary depth, not override
        self.depth_override: Optional[DepthOverride] = None
        self.switch_history: List[PersonaSwitch] = []
        self.inference_confidence = 0.0
        self.created_at = datetime.now().isoformat()

    def set_persona(
        self,
        persona: PersonaId,
        confidence: float = 1.0,
        trigger: str = "unknown"
    ) -> None:
        """
        Set primary persona for session.
        
        Args:
            persona: PersonaId to set
            confidence: Confidence score (0-1)
            trigger: What triggered the change
        """
        if self.primary_persona != persona:
            # Record switch
            self.switch_history.append(
                PersonaSwitch(
                    timestamp=datetime.now().isoformat(),
                    from_persona=self.primary_persona,
                    to_persona=persona,
                    confidence=confidence,
                    trigger=trigger
                )
            )
        
        self.primary_persona = persona
        self.inference_confidence = confidence

    def set_depth_override(
        self,
        level: DepthLevel,
        ttl_turns: int = 1,
        silent: bool = False
    ) -> None:
        """
        Set temporary depth override.
        
        Args:
            level: DepthLevel to override to
            ttl_turns: Number of turns before expiring (-1 = permanent)
            silent: If True, don't track in logs
        """
        self.depth_override = DepthOverride(
            level=level,
            set_at=datetime.now().isoformat(),
            ttl_turns=ttl_turns,
            turns_elapsed=0
        )
        # Note: Do NOT modify self.active_depth; it's the primary, not the override

    def get_active_depth(self) -> DepthLevel:
        """
        Get current active depth, handling override TTL.
        
        Returns:
            Current DepthLevel (override if active, otherwise primary)
        """
        if self.depth_override is None:
            return self.active_depth
        
        # Check if override expired
        if self.depth_override.ttl_turns != -1:
            if self.depth_override.turns_elapsed >= self.depth_override.ttl_turns:
                self.depth_override = None
                return self.active_depth
        
        return self.depth_override.level

    def advance_turn(self) -> None:
        """
        Advance turn counter. Call after each message processed.
        Decrements depth override TTL.
        """
        if self.depth_override is not None:
            self.depth_override.turns_elapsed += 1

    def clear_depth_override(self) -> None:
        """Clear active depth override"""
        self.depth_override = None

    def get_switch_history(self, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get persona switch history.
        
        Args:
            limit: Max number of switches to return (None = all)
            
        Returns:
            List of switch records
        """
        history = [
            {
                'timestamp': switch.timestamp,
                'from_persona': switch.from_persona.value,
                'to_persona': switch.to_persona.value,
                'confidence': switch.confidence,
                'trigger': switch.trigger
            }
            for switch in self.switch_history
        ]
        
        if limit:
            return history[-limit:]
        return history

    def reset(self) -> None:
        """Reset session context to initial state"""
        self.primary_persona = PersonaId.UNKNOWN
        self.active_depth = DepthLevel.STANDARD
        self.depth_override = None
        self.switch_history = []
        self.inference_confidence = 0.0

    def get_state_dict(self) -> Dict[str, Any]:
        """
        Get current session state as dict.
        
        Returns:
            Dict with current session state
        """
        return {
            'user_id': self.user_id,
            'primary_persona': self.primary_persona.value,
            'active_depth': self.get_active_depth().value,
            'depth_override_active': self.depth_override is not None,
            'inference_confidence': self.inference_confidence,
            'switch_count': len(self.switch_history),
            'created_at': self.created_at
        }
