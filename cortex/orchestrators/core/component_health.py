"""Component Health Tracker for CORTEX system.

Tracks health status of system components for monitoring and graceful degradation.

Author: Asif Hussain
Phase: AC-BUGFIX-004
Ticket: Missing module for master_orchestrator.py
"""

from enum import Enum
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from datetime import datetime


class ComponentType(Enum):  # CORE-035-scoped — domain-specific variant
    """Type classification for system components."""
    CRITICAL = "CRITICAL"      # System cannot function without this
    ESSENTIAL = "ESSENTIAL"    # System degraded without this
    OPTIONAL = "OPTIONAL"      # System can function without this
    EXPERIMENTAL = "EXPERIMENTAL"  # Experimental features


class HealthStatus(Enum):  # CORE-035-scoped — domain-specific health status — context-appropriate states
    """Health status of a component."""
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"


@dataclass
class ComponentHealth:  # CORE-035-scoped — domain-specific component health model
    """Health information for a single component."""
    name: str
    component_type: ComponentType
    status: HealthStatus = HealthStatus.UNKNOWN
    last_check: Optional[datetime] = None
    error_count: int = 0
    success_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def record_success(self) -> None:
        """Record successful component operation."""
        self.success_count += 1
        self.last_check = datetime.now()
        if self.error_count > 0:
            # Improve status if recovering
            if self.status == HealthStatus.UNHEALTHY:
                self.status = HealthStatus.DEGRADED
            elif self.status == HealthStatus.DEGRADED:
                # If 3+ successes after errors, mark healthy
                if self.success_count >= 3:
                    self.status = HealthStatus.HEALTHY
        else:
            self.status = HealthStatus.HEALTHY

    def record_failure(self, error: Optional[Exception] = None) -> None:
        """Record failed component operation."""
        self.error_count += 1
        self.last_check = datetime.now()

        if error:
            self.metadata["last_error"] = str(error)
            self.metadata["last_error_time"] = datetime.now().isoformat()

        # Degrade status based on error count
        if self.error_count >= 5:
            self.status = HealthStatus.UNHEALTHY
        elif self.error_count >= 2:
            self.status = HealthStatus.DEGRADED

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "component_type": self.component_type.value,
            "status": self.status.value,
            "last_check": self.last_check.isoformat() if self.last_check else None,
            "error_count": self.error_count,
            "success_count": self.success_count,
            "metadata": self.metadata,
        }


class ComponentHealthTracker:
    """Tracks health of system components for monitoring and graceful degradation.

    Used by MasterOrchestrator to monitor critical components and enable
    graceful degradation when components fail.

    Example:
        >>> tracker = ComponentHealthTracker()
        >>> tracker.register_component("MasterOrchestrator", ComponentType.CRITICAL)
        >>> tracker.record_success("MasterOrchestrator")
        >>> tracker.get_health_status("MasterOrchestrator")
        'HEALTHY'
    """

    def __init__(self) -> None:
        """Initialize component health tracker."""
        self._components: Dict[str, ComponentHealth] = {}

    def register_component(
        self,
        name: str,
        component_type: ComponentType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a component for health tracking.

        Args:
            name: Component name
            component_type: Classification of component importance
            metadata: Optional metadata about the component
        """
        if name in self._components:
            # Update existing component
            self._components[name].component_type = component_type
            if metadata:
                self._components[name].metadata.update(metadata)
        else:
            # Create new component
            self._components[name] = ComponentHealth(
                name=name,
                component_type=component_type,
                metadata=metadata or {}
            )

    def record_success(self, name: str) -> None:
        """Record successful operation for component.

        Args:
            name: Component name
        """
        if name not in self._components:
            # Auto-register as OPTIONAL if not registered
            self.register_component(name, ComponentType.OPTIONAL)

        self._components[name].record_success()

    def record_failure(
        self,
        name: str,
        error: Optional[Exception] = None
    ) -> None:
        """Record failed operation for component.

        Args:
            name: Component name
            error: Optional exception that caused failure
        """
        if name not in self._components:
            # Auto-register as OPTIONAL if not registered
            self.register_component(name, ComponentType.OPTIONAL)

        self._components[name].record_failure(error)

    def get_health_status(self, name: str) -> str:
        """Get health status of component.

        Args:
            name: Component name

        Returns:
            Health status string (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN)
        """
        if name not in self._components:
            return HealthStatus.UNKNOWN.value

        return self._components[name].status.value

    def get_component_health(self, name: str) -> Optional[ComponentHealth]:
        """Get full health information for component.

        Args:
            name: Component name

        Returns:
            ComponentHealth instance or None if not registered
        """
        return self._components.get(name)

    def get_all_components(self) -> List[ComponentHealth]:
        """Get health information for all components.

        Returns:
            List of ComponentHealth instances
        """
        return list(self._components.values())

    def get_critical_components(self) -> List[ComponentHealth]:
        """Get health information for critical components.

        Returns:
            List of ComponentHealth instances for critical components
        """
        return [
            component for component in self._components.values()
            if component.component_type == ComponentType.CRITICAL
        ]

    def is_system_healthy(self) -> bool:
        """Check if system is healthy overall.

        System is healthy if all CRITICAL components are HEALTHY or DEGRADED.

        Returns:
            True if system is healthy, False otherwise
        """
        critical_components = self.get_critical_components()

        if not critical_components:
            # No critical components registered - assume healthy
            return True

        for component in critical_components:
            if component.status == HealthStatus.UNHEALTHY:
                return False

        return True

    def get_system_health_summary(self) -> Dict[str, Any]:
        """Get summary of system health.

        Returns:
            Dictionary with health summary
        """
        all_components = self.get_all_components()
        critical_components = self.get_critical_components()

        healthy_count = sum(
            1 for c in all_components
            if c.status == HealthStatus.HEALTHY
        )
        degraded_count = sum(
            1 for c in all_components
            if c.status == HealthStatus.DEGRADED
        )
        unhealthy_count = sum(
            1 for c in all_components
            if c.status == HealthStatus.UNHEALTHY
        )

        return {
            "is_healthy": self.is_system_healthy(),
            "total_components": len(all_components),
            "critical_components": len(critical_components),
            "healthy_count": healthy_count,
            "degraded_count": degraded_count,
            "unhealthy_count": unhealthy_count,
            "components": [c.to_dict() for c in all_components],
        }

    def reset_component(self, name: str) -> None:
        """Reset health tracking for component.

        Args:
            name: Component name
        """
        if name in self._components:
            self._components[name].status = HealthStatus.UNKNOWN
            self._components[name].error_count = 0
            self._components[name].success_count = 0
            self._components[name].last_check = None

    def get_initialization_status(self) -> List[Dict[str, Any]]:
        """Get initialization status for all registered components.

        Returns a snapshot of each registered component's name, type and current
        health status — used by test harness and startup diagnostics.

        Returns:
            List of dicts with keys: name, component_type, status, error_count, success_count
        """
        return [
            {
                "name": c.name,
                "component_type": c.component_type.value,
                "status": c.status.value,
                "error_count": c.error_count,
                "success_count": c.success_count,
            }
            for c in self._components.values()
        ]

    def unregister_component(self, name: str) -> None:
        """Unregister component from health tracking.

        Args:
            name: Component name
        """
        if name in self._components:
            del self._components[name]
