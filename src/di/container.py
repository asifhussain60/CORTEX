"""
CORTEX 4.0 Dependency Injection Container

Centralizes all dependency creation and wiring using dependency-injector.

Architecture:
- Singleton pattern for container instance
- Provider-based dependency registration
- Lazy initialization of expensive resources
- Configuration-driven setup
"""

from dependency_injector import containers, providers
from typing import Optional

from src.config import ConfigManager
from src.logging import setup_logger
from src.templates import TemplateManager
from src.mcp import get_mcp_gateway


class CortexContainer(containers.DeclarativeContainer):
    """
    Main dependency injection container for CORTEX 4.0.
    
    Provides centralized management of:
    - Configuration (ConfigManager)
    - Logging (Logger instances)
    - Templates (TemplateManager)
    - MCP Gateway (MCPGateway)
    - Future: Brain interface, Orchestrators
    """
    
    # Configuration (singleton)
    config = providers.Singleton(
        ConfigManager
    )
    
    # Logging factory (creates loggers per module)
    logger_factory = providers.Factory(
        setup_logger
    )
    
    # Template Manager (singleton)
    template_manager = providers.Singleton(
        TemplateManager
    )
    
    # MCP Gateway (singleton via factory function)
    mcp_gateway = providers.Singleton(
        get_mcp_gateway
    )
    
    # Future providers (Phase 2-4):
    # brain_interface = providers.Singleton(BrainInterface)
    # base_orchestrator = providers.Factory(BaseOrchestrator, ...)
    # planning_orchestrator = providers.Factory(PlanningOrchestrator, ...)
    # tdd_orchestrator = providers.Factory(TDDOrchestrator, ...)


# Singleton container instance
_container_instance: Optional[CortexContainer] = None


def get_container() -> CortexContainer:
    """
    Get or create the singleton CortexContainer instance.
    
    Returns:
        CortexContainer: The singleton DI container
    """
    global _container_instance
    
    if _container_instance is None:
        _container_instance = CortexContainer()
        
        # Wire dependencies (connects @inject decorators to providers)
        # Note: Wiring done at module level as needed, not globally
        # Example: container.wire(modules=[src.orchestrators.base])
        
    return _container_instance


def reset_container() -> None:
    """
    Reset the container singleton (primarily for testing).
    
    Warning: This will clear all cached singletons.
    """
    global _container_instance
    
    if _container_instance is not None:
        _container_instance.unwire()
        _container_instance = None
