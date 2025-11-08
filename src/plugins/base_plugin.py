"""
Base Plugin System for CORTEX 2.0

Provides abstract base class and infrastructure for all CORTEX plugins.
Plugins extend CORTEX functionality without modifying core code.

Architecture:
- BasePlugin: Abstract class all plugins must inherit from
- PluginMetadata: Standardized plugin information
- Hook System: Lifecycle hooks for plugin execution
- Configuration: JSON schema validation for plugin settings

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class PluginCategory(Enum):
    """Plugin categories for organization"""
    INFRASTRUCTURE = "infrastructure"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    WORKFLOW = "workflow"
    EXTENSION = "extension"
    MAINTENANCE = "maintenance"
    ANALYSIS = "analysis"


class PluginPriority(Enum):
    """Plugin execution priority"""
    CRITICAL = 1
    HIGH = 2
    MEDIUM = 3
    LOW = 4
    BACKGROUND = 5


class HookPoint(Enum):
    """Lifecycle hooks for plugin execution"""
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"
    ON_DOC_REFRESH = "on_doc_refresh"
    ON_SELF_REVIEW = "on_self_review"
    ON_BRAIN_UPDATE = "on_brain_update"
    ON_CONVERSATION_END = "on_conversation_end"
    ON_ERROR = "on_error"
    ON_EXTENSION_SCAFFOLD = "on_extension_scaffold"
    ON_WORKFLOW_START = "on_workflow_start"
    ON_WORKFLOW_END = "on_workflow_end"


@dataclass
class PluginMetadata:
    """Standardized metadata for all plugins"""
    plugin_id: str
    name: str
    version: str
    category: PluginCategory
    priority: PluginPriority
    description: str
    author: str
    dependencies: List[str]
    hooks: List[str]
    config_schema: Dict[str, Any]


class BasePlugin(ABC):
    """
    Abstract base class for all CORTEX plugins.
    
    All plugins must:
    1. Inherit from BasePlugin
    2. Implement _get_metadata() method
    3. Implement initialize() method
    4. Implement execute() method
    5. Implement cleanup() method
    
    Example:
    ```python
    class MyPlugin(BasePlugin):
        def _get_metadata(self) -> PluginMetadata:
            return PluginMetadata(
                plugin_id="my_plugin",
                name="My Plugin",
                version="1.0.0",
                category=PluginCategory.WORKFLOW,
                priority=PluginPriority.MEDIUM,
                description="Does something useful",
                author="Your Name",
                dependencies=[],
                hooks=[HookPoint.ON_WORKFLOW_START.value],
                config_schema={}
            )
        
        def initialize(self) -> bool:
            # Setup plugin resources
            return True
        
        def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
            # Main plugin logic
            return {"success": True}
        
        def cleanup(self) -> bool:
            # Cleanup plugin resources
            return True
    ```
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with optional configuration.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.metadata = self._get_metadata()
        self._validate_metadata()
        self.enabled = True
        self.logger = logging.getLogger(f"plugin.{self.metadata.plugin_id}")
    
    @abstractmethod
    def _get_metadata(self) -> PluginMetadata:
        """
        Return plugin metadata.
        
        Must be implemented by all plugins.
        
        Returns:
            PluginMetadata object with plugin information
        """
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin resources.
        
        Called once when plugin is loaded. Use this to:
        - Verify dependencies
        - Setup connections
        - Load configuration
        - Validate environment
        
        Returns:
            True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin main logic.
        
        Args:
            context: Execution context with parameters
                - hook: Hook that triggered execution
                - Additional context-specific parameters
        
        Returns:
            Dictionary with execution results:
                - success: bool (required)
                - Additional result data
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> bool:
        """
        Cleanup plugin resources.
        
        Called when plugin is unloaded. Use this to:
        - Close connections
        - Release resources
        - Save state
        
        Returns:
            True if cleanup successful, False otherwise
        """
        pass
    
    def _validate_metadata(self) -> None:
        """Validate plugin metadata is complete and valid"""
        if not self.metadata.plugin_id:
            raise ValueError("Plugin must have plugin_id")
        
        if not self.metadata.name:
            raise ValueError("Plugin must have name")
        
        if not self.metadata.version:
            raise ValueError("Plugin must have version")
        
        if not isinstance(self.metadata.category, PluginCategory):
            raise ValueError("Plugin category must be PluginCategory enum")
        
        if not isinstance(self.metadata.priority, PluginPriority):
            raise ValueError("Plugin priority must be PluginPriority enum")
    
    def validate_config(self) -> bool:
        """
        Validate plugin configuration against schema.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # TODO: Implement JSON schema validation
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get plugin information.
        
        Returns:
            Dictionary with plugin metadata
        """
        return {
            "plugin_id": self.metadata.plugin_id,
            "name": self.metadata.name,
            "version": self.metadata.version,
            "category": self.metadata.category.value,
            "priority": self.metadata.priority.value,
            "description": self.metadata.description,
            "author": self.metadata.author,
            "dependencies": self.metadata.dependencies,
            "hooks": self.metadata.hooks,
            "enabled": self.enabled
        }
    
    def enable(self) -> None:
        """Enable plugin"""
        self.enabled = True
        self.logger.info(f"Plugin {self.metadata.name} enabled")
    
    def disable(self) -> None:
        """Disable plugin"""
        self.enabled = False
        self.logger.info(f"Plugin {self.metadata.name} disabled")
    
    def is_enabled(self) -> bool:
        """Check if plugin is enabled"""
        return self.enabled


