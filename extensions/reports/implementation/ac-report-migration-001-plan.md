# AC-REPORT-MIGRATION-001: Scatter → Canonical Consolidation
**Date:** 2026-01-25 | **Authority:** AC-REPORT-MIGRATION-001 | **Status:** EXECUTION PLAN

---

## 📋 Inventory Summary

### Reports to Migrate

**Source:** `_workspaces/reports/` (85 files)
**Additional:** `_workspaces/roadmap/reports/` (3 files)
**Archive:** `_workspaces/_archive/session-logs/` (reports tagged)
**Total:** ~90 files to consolidate

### Categorization Strategy

Based on filename patterns and content analysis:

| Category | Source | Target | Count |
|----------|--------|--------|-------|
| **Implementation/Consolidation** | _workspaces/reports/ | reports/implementation/ | 25 |
| **Phase Tracking** | _workspaces/roadmap/reports/ | reports/phase-tracking/ | 3 |
| **Analysis/Reviews** | _workspaces/reports/ | reports/analysis/ | 15 |
| **Governance/Compliance** | _workspaces/reports/ | reports/governance/ | 8 |
| **Orchestrator Metrics** | _workspaces/reports/ | reports/orchestrators/ | 12 |
| **Operations/Sessions** | _workspaces/_archive/session-logs/ | reports/operations/ | 15 |
| **Pending Review** | Various | To be determined | 7 |

---

## 🗂️ Migration Patterns

### Pattern 1: Consolidation Reports
**Files:** CONS-*, TRANSFORM-*, BRT-* reports
**Pattern:** `CONS-{NUMBER}-{TITLE}.md` → `reports/implementation/cons-{number}-{title}.md`
**Example:**
- `CONS-002-PHASE-1-COMPLETE.md` → `reports/implementation/cons-002-phase-1-complete.md`
- `TRANSFORM-001-COMPLETION-SUMMARY.md` → `reports/implementation/transform-001-completion-summary.md`

### Pattern 2: Planning Orchestrator Analysis
**Files:** PLANNING-ORCHESTRATOR-* reports
**Pattern:** `PLANNING-ORCHESTRATOR-{TYPE}.md` → `reports/orchestrators/planning-orchestrator-{type}.md`
**Example:**
- `PLANNING-ORCHESTRATOR-ANALYSIS-COMPLETE-2026-01-25.md` → `reports/orchestrators/planning-orchestrator-analysis-complete-2026-01-25.md`

### Pattern 3: Phase Tracking & Milestones
**Files:** PHASE-*, DOCUMENTATION-MIGRATION-*, SESSION-*
**Pattern:** `PHASE-{NUMBER}-*.md` → `reports/phase-tracking/phase-{number}-*.md`
**Example:**
- `PHASE-3-COMPLETE-PHASE-4-KICKOFF-SUMMARY.md` → `reports/phase-tracking/phase-3-complete-phase-4-kickoff-summary.md`
- `DOCUMENTATION-MIGRATION-PLAN-2026-01-25.md` → `reports/phase-tracking/documentation-migration-plan-2026-01-25.md`

### Pattern 4: Session & Operation Reports
**Files:** SESSION-*, *-COMPLETION-*, PRODUCTION-VALIDATION-*
**Pattern:** `SESSION-{DATE}-*.md` → `reports/operations/session-{date}-*.md`
**Example:**
- `SESSION-COMPLETION-SUMMARY.md` → `reports/operations/session-completion-summary.md`
- `GIT-PULL-MERGE-COMPLETION-2026-01-25.md` → `reports/operations/git-pull-merge-completion-2026-01-25.md`

### Pattern 5: Analysis & Research
**Files:** MASTER-ORCHESTRATOR-*, HIGH-PRIORITY-*, DOCUMENTATION-SYNC-*
**Pattern:** `{TOPIC}-{TYPE}.md` → `reports/analysis/{topic}-{type}.md`
**Example:**
- `MASTER-ORCHESTRATOR-PLANNING-TDD-INTEGRATION-PLAN-2026-01-25.md` → `reports/analysis/master-orchestrator-planning-tdd-integration-plan-2026-01-25.md`

