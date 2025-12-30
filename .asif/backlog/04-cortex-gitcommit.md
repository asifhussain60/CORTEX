# 🔄 Git Sync Deletion Issue Fix

**Priority:** LOW | **Estimated Effort:** 15 min | **Category:** DevOps

---

## 🎯 Objective

Fix issue where deleted files on one machine are not removed when pulling on another machine.

---

## 📋 Problem Analysis

**Issue:** When files are deleted on Machine A and pushed, Machine B's `git pull` does not remove those files.

**Root Causes:**
1. Files may be ignored by `.gitignore`
2. Commits may not include deletions properly
3. Local untracked files may mask deletions
4. Branch tracking issues

---

## 📋 Execution Steps

### Step 1: Diagnose Current State
```bash
# Check for untracked files
git status --porcelain

# Check .gitignore patterns
cat .gitignore | grep -v "^#" | grep -v "^$"

# List files that should be tracked but aren't
git ls-files --others --exclude-standard
```

### Step 2: Verify Deletion Tracking
```bash
# Show recent commits with deletions
git log --diff-filter=D --summary --oneline -10

# Check if deletions are in remote
git fetch origin
git diff --name-status origin/CORTEX-4.0..HEAD
```

### Step 3: Create Pre-Commit Hook (if needed)
If deletions aren't being tracked, create hook:

**File:** `.git/hooks/pre-commit`
```bash
#!/bin/bash
# Ensure deletions are staged
git diff --name-only --diff-filter=D | while read file; do
    git add -u "$file" 2>/dev/null
done
```

### Step 4: Document Pull Best Practice
Add to project documentation:

**Recommended Pull Command:**
```bash
# Clean pull that respects deletions
git fetch origin
git reset --hard origin/CORTEX-4.0
# OR for safer approach:
git pull --rebase origin CORTEX-4.0
```

### Step 5: Create Sync Script (Optional)
**File:** `scripts/git-sync.sh`
```bash
#!/bin/bash
# Safe cross-machine sync
echo "🔄 Syncing with remote..."
git fetch --all --prune
git reset --hard origin/$(git branch --show-current)
echo "✅ Sync complete"
```

### Step 6: Test Fix
1. Delete a test file on current machine
2. Commit and push
3. On another machine, run sync command
4. Verify file is removed

---

## ✅ Success Criteria
- [ ] Deletions properly tracked in commits
- [ ] Pull operations remove deleted files
- [ ] Sync script created (if needed)
- [ ] Documentation updated

---

## 🗑️ AUTO-DELETE INSTRUCTION
**After successful execution:** Delete this file with:
```bash
rm -f /Users/asifhussain/PROJECTS/CORTEX/.asif/backlog/04-cortex-gitcommit.md
```
