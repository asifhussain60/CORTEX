# 🔄 CORTEX Git Commit & Sync Automation

**Version:** 2.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

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

## 📋 Git Commit & Sync Workflow (7 Phases)

### **Phase 1: Pre-Flight Checks**

```bash
git status
git branch --show-current
git fetch origin
git log --oneline -3
```

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

```bash
git status | grep "both modified"    # Identify conflicts
git add <resolved-file>              # Stage after resolving
GIT_EDITOR=true git merge --continue # Complete merge
```

### **Phase 6: Push to Origin**

```bash
git push origin CORTEX-4.0
```

### **Phase 7: Multi-Machine Verification** ⭐ NEW

**On other machines after push:**

```bash
git fetch origin
git reset --hard origin/CORTEX-4.0
git clean -fd
```

**Why this matters:**
- `git pull` may not update working tree for renames/moves
- `git reset --hard` forces working tree to match remote exactly
- `git clean -fd` removes untracked files blocking renamed paths

---

## 🔄 Force-Sync Commands (Multi-Machine)

```bash
# Hard reset to remote (RECOMMENDED)
git fetch origin
git reset --hard origin/CORTEX-4.0
git clean -fd

# Preserve local changes first
git stash && git reset --hard origin/CORTEX-4.0 && git stash pop
```

---

## 🛡️ Common Issues & Solutions

| Issue | Symptom | Solution |
|-------|---------|----------|
| **Git object permission denied** | `unable to write file .git/objects/` | Close VS Code → Run as Admin → `git gc --prune=now` → Retry OR use GitKraken |
| **Large changeset (200+ files)** | `git add` fails repeatedly | Use GitKraken GUI for staging (handles permissions better) |
| **Renamed files not appearing** | Old folders still exist | `git reset --hard origin/BRANCH && git clean -fd` |
| **Editor suspension** | `zsh: suspended` | Use `GIT_EDITOR=true` prefix |
| **Divergent branches** | `have diverged` | `GIT_EDITOR=true git pull --no-rebase` |
| **Untracked blocking** | `would be overwritten` | `git clean -fd` then pull |
| **Pre-commit hook** | `Found marker(s)` | Auto-handled, no action needed |
| **CRLF warnings** | `CRLF will be replaced by LF` | Normal on Windows, ignore (Git auto-converts) |

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
| Stage all (small) | `git add -A` |
| Stage all (large 200+) | Use GitKraken GUI |
| Fix permission errors | `git gc --prune=now` (as Admin) |
| Commit | `git commit -m "message"` |
| Pull (non-interactive) | `GIT_EDITOR=true git pull origin CORTEX-5.0 --no-rebase` |
| Push | `git push origin CORTEX-5.0` |
| **Force-sync (multi-machine)** | `git fetch origin && git reset --hard origin/CORTEX-4.0` |
| Clean untracked | `git clean -fd` |
| Status | `git status` |

---

## 🚨 Emergency Recovery

```bash
# Abort operations
git merge --abort                                        # Abort merge
git add --renormalize .                                  # Fix CRLF issues
git reset --hard HEAD                                    # Discard all changes

# Reset to remote
git fetch origin && git reset --hard origin/CORTEX-5.0   # Reset to remote
fg && Ctrl+C                                             # Recover suspended process

# Fix .git/objects permission issues
git gc --prune=now                                       # Clean and repack (as Admin)
Remove-Item .git/index -Force; git reset                 # Rebuild index (PowerShell)
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
4. ✅ `git log --oneline -3` shows same commits on all machines

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

**Anti-Bloat:** This file is ~220 lines. Max 250 lines.
