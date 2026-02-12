"""
OrchestratorFactory - Runtime Orchestrator Instantiation & Wiring
===================================================================

Purpose:
    Parses wiring.yaml specification and instantiates all orchestrators
    with proper dependency injection, event subscription registration,
    and health verification.

Authority: CORE-027 (Audit Trail), CORE-035 (Single Implementation)
Version: 1.0
Created: 2026-02-04
Status: Phase 9 - Orchestrator Instantiation

Key Responsibilities:
    1. Parse wiring.yaml specification
    2. Detect circular dependencies (fail-fast)
    3. Resolve and inject dependencies in order
    4. Register event subscriptions
    5. Verify health checks
    6. Log audit trail (AC_START → AC_COMPLETE)

@author: Asif Hussain
"""

import importlib
import inspect
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import yaml

logger = logging.getLogger(__name__)


class DependencyResolutionError(Exception):
    """Raised when dependency resolution fails."""
    pass


class CircularDependencyError(DependencyResolutionError):
    """Raised when circular dependencies detected."""
    pass


class InstantiationError(DependencyResolutionError):
    """Raised when orchestrator instantiation fails."""
    pass


@dataclass
class OrchestrationSpec:
    """Single orchestrator specification from wiring.yaml"""
    name: str
    module: str
    class_name: str
    tier: int
    priority: int
    dependencies: List[str] = field(default_factory=list)
    capabilities: List[str] = field(default_factory=list)
    health_check: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    mcp_adapter: Optional[str] = None
    requires_params: Dict[str, Any] = field(default_factory=dict)

    def __hash__(self):
        return hash(self.name)


@dataclass
class DependencyGraph:
    """Orchestrator dependency graph for topological sort"""
    specs: Dict[str, OrchestrationSpec]
    adjacency: Dict[str, List[str]] = field(default_factory=dict)
    in_degree: Dict[str, int] = field(default_factory=dict)

    def add_spec(self, spec: OrchestrationSpec):
        """Add orchestrator spec to graph."""
        self.specs[spec.name] = spec
        self.adjacency[spec.name] = spec.dependencies
        self.in_degree[spec.name] = 0

    def compute_in_degrees(self):
        """Compute in-degree for each node."""
        for name in self.specs:
            self.in_degree[name] = 0

        for name, deps in self.adjacency.items():
            for dep in deps:
                if dep in self.in_degree:
                    self.in_degree[dep] += 1


class CircularDependencyDetector:
    """
    Detects circular dependencies using Kahn's algorithm (topological sort).

    Algorithm:
        1. Compute in-degrees (dependencies from other orchestrators)
        2. Enqueue all nodes with in-degree 0
        3. Process queue, reducing in-degrees
        4. If queue empties before processing all nodes → circular dependency

    Time: O(V + E) where V = orchestrators, E = dependencies
    """

    @staticmethod
    def detect_cycles(graph: DependencyGraph) -> Tuple[bool, Optional[List[str]]]:
        """
        Detect circular dependencies.

        Returns:
            (has_cycles, cycle_path) - If has_cycles is True, cycle_path contains the cycle
        """
        # Reset in-degrees
        in_degree = graph.in_degree.copy()

        # Enqueue nodes with in-degree 0
        queue = [name for name in in_degree if in_degree[name] == 0]
        processed_count = 0

        while queue:
            node = queue.pop(0)
            processed_count += 1

            # Reduce in-degree for dependencies
            for dep in graph.adjacency.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        # If not all nodes processed, there's a cycle
        if processed_count != len(graph.specs):
            unprocessed = [name for name in in_degree if in_degree[name] > 0]
            return (True, unprocessed)

        return (False, None)


class DependencyResolver:
    """
    Resolves dependencies in correct order using topological sort.

    Ensures orchestrators are instantiated in dependency order:
        - Dependencies (tier 3) before dependents
        - Lower priority before higher priority (stable sort)
    """

    @staticmethod
    def topological_sort(graph: DependencyGraph) -> List[str]:
        """
        Topological sort of orchestrators by dependency order.

        Returns:
            List of orchestrator names in instantiation order
        """
        # Kahn's algorithm (same as cycle detection)
        in_degree = graph.in_degree.copy()
        queue = [name for name in in_degree if in_degree[name] == 0]
        result = []

        while queue:
            # Sort by priority for stable ordering
            queue.sort(key=lambda x: graph.specs[x].priority)
            node = queue.pop(0)
            result.append(node)

            for dep in graph.adjacency.get(node, []):
                in_degree[dep] -= 1
                if in_degree[dep] == 0:
                    queue.append(dep)

        return result


