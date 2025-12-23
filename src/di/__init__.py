"""
Dependency Injection (DI) Module for CORTEX 4.0

Provides centralized dependency management using dependency-injector framework.

Phase: 7B - Operations Simplification (Task 7.7)

Exports:
    CortexContainer: Main DI container
    ServiceContainer: Core DI container with auto-wiring
    ServiceScope: Service lifecycle scopes
    ServiceRegistration: Service metadata
    AutoDiscovery: Auto-discovery engine for service registration
    orchestrator: Decorator for orchestrator registration
    service: Decorator for service registration
    injectable: Decorator for injectable functions
    get_container: Singleton container factory
"""

from src.di.container import CortexContainer, get_container
from src.di.decorators import orchestrator, service, injectable
from src.di.service_container import ServiceContainer, ServiceScope, ServiceRegistration
from src.di.auto_discovery import AutoDiscovery

__all__ = [
    "CortexContainer",
    "get_container",
    "orchestrator",
    "service",
    "injectable",
    "ServiceContainer",
    "ServiceScope",
    "ServiceRegistration",
    "AutoDiscovery",
]
