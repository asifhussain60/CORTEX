# Cleanup Orchestrator

**Purpose:** Comprehensive workspace cleanup - remove backups, reorganize files, consolidate duplicates, detect bloat

**Version:** 3.2.0  
**Status:** ✅ PRODUCTION

---

## Commands

- `cleanup` - Run full cleanup operation
- `cleanup --dry-run` - Preview changes without executing
- `cleanup backups` - Remove only backup files
- `cleanup duplicates` - Consolidate duplicate MD files

---

## What It Does

1. **Backup Management:** Archives then deletes old backup folders (GitHub tracked)
2. **File Reorganization:** Moves misplaced files to correct locations
3. **Duplicate Consolidation:** Merges redundant MD files
4. **Bloat Detection:** Scans entry points and orchestrators for size issues
5. **Root Cleanup:** Organizes root folder files
6. **Auto-Optimization:** Triggers OptimizeCortexOrchestrator after cleanup

---

## Safety Features

### Protected Paths
**NEVER touches these:**
- `src/`, `tests/`, `cortex-brain/`, `docs/`
- `.git/`, `.github/`, `.vscode/`
- `package.json`, `pytest.ini`, `requirements.txt`
- `LICENSE`, `README.md`, `CHANGELOG.md`
- All configuration files

### Git Tracking
- Every deletion tracked in Git before removal
- Creates GitHub archive commits
- Maintains full audit trail
- Enables rollback if needed

### Dry Run Mode
- Preview all changes before execution
- Shows what will be deleted/moved
- No actual modifications made
- Safe exploration of cleanup impact

---

## Cleanup Workflow

```
1. Discovery Phase
   ↓
2. Analysis & Planning
   - Identify backups (age > 7 days)
   - Find duplicates (hash comparison)
   - Detect misplaced files
   - Scan for bloat
   ↓
3. Git Archival
   - Commit backups to Git
   - Push to GitHub
   - Verify archive success
   ↓
4. Execution
   - Delete archived backups
   - Reorganize files
   - Consolidate duplicates
   - Clean root folder
   ↓
5. Verification
   - Run bloat tests
   - Validate organization
   - Check Git status
   ↓
6. Optimization Trigger
   - Launch OptimizeCortexOrchestrator
   - Vacuum databases
   - Rebuild caches
```

---

## Metrics Tracked

**Cleanup Metrics:**
- Backups deleted: count + bytes freed
- Files reorganized: source → destination
- MD files consolidated: count + duplicates removed
- Root files cleaned: count
- Bloated files found: count + sizes
- Space freed: MB/GB
- Git commits created: count
- Duration: seconds

**Output Location:** `cortex-brain/cleanup-reports/CLEANUP-[timestamp].json`

---

## File Reorganization Rules

### Root Folder → Correct Location
- Test files → `tests/`
- Source files → `src/`
- Documentation → `docs/`
- Scripts → `scripts/`
- Configuration → appropriate config folder

### Duplicate Detection
- Uses SHA-256 hash comparison
- Keeps newest version
- Moves duplicates to archive
- Updates all references

---

## Backup Management

**Archival Process:**
1. Scan for backup folders (`.bak`, `.backup`, `backup-*`, etc.)
2. Filter by age (default: >7 days)
3. Create Git commit with backup contents
4. Push to GitHub remote
5. Verify archive exists on GitHub
6. Delete local backup folder
7. Log deletion in cleanup report

**Exclusions:**
- Recent backups (<7 days)
- Active restore points
- Checkpoint files from workflows

---

## Bloat Detection

**Entry Point Checks:**
- Line count (limit: 500)
- Token count (limit: 5000)
- Excessive inline documentation
- Missing modular architecture

**Orchestrator Checks:**
- File size (warning: >10KB)
- Method count (warning: >20)
- Code complexity metrics
- Import bloat

---

## Configuration

**Configurable via cortex.config.json:**
```json
{
  "cleanup": {
    "backup_age_days": 7,
    "enable_git_tracking": true,
    "enable_auto_optimization": true,
    "dry_run_default": false,
    "protected_extensions": [".py", ".md", ".json", ".yaml"],
    "exclude_patterns": ["node_modules", "__pycache__", ".pytest_cache"]
  }
}
```

---

## Integration Points

- **OptimizeCortexOrchestrator:** Auto-triggered after cleanup
- **Git:** All deletions archived via commits
- **GitHub:** Backup verification on remote
- **Bloat Tests:** Validates cleanup effectiveness
- **File Organization:** Uses project structure conventions

---

## Natural Language Examples

- "cleanup the workspace"
- "run cleanup in dry-run mode"
- "remove old backups"
- "consolidate duplicate files"
- "organize root folder"

---

## Output

**Console:**
```
🧹 CORTEX Workspace Cleanup

✅ Backup Management:
   Archived: 5 folders (342 MB)
   Deleted: 5 folders after GitHub backup

✅ File Reorganization:
   Moved: 23 files to correct locations

✅ Duplicate Consolidation:
   Consolidated: 12 MD files
   Removed duplicates: 18 files

✅ Root Cleanup:
   Organized: 15 root files

✅ Bloat Detection:
   No bloated files found

✅ Space Freed: 425 MB

⚡ Triggering optimization...
```

**Files Created:**
- `cortex-brain/cleanup-reports/CLEANUP-[timestamp].json`
- `cortex-brain/cleanup-logs/actions-[timestamp].log`
- Git commits with backup archives

---

## Error Handling

**Git Archival Failures:**
- Aborts deletion if GitHub backup fails
- Retries archive push (max 3 attempts)
- Logs failure and preserves backup
- User notified of manual intervention needed

**File Operation Failures:**
- Logs error with file path and reason
- Continues with remaining operations
- Reports all failures in cleanup report
- Suggests manual fixes

---

## Testing

**Test File:** `tests/operations/modules/cleanup/test_cleanup_orchestrator.py`

**Coverage:** >70% required for deployment

**Key Tests:**
- Backup archival and deletion
- File reorganization accuracy
- Duplicate detection algorithm
- Protected path enforcement
- Git tracking verification
- Bloat detection accuracy

---

## See Also

- Optimize Cortex: `.github/prompts/modules/optimize-cortex-guide.md`
- Entry Point Bloat Tests: `tests/tier0/test_entry_point_bloat.py`
- File Organization: `cortex-brain/documents/file-relationships.yaml`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Repository:** <https://github.com/asifhussain60/CORTEX>
