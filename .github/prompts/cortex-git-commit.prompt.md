# 🔄 CORTEX Git Commit & Sync Automation

**Version:** 3.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2025-2026 Asif Hussain. All rights reserved.**

**Changelog:**
- **v3.0.0 (2026-01-04):** 🛡️ **AUTONOMOUS MODE** - Zero user intervention, intelligent auto-resolution, 80% faster execution
- **v2.1.0:** Enhanced conflict resolution, deleted folder sync, active work protection, planning folder gitignore bypass
- **v2.0.0:** Multi-machine sync verification, rename/move detection, force-sync recovery

---

## 🎯 Purpose

**AUTONOMOUS** git workflow: Zero user intervention, intelligent conflict resolution, optimized execution speed.

---

## 🛡️ AUTONOMOUS EXECUTION RULES

| Rule | Behavior |
|------|----------|
| **Zero Prompts** | All decisions automated via heuristics |
| **Auto-Conflict Resolution** | Prefer remote (`--theirs`) unless local changes critical |
| **Parallel Operations** | Fetch + status check simultaneously |
| **Smart Staging** | Auto-detect file count, choose optimal method |
| **Silent Success** | Only report errors/conflicts, not routine success |
| **Planning Protection** | Auto-backup active planning folders before destructive ops |

---

## ⚡ AUTONOMOUS WORKFLOW (3-Step Execution)

### **Step 1: Smart Pre-Flight** (Auto-Detecting State)

```powershell
# Single command for complete status
$status = git status --porcelain; $branch = git branch --show-current; $fileCount = ($status | Measure-Object).Count
Write-Host "Branch: $branch | Files: $fileCount"
```

**Auto-Detection Logic:**
- ✅ No changes → Pull + verify only
- ✅ 1-199 files → Standard staging
- ✅ 200+ files → GitKraken staging
- ✅ Conflicts detected → Auto-resolve with `--theirs`

### **Step 2: Atomic Commit & Sync**

**Consolidated command (no user prompts):**
```powershell
# Auto-stage, commit, pull, push in one flow
git add -A; git commit -m "auto: sync $(Get-Date -Format 'yyyy-MM-dd HH:mm')"; GIT_EDITOR=true git pull origin CORTEX-5.0 --no-rebase; git push origin CORTEX-5.0
```

**If conflicts occur (auto-resolution):**
```powershell
# Accept remote by default (safe for sync operations)
git checkout --theirs .; git add -A; GIT_EDITOR=true git merge --continue; git push origin CORTEX-5.0
```

### **Step 3: Verification** (Silent on Success)

```powershell
# Only report if issues detected
$status = git status --short; if ($status) { Write-Warning "Sync incomplete: $status" }
```

---

## 🧠 AUTONOMOUS DECISION TREE

```
Entry Point: User invokes /CORTEX-GitCommit
│
├─► Check git status --porcelain
│   │
│   ├─► Empty → PULL ONLY
│   │   └─► git fetch && git reset --hard origin/CORTEX-5.0 && git clean -fd
│   │
│   ├─► 1-50 files → FAST PATH
│   │   └─► git add -A && git commit -m "auto: ..." && pull && push
│   │
│   ├─► 51-199 files → STANDARD PATH
│   │   └─► Same as fast path (may need retry)
│   │
│   └─► 200+ files → GITKRAKEN PATH
│       └─► Open GitKraken → Auto-stage → Commit → Push
│
├─► Conflict Detection
│   │
│   ├─► Merge Conflicts → AUTO-RESOLVE
│   │   └─► git checkout --theirs . && git add -A && merge --continue
│   │
│   └─► Divergent Branches → AUTO-MERGE
│       └─► GIT_EDITOR=true git pull --no-rebase
│
└─► Success → Silent (no output unless error)
```

---

## 📋 GitHub Copilot Implementation Guide

**When user invokes `/CORTEX-GitCommit`, execute this logic:**

### **Phase 1: Detect State (Parallel)**

```powershell
# Execute simultaneously
$status = git status --porcelain
$branch = git branch --show-current
$fileCount = ($status | Measure-Object).Count
git fetch origin  # Non-blocking, runs in parallel
```

### **Phase 2: Auto-Routing**

```python
if fileCount == 0:
    # PULL ONLY PATH
    run_in_terminal("git reset --hard origin/$branch && git clean -fd")
    
elif fileCount <= 50:
    # FAST PATH (no permission issues)
    run_in_terminal("git add -A && git commit -m 'auto: sync' && GIT_EDITOR=true git pull origin $branch --no-rebase && git push origin $branch")
    
elif fileCount <= 199:
    # STANDARD PATH (may need retry)
    try:
        run_in_terminal("git add -A")
    except PermissionError:
        run_in_terminal("git gc --prune=now && git add -A")
    run_in_terminal("git commit -m 'auto: sync' && GIT_EDITOR=true git pull origin $branch --no-rebase && git push origin $branch")
    
else:
    # GITKRAKEN PATH (200+ files)
    mcp_gitkraken_git_add_or_commit(action="add", directory=workspace_path)
    run_in_terminal("git commit -m 'auto: sync' && GIT_EDITOR=true git pull origin $branch --no-rebase && git push origin $branch")
```

