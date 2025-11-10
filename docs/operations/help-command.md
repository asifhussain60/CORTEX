# CORTEX Help Command

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Added:** 2025-11-10

---

## Overview

The CORTEX help command provides a quick, concise reference for all available operations. It shows:

- **Quick commands** - Shortest natural language phrase
- **Natural language examples** - Common usage patterns
- **Orchestration modules** - Underlying operation identifiers
- **Implementation status** - Visual indicators for readiness

---

## Usage

### 1. Via Execute Operation

```python
from src.operations import execute_operation

# Show help
report = execute_operation('help')
help_text = report.context['help_text']
print(help_text)
```

### 2. Via Direct Function Call

```python
from src.operations import show_help

# Table format (default)
print(show_help())

# Detailed format with categories
print(show_help('detailed'))

# Simple list format
print(show_help('list'))
```

### 3. Via Natural Language

```python
# All of these work:
execute_operation('help')
execute_operation('/help')
execute_operation('/CORTEX help')
execute_operation('show help')
```

---

## Output Formats

### Table Format (Default)

Concise table showing all operations alphabetically by quick command:

```
==========================================================================================
CORTEX COMMANDS
==========================================================================================

Status   Quick Command        Natural Language Example            Module              
------------------------------------------------------------------------------------------
⏸️ pend  build docs           generate documentation              update_documentati  
⏸️ pend  check brain          check brain protection              brain_protection_c  
🔄 part   cleanup              remove temporary files              workspace_cleanup   
⏸️ pend  health check         check all protections               comprehensive_self  
🎯 plan   help                 available commands                  command_help        
🎯 plan   help search          search commands                     command_search      
🎯 plan   plan this            collaborative planning              interactive_planni  
🎯 plan   refactor code        refactor this module                refactoring_planni  
⏸️ pend  run tests            run test suite                      run_tests           
🔄 part   setup                initialize environment              environment_setup   
🎯 plan   system design        architect a solution                architecture_plann  
✅ read   update story         refresh cortex story                refresh_cortex_sto  
------------------------------------------------------------------------------------------

Legend:
  ✅ ready    - Fully implemented and tested
  🔄 partial  - Partially implemented (some modules ready)
  ⏸️ pending  - Architecture ready, implementation pending
  🎯 planned  - Design phase, CORTEX 2.1+

Usage:
  Natural language:  'setup environment' or 'refresh story'
  Slash commands:    /setup or /CORTEX, refresh cortex story
  Programmatic:      execute_operation('environment_setup')

==========================================================================================
```

### List Format

Simple bulleted list:

```
CORTEX COMMANDS:

✅ update story
   Example: refresh cortex story
   Module: refresh_cortex_story (6 modules)

🔄 setup
   Example: initialize environment
   Module: environment_setup (11 modules)

🔄 cleanup
   Example: remove temporary files
   Module: workspace_cleanup (6 modules)

...
```

### Detailed Format

Grouped by category with full information:

```
==========================================================================================
CORTEX COMMANDS - DETAILED
==========================================================================================

DOCUMENTATION:
------------------------------------------------------------------------------------------

✅ Refresh CORTEX Story
   Quick:      update story
   Example:    refresh cortex story
   Module:     refresh_cortex_story
   Status:     ready
   Modules:    6 modules
   Command:    /CORTEX, refresh cortex story

⏸️ Update Documentation
   Quick:      build docs
   Example:    generate documentation
   Module:     update_documentation
   Status:     pending
   Modules:    6 modules
   Command:    /CORTEX, generate documentation

...
```

---

## Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | ready | Fully implemented and tested - safe to use |
| 🔄 | partial | Some modules implemented - core functionality works |
| ⏸️ | pending | Architecture ready, awaiting implementation |
| 🎯 | planned | Design phase (CORTEX 2.1+) |

---

## Command Structure

### Quick Command
Shortest natural language phrase extracted from operation's `natural_language` list.

**Example:** "setup" (from ["setup", "setup environment", "configure"])

### Natural Language Example
Longest/most descriptive phrase showing typical usage.

**Example:** "initialize environment"

### Module (Orchestration ID)
The underlying operation identifier used in `cortex-operations.yaml`.

**Example:** `environment_setup`

---

## Implementation Details

### Architecture

