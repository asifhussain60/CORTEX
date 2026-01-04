# 🔄 CORTEX Git Commit & Sync Automation

**Version:** 2.1.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

**Changelog:**
- **v2.1.0 (2026-01-04):** Enhanced conflict resolution, deleted folder sync, active work protection, planning folder gitignore bypass
- **v2.0.0:** Multi-machine sync verification, rename/move detection, force-sync recovery

---

## 🎯 Purpose

Intelligent git workflow automation with **multi-machine sync verification**, rename/move detection, and force-sync recovery.

---

## ⚠️ CRITICAL RULES

| Rule | Command Pattern |
|------|-----------------|
| **Editor Suspension Prevention** | Always use `GIT_EDITOR=true` prefix |
| **Multi-Machine Sync** | Use `git reset --hard origin/BRANCH` after pull |
| **Rename Detection** | Git tracks renames as delete+add (requires `git add -A`) |
| **Clean State Verification** | Always verify with `git status` after sync |
| **Large Changeset Handling** | 200+ files: Use GitKraken for staging (permission issues) |
| **Git Object Permission Fix** | If `git add` fails: Close VS Code, run as Admin, or use GitKraken |

---

## 🔐 Protecting Active Work During Sync

**Before force-sync on multi-machine setups:**

**Check for active planning folders:**
```bash
# List uncommitted files in planning folders
git status --short | Select-String "planning/active"

# Check specific planning folder
Test-Path "cortex-brain/documents/planning/active/[project-name]"
```

**Preserve work before sync:**
```bash
# Option 1: Stash (includes untracked files)
git stash push -u -m "Active work: [project-name]"

# Option 2: Create backup branch
git checkout -b backup/[project-name]-$(date +%Y%m%d)
git add -A
git commit -m "backup: Active work before sync"
git checkout CORTEX-5.0

# Option 3: Manual backup
Copy-Item "cortex-brain/documents/planning/active/[project-name]" `
          "backups/planning-[project-name]-backup" -Recurse
```

**After sync, restore:**
```bash
# From stash
git stash pop

# From backup branch
git checkout backup/[project-name]-20260104 -- "cortex-brain/documents/planning/active/[project-name]"

# From manual backup
Copy-Item "backups/planning-[project-name]-backup" `
          "cortex-brain/documents/planning/active/[project-name]" -Recurse
```

---

## 📋 Git Commit & Sync Workflow (7 Phases)

### **Phase 1: Pre-Flight Checks**

```bash
git status
git branch --show-current
git fetch origin
git log --oneline -3
```

### **Phase 1.5: Planning Folder Protection** ⭐ NEW

**CRITICAL:** Planning folders MUST always be on remote for CORTEX developers.

**Check for gitignored planning folders:**
```bash
# Detect planning folders being blocked by gitignore
$planningFolders = Get-ChildItem "cortex-brain/documents/planning/active/" -Directory -ErrorAction SilentlyContinue

foreach ($folder in $planningFolders) {
    $status = git check-ignore -v $folder.FullName 2>$null
    if ($status) {
        Write-Warning "⚠️ Planning folder ignored: $($folder.Name)"
        Write-Host "🛡️ Force-adding to ensure availability for CORTEX developers..."
        git add -f "$($folder.FullName)/*"
    }
}
```

**Why this matters:**
- Planning folders contain work-in-progress plans for CORTEX v5.0
- Other developers need access to active plans for collaboration
- Gitignore may accidentally catch planning folders (wildcards, patterns)
- `git add -A` respects gitignore and will skip these folders
- `git add -f` (force) bypasses gitignore for essential files

**Quick check:**
```bash
# List untracked planning folders
git status --short | Select-String "planning/active" | Where-Object { $_ -match "^\?\?" }

# Force-add any found
git add -f cortex-brain/documents/planning/active/*/
```

---

### **Phase 2: Stage Changes**

**Standard Staging (< 200 files):**
```bash
git add -A
git status --short
```

**Large Changeset Staging (200+ files):**

If `git add -A` fails with "Permission denied" errors:

**Option 1: GitKraken (RECOMMENDED for 200+ files)**
1. Open GitKraken
2. Stage all files via GUI (handles permissions better)
3. Return to terminal for commit/push

**Option 2: PowerShell Admin + Retry**
```powershell
# Close VS Code and any file locks
# Reopen PowerShell as Administrator
git gc --prune=now
git add -A
```

**Option 3: Incremental Staging**
```bash
# Stage by directory (slower but avoids permission issues)
git add docs/architecture/
git add docs/features/
git add docs/orchestrators/
# ... continue for each directory
```

**Status codes:** `M` = Modified | `A` = Added | `D` = Deleted | `R` = Renamed

### **Phase 3: Commit Locally**

```bash
git commit -m "type(scope): Brief description

- Detailed change 1
- Detailed change 2"
```

