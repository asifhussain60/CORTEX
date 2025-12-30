# 🔄 Git Sync Best Practices for CORTEX

**Author:** Asif Hussain  
**Last Updated:** December 30, 2025  
**Purpose:** Ensure deleted files are properly synchronized across machines

---

## 🎯 Problem Statement

When files are deleted on Machine A and pushed to the repository, a standard `git pull` on Machine B may not remove those files. This creates inconsistency across development environments.

---

## ✅ Solution

CORTEX provides dedicated sync scripts that use `git reset --hard` or `git pull --rebase` to ensure exact synchronization with the remote branch, including proper file deletions.

---

## 🛠️ Sync Scripts

### Windows (PowerShell)
```powershell
# Location
scripts/git-sync.ps1

# Standard sync (exact match with remote)
.\scripts\git-sync.ps1

# Safe sync (preserves local changes)
.\scripts\git-sync.ps1 -Safe

# Preview changes without executing
.\scripts\git-sync.ps1 -DryRun
```

### Linux/macOS (Bash)
```bash
# Location
scripts/git-pull-sync.sh

# Make executable (first time only)
chmod +x scripts/git-pull-sync.sh

# Standard sync (exact match with remote)
./scripts/git-pull-sync.sh

# Safe sync (preserves local changes)
./scripts/git-pull-sync.sh --safe

# Preview changes without executing
./scripts/git-pull-sync.sh --dry-run
```

---

## 📋 How It Works

### Standard Sync (Default)
1. **Fetch** all changes from remote with `--prune` (removes deleted branch refs)
2. **Display** what will be deleted, added, or modified
3. **Reset** local branch to exactly match remote: `git reset --hard origin/<branch>`
4. **Clean** orphaned untracked files (with confirmation)

**Use When:** You want your local state to exactly match the remote (discards local changes)

### Safe Sync (`-Safe` / `--safe`)
1. **Fetch** all changes from remote
2. **Display** changes
3. **Rebase** local commits on top of remote: `git pull --rebase origin <branch>`
4. **Clean** orphaned untracked files (with confirmation)

**Use When:** You have local uncommitted changes you want to preserve

---

## 🔍 What Gets Synced

| Change Type | Standard Sync | Safe Sync |
|-------------|---------------|-----------|
| **Remote deletions** | ✅ Removed locally | ✅ Removed locally |
| **Remote additions** | ✅ Added locally | ✅ Added locally |
| **Remote modifications** | ✅ Updated locally | ✅ Updated locally |
| **Local uncommitted changes** | ❌ Lost | ✅ Preserved |
| **Orphaned untracked files** | ❓ Asks to remove | ❓ Asks to remove |

---

## ⚠️ Important Notes

### Before Running Sync
- **Commit or stash** your work if using standard sync (local changes will be lost)
- **Review warnings** about uncommitted changes
- The script will **ask for confirmation** before proceeding

### After Running Sync
- Orphaned files from deleted directories may remain as **untracked**
- Script will **prompt** to clean them with `git clean -fd`
- Review the list before confirming removal

---

## 📝 Manual Sync Commands

If you prefer manual control:

### Standard Sync (Exact Match)
```bash
# Fetch and prune
git fetch --all --prune

# Show what will change
git diff --name-status origin/CORTEX-4.0

# Reset to match remote exactly
git reset --hard origin/CORTEX-4.0

# Clean orphaned files (optional)
git clean -fd
```

### Safe Sync (Preserve Local Changes)
```bash
# Fetch changes
git fetch origin

# Rebase local commits
git pull --rebase origin CORTEX-4.0

# Clean orphaned files (optional)
git clean -fd
```

---

## 🔍 Troubleshooting

### Files Not Being Deleted?

**Check if files are tracked:**
```bash
git ls-files <filename>
```
If no output, the file isn't tracked by git.

**Check if files are in .gitignore:**
```bash
git check-ignore -v <filename>
```

**Check recent deletions:**
```bash
git log --diff-filter=D --summary --oneline -10
```

### Untracked Files Remain After Sync?

These are likely new files created locally or orphaned from deleted directories.

**List untracked files:**
```bash
git ls-files --others --exclude-standard
```

**Remove them:**
```bash
git clean -fd
```

**Preview what would be removed:**
```bash
git clean -fdn
```

---

## 🎯 Recommended Workflow

### For Daily Development
Use the sync scripts at start of day to ensure you have latest changes:

**Windows:**
```powershell
.\scripts\git-sync.ps1
```

**Linux/macOS:**
```bash
./scripts/git-pull-sync.sh
```

### Before Starting New Work
If you have uncommitted changes you want to keep:

**Windows:**
```powershell
.\scripts\git-sync.ps1 -Safe
```

**Linux/macOS:**
```bash
./scripts/git-pull-sync.sh --safe
```

### To Preview Changes
Always run with dry-run first if uncertain:

**Windows:**
```powershell
.\scripts\git-sync.ps1 -DryRun
```

**Linux/macOS:**
```bash
./scripts/git-pull-sync.sh --dry-run
```

---

## 🛡️ Safety Features

Both sync scripts include:

1. **Status Check** - Shows uncommitted changes before proceeding
2. **Confirmation Prompt** - Asks before making destructive changes
3. **Change Preview** - Lists files that will be deleted/modified
4. **Dry Run Mode** - Preview without executing
5. **Orphan Detection** - Identifies untracked files from deleted directories
6. **Clean Confirmation** - Asks before removing untracked files

---

## 📚 Related Documentation

- **Git Basics:** [GitHub Git Handbook](https://guides.github.com/introduction/git-handbook/)
- **Git Reset:** [Git Documentation](https://git-scm.com/docs/git-reset)
- **Git Rebase:** [Atlassian Git Tutorial](https://www.atlassian.com/git/tutorials/rewriting-history/git-rebase)

---

## ✅ Success Criteria

After running sync, you should have:
- ✅ All remote deletions removed locally
- ✅ All remote additions present locally
- ✅ All remote modifications applied locally
- ✅ Working tree clean (or with intended local changes in safe mode)
- ✅ No orphaned files from deleted directories

---

**Note:** These scripts are part of CORTEX's cross-machine development workflow. They ensure consistency when working on multiple machines or collaborating with team members.
