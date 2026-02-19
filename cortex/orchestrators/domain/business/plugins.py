"""Domain Plugin System

Domain plugin framework for extensible business logic.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


class DomainPlugin(ABC):
    """Base class for domain plugins."""

    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Get plugin identifier."""
        pass

    @property
    @abstractmethod
    def domain(self) -> str:
        """Get domain this plugin belongs to."""
        pass

    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic.

        Args:
            context: Execution context

        Returns:
            Execution result
        """
        pass

    def pre_execute(self, context: Dict[str, Any]) -> None:
        """Hook executed before main execution.

        Args:
            context: Execution context
        """
        pass

    def post_execute(self, context: Dict[str, Any], result: Dict[str, Any]) -> None:
        """Hook executed after main execution.

        Args:
            context: Execution context
            result: Execution result
        """
        pass


class DomainPluginRegistry:
    """Registry for domain plugins."""

    def __init__(self):
        """Initialize registry."""
        self._plugins: Dict[str, DomainPlugin] = {}
        self._domain_plugins: Dict[str, List[str]] = {}

    def register(self, plugin: DomainPlugin) -> None:
        """Register a plugin.

        Args:
            plugin: Plugin to register
        """
        plugin_id = plugin.plugin_id
        domain = plugin.domain

        self._plugins[plugin_id] = plugin

        if domain not in self._domain_plugins:
            self._domain_plugins[domain] = []

        if plugin_id not in self._domain_plugins[domain]:
            self._domain_plugins[domain].append(plugin_id)

    def get_plugin(self, plugin_id: str) -> Optional[DomainPlugin]:
        """Get plugin by ID.

        Args:
            plugin_id: Plugin identifier

        Returns:
            Plugin or None
        """
        return self._plugins.get(plugin_id)

    def list_plugins_by_domain(self, domain: str) -> List[DomainPlugin]:
        """List all plugins for a domain.

        Args:
            domain: Domain name

        Returns:
            List of plugins
        """
        plugin_ids = self._domain_plugins.get(domain, [])
        return [self._plugins[pid] for pid in plugin_ids if pid in self._plugins]


__all__ = ["DomainPlugin", "DomainPluginRegistry"]
