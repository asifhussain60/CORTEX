"""
Orchestrator Registry

Central registry for orchestrators with dependency injection support.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Type

from cortex.brain.core.interfaces import IOrchestrator
from cortex.brain.core.result import Result, Ok, Err


class OrchestratorRegistry:
    """
    Registry for managing orchestrator instances.
    
    Supports:
    - Registration by ID
    - Lookup by ID or capability
    - Dependency injection
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern for global registry."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._orchestrators: Dict[str, IOrchestrator] = {}
        return cls._instance
    
    def register(self, orchestrator: IOrchestrator) -> Result[None]:
        """
        Register an orchestrator instance.
        
        Args:
            orchestrator: Orchestrator to register
        
        Returns:
            Result indicating success or error
        """
        if orchestrator.id in self._orchestrators:
            return Err(f"Orchestrator already registered: {orchestrator.id}")
        
        self._orchestrators[orchestrator.id] = orchestrator
        return Ok(None)
    
    def get(self, orchestrator_id: str) -> Result[IOrchestrator]:
        """
        Get an orchestrator by ID.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            Result containing orchestrator or error
        """
        if orchestrator_id not in self._orchestrators:
            return Err(f"Orchestrator not found: {orchestrator_id}")
        
        return Ok(self._orchestrators[orchestrator_id])
    
    def find_handler(self, request: str) -> Result[IOrchestrator]:
        """
        Find an orchestrator that can handle a request.
        
        Args:
            request: Request string to handle
        
        Returns:
            Result containing matching orchestrator or error
        """
        for orchestrator in self._orchestrators.values():
            if orchestrator.can_handle(request):
                return Ok(orchestrator)
        
        return Err(f"No orchestrator can handle request: {request[:50]}...")
    
    def list_all(self) -> List[str]:
        """List all registered orchestrator IDs."""
        return list(self._orchestrators.keys())
    
    def clear(self):
        """Clear all registered orchestrators (for testing)."""
        self._orchestrators.clear()
    
    @classmethod
    def reset(cls):
        """Reset singleton instance (for testing)."""
        cls._instance = None
