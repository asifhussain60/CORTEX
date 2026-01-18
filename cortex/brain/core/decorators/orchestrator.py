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


class OrchestratorRegistry:
    """
    Central registry for all orchestrators.
    
    Maintains a mapping of:
    - orchestrator_id → orchestrator class
    - orchestrator_name → orchestrator class
    - tier → [orchestrators that access this tier]
    
    This enables dynamic discovery and dependency tracking.
    """
    
    _instance = None  # Singleton
    
    def __new__(cls):
        """Ensure only one instance exists"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize registry"""
        if self._initialized:
            return
        
        self.orchestrators: Dict[str, Dict[str, Any]] = {}
        self.by_name: Dict[str, str] = {}  # name → id mapping
        self.by_tier: Dict[int, List[str]] = {0: [], 1: [], 2: [], 3: []}
        self.registration_log: List[Dict[str, Any]] = []
        self._lock = False  # Protection against double registration
        self._initialized = True
    
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
        Register an orchestrator in the registry.
        
        Args:
            orchestrator_id: Unique identifier for orchestrator
            orchestrator_name: Human-readable name
            orchestrator_class: The orchestrator class
            tier_dependencies: Set of tiers (0-3) this orchestrator accesses
            required_rules: List of SKULL rule IDs required
            mcp_tools: List of MCP tool names exposed by this orchestrator
            description: Human-readable description
            
        Raises:
            ValueError: If orchestrator_id already registered
            TypeError: If orchestrator_class not a subclass of OrchestratorBase
        """
        if not issubclass(orchestrator_class, OrchestratorBase):
            raise TypeError(
                f"orchestrator_class must be subclass of OrchestratorBase, "
                f"got {orchestrator_class}"
            )
        
        if orchestrator_id in self.orchestrators:
            raise ValueError(f"Orchestrator {orchestrator_id} already registered")
        
        if orchestrator_name in self.by_name:
            raise ValueError(f"Orchestrator name {orchestrator_name} already registered")
        
        # Register orchestrator
        if tier_dependencies is None:
            tier_dependencies = {0, 1, 2, 3}  # Default: all tiers
        
        entry = {
            "id": orchestrator_id,
            "name": orchestrator_name,
            "class": orchestrator_class,
            "tier_dependencies": tier_dependencies,
            "required_rules": required_rules or [],
            "mcp_tools": mcp_tools or [],
            "description": description or "",
            "registered_at": datetime.utcnow().isoformat(),
        }
        
        self.orchestrators[orchestrator_id] = entry
        self.by_name[orchestrator_name] = orchestrator_id
        
        # Register tier dependencies
        for tier in tier_dependencies:
            if tier not in self.by_tier:
                self.by_tier[tier] = []
            self.by_tier[tier].append(orchestrator_id)
        
        # Log registration
        self.registration_log.append({
            "action": "register",
            "orchestrator_id": orchestrator_id,
            "timestamp": datetime.utcnow().isoformat(),
        })
    
    def get(self, orchestrator_id: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator entry by ID"""
        return self.orchestrators.get(orchestrator_id)
    
    def get_by_name(self, orchestrator_name: str) -> Optional[Dict[str, Any]]:
        """Get orchestrator entry by name"""
        orch_id = self.by_name.get(orchestrator_name)
        if orch_id:
            return self.orchestrators.get(orch_id)
        return None
    
    def get_by_tier(self, tier: int) -> List[Dict[str, Any]]:
        """Get all orchestrators that access a specific tier"""
        orch_ids = self.by_tier.get(tier, [])
        return [self.orchestrators[oid] for oid in orch_ids]
    
    def list_all(self) -> List[Dict[str, Any]]:
        """Get all registered orchestrators"""
        return list(self.orchestrators.values())
    
    def count(self) -> int:
        """Get count of registered orchestrators"""
        return len(self.orchestrators)
    
    def clear(self) -> None:
        """Clear registry (for testing)"""
        self.orchestrators.clear()
        self.by_name.clear()
        self.by_tier = {0: [], 1: [], 2: [], 3: []}
        self.registration_log.clear()


def orchestrator(
    orchestrator_id: Optional[str] = None,
    tier_dependencies: Optional[Set[int]] = None,
    required_rules: Optional[List[str]] = None,
    mcp_tools: Optional[List[str]] = None,
    description: Optional[str] = None,
) -> Callable[[Type[OrchestratorBase]], Type[OrchestratorBase]]:
    """
    Decorator for orchestrator classes.
    
    Automatically registers orchestrator in global registry and injects
    governance context on instantiation.
    
    Usage:
        @orchestrator(
            orchestrator_id="my-orch-001",
            tier_dependencies={0, 1},
            required_rules=["SKULL-001", "SKULL-002"]
        )
        class MyOrchestrator(OrchestratorBase):
            def execute(self):
                pass
    
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
        
        # Register in global registry
        registry = OrchestratorRegistry()
        registry.register(
            orchestrator_id=orch_id,
            orchestrator_name=orch_name,
            orchestrator_class=cls,
            tier_dependencies=tier_dependencies,
            required_rules=required_rules,
            mcp_tools=mcp_tools,
            description=description,
        )
        
        # Store metadata on class for later access
        cls._orchestrator_id = orch_id  # type: ignore
        cls._tier_dependencies = tier_dependencies or {0, 1, 2, 3}  # type: ignore
        cls._required_rules = required_rules or []  # type: ignore
        cls._mcp_tools = mcp_tools or []  # type: ignore
        cls._is_registered = True  # type: ignore
        
        # Wrap __init__ to inject context
        original_init = cls.__init__
        
        @wraps(original_init)
        def wrapped_init(self, context: OrchestrationContext):
            """Wrapped init that injects tier dependencies into context"""
            # Inject tier dependencies into context if not already set
            if not hasattr(context, 'tier_access') or context.tier_access == {0, 1, 2, 3}:
                context.tier_access = cls._tier_dependencies  # type: ignore
            
            # Inject required rules into context
            if not hasattr(context, 'required_rules') or not context.required_rules:
                context.required_rules = cls._required_rules  # type: ignore
            
            # Call original init
            original_init(self, context)
        
        cls.__init__ = wrapped_init  # type: ignore
        
        return cls
    
    return decorator


def get_registry() -> OrchestratorRegistry:
    """Get the global orchestrator registry"""
    return OrchestratorRegistry()


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