**Commit types:** `feat` | `fix` | `docs` | `refactor` | `test` | `chore`

### **Phase 4: Pull & Merge (Non-Interactive)**

```bash
GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase
```

**If merge needed:**
```bash
GIT_EDITOR=true git merge --continue
```

### **Phase 5: Conflict Resolution**

**Check for conflicts:**
```bash
git status                           # Shows "Unmerged paths"
git diff <conflicted-file>           # View conflict markers
```

**Resolution strategies:**

**A. Accept Remote (Clean Sync):**
```bash
git checkout --theirs <file>         # Accept remote version
git add <file>                       # Stage resolution
```

**B. Accept Local:**
```bash
git checkout --ours <file>           # Keep local version
git add <file>                       # Stage resolution
```

**C. Manual Merge:**
```bash
# Edit file, resolve <<<<<<< ======= >>>>>>> markers
git add <file>                       # Stage after manual edit
```

**Complete merge:**
```bash
GIT_EDITOR=true git merge --continue # Finalize merge
```

**⚠️ CRITICAL:** After resolving conflicts, ensure working tree is clean:
```bash
git status --short                   # Should show no unstaged changes
```

### **Phase 6: Push to Origin**

```bash
git push origin CORTEX-4.0
```

### **Phase 7: Multi-Machine Verification & Cleanup** ⭐ ENHANCED

**On other machines after push (MANDATORY for clean state):**

```bash
# Step 1: Fetch remote changes
git fetch origin

# Step 2: Check for deleted folders/files
git diff --name-status HEAD origin/CORTEX-5.0 | grep "^D"

# Step 3: Hard reset to remote (syncs deletions)
git reset --hard origin/CORTEX-5.0

# Step 4: Clean untracked files & deleted folders
git clean -fd

# Step 5: Verify clean state
git status                           # Should show "nothing to commit"
```

**Why each step matters:**
- `git fetch` downloads remote refs without modifying working tree
- `git diff --name-status` shows deleted files (prefixed with `D`)
- `git reset --hard` forces working tree to match remote exactly (includes deletions)
- `git clean -fd` removes untracked files AND empty directories left by deletions
- Final `git status` confirms sync success

**⚠️ CRITICAL for renamed/moved files:**
- `git pull` may NOT update working tree for renames/moves
- `git reset --hard` is REQUIRED to sync deleted source folders
- `git clean -fd` removes orphaned directories

**Protect active work (optional):**
```bash
# Before reset, preserve uncommitted work:
git stash push -u -m "Local work backup"

# After reset, restore if needed:
git stash pop
```

---

## 🔄 Force-Sync Commands (Multi-Machine)

**Standard sync (RECOMMENDED):**
```bash
git fetch origin
git reset --hard origin/CORTEX-5.0
git clean -fd
git status                           # Verify clean state
```

**With local work preservation:**
```bash
git stash push -u -m "Backup before sync"
git fetch origin
git reset --hard origin/CORTEX-5.0
git clean -fd
git stash pop                        # Restore local changes
```

**Emergency: Deleted folders not syncing:**
```bash
# This force-removes ALL untracked files and directories
git clean -fdx                       # -x removes ignored files too
```

**Check what will be deleted (dry run):**
```bash
git clean -fdn                       # Shows files/folders to be removed
```

---

## 🛡️ Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Git object permission denied** | `unable to write file .git/objects/` | Close VS Code → Run as Admin → `git gc --prune=now` → Retry OR use GitKraken |
| **Large changeset (200+ files)** | `git add` fails repeatedly | Use GitKraken GUI for staging (handles permissions better) |
| **Renamed files not appearing** | Old folders still exist | `git reset --hard origin/BRANCH && git clean -fd` |
| **Deleted folders persist** | Folders deleted remotely still exist locally | `git fetch && git reset --hard origin/BRANCH && git clean -fd` |
| **Pull causes conflicts** | `Unmerged paths` shown | Use `git checkout --theirs <file>` (remote) or `--ours` (local) |
| **Editor suspension** | `zsh: suspended` | Use `GIT_EDITOR=true` prefix |
| **Divergent branches** | `have diverged` | `GIT_EDITOR=true git pull --no-rebase` |
| **Untracked blocking** | `would be overwritten` | `git clean -fd` then pull |
| **Pre-commit hook** | `Found marker(s)` | Auto-handled, no action needed |
| **CRLF warnings** | `CRLF will be replaced by LF` | Normal on Windows, ignore (Git auto-converts) |
| **Merge in progress** | `You have unmerged paths` | Resolve conflicts → `git add` → `git merge --continue` |
| **Planning folder ignored** | `?? cortex-brain/documents/planning/active/[folder]/` persists after `git add -A` | `git add -f cortex-brain/documents/planning/active/[folder]/` (force-add bypasses gitignore) |

---

