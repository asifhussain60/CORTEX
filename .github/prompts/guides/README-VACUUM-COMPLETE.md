# CORTEX Vacuum System - Complete Guide
**Version:** 1.0 | **Updated:** 2026-01-24 | **Authority:** VacuumOrchestrator

---

## 🎯 Quick Start

The CORTEX Vacuum System intelligently cleans up your repository by:

1. **Analyzing** all files and classifying them into 4 tiers
2. **Recommending** actions (keep, archive, migrate, delete)
3. **Validating** safety before execution
4. **Executing** with full audit trail and git integration
5. **Logging** everything for reversibility

### First Run (Safe - Dry-Run Mode)

```bash
# 1. Analyze your repo
cortex-vacuum /vacuum-analyze

# 2. See recommendations (no changes made)
cortex-vacuum /vacuum-recommend --dry-run

# 3. Validate safety
cortex-vacuum /vacuum-validate

# 4. Preview full cleanup
cortex-vacuum /vacuum-full --dry-run
```

### When Ready to Execute

```bash
# Clean up session reports (30+ days old)
cortex-vacuum /vacuum-sessions --execute

# Clean up completion reports (14+ days old)
cortex-vacuum /vacuum-completion --execute

# Full cleanup (all categories)
cortex-vacuum /vacuum-full --execute
```

### If Something Goes Wrong

```bash
# See operation history
cortex-vacuum /vacuum-report

# Rollback to specific date
cortex-vacuum /vacuum-rollback --date 2026-01-23

# Restore single file
cortex-vacuum /vacuum-restore --file SESSION-SUMMARY-2026-01-20.md
```

---

## 📁 System Components

### 1. **cortex-vacuum-manifest.yaml** (Master Registry)

Defines what's safe to cleanup:

- ✅ **TIER 1** (IMMUTABLE): System files, prompts, governance
- ✅ **TIER 2** (CURATED): Documentation in docs/
- ✅ **TIER 3** (EPHEMERAL): Session reports, completion notices, working docs
- ✅ **TIER 4** (SPECIAL): Roadmap, presentations, sample apps

```yaml
# Example from manifest
ephemeral_patterns:
  session_reports:
    patterns: ['SESSION-*.md']
    max_age_days: 30
    archive_to: '_workspaces/_archive/sessions/'
```

### 2. **cortex-vacuum.prompt.md** (Intelligence)

Complete prompt for AI-assisted cleanup:

- CORTEX LENS protocol (Language→Examination→Navigation→Synthesis)
- DoR (Definition of Ready) approval gate
- 5-agent framework specification
- Policy definitions and examples
- Safety & rollback procedures

### 3. **cortex-vacuum-agents.md** (Agent Specifications)

Detailed agent implementations:

- **FileAnalyzer**: Scans repo and classifies files
- **PolicyMatcher**: Matches files to cleanup policies
- **SafetyValidator**: Checks safety thresholds
- **OperationExecutor**: Executes approved actions
- **AuditLogger**: Records and enables rollback

### 4. **vacuum-cli.py** (Optional Tool)

Python CLI for safe execution:

```bash
python .github/scripts/vacuum-cli.py /vacuum-analyze
python .github/scripts/vacuum-cli.py /vacuum-full --dry-run
python .github/scripts/vacuum-cli.py /vacuum-full --execute
```

---

## 🗑️ What Gets Cleaned Up?

### Category 1: Session Reports (>30 days)
```
_workspaces/SESSION-SUMMARY-2026-01-20.md    ← Archive
_workspaces/SESSION-FINAL-REPORT-2026-01-15.md  ← Archive
```

### Category 2: Completion Reports (>14 days)
```
docs/BRT-017-COMPLETION-REPORT.md            ← Archive
_workspaces/ENHANCEMENT-COMPLETE.md          ← Archive
```

### Category 3: Working Documents (>7 days)
```
_workspaces/DRY-RUN-VALIDATION-REPORT.md     ← Archive
_workspaces/CLEANUP-ACTION-PLAN.md           ← Archive
```

### Category 4: Analysis Files (>3 days)
```
_workspaces/CORTEX-OBSOLETE-FILES-INDEX.md   ← Archive
_workspaces/CORTEX-VACUUM-REGISTRY.md        ← Archive
```