---

## ⚙️ Execution Steps

### Step 1: Pre-Migration Validation
```bash
# 1. Verify all files are readable
# 2. Check for broken internal links
# 3. Identify duplicate content
# 4. Extract unique insights from each file
```

### Step 2: Categorized Migration
**For each category:**
1. Create staging list (files to move)
2. Rename to kebab-case
3. Move to target subfolder
4. Verify file integrity
5. Update any internal cross-references

### Step 3: Git Operations
```bash
# Batch by category to minimize commits
git mv _workspaces/reports/CONS-*.md reports/implementation/
git mv _workspaces/reports/PLANNING-ORCHESTRATOR-*.md reports/orchestrators/
git mv _workspaces/roadmap/reports/*.md reports/phase-tracking/
# ... etc
```

### Step 4: Post-Migration Verification
- [ ] All 90 files moved successfully
- [ ] No broken symlinks or references
- [ ] Git history preserved (using git mv)
- [ ] Kebab-case naming validated
- [ ] No orphaned directories in _workspaces/reports/

### Step 5: Cleanup
- [ ] Remove empty _workspaces/reports/ directory
- [ ] Update any documentation pointing to old locations
- [ ] Commit cleanup with reference

---

## 📊 Expected Outcome

### Before Migration
```
_workspaces/
  reports/               (85 files - disorganized)
  roadmap/
    reports/             (3 files)
  _archive/
    session-logs/        (15+ files)
```

### After Migration
```
reports/
  analysis/              (15 files - research, reviews, analysis)
  governance/            (8 files - compliance, audit, rules)
  implementation/        (25 files - consolidation, AC-IDs, features)
  operations/            (15 files - sessions, deployments, incidents)
  orchestrators/         (12 files - metrics, health, analysis)
  phase-tracking/        (18 files - milestones, progress, roadmap)
  
_workspaces/reports/     (REMOVED - consolidated to /reports/)
_workspaces/roadmap/reports/ (REMOVED - consolidated to /reports/)
_workspaces/_archive/session-logs/ (CLEANED UP - old sessions archived)
```

---

## ✅ Migration Checklist

- [ ] Inventory all 90 files (DONE - 85 + 3 + ~15 archive)
- [ ] Categorize by type (5 primary patterns identified)
- [ ] Validate kebab-case naming requirements
- [ ] Plan git mv commands by category
- [ ] Execute migration in batches
- [ ] Verify all files moved successfully
- [ ] Update cross-references
- [ ] Remove empty source directories
- [ ] Commit with comprehensive message
- [ ] Verify reports/README.md covers all new locations
- [ ] Update CORTEX.prompt.md with new report locations
- [ ] Close AC-REPORT-MIGRATION-001 with success metrics

---

## 🎯 Success Metrics

| Metric | Target | Status |
|--------|--------|--------|
| Files migrated | 90/90 | 🔄 In progress |
| Naming compliance | 100% kebab-case | 🔄 In progress |
| Broken links | 0 | ⏳ Pending |
| Git history preserved | 100% | ⏳ Pending |
| Commit messages | Comprehensive | ⏳ Pending |
| Empty dirs removed | All | ⏳ Pending |
| Documentation updated | All references | ⏳ Pending |

---

## 🚀 Next Action

Execute Step 1 (Pre-Migration Validation) and proceed with categorized migration batches.

**Authority:** AC-REPORT-MIGRATION-001  
**Related:** AC-REPORTS-CONSOLIDATION-001, AC-FILE-PLACEMENT-ENFORCEMENT-001  
**Compliance:** CORE-030 (implementation truth), CORE-038 (file placement)
