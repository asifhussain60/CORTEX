"""
Orchestrators Registry - Registration and Discovery System

DEPRECATED: This module provides stub implementations for backward compatibility.
The canonical wiring system is cortex.wiring.GitBackedRegistry.

Docker-First Architecture: YAML-backed wiring replaces database registries.

Exports:
- OrchestratorMetadata: Metadata container for orchestrators
- DiscoveryEngine: Query engine for finding orchestrators
- DiscoveryQuery: Query builder for discovery searches
- DiscoveryResult: Result container for discovery searches
"""

from typing import Any, Optional


class OrchestratorMetadata:
    """Metadata container for orchestrators."""
    def __init__(self, name: str, class_type: Any = None, **kwargs):
        self.name = name
        self.class_type = class_type
        self.__dict__.update(kwargs)


class OrchestratorRegistry:
    """
    Stub registry for backward compatibility.
    
    In Docker-first architecture, orchestrators are configured via YAML.
    """
    _instance = None
    
    @classmethod
    def instance(cls) -> 'OrchestratorRegistry':
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def get(self, name: str) -> Optional[Any]:
        return None
    
    def list_all(self) -> list:
        return []


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
