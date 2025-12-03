# CORTEX Optimize System - Implementation Guide

**Version:** 3.2.1  
**Author:** Asif Hussain  
**Date:** December 1, 2025  
**Status:** Active

---

## 🎯 Overview

The CORTEX Optimize System automatically maintains repository health by implementing all fixes from **CORTEX-OPTIMIZATION-PLAN-2025-12-01.md**.

**Key Features:**
- ✅ **File Organization** - Moves scattered test/script files to proper directories
- ✅ **Build Artifact Cleanup** - Removes dist/, publish/, *.db files from root
- ✅ **Duplicate Removal** - Eliminates duplicate templates and logos
- ✅ **Archive Consolidation** - Cleans old archives and temporary files
- ✅ **Database Optimization** - Vacuums SQLite databases to reclaim space
- ✅ **Cache Optimization** - Clears YAML cache for fresh rebuilds
- ✅ **Dry Run Mode** - Preview changes before executing
- ✅ **Detailed Reports** - JSON reports saved to cortex-brain/documents/reports/

---

## 🚀 Usage

### Command Line

```bash
# Run all optimizations
python run_optimize.py

# Preview changes without executing (DRY RUN)
python run_optimize.py --dry-run

# Target specific optimization areas
python run_optimize.py --target organization    # File organization only
python run_optimize.py --target archives        # Archive consolidation only
python run_optimize.py --target cortex          # Brain/DB/cache optimization
python run_optimize.py --target cache           # Cache optimization only

# Aggressive database optimization
python run_optimize.py --aggressive
```

### From Python Code

```python
from src.operations.optimize_operation import OptimizeOperation

# Create optimizer
optimizer = OptimizeOperation()

# Validate prerequisites
result = optimizer.validate()
if not result.success:
    print(f"Validation failed: {result.message}")

# Execute optimization
result = optimizer.execute(
    target='all',        # 'organization', 'archives', 'cortex', 'cache', 'all'
    aggressive=False,    # Aggressive database optimization
    dry_run=False        # Preview mode
)

# Check results
if result.success:
    print(f"Success: {result.message}")
    print(f"Space saved: {result.data['space_saved_mb']:.2f} MB")
    print(f"Optimizations: {len(result.data['optimizations_applied'])}")
```

### Natural Language (via CORTEX Chat)

```
User: "optimize cortex"
User: "optimize"
User: "run optimization with dry run"
User: "clean up the repository"
```

---

## 📋 Optimization Phases

### Phase 1: File Organization (Target: `organization`)

**Task 1.1: Move Test Files**
- Moves `test_*.py` from root → `tests/`
- Ensures proper test organization
- Prevents root directory clutter

**Task 1.2: Move Scripts**
- Moves `fix_*.py`, `analyze_*.py`, `check_*.py`, `run_*.py`, `generate_*.py` from root → `scripts/`
- Consolidates utility scripts
- Improves discoverability

**Task 1.3: Build Artifact Cleanup**
- Removes `dist/` directory (15+ MB)
- Removes `publish/` directory (2+ MB)
- Removes `*.db` files from root
- Updates `.gitignore` to prevent future commits

**Task 1.4: Large File Cleanup**
- Removes large zip files (>10 MB) from `scripts/temp/`
- Frees up significant space (40+ MB potential)

**Task 1.5: Duplicate Template Removal**
- Keeps primary: `cortex-brain/response-templates.yaml`
- Removes duplicates in `cortex-brain/templates/`

**Task 1.6: Duplicate Logo Removal**
- Keeps primary: `docs/assets/images/CORTEX-logo.png`
- Removes duplicates in artifact backups (5+ MB)

### Phase 2: Archive Consolidation (Target: `archives`)

**Task 2.5: Archive Cleanup**
- Cleans `scripts/temp/` of old files (>30 days)
- Identifies old archives in `cortex-brain/archives/` (>60 days)
- Reports potential external archiving candidates

### Database Optimization (Target: `cortex`)

**Database Vacuum**
- Vacuums `cortex-brain/tier1/working_memory.db`
- Vacuums `cortex-brain/tier2/knowledge_graph.db`
- Typical savings: 10-30% of database size

**Brain Storage Cleanup**
- Removes old conversation captures (>30 days)
- Cleans temporary crawler files
- Removes old log files (>7 days)

### Cache Optimization (Target: `cache`)

**YAML Cache**
- Clears YAML cache for fresh rebuilds
- Estimated savings: ~10KB per entry

---

## 🔧 Configuration

### .gitignore Updates (Automatic)

The optimizer automatically ensures these patterns are in `.gitignore`:

```gitignore
# Build artifacts
dist/
publish/
*.egg-info/
build/

# Database files (local only)
*.db
*.db-shm
*.db-wal

# Temporary files
test_merge/
scripts/temp/*.zip
*.log

# Large files
*.zip
*.tar.gz
```

### Validation Prerequisites

Before running, the optimizer validates:
- ✅ `cortex-brain/` directory exists
- ✅ `cortex-brain/tier1/working_memory.db` exists
- ✅ `cortex-brain/tier2/knowledge_graph.db` exists

---

## 📊 Output & Reports

### Console Output

