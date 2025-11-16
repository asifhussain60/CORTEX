# Cleanup Plugin - GitHub Archival Feature

**Feature Added:** 2025-11-08  
**Version:** 2.1.0  
**Status:** ✅ Production Ready

---

## 🎯 Overview

The Cleanup Plugin now automatically archives backup files to GitHub before deleting them locally. This ensures backups are safely preserved in version control while freeing local disk space.

---

## ✨ What's New

### GitHub Backup Archival

When cleaning up old backup files (`.bak`, `.old`, `.orig`, etc.), the plugin now:

1. ✅ **Copies** backup files to `.backup-archive/` directory
2. ✅ **Creates manifest** with metadata (paths, sizes, timestamps)
3. ✅ **Commits to Git** with descriptive message
4. ✅ **Pushes to GitHub** remote repository
5. ✅ **Deletes local copies** after successful push
6. ✅ **Keeps manifest files** for audit trail
7. ✅ **Cleans archive directory** (keeps only manifests)

---

## 🔧 How It Works

### Workflow

```
Old Backup File (15+ days old)
    ↓
Copy to .backup-archive/
    ↓
Create JSON manifest
    ↓
Git add .backup-archive/
    ↓
Git commit -m "Archive N backup files..."
    ↓
Git push
    ↓
Delete local backup file
    ↓
Clean archived copies (keep manifest)
```

### Manifest Structure

Each archival operation creates a manifest file:

**Location:** `.backup-archive/backup-manifest-YYYYMMDD-HHMMSS.json`

**Content:**
```json
{
  "timestamp": "2025-11-08T16:45:23.123456",
  "backup_count": 15,
  "total_size_bytes": 1234567,
  "files": [
    {
      "original_path": "src/module.py.bak",
      "archived_path": ".backup-archive/src/module.py.bak",
      "size_bytes": 12345,
      "modified_time": "2025-10-15T10:30:00"
    }
  ]
}
```

### Git Commit Message

```
Archive 15 backup files before cleanup - 20251108-164523
```

---

## 📋 Usage

### Automatic Operation

The GitHub archival happens automatically when running cleanup:

```bash
# Dry run - simulates archival
python scripts/run_cleanup.py --dry-run

# Live mode - actually archives and deletes
python scripts/run_cleanup.py --force --no-dry-run
```

### Configuration

No additional configuration needed! Uses existing backup cleanup settings:

```json
{
  "plugins": {
    "cleanup_plugin": {
      "max_backup_age_days": 14,
      "backup_patterns": [
        "*.bak",
        "*.backup",
        "*.old",
        "*_backup_*",
        "*_old_*",
        "*.orig"
      ]
    }
  }
}
```

---

## 🔄 Recovery

### Restore Archived Backup

To recover a backup file that was archived:

```bash
# 1. Find the archive commit
git log --grep="Archive.*backup files"

# 2. View the manifest
git show <commit-sha>:.backup-archive/backup-manifest-YYYYMMDD-HHMMSS.json

# 3. Restore specific file
git show <commit-sha>:.backup-archive/path/to/file.bak > restored_file.bak

# 4. Or restore entire archive directory
git checkout <commit-sha> -- .backup-archive/
```

### List All Archived Backups

```bash
# View all archive commits
git log --grep="Archive.*backup files" --oneline

# View manifest files in current commit
ls -la .backup-archive/*.json
```

---

## 🛡️ Safety Features

### Fail-Safe Behavior

- ❌ **Git add fails** → Abort deletion, keep local backups
- ❌ **Git commit fails** → Abort deletion, keep local backups  
- ❌ **Git push fails** → Warn but keep commit, backups in local git history
- ✅ **Manifest always created** → Audit trail maintained
- ✅ **Dry-run mode** → Preview what would be archived

### Protected Files

Manifests are protected from cleanup:

```json
{
  "preserve_patterns": [
    ".backup-archive/*.json"
  ]
}
```

---

## 📊 Benefits

### Before GitHub Archival

❌ **Problem:** Backup files accumulate over time  
❌ **Problem:** Manual deletion risks losing important backups  
❌ **Problem:** No centralized backup reference  
❌ **Problem:** Team members can't access old backups  

