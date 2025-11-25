# CORTEX Help System

**Quick command reference for CORTEX entry points.**

Struggling to remember commands? The help system provides concise, bulletted command lists that are easy to scan and memorize.

---

## 🎯 Quick Access

### In Python
```python
from src.cortex_help import cortex_help, get_quick_reference

# Concise help (recommended)
print(cortex_help())

# Ultra-concise quick reference
print(get_quick_reference())
```

### Command Line
```bash
# Quick reference (ultra-concise)
python scripts/cortex_help_cli.py --quick

# Concise help (default)
python scripts/cortex_help_cli.py

# Detailed help with examples
python scripts/cortex_help_cli.py --detailed

# Category overview
python scripts/cortex_help_cli.py --category
```

### In GitHub Copilot Chat
```
/CORTEX help
/help
show me available commands
what commands can I use?
```

---

## 📋 Help Formats

### 1. Quick Reference (Ultra-Concise)
**Use when:** You just need a quick reminder of core commands.

**Output:**
```
**CORTEX Quick Commands:**

• /help - Show all commands
• /setup - Configure environment
• /resume - Continue last conversation
• /status - Show progress

💡 Or just use natural language - CORTEX understands!
```

**Access:**
```python
from src.cortex_help import get_quick_reference
print(get_quick_reference())
```

---

### 2. Concise Help (Recommended)
**Use when:** You want a complete command list that's easy to scan.

**Output:**
```
🧠 CORTEX Quick Command Reference

💡 *Tip: Natural language works everywhere! Commands are optional shortcuts.*

**DOCUMENTATION**
• `/help` (`/h`, `/?`) - Show all available commands and help
  *Say: "show me all available commands"*

**SESSION**
• `/resume` (`/continue`) - Resume from where you left off
  *Say: "resume work"*
• `/status` (`/progress`) - Show current work status and progress
  *Say: "show progress"*

---
📊 3 commands • 1 plugins
```

**Access:**
```python
from src.cortex_help import cortex_help
print(cortex_help())  # Default format
```

---

### 3. Detailed Help
**Use when:** You need examples and full descriptions.

**Output:**
```
# CORTEX Command Reference (Detailed)

**Commands are shortcuts. Natural language works everywhere!**

## Documentation

### `/help`

Show all available commands and help

**Natural Language:** "show me all available commands"

**Aliases:** `/h`, `/?`

**Examples:**
- `@cortex /help`
- `/help`

---
```

**Access:**
```python
from src.cortex_help import show_help, HelpFormat
print(show_help(HelpFormat.DETAILED))
```

---

### 4. Category Overview
**Use when:** You want to see commands organized by category.

**Output:**
```
# CORTEX Commands by Category

| Category | Commands | Description |
|----------|----------|-------------|
| Documentation | 1 | Help and documentation |
| Session | 2 | Conversation and session management |
```

**Access:**
```python
from src.cortex_help import show_help, HelpFormat
print(show_help(HelpFormat.CATEGORY))
```

---

## 🎨 Intelligent Request Handling

The help system understands natural language requests:

```python
from src.cortex_help import handle_help_request

# Automatically detects intent
handle_help_request("show help")           # → Concise help
handle_help_request("quick reference")     # → Ultra-concise
handle_help_request("detailed help")       # → Detailed help
handle_help_request("platform commands")   # → Platform category only
handle_help_request("show categories")     # → Category overview
```

---

## 🔌 Integration with Router

The help system is automatically integrated with the CORTEX router:

```python
from src.router import CortexRouter

router = CortexRouter()
result = router.process_request("/help")

# result['help_text'] contains formatted help
print(result['help_text'])
```

**Supported help commands:**
- `/help` - Show concise help
- `/h` - Short alias
- `/?` - Alternative alias

---

## 🎯 Filtering by Category

```python
from src.cortex_help import show_help, HelpFormat
from src.plugins.command_registry import CommandCategory

# Show only platform commands
print(show_help(HelpFormat.CONCISE, CommandCategory.PLATFORM))

# Show only session commands
print(show_help(HelpFormat.CONCISE, CommandCategory.SESSION))
```

**Available categories:**
- `PLATFORM` - Environment and platform management
- `WORKFLOW` - Task and workflow control
- `SESSION` - Conversation and session management
- `DOCUMENTATION` - Help and documentation
- `TESTING` - Test execution and validation
- `MAINTENANCE` - Cleanup and optimization
- `EXTENSION` - VS Code extension features
- `CUSTOM` - User-defined commands

---

## 📊 Command Statistics

```python
from src.plugins.command_registry import get_command_registry

registry = get_command_registry()
stats = registry.get_stats()

print(f"Total commands: {stats['unique_commands']}")
print(f"Plugins: {stats['total_plugins']}")
print(f"Categories: {stats['categories']}")
```

---

## 🚀 Usage Examples

### Example 1: Quick Check During Development
```python
from src.cortex_help import get_quick_reference
print(get_quick_reference())
```

### Example 2: Full Command List
```python
from src.cortex_help import cortex_help
print(cortex_help())
```

### Example 3: Learning With Examples
```python
from src.cortex_help import show_help, HelpFormat
print(show_help(HelpFormat.DETAILED))
```

### Example 4: Category-Specific Help
```python
from src.cortex_help import handle_help_request
print(handle_help_request("show platform commands"))
```

---

## 🧪 Testing

Run the test suite:
```bash
pytest tests/test_cortex_help.py -v
```

**Test coverage:**
- ✅ Help generation in all formats
- ✅ Category filtering
- ✅ Quick reference
- ✅ Intelligent request handling
- ✅ Command registry integration
- ✅ Markdown formatting
- ✅ Edge cases (empty categories, etc.)

---

## 💡 Design Philosophy

**Principles:**
1. **Natural language first** - Commands are optional shortcuts
2. **Progressive disclosure** - Start simple, add detail as needed
3. **Easy to scan** - Bulletted lists, clear categories
4. **Memory-friendly** - Concise formats you can actually remember
5. **Context-aware** - Intelligent handling of help requests

**Why multiple formats?**
- **Quick reference** - For quick reminders
- **Concise** - For complete list that's easy to scan
- **Detailed** - For learning with examples
- **Category** - For understanding organization

---

## 🔧 Implementation Details

**Architecture:**
- `src/cortex_help.py` - Core help generation
- `src/router.py` - Integration with router (handles `/help`)
- `scripts/cortex_help_cli.py` - Command-line interface
- `tests/test_cortex_help.py` - Comprehensive test suite

**Performance:**
- Help generation: <10ms
- Category filtering: O(1) lookup
- No external dependencies

---

## 📚 API Reference

### `cortex_help() -> str`
Quick access to concise help. Recommended for most use cases.

### `get_quick_reference() -> str`
Ultra-concise reference with just the essentials.

### `show_help(format: HelpFormat, category: Optional[CommandCategory] = None) -> str`
Full-featured help generation with format and category options.

### `handle_help_request(request: str) -> str`
Intelligent help handling based on natural language request.

### `HelpFormat` enum
- `CONCISE` - Bulletted command list (default)
- `DETAILED` - Full descriptions with examples
- `CATEGORY` - Organized by category

---

## 🎯 Future Enhancements

**Planned features:**
- [ ] Interactive help in VS Code extension
- [ ] Search within help (e.g., "find commands related to testing")
- [ ] Custom format templates
- [ ] Export to different formats (PDF, HTML)
- [ ] Command usage statistics

---

**Last Updated:** 2025-11-10  
**Version:** 1.0  
**Status:** Production Ready ✅

**Part of CORTEX 2.0 - Modular Architecture**
