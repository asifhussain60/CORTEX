# CORTEX Help Command - Quick Reference Card

**Status:** ✅ Production Ready  
**Tests:** 18/18 passing  
**Version:** 1.0

---

## 🚀 Quick Usage

### Show Help
```python
# Any of these work:
execute_operation('help')
execute_operation('/help')
execute_operation('/CORTEX help')
show_help()
```

### Output Formats
```python
show_help()              # Table (default)
show_help('list')        # Simple list
show_help('detailed')    # Grouped by category
```

### Find Command
```python
from src.operations.help_command import find_command

op = find_command('cleanup')
print(op['operation_id'])  # → workspace_cleanup
print(op['status'])        # → partial
```

---

## 📊 What It Shows

**12 Operations Displayed:**
- ✅ 1 ready (refresh_cortex_story)
- 🔄 2 partial (environment_setup, workspace_cleanup)
- ⏸️ 4 pending (documentation, brain_protection, tests, self-review)
- 🎯 5 planned (CORTEX 2.1 features)

**Information Shown:**
- Status icon & name
- Quick command (shortest phrase)
- Natural language example
- Orchestration module (operation_id)

---

## 📋 Example Output

```
Status   Quick Command        Natural Language Example            Module
------------------------------------------------------------------------------------------
⏸️ pend  build docs           generate documentation              update_documentati
🔄 part   cleanup              remove temporary files              workspace_cleanup
✅ read   update story         refresh cortex story                refresh_cortex_sto
🔄 part   setup                initialize environment              environment_setup
```

---

## 📦 Files

- **Implementation:** `src/operations/help_command.py` (306 lines)
- **Tests:** `tests/operations/test_help_command.py` (18 tests)
- **Docs:** `docs/operations/help-command.md` (478 lines)
- **Integration:** `src/operations/__init__.py` (show_help added)

---

## ✅ Design Decisions

| Challenge | Solution |
|-----------|----------|
| "One word commands" | Use shortest natural language phrase |
| "Underlying module" | Show operation_id (orchestration identifier) |
| Status determination | Count implemented vs. total modules |
| Sorting | Alphabetical by quick command |

---

## 🎯 Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| ✅ | ready | 100% modules implemented |
| 🔄 | partial | Some modules implemented |
| ⏸️ | pending | Architecture ready, modules pending |
| 🎯 | planned | Design phase (CORTEX 2.1) |

---

## 🔧 Integration Points

**1. Execute Operation**
```python
report = execute_operation('help')
help_text = report.context['help_text']
```

**2. Direct Function**
```python
help_text = show_help('table')
```

**3. Natural Language**
```python
execute_operation('show me available commands')
```

---

## 🚀 Auto-Discovery

**New operations automatically appear!**

Add to `cortex-operations.yaml`:
```yaml
my_operation:
  name: "My Operation"
  natural_language: ["my cmd"]
  modules: [module1]
```

Immediately shows in help:
```
⏸️ pend  my cmd               my cmd                              my_operation
```

---

## 🎓 Future (CORTEX 2.1)

**Full operation implementation:**
- Context-aware suggestions
- Command search by keyword
- Usage history integration
- "You might also want to..." recommendations

---

## ✨ Key Benefits

- ✅ No memorization needed
- ✅ Visual status at a glance
- ✅ Multiple access methods
- ✅ Auto-discovers new operations
- ✅ Well-tested (18/18 passing)
- ✅ Three output formats
- ✅ Extensible architecture

---

**Author:** Asif Hussain  
**Date:** 2025-11-10  
**CORTEX Version:** 2.0
