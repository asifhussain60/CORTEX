"""
CORTEX Orchestrators Module

Hierarchical orchestrator architecture:
- core/: Framework orchestrators (master, composite)
- domain/: Business domain orchestrators (ac, governance, audit)
- custom/: User-defined orchestrators

CANONICAL IMPORTS (CORE-035 Compliance):
----------------------------------------
For wiring/registry operations, always use DatabaseBackedRegistry:

    from cortex.orchestrators.core.database_registry import (
        DatabaseBackedRegistry,
        get_database_registry,
        initialize_registry,
    )

Legacy registries (kept for backward compatibility):
- cortex.orchestrators.registry.OrchestratorRegistry - metadata storage
- cortex.orchestrators.core.OrchestratorRegistry - domain queries
- cortex.brain.mcp.OrchestratorRegistry - MCP interface
- cortex.brain.core.decorators.OrchestratorRegistry - @orchestrator decorator

AC-PERMANENT-FIX: AC-009 - Import stability via canonical public API
"""

# Canonical SSOT for orchestrator wiring (CORE-035)
from cortex.orchestrators.core.database_registry import (
    DatabaseBackedRegistry,
    get_database_registry,
    initialize_registry,
    OrchestratorConfig,
    OrchestratorCategory,
    WiringState,
    WiringResult,
)

# Health monitoring
from cortex.orchestrators.core.health_checker import (
    OrchestratorHealthChecker,
    create_health_checker,
)

# Legacy metadata registry (backward compatibility)
from cortex.orchestrators.registry.orchestrator_registry import (
    OrchestratorMetadata,
)

# Discovery engine
from cortex.orchestrators.registry.discovery_engine import (
    DiscoveryEngine,
    DiscoveryQuery,
    DiscoveryResult,
)

__all__ = [
    # Canonical SSOT (preferred)
    "DatabaseBackedRegistry",
    "get_database_registry",
    "initialize_registry",
    "OrchestratorConfig",
    "OrchestratorCategory",
    "WiringState",
    "WiringResult",
    # Health monitoring
    "OrchestratorHealthChecker",
    "create_health_checker",
    # Legacy (backward compatibility)
    "OrchestratorMetadata",
    "DiscoveryEngine",
    "DiscoveryQuery",
    "DiscoveryResult",
]
