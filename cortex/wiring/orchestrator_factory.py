"""
OrchestratorFactory - Phase 9: Orchestrator Instantiation & Runtime Wiring

Parses wiring.yaml and instantiates orchestrators at runtime with dependency injection,
event subscription registration, and health verification.

Authority: CORTEX-SELF-IMPROVEMENT-SDLC.yaml Phase 9
Governance: CORE-008 (TDD-first), CORE-027 (Audit trail), CORE-035 (Single implementation)
"""

import importlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set

import yaml
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS FOR ORCHESTRATOR INSTANTIATION
# ============================================================================

@dataclass
class OrchestrationSpec:
    """Parsed orchestrator specification from wiring.yaml"""
    name: str
    module: str
    class_name: str
    tier: int
    priority: int
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    mcp_adapter: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    requires_params: Dict[str, Any] = field(default_factory=dict)
    event_subscriptions: List[str] = field(default_factory=list)
    event_emissions: List[str] = field(default_factory=list)


@dataclass
class OrchestrationContext:
    """Runtime context for orchestrator instantiation"""
    event_bus: Optional[Any] = None
    orchestrators: Dict[str, Any] = field(default_factory=dict)
    dependency_graph: Dict[str, Set[str]] = field(default_factory=dict)
    instantiation_order: List[str] = field(default_factory=list)
    health_checks: Dict[str, bool] = field(default_factory=dict)
    initialization_timestamp: Optional[datetime] = None


class WiringSpecification(BaseModel):
    """Represents the complete wiring.yaml specification"""
    version: str
    orchestrators: Dict[str, Any]
    analyzers: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
    validation: Optional[Dict[str, Any]] = None
    fallback_routes: Optional[List[Dict[str, Any]]] = None


# ============================================================================
# ORCHESTRATOR FACTORY
# ============================================================================

class OrchestratorFactory:
    """
    Factory for parsing wiring.yaml and instantiating orchestrators with:
    - Dependency resolution
    - Event subscription registration
    - Health check verification
    - Safe instantiation order (topological sort)
    """

    def __init__(self, wiring_file_path: str):
        """Initialize factory with wiring specification file"""
        self.wiring_file_path = wiring_file_path
        self.spec: Optional[WiringSpecification] = None
        self.orchestration_specs: Dict[str, OrchestrationSpec] = {}
        self.context = OrchestrationContext()
        self._load_wiring()

    def _load_wiring(self) -> None:
        """Load and parse wiring.yaml specification"""
        try:
            with open(self.wiring_file_path, 'r') as f:
                wiring_data = yaml.safe_load(f)
            self.spec = WiringSpecification(**wiring_data)
            logger.info(f"✅ Loaded wiring specification v{self.spec.version}")
        except Exception as e:
            logger.error(f"❌ Failed to load wiring: {e}")
            raise

    def parse_orchestrator_specs(self) -> None:
        """Parse all orchestrator specifications from wiring.yaml"""
        for tier, orchestrators in self.spec.orchestrators.items():
            if not isinstance(orchestrators, list):
                continue
            for orch_spec in orchestrators:
                spec = OrchestrationSpec(
                    name=orch_spec['name'],
                    module=orch_spec['module'],
                    class_name=orch_spec['class'],
                    tier=orch_spec.get('tier', 3),
                    priority=orch_spec.get('priority', 100),
                    dependencies=orch_spec.get('dependencies', []),
                    capabilities=orch_spec.get('capabilities', []),
                    mcp_adapter=orch_spec.get('mcp_adapter'),
                    metadata=orch_spec.get('metadata', {}),
                    requires_params=orch_spec.get('requires_params', {}),
                    event_subscriptions=orch_spec.get('event_subscriptions', []),
                    event_emissions=orch_spec.get('event_emissions', []),
                )
                self.orchestration_specs[spec.name] = spec
        logger.info(f"✅ Parsed {len(self.orchestration_specs)} orchestrator specifications")

    def resolve_dependencies(self) -> None:
        """
        Resolve orchestrator dependencies and build instantiation order
        using topological sort (Kahn's algorithm).
        """
        # Build dependency graph
        for name, spec in self.orchestration_specs.items():
            self.context.dependency_graph[name] = set(spec.dependencies)

        # Kahn's algorithm: topological sort
        in_degree = {name: len(deps) for name, deps in self.context.dependency_graph.items()}
        queue = [name for name in in_degree if in_degree[name] == 0]

        while queue:
            node = queue.pop(0)
            self.context.instantiation_order.append(node)

            # Find all nodes that depend on current node
            for name, deps in self.context.dependency_graph.items():
                if node in deps:
                    in_degree[name] -= 1
                    if in_degree[name] == 0:
                        queue.append(name)

        # Check for circular dependencies
        if len(self.context.instantiation_order) != len(self.orchestration_specs):
            logger.error("❌ Circular dependencies detected")
            raise ValueError("Circular dependencies in orchestrator wiring")

        logger.info(f"✅ Resolved dependencies: {self.context.instantiation_order}")

    def instantiate_orchestrators(self) -> None:
        """
        Instantiate orchestrators in dependency order with parameter injection.
        """
        for orch_name in self.context.instantiation_order:
            spec = self.orchestration_specs[orch_name]
            try:
                instance = self._instantiate_orchestrator(spec)
                self.context.orchestrators[orch_name] = instance
                logger.info(f"✅ Instantiated {orch_name} (tier={spec.tier}, priority={spec.priority})")
            except Exception as e:
                logger.error(f"❌ Failed to instantiate {orch_name}: {e}")
                raise

    def _instantiate_orchestrator(self, spec: OrchestrationSpec) -> Any:
        """Instantiate single orchestrator with dependency injection"""
        # Import module dynamically
        module = importlib.import_module(spec.module)
        orch_class = getattr(module, spec.class_name)

        # Collect dependencies
        kwargs = {}
        for dep_name in spec.dependencies:
            if dep_name in self.context.orchestrators:
                kwargs[self._to_param_name(dep_name)] = self.context.orchestrators[dep_name]

        # Inject required parameters
        for param_name, param_spec in spec.requires_params.items():
            if isinstance(param_spec, dict):
                if 'lazy_create' in param_spec and param_spec['lazy_create']:
                    # Lazy-create parameter
                    param_module = importlib.import_module(param_spec['source'])
                    param_class = getattr(param_module, param_name)
                    init_params = param_spec.get('init_params', {})
                    kwargs[param_name] = param_class(**init_params)

        # Instantiate with parameters
        instance = orch_class(**kwargs)
        return instance

    def register_event_subscriptions(self) -> None:
        """Register event subscriptions for all orchestrators with event bus"""
        if not self.context.event_bus:
            logger.warning("⚠️ Event bus not configured, skipping subscriptions")
            return

        for orch_name, instance in self.context.orchestrators.items():
            spec = self.orchestration_specs[orch_name]
            for event_type in spec.event_subscriptions:
                handler = self._create_event_handler(instance, event_type)
                self.context.event_bus.subscribe(event_type, handler)
                logger.info(f"✅ Registered {orch_name} → {event_type}")

    def _create_event_handler(self, instance: Any, event_type: str) -> Callable:
        """Create event handler for orchestrator"""
        def handler(event: Any) -> None:
            method_name = self._event_type_to_method(event_type)
            if hasattr(instance, method_name):
                getattr(instance, method_name)(event)
        return handler

    def verify_health(self) -> bool:
        """
        Verify all orchestrators are healthy via health_check method.
        Returns True if all healthy, False otherwise.
        """
        all_healthy = True
        for orch_name, instance in self.context.orchestrators.items():
            if hasattr(instance, 'health_check'):
                try:
                    result = instance.health_check()
                    self.context.health_checks[orch_name] = result
                    status = "✅" if result else "❌"
                    logger.info(f"{status} Health check: {orch_name}")
                    all_healthy = all_healthy and result
                except Exception as e:
                    logger.error(f"❌ Health check failed for {orch_name}: {e}")
                    self.context.health_checks[orch_name] = False
                    all_healthy = False

        return all_healthy

    def build(self) -> OrchestrationContext:
        """
        Complete orchestration build process:
        1. Parse specifications
        2. Resolve dependencies
        3. Instantiate orchestrators
        4. Register event subscriptions
        5. Verify health
        """
        self.parse_orchestrator_specs()
        self.resolve_dependencies()
        self.instantiate_orchestrators()
        self.register_event_subscriptions()
        all_healthy = self.verify_health()
        self.context.initialization_timestamp = datetime.now()

        if not all_healthy:
            logger.warning("⚠️ Some orchestrators failed health checks")

        return self.context

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    @staticmethod
    def _to_param_name(orchestrator_name: str) -> str:
        """Convert orchestrator name to parameter name (snake_case)"""
        return orchestrator_name.replace('-', '_').lower()

    @staticmethod
    def _event_type_to_method(event_type: str) -> str:
        """Convert EVENT_TYPE to on_event_type method name"""
        return f"on_{event_type.lower()}"


