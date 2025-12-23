"""
Dependency Injection Decorators for CORTEX 4.0

Provides decorators for registering and injecting dependencies.

Phase: 7B - Operations Simplification (Task 7.7)
"""

from functools import wraps
from typing import Callable, Type, Any, Optional
from dependency_injector.wiring import inject, Provide

from src.di.container import CortexContainer


def service(
    scope: str = "transient",
    interface: Optional[Type] = None
) -> Callable[[Type], Type]:
    """
    Decorator to mark class for auto-discovery registration.
    
    Usage:
        @service(scope="singleton")
        class MyService:
            pass
        
        @service(scope="transient", interface=ILogger)
        class ConsoleLogger(ILogger):
            pass
    
    Args:
        scope: Service lifecycle ("singleton", "transient", "scoped")
        interface: Optional service interface/contract
        
    Returns:
        Decorator function
    """
    def decorator(cls: Type) -> Type:
        # Mark class for auto-discovery
        cls.__service__ = True
        cls.__service_scope__ = scope
        if interface:
            cls.__service_interface__ = interface
        return cls
    
    return decorator


def orchestrator(cls: Type) -> Type:
    """
    Decorator for orchestrator classes to enable dependency injection.
    
    Combines @service (for auto-discovery) with @inject (for dependency-injector).
    
    Usage:
        @orchestrator
        class MyOrchestrator:
            def __init__(
                self,
                config: ConfigManager = Provide[CortexContainer.config],
                logger: Callable = Provide[CortexContainer.logger_factory],
                templates: TemplateManager = Provide[CortexContainer.template_manager]
            ):
                self.config = config
                self.logger = logger(__name__)
                self.templates = templates
    
    Args:
        cls: The orchestrator class to decorate
    
    Returns:
        Decorated class with dependency injection enabled
    """
    # Mark for auto-discovery
    cls.__service__ = True
    cls.__service_scope__ = "transient"  # Orchestrators are typically transient
    
    # Apply @inject decorator from dependency-injector
    return inject(cls)


def injectable(func: Callable) -> Callable:
    """
    Decorator for functions that need dependency injection.
    
    Usage:
        @injectable
        def my_function(
            config: ConfigManager = Provide[CortexContainer.config],
            logger: Callable = Provide[CortexContainer.logger_factory]
        ):
            log = logger(__name__)
            log.info(f"Config version: {config.get('version')}")
    
    Args:
        func: The function to decorate
    
    Returns:
        Decorated function with dependency injection enabled
    """
    return inject(func)


# Export dependency-injector's Provide for use in type hints
__all__ = [
    "service",
    "orchestrator",
    "injectable",
    "Provide",
]