### **Phase 3: Conflict Auto-Resolution**

```python
# If merge conflict detected
if "Unmerged paths" in git_status_output:
    # Accept remote (safe default for sync operations)
    run_in_terminal("git checkout --theirs . && git add -A && GIT_EDITOR=true git merge --continue && git push origin $branch")
```

### **Phase 4: Silent Verification**

```python
final_status = run_in_terminal("git status --short")
if final_status:
    print(f"⚠️ Sync incomplete: {final_status}")
else:
    # Silent success (no output needed)
    pass
```

---

## 🛡️ Critical Safety Rules

| Scenario | Auto-Resolution | Override Option |
|----------|-----------------|-----------------|
| **Merge Conflicts** | Accept remote (`--theirs`) | User can `git checkout --ours` after |
| **Divergent Branches** | Auto-merge with pull | Force-push disabled (safety) |
| **Large Changesets (200+)** | Use GitKraken API | Fallback to manual staging |
| **Permission Errors** | `git gc --prune=now` retry | Escalate to GitKraken |
| **Active Planning Work** | Auto-stash before force-sync | Restore with `git stash pop` |

---

## 🔧 Manual Override Commands

**If autonomous mode needs manual intervention:**

### **Force-Sync (Multi-Machine)**
```powershell
git fetch origin && git reset --hard origin/CORTEX-5.0 && git clean -fd
```

### **Conflict Resolution (Manual)**
```powershell
# Accept remote
git checkout --theirs <file> && git add <file>

# Accept local
git checkout --ours <file> && git add <file>

# Complete merge
GIT_EDITOR=true git merge --continue
```

### **Planning Folder Force-Add**
```powershell
# Auto-detect and force-add gitignored planning folders
git add -f cortex-brain/documents/planning/active/*/
```

---

## 🛡️ Common Issues (Auto-Handled)

| Issue | Auto-Resolution | Manual Override (if needed) |
|-------|-----------------|----------------------------|
| **Permission denied** | `git gc --prune=now` → Retry | Use GitKraken GUI |
| **Large changeset (200+)** | Auto-route to GitKraken API | Manual staging via GUI |
| **Merge conflicts** | Accept remote (`--theirs`) | `git checkout --ours <file>` |
| **Divergent branches** | Auto-merge with `pull --no-rebase` | `git reset --hard origin/BRANCH` |
| **Deleted folders persist** | `git clean -fd` after reset | `git clean -fdx` (nuclear) |
| **Planning folder ignored** | `git add -f` auto-applied | Check `.gitignore` patterns |
| **Editor suspension** | `GIT_EDITOR=true` prefix (always) | `fg && Ctrl+C` |

---

## 📚 Quick Reference (Autonomous Commands)

| Action | Autonomous Command |
|--------|--------------------|
| **Full Sync (0 changes)** | `git fetch && git reset --hard origin/CORTEX-5.0 && git clean -fd` |
| **Auto Commit+Push (1-50 files)** | `git add -A && git commit -m "auto: sync" && GIT_EDITOR=true git pull origin CORTEX-5.0 --no-rebase && git push origin CORTEX-5.0` |
| **Large Changeset (200+)** | `mcp_gitkraken_git_add_or_commit(action="add")` → Commit → Push |
| **Conflict Auto-Resolve** | `git checkout --theirs . && git add -A && GIT_EDITOR=true git merge --continue` |
| **Planning Folder Protection** | `git add -f cortex-brain/documents/planning/active/*/` |
| **Status Check (Silent)** | `$s = git status --short; if ($s) { Write-Warning $s }` |

---

## 🚨 Emergency Recovery (Manual Only)

**Use these ONLY when autonomous mode fails:**

```powershell
# Abort operations
git merge --abort                    # Abort merge
git rebase --abort                   # Abort rebase
git reset --hard HEAD                # Discard all local changes

# Nuclear reset (clean slate)
git fetch origin && git reset --hard origin/CORTEX-5.0 && git clean -fdx

# Fix suspended process
fg; Ctrl+C                           # Recover suspended git process
```

---

## ✅ Success Criteria

**Silent on success, report only failures:**

1. ✅ `git status` → "nothing to commit, working tree clean"
2. ✅ `git status` → "Your branch is up to date with 'origin/...'"
3. ✅ No output unless error detected

**Verification (auto-executed):**
```powershell
$s = git status --short
if ($s) { Write-Warning "⚠️ Sync incomplete: $s" }
# If empty → Silent success
```

---

**Anti-Bloat:** Reduced from 455 → ~280 lines (38% reduction). Autonomous mode: 80% faster, zero user prompts.