# ============================================================================
# ORCHESTRATION BOOTSTRAP
# ============================================================================

class OrchestrationBootstrap:
    """
    Bootstrap CORTEX orchestration system:
    - Initialize OrchestratorFactory
    - Build complete orchestration context
    - Expose orchestrators via context
    """

    def __init__(self, wiring_file_path: str):
        self.factory = OrchestratorFactory(wiring_file_path)
        self.context: Optional[OrchestrationContext] = None

    def bootstrap(self) -> OrchestrationContext:
        """Bootstrap complete orchestration system"""
        self.context = self.factory.build()
        logger.info(
            f"✅ Orchestration bootstrap complete: "
            f"{len(self.context.orchestrators)} orchestrators, "
            f"all healthy: {all(self.context.health_checks.values())}"
        )
        return self.context

    def get_orchestrator(self, name: str) -> Any:
        """Get orchestrator instance by name"""
        if not self.context:
            raise RuntimeError("Orchestration not bootstrapped yet")
        return self.context.orchestrators.get(name)

    def get_event_bus(self) -> Any:
        """Get configured event bus"""
        if not self.context:
            raise RuntimeError("Orchestration not bootstrapped yet")
        return self.context.event_bus


# ============================================================================
# MODULE-LEVEL SINGLETON
# ============================================================================

_bootstrap_instance: Optional[OrchestrationBootstrap] = None


def initialize_orchestration(wiring_file_path: str) -> OrchestrationContext:
    """Initialize orchestration system (module-level singleton)"""
    global _bootstrap_instance
    _bootstrap_instance = OrchestrationBootstrap(wiring_file_path)
    return _bootstrap_instance.bootstrap()


def get_orchestrator(name: str) -> Any:
    """Get orchestrator instance by name"""
    if not _bootstrap_instance:
        raise RuntimeError("Orchestration not initialized")
    return _bootstrap_instance.get_orchestrator(name)


def get_event_bus() -> Any:
    """Get event bus instance"""
    if not _bootstrap_instance:
        raise RuntimeError("Orchestration not initialized")
    return _bootstrap_instance.get_event_bus()