## 🎯 GitKraken MCP Tool Commands

```python
mcp_gitkraken_git_add_or_commit(action="add", directory="/path/to/repo")
mcp_gitkraken_git_add_or_commit(action="commit", directory="/path/to/repo", message="feat: message")
mcp_gitkraken_git_push(directory="/path/to/repo")
mcp_gitkraken_git_status(directory="/path/to/repo")
# Pull: use run_in_terminal with GIT_EDITOR=true
```

---

## 📚 Quick Reference

| Action | Command |
|--------|---------|
| **Force-add planning folders** | `git add -f cortex-brain/documents/planning/active/*/` |
| Stage all (small) | `git add -A` |
| Stage all (large 200+) | Use GitKraken GUI |
| Fix permission errors | `git gc --prune=now` (as Admin) |
| Commit | `git commit -m "message"` |
| Pull (non-interactive) | `GIT_EDITOR=true git pull origin CORTEX-5.0 --no-rebase` |
| Push | `git push origin CORTEX-5.0` |
| **Force-sync (multi-machine)** | `git fetch && git reset --hard origin/CORTEX-5.0 && git clean -fd` |
| **Resolve conflict (remote)** | `git checkout --theirs <file> && git add <file>` |
| **Resolve conflict (local)** | `git checkout --ours <file> && git add <file>` |
| Check deleted files | `git diff --name-status HEAD origin/CORTEX-5.0 \| grep "^D"` |
| Clean untracked | `git clean -fd` |
| Clean untracked (dry run) | `git clean -fdn` |
| Status | `git status` |

---

## 🚨 Emergency Recovery

**Abort operations:**
```bash
git merge --abort                                        # Abort merge
git rebase --abort                                       # Abort rebase
git add --renormalize .                                  # Fix CRLF issues
git reset --hard HEAD                                    # Discard all changes
```

**Reset to remote (clean slate):**
```bash
git fetch origin && git reset --hard origin/CORTEX-5.0   # Reset to remote
git clean -fd                                            # Remove untracked
git status                                               # Verify clean state
```

**Fix suspended process:**
```bash
fg && Ctrl+C                                             # Recover suspended process
```

**Fix .git/objects permission issues:**
```bash
git gc --prune=now                                       # Clean and repack (as Admin)
Remove-Item .git/index -Force; git reset                 # Rebuild index (PowerShell)
```

**Unstage files:**
```bash
git reset HEAD <file>                                    # Unstage specific file
git reset HEAD                                           # Unstage all files
```

**View conflict resolution options:**
```bash
git diff --name-status HEAD origin/CORTEX-5.0            # Compare local vs remote
git log --oneline HEAD..origin/CORTEX-5.0                # Commits you're missing
git log --oneline origin/CORTEX-5.0..HEAD                # Commits not pushed
```

---

## 🔧 Automation Decision Tree

**When to use GitKraken vs Terminal:**

```
File Count Check:
├── < 50 files → Terminal `git add -A` ✅
├── 50-200 files → Terminal (may need retry) ⚠️
└── 200+ files → GitKraken GUI (prevents permission errors) 🛡️

Permission Error Handling:
├── First attempt → `git gc --prune=now` + retry
├── Second attempt → Close VS Code + Run as Admin
└── Third attempt → Use GitKraken GUI ✅
```

---

## ✅ Success Criteria

After successful sync on ALL machines:

1. ✅ `git status` → "nothing to commit, working tree clean"
2. ✅ `git status` → "Your branch is up to date with 'origin/...'"
3. ✅ Working tree matches remote exactly (renamed files in correct locations)
4. ✅ Deleted folders removed locally (no orphaned directories)
5. ✅ `git log --oneline -3` shows same commits on all machines
6. ✅ `git diff --name-status HEAD origin/CORTEX-5.0` → empty output

**Verification commands:**
```bash
git status                                               # Clean working tree
git diff --name-status HEAD origin/CORTEX-5.0            # No differences
git log --oneline -3                                     # Recent commits match
ls -la                                                   # Visual inspection of folders
```

---

## 📊 Large Changeset Workflow (200+ Files)

**Recommended Process:**

1. **Check file count:** `(git status --short | Measure-Object).Count`
2. **If 200+:** Open GitKraken → Stage All via GUI
3. **Return to terminal:** `git status` (verify staged)
4. **Commit:** `git commit -m "message"`
5. **Pull:** `GIT_EDITOR=true git pull origin CORTEX-5.0 --no-rebase`
6. **Push:** `git push origin CORTEX-5.0`

**Why GitKraken for large changesets:**
- Better file handle management (no permission errors)
- Batched staging (reduces .git/objects contention)
- Visual progress feedback
- Automatic retry logic for locked files

---

**Anti-Bloat:** Enhanced with conflict resolution & deleted folder sync. Current: ~350 lines. Max 400 lines.
