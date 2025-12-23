"""
Auto-Discovery Module for Dependency Injection

Phase: 7B - Operations Simplification (Task 7.7.2)
Author: Asif Hussain
Created: December 23, 2025

Provides automatic service registration via:
- Module scanning
- Decorator-based registration
- Convention-based discovery
"""

import inspect
import importlib
import pkgutil
from typing import Type, List, Optional, Set, Callable
from pathlib import Path
import logging

from .service_container import ServiceContainer, ServiceScope

logger = logging.getLogger("cortex.di.auto_discovery")


class AutoDiscovery:
    """
    Auto-discovery engine for dependency injection.
    
    Features:
    - Scan modules for @service decorated classes
    - Convention-based registration (IService -> ServiceImpl)
    - Lifecycle scope detection from class attributes
    - Circular dependency detection
    
    Usage:
        container = ServiceContainer()
        discovery = AutoDiscovery(container)
        
        # Scan all orchestrators
        discovery.scan_module("src.orchestration_4_0.orchestrators")
        
        # Or scan specific path
        discovery.scan_path(Path("src/orchestrators"))
    """
    
    def __init__(self, container: ServiceContainer):
        """
        Initialize auto-discovery engine.
        
        Args:
            container: Target service container for registration
        """
        self.container = container
        self._discovered: Set[str] = set()
        self._logger = logger
    
    def scan_module(
        self,
        module_name: str,
        recursive: bool = True,
        scope_detector: Optional[Callable[[Type], ServiceScope]] = None
    ) -> int:
        """
        Scan module for @service decorated classes.
        
        Args:
            module_name: Module to scan (e.g., "src.orchestrators")
            recursive: Scan submodules
            scope_detector: Custom function to detect service scope
            
        Returns:
            Number of services registered
            
        Example:
            # Scan all orchestrators recursively
            count = discovery.scan_module("src.orchestration_4_0.orchestrators")
            print(f"Registered {count} orchestrators")
        """
        self._logger.info(f"Scanning module: {module_name}")
        
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            self._logger.error(f"Failed to import module {module_name}: {e}")
            return 0
        
        registered_count = 0
        
        # Scan current module
        registered_count += self._scan_module_members(
            module,
            scope_detector=scope_detector
        )
        
        # Scan submodules if recursive
        if recursive and hasattr(module, '__path__'):
            for importer, modname, ispkg in pkgutil.walk_packages(
                path=module.__path__,
                prefix=module.__name__ + '.',
                onerror=lambda x: self._logger.warning(f"Error loading module: {x}")
            ):
                try:
                    submodule = importlib.import_module(modname)
                    registered_count += self._scan_module_members(
                        submodule,
                        scope_detector=scope_detector
                    )
                except Exception as e:
                    self._logger.warning(f"Failed to scan submodule {modname}: {e}")
        
        self._logger.info(
            f"Auto-discovery complete: {registered_count} services registered "
            f"from {module_name}"
        )
        
        return registered_count
    
    def scan_path(
        self,
        path: Path,
        base_module: Optional[str] = None,
        scope_detector: Optional[Callable[[Type], ServiceScope]] = None
    ) -> int:
        """
        Scan filesystem path for Python modules.
        
        Args:
            path: Directory path to scan
            base_module: Base module name (e.g., "src.orchestrators")
            scope_detector: Custom function to detect service scope
            
        Returns:
            Number of services registered
            
        Example:
            # Scan orchestrators directory
            discovery.scan_path(
                Path("src/orchestration_4_0/orchestrators"),
                base_module="src.orchestration_4_0.orchestrators"
            )
        """
        if not path.exists() or not path.is_dir():
            self._logger.warning(f"Path does not exist: {path}")
            return 0
        
        if base_module is None:
            # Infer base module from path
            base_module = str(path).replace('/', '.').replace('\\', '.')
        
        self._logger.info(f"Scanning path: {path} (module: {base_module})")
        
        return self.scan_module(
            base_module,
            recursive=True,
            scope_detector=scope_detector
        )
    
    def _scan_module_members(
        self,
        module,
        scope_detector: Optional[Callable[[Type], ServiceScope]] = None
    ) -> int:
        """
        Scan module members for registrable classes.
        
        Args:
            module: Module to scan
            scope_detector: Custom function to detect service scope
            
        Returns:
            Number of services registered
        """
        registered_count = 0
        
        for name, obj in inspect.getmembers(module):
            # Skip private members
            if name.startswith('_'):
                continue
            
            # Only process classes
            if not inspect.isclass(obj):
                continue
            
            # Skip classes not defined in this module
            if obj.__module__ != module.__name__:
                continue
            
            # Check if already discovered
            key = f"{obj.__module__}.{obj.__name__}"
            if key in self._discovered:
                continue
            
            # Check for @service decorator (marked with __service__ attribute)
            if hasattr(obj, '__service__'):
                scope = self._detect_scope(obj, scope_detector)
                self._register_service(obj, obj, scope)
                registered_count += 1
                self._discovered.add(key)
                self._logger.debug(f"Discovered service: {key} (scope={scope.value})")
            
            # Convention-based discovery: IService -> ServiceImpl
            elif self._is_implementation_class(obj):
                interface = self._find_interface(obj)
                if interface:
                    scope = self._detect_scope(obj, scope_detector)
                    self._register_service(interface, obj, scope)
                    registered_count += 1
                    self._discovered.add(key)
                    self._logger.debug(
                        f"Discovered implementation: {interface.__name__} -> {obj.__name__} "
                        f"(scope={scope.value})"
                    )
        
        return registered_count
    
    def _register_service(
        self,
        service_type: Type,
        implementation: Type,
        scope: ServiceScope
    ) -> None:
        """
        Register discovered service with container.
        
        Args:
            service_type: Service interface
            implementation: Concrete implementation
            scope: Service lifecycle scope
        """
        try:
            if not self.container.is_registered(service_type):
                self.container.register(service_type, implementation, scope)
        except ValueError as e:
            # Service already registered (race condition in parallel scanning)
            self._logger.debug(f"Service already registered: {service_type.__name__}")
    
    def _detect_scope(
        self,
        cls: Type,
        custom_detector: Optional[Callable[[Type], ServiceScope]] = None
    ) -> ServiceScope:
        """
        Detect service lifecycle scope.
        
        Priority:
        1. Custom detector function
        2. __service_scope__ class attribute
        3. Default to TRANSIENT
        
        Args:
            cls: Class to inspect
            custom_detector: Custom scope detection function
            
        Returns:
            Detected service scope
        """
        # Custom detector
        if custom_detector:
            try:
                return custom_detector(cls)
            except Exception as e:
                self._logger.warning(f"Custom scope detector failed: {e}")
        
        # Class attribute
        if hasattr(cls, '__service_scope__'):
            scope_value = cls.__service_scope__
            if isinstance(scope_value, ServiceScope):
                return scope_value
            elif isinstance(scope_value, str):
                try:
                    return ServiceScope[scope_value.upper()]
                except KeyError:
                    pass
        
        # Default
        return ServiceScope.TRANSIENT
    
    def _is_implementation_class(self, cls: Type) -> bool:
        """
        Check if class follows implementation naming convention.
        
        Conventions:
        - Ends with "Impl", "Implementation", "Service", "Manager"
        - Has public constructor
        - Not abstract
        
        Args:
            cls: Class to check
            
        Returns:
            True if class appears to be an implementation
        """
        name = cls.__name__
        
        # Check naming convention
        suffixes = ['Impl', 'Implementation', 'Service', 'Manager', 'Orchestrator']
        if not any(name.endswith(suffix) for suffix in suffixes):
            return False
        
        # Check not abstract
        if inspect.isabstract(cls):
            return False
        
        return True
    
    def _find_interface(self, impl_class: Type) -> Optional[Type]:
        """
        Find interface/abstract base for implementation class.
        
        Looks for:
        - Base class with name matching convention (IService, ServiceBase)
        - ABC base classes
        
        Args:
            impl_class: Implementation class
            
        Returns:
            Interface class or None
        """
        # Check direct bases
        for base in impl_class.__bases__:
            # Skip object and ABC
            if base in (object, type):
                continue
            
            base_name = base.__name__
            
            # Check naming convention: IService, ServiceBase, AbstractService
            if (base_name.startswith('I') and base_name[1].isupper()) or \
               base_name.endswith('Base') or \
               base_name.startswith('Abstract'):
                return base
            
            # Check if abstract
            if inspect.isabstract(base):
                return base
        
        return None
    
    def get_discovered_services(self) -> List[str]:
        """
        Get list of discovered service keys.
        
        Returns:
            List of service identifiers
        """
        return sorted(self._discovered)
    
    def clear(self) -> None:
        """Clear discovered services cache."""
        self._discovered.clear()
