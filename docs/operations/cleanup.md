# Workspace Cleanup Operation

**Operation ID:** `workspace_cleanup`  
**Natural Language:** "cleanup", "clean workspace", "remove temp files"  
**Version:** 1.0.0 (CORTEX 3.0 Phase 1.1)  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## Overview

The Workspace Cleanup operation safely removes temporary files, old logs, and cache to free disk space. It includes comprehensive safety checks to **never** delete source code, configuration files, or critical project data.

**What it does:**
- ✅ Removes temporary files (*.tmp, *.temp, *.pyc)
- ✅ Cleans __pycache__ directories
- ✅ Removes old log files (>30 days)
- ✅ Deletes large cache files (>10MB)
- ✅ Reports space freed in MB
- ✅ **Never** deletes source code or configuration

**Safety First:**
- 🔒 Protected extensions: .py, .js, .ts, .yaml, .json, .md
- 🔒 Protected directories: src/, docs/, tests/, .git/
- 🔒 Protected files: requirements.txt, package.json, etc.
- 🔒 Brain databases always preserved
- 🔒 Dry-run mode by default

**Time to complete:** 10-30 seconds

---

## Quick Start

### Natural Language (Safest)

Simply tell CORTEX to clean your workspace:

```
"cleanup workspace"
"remove temp files"
"free up disk space"
```

### Command Line (Dry Run)

See what would be deleted without actually deleting:

```powershell
# Dry run (default - shows what would be removed)
python src/operations/cleanup.py

# Same as above (explicit dry-run flag)
python src/operations/cleanup.py --dry-run
```

### Actually Remove Files

```powershell
# Remove files (will prompt for confirmation)
python src/operations/cleanup.py --no-dry-run

# Skip confirmation (use with caution!)
python src/operations/cleanup.py --no-dry-run --no-confirm
```

---

## Usage

### Dry Run Mode (Default)

**Always run dry-run first** to see what will be deleted:

```powershell
python src/operations/cleanup.py --dry-run
```

**Example output:**
```
🔍 Scanning workspace: D:\PROJECTS\CORTEX
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Searching for temporary files...
  Found 47 temporary items
Searching for old log files (>30 days)...
  Found 3 old log files
Searching for large cache files (>10MB)...
  Found 2 large cache files
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Cleanup Summary:
  Items to remove: 52
  Space to free: 245.67 MB

Items to be removed:
  [temp_files] module.pyc (0.02 MB)
  [temp_files] __pycache__ (1.23 MB)
  [old_logs] app-2024-09-15.log (5.44 MB)
  [cache_dirs] embeddings.cache (128.50 MB)
  ... and 48 more items

🔒 DRY RUN - No files deleted
   Run without --dry-run to actually remove files
```

---

### Actual Cleanup

Once you've reviewed the dry-run, remove files:

```powershell
# Will prompt "Delete 52 items (245.67 MB)? [y/N]:"
python src/operations/cleanup.py

# If you're confident (skips confirmation)
python src/operations/cleanup.py --no-confirm
```

---

### Category Selection

Clean only specific types of files:

```powershell
# Only temp files (*.tmp, __pycache__, *.pyc)
python src/operations/cleanup.py --category temp

# Only old logs (>30 days)
python src/operations/cleanup.py --category logs

# Only large cache files (>10MB)
python src/operations/cleanup.py --category cache

# Everything (default)
python src/operations/cleanup.py --category all
```

---

## Python API

Use programmatically:

```python
from pathlib import Path
from src.operations.cleanup import cleanup_workspace, CleanupCategory

# Dry run (safe - just preview)
result = cleanup_workspace(
    project_root=Path('d:/PROJECTS/CORTEX'),
    dry_run=True
)

print(f"Would remove {result['items_found']} items")
print(f"Would free {result['space_would_free_mb']:.2f} MB")

# Actual cleanup (prompts for confirmation)
result = cleanup_workspace(
    project_root=Path('d:/PROJECTS/CORTEX'),
    dry_run=False,
    confirm=True
)

if result['success']:
    print(f"Removed {result['items_removed']} items")
    print(f"Freed {result['space_freed_mb']:.2f} MB")

# Cleanup specific categories only
result = cleanup_workspace(
    project_root=Path('d:/PROJECTS/CORTEX'),
    dry_run=False,
    confirm=False,
    categories=[CleanupCategory.TEMP_FILES, CleanupCategory.OLD_LOGS]
)
```

