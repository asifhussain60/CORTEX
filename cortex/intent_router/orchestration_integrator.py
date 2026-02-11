"""Orchestration Integrator - Connect intent router to orchestrators.

Provides integration layer between intent classification and orchestrators.

Author: CORTEX Framework
"""

from typing import Any, Dict, Optional


class OrchestrationIntegrator:
    """Integrate with orchestrators.

    Manages orchestrator registry and provides access to registered orchestrators.

    Attributes:
        orchestrator_registry: Dictionary mapping handler names to orchestrators
    """

    def __init__(self):
        """Initialize integrator."""
        self.orchestrator_registry: Dict[str, Any] = {}

    def register_orchestrator(self, handler_name: str, orchestrator: Any) -> None:
        """Register an orchestrator.

        Args:
            handler_name: Handler name (e.g., 'CreateHandler')
            orchestrator: Orchestrator instance
        """
        self.orchestrator_registry[handler_name] = orchestrator

    def get_orchestrator(self, handler_name: str) -> Optional[Any]:
        """Get registered orchestrator (delegating accessor).

        CORE-035: Single Canonical Implementation
        This method delegates to GitBackedRegistry.get_orchestrator() which is
        the canonical accessor. This wrapper exists for backward compatibility
        with code that expects OrchestrationIntegrator to provide orchestrator access.

        Args:
            handler_name: Handler name or orchestrator name

        Returns:
            Orchestrator instance or None if not registered
        """
        try:
            # AC-CORE-035: Delegate to canonical GitBackedRegistry accessor
            from cortex.wiring import get_cortex
            registry = get_cortex()
            if registry:
                return registry.get_orchestrator(handler_name)
            # Fallback to local registry for backward compatibility
            return self.orchestrator_registry.get(handler_name)
        except Exception:
            # Graceful degradation: fall back to local registry
            return self.orchestrator_registry.get(handler_name)


__all__ = ["OrchestrationIntegrator"]
