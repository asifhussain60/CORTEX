# 🧹 CORTEX Cleanup System

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Website:** https://asifhussain60.github.io/CORTEX/  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Comprehensive workspace cleanup orchestrator for CORTEX that:
1. **Clears VS Code caches** for fresh state
2. **Validates response templates** (visual progress bars, autonomous execution)
3. **Removes deprecated references** (5-part templates, old configs)
4. **Resolves duplicate files** (keeps latest, deletes conflicts)
5. **Runs holistic validation** in a loop until clean

---

## ⚡ Quick Commands

| Command | Description |
|---------|-------------|
| `cleanup full` | Run all 5 phases end-to-end |
| `cleanup cache` | Clear VS Code caches only |
| `cleanup validate` | Run holistic validation only |
| `cleanup duplicates` | Resolve duplicate files only |
| `cleanup legacy` | Remove deprecated references only |

---

## 🔄 5-Phase Cleanup Pipeline

### Phase 1: VS Code Cache Clear
**Purpose:** Remove stale cached data for fresh workspace state

**Actions:**
```bash
# Clear VS Code workspace cache
rm -rf ~/Library/Application\ Support/Code/Cache/*
rm -rf ~/Library/Application\ Support/Code/CachedData/*
rm -rf ~/Library/Application\ Support/Code/CachedExtensions/*
rm -rf ~/Library/Application\ Support/Code/CachedExtensionVSIXs/*

# Clear workspace-specific state
rm -rf .vscode/.history/
rm -rf .vscode/.cache/
rm -rf .vscode/*.log

# Clear Python caches
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null
find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null
```

**Python Toolkit:** `cortex-toolkit/maintenance/clear_caches.py`

---

### Phase 2: Response Template Validation
**Purpose:** Ensure visual progress bars are wired correctly

**Validation Checks:**

| Check | Expected Value | File(s) to Verify |
|-------|----------------|-------------------|
| Planning progress template | `autonomous_execution_progress` | `planning_orchestrator.py` |
| ADO progress template | `ado_execution_progress` | `ado_orchestrator.py` |
| Maintenance progress template | `maintenance_execution_progress` | `cortex-maintenance.prompt.md` |
| Sanitization progress template | `sanitization_execution_progress` | `code-sanitization-manifest.yaml` |
| Refinement progress template | `refinement_execution_progress` | `refinement-orchestrator-manifest.yaml` |

**Visual Progress Bar Requirements:**
- ✅ Unicode block characters: `█` (filled) `░` (empty)
- ✅ Percentage display: `[████████░░░░░░░░░░░░] 40%`
- ✅ Phase table with status emojis: ✅ ⏳ ⏸️
- ✅ TDD status column (where applicable)
- ✅ Time tracking (elapsed/remaining)

**Key Files:**
- `cortex-brain/response-templates-v4.yaml` (canonical source)
- `cortex-brain/response-templates/base-components.yaml` (component definitions)
- `src/response_templates/template_renderer.py` (rendering logic)

---

### Phase 3: Autonomous Execution Validation
**Purpose:** Ensure autonomous execution defaults to `true`

**Validation Points:**

| Location | Setting | Expected |
|----------|---------|----------|
| `planning_orchestrator.py` | `auto_execute` kwarg default | `True` |
| `planning_orchestrator.py` | `enable_autonomous_execution` config | `True` |
| `ado_orchestrator.py` | `autonomous_execution` in copilot_instructions | `True` |
| `plan_executor.py` | Default execution mode | `ExecutionMode.AUTONOMOUS` |

**Search Pattern:**
```python
# Must find: default=True or True as explicit value
kwargs.get("auto_execute", True)
config.get("enable_autonomous_execution", True)
"autonomous_execution": True
```

---

### Phase 4: Legacy Reference Removal
**Purpose:** Remove ALL references to deprecated 5-part response templates

