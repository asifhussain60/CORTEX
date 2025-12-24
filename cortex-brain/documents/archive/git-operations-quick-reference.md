# Git Operations Quick Reference

**Version:** 3.2.1  
**Created:** December 3, 2025  
**Author:** Asif Hussain

---

## 🎯 Overview

CORTEX now includes two powerful git orchestrators for managing repository operations safely and efficiently.

---

## 📦 Git Sync & Optimize Orchestrator

**File:** `src/orchestrators/git_sync_and_optimize.py`

### Purpose
Comprehensive workflow for safely syncing with remote while preserving local work, then optimizing CORTEX to maintain peak performance.

### Features
- ✅ Smart stash with timestamp backup
- ✅ Pull latest changes from remote with rebase
- ✅ Intelligent merge with auto-conflict resolution
- ✅ System alignment validation
- ✅ Performance optimization
- ✅ Cleanup obsolete artifacts
- ✅ Push merged changes to remote
- ✅ Final sync verification
- ✅ Rollback safety on failures

### Usage

```bash
# Standard execution (auto-resolve conflicts)
python3 src/orchestrators/git_sync_and_optimize.py

# Manual conflict resolution
python3 src/orchestrators/git_sync_and_optimize.py --no-auto-resolve

# Custom repository path
python3 src/orchestrators/git_sync_and_optimize.py --repo /path/to/repo
```

### Natural Language Commands
```
"sync with remote"
"pull and merge my work"
"optimize cortex and sync"
"git sync and optimize"
```

### Workflow Steps

1. **Pre-Sync Status** - Check current branch and changes
2. **Stash Work** - Safely backup local changes with timestamp
3. **Pull Remote** - Fetch latest changes with rebase
4. **Merge Stash** - Intelligently apply stashed work
5. **System Alignment** - Validate integration (non-blocking)
6. **Optimization** - Improve performance (non-blocking)
7. **Cleanup** - Remove obsolete artifacts (non-blocking)
8. **Push Changes** - Sync merged work to remote
9. **Final Sync** - Verify consistency with origin
10. **Status Check** - Confirm clean state

### Auto-Conflict Resolution Strategies

**Documentation Files** (.md, .txt, .yaml, .json)
- Strategy: Accept both changes (keep working tree)
- Rationale: Documentation typically merges well

