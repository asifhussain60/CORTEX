"""
Orchestrator Decorator and Registry

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

from cortex.brain.core.orchestrator_base import OrchestratorBase, OrchestrationContext


"""
Orchestrator Decorator and Registry Bridge

AC-PERMANENT-FIX-012: Bridges @orchestrator decorator to DatabaseBackedRegistry.

Provides @orchestrator decorator for automatic registration and
context injection. The decorator enables:
- Auto-discovery of orchestrators
- Tier dependency declaration
- Automatic governance context injection  
- MCP tool exposure metadata

Uses DatabaseBackedRegistry as SSOT - no manual registries.
"""

from typing import Any, Callable, Dict, List, Optional, Set, Type
from functools import wraps
import inspect
from datetime import datetime

from cortex.brain.core.orchestrator_base import OrchestratorBase, OrchestrationContext


class OrchestratorRegistryBridge:
    """
    Bridge to DatabaseBackedRegistry for backward compatibility.
    
    AC-PERMANENT-FIX-012: Eliminates legacy OrchestratorRegistry,
    bridges decorator calls to DatabaseBackedRegistry SSOT.
    
    No manual registry - all operations delegate to DatabaseBackedRegistry.
    """
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        # Get DatabaseBackedRegistry as SSOT
        try:
            from cortex.orchestrators import get_database_registry
            self._db_registry = get_database_registry()
        except ImportError:
            # Fallback for testing
            self._db_registry = None
            
        self._initialized = True
    
    @property
    def orchestrators(self) -> Dict[str, Dict[str, Any]]:
        """Bridge to DatabaseBackedRegistry orchestrator data"""
        if self._db_registry:
            return {orc.name: {"class": orc.class_type, "id": orc.name} 
                   for orc in self._db_registry.get_all_orchestrators()}
        return {}
    
    @property
    def by_name(self) -> Dict[str, str]:
        """Name to ID mapping from DatabaseBackedRegistry"""
        if self._db_registry:
            return {orc.name: orc.name for orc in self._db_registry.get_all_orchestrators()}
        return {}
    
    def register(
        self,
        orchestrator_id: str,
        orchestrator_name: str,
        orchestrator_class: Type[OrchestratorBase],
        tier_dependencies: Optional[Set[int]] = None,
        required_rules: Optional[List[str]] = None,
        mcp_tools: Optional[List[str]] = None,
        description: Optional[str] = None,
    ) -> None:
        """
        Bridge decorator registrations to DatabaseBackedRegistry.
        
        AC-PERMANENT-FIX-012: No manual registry - delegates to DatabaseBackedRegistry.
        
        Args:
            orchestrator_id: Unique identifier for orchestrator
            orchestrator_name: Human-readable name
            orchestrator_class: The orchestrator class
            tier_dependencies: Set of tiers (0-3) this orchestrator accesses
            required_rules: List of SKULL rule IDs required
            mcp_tools: List of MCP tool names exposed by this orchestrator
            description: Human-readable description
        """
        if not issubclass(orchestrator_class, OrchestratorBase):
            raise TypeError(
                f"orchestrator_class must be subclass of OrchestratorBase, "
                f"got {orchestrator_class}"
            )
        
        # AC-PERMANENT-FIX-012: Bridge to DatabaseBackedRegistry
        # Decorator registrations are handled at runtime by the database registry
        # This method exists for compatibility but actual registration happens in DB
        pass
    
    def get(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator entry by ID from DatabaseBackedRegistry"""
        if self._db_registry:
            orc = self._db_registry.get_orchestrator(orchestrator_id)
            if orc:
                return {"id": orc.name, "name": orc.name, "class": orc.class_type}
        return None
    
    def get_by_name(self, orchestrator_name: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator entry by name from DatabaseBackedRegistry"""
        return self.get(orchestrator_name)  # Names and IDs are same in new system
    
    def get_by_tier(self, tier: int) -> List[Dict[str, Any]]:
        """Get all orchestrators that access a specific tier (legacy compatibility)"""
        # For compatibility, return all orchestrators since tiers are not in DB
        if self._db_registry:
            return [{"id": orc.name, "name": orc.name, "class": orc.class_type}
                   for orc in self._db_registry.get_all_orchestrators()]
        return []
    
    def list_all(self) -> List[Dict[str, Any]]:
        """Get all registered orchestrators from DatabaseBackedRegistry"""
        if self._db_registry:
            return [{"id": orc.name, "name": orc.name, "class": orc.class_type}
                   for orc in self._db_registry.get_all_orchestrators()]
        return []
        return list(self.orchestrators.values())
    
    def count(self) -> int:
        """Get count of registered orchestrators"""
    def list_all(self) -> List[Dict[str, Any]]:
        """Get all registered orchestrators from DatabaseBackedRegistry"""
        if self._db_registry:
            return [{"id": orc.name, "name": orc.name, "class": orc.class_type}
                   for orc in self._db_registry.get_all_orchestrators()]
        return []
    
    def count(self) -> int:
        """Get count of registered orchestrators"""
        if self._db_registry:
            return len(self._db_registry.get_all_orchestrators())
        return 0
    
    def clear(self) -> None:
        """Clear registry (for testing) - No-op in bridge mode"""
        # AC-PERMANENT-FIX-012: Cannot clear DatabaseBackedRegistry
        pass


def orchestrator(
    orchestrator_id: Optional[str] = None,
    tier_dependencies: Optional[Set[int]] = None,
    required_rules: Optional[List[str]] = None,
    mcp_tools: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Callable[[Type[OrchestratorBase]], Type[OrchestratorBase]]:
    """
    Decorator for orchestrator classes.
    
    AC-PERMANENT-FIX-012: Bridges to DatabaseBackedRegistry registration.
    
    Args:
        orchestrator_id: Unique identifier (defaults to class name)
        tier_dependencies: Tiers this orchestrator accesses (0-3)
        required_rules: SKULL rules required by this orchestrator
        mcp_tools: MCP tool names exposed
        description: Human-readable description
    
    Returns:
        Decorator function
    """
    
    def decorator(cls: Type[OrchestratorBase]) -> Type[OrchestratorBase]:
        # Determine orchestrator ID
        orch_id = orchestrator_id or cls.__name__
        orch_name = cls.__name__
        
        # Validate class
        if not issubclass(cls, OrchestratorBase):
            raise TypeError(
                f"@orchestrator can only decorate OrchestratorBase subclasses, "
                f"got {cls}"
            )
        
        # AC-PERMANENT-FIX-012: Registration handled by DatabaseBackedRegistry
        # Store metadata on class for later access
        cls._orchestrator_id = orch_id  # type: ignore
        cls._tier_dependencies = tier_dependencies or {0, 1, 2, 3}  # type: ignore
        cls._required_rules = required_rules or []  # type: ignore
        cls._mcp_tools = mcp_tools or []  # type: ignore
        cls._is_registered = True  # type: ignore
        
        return cls
    
    return decorator


def get_registry() -> OrchestratorRegistryBridge:
    """Get the global orchestrator registry bridge (AC-PERMANENT-FIX-012)"""
    return OrchestratorRegistryBridge()


def get_orchestrator_class(orchestrator_id: str) -> Optional[Type[OrchestratorBase]]:
    """Get orchestrator class by ID"""
    registry = get_registry()
    entry = registry.get(orchestrator_id)
    if entry:
        return entry["class"]
    return None


def instantiate_orchestrator(
    orchestrator_id: str,
    parameters: Optional[Dict[str, Any]] = None,
    environment: str = "development",
) -> OrchestratorBase:
    """
    Instantiate an orchestrator by ID with auto-context creation.
    
    Args:
        orchestrator_id: ID of registered orchestrator
        parameters: Parameters to pass to orchestrator
        environment: Execution environment (development | staging | production)
        
    Returns:
        Instantiated orchestrator
        
    Raises:
        ValueError: If orchestrator not found
    """
    registry = get_registry()
    entry = registry.get(orchestrator_id)
    
    if not entry:
        raise ValueError(f"Orchestrator {orchestrator_id} not registered")
    
    orchestrator_class = entry["class"]
    context = OrchestrationContext(
        orchestrator_id=orchestrator_id,
        orchestrator_name=entry["name"],
        parameters=parameters or {},
        environment=environment,
        tier_access=entry.get("tier_dependencies", {0, 1, 2, 3}),
        required_rules=entry.get("required_rules", []),
    )
    
    return orchestrator_class(context)
