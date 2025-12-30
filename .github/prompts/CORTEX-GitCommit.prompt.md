# 🔄 CORTEX Git Commit & Sync Automation

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Intelligent git workflow automation that stages, commits, pulls, merges, and pushes changes without editor suspension issues.

---

## ⚠️ CRITICAL: Editor Suspension Prevention

**ALWAYS use `GIT_EDITOR=true` for automated operations:**

```bash
# ❌ WRONG - Suspends process waiting for editor
git pull origin CORTEX-4.0 --no-rebase
git merge --continue

# ✅ CORRECT - Non-interactive, uses default messages
GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase
GIT_EDITOR=true git merge --continue
```

---

## 📋 Git Commit & Sync Workflow

### **Phase 1: Pre-Flight Checks**

**Check current status:**
```bash
git status
git branch --show-current
git log --oneline -5
```

**Verify remote connection:**
```bash
git remote -v
git fetch origin
```

---

### **Phase 2: Stage Changes**

**Stage all changes (modified + untracked):**
```bash
git add -A
```

**Verify staged files:**
```bash
git status --short
```

**Expected output patterns:**
- `M` = Modified file
- `A` = Added file (new/untracked)
- `D` = Deleted file

---

### **Phase 3: Commit Locally**

**Create descriptive commit message:**

```bash
git commit -m "feat(module): Brief description

- Detailed change 1
- Detailed change 2
- Detailed change 3"
```

**Commit message format:**
- `feat(scope):` - New feature
- `fix(scope):` - Bug fix
- `docs(scope):` - Documentation only
- `refactor(scope):` - Code refactoring
- `test(scope):` - Test additions
- `chore(scope):` - Maintenance tasks

---

### **Phase 4: Pull & Merge (Non-Interactive)**

**⚠️ CRITICAL: Always use GIT_EDITOR=true**

**Option A: Fast-Forward Pull (No Merge Needed)**
```bash
GIT_EDITOR=true git pull origin CORTEX-4.0 --ff-only
```

**Option B: Pull with Auto-Merge**
```bash
GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase
```

**If merge commits are needed:**
```bash
GIT_EDITOR=true git merge --continue
```

---

### **Phase 5: Conflict Resolution**

**If conflicts occur:**

1. **Identify conflicted files:**
   ```bash
   git status | grep "both modified"
   ```

2. **For each conflicted file:**
   - Open file
   - Look for conflict markers: `<<<<<<<`, `=======`, `>>>>>>>`
   - Choose correct version or merge manually
   - Remove conflict markers

3. **Stage resolved files:**
   ```bash
   git add <resolved-file>
   ```

4. **Continue merge:**
   ```bash
   GIT_EDITOR=true git merge --continue
   ```

---

### **Phase 6: Push to Origin**

**Push merged changes:**
```bash
git push origin CORTEX-4.0
```

**Verify push success:**
```bash
git status
```

**Expected output:**
```
On branch CORTEX-4.0
Your branch is up to date with 'origin/CORTEX-4.0'.

nothing to commit, working tree clean
```

---

## 🛡️ Common Issue Patterns & Solutions

### **Issue 1: Editor Suspension**

**Symptom:**
```
hint: Waiting for your editor to close the file...
zsh: suspended  git pull origin CORTEX-4.0
```

**Solution:**
```bash
# Always prefix with GIT_EDITOR=true
GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase
GIT_EDITOR=true git merge --continue
```

---

### **Issue 2: Untracked Files Remain**

**Symptom:**
```
Untracked files:
  (use "git add <file>..." to include in what will be committed)
```

**Solution:**
```bash
# Stage ALL untracked files
git add -A

# Or stage specific directory
git add cortex-brain/documents/
```

---

### **Issue 3: Divergent Branches**

**Symptom:**
```
Your branch and 'origin/CORTEX-4.0' have diverged,
and have 2 and 3 different commits each, respectively.
```

**Solution:**
```bash
# Fetch latest
git fetch origin

# View differences
git log HEAD..origin/CORTEX-4.0 --oneline

# Pull and merge (non-interactive)
GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase
```

---

### **Issue 4: Merge Conflicts**

**Symptom:**
```
CONFLICT (content): Merge conflict in <file>
Automatic merge failed; fix conflicts and then commit the result.
```

**Solution:**
```bash
# 1. Check conflicted files
git status

# 2. Resolve conflicts in each file
# 3. Stage resolved files
git add <resolved-file>

# 4. Continue merge (non-interactive)
GIT_EDITOR=true git merge --continue
```