---

## What Gets Removed

### Temporary Files (`temp`)
- `*.tmp` - Temporary files
- `*.temp` - Temporary files
- `*.pyc` - Compiled Python bytecode
- `*.pyo` - Optimized Python bytecode
- `*.pyd` - Python DLL files
- `__pycache__/` - Python cache directories
- `.pytest_cache/` - Pytest cache
- `.mypy_cache/` - Mypy cache
- `.ruff_cache/` - Ruff cache

### Old Logs (`logs`)
- `*.log` files in `logs/` older than 30 days

### Large Cache Files (`cache`)
- `*.cache` files larger than 10MB
- `*.pkl` pickle files larger than 10MB
- `*.pickle` pickle files larger than 10MB
- `*.dat` data files larger than 10MB

---

## What's NEVER Removed

### Protected File Extensions
- **Source code:** .py, .js, .ts, .jsx, .tsx, .java, .cpp, .c, .h, .cs, .rb, .go, .rs, .php, .swift, .kt, .scala
- **Config files:** .yaml, .yml, .json, .toml, .ini, .cfg, .conf
- **Documentation:** .md, .rst, .txt, .pdf, .doc, .docx

### Protected Directories
- `.git/` - Git repository
- `.github/` - GitHub workflows
- `src/` - Source code
- `docs/` - Documentation
- `tests/` - Test suites
- `prompts/` - AI prompts
- `cortex-brain/` - Brain databases
- `scripts/` - Automation scripts
- `workflows/` - Workflow definitions
- `examples/` - Example code

### Protected Files
- `requirements.txt` - Python dependencies
- `package.json` - Node dependencies
- `setup.py` - Python setup
- `pyproject.toml` - Python project config
- `Cargo.toml` - Rust dependencies
- `go.mod` - Go dependencies
- `pom.xml` - Maven dependencies
- `build.gradle` - Gradle config
- `.gitignore` - Git ignore rules
- `LICENSE` - License file
- `README.md` - Project readme
- `CHANGELOG.md` - Change history

### Brain Databases
All CORTEX brain databases are **always protected**:
- `cortex-brain/tier1/conversations.db`
- `cortex-brain/tier2/knowledge-graph.db`
- `cortex-brain/tier3/context-intelligence.db`

---

## Safety Features

### 1. Dry Run by Default
Running without flags defaults to dry-run mode - nothing is deleted.

### 2. Confirmation Prompt
Even when cleanup is enabled, you must confirm before deletion:
```
⚠️  Delete 52 items (245.67 MB)? [y/N]:
```

### 3. Per-File Safety Checks
Every file/directory is checked against safety rules before deletion.

### 4. Protected Path Detection
Files in protected directories (src/, docs/, tests/) are never removed.

### 5. Extension Validation
Source code extensions (.py, .js, .yaml) are never removed.

### 6. Detailed Reporting
See exactly what was removed and any errors encountered.

---

## Troubleshooting

### "Permission denied" errors

**Problem:** Can't delete some files  
**Solution:** 
- Windows: Run PowerShell as Administrator
- Mac/Linux: Check file permissions with `ls -la`
- Some files may be locked by running processes

### "Nothing to clean" message

**Problem:** Workspace already clean  
**Solution:** This is good! No action needed.

### Files in src/ not being removed

**Problem:** Temp files in src/ directory  
**Solution:** This is intentional - src/ is protected. Move temp files outside src/ if they need cleanup.

### Dry run shows files but actual run finds nothing

**Problem:** Files changed between dry-run and actual cleanup  
**Solution:** Another process may have cleaned files. Re-run dry-run to verify current state.

---

## Examples

### Example 1: First-time cleanup