**Target Patterns to DELETE:**
```yaml
# MUST NOT EXIST in any file:
inherits_from: core/base-templates/5-part-standard.yaml
5-part-standard
five-part-standard
5_part_standard
```

**Files to Check:**
- `cortex-brain/response-templates/**/*.yaml`
- `.github/prompts/*.md`
- `cortex-brain/*.yaml`

**Safe to Delete (if exists):**
- `cortex-brain/response-templates/core/base-templates/5-part-standard.yaml`

**Replacement Template:** `core/base-templates/adaptive-base.yaml`

---

### Phase 5: Duplicate File Resolution
**Purpose:** Find and resolve conflicting duplicate files

**Detection Algorithm:**
1. Find files with same base name in different locations
2. Compare content hashes (SHA-256)
3. If different content: identify correct version by:
   - Version number in header
   - Last modification date
   - Line count (more comprehensive usually correct)
4. Keep correct version, delete others

**Common Duplicate Patterns:**
```
# Response templates (check for duplicates)
cortex-brain/response-templates.yaml
cortex-brain/response-templates-v4.yaml       # ← Keep v4
cortex-brain/templates/response-templates-condensed.yaml

# Planning manifests (check for old versions)
cortex-brain/manifests/orchestrators/planning-system-*.yaml
# Keep: planning-system-4.0-manifest.yaml
# Delete: planning-system-3.x-manifest.yaml, planning-system-v3-*.yaml
```

**Python Toolkit:** `cortex-toolkit/maintenance/detect_duplicates.py`

---

## 🔁 Holistic Validation Loop

After all phases complete, run validation loop:

```
LOOP until no_issues_found:
    1. Search for 5-part references → Fix if found
    2. Verify all progress templates registered → Register if missing
    3. Check autonomous_execution=True → Set if false
    4. Scan for duplicate files → Resolve conflicts
    5. Validate YAML syntax → Fix if broken
    6. Run test suite → Fix failures
    
    IF issues_found == 0:
        BREAK with success
    ELSE:
        INCREMENT loop_count
        IF loop_count > MAX_ITERATIONS (5):
            REPORT remaining issues and EXIT
```

---

## 📊 Visual Progress Template

```
## 🧠 CORTEX Cleanup System
**Author:** Asif Hussain | **Operation:** Full Cleanup

---

### 📊 Cleanup Progress
```
╔══════════════════════════════════════════════════════════════════════════╗
║  Operation: CORTEX Full Cleanup                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Overall: [████████████░░░░░░░░] 60%  ⏳                                  ║
║  Phase 3/5: Legacy Reference Removal                                     ║
║  Issues: 4 found | 2 fixed                                               ║
║  Time: 2m 15s elapsed | ~1m 30s remaining                                ║
╚══════════════════════════════════════════════════════════════════════════╝
```

### 📋 Cleanup Phases

| # | Phase | Status | Progress | Issues | Time |
|---|-------|--------|----------|--------|------|
| 1 | ✅ **Cache Clear** | Complete | [██████████] 100% | 0 | 15s |
| 2 | ✅ **Template Validation** | Complete | [██████████] 100% | 1 fixed | 45s |
| 3 | ⏳ **Legacy Removal** | In Progress | [██████░░░░] 60% | 2 found | 1m |
| 4 | ⏸️ **Duplicate Resolution** | Not Started | [░░░░░░░░░░] 0% | - | - |
| 5 | ⏸️ **Holistic Validation** | Not Started | [░░░░░░░░░░] 0% | - | - |

**Next:** Removing `inherits_from: 5-part-standard.yaml` from 3 files...
```

---

## 🐍 Python Toolkit Scripts

### Script 1: `clear_caches.py`
Location: `cortex-toolkit/maintenance/clear_caches.py`

```python
# Features:
# - Cross-platform (macOS, Windows, Linux)
# - VS Code cache directories
# - Python __pycache__ and .pyc
# - pytest/mypy caches
# - Workspace-specific caches
# - Dry-run mode
# - Size reporting
```

