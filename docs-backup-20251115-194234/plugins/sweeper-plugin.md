# File Sweeper Plugin

**Aggressive workspace cleanup with OS-native reversibility**

## Overview

The File Sweeper plugin scans the CORTEX workspace for unnecessary files and moves them to the OS Recycle Bin. **Fully reversible** - restore any file from your Recycle Bin/Trash anytime.

**Safety through INTELLIGENCE + OS-native reversibility:**
- Smart classification rules (age, size, location, naming patterns)
- Whitelist protection (respects `cleanup-rules.yaml`)
- Recycle Bin instead of permanent deletion (uses `send2trash`)
- Minimal audit trail (JSON log for tracking only)

## Target Files

The sweeper identifies and moves to Recycle Bin:

- **Backup files**: `*.bak`, `*.backup`, `*-BACKUP-*`, `*-OLD-*`
- **Temporary files**: `*.tmp`, `*.temp`
- **Python cache**: `*.pyc`, `*.pyo`, `__pycache__`
- **Dated duplicates**: `file.2024-11-10.md`, `notes.20241110.txt`
- **Old logs**: `*.log` (older than 30 days)
- **Old session reports**: `SESSION-*.md` (older than 30 days)
- **Old reference docs**: `*-REFERENCE.md`, `*-IMPLEMENTATION.md`, `*-QUICK-REFERENCE.md` (older than 60 days)
- **Old guides**: `*-GUIDE.md`, `*-INSTRUCTIONS.md`, `*-MANUAL.md` (older than 60 days)
- **Old summaries**: `*-SUMMARY.md` (older than 60 days)

## Protected Files

The sweeper NEVER deletes:

- **Source code**: `src/`, `tests/`
- **Config files**: `*.py`, `*.yaml`, `*.json`
- **Brain data**: `cortex-brain/tier1`, `tier2`, `tier3`, `schemas`
- **Core docs**: `README.md`, `LICENSE`, `requirements.txt`, etc.
- **Git repository**: `.git/`, `.github/`
- **Virtual environment**: `.venv/`

Full protection list defined in `cortex-brain/cleanup-rules.yaml`.

## Usage

### Natural Language (Recommended)

```
sweep workspace
run sweeper
clean up files
sweep files
```

### Python Script

```bash
# Interactive demo
python scripts/demo_sweeper.py

# Programmatic usage
from src.plugins.sweeper_plugin import SweeperPlugin

sweeper = SweeperPlugin()
sweeper.initialize()
results = sweeper.execute({"workspace_root": "/path/to/cortex"})
```

### Direct Plugin Call

```python
from src.plugins.sweeper_plugin import register

plugin = register()
plugin.initialize()
results = plugin.execute({"workspace_root": "."})

print(f"Deleted {results['stats']['files_deleted']} files")
print(f"Freed {results['stats']['space_freed_mb']:.2f} MB")
```

## Configuration

Edit `cortex-brain/cleanup-rules.yaml` to customize:

```yaml
categories:
  sweeper:
    enabled: true
    
    target_extensions:
      - "*.md"
      - "*.log"
      - "*.bak"
      # Add more...
    
    age_policies:
      session_reports_days: 30
      log_files_days: 30
      reference_docs_days: 60
    
    safety:
      require_confirmation: false
      create_manifest: false
      create_backup: false
      create_audit_log: true
```

## Output

After execution, you'll see:

```
================================================================================
CORTEX FILE SWEEPER
================================================================================
Workspace: D:\PROJECTS\CORTEX
Mode: RECYCLE BIN (OS-native reversibility)
================================================================================
Scanning workspace...
Scanned 1,247 files
Classified 87 files for review
Moving 42 files to Recycle Bin...
================================================================================
SWEEPER SUMMARY
================================================================================
Files scanned:     1,247
Files moved:       42 (to Recycle Bin)
Files kept:        45
Space freed:       12.34 MB
Execution time:    0.85s

Recovery:          Files can be restored from Recycle Bin
================================================================================
Audit log saved: cortex-brain/sweeper-logs/sweeper-20251112-182530.json
```

## Audit Trail

A minimal audit log is saved in `cortex-brain/sweeper-logs/`:

```json
{
  "timestamp": "2025-11-12T18:25:30",
  "mode": "recycle_bin",
  "recoverable": true,
  "recovery_instructions": "Files can be restored from your OS Recycle Bin/Trash",
  "stats": {
    "files_deleted": 42,
    "space_freed_mb": 12.34
  },
  "deleted_files": [
    {
      "path": "docs/backup.bak",
      "category": "backup",
      "reason": "Manual backup file",
      "size_bytes": 1024,
      "age_days": 15,
      "moved_to_recycle_bin_at": "2025-11-12T18:25:30",
      "recoverable": true
    }
  ]
}
```

## Safety Features

### 1. Recycle Bin Reversibility (NEW!)
Files are moved to OS-native Recycle Bin/Trash, not permanently deleted.
- **Windows**: Recycle Bin
- **macOS**: Trash
- **Linux**: Trash (freedesktop.org standard)

**Recovery:** Right-click → Restore in your OS file manager.

### 2. Whitelist Protection
Files matching protected patterns are NEVER scanned or classified.

### 3. Intelligent Classification
Each file is classified based on:
- File extension
- Naming patterns (backups, references, etc.)
- Age (modification time)
- Location in workspace
- Size

### 4. Conservative Defaults
- Unknown files are kept
- Recent files are kept
- Files in protected directories are skipped

### 5. Audit Recovery
If you need to verify what was moved:
1. Check audit log: `cortex-brain/sweeper-logs/sweeper-YYYYMMDD-HHMMSS.json`
2. Find file path and timestamp
3. Restore from Recycle Bin (OS native)
4. Or restore from Git history if file was tracked

## Testing

Run comprehensive tests:

```bash
pytest tests/plugins/test_sweeper_plugin.py -v
```

**Test Coverage:**
- ✅ File classification (backups, temps, duplicates, logs, references)
- ✅ Protected directories and patterns
- ✅ Recycle Bin execution (mocked)
- ✅ Audit log creation with recovery info
- ✅ Error handling
- ✅ Full integration workflow

**All 17 tests passing** ✅

## Integration

The sweeper integrates with:

- **Cleanup Orchestrator**: Can be called from cleanup workflows
- **Plugin System**: Auto-registers with CORTEX plugin registry
- **Natural Language**: Responds to "sweep", "clean files", etc.

## Author

**Asif Hussain**  
Copyright © 2024-2025 Asif Hussain. All rights reserved.

## License

Proprietary - See LICENSE file for terms
