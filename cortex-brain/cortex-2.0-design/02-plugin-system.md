# CORTEX 2.0 Plugin System Architecture

**Document:** 02-plugin-system.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Enable extensibility without bloating CORTEX core by providing:
- Standard plugin interface
- Lifecycle management
- Hook system for integration
- Auto-discovery and registration
- Enable/disable without code changes

---

## 🏗️ Plugin Architecture

### Base Plugin Interface

```python
# src/plugins/base_plugin.py

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

class PluginCategory(Enum):
    """Plugin categories"""
    CLEANUP = "cleanup"
    ORGANIZATION = "organization"
    MAINTENANCE = "maintenance"
    DOCUMENTATION = "documentation"
    VALIDATION = "validation"
    CUSTOM = "custom"

class PluginPriority(Enum):
    """Execution priority"""
    CRITICAL = 0   # Run first
    HIGH = 10
    NORMAL = 50
    LOW = 100
    OPTIONAL = 1000

@dataclass
class PluginMetadata:
    """Plugin metadata"""
    plugin_id: str              # Unique identifier
    name: str                   # Display name
    version: str                # Semantic version
    category: PluginCategory    # Category
    priority: PluginPriority    # Execution priority
    description: str            # Short description
    author: str                 # Author name
    dependencies: List[str]     # Required plugin IDs
    hooks: List[str]            # Hook points this plugin uses
    config_schema: Dict         # Configuration schema (JSON Schema)

class BasePlugin(ABC):
    """Base class for all CORTEX plugins"""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize plugin with optional configuration
        
        Args:
            config: Plugin-specific configuration from cortex.config.json
        """
        self.config = config or {}
        self.enabled = True
        self.metadata = self._get_metadata()
    
    @abstractmethod
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        pass
    
    @abstractmethod
    def initialize(self) -> bool:
        """
        Initialize plugin (one-time setup)
        
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute plugin logic
        
        Args:
            context: Execution context from hook
        
        Returns:
            Dict containing:
                - success: bool
                - result: Any
                - message: str
                - modified_files: List[str] (optional)
                - errors: List[str] (optional)
        """
        pass
    
    def validate_config(self) -> bool:
        """
        Validate plugin configuration
        
        Returns:
            bool: True if valid, False otherwise
        """
        # Default: no validation
        return True
    
    def cleanup(self) -> bool:
        """
        Cleanup after plugin execution
        
        Returns:
            bool: True if successful, False otherwise
        """
        # Default: no cleanup needed
        return True
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get plugin status
        
        Returns:
            Dict with status information
        """
        return {
            "plugin_id": self.metadata.plugin_id,
            "enabled": self.enabled,
            "initialized": hasattr(self, '_initialized'),
            "last_execution": getattr(self, '_last_execution', None)
        }
```

---

## 🔌 Plugin Hook System

### Hook Points

CORTEX 2.0 provides standardized hooks at key lifecycle stages:

