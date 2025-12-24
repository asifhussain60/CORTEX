# Git Recovery Manifest Quick Reference

## 🧠 CORTEX Git Recovery System
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

## Overview

The Git Recovery Manifest system creates comprehensive tracking of all file deletions and reorganizations during cleanup operations, enabling easy recovery from git history.

## Key Features

- **Git Commit Tracking:** Captures last git commit hash for each deleted file
- **Content Verification:** SHA256 hash of file content
- **Recovery Commands:** Auto-generated git restore commands
- **Bulk Recovery:** Single command to recover all deleted files
- **File Moves:** Tracks reorganizations with reverse commands

## Manifest Locations

All manifests are stored in:
```
cortex-brain/cleanup-manifests/
├── deletion-manifest-backup_cleanup-YYYYMMDD-HHMMSS.json
├── deletion-manifest-md_consolidation-YYYYMMDD-HHMMSS.json
├── reorganization-manifest-YYYYMMDD-HHMMSS.json
└── ...
```

## Manifest Structure

### Deletion Manifest

```json
{
  "metadata": {
    "created": "2025-12-07T15:30:00",
    "operation_type": "backup_cleanup",
    "dry_run": false,
    "total_files": 15,
    "total_size_mb": 2.5
  },
  "files": [
    {
      "path": ".github/prompts/CORTEX.prompt.md.backup",
      "size_mb": 0.5,
      "content_hash": "abc123...",
      "git_commit": "a1b2c3d4...",
      "git_log_snippet": "a1b2c3d4 Updated prompts",
      "recovery_command": "git restore --source=a1b2c3d4 \".github/prompts/CORTEX.prompt.md.backup\""
    }
  ],
  "recovery": {
    "instructions": ["..."],
    "bulk_recovery_command": "git restore --source=a1b2c3d4 ... && ..."
  }
}
```

### Reorganization Manifest

```json
{
  "metadata": {
    "created": "2025-12-07T15:30:00",
    "operation_type": "reorganization",
    "total_moves": 5
  },
  "moves": [
    {
      "old_path": "test_output.txt",
      "new_path": "scripts/temp/test_output.txt",
      "git_commit": "a1b2c3d4...",
      "reverse_command": "git mv \"scripts/temp/test_output.txt\" \"test_output.txt\""
    }
  ],
  "recovery": {
    "bulk_reverse_command": "git mv ... && git mv ..."
  }
}
```

## Recovery Operations

### 1. Review Manifest

```bash
# List all manifests
ls cortex-brain/cleanup-manifests/

# View specific manifest
cat cortex-brain/cleanup-manifests/deletion-manifest-backup_cleanup-20251207-153000.json
```

### 2. Recover Single File

```bash
# Copy recovery_command from manifest
git restore --source=a1b2c3d4 ".github/prompts/CORTEX.prompt.md.backup"
```

### 3. Recover All Files (Bulk)

```bash
# Copy bulk_recovery_command from manifest
git restore --source=a1b2c3d4 "file1.txt" && \
git restore --source=a1b2c3d5 "file2.txt" && \
...
```

### 4. Reverse File Moves

```bash
# Copy reverse_command from reorganization manifest
git mv "scripts/temp/test_output.txt" "test_output.txt"

# Or bulk reverse
git mv "scripts/temp/file1.txt" "file1.txt" && \
git mv "scripts/temp/file2.txt" "file2.txt"
```

### 5. Programmatic Recovery

```python
from pathlib import Path
from src.operations.modules.cleanup.git_recovery_manifest import GitRecoveryManifest

recovery = GitRecoveryManifest(Path.cwd())

# Load manifest
manifest_path = Path("cortex-brain/cleanup-manifests/deletion-manifest-backup_cleanup-20251207-153000.json")

# Recover all files
stats = recovery.recover_from_manifest(manifest_path, dry_run=False)

# Or recover specific files
stats = recovery.recover_from_manifest(
    manifest_path,
    file_paths=[".github/prompts/CORTEX.prompt.md.backup"],
    dry_run=False
)

print(f"Recovered: {stats['succeeded']}, Failed: {stats['failed']}")
```

## Integration with Cleanup Operations

### Automatic Manifest Creation

Manifests are automatically created during:

1. **Backup File Cleanup** (`_manage_backups`)
   - Before deleting `.backup`, `.bak`, `.old` files
   - Manifest type: `deletion-manifest-backup_cleanup`

2. **MD File Consolidation** (`_consolidate_md_files`)
   - Before archiving duplicate markdown files
   - Manifest type: `deletion-manifest-md_consolidation`

3. **Root Folder Cleanup** (`_cleanup_root_folder`)
   - Before moving misplaced files from root
   - Manifest type: `reorganization-manifest`

4. **File Reorganization** (enhanced cleanup)
   - When moving files to correct locations
   - Manifest type: `reorganization-manifest`

### Manifest Creation Flow

```
1. Cleanup operation identifies files to delete/move
2. Git Recovery Manifest captures:
   - File metadata (size, mtime, path)
   - Git commit hash (last modification)
   - Content hash (SHA256)
   - Recovery commands
3. Manifest saved to cortex-brain/cleanup-manifests/
4. Cleanup operation proceeds with deletion/move
5. User can recover at any time using manifest
```

## Safety Features

- **Git History Required:** Files must be committed to git for recovery
- **Content Verification:** SHA256 hash confirms file integrity
- **Atomic Operations:** Manifests created before any deletions
- **Detailed Logging:** Each operation logged with timestamps
- **Dry-Run Support:** Preview manifests without actual changes

## Limitations

- **Uncommitted Files:** Cannot recover files never committed to git
- **Untracked Files:** Files in `.gitignore` may not have git history
- **Multiple Commits:** Only captures last commit, not full history
- **Large Files:** Recovery may be slow for large files

## Troubleshooting

### File Not in Git History

```
Error: pathspec 'file.txt' did not match any file(s) known to git
```

**Solution:** File was never committed. Check:
1. System trash/recycle bin
2. Editor auto-save/backup features
3. Time Machine (macOS) or File History (Windows)

### Wrong Git Commit

```
Error: File recovered but content is wrong
```

**Solution:** Manifest captured last commit, file may have older versions:
```bash
# Find all commits that modified the file
git log --all -- path/to/file.txt

# Restore from specific commit
git restore --source=<commit-hash> path/to/file.txt
```

### Bulk Recovery Fails

```
Error: Some files failed to recover
```

**Solution:** Recover files individually:
```python
from src.operations.modules.cleanup.git_recovery_manifest import GitRecoveryManifest

recovery = GitRecoveryManifest(Path.cwd())
manifest = recovery.load_manifest(Path("cortex-brain/cleanup-manifests/...json"))

for file_info in manifest['files']:
    if 'recovery_command' in file_info:
        print(f"Recovering: {file_info['path']}")
        # Run command manually or via subprocess
```

## Best Practices

1. **Review Manifests:** Always check manifest before cleanup
2. **Keep Manifests:** Don't delete manifests (stored in git)
3. **Test Recovery:** Verify recovery commands in dry-run
4. **Commit Often:** Regular commits enable better recovery
5. **Backup Critical Files:** Important files should be in git

## Related Files

- **Implementation:** `src/operations/modules/cleanup/git_recovery_manifest.py`
- **Integration:** `src/operations/modules/cleanup/cleanup_orchestrator.py`
- **Manifests:** `cortex-brain/cleanup-manifests/`
- **Guide:** `cortex-brain/documents/implementation-guides/enhanced-cleanup-summary.md`
