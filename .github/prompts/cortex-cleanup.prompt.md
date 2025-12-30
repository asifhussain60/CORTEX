# 🧹 CORTEX Cleanup System (ALIAS)

**Version:** 2.0.0 | **Status:** ✅ ALIAS TO MAINTENANCE  
**Author:** Asif Hussain | **Website:** https://asifhussain60.github.io/CORTEX/  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## ⚠️ IMPORTANT: This is an Alias

**This file routes cleanup commands to the consolidated maintenance system.**

All cleanup operations are now part of **Phase 2** in `cortex-maintenance.prompt.md`.

---

## 🎯 Quick Command Routing

| User Command | Routes To | Description |
|--------------|-----------|-------------|
| `cleanup full` | `system maintenance` (all 11 phases) | Full system maintenance with cleanup |
| `cleanup cache` | Maintenance Phase 2a | Clear VS Code & Python caches |
| `cleanup validate` | Maintenance Phase 2b | Validate response templates |
| `cleanup legacy` | Maintenance Phase 2c | Remove 5-part template references |
| `cleanup duplicates` | Maintenance Phase 2d | Resolve duplicate files |
| `cleanup backups` | Maintenance Phase 2e-2g | Delete backup dirs/files |

---

## 📋 Consolidated Cleanup (Phase 2 Sub-Tasks)

**All cleanup operations execute as part of Maintenance Phase 2:**

### Phase 2: System Cleanup 🗑️
- **2a:** Clear VS Code & Python caches
- **2b:** Validate response templates (progress bars, autonomous execution)
- **2c:** Remove legacy 5-part template references
- **2d:** Resolve duplicate files
- **2e:** Delete backup directories
- **2f:** Delete backup files
- **2g:** Consolidate duplicate reports
- **2h:** Verify cleanup complete

---

## 🚀 Usage

### Run Full Maintenance (Includes All Cleanup)
```
system maintenance
```

### Run Specific Cleanup Phases
```
system maintenance --phases 2
```

---

## 📚 Documentation

**Full cleanup documentation:** See `cortex-maintenance.prompt.md` Phase 2

**Implementation details:** `cortex-brain/documents/implementation-guides/maintenance/phase-2-cleanup.md`

**Python toolkit:** `cortex-toolkit/maintenance/`
- `clear_caches.py` - Cache clearing (Phase 2a)
- `validate_templates.py` - Template validation (Phase 2b)
- `remove_legacy_refs.py` - Legacy reference removal (Phase 2c)
- `resolve_duplicates.py` - Duplicate resolution (Phase 2d)

---

## 🔗 Related Files

| File | Purpose |
|------|---------|
| `.github/prompts/cortex-maintenance.prompt.md` | **Primary system (11 phases)** |
| `cortex-brain/cleanup-rules.yaml` | Cleanup rule definitions |
| `cortex-cleanup.ps1` | PowerShell cleanup wrapper |

---

**Why Consolidate?**
1. **Single source of truth** - One maintenance system
2. **Reduced redundancy** - No duplicate cleanup logic
3. **Better integration** - Cleanup as part of holistic maintenance
4. **Consistent execution** - Same autonomous execution model
5. **Easier maintenance** - Update one file, not two

---

**Anti-Bloat:** This alias file MUST stay under 150 lines.
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
