# CORTEX Vacuum - Quick Operations Guide
**Version:** 1.0 | **Updated:** 2026-01-24 | **Status:** Ready for Use

---

## 🚀 Essential Commands

### Analysis Phase
```bash
# 1. Full repository scan
cortex-vacuum /vacuum-analyze

# 2. See recommendations without changes
cortex-vacuum /vacuum-recommend --dry-run

# 3. Validate safety thresholds
cortex-vacuum /vacuum-validate

# 4. Preview full cleanup (what would happen)
cortex-vacuum /vacuum-full --dry-run
```

### Execution Phase
```bash
# Clean up session reports (>30 days old)
cortex-vacuum /vacuum-sessions --execute

# Clean up completion reports (>14 days old)
cortex-vacuum /vacuum-completion --execute

# Clean up working documents (>7 days old)
cortex-vacuum /vacuum-working-docs --execute

# Clean up analysis files (>3 days old)
cortex-vacuum /vacuum-analysis --execute

# Full cleanup (all categories)
cortex-vacuum /vacuum-full --execute
```

### Recovery Phase
```bash
# View operation history
cortex-vacuum /vacuum-report

# Rollback to specific date
cortex-vacuum /vacuum-rollback --date 2026-01-23

# Restore single file from archive
cortex-vacuum /vacuum-restore --file SESSION-SUMMARY-2026-01-20.md

# Git rollback (if needed)
git revert HEAD~1
git status
```

---

## 📋 Category Reference

| Category | Pattern | Age | Action | Archive To |
|----------|---------|-----|--------|------------|
| **Sessions** | `SESSION-*` | 30d | ARCHIVE | `_archive/sessions/` |
| **Completion** | `*-COMPLETION-*` | 14d | ARCHIVE | `_archive/completed/` |
| **Working Docs** | `*-DRY-RUN-*` | 7d | ARCHIVE | `_archive/working/` |
| **Analysis** | `*-INDEX.md` | 3d | ARCHIVE | `_archive/analysis/` |
| **Executive** | `EXECUTIVE-*` | 14d | ARCHIVE | `_archive/summaries/` |
| **Reports** | `*-REPORT.md` | 30d | ARCHIVE | `_archive/reports/` |
| **Comparisons** | `BEFORE-AFTER-*` | 7d | ARCHIVE | `_archive/analysis/` |

---

## ✅ Pre-Execution Checklist

Before running any cleanup:

- [ ] Git working directory is clean (`git status`)
- [ ] No uncommitted changes
- [ ] Backup exists for critical files
- [ ] Disk space available (at least 1 GB)
- [ ] Ran with `--dry-run` first
- [ ] Reviewed recommendations
- [ ] Safety validation passed

---

## 🎯 Common Scenarios

### Scenario: End of Week Cleanup
```bash
# Friday afternoon cleanup
cortex-vacuum /vacuum-sessions --dry-run
# Review output
cortex-vacuum /vacuum-sessions --execute
# Done!
```

### Scenario: After Analysis Run
```bash
# Clean up temporary analysis files
cortex-vacuum /vacuum-working-docs --dry-run
cortex-vacuum /vacuum-analysis --dry-run
# Approve both
cortex-vacuum /vacuum-working-docs --execute
cortex-vacuum /vacuum-analysis --execute
```

### Scenario: Full Maintenance
```bash
# Complete system audit
cortex-vacuum /vacuum-analyze
cortex-vacuum /vacuum-full --dry-run
# Review impact
cortex-vacuum /vacuum-full --execute
# Verify results
git log --oneline -5
cortex-vacuum /vacuum-report
```

### Scenario: Oops! I Made a Mistake
```bash
# See what happened
cortex-vacuum /vacuum-report

# Restore everything
cortex-vacuum /vacuum-rollback --date 2026-01-24

# Or restore single file
cortex-vacuum /vacuum-restore --file important-file.md

# Verify restoration
git status
```

---

## 🛡️ Safety Guardrails

These files are **NEVER** deleted:

```
✅ PROTECTED:
.github/prompts/*.prompt.md
.github/prompts/*-agents.md
cortex*.yaml
pyrightconfig.json
cortex_brain/tier0/**/*.yaml
docs/0-README.md
docs/INDEX.md
```

Operation will **ABORT** if:
- Would delete last file in category
- Git working directory has changes
- Insufficient disk space for archive
- Backup location doesn't exist
- Safety validation fails

---

## 📊 Expected Results

### After Session Report Cleanup
```
Files Processed: 12
Age Range: 30-120 days
Space Freed: 6.2 MB
Destination: _workspaces/_archive/sessions/
Reversible: YES (via /vacuum-rollback)
Git Commits: 2 (checkpoint + cleanup)
```

### After Full Cleanup
```
Categories Processed: 7
Total Files: 28
Total Space: 12.5 MB
Duration: 125 seconds
Categories Affected:
  - sessions: 12 archived
  - completion: 8 archived
  - working-docs: 5 archived
  - analysis: 3 archived
Reversible: YES (single rollback restores all)
```

---

## 🔄 Undo/Rollback Options

### Option 1: Rollback via Vacuum
```bash
cortex-vacuum /vacuum-rollback --date 2026-01-24
# Automatically:
# - Restores files from archive
# - Reverts git commits
# - Updates working directory
```

### Option 2: Git Revert
```bash
git log --oneline -5
# Shows: vacuum: cleanup operations (28 files)
#        vacuum: pre-cleanup checkpoint
git revert HEAD~1  # Undo cleanup
git revert HEAD~1  # Undo checkpoint
```

