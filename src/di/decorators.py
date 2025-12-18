"""
Dependency Injection Decorators for CORTEX 4.0

Provides decorators for registering and injecting dependencies.
"""

from functools import wraps
from typing import Callable, Type, Any
from dependency_injector.wiring import inject, Provide

from src.di.container import CortexContainer


def orchestrator(cls: Type) -> Type:
    """
    Decorator for orchestrator classes to enable dependency injection.
    
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
    "orchestrator",
    "injectable",
    "Provide",
]