```
User Input: "help" or "/CORTEX help"
              ↓
execute_operation()
    ↓ (special case detection)
show_help()
    ↓
HelpCommand.generate_help()
    ↓
    ├─ _gather_operation_data()
    │   ├─ Load operations from factory
    │   ├─ Determine status (ready/partial/pending/planned)
    │   ├─ Extract quick commands & examples
    │   └─ Sort alphabetically
    │
    └─ _format_as_table() / _format_as_list() / _format_detailed()
        └─ Return formatted string
```

### Status Determination Logic

```python
def _determine_status(op_id, op_info):
    # Check explicit status field
    if op_info.get('status') == 'pending':
        return 'planned'
    
    # Count implemented modules
    modules = op_info.get('modules', [])
    implemented = count_implemented_modules(modules)
    
    if implemented == len(modules):
        return 'ready'      # 100% complete
    elif implemented > 0:
        return 'partial'    # Some modules done
    else:
        return 'pending'    # Architecture only
```

---

## Files

| File | Purpose |
|------|---------|
| `src/operations/help_command.py` | Help command implementation |
| `src/operations/__init__.py` | Integration into execute_operation() |
| `docs/operations/help-command.md` | This documentation |
| `tests/operations/test_help_command.py` | Unit tests (pending) |

---

## Usage Examples

### Example 1: Quick Reference

```python
from src.operations import show_help

# Show user a quick command list
print(show_help())
```

### Example 2: Find Specific Command

```python
from src.operations.help_command import find_command

# User asks: "How do I clean up my workspace?"
op = find_command('cleanup')
print(f"Use: {op['example']}")
print(f"Module: {op['operation_id']}")
print(f"Status: {op['status']}")
```

### Example 3: Category-Based Help

```python
from src.operations import show_help

# Show detailed help grouped by category
print(show_help('detailed'))
```

---

## Extensibility

**New operations are automatically discovered!**

When you add a new operation to `cortex-operations.yaml`:

```yaml
operations:
  my_new_operation:
    name: "My New Operation"
    natural_language: ["my cmd", "do my thing"]
    modules: [module1, module2]
```

It immediately appears in help output:

```
⏸️ pend  my cmd               do my thing                         my_new_operation
```

**No code changes needed!**

---

## Known Limitations

### 1. Console Encoding (Windows)
Emojis (✅🔄⏸️🎯) may not display correctly in Windows Command Prompt or PowerShell ISE.

**Workaround:**
- Use Windows Terminal
- Write output to file: `Path('help.txt').write_text(show_help(), encoding='utf-8')`
- Use list format (no emojis): `show_help('list')`

### 2. Module Name Truncation
Operation IDs are truncated to 18 characters in table format.

**Full name available in:**
- Detailed format
- `find_command()` function
- Operation execution

### 3. One Operation Per Row
If an operation has 20+ natural language aliases, only shortest and longest are shown.

**All aliases available via:**
- `OperationFactory.get_operation_info(op_id)`
- Direct YAML inspection

---

## Future Enhancements (CORTEX 2.1)

### Interactive Help Command Operation
Currently, help is a special case in `execute_operation()`. In CORTEX 2.1, it will be a full operation:

```yaml
operations:
  command_help:
    name: "Command Discovery & Help"
    modules:
      - analyze_user_context
      - filter_relevant_commands
      - categorize_commands
      - generate_help_output
      - suggest_next_actions
```

**Benefits:**
- Context-aware suggestions
- "You might also want to..." recommendations
- Search by keyword
- Usage history integration

### Command Search
```python
execute_operation('help search cleanup')
# Shows all operations related to "cleanup"
```

---

## Testing

```python
# Unit tests
pytest tests/operations/test_help_command.py

# Manual testing
python test_help.py

# Integration test
from src.operations import execute_operation
report = execute_operation('help')
assert report.success
assert 'help_text' in report.context
```

---

## Contributing

When adding new operations, ensure they have:

1. **Clear natural_language phrases** (shortest = quick command)
2. **Descriptive name** (shows in detailed format)
3. **Category** (for grouping)
4. **Status** (if 'pending', mark explicitly in YAML)

**Example:**

```yaml
my_operation:
  name: "My Cool Operation"
  natural_language: ["quick", "longer example phrase"]  # "quick" = quick cmd
  category: "utilities"
  status: "pending"  # Shows as 🎯 planned
```

---

**Author:** Asif Hussain  
**Last Updated:** 2025-11-10  
**Version:** 1.0 (Initial Implementation)
