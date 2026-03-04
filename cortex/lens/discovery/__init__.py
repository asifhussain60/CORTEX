"""
CORTEX LENS Discovery Package

Configuration and database discovery plugins.

Available Plugins:
- ConfigurationDiscovery: Discover and parse config files
- DatabaseDiscovery: Discover database topology and schemas

Authority: CORE-035 (Consolidation)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict


class DiscoveryPlugin(ABC):
    """Base interface for discovery plugins."""

    @abstractmethod
    def discover(self, repo_path: Any) -> Dict[str, Any]:
        """Discover topology information from repository."""


class TopologyMap:
    """Unified topology information container."""

    def __init__(self) -> None:
        """Initialize empty topology map."""
        self.config: Dict[str, Any] = {}
        self.databases: Dict[str, Any] = {}
        self.apis: Dict[str, Any] = {}
        self.microservices: Dict[str, Any] = {}


from cortex.lens.discovery.config_discovery import (
    ConfigTopology,
    ConfigurationDiscovery,
    ConnectionString,
)
from cortex.lens.discovery.database_discovery import (
    ConnectionInfo,
    DatabaseDiscovery,
    DatabaseTopology,
    ModelInfo,
    ORMType,
)

__all__ = [
    "DiscoveryPlugin",
    "TopologyMap",
    "ConfigurationDiscovery",
    "ConnectionString",
    "ConfigTopology",
    "DatabaseDiscovery",
    "ConnectionInfo",
    "ORMType",
    "ModelInfo",
    "DatabaseTopology",
]
