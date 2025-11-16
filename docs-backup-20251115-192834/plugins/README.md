# CORTEX Plugin System

## Overview

CORTEX uses an extensible plugin architecture that allows the system to grow with new capabilities. All plugins inherit from `BasePlugin` and register via the plugin registry.

---

## Available Plugins

### 🔄 Documentation Refresh Plugin

**Purpose:** Synchronize 6 documentation files from design documents

**Status:** ✅ Production Ready (v2.1)

**Documents Synchronized:**
1. Technical Reference (`docs/CORTEX-TECHNICAL-DOCS.md`)
2. Story Narrative (`docs/story/CORTEX-STORY/CORTEX-STORY.md`)
3. Image Reference (`docs/CORTEX-IMAGE-REFERENCE.md`)
4. History Timeline (`docs/CORTEX-HISTORY.md`)
5. **Ancient Rules** (`docs/Ancient-Rules.md`) - NEW in v2.1
6. **Features List** (`docs/CORTEX-FEATURES.md`) - NEW in v2.1

**Key Features:**
- ✅ Automatic governance rules sync from `brain-protection-rules.yaml`
- ✅ Human-readable feature list generation from design docs
- ✅ Story technical recaps with 3 creative styles
- ✅ Backup creation before refresh
- ✅ File creation prohibition enforcement

**Test Coverage:** 37/38 tests passing (97.4%)

**Learn More:** [Documentation Refresh Enhancements](doc-refresh-plugin-enhancements.md)

---

### 🖥️ Platform Switch Plugin

**Purpose:** Automatic cross-platform environment setup

**Status:** ✅ Production Ready

**Supported Platforms:**
- 🍎 macOS (Darwin) - zsh, Unix paths
- 🪟 Windows - PowerShell, Windows paths
- 🐧 Linux - bash, Unix paths

**Key Features:**
- ✅ Automatic platform detection on startup
- ✅ Auto-configuration when platform changes
- ✅ Git pull latest code
- ✅ Platform-specific path configuration
- ✅ Quick dependency validation
- ✅ Tooling check (Git, Python, etc.)

**Commands:**
- `/setup` - Manual environment setup
- Aliases: `/env`, `/environment`, `/configure`

**Learn More:** [Platform Switch Plugin](platform-switch-plugin.md)

---

### 🔍 Code Review Plugin

**Purpose:** Automated code quality analysis

**Status:** ✅ Production Ready

**Key Features:**
- Code quality metrics
- Style consistency checks
- Best practice validation
- Security vulnerability detection

**Learn More:** [Code Review Plugin](code-review-plugin.md)

---

### ⚙️ Command System

**Purpose:** Extensible command registration and routing

**Status:** ✅ Production Ready

**Key Features:**
- Slash command registration
- Natural language equivalent mapping
- Plugin command discovery
- Automatic entry point updates

**Learn More:** [Command System](command-system.md)

---

## Plugin Architecture

### Base Plugin Structure

All plugins inherit from `BasePlugin` and implement:

```python
from src.plugins.base_plugin import BasePlugin, PluginMetadata

class MyPlugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            plugin_id="my_plugin",
            name="My Plugin",
            version="1.0.0",
            description="What this plugin does",
            author="Your Name",
            category=PluginCategory.UTILITY
        )
    
    def initialize(self) -> bool:
        """Setup logic"""
        return True
    
    def execute(self, request: str, context: Dict) -> Dict:
        """Main plugin logic"""
        return {"success": True}
    
    def cleanup(self) -> bool:
        """Teardown logic"""
        return True
```

### Registering Commands (Optional)

Plugins can register slash commands:

```python
def register_commands(self) -> List[CommandMetadata]:
    return [
        CommandMetadata(
            command="/mycommand",
            natural_language_equivalent="my feature",
            plugin_id=self.metadata.plugin_id,
            description="Does something cool"
        )
    ]
```

### Plugin Registration

Register your plugin in `src/plugins/__init__.py`:

```python
def register() -> BasePlugin:
    return MyPlugin()
```

---

## Development Guidelines

### Creating a New Plugin

1. **Create plugin file** in `src/plugins/`
2. **Inherit from BasePlugin** and implement required methods
3. **Register commands** (optional)
4. **Add tests** in `tests/plugins/test_my_plugin.py`
5. **Update documentation** in `docs/plugins/my-plugin.md`
6. **Register plugin** in `src/plugins/__init__.py`

### Testing

```bash
# Run all plugin tests
pytest tests/plugins/

# Run specific plugin tests
pytest tests/plugins/test_my_plugin.py

# Run with coverage
pytest --cov=src/plugins tests/plugins/
```

### Best Practices

✅ **Follow BasePlugin contract** for compatibility  
✅ **Add comprehensive tests** (aim for >90% coverage)  
✅ **Document public APIs** with clear docstrings  
✅ **Use command registry** for slash commands  
✅ **Handle errors gracefully** with meaningful messages  
✅ **Validate inputs** before processing  
✅ **Log important operations** for debugging  

---

## Plugin Categories

Plugins are organized by category:

### 🛠️ Utility Plugins
- Documentation refresh
- Code formatting
- File cleanup

### 🎯 Development Plugins
- Platform setup
- Environment configuration
- Dependency management

### 🔍 Analysis Plugins
- Code review
- Quality metrics
- Performance profiling

### 🤖 Agent Plugins
- Intent detection
- Workflow orchestration
- Task automation

---

## Command Registry

The command registry provides centralized command management:

```python
from src.plugins.command_registry import CommandRegistry

registry = CommandRegistry.get_instance()

# Register command
registry.register_command(
    command="/mycommand",
    natural_language="my feature",
    plugin_id="my_plugin",
    description="What it does"
)

# Find plugin for command
plugin_id = registry.find_plugin_for_command("/mycommand")

# Get all commands for plugin
commands = registry.get_commands_for_plugin("my_plugin")
```

---

## Future Enhancements

### Planned Plugins

**🧪 Test Generator Plugin**
- Automatic test creation
- Coverage gap detection
- Mock generation

**📊 Metrics Plugin**
- Token usage tracking
- Performance monitoring
- Cost analysis

**🔐 Security Scanner Plugin**
- Vulnerability detection
- Dependency audit
- Secret detection

**📝 Changelog Generator Plugin**
- Automatic changelog from commits
- Release notes generation
- Version management

---

## Plugin Metrics

**Total Plugins:** 4 (Production)  
**Test Coverage:** 150+ tests across all plugins  
**Pass Rate:** >95% average  
**Command Coverage:** 8+ slash commands  

---

## Contributing

Want to add a new plugin?

1. **Discuss in GitHub Issues** - Propose your plugin idea
2. **Follow architecture** - Use BasePlugin pattern
3. **Add comprehensive tests** - Maintain high coverage
4. **Document thoroughly** - Help users understand
5. **Submit PR** - Include tests and docs

---

## Resources

- [Plugin Base Class](../reference/plugin-api.md)
- [Command Registry API](command-system.md)
- [Testing Guidelines](../testing/plugin-testing.md)
- [Plugin Development Tutorial](../guides/plugin-development.md)

---

*Last Updated: 2025-11-09*  
*CORTEX Plugin System v2.1*
