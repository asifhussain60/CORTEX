"""
Planning Orchestrator Registration

Registers consolidated planning orchestrator with DatabaseBackedRegistry.

Authority: AC-PERMANENT-FIX-009 (DatabaseBackedRegistry)
Author: GitHub Copilot
Date: 2026-01-25
"""

from cortex.orchestrators.core.database_registry import (
    get_database_registry,
    OrchestratorConfig,
    OrchestratorCategory,
)


def register_planning_orchestrator() -> None:
    """Register consolidated planning orchestrator with database registry."""
    
    from cortex.orchestrators.domain.planning_orchestrator import (
        ORCHESTRATOR_CONFIG,
        PlanningOrchestrator,
    )
    
    # Get registry instance
    registry = get_database_registry()
    
    # Register configuration
    registry.register(ORCHESTRATOR_CONFIG)
    
    # Wire instance
    registry.wire_orchestrator(
        ORCHESTRATOR_CONFIG.name,
        PlanningOrchestrator.instance(),
    )
    
    print(f"✅ {ORCHESTRATOR_CONFIG.name} registered and wired successfully")


if __name__ == "__main__":
    register_planning_orchestrator()