### Option 3: Manual Restore
```bash
# Find file in archive
ls -la _workspaces/_archive/sessions/ | grep "SESSION-"

# Restore single file
cp _workspaces/_archive/sessions/SESSION-2026-01-20.md \
   _workspaces/SESSION-2026-01-20.md

# Or entire category
cp -r _workspaces/_archive/sessions/* _workspaces/
```

---

## 📝 Log Files & Audit Trail

### Main Operation Log
```
Location: _workspaces/.vacuum-operations.log

Contains:
- Timestamp of operation
- Operation ID
- Files processed
- Space reclaimed
- Git commits created
- Rollback instructions
```

### View Recent Operations
```bash
tail -50 _workspaces/.vacuum-operations.log
```

### Check Rollback Manifest
```bash
# Lists all backups and how to restore
ls _workspaces/_archive/.rollback-manifests/

# View specific operation
cat _workspaces/_archive/.rollback-manifests/vacuum-20260124-001.json
```

---

## 🔧 Customization

### Add New Category to Manifest
Edit `cortex-vacuum-manifest.yaml`:

```yaml
ephemeral_patterns:
  my_custom_category:
    paths:
      - "_workspaces/MY-*.md"
      - "docs/*-MY-*.md"
    pattern_match:
      - "MY-"
    description: "My custom ephemeral files"
    policy: "ARCHIVE_AFTER_N_DAYS"
    max_age_days: 10  # Keep for 10 days
    archive_to: "_workspaces/_archive/my-category/"
    reason: "Custom operational files"
```

Then use:
```bash
cortex-vacuum /vacuum-my-custom-category --dry-run
cortex-vacuum /vacuum-my-custom-category --execute
```

### Change Age Threshold
Edit `cortex-vacuum-manifest.yaml`:

```yaml
# Before:
session_reports:
  max_age_days: 30

# After:
session_reports:
  max_age_days: 60  # Keep sessions for 60 days instead
```

Apply immediately next time you run cleanup.

---

## 🆘 Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| "Safety validation failed" | Check category minimums - may be last file |
| "Permission denied" | Run with appropriate permissions or `sudo` |
| "Git commit failed" | Commit/stash changes first with `git add .` |
| "Disk full" | Clean `_workspaces/_archive/.backup/` or expand space |
| "Can't restore file" | Check `_workspaces/_archive/` structure |
| "Operation too slow" | Normal - 1000+ files takes time. Don't interrupt |
| "Lost file - help!" | Immediately run `/vacuum-rollback --date {day-before}` |

---

## ⏱️ Timing Expectations

```
Operation breakdown for ~1000 files:

Analysis:        5-10 seconds (scan + classify)
Policy Matching: 5-10 seconds (age checks + recommendations)
Safety Check:    2-5 seconds (validation)
Execution:       30-60 seconds (archive/migrate/delete)
Audit Logging:   5-10 seconds (record + manifest)
Git Commits:     10-30 seconds (checkpoint + cleanup)
───────────────────────────────
TOTAL:           60-130 seconds (~2 minutes)
```

---

## 📱 Integration Examples

### With Git Hooks
```bash
# .git/hooks/post-commit
#!/bin/bash
# Auto-cleanup after commits
cortex-vacuum /vacuum-sessions --execute 2>/dev/null &
```

### With CI/CD
```yaml
# In GitHub Actions
- name: Vacuum cleanup
  run: |
    python .github/scripts/vacuum-cli.py /vacuum-sessions --execute
  if: github.event_name == 'schedule'  # Weekly
```

### With Cron (Weekly)
```bash
# Add to crontab -e
0 9 * * 1 cd /Users/asifhussain/PROJECTS/CORTEX && python .github/scripts/vacuum-cli.py /vacuum-sessions --execute >> /tmp/vacuum.log 2>&1
```

---

## 📞 Quick Reference

### Status Commands
```bash
cortex-vacuum /vacuum-analyze          # See current state
cortex-vacuum /vacuum-report           # View operation history
git log --oneline -10                  # See recent changes
```

### Safe Preview Commands
```bash
cortex-vacuum /vacuum-recommend --dry-run    # Show recommendations
cortex-vacuum /vacuum-full --dry-run         # Preview full cleanup
```

### Execute Commands
```bash
cortex-vacuum /vacuum-sessions --execute     # Clean sessions
cortex-vacuum /vacuum-full --execute         # Full cleanup
```

### Recovery Commands
```bash
cortex-vacuum /vacuum-rollback --date DATE   # Restore to date
git revert HEAD~1                            # Git rollback
```

---

## 🎓 Learning Path

**Day 1: Understanding**
- [ ] Read main prompt: `cortex-vacuum.prompt.md`
- [ ] Review manifest: `cortex-vacuum-manifest.yaml`
- [ ] Understand categories and age thresholds

**Day 2: Testing**
- [ ] Run `/vacuum-analyze` (safe, read-only)
- [ ] Run `/vacuum-full --dry-run` (safe, preview)
- [ ] Study recommendations and safety report

**Day 3: Execution**
- [ ] Clean up one category: `/vacuum-sessions --execute`
- [ ] Monitor operation
- [ ] Verify results and git commits

**Day 4+: Maintenance**
- [ ] Schedule weekly cleanups
- [ ] Monitor operation logs
- [ ] Adjust manifest as needed
- [ ] Document custom categories

---

## ✨ Key Takeaways

1. **Always use `--dry-run` first** - Preview before executing
2. **Cleanup is reversible** - Git integration enables easy rollback
3. **Operation is logged** - Complete audit trail for accountability
4. **Safety-first design** - Won't delete last file in category
5. **Extensible system** - Easy to add new cleanup policies
6. **CORTEX-compliant** - Follows governance rules and protocols

---

**Ready to Clean? Start with:** `cortex-vacuum /vacuum-analyze`

