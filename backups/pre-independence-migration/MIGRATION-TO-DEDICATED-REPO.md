# KDS Migration to Dedicated Repository

**Date:** 2025-11-04  
**Status:** 🚀 IN PROGRESS  
**Source:** `D:\PROJECTS\DevProjects\KDS`  
**Destination:** `https://github.com/asifhussain60/KDS`

---

## 📊 Migration Overview

**Purpose:** Move KDS to its own dedicated repository to:
- ✅ Prevent accidental merges with application code
- ✅ Enable independent KDS versioning and releases
- ✅ Simplify KDS development workflow
- ✅ Make KDS portable across projects
- ✅ Enforce git hooks for KDS-only commits

**Migration Strategy:** Git subtree extraction with full history preservation

---

## 🔄 Migration Steps

### Step 1: Create New GitHub Repository

**Manual Action Required:**
1. Go to https://github.com/new
2. Repository name: `KDS`
3. Description: "Knowledge-Driven System - Self-learning AI assistant framework"
4. Visibility: Public (or Private if preferred)
5. **DO NOT** initialize with README, .gitignore, or license (we'll push existing)
6. Click "Create repository"

**Expected Result:**
```
Repository URL: https://github.com/asifhussain60/KDS
Clone URL: https://github.com/asifhussain60/KDS.git
```

---

### Step 2: Extract KDS History and Push to New Repo

**PowerShell Script:** `migrate-kds-to-new-repo.ps1`

```powershell
<#
.SYNOPSIS
    Migrate KDS folder to dedicated repository with full git history

.DESCRIPTION
    Uses git filter-repo to extract KDS subfolder history and push to new repo.
    Preserves commits, authors, timestamps, and all KDS-related history.
#>

param(
    [Parameter(Mandatory=$false)]
    [string]$NewRepoUrl = "https://github.com/asifhussain60/KDS.git",
    
    [Parameter(Mandatory=$false)]
    [string]$TempDir = "$env:TEMP\KDS-migration-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
)

Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🔄 KDS Migration to Dedicated Repository" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Create temporary clone of DevProjects
Write-Host "[1/7] Creating temporary clone..." -ForegroundColor Yellow
git clone D:\PROJECTS\DevProjects $TempDir
if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to clone repository"
    exit 1
}
Set-Location $TempDir

# Step 2: Filter to keep only KDS folder history
Write-Host "`n[2/7] Extracting KDS folder history..." -ForegroundColor Yellow
Write-Host "  This will rewrite git history to keep only KDS-related commits" -ForegroundColor Gray

# Option A: Using git filter-branch (built-in, slower but works)
git filter-branch --subdirectory-filter KDS -- --all

# Clean up refs
git for-each-ref --format="%(refname)" refs/original/ | ForEach-Object {
    git update-ref -d $_
}
git reflog expire --expire=now --all
git gc --prune=now --aggressive

Write-Host "  ✅ KDS history extracted" -ForegroundColor Green

# Step 3: Add new remote
Write-Host "`n[3/7] Adding new remote..." -ForegroundColor Yellow
git remote remove origin
git remote add origin $NewRepoUrl
git remote -v

# Step 4: Create main branch if needed
Write-Host "`n[4/7] Setting up branches..." -ForegroundColor Yellow
$currentBranch = git branch --show-current
if ($currentBranch -ne "main") {
    git branch -M main
}

# Step 5: Push to new repository
Write-Host "`n[5/7] Pushing to new repository..." -ForegroundColor Yellow
Write-Host "  URL: $NewRepoUrl" -ForegroundColor Gray

git push -u origin main --force

if ($LASTEXITCODE -ne 0) {
    Write-Error "Failed to push to new repository"
    Write-Host "Please ensure:" -ForegroundColor Yellow
    Write-Host "  1. Repository exists at $NewRepoUrl" -ForegroundColor Yellow
    Write-Host "  2. You have push permissions" -ForegroundColor Yellow
    Write-Host "  3. You're authenticated with GitHub" -ForegroundColor Yellow
    exit 1
}

Write-Host "  ✅ Pushed successfully" -ForegroundColor Green

# Step 6: Push all branches/tags
Write-Host "`n[6/7] Pushing branches and tags..." -ForegroundColor Yellow
git push origin --all --force
git push origin --tags --force

# Step 7: Verify migration
Write-Host "`n[7/7] Verifying migration..." -ForegroundColor Yellow
$commitCount = git rev-list --count HEAD
Write-Host "  Total commits in new repo: $commitCount" -ForegroundColor Green
Write-Host "  Repository URL: $NewRepoUrl" -ForegroundColor Green

Write-Host ""
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ Migration Complete!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "  1. Verify new repository at: $NewRepoUrl" -ForegroundColor White
Write-Host "  2. Clone to new location: git clone $NewRepoUrl" -ForegroundColor White
Write-Host "  3. Delete KDS folder from DevProjects" -ForegroundColor White
Write-Host "  4. Update DevProjects documentation" -ForegroundColor White
Write-Host ""
Write-Host "Temp directory: $TempDir" -ForegroundColor Gray
Write-Host "  (Can be deleted after verification)" -ForegroundColor Gray
Write-Host ""

# Return to original directory
Set-Location D:\PROJECTS\DevProjects
```

**Run Migration:**
```powershell
.\KDS\scripts\migrate-kds-to-new-repo.ps1
```

---

### Step 3: Clone New KDS Repository

After migration succeeds:

```powershell
# Clone to dedicated location
cd D:\PROJECTS
git clone https://github.com/asifhussain60/KDS.git
cd KDS

# Verify contents
ls
# Should see all KDS folders: brain/, docs/, prompts/, scripts/, etc.

# Check commit history
git log --oneline | Select-Object -First 20
# Should see KDS-related commits with full history
```

---

### Step 4: Configure Git Hooks in New Repo

**Create Enhanced Pre-Commit Hook:**

File: `KDS/.git/hooks/pre-commit` (or use `KDS/hooks/pre-commit` and symlink)

```bash
#!/bin/bash
# KDS Pre-Commit Hook - Enforce KDS-only commits
# Installation: Copy to .git/hooks/pre-commit and chmod +x

echo "🔍 KDS Pre-Commit Hook - Validating commit..."

# 1. Ensure we're in KDS repository (not DevProjects or other projects)
REPO_NAME=$(git config --get remote.origin.url | grep -o '[^/]*\.git$' | sed 's/.git$//')

if [ "$REPO_NAME" != "KDS" ]; then
    echo "❌ ERROR: Not in KDS repository!"
    echo "   Current repo: $REPO_NAME"
    echo "   Expected: KDS"
    echo ""
    echo "⚠️  This commit is being rejected to prevent accidental merges."
    echo "   KDS development should only happen in the dedicated KDS repository."
    echo ""
    echo "If you're working on KDS:"
    echo "  1. Clone: git clone https://github.com/asifhussain60/KDS.git"
    echo "  2. Commit there instead"
    exit 1
fi

# 2. Validate commit message follows KDS conventions
COMMIT_MSG_FILE=$1
if [ -f "$COMMIT_MSG_FILE" ]; then
    COMMIT_MSG=$(cat "$COMMIT_MSG_FILE")
    
    # Check for conventional commit format (feat/fix/docs/chore/refactor)
    if ! echo "$COMMIT_MSG" | grep -qE "^(feat|fix|docs|chore|refactor|test|style|perf)\(kds\):"; then
        echo "⚠️  WARNING: Commit message should follow convention:"
        echo "   Format: <type>(kds): <description>"
        echo "   Examples:"
        echo "     feat(kds): Add multi-threaded crawler"
        echo "     fix(kds): Fix BRAIN feeder YAML parsing"
        echo "     docs(kds): Update Phase 2 completion summary"
        echo ""
        echo "Continue anyway? (y/N)"
        read -r response
        if [ "$response" != "y" ]; then
            exit 1
        fi
    fi
fi

# 3. Check for sensitive data
if git diff --cached --name-only | grep -qE '\.(env|key|secret|password)$'; then
    echo "❌ ERROR: Attempting to commit sensitive files!"
    echo "   Files with .env, .key, .secret, .password extensions are blocked"
    exit 1
fi

# 4. Validate BRAIN files are not corrupted
BRAIN_FILES=$(git diff --cached --name-only | grep 'kds-brain/.*\.yaml$')
if [ -n "$BRAIN_FILES" ]; then
    echo "  Validating BRAIN YAML files..."
    for file in $BRAIN_FILES; do
        if ! python -c "import yaml; yaml.safe_load(open('$file'))" 2>/dev/null; then
            echo "❌ ERROR: Invalid YAML in $file"
            exit 1
        fi
    done
    echo "  ✅ BRAIN files valid"
fi

echo "✅ Pre-commit validation passed"
exit 0
```

**Create Enhanced Post-Merge Hook:**

File: `KDS/.git/hooks/post-merge`

```bash
#!/bin/bash
# KDS Post-Merge Hook - Sync after merge

echo "🔄 KDS Post-Merge Hook - Syncing..."

# 1. Verify we're in KDS repo
REPO_NAME=$(git config --get remote.origin.url | grep -o '[^/]*\.git$' | sed 's/.git$//')

if [ "$REPO_NAME" != "KDS" ]; then
    echo "⚠️  WARNING: Not in KDS repository (found: $REPO_NAME)"
    exit 0
fi

# 2. Update BRAIN if needed
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q "kds-brain/events.jsonl"; then
    echo "  📊 Events updated - triggering BRAIN update..."
    # Optionally run brain-updater
    # pwsh -File scripts/brain-updater.ps1
fi

# 3. Check for schema changes
if git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD | grep -q "schemas/"; then
    echo "  📋 Schema changes detected - validate configurations"
fi

echo "✅ Post-merge sync complete"
exit 0
```

**Install Hooks:**
```powershell
# Copy hooks to .git/hooks
cd D:\PROJECTS\KDS
Copy-Item hooks\pre-commit .git\hooks\pre-commit -Force
Copy-Item hooks\post-merge .git\hooks\post-merge -Force

# Make executable (if on Linux/Mac)
# chmod +x .git/hooks/pre-commit
# chmod +x .git/hooks/post-merge
```

---

### Step 5: Delete KDS from DevProjects

**After verifying new repo works:**

```powershell
# 1. Verify new KDS repo is working
cd D:\PROJECTS\KDS
git status
git log --oneline | Select-Object -First 10

# 2. Back in DevProjects, remove KDS folder
cd D:\PROJECTS\DevProjects
Remove-Item -Path KDS -Recurse -Force

# 3. Create .gitignore entry (prevent re-adding)
Add-Content -Path .gitignore -Value "`n# KDS moved to dedicated repository`nKDS/`n"

# 4. Commit removal
git add .
git add .gitignore
git commit -m "chore: Remove KDS folder (moved to dedicated repository)

KDS has been migrated to its own repository for better isolation:
https://github.com/asifhussain60/KDS

This prevents accidental merges between KDS framework and application code."

git push origin features/kds
```

---

### Step 6: Update DevProjects Documentation

**Create Reference File:**

File: `D:\PROJECTS\DevProjects\KDS-MOVED.md`

```markdown
# KDS Location Change

**Date:** 2025-11-04

## KDS Has Moved! 🚀

The KDS (Knowledge-Driven System) framework has been migrated to its own dedicated repository for better isolation and development workflow.

### New Location

**Repository:** https://github.com/asifhussain60/KDS  
**Clone Command:**
```bash
git clone https://github.com/asifhussain60/KDS.git
```

### Why the Move?

1. **Prevent Accidental Merges** - KDS framework code stays separate from application code
2. **Independent Versioning** - KDS can have its own version releases
3. **Portable** - Easy to use KDS in multiple projects
4. **Cleaner Git History** - Each project has its own focused history

### Using KDS in This Project

If you need KDS functionality in this project:

**Option 1: Git Submodule (Recommended)**
```bash
git submodule add https://github.com/asifhussain60/KDS.git KDS
git submodule update --init --recursive
```

**Option 2: Manual Clone**
```bash
cd D:\PROJECTS
git clone https://github.com/asifhussain60/KDS.git
# Reference KDS from ../KDS/ in your scripts
```

**Option 3: NPM/PyPI Package (Future)**
When KDS is published as a package, install via:
```bash
npm install @asifhussain60/kds
# or
pip install kds-framework
```

### Migration History

- Original Location: `D:\PROJECTS\DevProjects\KDS`
- Migration Date: 2025-11-04
- Commits Preserved: All KDS-related history migrated to new repo
- New Default Branch: `main`

### Questions?

See new KDS repository README for documentation:
https://github.com/asifhussain60/KDS/blob/main/README.md
```

---

## 📋 Verification Checklist

After completing migration:

**New KDS Repository:**
- [ ] Repository created at https://github.com/asifhussain60/KDS
- [ ] All KDS folders present (brain/, docs/, prompts/, scripts/, etc.)
- [ ] Git history preserved (check with `git log`)
- [ ] Pre-commit hook installed and tested
- [ ] Post-merge hook installed and tested
- [ ] README.md renders correctly on GitHub
- [ ] Can clone repository successfully
- [ ] Can make commits (hook validation works)

**DevProjects Repository:**
- [ ] KDS folder deleted
- [ ] .gitignore updated to exclude KDS/
- [ ] Commit made to record removal
- [ ] KDS-MOVED.md reference file created
- [ ] Documentation updated (if applicable)
- [ ] No broken references to KDS paths

**Workflow Validation:**
- [ ] Can work in new KDS repo independently
- [ ] Accidental commits to wrong repo are blocked by hooks
- [ ] Can reference KDS from other projects (if needed)
- [ ] All team members aware of new location

---

## 🚀 Post-Migration: Resume KDS Development

Once migration is complete, continue KDS v6.0 implementation in new repository:

```powershell
# Work in dedicated KDS repository
cd D:\PROJECTS\KDS

# Continue Phase 3 (Database Evaluation)
# or
# Continue Phase 4 (E2E Integration & Testing)

# All KDS development happens here now
git status
git log
```

---

## ⚠️ Important Notes

**DO NOT:**
- ❌ Commit KDS changes to DevProjects anymore
- ❌ Keep both repositories in sync manually (use git submodule if needed)
- ❌ Delete temp migration directory until verified

**DO:**
- ✅ Work in `D:\PROJECTS\KDS` for all KDS development
- ✅ Use git hooks to prevent accidental commits
- ✅ Keep DevProjects focused on application code
- ✅ Reference new KDS repo URL in all documentation

---

## 🔄 Rollback Plan

If migration fails or issues arise:

**Rollback Steps:**
1. Temp directory still exists: `$env:TEMP\KDS-migration-*`
2. Original KDS folder backed up in DevProjects git history
3. Can restore with: `git checkout HEAD~1 -- KDS/`
4. Delete new GitHub repository
5. Continue in original location

---

**END OF MIGRATION GUIDE**
