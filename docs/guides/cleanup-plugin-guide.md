# CORTEX Cleanup Plugin - User Guide

**Version:** 2.0.0  
**Author:** Asif Hussain  
**Date:** 2025-11-08

---

## 🎯 Overview

The CORTEX Cleanup Plugin is a comprehensive, production-ready maintenance tool that safely removes unnecessary files, detects duplicates, and keeps your project organized.

### Key Features

✅ **Smart Temp File Removal** - Age-based cleanup with configurable thresholds  
✅ **Duplicate Detection** - Find and optionally remove duplicate files  
✅ **Cache Management** - Clean Python `__pycache__` and build artifacts  
✅ **Log Rotation** - Archive old logs automatically  
✅ **Empty Directory Cleanup** - Remove orphaned empty directories  
✅ **Large File Detection** - Identify files consuming excessive space  
✅ **Structure Enforcement** - Validate CORTEX project organization  
✅ **Git-Aware** - Respects `.gitignore` patterns  
✅ **Dry-Run Mode** - Preview changes before applying  
✅ **Rollback Support** - Detailed logs for recovery  

### Safety Features

🛡️ **Core File Protection** - Critical CORTEX files are NEVER touched  
🛡️ **Multi-Layer Safety** - Pattern matching + path verification + type checking  
🛡️ **Pre-Cleanup Verification** - Validates core files protected before any deletion  
🛡️ **Preserve Patterns** - Configurable whitelist of protected files/directories  
🛡️ **Dry-Run Default** - Must explicitly enable live mode  

---

## 🚀 Quick Start

### Basic Usage

```bash
# Dry run (safe - no files deleted)
python scripts/run_cleanup.py --dry-run

# View detailed output
python scripts/run_cleanup.py --dry-run --verbose

# Actual cleanup (requires confirmation)
python scripts/run_cleanup.py --force --no-dry-run
```

### First Run Checklist

1. ✅ Review configuration in `cortex.config.json`
2. ✅ Run with `--dry-run` first
3. ✅ Check the report in `logs/cleanup/`
4. ✅ Verify no core files are targeted
5. ✅ Run with `--force` if satisfied

---

## ⚙️ Configuration

### Location
`cortex.config.json` → `plugins.cleanup_plugin`

### Default Configuration

```json
{
  "plugins": {
    "cleanup_plugin": {
      "enabled": true,
      "dry_run": true,
      "auto_cleanup_on_startup": false,
      
      "temp_patterns": [
        "*.tmp", "*.temp", "*~", "*.swp", "*.swo",
        "*.bak", "*.old", "*.orig", "*.rej",
        ".DS_Store", "Thumbs.db", "desktop.ini"
      ],
      
      "backup_patterns": [
        "*.bak", "*.backup", "*.old",
        "*_backup_*", "*_old_*", "*.orig"
      ],
      
      "cache_dirs": [
        "__pycache__", ".pytest_cache", ".mypy_cache"
      ],
      
      "preserve_patterns": [
        "*.keep", ".gitkeep", "LICENSE", "README*",
        ".git/", "cortex-brain/", "src/", "tests/",
        "docs/", "prompts/", "workflows/", "scripts/"
      ],
      
      "max_temp_age_days": 7,
      "max_log_age_days": 30,
      "max_backup_age_days": 14,
      "min_duplicate_size_kb": 10,
      "large_file_threshold_mb": 100,
      
      "compress_old_archives": true,
      "enforce_structure": true,
      "detect_orphans": true
    }
  }
}
```

