# 🧹 CORTEX Untracked Files Analysis Report

**Generated:** 2026-01-07T04:05:27.084447

**Analyzer:** Organization Intelligence v1.0

---

## 📊 Statistics

- **Total Untracked:** 358
- **Total Deleted:** 48
- **Total Modified:** 1
- **Orphaned Files:** 2
- **Relocations Needed:** 3

## 📁 Files by Category

- **unknown:** 102 files
- **source_code:** 8 files
- **build_artifacts:** 1 files
- **temp_cache:** 7 files
- **documentation:** 108 files
- **config:** 118 files
- **backups:** 3 files
- **logs:** 2 files
- **data_files:** 5 files
- **scripts:** 4 files

## 🎯 Recommended Actions

- **REVIEW:** 102 files
- **PRESERVE:** 243 files
- **DELETE:** 10 files
- **RELOCATE:** 3 files

## 🗑️ Files to DELETE

**Total:** 10 files

- `.coveragerc`
- `.env.template`
- `cortex-brain/brain-protection-rules.yaml.backup-corrupted`
- `cortex-brain/cleanup-logs/`
- `cortex-brain/config/vision_api_config.template.yaml`
- `cortex-brain/documents/.backups/`
- `cortex-brain/documents/authorized-entry-points.json.bak.20251231_151032`
- `cortex-brain/documents/authorized-entry-points.json.bak.20251231_151915`
- `cortex-brain/sweeper-logs/`
- `cortex.config.template.json`

## 📦 Files to RELOCATE

**Total:** 3 files

- `backups/` → `cortex-brain/archives/backups/backups`
- `cortex-brain/documents/planning/backups/` → `cortex-brain/archives/backups/backups`
- `cortex-brain/documents/reports/css-backup-cleanup-summary-20260103.md` → `cortex-brain/archives/backups/css-backup-cleanup-summary-20260103.md`

## ✅ Files to PRESERVE

**Total:** 243 files


### .csv (1 files)
- `cortex-brain/documents/reports/test-gap-matrix-2025-12-23.csv`

### .html (2 files)
- `cortex-brain/documents/reports/four-tier-brain-preview.html`
- `cortex-brain/documents/reports/sample-dashboard.html`

### .json (49 files)
- `cortex-brain/.platform_state.json`
- `cortex-brain/CLEANUP-DRY-RUN-REPORT.json`
- `cortex-brain/config/e2e-criteria-config.json`
- `cortex-brain/config/orchestrator-registry.json`
- `cortex-brain/config/sanitization-whitelist.json`
- `cortex-brain/config/shared.config.json`
- `cortex-brain/config/visualstudio.config.json`
- `cortex-brain/config/vscode.config.json`
- `cortex-brain/documents/authorized-entry-points.json`
- `cortex-brain/documents/diagram-manifest.json`
  ... and 39 more

### .md (98 files)
- `.github/USER-COPILOT-INTEGRATION.md`
- `.github/light-bulbs.md/`
- `.github/prompts/cortex-git-commit.prompt.md`
- `.github/prompts/cortex-investigate.prompt.md`
- `.github/prompts/cortex-maintenance.prompt.md`
- `.github/prompts/cortex-plan-upgrade.prompt.md`
- `.github/prompts/cortex-refactor.prompt.md`
- `.github/prompts/cortex-upgrade.prompt.md`
- `.github/prompts/cortex-vacuum.prompt.md`
- `DEPLOYMENT.md`
  ... and 88 more

### .ps1 (3 files)
- `cortex-cleanup.ps1`
- `cortex-upgrade.ps1`
- `create-cortex-5.5-branch.ps1`

### .py (3 files)
- `cortex-brain/migrate_brain_db.py`
- `cortex-brain/tier2/migrate_brain_db.py`
- `cortex-upgrade-plan.py`

### .sh (1 files)
- `cortex-upgrade.sh`

### .sql (5 files)
- `cortex-brain/compliance-tracking-schema.sql`
- `cortex-brain/governance-schema.sql`
- `cortex-brain/schema.sql`
- `cortex-brain/tier2/compliance-tracking-schema.sql`
- `cortex-brain/tier2/schema.sql`

### .txt (9 files)
- `PUBLISH-GUIDE.txt`
- `cortex-brain/MILESTONE-0-BASELINE-COMPLETE.txt`
- `cortex-brain/documents/reports/c150-FINAL-STATUS.txt`
- `cortex-brain/documents/reports/c150-test-analysis-SUMMARY.txt`
- `cortex-brain/documents/reports/docs-cleanup-final-report-20260103-075200.txt`
- `cortex-brain/documents/reports/missing-files-list.txt`
- `cortex-brain/documents/reports/sqlite-optimization-report.txt`
- `cortex-brain/documents/reports/test-coverage-visual-summary.txt`
- `cortex-brain/documents/reports/wiring-check-output.txt`

### .yaml (69 files)
- `.pre-commit-config.yaml`
- `cortex-brain/TRUTH-SOURCES.yaml`
- `cortex-brain/cleanup-rules.yaml`
- `cortex-brain/config/acceptance-criteria.yaml`
- `cortex-brain/config/ado-v2-default.yaml`
- `cortex-brain/config/ado-yaml-schema.yaml`
- `cortex-brain/config/audit-logging-dev.yaml`
- `cortex-brain/config/audit-logging-prod.yaml`
- `cortex-brain/config/audit-logging-staging.yaml`
- `cortex-brain/config/clarification-rules.yaml`
  ... and 59 more

### no_ext (3 files)
- `.cortex-installed`
- `.cortexignore`
- `docs/`

## 🔍 Orphaned Files (No References)

**Total:** 2 files

- `cortex-brain/brain-protection-rules.yaml.backup-corrupted`
- `cortex-brain/documents/reports/css-backup-cleanup-summary-20260103.md`

---

## 🎯 Next Steps

1. Review DELETE recommendations (automated cleanup safe)
2. Verify RELOCATE suggestions (folder structure optimization)
3. Confirm PRESERVE files are in correct locations
4. Execute vacuum orchestrator with approved actions