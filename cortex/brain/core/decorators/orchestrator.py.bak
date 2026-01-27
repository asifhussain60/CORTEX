"""
Orchestrator Decorator and Registry

Docker-First Architecture: YAML-backed wiring replaces database registries.

Provides @orchestrator decorator for automatic registration and
context injection. The decorator enables:
- Auto-discovery of orchestrators
- Tier dependency declaration
- Automatic governance context injection
- MCP tool exposure metadata
"""

from typing import Any, Callable, Dict, List, Optional, Set, Type
from functools import wraps
import inspect
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# Try importing base class
try:
    from cortex.brain.core.orchestrator_base import OrchestratorBase, OrchestrationContext
except ImportError:
    # Fallback for when base classes not available
    OrchestratorBase = object
    OrchestrationContext = None

# Global in-memory registry for decorated orchestrators
_ORCHESTRATOR_REGISTRY: Dict[str, Dict[str, Any]] = {}


class OrchestratorRegistry:
    """
    Simple orchestrator registry for backward compatibility.
    
    Docker-first architecture: Actual wiring is via YAML configuration.
    This provides a runtime registry for decorator-based registration.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._orchestrators: Dict[str, Dict[str, Any]] = {}
            self._name_to_id: Dict[str, str] = {}
            self._initialized = True
    
    def register(
        self,
        orchestrator_id: str,
        name: str,
        cls: Type,
        module_path: str,
        tier_dependencies: Optional[Set[str]] = None,
        expose_mcp: bool = True,
        description: str = "",
    ) -> None:
        """Register an orchestrator."""
        entry = {
            "id": orchestrator_id,
            "name": name,
            "class": cls,
            "module_path": module_path,
            "tier_dependencies": tier_dependencies or set(),
            "expose_mcp": expose_mcp,
            "description": description,
            "registered_at": datetime.now().isoformat(),
            "wired": True,
        }
        self._orchestrators[orchestrator_id] = entry
        self._name_to_id[name] = orchestrator_id
        _ORCHESTRATOR_REGISTRY[orchestrator_id] = entry
        logger.debug(f"Registered orchestrator: {name} ({orchestrator_id})")
    
    def get_by_id(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator by ID."""
        return self._orchestrators.get(orchestrator_id)
    
    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator by name."""
        orch_id = self._name_to_id.get(name)
        if orch_id:
            return self._orchestrators.get(orch_id)
        return None
    
    def get_all(self) -> List[Dict[str, Any]]:
        """Get all registered orchestrators."""
        return list(self._orchestrators.values())
    
    def count(self) -> int:
        """Count registered orchestrators."""
        return len(self._orchestrators)
    
    def clear(self) -> None:
        """Clear registry (for testing)."""
        self._orchestrators.clear()
        self._name_to_id.clear()
        _ORCHESTRATOR_REGISTRY.clear()


# Singleton instance
_registry = OrchestratorRegistry()


def get_orchestrator_registry() -> OrchestratorRegistry:
    """Get the singleton orchestrator registry."""
    return _registry


def orchestrator(
    orchestrator_id: str,
    name: Optional[str] = None,
    tier_dependencies: Optional[Set[str]] = None,
    expose_mcp: bool = True,
    description: str = "",
) -> Callable[[Type], Type]:
    """
    Decorator to register an orchestrator.
    
    Docker-first architecture: Decorates class for runtime registration.
    Actual wiring is managed via YAML configuration.
    
    Args:
        orchestrator_id: Unique identifier for the orchestrator
        name: Human-readable name (defaults to class name)
        tier_dependencies: Set of tier IDs this orchestrator depends on
        expose_mcp: Whether to expose via MCP
        description: Description of the orchestrator
        
    Returns:
        Decorated class with registration
        
    Example:
        @orchestrator(
            orchestrator_id="governance_orch",
            name="GovernanceOrchestrator",
            tier_dependencies={"tier0"},
        )
        class GovernanceOrchestrator(OrchestratorBase):
            pass
    """
    def decorator(cls: Type) -> Type:
        actual_name = name or cls.__name__
        module_path = f"{cls.__module__}.{cls.__name__}"
        
        _registry.register(
            orchestrator_id=orchestrator_id,
            name=actual_name,
            cls=cls,
            module_path=module_path,
            tier_dependencies=tier_dependencies,
            expose_mcp=expose_mcp,
            description=description,
        )
        
        cls._orchestrator_id = orchestrator_id
        cls._orchestrator_name = actual_name
        cls._tier_dependencies = tier_dependencies or set()
        cls._expose_mcp = expose_mcp
        
        return cls
    
    return decorator


def is_orchestrator(cls: Type) -> bool:
    """Check if a class is a registered orchestrator."""
    return hasattr(cls, '_orchestrator_id')


def get_orchestrator_id(cls: Type) -> Optional[str]:
    """Get orchestrator ID from a decorated class."""
    return getattr(cls, '_orchestrator_id', None)


def get_orchestrator_name(cls: Type) -> Optional[str]:
    """Get orchestrator name from a decorated class."""
    return getattr(cls, '_orchestrator_name', None)


# Backward compatibility alias
OrchestratorRegistryBridge = OrchestratorRegistry