```
🧠 CORTEX Comprehensive Optimization
============================================================
Mode: EXECUTE
Target: all
Aggressive: False
============================================================

📋 Validating prerequisites...
   ✅ Optimization prerequisites validated

🔧 Running optimization...

✅ Optimization complete (12 actions, 68.45 MB saved)

📊 Results:
   • Optimizations applied: 12
   • Space saved: 68.45 MB
   • Files moved: 21
   • Files removed: 134
   • Directories cleaned: 2

   Applied optimizations:
      1. Moved 13 test files from root → tests/
      2. Moved 8 script files from root → scripts/
      3. Removed dist/ directory (15.24 MB, 976 files)
      4. Removed publish/ directory (2.10 MB, 93 files)
      5. Removed 3 database files from root
      6. Removed 1 large zip files from scripts/temp/ (46.22 MB)
      7. Removed duplicate response template files
      8. Removed 3 duplicate CORTEX logo files (5.31 MB)
      9. Removed 45 old files from scripts/temp/ (>30 days)
      10. Removed 12 old conversation captures (>30 days)
      11. Cleaned 8 temporary crawler files
      12. Vacuumed working_memory.db (saved 0.15 MB)

📄 Detailed report: cortex-brain/documents/reports/optimization-report-20251201_143022.json
```

### JSON Report Format

```json
{
  "timestamp": "2025-12-01T14:30:22.123456",
  "summary": {
    "total_optimizations": 12,
    "space_saved_mb": 68.45,
    "files_moved": 21,
    "files_removed": 134,
    "directories_cleaned": 2,
    "dry_run": false
  },
  "optimizations": [
    "Moved 13 test files from root → tests/",
    "Moved 8 script files from root → scripts/",
    "Removed dist/ directory (15.24 MB, 976 files)",
    ...
  ]
}
```

Reports saved to: `cortex-brain/documents/reports/optimization-report-<timestamp>.json`

---

## 🔄 Maintenance Schedule

### Recommended Frequency

| Target | Frequency | Reason |
|--------|-----------|--------|
| `organization` | After adding new files | Keep root clean |
| `archives` | Monthly | Manage historical data |
| `cortex` | Weekly | Database/cache health |
| `cache` | On-demand | After major config changes |
| `all` | Quarterly | Comprehensive cleanup |

### Automated Integration

To run optimize automatically:

**Git Pre-Commit Hook:**
```bash
#!/bin/bash
# .git/hooks/pre-commit
python run_optimize.py --dry-run --target organization
```

**Scheduled Task (Windows):**
```powershell
# Run weekly
schtasks /create /tn "CORTEX Optimize" /tr "python D:\PROJECTS\CORTEX\run_optimize.py" /sc weekly
```

---

## 🚨 Safety Features

### Dry Run Mode

Always preview changes first:
```bash
python run_optimize.py --dry-run
```

Output includes `[DRY RUN]` prefix for all actions.

### Validation Before Execution

- ✅ Checks critical directories exist
- ✅ Validates database files are present
- ✅ Verifies write permissions

### Rollback Support

```python
optimizer = OptimizeOperation()
result = optimizer.rollback()
# Returns: "Optimization rollback not applicable (changes are safe)"
```

**Note:** Optimization changes are safe and don't require rollback.

---

## 📈 Expected Outcomes

### Size Reduction Target

| Phase | Size Reduction |
|-------|---------------|
| File Organization | ~55 MB (46 MB zip + duplicates) |
| Build Artifacts | ~17 MB (dist/ + publish/) |
| Archive Consolidation | ~10 MB (old temps) |
| Database Vacuum | ~2-5 MB (10-30% of DB size) |
| **Total** | **~70-90 MB** |

### Repository Health Improvements

- ✅ Clean root directory (0 scattered test/script files)
- ✅ Proper file organization (tests in tests/, scripts in scripts/)
- ✅ No build artifacts committed (dist/, publish/ excluded)
- ✅ Single source of truth (no duplicate templates/logos)
- ✅ Optimized databases (vacuumed, compact)
- ✅ Fresh cache (rebuilt on next access)

---

## 🔍 Troubleshooting

### Issue: "Validation failed: cortex-brain/ directory not found"

**Solution:** Ensure you're in the CORTEX repository root:
```bash
cd D:\PROJECTS\CORTEX
python run_optimize.py
```

### Issue: "Permission denied" when removing files

**Solution:** Close applications using the files (VS Code, database browsers):
```bash
# Windows: Check processes using files
handle dist\
# Then close applications and retry
```

### Issue: Dry run shows unexpected file removals

**Solution:** Review the optimization plan and adjust `.gitignore`:
```bash
python run_optimize.py --dry-run
# Review output
# Adjust .gitignore if needed
# Re-run dry run
```

---

## 📚 Related Documentation

- **Planning Document:** `cortex-brain/documents/planning/CORTEX-OPTIMIZATION-PLAN-2025-12-01.md`
- **Response Format:** `.github/prompts/modules/response-format.md`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`
- **Operations System:** `src/operations/README.md`

---

## 🎓 Best Practices

1. **Always run dry-run first** - Preview changes before executing
2. **Review reports** - Check optimization reports in `cortex-brain/documents/reports/`
3. **Commit .gitignore changes** - Ensure updated .gitignore is committed
4. **Run regularly** - Weekly `cortex` optimization, monthly `all` optimization
5. **Monitor space savings** - Track repository size over time
6. **Archive externally** - Move old archives (>60 days) to external backup before deletion

---

**Last Updated:** December 1, 2025  
**Version:** 3.2.1  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
