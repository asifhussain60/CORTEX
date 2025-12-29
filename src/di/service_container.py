"""
Dependency Injection Container for CORTEX 4.0

Phase: 7B - Operations Simplification (Task 7.7)
Author: Asif Hussain
Created: December 23, 2025

Provides:
- Service registration with lifecycle scopes
- Auto-wiring via constructor inspection  
- Circular dependency detection
- Singleton, transient, and scoped lifetimes
"""

from typing import Any, Callable, Dict, Type, Optional, Union, Set, get_type_hints
from enum import Enum
from dataclasses import dataclass
import inspect
import logging


class ServiceScope(Enum):
    """Service lifecycle scope."""
    SINGLETON = "singleton"  # One instance for entire application
    TRANSIENT = "transient"  # New instance per resolution
    SCOPED = "scoped"         # One instance per scope (e.g., per request)


@dataclass
class ServiceRegistration:
    """
    Service registration metadata.
    
    Stores information about how to create and manage a service.
    """
    service_type: Type
    implementation: Union[Type, Callable]
    scope: ServiceScope
    dependencies: Dict[str, Type]
    singleton_instance: Optional[Any] = None
    
    def __repr__(self) -> str:
        return (
            f"ServiceRegistration("
            f"service={self.service_type.__name__}, "
            f"scope={self.scope.value}, "
            f"deps={list(self.dependencies.keys())})"
        )


