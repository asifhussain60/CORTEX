"""
AC-PHX-008-04: Domain Plugin System

Framework for domain-specific plugins that extend orchestrator capabilities.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional
import uuid


@dataclass
class PluginMetadata:
    """Plugin metadata."""
    plugin_id: str
    domain: str
    version: str = "1.0.0"
    author: str = ""
    description: str = ""
    created_at: datetime = field(default_factory=datetime.utcnow)


class DomainPlugin(ABC):
    """
    Abstract base class for domain plugins.
    
    Plugins extend orchestrator functionality with domain-specific
    capabilities, hooks, and transformations.
    """
    
    @property
    @abstractmethod
    def plugin_id(self) -> str:
        """Return unique plugin identifier."""
        pass
    
    @property
    @abstractmethod
    def domain(self) -> str:
        """Return the domain this plugin applies to."""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin logic.
        
        Args:
            context: Execution context
            
        Returns:
            Plugin result
        """
        pass
    
    def pre_execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Hook called before main execution.
        
        Args:
            context: Execution context
            
        Returns:
            Modified context (or original if no changes)
        """
        return context
    
    def post_execute(
        self,
        context: Dict[str, Any],
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Hook called after main execution.
        
        Args:
            context: Execution context
            result: Execution result
            
        Returns:
            Modified result (or original if no changes)
        """
        return result
    
    @property
    def metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            plugin_id=self.plugin_id,
            domain=self.domain,
        )


class DomainPluginRegistry:
    """
    Registry for domain plugins.
    
    Manages plugin registration, discovery, and lifecycle.
    """
    
    _instance: Optional['DomainPluginRegistry'] = None
    
    def __init__(self) -> None:
        """Initialize plugin registry."""
        self._plugins: Dict[str, DomainPlugin] = {}
        self._domain_index: Dict[str, List[str]] = {}
    
    @classmethod
    def get_instance(cls) -> 'DomainPluginRegistry':
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    def register(self, plugin: DomainPlugin) -> None:
        """
        Register a plugin.
        
        Args:
            plugin: Plugin to register
            
        Raises:
            ValueError: If plugin ID already exists
        """
        plugin_id = plugin.plugin_id
        if plugin_id in self._plugins:
            raise ValueError(f"Plugin {plugin_id} already registered")
        
        self._plugins[plugin_id] = plugin
        
        # Update domain index
        domain = plugin.domain
        if domain not in self._domain_index:
            self._domain_index[domain] = []
        self._domain_index[domain].append(plugin_id)
    
    def unregister(self, plugin_id: str) -> bool:
        """
        Unregister a plugin.
        
        Args:
            plugin_id: Plugin ID to unregister
            
        Returns:
            True if plugin was unregistered, False if not found
        """
        if plugin_id not in self._plugins:
            return False
        
        plugin = self._plugins[plugin_id]
        domain = plugin.domain
        
        del self._plugins[plugin_id]
        
        if domain in self._domain_index:
            self._domain_index[domain].remove(plugin_id)
        
        return True
    
    def get_plugin(self, plugin_id: str) -> Optional[DomainPlugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: Plugin ID
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_id)
    
    def list_plugins_by_domain(self, domain: str) -> List[DomainPlugin]:
        """
        List all plugins for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of plugins for the domain
        """
        plugin_ids = self._domain_index.get(domain, [])
        return [self._plugins[pid] for pid in plugin_ids if pid in self._plugins]
    
    def list_all_plugins(self) -> List[DomainPlugin]:
        """Return all registered plugins."""
        return list(self._plugins.values())
    
    def execute_plugin(
        self,
        plugin_id: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute a plugin.
        
        Args:
            plugin_id: Plugin to execute
            context: Execution context
            
        Returns:
            Plugin execution result
            
        Raises:
            ValueError: If plugin not found
        """
        plugin = self.get_plugin(plugin_id)
        if not plugin:
            raise ValueError(f"Plugin {plugin_id} not found")
        
        # Pre-execution hook
        modified_context = plugin.pre_execute(context)
        
        # Main execution
        result = plugin.execute(modified_context)
        
        # Post-execution hook
        final_result = plugin.post_execute(modified_context, result)
        
        return final_result
