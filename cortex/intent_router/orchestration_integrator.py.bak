"""Orchestration Integrator - Connect intent router to orchestrators.

Provides integration layer between intent classification and orchestrators.

Author: CORTEX Framework
"""

from typing import Dict, Optional, Any


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
        """Get registered orchestrator.
        
        Args:
            handler_name: Handler name
            
        Returns:
            Orchestrator instance or None if not registered
        """
        return self.orchestrator_registry.get(handler_name)


__all__ = ["OrchestrationIntegrator"]