class ServiceContainer:
    """
    Dependency Injection Container.
    
    Features:
    - Auto-wiring via constructor inspection
    - Lifecycle management (singleton, transient, scoped)
    - Circular dependency detection
    - Lazy resolution
    - Scope management
    
    Usage:
        container = ServiceContainer()
        
        # Register services
        container.register(ILogger, ConsoleLogger, ServiceScope.SINGLETON)
        container.register(IDatabase, SqliteDatabase, ServiceScope.TRANSIENT)
        
        # Resolve services (auto-wires dependencies)
        logger = container.resolve(ILogger)
        db = container.resolve(IDatabase)
    """
    
    def __init__(self):
        """Initialize empty service container."""
        self._registrations: Dict[str, ServiceRegistration] = {}
        self._resolving: Set[str] = set()  # Track circular dependencies
        self._scoped_instances: Dict[str, Dict[str, Any]] = {}  # scope_id -> {key -> instance}
        self._logger: logging.Logger = logging.getLogger("cortex.di.container")
        
        self._logger.debug("ServiceContainer initialized")
    
    def register(
        self,
        service_type: Type,
        implementation: Optional[Union[Type, Callable]] = None,
        scope: ServiceScope = ServiceScope.TRANSIENT
    ) -> None:
        """
        Register service with container.
        
        Args:
            service_type: Service interface or abstract class
            implementation: Concrete implementation (defaults to service_type)
            scope: Lifecycle scope (SINGLETON, TRANSIENT, SCOPED)
            
        Raises:
            ValueError: If service already registered
            TypeError: If implementation is invalid
            
        Example:
            container.register(ILogger, ConsoleLogger, ServiceScope.SINGLETON)
        """
        impl = implementation or service_type
        key = self._get_service_key(service_type)
        
        # Check for duplicate registration
        if key in self._registrations:
            raise ValueError(f"Service already registered: {service_type.__name__}")
        
        # Validate implementation
        if not callable(impl):
            raise TypeError(f"Implementation must be callable: {impl}")
        
        # Extract dependencies from constructor
        try:
            dependencies = self._extract_dependencies(impl)
        except Exception as e:
            raise TypeError(f"Failed to extract dependencies from {impl.__name__}: {e}")
        
        # Create registration
        registration = ServiceRegistration(
            service_type=service_type,
            implementation=impl,
            scope=scope,
            dependencies=dependencies
        )
        
        self._registrations[key] = registration
        
        self._logger.debug(
            f"Registered: {service_type.__name__} -> {impl.__name__} "
            f"(scope={scope.value}, deps={list(dependencies.keys())})"
        )
    
    def register_instance(
        self,
        service_type: Type,
        instance: Any
    ) -> None:
        """
        Register existing instance as singleton.
        
        Useful for pre-configured objects.
        
        Args:
            service_type: Service type
            instance: Pre-created instance
            
        Example:
            logger = ConsoleLogger()
            container.register_instance(ILogger, logger)
        """
        key = self._get_service_key(service_type)
        
        registration = ServiceRegistration(
            service_type=service_type,
            implementation=lambda: instance,
            scope=ServiceScope.SINGLETON,
            dependencies={},
            singleton_instance=instance
        )
        
        self._registrations[key] = registration
        
        self._logger.debug(f"Registered instance: {service_type.__name__}")
    
    def resolve(
        self,
        service_type: Type,
        scope_id: Optional[str] = None
    ) -> Any:
        """
        Resolve service instance.
        
        Auto-wires dependencies and manages lifecycle based on scope.
        
        Args:
            service_type: Service type to resolve
            scope_id: Scope identifier for SCOPED services
            
        Returns:
            Service instance
            
        Raises:
            KeyError: If service not registered
            RuntimeError: If circular dependency detected
            
        Example:
            logger = container.resolve(ILogger)
        """
        key = self._get_service_key(service_type)
        
        # Check if registered
        if key not in self._registrations:
            # Handle string type annotations
            service_name = service_type if isinstance(service_type, str) else service_type.__name__
            raise KeyError(
                f"Service not registered: {service_name}. "
                f"Available services: {list(self._registrations.keys())}"
            )
        
        # Circular dependency check
        if key in self._resolving:
            chain = " -> ".join(self._resolving)
            raise RuntimeError(
                f"Circular dependency detected: {chain} -> {key}"
            )
        
        registration = self._registrations[key]
        
        # Return singleton instance
        if registration.scope == ServiceScope.SINGLETON:
            if registration.singleton_instance is None:
                self._logger.debug(f"Creating singleton: {service_type.__name__}")
                registration.singleton_instance = self._create_instance(registration)
            return registration.singleton_instance
        
        # Return scoped instance
        if registration.scope == ServiceScope.SCOPED:
            if scope_id is None:
                raise ValueError(
                    f"Scope ID required for scoped service: {service_type.__name__}"
                )
            
            if scope_id not in self._scoped_instances:
                self._scoped_instances[scope_id] = {}
            
            if key not in self._scoped_instances[scope_id]:
                self._logger.debug(
                    f"Creating scoped instance: {service_type.__name__} (scope={scope_id})"
                )
                self._scoped_instances[scope_id][key] = self._create_instance(registration)
            
            return self._scoped_instances[scope_id][key]
        
        # Create transient instance
        self._logger.debug(f"Creating transient: {service_type.__name__}")
        return self._create_instance(registration)
    
    def clear_scope(self, scope_id: str) -> None:
        """
        Clear scoped instances.
        
        Call this when scope ends (e.g., end of request).
        
        Args:
            scope_id: Scope identifier to clear
        """
        if scope_id in self._scoped_instances:
            count = len(self._scoped_instances[scope_id])
            del self._scoped_instances[scope_id]
            self._logger.debug(f"Cleared scope: {scope_id} ({count} instances)")
    
    def is_registered(self, service_type: Type) -> bool:
        """
        Check if service is registered.
        
        Args:
            service_type: Service type to check
            
        Returns:
            True if registered
        """
        key = self._get_service_key(service_type)
        return key in self._registrations
    
    def get_registration(self, service_type: Type) -> Optional[ServiceRegistration]:
        """
        Get service registration metadata.
        
        Args:
            service_type: Service type
            
        Returns:
            ServiceRegistration or None if not registered
        """
        key = self._get_service_key(service_type)
        return self._registrations.get(key)
    
    def _create_instance(self, registration: ServiceRegistration) -> Any:
        """
        Create instance with auto-wiring.
        
        Args:
            registration: Service registration
            
        Returns:
            Created instance
        """
        key = self._get_service_key(registration.service_type)
        self._resolving.add(key)
        
        try:
            # Resolve dependencies
            resolved_deps = self._resolve_dependencies(registration)
            
            # Create instance
            if inspect.isclass(registration.implementation):
                return registration.implementation(**resolved_deps)
            else:
                # Factory function
                return registration.implementation(**resolved_deps)
        
        finally:
            self._resolving.discard(key)
    
    def _resolve_dependencies(self, registration: ServiceRegistration) -> Dict[str, Any]:
        """
        Resolve all dependencies for a service registration.
        
        Args:
            registration: Service registration
            
        Returns:
            Dict of resolved dependencies
        """
        resolved_deps = {}
        sig, _ = self._get_constructor_info(registration.implementation)
        
        for dep_name, dep_type in registration.dependencies.items():
            resolved_dep = self._resolve_dependency_safely(
                dep_name, dep_type, sig, registration.service_type
            )
            if resolved_dep is not inspect.Parameter.empty:
                resolved_deps[dep_name] = resolved_dep
        
        return resolved_deps
    
    def _resolve_dependency_safely(
        self,
        dep_name: str,
        dep_type: Type,
        sig: inspect.Signature,
        service_type: Type
    ) -> Any:
        """
        Safely resolve a single dependency with fallback handling.
        
        Args:
            dep_name: Dependency parameter name
            dep_type: Dependency type
            sig: Constructor signature
            service_type: Parent service type (for logging)
            
        Returns:
            Resolved dependency instance, None, or Parameter.empty if has default
        """
        try:
            return self.resolve(dep_type)
        except KeyError:
            # Check if parameter has a default value
            param = sig.parameters.get(dep_name)
            if param and param.default != inspect.Parameter.empty:
                # Has default, skip this dependency
                return inspect.Parameter.empty
            
            self._logger.warning(
                f"Dependency not registered for {service_type.__name__}: "
                f"{dep_name}: {dep_type.__name__ if hasattr(dep_type, '__name__') else dep_type}"
            )
            # Provide None for missing optional dependencies
            return None
    
    def _extract_dependencies(self, cls: Union[Type, Callable]) -> Dict[str, Type]:
        """
        Extract constructor dependencies via inspection.
        
        Args:
            cls: Class or callable to inspect
            
        Returns:
            Dict mapping parameter names to types
        """
        dependencies = {}
        
        try:
            sig, type_hints = self._get_constructor_info(cls)
            
            for param_name, param in sig.parameters.items():
                if param_name in ('self', 'cls'):
                    continue
                
                # Try to get type from type_hints first (resolves forward refs)
                if param_name in type_hints:
                    param_type = type_hints[param_name]
                elif param.annotation != inspect.Parameter.empty:
                    param_type = param.annotation
                else:
                    continue
                
                # Handle Optional types - unwrap to get inner type
                if hasattr(param_type, '__origin__') and param_type.__origin__ is Union:
                    # Get first non-None type from Union
                    args = [arg for arg in param_type.__args__ if arg is not type(None)]
                    if args:
                        param_type = args[0]
                
                dependencies[param_name] = param_type
        
        except Exception as e:
            self._logger.debug(f"Could not extract dependencies: {e}")
            # Return empty dict - service has no dependencies
        
        return dependencies
    
    def _get_constructor_info(
        self, cls: Union[Type, Callable]
    ) -> tuple[inspect.Signature, Dict[str, Type]]:
        """
        Get constructor signature and type hints with forward reference resolution.
        
        Args:
            cls: Class or callable to inspect
            
        Returns:
            Tuple of (signature, type_hints dict)
        """
        if inspect.isclass(cls):
            sig = inspect.signature(cls.__init__)
            globalns = getattr(cls.__init__, '__globals__', None) or {}
            type_hints = get_type_hints(cls.__init__, globalns=globalns, localns=None)
        else:
            sig = inspect.signature(cls)
            globalns = getattr(cls, '__globals__', None) or {}
            type_hints = get_type_hints(cls, globalns=globalns, localns=None)
        
        return sig, type_hints
    
    def _get_service_key(self, service_type: Union[Type, str]) -> str:
        """
        Generate unique key for service type.
        
        Args:
            service_type: Service type or string (forward reference)
            
        Returns:
            Unique string key
        """
        # Handle string type annotations (forward references from annotations)
        if isinstance(service_type, str):
            return service_type
        return f"{service_type.__module__}.{service_type.__name__}"
    
    def __repr__(self) -> str:
        """String representation."""
        return (
            f"ServiceContainer("
            f"services={len(self._registrations)}, "
            f"resolving={len(self._resolving)})"
        )
