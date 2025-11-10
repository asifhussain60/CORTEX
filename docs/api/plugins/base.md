# Plugin Base API

**Module:** `src.plugins.base_plugin`  
**Purpose:** Foundation class for all CORTEX plugins

## Overview

`BasePlugin` provides the contract and infrastructure for CORTEX's extensible plugin system. All plugins inherit from this base class.

## Classes

### BasePlugin

Abstract base class for all plugins.

```python
from src.plugins.base_plugin import BasePlugin, PluginMetadata

class MyPlugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        
    def initialize(self) -> bool:
        """Setup logic - return True if successful"""
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Main plugin logic"""
        
    def cleanup(self) -> bool:
        """Teardown logic"""
```

#### Methods

##### `_get_metadata() -> PluginMetadata`
**Abstract method** that returns plugin metadata.

**Returns:** `PluginMetadata` object with plugin info

**Example:**
```python
def _get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        plugin_id="my_plugin",
        name="My Plugin",
        version="1.0.0",
        category=PluginCategory.UTILITIES,
        priority=PluginPriority.NORMAL,
        description="Does something useful",
        author="Developer Name",
        dependencies=[],
        hooks=[HookPoint.ON_EXECUTE.value]
    )
```

##### `initialize() -> bool`
**Abstract method** for plugin setup.

**Returns:** `True` if initialization successful, `False` otherwise

**Example:**
```python
def initialize(self) -> bool:
    try:
        self.cache = {}
        self.config = self.load_config()
        logger.info(f"{self.metadata.name} initialized")
        return True
    except Exception as e:
        logger.error(f"Init failed: {e}")
        return False
```

##### `execute(context: Dict[str, Any]) -> Dict[str, Any]`
**Abstract method** containing main plugin logic.

**Parameters:**
- `context`: Dictionary with execution context (hook, data, etc.)

**Returns:** Dictionary with result:
```python
{
    "success": bool,
    "message": str,
    "data": Any,
    "error": Optional[str]
}
```

**Example:**
```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    hook = context.get("hook")
    
    if hook == HookPoint.ON_EXECUTE.value:
        return self._do_work(context)
    
    return {"success": False, "error": "Unknown hook"}
```

##### `cleanup() -> bool`
**Abstract method** for plugin teardown.

**Returns:** `True` if cleanup successful

**Example:**
```python
def cleanup(self) -> bool:
    try:
        self.cache.clear()
        logger.info(f"{self.metadata.name} cleaned up")
        return True
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        return False
```

##### `register_commands() -> List[CommandMetadata]`
**Optional method** to register plugin commands.

**Returns:** List of `CommandMetadata` objects

**Example:**
```python
def register_commands(self) -> List[CommandMetadata]:
    return [
        CommandMetadata(
            command="/mycommand",
            natural_language_equivalent="do my thing",
            plugin_id=self.metadata.plugin_id,
            description="Does my thing",
            parameters=["param1", "param2"]
        )
    ]
```

---

### PluginMetadata

Data class containing plugin metadata.

```python
@dataclass
class PluginMetadata:
    plugin_id: str          # Unique identifier
    name: str              # Human-readable name
    version: str           # Semantic version
    category: PluginCategory
    priority: PluginPriority
    description: str       # Short description
    author: str           # Author name
    dependencies: List[str]  # Required plugin IDs
    hooks: List[str]      # Lifecycle hooks
    config_schema: Dict = field(default_factory=dict)
```

**Fields:**
- **plugin_id**: Unique identifier (e.g., "cleanup_plugin")
- **name**: Display name (e.g., "Workspace Cleanup")
- **version**: Semantic version (e.g., "2.0.0")
- **category**: Plugin category (see `PluginCategory`)
- **priority**: Execution priority (see `PluginPriority`)
- **description**: Brief description of functionality
- **author**: Plugin author name
- **dependencies**: List of plugin IDs this plugin requires
- **hooks**: List of hook points (see `HookPoint`)
- **config_schema**: JSON schema for plugin configuration

---

### PluginCategory

Enum defining plugin categories.

```python
class PluginCategory(Enum):
    ENVIRONMENT = "environment"
    DOCUMENTATION = "documentation"
    TESTING = "testing"
    ANALYSIS = "analysis"
    UTILITIES = "utilities"
    DEVELOPMENT = "development"
    INTEGRATION = "integration"
```

---

### PluginPriority

Enum defining execution priority.

```python
class PluginPriority(Enum):
    CRITICAL = 0   # Must run first
    HIGH = 1      # High priority
    NORMAL = 2    # Normal priority
    LOW = 3       # Low priority
    OPTIONAL = 4  # Can be skipped
```

