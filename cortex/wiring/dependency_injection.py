"""
Dependency Injection System for Orchestrators - Phase 9

Provides type-safe dependency injection for orchestrator parameters with:
- Parameter validation
- Circular dependency detection
- Lazy initialization
- Parameter override capability
"""

import logging
from typing import Any, Callable, Dict, Optional, Type, TypeVar, get_type_hints
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

T = TypeVar('T')


# ============================================================================
# DEPENDENCY INJECTION CONTAINER
# ============================================================================

@dataclass
class DIParameter:
    """Represents an injectable parameter"""
    name: str
    param_type: Type
    required: bool = True
    default: Any = None
    factory: Optional[Callable[[], Any]] = None
    lazy: bool = False


class DIContainer:
    """
    Dependency injection container for orchestrator parameters.
    Manages instance creation, lazy initialization, and parameter override.
    """

    def __init__(self):
        self.singletons: Dict[str, Any] = {}
        self.factories: Dict[str, Callable[[], Any]] = {}
        self.parameters: Dict[str, DIParameter] = {}
        self._initializing: Set[str] = set()

    def register_singleton(self, name: str, instance: Any) -> None:
        """Register singleton instance"""
        self.singletons[name] = instance
        logger.debug(f"Registered singleton: {name}")

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register factory function for lazy creation"""
        self.factories[name] = factory
        logger.debug(f"Registered factory: {name}")

    def register_parameter(self, param: DIParameter) -> None:
        """Register injectable parameter"""
        self.parameters[param.name] = param
        logger.debug(f"Registered parameter: {param.name} ({param.param_type.__name__})")

    def get_instance(self, name: str) -> Any:
        """Get or create instance by name"""
        # Check singletons first
        if name in self.singletons:
            return self.singletons[name]

        # Detect circular dependencies
        if name in self._initializing:
            raise ValueError(f"Circular dependency detected: {name}")

        # Create via factory
        if name in self.factories:
            self._initializing.add(name)
            try:
                instance = self.factories[name]()
                self.singletons[name] = instance  # Cache as singleton
                logger.debug(f"Created singleton from factory: {name}")
                return instance
            finally:
                self._initializing.discard(name)

        # Check parameters
        if name in self.parameters:
            param = self.parameters[name]
            if param.default is not None:
                return param.default
            if not param.required:
                return None

        raise ValueError(f"Dependency not registered: {name}")

    def inject(self, target_class: Type[T], **overrides: Any) -> T:
        """
        Inject dependencies into class constructor.
        Returns: Instance of target_class with dependencies injected.
        """
        # Get type hints for constructor
        hints = get_type_hints(target_class.__init__)
        kwargs = {}

        for param_name, param_type in hints.items():
            if param_name == 'return' or param_name == 'self':
                continue

            # Check for override
            if param_name in overrides:
                kwargs[param_name] = overrides[param_name]
            # Check if registered
            elif param_name in self.singletons or param_name in self.factories:
                kwargs[param_name] = self.get_instance(param_name)
            # Check parameters
            elif param_name in self.parameters:
                param = self.parameters[param_name]
                if param.required:
                    kwargs[param_name] = self.get_instance(param_name)
                elif param.default is not None:
                    kwargs[param_name] = param.default

        return target_class(**kwargs)

    def clear_singletons(self) -> None:
        """Clear cached singletons (for testing)"""
        self.singletons.clear()
        logger.debug("Cleared singletons")


# ============================================================================
# DEPENDENCY INJECTION PROVIDER
# ============================================================================

class DIProvider:
    """
    Provides dependency injection for orchestrators.
    Integrates with OrchestratorFactory.
    """

    def __init__(self):
        self.container = DIContainer()

    def configure_standard_dependencies(self, event_bus: Any) -> None:
        """Configure standard dependencies used by all orchestrators"""
        self.container.register_singleton('event_bus', event_bus)
        logger.info("✅ Configured standard dependencies")

    def register_orchestrator_dependencies(self, orch_name: str, **dependencies: Any) -> None:
        """Register orchestrator-specific dependencies"""
        for dep_name, dep_value in dependencies.items():
            if callable(dep_value):
                self.container.register_factory(dep_name, dep_value)
            else:
                self.container.register_singleton(dep_name, dep_value)
        logger.debug(f"Registered dependencies for {orch_name}")

    def inject_orchestrator(self, orchestrator_class: Type[T], orch_name: str = None) -> T:
        """Inject dependencies into orchestrator"""
        instance = self.container.inject(orchestrator_class)
        logger.info(f"✅ Injected dependencies into {orch_name or orchestrator_class.__name__}")
        return instance


# ============================================================================
# PARAMETER RESOLVER
# ============================================================================

class ParameterResolver:
    """
    Resolves required parameters from specification before instantiation.
    Validates parameter types and required fields.
    """

    @staticmethod
    def resolve_parameters(requires_params: Dict[str, Any], available_instances: Dict[str, Any]) -> Dict[str, Any]:
        """
        Resolve parameters from specification.
        Args:
            requires_params: Dict of {param_name: param_spec}
            available_instances: Dict of {name: instance}
        Returns:
            Dict of {param_name: resolved_value}
        """
        resolved = {}

        for param_name, param_spec in requires_params.items():
            if isinstance(param_spec, dict):
                param_type = param_spec.get('type')
                source = param_spec.get('source')
                lazy_create = param_spec.get('lazy_create', False)

                if lazy_create and source:
                    # Lazy creation case (will be handled by factory)
                    continue

                # Try to resolve from available instances
                if param_name in available_instances:
                    resolved[param_name] = available_instances[param_name]
                    logger.debug(f"Resolved parameter: {param_name}")

        return resolved

    @staticmethod
    def validate_parameters(requires_params: Dict[str, Any]) -> bool:
        """Validate parameter specifications"""
        for param_name, param_spec in requires_params.items():
            if isinstance(param_spec, dict):
                required_fields = ['type', 'source']
                if not all(field in param_spec for field in required_fields):
                    logger.warning(f"Parameter {param_name} missing required fields: {required_fields}")
                    return False
        return True


from typing import Set