```python
# src/plugins/hooks.py

from typing import Callable, Dict, Any, List
from enum import Enum

class HookPoint(Enum):
    """Standard hook points in CORTEX lifecycle"""
    
    # Conversation Lifecycle
    BEFORE_CONVERSATION_START = "before_conversation_start"
    AFTER_CONVERSATION_START = "after_conversation_start"
    BEFORE_CONVERSATION_END = "before_conversation_end"
    AFTER_CONVERSATION_END = "after_conversation_end"
    
    # Task Lifecycle
    BEFORE_TASK_START = "before_task_start"
    AFTER_TASK_COMPLETE = "after_task_complete"
    AFTER_TASK_FAILURE = "after_task_failure"
    
    # Phase Lifecycle
    BEFORE_PLAN_PHASE = "before_plan_phase"
    AFTER_PLAN_PHASE = "after_plan_phase"
    BEFORE_EXECUTE_PHASE = "before_execute_phase"
    AFTER_EXECUTE_PHASE = "after_execute_phase"
    BEFORE_TEST_PHASE = "before_test_phase"
    AFTER_TEST_PHASE = "after_test_phase"
    BEFORE_VALIDATE_PHASE = "before_validate_phase"
    AFTER_VALIDATE_PHASE = "after_validate_phase"
    
    # Maintenance Lifecycle
    ON_SELF_REVIEW = "on_self_review"
    ON_CLEANUP_REQUEST = "on_cleanup_request"
    ON_DB_MAINTENANCE = "on_db_maintenance"
    ON_DOC_REFRESH = "on_doc_refresh"
    
    # File Operations
    BEFORE_FILE_CREATE = "before_file_create"
    AFTER_FILE_CREATE = "after_file_create"
    BEFORE_FILE_MODIFY = "before_file_modify"
    AFTER_FILE_MODIFY = "after_file_modify"
    
    # Brain Operations
    BEFORE_BRAIN_UPDATE = "before_brain_update"
    AFTER_BRAIN_UPDATE = "after_brain_update"
    ON_PATTERN_LEARNED = "on_pattern_learned"
    
    # System Events
    ON_STARTUP = "on_startup"
    ON_SHUTDOWN = "on_shutdown"
    ON_ERROR = "on_error"

class HookRegistry:
    """Registry for plugin hooks"""
    
    def __init__(self):
        self._hooks: Dict[str, List[Callable]] = {}
        self._plugin_hooks: Dict[str, List[str]] = {}  # plugin_id -> hook_points
    
    def register_hook(self, 
                     hook_point: HookPoint, 
                     plugin_id: str,
                     callback: Callable) -> None:
        """Register a plugin callback for a hook point"""
        hook_name = hook_point.value
        
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        
        self._hooks[hook_name].append({
            'plugin_id': plugin_id,
            'callback': callback
        })
        
        if plugin_id not in self._plugin_hooks:
            self._plugin_hooks[plugin_id] = []
        self._plugin_hooks[plugin_id].append(hook_name)
    
    def trigger_hook(self, 
                    hook_point: HookPoint, 
                    context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Trigger all callbacks for a hook point
        
        Args:
            hook_point: Hook point to trigger
            context: Context data to pass to callbacks
        
        Returns:
            List of results from each callback
        """
        hook_name = hook_point.value
        results = []
        
        if hook_name not in self._hooks:
            return results
        
        for hook_info in self._hooks[hook_name]:
            try:
                result = hook_info['callback'](context)
                results.append({
                    'plugin_id': hook_info['plugin_id'],
                    'success': True,
                    'result': result
                })
            except Exception as e:
                results.append({
                    'plugin_id': hook_info['plugin_id'],
                    'success': False,
                    'error': str(e)
                })
        
        return results
    
    def unregister_plugin(self, plugin_id: str) -> None:
        """Remove all hooks for a plugin"""
        if plugin_id in self._plugin_hooks:
            for hook_name in self._plugin_hooks[plugin_id]:
                self._hooks[hook_name] = [
                    h for h in self._hooks[hook_name] 
                    if h['plugin_id'] != plugin_id
                ]
            del self._plugin_hooks[plugin_id]
```

---

## 📦 Plugin Manager

