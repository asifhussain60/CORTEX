"""
Dependency Injection Container for CORTEX 4.0 Orchestrators

Provides service registration, lifecycle management, and automatic dependency resolution.
Eliminates code duplication across orchestrators.

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, Callable, Optional, Type, TypeVar, get_type_hints
from enum import Enum
import inspect
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

T = TypeVar('T')


class ServiceLifecycle(Enum):
    """Service lifecycle management options."""
    SINGLETON = "singleton"  # Single instance shared across all requests
    TRANSIENT = "transient"  # New instance created for each request
    SCOPED = "scoped"  # Single instance per scope (e.g., per tenant, per request)


@dataclass
class ServiceRegistration:
    """Registration information for a service."""
    service_type: Type
    implementation: Any  # Can be class, instance, or factory function
    lifecycle: ServiceLifecycle
    instance: Optional[Any] = None  # Cached instance for singletons


class CircularDependencyError(Exception):
    """Raised when circular dependency is detected."""
    pass


class ServiceNotFoundError(Exception):
    """Raised when requested service is not registered."""
    pass


class DependencyContainer:
    """
    Dependency Injection container for automatic service resolution.
    
    Supports:
    - Constructor injection
    - Service lifecycles (singleton, transient, scoped)
    - Circular dependency detection
    - Interface-based contracts
    - Multi-tenant service isolation
    """
    
    def __init__(self, container_name: str = "default"):
        """
        Initialize dependency container.
        
        Args:
            container_name: Name of this container (for logging)
        """
        self.container_name = container_name
        self.services: Dict[Type, ServiceRegistration] = {}
        self.scoped_instances: Dict[str, Dict[Type, Any]] = {}  # scope_id -> {type -> instance}
        self._resolution_stack: list = []  # For circular dependency detection
        
        logger.info(f"DependencyContainer '{container_name}' initialized")
    
    def register_singleton(
        self,
        service_type: Type[T],
        implementation: Optional[Any] = None
    ) -> None:
        """
        Register a singleton service (single instance shared).
        
        Args:
            service_type: Interface or abstract class type
            implementation: Concrete implementation (defaults to service_type)
        """
        impl = implementation or service_type
        self.services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=impl,
            lifecycle=ServiceLifecycle.SINGLETON
        )
        logger.debug(f"Registered singleton: {service_type.__name__}")
    
    def register_transient(
        self,
        service_type: Type[T],
        implementation: Optional[Any] = None
    ) -> None:
        """
        Register a transient service (new instance each time).
        
        Args:
            service_type: Interface or abstract class type
            implementation: Concrete implementation (defaults to service_type)
        """
        impl = implementation or service_type
        self.services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=impl,
            lifecycle=ServiceLifecycle.TRANSIENT
        )
        logger.debug(f"Registered transient: {service_type.__name__}")
    
    def register_scoped(
        self,
        service_type: Type[T],
        implementation: Optional[Any] = None
    ) -> None:
        """
        Register a scoped service (single instance per scope).
        
        Args:
            service_type: Interface or abstract class type
            implementation: Concrete implementation (defaults to service_type)
        """
        impl = implementation or service_type
        self.services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=impl,
            lifecycle=ServiceLifecycle.SCOPED
        )
        logger.debug(f"Registered scoped: {service_type.__name__}")
    
    def register_instance(
        self,
        service_type: Type[T],
        instance: T
    ) -> None:
        """
        Register a pre-created instance as singleton.
        
        Args:
            service_type: Service type
            instance: Pre-created instance
        """
        registration = ServiceRegistration(
            service_type=service_type,
            implementation=instance.__class__,
            lifecycle=ServiceLifecycle.SINGLETON,
            instance=instance
        )
        self.services[service_type] = registration
        logger.debug(f"Registered instance: {service_type.__name__}")
    
    def register_factory(
        self,
        service_type: Type[T],
        factory: Callable[[], T],
        lifecycle: ServiceLifecycle = ServiceLifecycle.TRANSIENT
    ) -> None:
        """
        Register a factory function for service creation.
        
        Args:
            service_type: Service type
            factory: Factory function that creates instances
            lifecycle: Service lifecycle
        """
        self.services[service_type] = ServiceRegistration(
            service_type=service_type,
            implementation=factory,
            lifecycle=lifecycle
        )
        logger.debug(f"Registered factory: {service_type.__name__}")
    
    def resolve(
        self,
        service_type: Type[T],
        scope_id: Optional[str] = None
    ) -> T:
        """
        Resolve a service instance.
        
        Args:
            service_type: Type of service to resolve
            scope_id: Optional scope ID for scoped services
            
        Returns:
            Service instance
            
        Raises:
            ServiceNotFoundError: If service not registered
            CircularDependencyError: If circular dependency detected
        """
        # Check if service is registered
        if service_type not in self.services:
            raise ServiceNotFoundError(
                f"Service {service_type.__name__} not registered in container '{self.container_name}'"
            )
        
        registration = self.services[service_type]
        
        # Check for circular dependencies
        if service_type in self._resolution_stack:
            cycle = " -> ".join([t.__name__ for t in self._resolution_stack] + [service_type.__name__])
            raise CircularDependencyError(f"Circular dependency detected: {cycle}")
        
        # Handle different lifecycles
        if registration.lifecycle == ServiceLifecycle.SINGLETON:
            return self._resolve_singleton(registration)
        
        elif registration.lifecycle == ServiceLifecycle.SCOPED:
            if scope_id is None:
                raise ValueError(f"Scope ID required for scoped service {service_type.__name__}")
            return self._resolve_scoped(registration, scope_id)
        
        else:  # TRANSIENT
            return self._resolve_transient(registration)
    
    def _resolve_singleton(self, registration: ServiceRegistration) -> Any:
        """Resolve singleton service."""
        if registration.instance is None:
            self._resolution_stack.append(registration.service_type)
            try:
                registration.instance = self._create_instance(registration.implementation)
            finally:
                self._resolution_stack.pop()
        
        return registration.instance
    
    def _resolve_scoped(self, registration: ServiceRegistration, scope_id: str) -> Any:
        """Resolve scoped service."""
        # Initialize scope if needed
        if scope_id not in self.scoped_instances:
            self.scoped_instances[scope_id] = {}
        
        scope = self.scoped_instances[scope_id]
        
        # Check if instance exists in scope
        if registration.service_type not in scope:
            self._resolution_stack.append(registration.service_type)
            try:
                scope[registration.service_type] = self._create_instance(registration.implementation)
            finally:
                self._resolution_stack.pop()
        
        return scope[registration.service_type]
    
    def _resolve_transient(self, registration: ServiceRegistration) -> Any:
        """Resolve transient service."""
        self._resolution_stack.append(registration.service_type)
        try:
            return self._create_instance(registration.implementation)
        finally:
            self._resolution_stack.pop()
    
    def _create_instance(self, implementation: Any) -> Any:
        """
        Create instance of implementation with dependency injection.
        
        Args:
            implementation: Class or factory function
            
        Returns:
            Created instance
        """
        # Check if it's a factory function
        if callable(implementation) and not inspect.isclass(implementation):
            return implementation()
        
        # It's a class - perform constructor injection
        if not inspect.isclass(implementation):
            # Already an instance
            return implementation
        
        # Get constructor parameters
        try:
            signature = inspect.signature(implementation.__init__)
            parameters = signature.parameters
            
            # Build kwargs for constructor
            kwargs = {}
            for param_name, param in parameters.items():
                if param_name == 'self':
                    continue
                
                # Try to resolve parameter type
                if param.annotation != inspect.Parameter.empty:
                    param_type = param.annotation
                    try:
                        kwargs[param_name] = self.resolve(param_type)
                    except ServiceNotFoundError:
                        # Parameter not registered - check if it has default
                        if param.default == inspect.Parameter.empty:
                            logger.warning(
                                f"Cannot resolve parameter '{param_name}' of type "
                                f"{param_type.__name__} for {implementation.__name__}"
                            )
                        # If has default, skip it
            
            # Create instance with resolved dependencies
            instance = implementation(**kwargs)
            logger.debug(f"Created instance: {implementation.__name__}")
            return instance
            
        except Exception as e:
            logger.error(f"Failed to create instance of {implementation.__name__}: {e}")
            raise
    
    def clear_scope(self, scope_id: str) -> None:
        """
        Clear all instances in a scope.
        
        Args:
            scope_id: Scope ID to clear
        """
        if scope_id in self.scoped_instances:
            del self.scoped_instances[scope_id]
            logger.debug(f"Cleared scope: {scope_id}")
    
    def clear_all_scopes(self) -> None:
        """Clear all scoped instances."""
        self.scoped_instances.clear()
        logger.debug("Cleared all scopes")
    
    def reset(self) -> None:
        """Reset container - clear all singleton instances and scopes."""
        for registration in self.services.values():
            if registration.lifecycle == ServiceLifecycle.SINGLETON:
                registration.instance = None
        
        self.scoped_instances.clear()
        logger.info(f"Container '{self.container_name}' reset")
    
    def is_registered(self, service_type: Type) -> bool:
        """Check if service type is registered."""
        return service_type in self.services
    
    def get_registrations(self) -> Dict[Type, ServiceRegistration]:
        """Get all service registrations."""
        return self.services.copy()
    
    def __repr__(self) -> str:
        """String representation of container."""
        return (
            f"DependencyContainer(name={self.container_name}, "
            f"services={len(self.services)}, "
            f"scopes={len(self.scoped_instances)})"
        )


# Global container instance
_global_container: Optional[DependencyContainer] = None


def get_container() -> DependencyContainer:
    """
    Get global dependency container.
    
    Returns:
        Global DependencyContainer instance
    """
    global _global_container
    if _global_container is None:
        _global_container = DependencyContainer("global")
    return _global_container


def reset_container() -> None:
    """Reset global container."""
    global _global_container
    if _global_container:
        _global_container.reset()


def create_container(name: str) -> DependencyContainer:
    """
    Create a new isolated container.
    
    Args:
        name: Container name
        
    Returns:
        New DependencyContainer instance
    """
    return DependencyContainer(name)