### Configuration Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `enabled` | bool | `true` | Enable/disable plugin |
| `dry_run` | bool | `true` | Preview mode (no deletions) |
| `auto_cleanup_on_startup` | bool | `false` | Run automatically on CORTEX startup |
| `temp_patterns` | array | See above | File patterns to clean |
| `preserve_patterns` | array | See above | Files/dirs to NEVER touch |
| `max_temp_age_days` | int | `7` | Delete temp files older than N days |
| `max_log_age_days` | int | `30` | Archive logs older than N days |
| `max_backup_age_days` | int | `14` | Delete backups older than N days |
| `min_duplicate_size_kb` | int | `10` | Minimum file size to check for duplicates |
| `large_file_threshold_mb` | int | `100` | Report files larger than N MB |
| `compress_old_archives` | bool | `true` | Compress old archive directories |
| `enforce_structure` | bool | `true` | Validate CORTEX project structure |
| `detect_orphans` | bool | `true` | Find orphaned files |

---

## 🔒 Safety Mechanisms

### Core Files Always Protected

The following are **NEVER** touched by the cleanup plugin:

```
✅ src/                    - All Python source code
✅ tests/                  - All test files
✅ cortex-brain/          - Brain database and knowledge
✅ docs/                  - Documentation
✅ prompts/               - Prompt files
✅ workflows/             - Workflow definitions
✅ scripts/               - All scripts
✅ .git/                  - Git repository
✅ .vscode/               - VS Code settings
✅ .github/               - GitHub workflows
✅ package.json           - Node dependencies
✅ tsconfig.json          - TypeScript config
✅ pytest.ini             - Test configuration
✅ requirements.txt       - Python dependencies
✅ cortex.config.json     - CORTEX configuration
✅ LICENSE                - License file
✅ README.md              - Project readme
✅ .gitignore             - Git ignore rules
```

### Additional Safety Rules

1. **Extension Protection** - All `.py`, `.md`, `.db` files in core directories
2. **Path Verification** - Multi-stage path checking before any deletion
3. **Pre-Cleanup Validation** - Verifies core files protected before starting
4. **Error Recovery** - If safety check fails, cleanup aborts immediately
5. **Detailed Logging** - Every action logged for audit trail

---

## 📊 What Gets Cleaned

### ✅ Safe to Clean

- **Temp Files** - `*.tmp`, `*.temp`, `*~`, `*.swp` older than 7 days
- **Backup Files** - `*.bak`, `*.old`, `*.orig` older than 14 days
- **Cache Directories** - `__pycache__`, `.pytest_cache`, `.mypy_cache`
- **Empty Directories** - Directories with no files
- **Old Logs** - Log files older than 30 days (archived first)
- **System Files** - `.DS_Store`, `Thumbs.db`, `desktop.ini`

### ⚠️ Reported Only (Not Deleted)

- **Duplicate Files** - Same content, different names
- **Large Files** - Files over 100MB (top 10 reported)
- **Orphaned Files** - Files in unexpected locations
- **Misplaced Files** - Files in root that should be in subdirectories

---

## 📈 Understanding Reports

### Report Location
`logs/cleanup/cleanup-YYYYMMDD-HHMMSS.json`

### Report Structure

```json
{
  "timestamp": "2025-11-08T15:30:49.284034",
  "dry_run": true,
  "stats": {
    "files_scanned": 5234,
    "files_deleted": 0,
    "files_archived": 12,
    "directories_removed": 21,
    "duplicates_found": 236,
    "space_freed_mb": 0.15,
    "warnings": [],
    "errors": []
  },
  "actions_taken": [
    {
      "action": "delete",
      "path": "src/__pycache__",
      "reason": "__pycache__ cache directory",
      "timestamp": "2025-11-08T15:30:21.095015"
    }
  ],
  "recommendations": [
    "Found 236 duplicate files. Review and remove to save space.",
    "Removed 21 empty directories. Consider reviewing project structure."
  ]
}
```

### Statistics Explained

- **files_scanned** - Total files examined
- **files_deleted** - Files removed (0 in dry-run)
- **files_archived** - Files moved to archive (logs)
- **directories_removed** - Empty directories removed
- **duplicates_found** - Files with identical content
- **space_freed_mb** - Megabytes freed (calculated even in dry-run)
- **warnings** - Non-critical issues
- **errors** - Failed operations

---

## 🎨 Usage Examples

### Example 1: Regular Maintenance