```python
# src/plugins/plugin_manager.py

from pathlib import Path
from typing import Dict, List, Optional, Any
import importlib
import json
import logging

logger = logging.getLogger(__name__)

class PluginManager:
    """Manages plugin lifecycle and execution"""
    
    def __init__(self, plugin_dir: Path, config: Dict[str, Any]):
        """
        Initialize plugin manager
        
        Args:
            plugin_dir: Directory containing plugins
            config: Plugin configuration from cortex.config.json
        """
        self.plugin_dir = plugin_dir
        self.config = config
        self.plugins: Dict[str, BasePlugin] = {}
        self.hook_registry = HookRegistry()
        self._load_order: List[str] = []
    
    def discover_plugins(self) -> List[str]:
        """
        Auto-discover plugins in plugin directory
        
        Returns:
            List of discovered plugin IDs
        """
        discovered = []
        
        for plugin_path in self.plugin_dir.glob("*_plugin.py"):
            try:
                plugin_id = plugin_path.stem
                discovered.append(plugin_id)
                logger.info(f"Discovered plugin: {plugin_id}")
            except Exception as e:
                logger.error(f"Error discovering plugin {plugin_path}: {e}")
        
        return discovered
    
    def load_plugin(self, plugin_id: str) -> bool:
        """
        Load a plugin by ID
        
        Args:
            plugin_id: Plugin identifier (filename without .py)
        
        Returns:
            bool: True if loaded successfully
        """
        try:
            # Import plugin module
            module_name = f"plugins.{plugin_id}"
            module = importlib.import_module(module_name)
            
            # Find plugin class (should be PluginClass in module)
            plugin_class = getattr(module, 'Plugin')
            
            # Get plugin config
            plugin_config = self.config.get('plugins', {}).get(plugin_id, {})
            
            # Instantiate plugin
            plugin = plugin_class(config=plugin_config)
            
            # Validate config
            if not plugin.validate_config():
                logger.error(f"Plugin {plugin_id} config validation failed")
                return False
            
            # Initialize plugin
            if not plugin.initialize():
                logger.error(f"Plugin {plugin_id} initialization failed")
                return False
            
            # Register hooks
            for hook_name in plugin.metadata.hooks:
                hook_point = HookPoint(hook_name)
                self.hook_registry.register_hook(
                    hook_point,
                    plugin_id,
                    plugin.execute
                )
            
            # Store plugin
            self.plugins[plugin_id] = plugin
            self._load_order.append(plugin_id)
            
            logger.info(f"Loaded plugin: {plugin_id} v{plugin.metadata.version}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load plugin {plugin_id}: {e}")
            return False
    
    def load_all_plugins(self) -> Dict[str, bool]:
        """
        Load all discovered plugins
        
        Returns:
            Dict mapping plugin_id to load success status
        """
        discovered = self.discover_plugins()
        results = {}
        
        for plugin_id in discovered:
            # Check if plugin is enabled in config
            plugin_config = self.config.get('plugins', {}).get(plugin_id, {})
            if not plugin_config.get('enabled', True):
                logger.info(f"Plugin {plugin_id} disabled in config")
                results[plugin_id] = False
                continue
            
            results[plugin_id] = self.load_plugin(plugin_id)
        
        # Resolve dependencies and determine load order
        self._resolve_dependencies()
        
        return results
    
    def _resolve_dependencies(self) -> None:
        """Resolve plugin dependencies and determine load order"""
        # Simple topological sort based on dependencies
        # (Implementation omitted for brevity - standard algorithm)
        pass
    
    def execute_hook(self, 
                    hook_point: HookPoint, 
                    context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute all plugins registered for a hook point
        
        Args:
            hook_point: Hook point to execute
            context: Context data for plugins
        
        Returns:
            List of execution results
        """
        logger.debug(f"Executing hook: {hook_point.value}")
        results = self.hook_registry.trigger_hook(hook_point, context)
        logger.debug(f"Hook {hook_point.value} completed: {len(results)} plugins executed")
        return results
    
    def get_plugin(self, plugin_id: str) -> Optional[BasePlugin]:
        """Get a loaded plugin by ID"""
        return self.plugins.get(plugin_id)
    
    def get_all_plugins(self) -> Dict[str, BasePlugin]:
        """Get all loaded plugins"""
        return self.plugins.copy()
    
    def enable_plugin(self, plugin_id: str) -> bool:
        """Enable a plugin"""
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = True
            return True
        return False
    
    def disable_plugin(self, plugin_id: str) -> bool:
        """Disable a plugin"""
        if plugin_id in self.plugins:
            self.plugins[plugin_id].enabled = False
            return True
        return False
    
    def unload_plugin(self, plugin_id: str) -> bool:
        """Unload a plugin"""
        if plugin_id in self.plugins:
            plugin = self.plugins[plugin_id]
            plugin.cleanup()
            self.hook_registry.unregister_plugin(plugin_id)
            del self.plugins[plugin_id]
            self._load_order.remove(plugin_id)
            return True
        return False
    
    def get_plugin_status(self) -> Dict[str, Dict]:
        """Get status of all plugins"""
        return {
            plugin_id: plugin.get_status()
            for plugin_id, plugin in self.plugins.items()
        }
```

