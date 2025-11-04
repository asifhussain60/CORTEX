# KDS Branch Isolation - Complete Protection System

**Purpose:** Ensure KDS development stays isolated in the `KDS/` folder and never accidentally contaminates other branches or project code.

**Status:** ✅ Active  
**Date:** 2025-11-04  
**Git Hooks:** `pre-commit`, `post-merge`

---

## 🎯 Problem Statement

**Challenge:** KDS is a self-contained development system that should never mix with application code. We need to prevent:

❌ **Accidental KDS commits on application branches** (master, develop, feature/*)  
❌ **Non-KDS files in KDS commits** (mixing application code with KDS changes)  
❌ **KDS system files leaking into application branches**  
❌ **Forgetting which branch you're on** (manual context switching is error-prone)

**Solution:** Automated git hooks that enforce complete isolation.

---

## 🛡️ Protection System Architecture

### Branch Structure

```
master (or main)           → Application development
  ├── feature/user-auth    → Application features
  ├── feature/new-ui       → Application features
  └── ...
  
features/kds               → KDS-ONLY development (ISOLATED)
  └── (ALL KDS changes live here)
```

**Rule:** KDS changes = `features/kds` branch. Application changes = any other branch.

### Git Hooks

**1. Pre-Commit Hook** (`KDS/hooks/pre-commit`)
- ✅ Enforces `features/kds` branch for KDS commits
- ✅ Blocks commits if on wrong branch
- ✅ Validates ONLY KDS/ files are in commit
- ✅ Rejects non-KDS files in KDS commits
- ✅ Runs KDS light checks before commit

**2. Post-Merge Hook** (`KDS/hooks/post-merge`)
- ✅ Auto-returns to `features/kds` after merging KDS to other branches
- ✅ Prevents "forgetting to switch back" errors
- ✅ Seamless workflow (merge → auto-switch)

---

## 🚀 Setup (One-Time Installation)

### Automatic Installation

Run the setup script from your workspace root:

```powershell
.\KDS\scripts\setup-kds-branch-protection.ps1
```

**What it does:**
1. Creates `features/kds` branch (if doesn't exist)
2. Installs git hooks to `.git/hooks/`
3. Switches you to `features/kds` automatically
4. Stashes uncommitted changes if needed

**Force reinstall:**
```powershell
.\KDS\scripts\setup-kds-branch-protection.ps1 -Force
```

### Manual Installation (Alternative)

If you prefer manual installation:

```powershell
# Create branch
git branch features/kds

# Copy hooks
Copy-Item KDS/hooks/pre-commit .git/hooks/pre-commit -Force
Copy-Item KDS/hooks/post-merge .git/hooks/post-merge -Force

# Switch to KDS branch
git checkout features/kds
```

---

## 📋 Daily Workflow

### Working on KDS

**Always work on `features/kds` branch:**

```powershell
# Switch to KDS branch (if not already there)
git checkout features/kds

# Make KDS changes
# Edit KDS/prompts/user/kds.md, add new agents, etc.

# Stage and commit (hooks will validate)
git add KDS/
git commit -m "feat(kds): Add new screenshot analyzer agent"

# ✅ Hook validates: ONLY KDS/ files, correct branch
```

**If you accidentally try to commit KDS on wrong branch:**

```bash
❌ ERROR: KDS changes ONLY allowed on features/kds branch

Current branch: master
Required branch: features/kds

To fix:
  git checkout features/kds
  git cherry-pick <commit-hash>
```

### Working on Application Code

**Switch to application branch:**

```powershell
# Switch to master/feature branch
git checkout master

# Make application changes
# Edit SPA/NoorCanvas/Pages/HostControlPanel.razor, etc.

# Stage and commit
git add SPA/
git commit -m "feat: Add PDF export to canvas"

# ✅ No KDS files = hooks don't interfere
```

**If you accidentally include KDS files on application branch:**

```bash
❌ ERROR: KDS branch ONLY for KDS/ changes

Non-KDS files detected in commit:
KDS/prompts/user/kds.md

To fix:
  1. git reset HEAD KDS/prompts/user/kds.md
  2. Commit non-KDS files on current branch
  3. git checkout features/kds (for KDS changes)
```

### Merging KDS to Application Branches

**Standard merge workflow:**

```powershell
# 1. Ensure KDS changes are committed
git checkout features/kds
git add KDS/
git commit -m "feat(kds): Complete brain amnesia feature"

# 2. Switch to target branch (e.g., master)
git checkout master

# 3. Merge KDS changes
git merge features/kds

# 4. Post-merge hook AUTO-SWITCHES back to features/kds!
# 🔄 KDS Merge Detected - Returning to features/kds branch
# ✅ Successfully returned to features/kds
# 📝 Ready for next KDS change
```

**Result:** You're automatically back on `features/kds` after merge. Zero manual switching!

---

## 🧪 Testing the Protection System

### Test 1: KDS Commit on Wrong Branch (Should FAIL)

```powershell
# Start on master branch
git checkout master

# Try to commit KDS changes
git add KDS/prompts/user/kds.md
git commit -m "test"

# Expected Output:
# ❌ ERROR: KDS changes ONLY allowed on features/kds branch
# Commit BLOCKED
```

### Test 2: Non-KDS Files in KDS Commit (Should FAIL)

```powershell
# On features/kds branch
git checkout features/kds

# Try to commit mixed files
git add KDS/prompts/user/kds.md
git add SPA/NoorCanvas/Pages/HostControlPanel.razor
git commit -m "test"

# Expected Output:
# ❌ ERROR: KDS branch ONLY for KDS/ changes
# Non-KDS files detected: SPA/NoorCanvas/Pages/HostControlPanel.razor
# Commit BLOCKED
```

### Test 3: KDS-Only Commit on features/kds (Should SUCCEED)

```powershell
# On features/kds branch
git checkout features/kds

# Commit only KDS files
git add KDS/
git commit -m "feat(kds): New feature"

# Expected Output:
# ✅ KDS-only commit validated
# 📁 Files in commit:
#    - KDS/prompts/user/kds.md
# 🔎 Running KDS light checks...
# ✅ KDS light checks passed
# [features/kds abc1234] feat(kds): New feature
```

### Test 4: Auto-Return After Merge (Should SUCCEED)

```powershell
# Merge KDS to master
git checkout master
git merge features/kds

# Expected Output:
# ... merge output ...
# 🔄 KDS Merge Detected - Returning to features/kds branch
# ✅ Successfully returned to features/kds
# 📝 Ready for next KDS change

# Verify
git branch --show-current
# features/kds ✅
```

---

## 🔧 Troubleshooting

### Hook Not Running

**Symptom:** Commits succeed without validation

**Causes:**
1. Hooks not installed in `.git/hooks/`
2. Hooks not executable (rare on Windows)
3. Git hooks disabled globally

**Fix:**
```powershell
# Reinstall hooks
.\KDS\scripts\setup-kds-branch-protection.ps1 -Force

# Verify installation
Get-ChildItem .git\hooks\ | Where-Object { $_.Name -in @("pre-commit", "post-merge") }

# Check git config
git config core.hooksPath  # Should be empty (use default .git/hooks/)
```

### Accidentally Committed KDS on Wrong Branch

**Scenario:** You bypassed hooks (e.g., `git commit --no-verify`) and committed KDS to master.

**Fix:**
```powershell
# Option 1: Revert the commit
git revert HEAD

# Option 2: Cherry-pick to correct branch
git checkout features/kds
git cherry-pick <commit-hash-from-master>

# Then remove from wrong branch
git checkout master
git reset --hard HEAD~1  # ⚠️ DESTRUCTIVE - use with caution
```

### Post-Merge Hook Not Auto-Switching

**Symptom:** After merging KDS to master, you stay on master

**Possible Causes:**
1. Post-merge hook not installed
2. Merge conflicts (hook doesn't run if conflicts exist)
3. Fast-forward merge (hook may not trigger)

**Fix:**
```powershell
# Manual switch
git checkout features/kds

# Reinstall hook
.\KDS\scripts\setup-kds-branch-protection.ps1 -Force
```

### Need to Disable Hooks Temporarily

**Scenario:** Emergency fix, need to bypass validation

**Option 1: Skip hooks for one commit**
```powershell
git commit --no-verify -m "emergency fix"
```

**Option 2: Temporarily disable hooks**
```powershell
# Rename hooks (disable)
Rename-Item .git\hooks\pre-commit .git\hooks\pre-commit.disabled
Rename-Item .git\hooks\post-merge .git\hooks\post-merge.disabled

# Do your work...

# Re-enable hooks
Rename-Item .git\hooks\pre-commit.disabled .git\hooks\pre-commit
Rename-Item .git\hooks\post-merge.disabled .git\hooks\post-merge
```

---

## 📊 Hook Behavior Reference

### Pre-Commit Hook Logic

```
IF current_branch != "features/kds":
  ❌ REJECT commit (wrong branch)
  EXIT 1

ELSE IF commit contains non-KDS files:
  ❌ REJECT commit (non-KDS files detected)
  EXIT 1

ELSE:
  ✅ Run KDS light checks
  IF light checks FAIL:
    ❌ REJECT commit (KDS violations)
    EXIT 1
  ELSE:
    ✅ ALLOW commit
    EXIT 0
```

### Post-Merge Hook Logic

```
IF current_branch != "features/kds":
  🔄 Auto-switch to features/kds
  IF switch successful:
    ✅ Display success message
  ELSE:
    ⚠️  Display manual switch instruction
```

---

## 🎯 Benefits of This System

✅ **Zero accidental contamination** - Hooks enforce isolation automatically  
✅ **Seamless workflow** - Auto-switch after merges, no manual tracking  
✅ **Clear separation** - KDS = features/kds, App = any other branch  
✅ **Fast feedback** - Pre-commit validation catches mistakes immediately  
✅ **Light overhead** - Hooks run in <1 second, minimal performance impact  
✅ **Foolproof** - Can't commit wrong files even if you forget branch  

---

## 📝 Commit Message Conventions (KDS)

**Format:** `<type>(kds): <description>`

**Types:**
- `feat(kds):` New KDS feature (agent, prompt, script)
- `fix(kds):` Bug fix in KDS system
- `docs(kds):` Documentation updates
- `refactor(kds):` Code refactoring
- `test(kds):` Test-related changes
- `chore(kds):` Maintenance (dependencies, configs)

**Examples:**
```
feat(kds): Add brain amnesia feature for application reset
fix(kds): Correct pre-commit hook path resolution
docs(kds): Add branch isolation documentation
refactor(kds): Split intent router into modular functions
test(kds): Add validation tests for commit handler
chore(kds): Update .gitignore for BRAIN state files
```

---

## 🔄 Migration from Other Workflows

### If You Were Committing KDS on Master

**Old workflow:**
```powershell
git checkout master
# Edit KDS and application files
git add .
git commit -m "mixed changes"  # ❌ BAD
```

**New workflow:**
```powershell
# Application changes
git checkout master
git add SPA/ Controllers/ Services/
git commit -m "feat: Add new feature"

# KDS changes
git checkout features/kds
git add KDS/
git commit -m "feat(kds): Update agent"

# Merge KDS when ready
git checkout master
git merge features/kds  # Auto-returns to features/kds
```

---

## 📚 Related Documentation

- **KDS Design:** `KDS/KDS-DESIGN.md`
- **Brain Amnesia:** `KDS/BRAIN-AMNESIA-IMPLEMENTATION.md`
- **Commit Handler:** `KDS/scripts/commit-kds-changes.ps1`
- **Git Hooks Source:** `KDS/hooks/`

---

## ✅ Setup Checklist

After running setup, verify:

- [ ] `features/kds` branch exists (`git branch --list features/kds`)
- [ ] Pre-commit hook installed (`.git/hooks/pre-commit` exists)
- [ ] Post-merge hook installed (`.git/hooks/post-merge` exists)
- [ ] Currently on `features/kds` branch (`git branch --show-current`)
- [ ] Test: Try committing KDS on master (should fail)
- [ ] Test: Commit KDS on features/kds (should succeed)
- [ ] Test: Merge to master, verify auto-return to features/kds

---

**Ready to use!** 🚀

Your KDS development is now fully isolated and protected. Work on `features/kds`, merge when ready, and let the hooks handle the rest.