```bash
# Weekly cleanup routine
python scripts/run_cleanup.py --dry-run
# Review report in logs/cleanup/
python scripts/run_cleanup.py --force --no-dry-run
```

### Example 2: Quick Cache Cleanup

```bash
# Just remove Python cache files
# Edit cortex.config.json temporarily:
{
  "cleanup_plugin": {
    "temp_patterns": [],
    "backup_patterns": [],
    "cache_dirs": ["__pycache__"]
  }
}

python scripts/run_cleanup.py --force --no-dry-run
```

### Example 3: Find Duplicates Only

```bash
# Set all cleanup to false, just detect duplicates
# Check the report for duplicate file list
python scripts/run_cleanup.py --dry-run
# Review logs/cleanup/cleanup-*.json → "duplicates_found"
```

### Example 4: Aggressive Cleanup

```bash
# Reduce age thresholds for more aggressive cleanup
{
  "cleanup_plugin": {
    "max_temp_age_days": 3,
    "max_log_age_days": 14,
    "max_backup_age_days": 7
  }
}

python scripts/run_cleanup.py --dry-run
```

---

## 🔧 Troubleshooting

### Issue: "Safety check failed"

**Cause:** Core files would be affected by cleanup  
**Solution:** Review `violations` in error message, update `preserve_patterns`

### Issue: "Permission denied" errors

**Cause:** Files locked by other processes  
**Solution:** Close running applications, try again

### Issue: No files being cleaned

**Cause:** All files are recent or protected  
**Solution:** Normal behavior - review age thresholds in config

### Issue: Duplicates not detected

**Cause:** Files below `min_duplicate_size_kb` threshold  
**Solution:** Lower threshold in config (default: 10KB)

---

## 📝 Best Practices

### DO ✅

- **Always run dry-run first** - Preview changes before applying
- **Review reports regularly** - Check for unexpected patterns
- **Commit to git before cleanup** - Easy rollback if needed
- **Run weekly/monthly** - Prevent accumulation of clutter
- **Customize patterns** - Adapt to your workflow

### DON'T ❌

- **Don't disable safety checks** - Core files must stay protected
- **Don't run on unsaved work** - Commit first
- **Don't force without review** - Always check dry-run output
- **Don't modify core_protected_paths** - Critical safety mechanism
- **Don't run with `auto_cleanup_on_startup=true`** until fully tested

---

## 🧪 Testing

### Run Tests

```bash
# Run cleanup plugin tests
pytest tests/plugins/test_cleanup_plugin.py -v

# Run with coverage
pytest tests/plugins/test_cleanup_plugin.py --cov=src.plugins.cleanup_plugin
```

### Test Coverage

- ✅ Initialization and configuration
- ✅ Temp file cleanup with age filtering
- ✅ Backup file removal
- ✅ Cache directory cleanup
- ✅ Duplicate detection
- ✅ Empty directory removal
- ✅ Safety mechanisms
- ✅ Dry-run vs live mode
- ✅ Error handling
- ✅ Report generation

---

## 📞 Support

### Getting Help

1. Check this guide first
2. Review cleanup reports in `logs/cleanup/`
3. Run with `--verbose` for detailed logging
4. Check `logs/cleanup.log` for errors

### Reporting Issues

Include:
- Configuration used
- Command run
- Error message
- Relevant section of cleanup report
- Operating system

---

## 🔄 Version History

### Version 2.0.0 (2025-11-08)

**Initial Release**

- ✅ Comprehensive cleanup operations
- ✅ Multi-layer safety mechanisms
- ✅ Duplicate detection
- ✅ Dry-run mode
- ✅ Detailed reporting
- ✅ Git-aware cleanup
- ✅ Structure enforcement
- ✅ 41+ unit tests
- ✅ Full documentation

---

## 📄 License

Copyright © 2024-2025 Asif Hussain. All rights reserved.  
See LICENSE file for terms.

---

**Remember:** When in doubt, run `--dry-run` first! 🛡️
