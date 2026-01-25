"""
Orchestrators Registry - Registration and Discovery System (AC-PERMANENT-FIX-012)

Orchestrator registration and discovery services.
Bridges legacy registry APIs to DatabaseBackedRegistry.

Exports:
- OrchestratorRegistry: Bridge to DatabaseBackedRegistry (legacy compatibility)
- OrchestratorMetadata: Metadata container for orchestrators
- DiscoveryEngine: Query engine for finding orchestrators
- DiscoveryQuery: Query builder for discovery searches
- DiscoveryResult: Result container for discovery searches
"""

# AC-PERMANENT-FIX-012: Bridge legacy registry imports to DatabaseBackedRegistry
try:
    from cortex.orchestrators import DatabaseBackedRegistry
    from cortex.brain.core.decorators.orchestrator import OrchestratorRegistryBridge
    
    # Create legacy compatibility aliases
    OrchestratorRegistry = OrchestratorRegistryBridge
    
    # Temporary metadata class for compatibility
    class OrchestratorMetadata:
        """Legacy compatibility class"""
        def __init__(self, name, class_type=None, **kwargs):
            self.name = name
            self.class_type = class_type
            self.__dict__.update(kwargs)
            
except ImportError:
    # Fallback for tests
    class OrchestratorRegistry:
        pass
    
    class OrchestratorMetadata:
        pass

from cortex.orchestrators.registry.discovery_engine import (
    DiscoveryEngine,
    DiscoveryQuery,
    DiscoveryResult,
)

__all__ = [
    "OrchestratorRegistry",
    "OrchestratorMetadata",
    "DiscoveryEngine",
    "DiscoveryQuery",
    "DiscoveryResult",
]
