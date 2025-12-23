"""
Dependency Injection (DI) Module for CORTEX 4.0

Provides centralized dependency management using dependency-injector framework.

Exports:
    CortexContainer: Main DI container
    ServiceContainer: Core DI container (Task 7.7)
    ServiceScope: Service lifecycle scopes
    ServiceRegistration: Service metadata
    orchestrator: Decorator for orchestrator registration
    injectable: Decorator for injectable functions
    get_container: Singleton container factory
"""

from src.di.container import CortexContainer, get_container
from src.di.decorators import orchestrator, injectable
from src.di.service_container import ServiceContainer, ServiceScope, ServiceRegistration

__all__ = [
    "CortexContainer",
    "get_container",
    "orchestrator",
    "injectable",
    "ServiceContainer",
    "ServiceScope",
    "ServiceRegistration",
]
