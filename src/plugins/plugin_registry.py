"""
Plugin Registry

Central registry for CORTEX plugins. Manages plugin discovery, registration,
and lifecycle.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Type
from pathlib import Path
import importlib.util
import sys

from src.plugins.base_plugin import BasePlugin, PluginMetadata


class PluginRegistry:
    """
    Central registry for plugin management.
    
    Responsibilities:
    - Plugin discovery and loading
    - Plugin lifecycle management (init, execute, cleanup)
    - Plugin metadata and capability tracking
    - Natural language command routing
    """
    
    def __init__(self):
        """Initialize plugin registry."""
        self._plugins: Dict[str, BasePlugin] = {}
        self._metadata: Dict[str, PluginMetadata] = {}
        self._initialized = False
    
    def discover_plugins(self, plugins_dir: Optional[Path] = None) -> int:
        """
        Discover and load plugins from plugins directory.
        
        Args:
            plugins_dir: Path to plugins directory (defaults to src/plugins)
            
        Returns:
            Number of plugins discovered
        """
        if plugins_dir is None:
            # Default to src/plugins relative to this file
            plugins_dir = Path(__file__).parent
        
        plugin_count = 0
        
        # Find all *_plugin.py files
        for plugin_file in plugins_dir.glob('*_plugin.py'):
            try:
                plugin = self._load_plugin(plugin_file)
                if plugin:
                    self.register_plugin(plugin)
                    plugin_count += 1
            except Exception as e:
                print(f"Failed to load plugin {plugin_file.name}: {e}")
        
        self._initialized = True
        return plugin_count
    
    def _load_plugin(self, plugin_file: Path) -> Optional[BasePlugin]:
        """Load a plugin from a file."""
        module_name = f"cortex.plugins.{plugin_file.stem}"
        
        spec = importlib.util.spec_from_file_location(module_name, plugin_file)
        if not spec or not spec.loader:
            return None
        
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
        
        # Look for register() function
        if hasattr(module, 'register'):
            return module.register()
        
        return None
    
    def register_plugin(self, plugin: BasePlugin) -> None:
        """
        Register a plugin instance.
        
        Args:
            plugin: Plugin instance to register
        """
        self._plugins[plugin.metadata.plugin_id] = plugin
        self._metadata[plugin.metadata.plugin_id] = plugin.metadata
    
    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """
        Get a plugin by ID.
        
        Args:
            plugin_id: Plugin identifier
            
        Returns:
            Plugin instance or None if not found
        """
        return self._plugins.get(plugin_id)
    
    def list_plugins(self) -> List[PluginMetadata]:
        """
        List all registered plugins.
        
        Returns:
            List of plugin metadata
        """
        return list(self._metadata.values())
    
    def get_plugin_by_natural_language(self, text: str) -> Optional[BasePlugin]:
        """
        Find plugin that handles a natural language request.
        
        Args:
            text: Natural language text
            
        Returns:
            Best matching plugin or None
        """
        text_lower = text.lower()
        
        # Check each plugin's natural language patterns
        for plugin in self._plugins.values():
            if hasattr(plugin.metadata, 'natural_language_patterns'):
                for pattern in plugin.metadata.natural_language_patterns:
                    if pattern.lower() in text_lower:
                        return plugin
        
        return None
    
    def initialize_all(self) -> Dict[str, bool]:
        """
        Initialize all registered plugins.
        
        Returns:
            Dict mapping plugin_id to initialization success
        """
        results = {}
        
        for plugin_id, plugin in self._plugins.items():
            try:
                results[plugin_id] = plugin.initialize()
            except Exception as e:
                print(f"Failed to initialize {plugin_id}: {e}")
                results[plugin_id] = False
        
        return results
    
    def cleanup_all(self) -> Dict[str, bool]:
        """
        Clean up all registered plugins.
        
        Returns:
            Dict mapping plugin_id to cleanup success
        """
        results = {}
        
        for plugin_id, plugin in self._plugins.items():
            try:
                results[plugin_id] = plugin.cleanup()
            except Exception as e:
                print(f"Failed to cleanup {plugin_id}: {e}")
                results[plugin_id] = False
        
        return results
    
    @property
    def is_initialized(self) -> bool:
        """Check if registry has been initialized."""
        return self._initialized
    
    @property
    def plugin_count(self) -> int:
        """Get number of registered plugins."""
        return len(self._plugins)


# Global singleton instance
_registry = None


def get_registry() -> PluginRegistry:
    """Get global plugin registry instance."""
    global _registry
    if _registry is None:
        _registry = PluginRegistry()
    return _registry
