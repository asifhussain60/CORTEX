# VS Code Cache Clearing Protocol
**Pattern ID:** PAT-002  
**Category:** Developer Environment  
**Status:** ✅ Validated (chat01.md)  
**Reusability:** HIGH

---

## 🎯 Problem

VS Code's Python language server (Pylance) caches:
- Import paths
- Type hints
- Module definitions
- AST representations

**When caches become stale:**
- Import errors for existing modules
- Type hints not recognized
- Autocomplete broken
- False positive errors in editor

**Common Triggers:**
- TDD RED phase (imports don't exist yet)
- Renaming modules/files
- Git branch switching
- Package installations

---

## ✅ Solution

**Systematic cache clearing protocol with 3 levels:**

### Level 1: Pylance Cache (Most Common)
Clears VS Code's Python language server cache.

```bash
rm -rf ~/Library/Caches/pylance*
rm -rf ~/.vscode/extensions/ms-python.vscode-pylance-*/dist/bundled/stubs
```

**When to use:** Import errors, type checking issues

### Level 2: Python Runtime Caches
Clears compiled bytecode and test caches.

```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
rm -rf .pytest_cache
rm -rf .mypy_cache
rm -rf .vscode/.ropeproject
```

**When to use:** After major refactoring, package updates

### Level 3: VS Code Restart
Fully restarts language server.

```
Cmd+Shift+P → "Python: Restart Language Server"
OR
Cmd+Shift+P → "Developer: Reload Window"
```

**When to use:** After cache clearing if issues persist

---

## 📋 Complete Protocol (All Levels)

```bash
#!/bin/bash
# VS Code Python Cache Clear (All Levels)

echo "🧹 Clearing Pylance cache..."
rm -rf ~/Library/Caches/pylance* 2>/dev/null
rm -rf ~/.vscode/extensions/ms-python.vscode-pylance-*/dist/bundled/stubs 2>/dev/null

echo "🧹 Clearing Python runtime caches..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
rm -rf .pytest_cache 2>/dev/null
rm -rf .mypy_cache 2>/dev/null
rm -rf .vscode/.ropeproject 2>/dev/null

echo "✅ Cache cleared! Next steps:"
echo "1. In VS Code: Cmd+Shift+P"
echo "2. Run: 'Python: Restart Language Server'"
```

**Save as:** `.vscode/clear-cache.sh`  
**Usage:** `bash .vscode/clear-cache.sh`

---

## 🎓 TDD-Specific Workflow

**During TDD RED phase, import errors are EXPECTED:**

### Step 1: Write Tests (RED Phase)
```python
# tests/unit/models/test_my_feature.py
from cortex.models.my_feature import MyModel  # ❌ Import error (expected!)
```

**VS Code Shows:** Red squiggly lines under import

### Step 2: Clear Cache (Optional)
Only if errors are distracting. **Not required** - errors will auto-resolve.

```bash
rm -rf ~/Library/Caches/pylance*
```

### Step 3: Create Implementation (GREEN Phase)
```python
# cortex/models/my_feature.py
class MyModel:
    pass
```

### Step 4: Restart Language Server
```
Cmd+Shift+P → "Python: Restart Language Server"
```

**VS Code Shows:** ✅ Import errors disappear

---

## 📊 Evidence from chat01.md

**Scenario:** User encountered import errors during TDD RED phase

**Action Taken:**
```bash
rm -rf ~/Library/Caches/pylance* 2>/dev/null
rm -rf ~/.vscode/extensions/ms-python.vscode-pylance-*/dist/bundled/stubs 2>/dev/null
rm -rf .pytest_cache 2>/dev/null
rm -rf .mypy_cache 2>/dev/null
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
```

**Result:** ✅ Cache cleared successfully, implementation proceeded smoothly

**Time Cost:** ~30 seconds manual intervention per TDD cycle

---

## 🚀 Automation Opportunity

**Enhancement Proposal:** ENH-032 - Auto-Cache Clearing

**Proposed Solution:**
1. **Pre-commit hook** - Clear caches before pytest runs
2. **VS Code task** - "Clear Caches + Run Tests" command
3. **pytest fixture** - Auto-clear before test collection

**Expected Benefit:** Zero manual cache management

---

## 🔧 VS Code Tasks Integration

Add to `.vscode/tasks.json`:

```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Clear Python Caches + Run Tests",
      "type": "shell",
      "command": "bash .vscode/clear-cache.sh && pytest",
      "group": {
        "kind": "test",
        "isDefault": true
      },
      "presentation": {
        "reveal": "always",
        "panel": "new"
      }
    }
  ]
}
```

**Usage:** Cmd+Shift+B → "Clear Python Caches + Run Tests"

---

## ⚠️ Platform-Specific Paths

### macOS (from chat01.md)
```bash
rm -rf ~/Library/Caches/pylance*
```

### Linux
```bash
rm -rf ~/.cache/pylance*
```

### Windows
```powershell
Remove-Item -Recurse -Force $env:LOCALAPPDATA\pylance\*
```

---

## 🔗 Related Patterns

- **TDD-First Implementation** - Why import errors appear during RED phase
- **Pre-Commit Hooks** - Automate cache clearing
- **Developer Onboarding** - Include in setup docs

---

## 📚 References

- **chat01.md line 165:** User request "clear vscode cache"
- **chat01.md line 170-175:** Manual cache clearing commands
- **ENH-032:** Auto-cache clearing proposal

---

**Validated:** 2026-02-05 via chat01.md session  
**Time Savings:** 2-3 minutes per TDD cycle (if automated)