Lower numbers = higher priority (CRITICAL runs before OPTIONAL).

---

## Usage Examples

### Creating a Plugin

```python
from src.plugins.base_plugin import (
    BasePlugin, PluginMetadata, PluginCategory, PluginPriority
)
from src.plugins.hooks import HookPoint
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

class MyPlugin(BasePlugin):
    """My custom plugin"""
    
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="my_plugin",
            name="My Plugin",
            version="1.0.0",
            category=PluginCategory.UTILITIES,
            priority=PluginPriority.NORMAL,
            description="My custom plugin",
            author="Me",
            dependencies=[],
            hooks=[HookPoint.ON_EXECUTE.value]
        )
    
    def initialize(self) -> bool:
        logger.info("Initializing my plugin")
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "success": True,
            "message": "Plugin executed successfully"
        }
    
    def cleanup(self) -> bool:
        logger.info("Cleaning up my plugin")
        return True

# Export plugin
def register() -> BasePlugin:
    return MyPlugin()
```

### Registering Commands

```python
from src.plugins.command_registry import CommandMetadata

class MyPlugin(BasePlugin):
    # ... other methods ...
    
    def register_commands(self) -> List[CommandMetadata]:
        return [
            CommandMetadata(
                command="/mycommand",
                natural_language_equivalent="run my command",
                plugin_id=self.metadata.plugin_id,
                description="Runs my custom command",
                parameters=["input"]
            )
        ]
```

### Using Configuration

```python
class MyPlugin(BasePlugin):
    def initialize(self) -> bool:
        # Get config with defaults
        self.max_retries = self.config.get("max_retries", 3)
        self.timeout = self.config.get("timeout", 30)
        return True
```

Configuration in `cortex.config.json`:
```json
{
  "plugins": {
    "my_plugin": {
      "max_retries": 5,
      "timeout": 60
    }
  }
}
```

---

## Plugin Lifecycle

1. **Discovery:** Plugin registry scans `src/plugins/` directory
2. **Registration:** Plugin's `register()` function called
3. **Initialization:** `initialize()` called on plugin instance
4. **Execution:** `execute()` called when hook triggered
5. **Cleanup:** `cleanup()` called on shutdown

---

## Hook Points

Plugins can hook into these lifecycle events:

- `ON_STARTUP` - System startup
- `ON_SHUTDOWN` - System shutdown
- `ON_DOC_REFRESH` - Documentation refresh
- `ON_CLEANUP` - Workspace cleanup
- `ON_SELF_REVIEW` - Self-review checks
- `ON_TEST_RUN` - Test execution
- `ON_EXECUTE` - General execution

See [Plugin Hooks](./hooks.md) for details.

---

## Best Practices

### 1. Fail Fast in Initialize
```python
def initialize(self) -> bool:
    if not self._check_prerequisites():
        logger.error("Prerequisites not met")
        return False  # Fail fast
    return True
```

### 2. Provide Clear Error Messages
```python
def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
    try:
        result = self._do_work()
        return {"success": True, "data": result}
    except Exception as e:
        return {
            "success": False,
            "error": f"Work failed: {str(e)}",
            "details": {"context": context}
        }
```

### 3. Use Configuration Schema
```python
def _get_metadata(self) -> PluginMetadata:
    return PluginMetadata(
        # ... other fields ...
        config_schema={
            "type": "object",
            "properties": {
                "enabled": {"type": "boolean", "default": True},
                "max_items": {"type": "integer", "default": 100}
            }
        }
    )
```

### 4. Clean Up Resources
```python
def cleanup(self) -> bool:
    try:
        if hasattr(self, 'file_handle'):
            self.file_handle.close()
        if hasattr(self, 'cache'):
            self.cache.clear()
        return True
    except Exception as e:
        logger.error(f"Cleanup error: {e}")
        return False
```

### 5. Log Important Events
```python
logger.info(f"Plugin {self.metadata.name} starting execution")
logger.debug(f"Context: {context}")
logger.error(f"Error occurred: {e}")
```

---

## Testing Plugins

```python
import pytest
from src.plugins.my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    assert plugin.initialize() == True

def test_plugin_execution():
    plugin = MyPlugin()
    plugin.initialize()
    
    result = plugin.execute({"hook": "ON_EXECUTE"})
    assert result["success"] == True

def test_plugin_cleanup():
    plugin = MyPlugin()
    plugin.initialize()
    assert plugin.cleanup() == True
```

---

## Related Documentation

- [Plugin Registry](./registry.md)
- [Plugin Hooks](./hooks.md)
- [Command Registry](./command-registry.md)
- [Plugin Development Guide](../../guides/plugin-development.md)

---

*Part of CORTEX 2.0 Plugin System API Documentation*