### After GitHub Archival

✅ **Benefit:** Automatic archival before deletion  
✅ **Benefit:** Zero risk - backups in GitHub history  
✅ **Benefit:** Manifest provides clear audit trail  
✅ **Benefit:** Team-wide access via GitHub  
✅ **Benefit:** Significant disk space savings  

---

## 📈 Example Output

```
🧹 Running cleanup operations...

Cleaning backup files with GitHub archival...
  ✓ Found 15 backup files older than 14 days
  ✓ Copied to .backup-archive/
  ✓ Created manifest: backup-manifest-20251108-164523.json
  ✓ Git commit: a1b2c3d4
  ✓ Pushed to GitHub
  ✓ Deleted 15 local backup files
  ✓ Freed 1.2 MB disk space

Cleaning backup archive directory...
  ✓ Deleted 15 archived files
  ✓ Kept 1 manifest file for reference
  ✓ Freed additional 1.2 MB disk space

Total space freed: 2.4 MB
```

---

## 🧪 Testing

### Test Suite

New tests added in `tests/plugins/test_cleanup_plugin.py`:

- ✅ `test_archive_backups_to_github` - Archival workflow
- ✅ `test_manifest_creation` - Manifest file generation
- ✅ `test_backup_archive_cleanup` - Archive directory cleanup

### Run Tests

```bash
# Run all cleanup plugin tests
pytest tests/plugins/test_cleanup_plugin.py -v

# Run only GitHub archival tests
pytest tests/plugins/test_cleanup_plugin.py::TestGitHubArchival -v
```

---

## ⚙️ Technical Details

### Code Changes

**File:** `src/plugins/cleanup_plugin.py`

**New Methods:**
- `_archive_backups_to_github()` - Archives backups to Git
- `_cleanup_backup_archive()` - Cleans archive directory after push

**Modified Methods:**
- `_cleanup_backup_files()` - Now archives before deletion
- `_run_full_cleanup()` - Calls archive cleanup at end

**Dependencies:**
- `subprocess` - Git command execution

### File Structure

```
.backup-archive/
├── backup-manifest-20251108-164523.json  ← Kept
├── backup-manifest-20251107-120000.json  ← Kept
└── (archived files deleted after push)
```

---

## 🚨 Troubleshooting

### Git Push Fails

**Problem:** Git push fails due to authentication or network

**Solution:**
- Commit is saved locally - backups are safe
- Warning logged but cleanup continues
- Manually push later: `git push`

### No Git Repository

**Problem:** Not a git repository

**Solution:**
- Git operations skipped
- Backups NOT deleted (safety measure)
- Warning logged

### Permission Errors

**Problem:** Can't write to `.backup-archive/`

**Solution:**
- Check directory permissions
- Run with appropriate user
- Error logged, cleanup continues for other files

---

## 📝 Configuration Reference

### Related Settings

```json
{
  "plugins": {
    "cleanup_plugin": {
      "enabled": true,
      "dry_run": true,
      "max_backup_age_days": 14,
      "backup_patterns": [
        "*.bak",
        "*.backup", 
        "*.old",
        "*_backup_*",
        "*_old_*",
        "*.orig"
      ],
      "preserve_patterns": [
        ".backup-archive/*.json"
      ]
    }
  }
}
```

---

## 🎓 Best Practices

### Recommended Workflow

1. ✅ **Run dry-run first** - Preview what would be archived
2. ✅ **Check disk space** - Ensure enough space for archive copy
3. ✅ **Verify Git status** - Ensure no uncommitted changes
4. ✅ **Run live cleanup** - Archives and deletes
5. ✅ **Verify push** - Check GitHub for new commit
6. ✅ **Review manifest** - Confirm all backups archived

### Frequency

- **Development:** Weekly cleanup
- **Production:** Monthly cleanup
- **Large projects:** After major milestones

---

## 📚 See Also

- [Cleanup Plugin User Guide](cleanup-plugin-guide.md)
- [CORTEX Configuration Reference](../architecture/cortex-configuration-reference.md)
- [Git Workflow Guide](../development/git-workflow.md)

---

**Last Updated:** 2025-11-08  
**Author:** Asif Hussain  
**Version:** 2.1.0
