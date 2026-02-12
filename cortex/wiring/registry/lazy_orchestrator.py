"""
Lazy Orchestrator Proxy - Load orchestrators on first access.

Authority: cortex-registry/_cortex-master/phases/completed/2025/ (Phase 3)
Rule: CORE-035 (Single Canonical Implementation)
"""

import importlib
import logging
from typing import Any, Callable, Dict, Optional

logger = logging.getLogger(__name__)


class LazyOrchestrator:
    """
    Proxy that delays orchestrator instantiation until first access.

    This enables:
    - Fast startup (no heavy initialization)
    - Circular dependency resolution
    - Memory efficiency (only load what's used)

    Example:
        >>> lazy_orch = LazyOrchestrator("TDDOrchestrator", "cortex.orchestrators.core.tdd_orchestrator", "TDDOrchestrator")
        >>> # Not yet loaded
        >>> orch = lazy_orch.instance()  # Loads now
        >>> result = orch.generate_tests(...)
    """

    def __init__(
        self,
        name: str,
        module_path: str,
        class_name: str,
        dependencies: Optional[list] = None,
        required_params: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Initialize lazy orchestrator proxy.

        Args:
            name: Orchestrator name (e.g., "TDDOrchestrator")
            module_path: Python module path (e.g., "cortex.orchestrators.core.tdd_orchestrator")
            class_name: Class name within module (e.g., "TDDOrchestrator")
            dependencies: List of dependency orchestrator names
            required_params: Dict of required constructor parameters
        """
        self.name = name
        self.module_path = module_path
        self.class_name = class_name
        self.dependencies = dependencies or []
        self.required_params = required_params or {}

        self._instance: Optional[Any] = None
        self._loading = False  # Detect circular dependency attempts

    def instance(self, registry: Optional[Any] = None) -> Any:
        """
        Get or create the orchestrator instance.

        Args:
            registry: Registry to resolve dependencies (optional)

        Returns:
            Initialized orchestrator instance

        Raises:
            ImportError: If module/class not found
            RuntimeError: If circular dependency detected
        """
        if self._instance is not None:
            return self._instance

        if self._loading:
            raise RuntimeError(
                f"Circular dependency detected: {self.name} is already being loaded. "
                f"Check wiring.yaml for circular references."
            )

        try:
            self._loading = True
            logger.debug(f"Loading orchestrator: {self.name} from {self.module_path}")

            # Import module
            module = importlib.import_module(self.module_path)

            # Get class
            if not hasattr(module, self.class_name):
                raise ImportError(
                    f"Class {self.class_name} not found in {self.module_path}"
                )

            orch_class = getattr(module, self.class_name)

            # Prepare constructor kwargs
            kwargs = self._resolve_params(registry)

            # Instantiate
            self._instance = orch_class(**kwargs)

            logger.info(f"✅ Loaded orchestrator: {self.name}")
            return self._instance

        except Exception as e:
            logger.error(f"❌ Failed to load orchestrator {self.name}: {e}")
            raise
        finally:
            self._loading = False

    def _resolve_params(self, registry: Optional[Any]) -> Dict[str, Any]:
        """
        Resolve required constructor parameters.

        Args:
            registry: Registry to resolve dependencies

        Returns:
            Dict of resolved parameters
        """
        kwargs: Dict[str, Any] = {}

        for param_name, param_spec in self.required_params.items():
            if param_spec.get('source') == 'wiring_registry' and registry:
                # Inject all orchestrators from registry
                if param_spec.get('inject_all'):
                    kwargs[param_name] = registry.get_all_orchestrators()
            elif param_spec.get('lazy_create'):
                # Create param on-the-fly
                param_module = param_spec.get('source')
                param_type = param_spec.get('type')
                if param_module and param_type:
                    try:
                        mod = importlib.import_module(param_module)
                        param_class = getattr(mod, param_type)
                        kwargs[param_name] = param_class()
                    except Exception as e:
                        logger.warning(f"Failed to lazy-create {param_type}: {e}")

        return kwargs

    def is_loaded(self) -> bool:
        """Check if orchestrator has been loaded."""
        return self._instance is not None

    def __repr__(self) -> str:
        """String representation."""
        status = "loaded" if self._instance else "lazy"
        return f"<LazyOrchestrator({self.name}, {status})>"

    def __getattr__(self, name: str) -> Any:
        """
        Forward attribute access to the real instance.

        This enables transparent lazy loading:
            lazy_orch.some_method()  # Loads instance automatically
        """
        if name.startswith('_') or name in ['name', 'module_path', 'class_name', 'dependencies', 'required_params']:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

        # Load instance and forward attribute access
        instance = self.instance()
        return getattr(instance, name)