---

## 📝 Plugin Configuration

### cortex.config.json (Plugin Section)

```json
{
  "plugins": {
    "cleanup_plugin": {
      "enabled": true,
      "config": {
        "auto_cleanup": true,
        "cleanup_patterns": ["*.tmp", "*.bak", "__pycache__"],
        "preserve_patterns": ["*.keep"],
        "max_file_age_days": 30
      }
    },
    "organization_plugin": {
      "enabled": true,
      "config": {
        "enforce_structure": true,
        "allowed_locations": {
          "tests": "tests/",
          "sources": "src/",
          "docs": "docs/"
        }
      }
    },
    "documentation_plugin": {
      "enabled": true,
      "config": {
        "auto_refresh": true,
        "remove_duplicates": true,
        "validate_links": true
      }
    },
    "custom_plugin": {
      "enabled": false,
      "config": {
        "custom_setting": "value"
      }
    }
  }
}
```

---

## 🚀 Usage Examples

### Creating a Custom Plugin

```python
# src/plugins/my_custom_plugin.py

from plugins.base_plugin import (
    BasePlugin, 
    PluginMetadata, 
    PluginCategory, 
    PluginPriority
)
from plugins.hooks import HookPoint
from typing import Dict, Any

class Plugin(BasePlugin):
    """Custom plugin example"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="my_custom_plugin",
            name="My Custom Plugin",
            version="1.0.0",
            category=PluginCategory.CUSTOM,
            priority=PluginPriority.NORMAL,
            description="Example custom plugin",
            author="Your Name",
            dependencies=[],
            hooks=[
                HookPoint.AFTER_TASK_COMPLETE.value,
                HookPoint.ON_CLEANUP_REQUEST.value
            ],
            config_schema={
                "type": "object",
                "properties": {
                    "setting1": {"type": "string"},
                    "setting2": {"type": "integer"}
                }
            }
        )
    
    def initialize(self) -> bool:
        """Initialize plugin"""
        # Setup logic here
        self._initialized = True
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute plugin logic"""
        # Your plugin logic here
        return {
            "success": True,
            "message": "Plugin executed successfully",
            "result": {}
        }
    
    def cleanup(self) -> bool:
        """Cleanup resources"""
        return True
```

### Using Plugin Manager

```python
# Example: Loading and using plugins

from pathlib import Path
from plugins.plugin_manager import PluginManager
from plugins.hooks import HookPoint

# Initialize plugin manager
plugin_manager = PluginManager(
    plugin_dir=Path("src/plugins"),
    config=config['plugins']
)

# Load all plugins
results = plugin_manager.load_all_plugins()
print(f"Loaded {len(results)} plugins")

# Execute hook
context = {
    "task_id": "task-123",
    "files_modified": ["src/main.py"],
    "success": True
}

results = plugin_manager.execute_hook(
    HookPoint.AFTER_TASK_COMPLETE,
    context
)

for result in results:
    print(f"Plugin {result['plugin_id']}: {result['success']}")
```

---

## ✅ Benefits

1. **Reduced Core Bloat:** Move non-essential features to plugins
2. **Easy Extension:** Add new functionality without modifying core
3. **User Customization:** Users can create custom plugins
4. **Enable/Disable:** Control features via configuration
5. **Dependency Management:** Plugins can depend on other plugins
6. **Lifecycle Management:** Proper initialization, execution, cleanup

---

**Next:** 03-conversation-state.md (Conversation resume and task tracking)
