"""
Persona Models for Phase 37 Role-Adaptive System

Dataclasses representing personas, depth levels, and configuration.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class DepthLevel(str, Enum):
    """Response detail level options"""
    EXECUTIVE = "executive"
    STANDARD = "standard"
    DETAILED = "detailed"
    FULL = "full"


class PersonaId(str, Enum):
    """User persona identifiers"""
    BUSINESS_LEADER = "business_leader"
    PRODUCT_OWNER = "product_owner"
    SCRUM_MASTER = "scrum_master"
    TECH_LEAD = "tech_lead"
    ENGINEER = "engineer"
    UNKNOWN = "unknown"


@dataclass
class DepthConfig:
    """Configuration for a specific depth level"""
    id: DepthLevel
    description: str
    word_limit: Optional[int]
    show_code: Union[bool, str]
    metrics: str

    def __post_init__(self):
        if isinstance(self.show_code, str):
            self.show_code = self.show_code
        else:
            self.show_code = "complete" if self.show_code else "none"


@dataclass
class PersonaConfig:
    """Configuration for a specific persona"""
    id: PersonaId
    display_name: str
    description: str
    format: str
    depth: Optional[DepthLevel]
    word_limit: Optional[int]
    show_code: Union[bool, str]
    show_metrics: bool
    metric_types: List[str] = field(default_factory=list)
    onboarding: bool = False
    onboarding_focus: List[str] = field(default_factory=list)
    trigger_discovery: bool = False

    def get_depth_config(self, depth: DepthLevel) -> Optional[DepthConfig]:
        """Get configuration for a specific depth level within this persona"""
        # This will be mapped via depth_levels registry
        return None


@dataclass
class SessionContext:
    """In-session persona context (ephemeral)"""
    primary_persona: PersonaId
    active_depth: DepthLevel
    depth_override_ttl: int = 0  # Turns remaining for override
    inference_confidence: float = 0.0
    switch_history: List[Dict[str, Any]] = field(default_factory=list)

    def has_active_override(self) -> bool:
        """Check if depth override is still active"""
        return self.depth_override_ttl > 0

    def decrement_override_ttl(self):
        """Decrement override TTL (called each turn)"""
        if self.depth_override_ttl > 0:
            self.depth_override_ttl -= 1


@dataclass
class UserPreferences:
    """Persistent user persona preferences (cross-session)"""
    username: str
    primary_persona: PersonaId
    depth_preference: DepthLevel
    created_at: str
    last_active: str
    overrides: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class WorkspaceConfig:
    """Team/workspace persona configuration"""
    default_persona: PersonaId
    allowed_personas: List[PersonaId] = field(default_factory=list)
    require_explicit_role: bool = False
    enable_role_inference: bool = True
