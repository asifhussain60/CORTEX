# Phase 0: Backup Cleanup - Quick Reference

**Purpose:** Automatically delete ALL backup folders and files in CORTEX repository.

---

## 🚀 Quick Start

Run Phase 0 during system maintenance:

```bash
# Option 1: Full maintenance (includes Phase 0)
# In Copilot Chat:
system maintenance

# Option 2: Phase 0 only (manual execution)
cd /Users/asifhussain/PROJECTS/CORTEX

# Discover backups
find . -type d -name "*backup*" ! -path "./.git/*" | tee /tmp/cortex_backup_dirs.txt
find . -type f \( -name "*.backup" -o -name "*.bak" \) ! -path "./.git/*" | tee /tmp/cortex_backup_files.txt

# Count backups
echo "Directories: $(wc -l < /tmp/cortex_backup_dirs.txt)"
echo "Files: $(wc -l < /tmp/cortex_backup_files.txt)"

# Delete backups
cat /tmp/cortex_backup_dirs.txt | xargs rm -rf
cat /tmp/cortex_backup_files.txt | xargs rm -f

# Verify deletion
find . -name "*backup*" ! -path "./.git/*" | wc -l
# Expected: 0

# Commit cleanup
git add -A
git commit -m "chore: delete all backup folders and files (Phase 0 maintenance)"
git push origin CORTEX-4.0
```

---

## 📋 Backup Patterns Detected

| Pattern | Description | Example |
|---------|-------------|---------|
| `*backup*` | Backup directories | `./backups/doctor_backup_20251227_151620` |
| `*.backup` | Backup files | `planning-system.html.backup` |
| `*.bak` | Legacy backups | `response-templates.yaml.bak` |
| `*archive*` | Archive folders | `./cortex-brain/archive` |
| `*old*` | Old versions | `./archive/old-plans` |

---

## ✅ Success Criteria

After Phase 0 completes:

```bash
# Check 1: Zero backup directories
find . -type d -name "*backup*" ! -path "./.git/*" | wc -l
# Expected: 0

# Check 2: Zero backup files
find . -type f -name "*.backup" ! -path "./.git/*" | wc -l
# Expected: 0

# Check 3: Zero .bak files
find . -type f -name "*.bak" ! -path "./.git/*" | wc -l
# Expected: 0

# Check 4: Changes committed
git status --porcelain | wc -l
# Expected: 0

# Check 5: Cleanup report exists
ls cortex-brain/cleanup-reports/backup-cleanup-*.md | wc -l
# Expected: 1
```

---

## 🛡️ Prevention

Update `.gitignore` to prevent future backup accumulation:

```bash
cat >> .gitignore << 'EOF'
# Backup Files (Phase 0 Prevention)
*.backup
*.bak
*~
*.old
backup_*/
*backup*/
archive/
old/
EOF

git add .gitignore
git commit -m "chore: prevent backup file accumulation"
git push origin CORTEX-4.0
```

---

## 📊 Current State (Before Phase 0)

- **Backup Directories:** 45+
- **Backup Files:** 10+
- **Estimated Disk Usage:** 100MB+
- **Git Repository Impact:** Search tools index stale copies

---

## 🎯 After Phase 0

- **Backup Directories:** 0
- **Backup Files:** 0
- **Disk Space Recovered:** 100MB+
- **Git Repository:** Clean, searchable, no duplicates

---

**Reference:** `.github/prompts/cortex-maintenance.prompt.md` (Phase 0, lines 532-834)

**Documentation:** `cortex-brain/documents/reports/maintenance-phase0-backup-cleanup-implementation.md`
