# LENS Consolidation Migration Guide

**Date:** 2026-02-02  
**Version:** LENS 2.0  
**Authority:** CORE-035 (Single Canonical Implementation)

---

## 🎯 What Changed

All CORTEX LENS components consolidated into **unified `cortex.lens` package**:

- ✅ **7 analyzers** moved from `cortex/brain/analysis/` → `cortex/lens/analyzers/`
- ✅ **2 discovery plugins** moved from `cortex/brain/discovery/` → `cortex/lens/discovery/`
- ✅ **LENSOrchestrator** moved from `cortex/orchestrators/support/` → `cortex/lens/`
- ✅ **MCP tools** updated to import from `cortex.lens.*`
- ✅ **Deprecation stubs** created in old locations (emit warnings)

---

## 🔄 Import Migration (Required)

### Before (Old Paths - DEPRECATED)

```python
# OLD - Scattered across codebase
from cortex.brain.analysis.ast_analyzer import ASTAnalyzer
from cortex.brain.analysis.git_history_analyzer import GitHistoryAnalyzer
from cortex.brain.analysis.comment_extractor import CommentExtractor
from cortex.brain.analysis.config_analyzer import ConfigAnalyzer
from cortex.brain.analysis.database_analyzer import DatabaseAnalyzer
from cortex.brain.analysis.api_analyzer import APIAnalyzer
from cortex.brain.analysis.dependency_analyzer import DependencyAnalyzer

from cortex.brain.discovery.config_discovery import ConfigurationDiscovery
from cortex.brain.discovery.database_discovery import DatabaseDiscovery

from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
```

### After (New Paths - PRODUCTION)

```python
# NEW - Unified in cortex.lens package
from cortex.lens import LENSOrchestrator
from cortex.lens.analyzers import (
    ASTAnalyzer,
    GitHistoryAnalyzer,
    CommentExtractor,
    ConfigAnalyzer,
    DatabaseAnalyzer,
    APIAnalyzer,
    DependencyAnalyzer,
)
from cortex.lens.discovery import ConfigurationDiscovery, DatabaseDiscovery
```

---

## ⚡ Quick Migration Script

**Find and replace** across your codebase:

```python
# Step 1: Update LENSOrchestrator imports
from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator
→
from cortex.lens import LENSOrchestrator

# Step 2: Update analyzer imports (bulk replace)
from cortex.brain.analysis.ast_analyzer import ASTAnalyzer
→
from cortex.lens.analyzers import ASTAnalyzer

from cortex.brain.analysis.git_history_analyzer import GitHistoryAnalyzer
→
from cortex.lens.analyzers import GitHistoryAnalyzer

# Step 3: Update discovery imports
from cortex.brain.discovery.config_discovery import ConfigurationDiscovery
→
from cortex.lens.discovery import ConfigurationDiscovery
```

**PowerShell find/replace:**
```powershell
# Find all Python files with old imports
Get-ChildItem -Recurse -Include *.py | Select-String "from cortex\.brain\.analysis" | Select Path -Unique

# Replace in file (example)
(Get-Content tests\unit\analysis\test_ast.py) -replace 'from cortex\.brain\.analysis\.ast_analyzer', 'from cortex.lens.analyzers' | Set-Content tests\unit\analysis\test_ast.py
```

---

## 📦 Package Structure

### Before (Scattered)

```
cortex/
├── brain/
│   ├── analysis/
│   │   ├── ast_analyzer.py           # LENS
│   │   ├── git_history_analyzer.py   # LENS
│   │   ├── comment_extractor.py      # LENS
│   │   ├── config_analyzer.py        # LENS
│   │   ├── database_analyzer.py      # LENS
│   │   ├── api_analyzer.py           # LENS
│   │   ├── dependency_analyzer.py    # LENS
│   │   ├── remote_git_adapter.py     # Not LENS
│   │   └── vision_analyzer.py        # Not LENS
│   └── discovery/
│       ├── config_discovery.py       # LENS
│       ├── database_discovery.py     # LENS
│       └── __init__.py
└── orchestrators/
    └── support/
        └── lens_orchestrator.py      # LENS
```

### After (Unified)

