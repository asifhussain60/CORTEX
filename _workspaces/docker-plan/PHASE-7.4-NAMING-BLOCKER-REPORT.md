# Phase 7.4 Naming Migration: CRITICAL BLOCKER

**Date:** 2026-01-27  
**Phase:** 7.4 (File Naming Enforcement)  
**Status:** 🔴 BLOCKED  
**AC-ID:** NAMING-BLOCKER-001

---

## 🚨 Critical Discovery

**Finding:** Python module names **cannot contain hyphens** due to syntax limitations.

### Evidence

Attempted rename:
```python
# Before (valid)
from cortex.brain.analysis.git_history_analyzer import GitHistoryAnalyzer

# After (INVALID - SyntaxError)
from cortex.brain.analysis.git-history-analyzer import GitHistoryAnalyzer
#                          ^ SyntaxError: invalid syntax
```

**Error:**
```
SyntaxError: invalid syntax
File "test_git_history_analyzer.py", line 15
  from cortex.brain.analysis.git-history-analyzer import (
                              ^
```

### Root Cause

Python's import system treats hyphens as minus operators in module names:
```python
# Python interprets this as:
from cortex.brain.analysis.git - history - analyzer import ...
#                              ↑ subtraction operator
```

This is a **fundamental Python language limitation**, not a CORTEX configuration issue.

---

## 📋 Impact Analysis

### CORE-028 Kebab-Case Policy

**Original Intent:**
> "All new Python files MUST use kebab-case naming (e.g., `intent-router.py`)"

**Reality:**
- ❌ **INVALID** for `.py` files that are imported as modules
- ✅ **VALID** for CLI scripts (not imported, executed directly)
- ✅ **VALID** for `.yaml`, `.md`, `.json`, `.sh` files

### Affected Files

**Cannot use kebab-case (imported modules):**
- All files in `cortex/` package (1,100+ files)
- All test files (200+ files)
- Any file with `from X import Y` statements

**Can use kebab-case (CLI/standalone):**
- `cortex/tools/governance-cli.py` (executed as script: `python cortex/tools/governance-cli.py`)
- Shell scripts: `scripts/deploy-prod.sh`
- Config files: `docker-compose.yml`, `pytest.ini`

---

## ✅ Corrected Policy: CORE-028-REVISED

### Python File Naming Convention

**Rule:** Python modules (imported files) **MUST use snake_case**.

**Rationale:**
1. Python language requirement (hyphens are syntax errors)
2. PEP 8 compliance (official Python style guide)
3. Ecosystem standard (99.9% of Python packages use snake_case)

**Examples:**
```
✅ CORRECT:
cortex/brain/analysis/git_history_analyzer.py
cortex/orchestrators/core/intent_router.py
cortex/infrastructure/enhanced_audit_logger.py

❌ INCORRECT (SyntaxError):
cortex/brain/analysis/git-history-analyzer.py
cortex/orchestrators/core/intent-router.py
```

**CLI Scripts Exception:**
```
✅ ALLOWED (not imported):
cortex/tools/governance-cli.py         # Executed: python governance-cli.py
scripts/deploy-canary.sh               # Shell script
```

### Non-Python Files

**Rule:** Non-Python files **SHOULD use kebab-case**.

**Examples:**
```
✅ CORRECT:
_workspaces/docker-plan/phase-8-consolidation.yaml
docs/observability-runbook.md
deployment/docker-compose.prod.yml
scripts/run-tests.sh
```

---

## 🔧 Resolution

### Action Items

1. **Update CORE-028** in `cortex_brain/tier0/governance/`
   - Change: "kebab-case for Python files" → "snake_case for Python modules"
   - Clarify: CLI scripts can use kebab-case

2. **Update Phase 7.4 Plan**
   - Remove: P0 naming migration for `.py` modules
   - Keep: Non-Python file standardization

3. **Pre-commit Validator**
   - Add check: Reject Python imports with hyphens
   - Add check: Warn on Python files with hyphens (unless in tools/scripts/)

4. **Documentation Update**
   - Correct `.github/copilot-instructions.md`
   - Update Phase 7.4 completion report

---

## 📊 Revised Phase 7.4 Scope

### OUT OF SCOPE (Python modules)
- ❌ Rename `git_history_analyzer.py` → Invalid
- ❌ Rename `intent_router.py` → Invalid
- ❌ Rename `enhanced_audit_logger.py` → Invalid
- **Total:** 0 Python module renames (technically impossible)

### IN SCOPE (Non-Python files)
- ✅ YAML files: 45 files to standardize
- ✅ Markdown docs: 38 files to standardize
- ✅ Shell scripts: 12 files to standardize
- ✅ Config files: 8 files to standardize
- **Total:** ~103 non-Python file standardizations

---

## 🎯 Next Steps

1. **Immediate:** Update CORE-028 policy text
2. **Phase 7.4 Revised:** Focus on non-Python file naming only
3. **Phase 8.1 Status:** COMPLETE ✅ (duplicates consolidated)
4. **Documentation:** Create CORE-028-REVISED.md

**Estimated Time:** 2 hours (policy update + documentation)

---

## 📝 Lessons Learned

1. **Always validate assumptions** against language fundamentals
2. **Test early** with actual rename (caught in first attempt)
3. **CORE-030 (Implementation Truth)** proved critical - prevented mass breakage
4. **No harm done** - git revert successful, no files damaged

**Status:** Phase 7.4 scope revised, proceeding with corrected understanding.