class PluginManager:
    """
    Manages plugin lifecycle and execution.
    
    Responsibilities:
    - Plugin discovery and loading
    - Hook registration and execution
    - Plugin dependency resolution
    - Configuration management
    """
    
    def __init__(self):
        self.plugins: Dict[str, BasePlugin] = {}
        self.hooks: Dict[str, List[BasePlugin]] = {}
        self.logger = logging.getLogger("plugin.manager")
    
    def register_plugin(self, plugin: BasePlugin) -> bool:
        """
        Register a plugin.
        
        Args:
            plugin: Plugin instance to register
        
        Returns:
            True if registration successful, False otherwise
        """
        try:
            # Check if already registered
            if plugin.metadata.plugin_id in self.plugins:
                self.logger.warning(
                    f"Plugin {plugin.metadata.plugin_id} already registered"
                )
                return False
            
            # Initialize plugin
            if not plugin.initialize():
                self.logger.error(
                    f"Failed to initialize plugin {plugin.metadata.plugin_id}"
                )
                return False
            
            # Register plugin
            self.plugins[plugin.metadata.plugin_id] = plugin
            
            # Register hooks
            for hook_name in plugin.metadata.hooks:
                if hook_name not in self.hooks:
                    self.hooks[hook_name] = []
                self.hooks[hook_name].append(plugin)
            
            self.logger.info(
                f"Plugin {plugin.metadata.name} registered successfully"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error registering plugin: {e}")
            return False
    
    def execute_hook(
        self,
        hook: HookPoint,
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Execute all plugins registered for a hook.
        
        Args:
            hook: Hook to execute
            context: Context for plugin execution
        
        Returns:
            List of results from all plugins
        """
        results = []
        hook_name = hook.value
        
        if hook_name not in self.hooks:
            return results
        
        # Sort plugins by priority
        plugins = sorted(
            self.hooks[hook_name],
            key=lambda p: p.metadata.priority.value
        )
        
        # Execute each plugin
        for plugin in plugins:
            if not plugin.is_enabled():
                continue
            
            try:
                context["hook"] = hook_name
                result = plugin.execute(context)
                results.append({
                    "plugin_id": plugin.metadata.plugin_id,
                    "result": result
                })
            except Exception as e:
                self.logger.error(
                    f"Error executing plugin {plugin.metadata.plugin_id}: {e}"
                )
                results.append({
                    "plugin_id": plugin.metadata.plugin_id,
                    "error": str(e)
                })
        
        return results
    
    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def list_plugins(self) -> List[Dict[str, Any]]:
        """List all registered plugins"""
        return [plugin.get_info() for plugin in self.plugins.values()]
    
    def cleanup_all(self) -> bool:
        """Cleanup all plugins"""
        success = True
        for plugin in self.plugins.values():
            try:
                if not plugin.cleanup():
                    success = False
            except Exception as e:
                self.logger.error(
                    f"Error cleaning up plugin {plugin.metadata.plugin_id}: {e}"
                )
                success = False
        return success