```powershell
# Step 1: See what would be removed (safe)
PS> python src/operations/cleanup.py --dry-run

📊 Cleanup Summary:
  Items to remove: 127
  Space to free: 532.18 MB

# Step 2: Review the list, then actually clean
PS> python src/operations/cleanup.py

⚠️  Delete 127 items (532.18 MB)? [y/N]: y

✅ Cleanup Complete!
  Files removed: 115
  Directories removed: 12
  Space freed: 532.18 MB
```

---

### Example 2: Clean only temp files

```powershell
PS> python src/operations/cleanup.py --category temp --no-confirm

🔍 Scanning workspace: D:\PROJECTS\CORTEX
Searching for temporary files...
  Found 89 temporary items

🗑️  Removing items...
  ✓ Removed: module.pyc
  ✓ Removed: __pycache__
  ✓ Removed: test.tmp
  ... (86 more)

✅ Cleanup Complete!
  Files removed: 87
  Directories removed: 2
  Space freed: 45.23 MB
```

---

### Example 3: Clean old logs only

```powershell
PS> python src/operations/cleanup.py --category logs --dry-run

🔍 Scanning workspace: D:\PROJECTS\CORTEX
Searching for old log files (>30 days)...
  Found 5 old log files

📊 Cleanup Summary:
  Items to remove: 5
  Space to free: 23.45 MB

Items to be removed:
  [old_logs] app-2024-09-01.log (4.56 MB)
  [old_logs] app-2024-09-08.log (5.12 MB)
  [old_logs] app-2024-09-15.log (6.78 MB)
  [old_logs] app-2024-09-22.log (3.45 MB)
  [old_logs] app-2024-09-29.log (3.54 MB)

🔒 DRY RUN - No files deleted
```

---

## Performance

**Typical execution times:**

| Workspace Size | Scan Time | Delete Time | Total |
|----------------|-----------|-------------|-------|
| Small (<1000 files) | 1-2s | 1s | ~3s |
| Medium (1000-10000 files) | 3-5s | 2-3s | ~8s |
| Large (>10000 files) | 8-15s | 5-10s | ~25s |

**Disk I/O:**
- Scan: Read-only operations
- Delete: Minimal write (mainly removing directory entries)
- Space freed varies: typically 50-500MB

---

## Integration with CORTEX Operations

The cleanup operation integrates with CORTEX's universal operations system:

```python
from src.operations import execute_operation

# Execute via operations system
result = execute_operation('workspace_cleanup', dry_run=True)

# Or use natural language
result = execute_operation('cleanup workspace')
```

---

## Best Practices

1. **Always dry-run first** - See what will be deleted before committing
2. **Review the list** - Check that nothing important is being removed
3. **Start with categories** - Clean temp files first, then logs, then cache
4. **Regular cleanup** - Run monthly to keep workspace lean
5. **Check space freed** - Verify cleanup was worthwhile

---

## Command Reference

```powershell
# Dry run (default - safe preview)
python src/operations/cleanup.py
python src/operations/cleanup.py --dry-run

# Actual cleanup (with confirmation)
python src/operations/cleanup.py --no-dry-run

# Skip confirmation (use with caution!)
python src/operations/cleanup.py --no-dry-run --no-confirm

# Category-specific cleanup
python src/operations/cleanup.py --category temp
python src/operations/cleanup.py --category logs
python src/operations/cleanup.py --category cache

# Custom project root
python src/operations/cleanup.py --project-root /path/to/project
```

---

## Security Notes

- ✅ **No network access** - All operations are local
- ✅ **No credentials needed** - File system operations only
- ✅ **Protected paths** - Critical directories never touched
- ✅ **Audit trail** - Detailed logging of all removals
- ✅ **Reversible** - Only removes cache/temp (not critical data)

---

## Support

**Issues?**

1. Run dry-run mode first to diagnose
2. Check troubleshooting section above
3. Verify file permissions
4. Check logs for detailed errors

**Need help?**

- Natural language: "help with cleanup"
- Documentation: This file
- Source code: `src/operations/cleanup.py`

---

**Last Updated:** 2025-11-14  
**Phase:** 1.1 Week 3 (Simplified Operations)  
**Status:** ✅ Production Ready

---

*This operation is part of CORTEX 3.0 - The cognitive framework for GitHub Copilot.*
