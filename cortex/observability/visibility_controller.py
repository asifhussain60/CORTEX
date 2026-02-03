"""
CORTEX Visibility Controller - Training Wheels Toggle System

Manages orchestrator visibility modes with lifecycle-based transitions.
Implements toggle via environment variable precedence.

Authority: AC-UX-VISIBILITY-001 (Phase 20.2 Component #1)
Rule: CORE-011 (Type Hints)
"""

import os
from enum import Enum
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class VisibilityMode(str, Enum):
    """Visibility modes for orchestrator activity."""
    
    FULL = "full"  # All indicators (learning phase)
    FAILURES_ONLY = "failures"  # Only show failures (transitioning)
    OFF = "off"  # Disabled (mature phase)


@dataclass
class IntelligenceFlags:
    """Intelligence activation flags."""
    
    lens_enabled: bool = False
    knowledge_enabled: bool = False
    synthesis_enabled: bool = False


@dataclass
class OrchestratorContext:
    """Context for orchestrator execution visibility."""
    
    orchestrator_name: str
    orchestrator_icon: str
    current_stage: int
    stages_completed: list[str]
    intelligence_active: IntelligenceFlags
    failure_stage: Optional[int] = None
    failure_reason: Optional[str] = None


class VisibilityController:
    """
    Controls visibility of orchestrator activity indicators.
    
    Implements training wheels pattern:
    - FULL mode: All badges, stage progress, intelligence indicators
    - FAILURES_ONLY mode: Only show failures (transitioning)
    - OFF mode: Clean responses (mature phase)
    
    Precedence: ENV VAR > Config > Default
    
    Usage:
        >>> controller = VisibilityController()
        >>> if controller.should_show_success_details():
        ...     # Display orchestrator badges
        ...     pass
    
    Authority: AC-UX-VISIBILITY-001
    """
    
    def __init__(self) -> None:
        """Initialize VisibilityController."""
        self._mode_cache: Optional[VisibilityMode] = None
        logger.debug("VisibilityController initialized")
    
    def get_visibility_mode(self) -> VisibilityMode:
        """
        Get current visibility mode with precedence: ENV > Config > Default.
        
        Returns:
            Current VisibilityMode
        """
        if self._mode_cache is None:
            # 1. Check environment variable (highest precedence)
            env_mode = os.getenv("CORTEX_ORCHESTRATOR_VISIBILITY", "").lower()
            if env_mode in ["full", "failures", "off"]:
                self._mode_cache = VisibilityMode(env_mode)
                logger.info(f"Visibility mode set from ENV VAR: {env_mode}")
            
            # 2. TODO Phase 20.2: Add config file support
            # elif self._config.observability.orchestrator_visibility.mode:
            #     self._mode_cache = VisibilityMode(
            #         self._config.observability.orchestrator_visibility.mode
            #     )
            
            # 3. Default to FULL
            else:
                self._mode_cache = VisibilityMode.FULL
                logger.info("Visibility mode defaulted to FULL (learning phase)")
        
        return self._mode_cache
    
    def should_show_success_details(self) -> bool:
        """
        Check if success details should be shown.
        
        Returns:
            True if FULL mode, False otherwise
        """
        return self.get_visibility_mode() == VisibilityMode.FULL
    
    def should_show_failure_details(self) -> bool:
        """
        Check if failure details should be shown.
        
        Returns:
            True if FULL or FAILURES_ONLY mode, False if OFF
        """
        mode = self.get_visibility_mode()
        return mode in [VisibilityMode.FULL, VisibilityMode.FAILURES_ONLY]
    
    def reset_cache(self) -> None:
        """Reset cached visibility mode (for testing or runtime changes)."""
        self._mode_cache = None
        logger.debug("Visibility mode cache reset")


# Singleton instance
_controller_instance: Optional[VisibilityController] = None


def get_visibility_controller() -> VisibilityController:
    """
    Get singleton VisibilityController instance.
    
    Returns:
        VisibilityController instance
    """
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = VisibilityController()
    return _controller_instance