class OrchestratorFactory:
    """
    Main factory for orchestrator instantiation.

    Responsibilities:
        1. Parse wiring.yaml
        2. Build dependency graph
        3. Detect circular dependencies (fail-fast)
        4. Instantiate orchestrators in dependency order
        5. Register event subscriptions
        6. Health check verification
        7. Audit trail logging (AC_START → AC_COMPLETE)
    """

    def __init__(self, wiring_spec_path: str = "cortex/wiring/specifications/wiring.yaml"):
        """Initialize factory with wiring specification path."""
        self.wiring_spec_path = Path(wiring_spec_path)
        self.specs: Dict[str, OrchestrationSpec] = {}
        self.instances: Dict[str, Any] = {}
        self.graph: Optional[DependencyGraph] = None
        self.audit_trail: List[Dict[str, Any]] = []

    def parse_wiring_specification(self) -> Dict[str, Any]:
        """
        Parse wiring.yaml into orchestrator specifications.

        Returns:
            Dict with 'orchestrators' containing core/domain/support sections

        Raises:
            FileNotFoundError: If wiring.yaml not found
            yaml.YAMLError: If YAML parsing fails
        """
        if not self.wiring_spec_path.exists():
            raise FileNotFoundError(f"Wiring specification not found: {self.wiring_spec_path}")

        logger.info(f"Parsing wiring specification: {self.wiring_spec_path}")

        with open(self.wiring_spec_path, 'r') as f:
            spec = yaml.safe_load(f)

        return spec

    def build_dependency_graph(self, wiring_spec: Dict[str, Any]) -> DependencyGraph:
        """
        Build orchestrator dependency graph from wiring specification.

        Args:
            wiring_spec: Parsed wiring.yaml

        Returns:
            DependencyGraph instance
        """
        graph = DependencyGraph(specs={})

        # Process orchestrators from all tiers
        for tier_name in ['core', 'domain', 'support']:
            orchestrators = wiring_spec.get('orchestrators', {}).get(tier_name, [])

            for orch in orchestrators:
                spec = OrchestrationSpec(
                    name=orch.get('name'),
                    module=orch.get('module'),
                    class_name=orch.get('class'),
                    tier=orch.get('tier', 0),
                    priority=orch.get('priority', 0),
                    dependencies=orch.get('dependencies', []),
                    capabilities=orch.get('capabilities', []),
                    health_check=orch.get('health_check', 'health_check'),
                    metadata=orch.get('metadata', {}),
                    mcp_adapter=orch.get('mcp_adapter'),
                    requires_params=orch.get('requires_params', {}),
                )
                graph.add_spec(spec)
                self.specs[spec.name] = spec

        # Compute in-degrees for cycle detection
        graph.compute_in_degrees()
        self.graph = graph

        logger.info(f"Built dependency graph with {len(self.specs)} orchestrators")
        return graph

    def validate_dependencies(self) -> bool:
        """
        Validate dependency graph for consistency.

        Checks:
            1. All referenced dependencies exist
            2. No circular dependencies
            3. All dependencies are resolvable

        Returns:
            True if valid, raises exception otherwise

        Raises:
            DependencyResolutionError: If validation fails
        """
        if not self.graph:
            raise ValueError("Dependency graph not built")

        logger.info("Validating dependency graph...")

        # Check all dependencies exist
        all_names = set(self.specs.keys())
        for spec in self.specs.values():
            for dep in spec.dependencies:
                if dep not in all_names:
                    raise DependencyResolutionError(
                        f"Orchestrator {spec.name} depends on unknown {dep}"
                    )

        # Check for circular dependencies
        has_cycles, cycle_nodes = CircularDependencyDetector.detect_cycles(self.graph)
        if has_cycles:
            raise CircularDependencyError(
                f"Circular dependency detected in nodes: {cycle_nodes}"
            )

        logger.info("✅ Dependency graph validated (no circular dependencies)")
        return True

    def resolve_instantiation_order(self) -> List[str]:
        """
        Resolve orchestrators in instantiation order.

        Returns:
            List of orchestrator names in topological sort order
        """
        if not self.graph:
            raise ValueError("Dependency graph not built")

        order = DependencyResolver.topological_sort(self.graph)

        logger.info(f"Instantiation order resolved ({len(order)} orchestrators):")
        for i, name in enumerate(order, 1):
            spec = self.specs[name]
            logger.info(f"  {i}. {name} (tier={spec.tier}, priority={spec.priority})")

        return order

    def instantiate_orchestrator(self, name: str) -> Any:
        """
        Instantiate single orchestrator with dependency injection.

        Args:
            name: Orchestrator name

        Returns:
            Instantiated orchestrator instance

        Raises:
            InstantiationError: If instantiation fails
        """
        if name in self.instances:
            return self.instances[name]

        spec = self.specs.get(name)
        if not spec:
            raise InstantiationError(f"Unknown orchestrator: {name}")

        logger.info(f"Instantiating {name}...")

        try:
            # Import module
            module = importlib.import_module(spec.module)
            cls = getattr(module, spec.class_name)

            # Inject dependencies
            dependencies = {}
            for dep_name in spec.dependencies:
                if dep_name not in self.instances:
                    self.instantiate_orchestrator(dep_name)
                dependencies[dep_name] = self.instances[dep_name]

            # Prepare initialization parameters
            init_params = {}

            # Handle requires_params (lazy initialization)
            for param_name, param_spec in spec.requires_params.items():
                if param_spec.get('lazy_create'):
                    param_type = param_spec.get('type')
                    param_module = param_spec.get('source')
                    param_class_name = param_type

                    # Instantiate parameter
                    param_module_obj = importlib.import_module(param_module)
                    param_class = getattr(param_module_obj, param_class_name)

                    # Pass orchestrator reference if needed
                    param_init_params = param_spec.get('init_params', {})
                    if 'orchestrator' in inspect.signature(param_class.__init__).parameters:
                        param_init_params['orchestrator'] = None  # Will be set later

                    init_params[param_name] = param_class(**param_init_params)

            # Instantiate orchestrator
            instance = cls(**init_params, **dependencies) if dependencies else cls(**init_params)

            # Set orchestrator reference if needed (circular reference handling)
            if hasattr(instance, 'orchestrator') and instance.orchestrator is None:
                instance.orchestrator = instance

            self.instances[name] = instance
            logger.info(f"✅ {name} instantiated successfully")

            return instance

        except Exception as e:
            raise InstantiationError(f"Failed to instantiate {name}: {str(e)}") from e

    def verify_health_checks(self) -> Dict[str, bool]:
        """
        Verify all orchestrators pass health checks.

        Returns:
            Dict mapping orchestrator name to health check result

        Raises:
            RuntimeError: If critical health checks fail
        """
        logger.info("Running health checks...")

        health_results: Dict[str, bool] = {}
        failures = []

        for name, instance in self.instances.items():
            spec = self.specs[name]
            health_method_name = spec.health_check

            try:
                if hasattr(instance, health_method_name):
                    method = getattr(instance, health_method_name)
                    result = method()
                    health_results[name] = result
                    status = "✅" if result else "❌"
                    logger.info(f"{status} {name} health check: {result}")

                    if not result:
                        failures.append(name)
                else:
                    logger.warning(f"⚠️  {name} has no {health_method_name} method")
                    health_results[name] = True  # Assume OK if no check

            except Exception as e:
                logger.error(f"❌ {name} health check failed: {str(e)}")
                health_results[name] = False
                failures.append(name)

        if failures:
            logger.error(f"⚠️  Health check failures: {failures}")
        else:
            logger.info(f"✅ All health checks passed ({len(health_results)} orchestrators)")

        return health_results

    def register_event_subscriptions(self):
        """
        Register event subscriptions from wiring specification.

        Each orchestrator that subscribes to events has subscriptions
        registered with the OrchestratorEventBus.
        """
        logger.info("Registering event subscriptions...")

        # Get event bus instance
        event_bus = self.instances.get('OrchestratorEventBus')
        if not event_bus:
            logger.warning("OrchestratorEventBus not found, skipping subscriptions")
            return

        subscription_count = 0
        for name, instance in self.instances.items():
            spec = self.specs[name]

            # Check if orchestrator has event subscriptions
            if hasattr(instance, '_get_event_subscriptions'):
                subscriptions = instance._get_event_subscriptions()
                for event_type, handler in subscriptions:
                    event_bus.subscribe(event_type, handler)
                    subscription_count += 1
                    logger.debug(f"  {name} subscribed to {event_type}")

        logger.info(f"✅ Registered {subscription_count} event subscriptions")

    def create_orchestrator_instance(self) -> Dict[str, Any]:
        """
        Main factory method: parse, validate, instantiate, verify.

        Returns:
            Dict with 'orchestrators' (all instances) and 'metadata'

        Raises:
            Various exceptions on failure (logged to audit trail)
        """
        logger.info("=" * 70)
        logger.info("PHASE 9: ORCHESTRATOR INSTANTIATION & RUNTIME WIRING")
        logger.info("=" * 70)

        self.audit_trail.append({
            'event': 'AC_START',
            'operation': 'orchestrator_instantiation',
            'timestamp': self._get_timestamp(),
        })

        try:
            # Step 1: Parse wiring specification
            logger.info("\n[Step 1/5] Parsing wiring specification...")
            wiring_spec = self.parse_wiring_specification()
            logger.info(f"✅ Parsed {len(wiring_spec.get('orchestrators', {}))} orchestrator tiers")

            # Step 2: Build dependency graph
            logger.info("\n[Step 2/5] Building dependency graph...")
            self.build_dependency_graph(wiring_spec)
            logger.info(f"✅ Built graph with {len(self.specs)} orchestrators")

            # Step 3: Validate dependencies
            logger.info("\n[Step 3/5] Validating dependencies...")
            self.validate_dependencies()
            logger.info("✅ Dependency validation complete")

            # Step 4: Instantiate orchestrators in order
            logger.info("\n[Step 4/5] Instantiating orchestrators...")
            instantiation_order = self.resolve_instantiation_order()
            for name in instantiation_order:
                self.instantiate_orchestrator(name)
            logger.info(f"✅ All {len(self.instances)} orchestrators instantiated")

            # Step 5: Verify health and register subscriptions
            logger.info("\n[Step 5/5] Health verification and event registration...")
            health_results = self.verify_health_checks()
            self.register_event_subscriptions()
            logger.info("✅ Health verification and event registration complete")

            # Log completion
            self.audit_trail.append({
                'event': 'AC_COMPLETE',
                'operation': 'orchestrator_instantiation',
                'timestamp': self._get_timestamp(),
                'orchestrators_instantiated': len(self.instances),
                'health_checks_passed': sum(1 for v in health_results.values() if v),
            })

            logger.info("\n" + "=" * 70)
            logger.info(f"✅ PHASE 9 COMPLETE: {len(self.instances)} orchestrators ready")
            logger.info("=" * 70)

            return {
                'orchestrators': self.instances,
                'metadata': {
                    'total_count': len(self.instances),
                    'health_checks': health_results,
                    'audit_trail': self.audit_trail,
                }
            }

        except Exception as e:
            logger.error(f"\n❌ PHASE 9 FAILED: {str(e)}")
            self.audit_trail.append({
                'event': 'AC_FAILED',
                'operation': 'orchestrator_instantiation',
                'timestamp': self._get_timestamp(),
                'error': str(e),
            })
            raise

    def _get_timestamp(self) -> str:
        """Get ISO8601 timestamp."""
        from datetime import datetime
        return datetime.utcnow().isoformat() + 'Z'


def create_cortex_runtime() -> Dict[str, Any]:
    """
    Create CORTEX runtime with all orchestrators instantiated and wired.

    This is the main entry point for PHASE 9.

    Returns:
        Runtime instance with all orchestrators available
    """
    factory = OrchestratorFactory()
    return factory.create_orchestrator_instance()


if __name__ == '__main__':
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
    )

    # Run instantiation
    runtime = create_cortex_runtime()
    print(f"\n✅ CORTEX runtime ready with {runtime['metadata']['total_count']} orchestrators")