### Script 2: `validate_templates.py`
Location: `cortex-toolkit/maintenance/validate_templates.py`

```python
# Features:
# - Verify all orchestrators reference correct templates
# - Check visual progress bar components exist
# - Validate autonomous_execution defaults
# - Report missing/broken references
# - Auto-fix capability
```

### Script 3: `remove_legacy_refs.py`
Location: `cortex-toolkit/maintenance/remove_legacy_refs.py`

```python
# Features:
# - Search for 5-part-standard references
# - Safe removal with backup
# - Update to adaptive-base.yaml
# - Dry-run mode
# - Detailed report
```

### Script 4: `resolve_duplicates.py`
Location: `cortex-toolkit/maintenance/resolve_duplicates.py`

```python
# Features:
# - SHA-256 content hashing
# - Version detection from headers
# - Modification date comparison
# - Interactive or auto mode
# - Backup before deletion
```

---

## 🛡️ Safety Rules

| Rule | Enforcement |
|------|-------------|
| **BACKUP_FIRST** | Create .cleanup-backup/ before any deletion |
| **DRY_RUN_DEFAULT** | All scripts default to dry-run mode |
| **GIT_CHECK** | Warn if uncommitted changes exist |
| **BRAIN_PROTECTION** | Never delete cortex-brain/tier0/ files |
| **MANIFEST_VERIFY** | Validate YAML syntax after edits |

---

## 📁 Cleanup Targets

### ✅ Safe to Clean
- `__pycache__/` directories
- `.pytest_cache/` directories
- `.mypy_cache/` directories
- VS Code cache files
- Old manifest versions (<4.0)
- Duplicate/conflicting files
- Empty directories

### ⚠️ Requires Confirmation
- Response template files
- Orchestrator manifests
- Brain tier files
- Configuration files

### ❌ Never Delete
- `cortex-brain/tier0/` (governance)
- `cortex-brain/brain-protection-rules.yaml`
- `.git/` directory
- Active planning documents
- User conversation history

---

## 🔍 Validation Queries

### Find 5-part References
```bash
grep -r "5-part\|five-part\|5_part" cortex-brain/ --include="*.yaml" --include="*.md"
```

### Check Progress Template Registration
```bash
grep -r "response_template.*progress" src/orchestrators/ --include="*.py"
```

### Verify Autonomous Execution
```bash
grep -r "auto_execute\|autonomous_execution\|enable_autonomous" src/ --include="*.py"
```

### Find Duplicate Files
```bash
# Using toolkit script
python cortex-toolkit/maintenance/detect_duplicates.py --report
```

---

## 🚀 Usage

### Full Cleanup (Recommended)
```bash
# Dry-run first
python cortex-toolkit/maintenance/full_cleanup.py --dry-run

# Execute
python cortex-toolkit/maintenance/full_cleanup.py --execute
```

### Individual Phases
```bash
# Phase 1: Clear caches
python cortex-toolkit/maintenance/clear_caches.py --execute

# Phase 2-3: Validate and fix templates
python cortex-toolkit/maintenance/validate_templates.py --fix

# Phase 4: Remove legacy
python cortex-toolkit/maintenance/remove_legacy_refs.py --execute

# Phase 5: Resolve duplicates
python cortex-toolkit/maintenance/resolve_duplicates.py --auto
```

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| `cortex-brain/cleanup-rules.yaml` | Dynamic cleanup rule definitions |
| `cortex-toolkit/maintenance/master_cleanup.py` | Existing master cleanup script |
| `cortex-cleanup.ps1` | PowerShell cleanup wrapper |
| `.github/prompts/cortex-maintenance.prompt.md` | 6-phase maintenance system |

---

**Anti-Bloat:** This file MUST stay under 300 lines. Details defer to toolkit scripts.