### ❌ NEVER Deleted

```
.github/prompts/*.prompt.md              # System prompts
.github/prompts/*-agents.md              # Agent definitions
cortex*.yaml                             # Configuration
cortex_brain/tier0/**/*.yaml             # Governance
docs/0-README.md                         # Doc entry points
pyrightconfig.json                       # Type checking
```

---

## 🛡️ Safety Features

### Automatic Safeguards

1. **No deletion without backup**
   - All files moved to archive first
   - Backups kept in `_workspaces/_archive/.backup/` for 30 days

2. **Category minimum threshold**
   - Won't reduce any category below 1 file
   - Prevents accidental deletion of entire categories

3. **Git integration**
   - Checkpoint created before operations
   - All changes committed for easy rollback
   - Full git history preserved

4. **Explicit user approval**
   - Preview with `--dry-run` before executing
   - `--execute` flag required for actual changes
   - Confirmation prompts for large operations

5. **Complete audit trail**
   - Every operation logged to `_workspaces/.vacuum-operations.log`
   - Rollback manifests created for recovery
   - 90-day retention of audit logs

### Dry-Run Mode (Default)

Always preview first:

```bash
cortex-vacuum /vacuum-full --dry-run

# Output shows what WOULD happen, no changes made
[DRY-RUN] Would archive: _workspaces/SESSION-SUMMARY-2026-01-20.md
[DRY-RUN] Would archive: _workspaces/SESSION-FINAL-REPORT-2026-01-15.md
...
Total: 28 files would be archived
```

---

## 📊 Vacuum Operations Breakdown

### Operation: Session Cleanup
```
cortex-vacuum /vacuum-sessions --execute

Result:
├─ 12 files archived (>30 days old)
├─ 0 files deleted
├─ 6.2 MB space reclaimed
└─ ✅ Reversible via rollback
```

### Operation: Full Cleanup
```
cortex-vacuum /vacuum-full --execute

Result:
├─ Category Breakdown:
│  ├─ Session Reports: 12 archived
│  ├─ Completion Reports: 8 archived
│  ├─ Working Docs: 5 archived
│  └─ Analysis Files: 3 archived
├─ Total: 28 files archived
├─ Space Reclaimed: 12.5 MB
├─ Time: 125 seconds
└─ Git commits: 2
```

---

## 🔄 Rollback Procedures

### See What Changed
```bash
git log --oneline -5
# vacuum: cleanup operations (28 files)
# vacuum: pre-cleanup checkpoint
```

### Restore Everything
```bash
cortex-vacuum /vacuum-rollback --date 2026-01-24
```

### Restore Single File
```bash
cortex-vacuum /vacuum-restore --file SESSION-SUMMARY-2026-01-20.md
```

### Git Revert (Nuclear Option)
```bash
git revert HEAD~1  # Undo last commit
git status
```

---

## 📈 Metrics & Reporting

### View Operation History
```bash
cortex-vacuum /vacuum-report

# Shows all vacuum operations with:
# - Date/time
# - Files processed
# - Space freed
# - Rollback options
```

### Log File Location
```
_workspaces/.vacuum-operations.log
```

Each entry includes:
- Operation ID
- Timestamp
- Files processed
- Space reclaimed
- Git commits
- Rollback instructions

---

## 🎯 Common Use Cases

### Use Case 1: Weekly Cleanup
```bash
# Run every Monday morning
cortex-vacuum /vacuum-sessions --execute
cortex-vacuum /vacuum-completion --execute
```

### Use Case 2: After Large Analysis
```bash
# Clean up working documents
cortex-vacuum /vacuum-working-docs --execute
cortex-vacuum /vacuum-analysis --execute
```

### Use Case 3: Repository Maintenance
```bash
# Full cleanup with safety checks
cortex-vacuum /vacuum-analyze
cortex-vacuum /vacuum-recommend --dry-run
cortex-vacuum /vacuum-validate
cortex-vacuum /vacuum-full --dry-run
cortex-vacuum /vacuum-full --execute  # After approval
```

### Use Case 4: Documentation Migration
```bash
# Move roadmap to docs/
cortex-vacuum /vacuum-migrate --target roadmap --dry-run
cortex-vacuum /vacuum-migrate --target roadmap --execute
```

---

