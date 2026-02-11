"""
Component initialization status tracking and health checks.

AC-REM-004-01: Explicit Initialization Status API
AC-REM-004-02: Component Health Checks
AC-REM-004-03: Degradation Mode Visibility
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional


class ComponentType(Enum):
    """Component criticality classification."""
    CRITICAL = "CRITICAL"  # Must succeed or fail fast
    OPTIONAL = "OPTIONAL"  # Can degrade gracefully


@dataclass
class ComponentStatus:
    """Status of a single component."""

    component_name: str
    initialized: bool
    required: bool  # True if CRITICAL
    degraded: bool
    error_message: Optional[str] = None
    component_type: ComponentType = ComponentType.OPTIONAL


class ComponentHealthTracker:
    """
    Tracks component initialization status and provides health check API.

    Provides:
    - get_initialization_status() - per-component status
    - get_health_summary() - overall system health
    - is_ready() - CRITICAL components check
    - is_live() - system running check
    """

    def __init__(self):
        """Initialize health tracker."""
        self._components: Dict[str, ComponentStatus] = {}

    def register_component(
        self,
        component_name: str,
        component_type: ComponentType = ComponentType.OPTIONAL
    ) -> None:
        """
        Register a component for tracking.

        Args:
            component_name: Name of component
            component_type: CRITICAL or OPTIONAL
        """
        self._components[component_name] = ComponentStatus(
            component_name=component_name,
            initialized=False,
            required=(component_type == ComponentType.CRITICAL),
            degraded=False,
            component_type=component_type
        )

    def mark_initialized(
        self,
        component_name: str,
        success: bool,
        error_message: Optional[str] = None
    ) -> None:
        """
        Mark component as initialized.

        Args:
            component_name: Component name
            success: Whether initialization succeeded
            error_message: Error if failed
        """
        if component_name not in self._components:
            return

        component = self._components[component_name]
        component.initialized = success
        component.degraded = not success
        component.error_message = error_message

    def get_initialization_status(
        self,
        component_name: Optional[str] = None
    ) -> List[ComponentStatus]:
        """
        Get initialization status.

        Args:
            component_name: Specific component or all if None

        Returns:
            List of component statuses
        """
        if component_name:
            return [self._components[component_name]] if component_name in self._components else []
        return list(self._components.values())

    def is_ready(self) -> bool:
        """
        Check if system is ready (all CRITICAL components initialized).

        Returns:
            True if all CRITICAL components initialized
        """
        for component in self._components.values():
            if component.required and not component.initialized:
                return False
        return True

    def is_live(self) -> bool:
        """
        Check if system is live (at least running).

        Returns:
            True (always, if process is running)
        """
        return True

    def get_health_summary(self) -> Dict[str, any]:
        """
        Get overall health summary.

        Returns:
            Dictionary with health metrics
        """
        total = len(self._components)
        initialized = sum(1 for c in self._components.values() if c.initialized)
        degraded = sum(1 for c in self._components.values() if c.degraded)
        critical_failed = sum(
            1 for c in self._components.values()
            if c.required and not c.initialized
        )

        return {
            "ready": self.is_ready(),
            "live": self.is_live(),
            "total_components": total,
            "initialized": initialized,
            "degraded": degraded,
            "critical_failed": critical_failed,
            "health_percentage": (initialized / total * 100) if total > 0 else 0
        }


# Global instance
_health_tracker = ComponentHealthTracker()


def get_health_tracker() -> ComponentHealthTracker:
    """Get global health tracker instance."""
    return _health_tracker