---

### **Issue 5: Pre-Commit Hook Failures**

**Symptom:**
```
🔍 Checking for debug markers in staged files...
⚠️  Found 1 marker(s) in tests/...
```

**Solution:**
- Hook auto-removes markers
- Files are cleaned and re-staged
- Commit continues automatically
- **No manual intervention needed**

---

## 🔄 Complete Automation Script

**Save as:** `scripts/git-sync.sh`

```bash
#!/bin/bash
# CORTEX Git Sync Automation
# Usage: ./scripts/git-sync.sh "commit message"

set -e  # Exit on error

COMMIT_MSG="${1:-chore: sync workspace changes}"
BRANCH="${2:-CORTEX-4.0}"

echo "🔄 CORTEX Git Sync Starting..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Phase 1: Status Check
echo "📊 Phase 1: Checking status..."
git status --short

# Phase 2: Stage Changes
echo "📦 Phase 2: Staging changes..."
git add -A
echo "✅ Staged: $(git diff --cached --name-only | wc -l) files"

# Phase 3: Commit
echo "💾 Phase 3: Committing changes..."
git commit -m "$COMMIT_MSG" || echo "⚠️  Nothing to commit"

# Phase 4: Pull & Merge (Non-Interactive)
echo "⬇️  Phase 4: Pulling from origin..."
GIT_EDITOR=true git pull origin "$BRANCH" --no-rebase

# Phase 5: Verify Clean State
echo "🔍 Phase 5: Verifying state..."
if git status | grep -q "nothing to commit"; then
    echo "✅ Working tree clean"
else
    echo "⚠️  Uncommitted changes detected"
    git status
    exit 1
fi

# Phase 6: Push
echo "⬆️  Phase 6: Pushing to origin..."
git push origin "$BRANCH"

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ CORTEX Git Sync Complete!"
git log --oneline -1
```

**Make executable:**
```bash
chmod +x scripts/git-sync.sh
```

**Usage:**
```bash
# Basic sync
./scripts/git-sync.sh "feat: add new feature"

# Sync to different branch
./scripts/git-sync.sh "fix: bug fix" "main"
```

---

## 🎯 GitKraken MCP Tool Commands

**When using GitKraken MCP tools in VS Code:**

### **Stage Files:**
```
mcp_gitkraken_git_add_or_commit(
    action="add",
    directory="/Users/asifhussain/PROJECTS/CORTEX"
)
```

### **Commit:**
```
mcp_gitkraken_git_add_or_commit(
    action="commit",
    directory="/Users/asifhussain/PROJECTS/CORTEX",
    message="feat: your message here"
)
```

### **Pull (with manual merge if needed):**
```
# Use terminal with GIT_EDITOR=true instead of MCP tool
run_in_terminal(
    command="GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase",
    explanation="Pull and merge changes non-interactively"
)
```

### **Push:**
```
mcp_gitkraken_git_push(
    directory="/Users/asifhussain/PROJECTS/CORTEX"
)
```

### **Check Status:**
```
mcp_gitkraken_git_status(
    directory="/Users/asifhussain/PROJECTS/CORTEX"
)
```

---

## 📚 Quick Reference

| Action | Command |
|--------|---------|
| Stage all | `git add -A` |
| Commit | `git commit -m "message"` |
| Pull (non-interactive) | `GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase` |
| Continue merge | `GIT_EDITOR=true git merge --continue` |
| Push | `git push origin CORTEX-4.0` |
| Check status | `git status` |
| View log | `git log --oneline -5` |

---

## 🚨 Emergency Recovery

**If process gets suspended:**
```bash
# 1. Kill suspended process
fg  # Brings to foreground
Ctrl+C  # Cancel

# 2. Abort merge if needed
git merge --abort

# 3. Start fresh
git fetch origin
GIT_EDITOR=true git pull origin CORTEX-4.0 --no-rebase
```

**If merge goes wrong:**
```bash
# Reset to pre-merge state
git merge --abort

# Or reset to origin
git fetch origin
git reset --hard origin/CORTEX-4.0
```

---

## ✅ Success Criteria

**After successful sync, verify:**

1. ✅ `git status` shows: "nothing to commit, working tree clean"
2. ✅ `git status` shows: "Your branch is up to date with 'origin/CORTEX-4.0'"
3. ✅ No untracked files listed
4. ✅ `git log --oneline -5` shows your commits + merged commits

---

**Next Steps:** Use this prompt as reference for all future git sync operations to avoid editor suspension issues.