## 🚀 Integration with CORTEX System

### With cortex-doc.prompt.md
- Vacuum removes obsolete documentation
- Documentation generator creates new guides
- Manifest tracks "current" vs "historical" versions

### With cortex-review.prompt.md
- Review agents can flag files for cleanup
- Review reports get archived automatically

### With CORTEX.prompt.md
- All operations follow CORTEX LENS → DoR → Approval
- All operations logged to audit trail (AC_START/COMPLETE)
- All operations respect CORE governance rules (CORE-030 through CORE-035)

---

## 🔧 Configuration

Edit `cortex-vacuum-manifest.yaml` to:

1. **Add new ephemeral categories**
```yaml
ephemeral_patterns:
  my_category:
    patterns: ['MY-*.md']
    max_age_days: 7
    archive_to: '_workspaces/_archive/my-category/'
```

2. **Change age thresholds**
```yaml
session_reports:
  max_age_days: 60  # Changed from 30
```

3. **Adjust safety rules**
```yaml
safety_rules:
  minimum_docs_per_category: 2  # Changed from 1
```

---

## ⚠️ Important Notes

### Before First Run
- [ ] Review `cortex-vacuum-manifest.yaml` - customize if needed
- [ ] Ensure `_workspaces/_archive/` exists
- [ ] Run in dry-run mode first
- [ ] Verify git working directory is clean

### During Operation
- [ ] Don't interrupt vacuum process
- [ ] Monitor disk space
- [ ] Check logs for errors
- [ ] Have rollback command ready

### After Operation
- [ ] Review git commits
- [ ] Verify archived files
- [ ] Check space reclaimed
- [ ] Update any broken links

---

## 🆘 Troubleshooting

### Problem: "Safety validation failed"
**Solution:** Check `cortex-vacuum-manifest.yaml` - you may be trying to delete the last file in a category

### Problem: "Permission denied"
**Solution:** Check file permissions - may need to `chmod` certain files before cleanup

### Problem: "Git commit failed"
**Solution:** Ensure `_workspaces/` is in `.gitignore` or commit changes first

### Problem: "Disk full during archival"
**Solution:** Clean up old backups in `_workspaces/_archive/.backup/` or increase disk space

### Problem: "I deleted something I shouldn't have!"
**Solution:** Run `cortex-vacuum /vacuum-rollback --date {before-date}` immediately

---

## 📚 Related Documentation

- [`cortex-vacuum.prompt.md`](.github/prompts/cortex-vacuum.prompt.md) - AI-assisted prompt
- [`cortex-vacuum-agents.md`](.github/prompts/cortex-vacuum-agents.md) - Agent specifications
- [`cortex-vacuum-manifest.yaml`](.github/prompts/cortex-vacuum-manifest.yaml) - Master registry
- [`CORTEX.prompt.md`](.github/prompts/CORTEX.prompt.md) - Main CORTEX system
- [`cortex-doc.prompt.md`](.github/prompts/cortex-doc.prompt.md) - Documentation system

---

## 🎓 Learning Resources

### Video: Understanding Vacuum System
TBD

### Video: First Cleanup Run
TBD

### Video: Rollback Recovery
TBD

### Blog: Best Practices
TBD

---

## 📞 Support

### Questions?
- Check troubleshooting section above
- Review audit logs in `_workspaces/.vacuum-operations.log`
- Test with `--dry-run` mode first

### Report Issues
- File issue with detailed logs
- Include operation ID from report
- Attach relevant manifest snippets

### Feature Requests
- Suggest new categories to manifest
- Request new age thresholds
- Propose safety rule improvements

---

## 📝 Changelog

### Version 1.0 (2026-01-24)
- ✅ Initial release
- ✅ 4-tier classification system
- ✅ 5-agent framework
- ✅ Full audit trail
- ✅ Rollback capability
- ✅ 7 ephemeral categories

### Version 2.0 (Planned)
- 🔄 ML-based content classification
- 🔄 Predictive retention periods
- 🔄 Automated weekly scheduling
- 🔄 Slack notifications
- 🔄 Cross-reference aware deletion

---

**Last Updated:** 2026-01-24  
**Maintained by:** CORTEX VacuumOrchestrator  
**Authority:** CORTEX Master Orchestrator v4.0