```
cortex/
├── lens/                              # NEW - All LENS here
│   ├── __init__.py
│   ├── README.md
│   ├── orchestrator.py                # LENSOrchestrator
│   ├── analyzers/
│   │   ├── __init__.py
│   │   ├── ast_analyzer.py
│   │   ├── git_history_analyzer.py
│   │   ├── comment_extractor.py
│   │   ├── config_analyzer.py
│   │   ├── database_analyzer.py
│   │   ├── api_analyzer.py
│   │   └── dependency_analyzer.py
│   └── discovery/
│       ├── __init__.py
│       ├── config_discovery.py
│       └── database_discovery.py
└── brain/
    └── analysis/
        ├── remote_git_adapter.py      # Stays (not LENS-specific)
        ├── vision_analyzer.py         # Stays (not LENS-specific)
        └── _LENS_MOVED_TO_cortex_lens.md  # Deprecation notice
```

---

## 🧪 Test Migration

Update test imports:

```python
# OLD tests/unit/analysis/test_ast_analyzer.py
from cortex.brain.analysis.ast_analyzer import ASTAnalyzer

# NEW tests/unit/lens/analyzers/test_ast_analyzer.py
from cortex.lens.analyzers import ASTAnalyzer
```

**Move test files:**
```
tests/unit/analysis/test_ast_analyzer.py → tests/unit/lens/analyzers/test_ast_analyzer.py
```

---

## ⚠️ Breaking Changes

### 1. No Backward Compatibility (ARCH-006)

Old imports will **fail** (or emit deprecation warnings via stub for 1 sprint).

### 2. Module Paths Changed

- `cortex.brain.analysis.*` → `cortex.lens.analyzers.*`
- `cortex.brain.discovery.*` → `cortex.lens.discovery.*`
- `cortex.orchestrators.support.lens_orchestrator` → `cortex.lens.orchestrator`

### 3. Deprecation Stubs (Temporary)

Old paths have deprecation stubs that emit warnings:

```python
DeprecationWarning: Importing LENSOrchestrator from cortex.orchestrators.support.lens_orchestrator is deprecated. 
Use 'from cortex.lens import LENSOrchestrator' instead. 
This stub will be removed in next sprint.
```

**Stubs removed:** Next sprint (2 weeks)

---

## ✅ Verification Checklist

After migration, verify:

- [ ] All tests pass: `pytest tests/unit/lens/`
- [ ] No deprecation warnings in test output
- [ ] MCP tools functional: `curl http://localhost:8000/tools`
- [ ] LENSOrchestrator imports correctly:
  ```python
  from cortex.lens import LENSOrchestrator
  orchestrator = LENSOrchestrator()
  ```
- [ ] Analyzers import correctly:
  ```python
  from cortex.lens.analyzers import ASTAnalyzer
  analyzer = ASTAnalyzer()
  ```

---

## 🔧 Troubleshooting

### Issue: `ModuleNotFoundError: No module named 'cortex.brain.analysis.ast_analyzer'`

**Solution:** Update import to `from cortex.lens.analyzers import ASTAnalyzer`

### Issue: `ImportError: cannot import name 'LENSOrchestrator' from 'cortex.orchestrators.support'`

**Solution:** Update import to `from cortex.lens import LENSOrchestrator`

### Issue: Deprecation warnings flooding test output

**Solution:** Update all imports to new paths. Warnings removed once stubs deleted.

### Issue: Tests fail after migration

**Solution:** 
1. Check test file imports updated
2. Verify test fixtures use new paths
3. Run `pytest -v` for detailed error messages

---

## 📚 Resources

- **Package README:** `cortex/lens/README.md`
- **MCP Tools:** `cortex/mcp/tools/lens_tools.py`
- **Deprecation Notices:**
  - `cortex/brain/analysis/_LENS_MOVED_TO_cortex_lens.md`
  - `cortex/brain/discovery/_LENS_MOVED_TO_cortex_lens.md`
  - `cortex/orchestrators/support/lens_orchestrator.py` (stub)

---

## 🎯 Benefits of Consolidation

1. **Discoverability** - All LENS components in one place
2. **Clarity** - `from cortex.lens import X` is intuitive
3. **Maintainability** - Single package to version and deploy
4. **MCP-First** - Clear boundary: `cortex.lens` (backend) → `cortex/mcp/tools/` (gateway)
5. **Separation** - Backend Python distinct from frontend HTML/JS (`cortex-lens/` folder)

---

*LENS Consolidation complete. Update your imports today. Deprecation stubs removed next sprint.*
