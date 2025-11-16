# CORTEX Command System

**Extensible slash command system for CORTEX plugins**

## Overview

The CORTEX Command System allows plugins to register **slash commands** (like `/mac`, `/setup`) as shortcuts to natural language. This provides:

- ✅ **Speed for power users** - Type `/mac` instead of "switched to mac"
- ✅ **Natural language preserved** - Commands expand to natural language before routing
- ✅ **Plugin-driven** - Each plugin declares its own commands
- ✅ **Zero conflicts** - Automatic detection and resolution
- ✅ **Discoverable** - Auto-generated help text
- ✅ **Fast** - O(1) lookup performance

## Architecture

```
User Input → Command Expansion → Intent Detection → Plugin Routing
   ↓              ↓                     ↓                  ↓
 "/mac"   → "switched to mac" → PLATFORM_SWITCH → platform_switch_plugin
```

### Components

1. **CommandRegistry** (`src/plugins/command_registry.py`)
   - Central registry for all commands
   - Singleton pattern
   - Conflict detection
   - Help generation

2. **BasePlugin** (`src/plugins/base_plugin.py`)
   - `register_commands()` method
   - Auto-registration on initialization

3. **Router** (`src/router.py`)
   - Command expansion before intent detection
   - Tracks which commands were used

4. **VS Code Extension** (`cortex-extension/src/cortex/chatParticipant.ts`)
   - Syncs with registered commands
   - Platform-specific UI

## For Plugin Developers

### Registering Commands

Override `register_commands()` in your plugin:

```python
from plugins.base_plugin import BasePlugin
from plugins.command_registry import CommandMetadata, CommandCategory

class MyPlugin(BasePlugin):
    def register_commands(self):
        """Register plugin commands."""
        return [
            CommandMetadata(
                command="/mycommand",
                natural_language_equivalent="do my action",
                plugin_id=self.metadata.plugin_id,
                description="Does something useful",
                category=CommandCategory.WORKFLOW,
                aliases=["/mc", "/my"],
                examples=["@cortex /mycommand", "do my action"],
                requires_online=False
            )
        ]
```

### Command Metadata

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | str | Yes | Slash command (e.g., `/mac`) |
| `natural_language_equivalent` | str | Yes | What command expands to |
| `plugin_id` | str | Yes | Your plugin's ID |
| `description` | str | Yes | Help text for users |
| `category` | CommandCategory | Yes | Platform, Workflow, Session, etc. |
| `aliases` | List[str] | No | Alternative commands |
| `examples` | List[str] | No | Usage examples |
| `requires_online` | bool | No | Needs brain connection? |

### Categories

```python
class CommandCategory(Enum):
    PLATFORM = "platform"          # Platform/environment management
    WORKFLOW = "workflow"          # Task/workflow control
    SESSION = "session"            # Session/conversation management
    DOCUMENTATION = "documentation"  # Docs and help
    TESTING = "testing"            # Test execution
    MAINTENANCE = "maintenance"    # Cleanup, optimization
    EXTENSION = "extension"        # Extension management
    CUSTOM = "custom"              # User-defined
```

## For Users

### Natural Language (Recommended)

```markdown
#file:prompts/user/cortex.md

switched to mac
setup environment
show me progress
```

### Slash Commands (Optional)

```markdown
#file:prompts/user/cortex.md

/mac
/setup
/status
```

Both work identically! Commands are just shortcuts.

### Available Commands

Use `/help` to see all commands:

```markdown
@cortex /help
```

Or check `cortex.md` for full list.

## Implementation Details

### Registration Flow

```python
# 1. Plugin initialization
plugin = PlatformSwitchPlugin()

# 2. BasePlugin.__init__ calls _auto_register_commands()
# 3. Plugin's register_commands() is invoked
commands = plugin.register_commands()

# 4. Commands registered to global registry
for cmd in commands:
    registry.register_command(cmd)
```

### Expansion Flow

```python
# 1. User types "/mac"
user_input = "/mac"

# 2. Router checks if it's a command
if router.command_registry.is_command(user_input):
    expanded = router.command_registry.expand_command(user_input)
    # expanded = "switched to mac"

# 3. Intent detection proceeds with natural language
intent = router.intent_router.route_request(expanded)
# intent = 'PLATFORM_SWITCH'

# 4. Plugin routing
plugin.execute(expanded, context)
```

### Conflict Resolution

```python
# First plugin registers
registry.register_command(
    CommandMetadata(command="/test", ...)
)  # ✅ Success

# Second plugin tries same command
registry.register_command(
    CommandMetadata(command="/test", ...)
)  # ❌ Rejected - conflict logged
```

## Performance

- **Command detection:** O(1) via dict lookup
- **Expansion:** O(1) via dict lookup
- **Registry overhead:** <0.001ms per lookup
- **Total routing:** Still <100ms (design target)

## Testing

```bash
# Run command registry tests
pytest tests/plugins/test_command_registry.py -v

# Run command expansion tests
pytest tests/plugins/test_command_expansion.py -v

# Run all plugin tests
pytest tests/plugins/ -v
```

## Examples

### Platform Switch Plugin

```python
class PlatformSwitchPlugin(BasePlugin):
    def register_commands(self):
        return [
            CommandMetadata(
                command="/mac",
                natural_language_equivalent="switched to mac",
                plugin_id="platform_switch",
                description="Switch to macOS environment",
                category=CommandCategory.PLATFORM,
                aliases=["/macos", "/darwin"],
                examples=["@cortex /mac"]
            ),
            CommandMetadata(
                command="/windows",
                natural_language_equivalent="switched to windows",
                plugin_id="platform_switch",
                description="Switch to Windows environment",
                category=CommandCategory.PLATFORM,
                aliases=["/win"],
                examples=["@cortex /windows"]
            ),
            # ... more commands
        ]
```

### Cleanup Plugin

```python
class CleanupPlugin(BasePlugin):
    def register_commands(self):
        return [
            CommandMetadata(
                command="/cleanup",
                natural_language_equivalent="cleanup workspace",
                plugin_id="cleanup",
                description="Clean up workspace files",
                category=CommandCategory.MAINTENANCE,
                aliases=["/clean"],
                examples=["@cortex /cleanup"]
            )
        ]
```

## Design Principles

1. **Natural language first** - Commands are shortcuts, not replacements
2. **Plugin-driven** - Plugins own their commands
3. **Conflict-free** - Registry prevents duplicates
4. **Performant** - O(1) lookups, <100ms routing
5. **Discoverable** - Auto-generated help
6. **Extensible** - Easy to add new commands
7. **Type-safe** - Dataclasses with validation

## Future Enhancements

- **Command parameters** - `/test --unit` or `/deploy production`
- **Context-aware commands** - Different behavior based on workspace
- **Dynamic aliases** - User-defined shortcuts
- **Command history** - Track which commands are used
- **Auto-complete** - VS Code completion for commands
- **Command chaining** - `/mac && /setup && /test`

## See Also

- **Plugin System:** `src/plugins/base_plugin.py`
- **Command Registry:** `src/plugins/command_registry.py`
- **Router Integration:** `src/router.py`
- **VS Code Extension:** `cortex-extension/src/cortex/chatParticipant.ts`
- **User Documentation:** `prompts/user/cortex.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file