**Generated Files** (cortex-brain/*, *generated*)
- Strategy: Accept remote version (--theirs)
- Rationale: Generated content should match remote

**Source Code** (.py, .js, .ts)
- Strategy: Keep local version (--ours)
- Rationale: Preserve active development work

### Safety Features

**Automatic Stash Backup**
- Timestamped stash names
- Preserved even on failure
- Easy recovery with `git stash list`

**Rollback on Failure**
- Automatically reapplies stash if merge fails
- Work never lost
- Clear instructions for manual recovery

**Non-Blocking Operations**
- Alignment, optimization, cleanup are non-critical
- Warnings don't stop workflow
- Continue even if these steps have issues

### Output Files

**Results Report:** `cortex-brain/documents/reports/git-sync-YYYYMMDD_HHMMSS.json`

Contains complete execution log:
```json
{
  "success": true,
  "timestamp": "20251203_074545",
  "results": {
    "pre_status": {...},
    "stash": {...},
    "pull": {...},
    "merge": {...},
    "align": {...},
    "optimize": {...},
    "cleanup": {...},
    "push": {...},
    "sync": {...},
    "post_status": {...}
  }
}
```

---

## 💾 Commit & Push Orchestrator

**File:** `src/operations/commit_and_push.py`

### Purpose
Simplified workflow for staging all changes, creating commits, and pushing to remote.

### Features
- ✅ Automatic file staging (git add -A)
- ✅ Smart commit message generation
- ✅ Push to remote with branch detection
- ✅ Final sync with origin
- ✅ Clean status reporting

### Usage

```bash
# Auto-generated commit message
python3 src/operations/commit_and_push.py

# Custom commit message
python3 src/operations/commit_and_push.py -m "Your commit message"

# Custom repository
python3 src/operations/commit_and_push.py --repo /path/to/repo
```

### Natural Language Commands
```
"commit and push"
"save and push my changes"
"commit these changes"
"push to remote"
```

### Workflow Steps

1. **Status Check** - Identify files to commit
2. **Stage Changes** - Add all modified/new files
3. **Create Commit** - Generate commit with message
4. **Push Remote** - Upload to origin
5. **Sync** - Verify consistency
6. **Final Status** - Confirm clean state

### Auto-Generated Commit Messages

Format: `CORTEX: Auto-commit {summary} [{timestamp}]`

Examples:
```
CORTEX: Auto-commit 5 new file(s), 3 modified file(s) [2025-12-03 07:46:10]
CORTEX: Auto-commit 2 modified file(s) [2025-12-03 08:15:22]
CORTEX: Auto-commit changes [2025-12-03 09:30:45]
```

### Output Format

```
======================================================================
🔄 CORTEX Commit and Push Orchestrator
======================================================================
Repository: /Users/asifhussain/PROJECTS/CORTEX
Timestamp: 2025-12-03 07:46:10
======================================================================

📊 Step 1: Checking repository status...
   Found 9 file(s) to commit

📦 Step 2: Staging changes...
✅ Staged 9 file(s)

💾 Step 3: Creating commit...
✅ Commit created: 6904f7cd
   Message: Add Git Sync & Optimize orchestrator

🚀 Step 4: Pushing to remote...
✅ Pushed to origin/CORTEX-3.0

🔄 Step 5: Syncing with remote...
✅ Synced with remote

✨ Step 6: Final status check...

======================================================================
🎉 COMMIT AND PUSH COMPLETE
======================================================================
Commit: 6904f7cd
Branch: CORTEX-3.0
Remote: origin
Status: ✅ Clean
======================================================================
```

---

## 🔄 Integration with CORTEX

### Response Template Triggers

Both orchestrators are integrated into CORTEX response templates:

**Git Sync & Optimize:**
```yaml
triggers:
  - "sync with remote"
  - "pull and merge"
  - "optimize and sync"
  - "git sync"
```

**Commit & Push:**
```yaml
triggers:
  - "commit and push"
  - "save changes"
  - "push to remote"
```

### TDD Mastery Integration

**Git Checkpoint** - Create lightweight checkpoints during TDD
- File: `src/operations/git_checkpoint.py`
- Usage: `python3 -m src.operations.git_checkpoint create --phase RED`

**Git Sync** - Full sync and optimization
- File: `src/orchestrators/git_sync_and_optimize.py`
- Usage: When switching branches or syncing major changes

**Commit & Push** - Quick commits
- File: `src/operations/commit_and_push.py`
- Usage: Daily commits, checkpoint completion

---

## 🛡️ Safety Guarantees

### Git Sync & Optimize

✅ **Stash Preservation** - Work backed up before any operations  
✅ **Rollback Support** - Automatic recovery on failures  
✅ **Conflict Resolution** - Smart strategies by file type  
✅ **Non-Destructive** - Never loses uncommitted work  
✅ **Timestamped Backups** - Easy identification and recovery

### Commit & Push

✅ **Status Validation** - Checks for changes before committing  
✅ **Clean Staging** - Uses `git add -A` for comprehensive staging  
✅ **Remote Verification** - Confirms push success  
✅ **Sync Check** - Ensures consistency with origin  
✅ **Detailed Logging** - Clear visibility into each step

---

## 📊 Comparison Matrix

| Feature | Git Checkpoint | Commit & Push | Git Sync & Optimize |
|---------|---------------|---------------|---------------------|
| **Speed** | Fast (<2s) | Medium (5-10s) | Slow (30-120s) |
| **Scope** | TDD phases | Single commit | Full sync + optimize |
| **Stash** | No | No | Yes |
| **Pull** | No | No | Yes |
| **Merge** | No | No | Yes (intelligent) |
| **Optimize** | No | No | Yes |
| **Rollback** | No | No | Yes |
| **Use Case** | TDD checkpoints | Quick commits | Branch sync |

---

## 🎓 Best Practices

### When to Use Git Sync & Optimize

✅ Before starting a new feature branch  
✅ After merging major changes  
✅ When returning to work after time away  
✅ Before running system alignment  
✅ After pulling changes from team  
✅ When switching between major branches

### When to Use Commit & Push

✅ Daily work commits  
✅ Quick checkpoint after completing a task  
✅ Saving progress before meetings/breaks  
✅ Completing user stories  
✅ End-of-day commits

### When to Use Git Checkpoint

✅ During TDD RED phase  
✅ During TDD GREEN phase  
✅ During TDD REFACTOR phase  
✅ Between test-first cycles  
✅ Quick snapshots without push

---

## 🔧 Troubleshooting

### Git Sync & Optimize Issues

**Issue:** Merge conflicts not auto-resolved
```bash
# Check conflicted files
git status

# Manually resolve and continue
git add .
git stash drop
python3 src/orchestrators/git_sync_and_optimize.py
```

**Issue:** Stash not applied
```bash
# List stashes
git stash list

# Find your stash (CORTEX_sync_backup_*)
git stash show stash@{0}

# Manually apply
git stash pop stash@{0}
```

**Issue:** Optimization timeout
- Non-critical - sync completed successfully
- Run optimization separately if needed
- Check logs in `cortex-brain/documents/reports/`

### Commit & Push Issues

**Issue:** Nothing to commit
- Expected if no changes detected
- Verify with `git status`

**Issue:** Push rejected
```bash
# Pull first, then retry
git pull --rebase origin CORTEX-3.0
python3 src/operations/commit_and_push.py
```

---

## 📈 Performance Metrics

### Git Sync & Optimize
- Average execution: 45-90 seconds
- Stash operation: <1 second
- Pull operation: 2-10 seconds (network dependent)
- Merge operation: 1-5 seconds
- Optimization: 15-30 seconds
- Push operation: 2-10 seconds (network dependent)

### Commit & Push
- Average execution: 5-15 seconds
- Staging: 1-2 seconds
- Commit: <1 second
- Push: 2-10 seconds (network dependent)

---

## 🔗 Related Documentation

- **TDD Mastery:** `.github/prompts/modules/tdd-mastery-guide.md`
- **Git Checkpoint:** `src/operations/git_checkpoint.py`
- **Brain Protection:** `cortex-brain/brain-protection-rules.yaml`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

## ✅ Validation Checklist

**After Git Sync & Optimize:**
- [ ] Working directory clean
- [ ] Branch synced with origin
- [ ] No merge conflicts
- [ ] Optimization completed
- [ ] Results report generated

**After Commit & Push:**
- [ ] All changes committed
- [ ] Pushed to remote
- [ ] Branch up to date with origin
- [ ] Working directory clean

---

**Last Updated:** December 3, 2025  
**Tested On:** macOS, CORTEX 3.2.1  
**Status:** ✅ Production Ready
