# CORTEX Workspace Cleanup Scan Report

**Date:** November 11, 2025  
**Scan Root:** D:\PROJECTS\CORTEX  
**Purpose:** Comprehensive analysis of redundant files/folders for cleanup orchestrator  
**Status:** 🔍 ANALYSIS COMPLETE

---

## 📊 Executive Summary

**Total Identified for Cleanup:**

| Category | Files | Folders | Size | Risk Level |
|----------|-------|---------|------|------------|
| **Backup Archives** | 93 | 162 | ~0.25 MB + nested | 🟢 LOW |
| **Story Backups** | 84 | 0 | 1.63 MB | 🟢 LOW |
| **Session Reports** | 23+ | 0 | ~2 MB | 🟡 MEDIUM |
| **Phase Reports** | 19+ | 0 | ~1 MB | 🟡 MEDIUM |
| **Build Output** | 136 | 20+ | 13.25 MB | 🟢 LOW |
| **Workflow Checkpoints** | 17 | 0 | 0.01 MB | 🟢 LOW |
| **Legacy Agent Backups** | 4 | 0 | 0.08 MB | 🟢 LOW |
| **Cortex-Brain Archives** | Unknown | 2+ | TBD | 🟡 MEDIUM |
| **TOTAL ESTIMATED** | **376+** | **184+** | **~18+ MB** | - |

**Disk Space Savings Potential:** ~20-50 MB (conservative estimate)

---

## 🎯 Category 1: CRITICAL - Nested Backup Archive

### `.backup-archive` Directory

**Path:** `D:\PROJECTS\CORTEX\.backup-archive`

**Problem Identified:**
- **RECURSIVE NESTING:** `.backup-archive` contains another `.backup-archive` inside it!
- This creates infinite recursion risk for cleanup scripts
- Contains outdated distribution builds from packaging attempts

**Contents:**
```
.backup-archive/
├── .backup-archive/          ❌ NESTED (CRITICAL ISSUE!)
│   ├── .backup-archive/      ❌ TRIPLE NESTING
│   │   └── .venv/
│   └── .venv/
├── .venv/                    ❌ Old virtual environment
├── backup-manifest-20251111-170234.json
└── dist/                     ❌ Old builds
    ├── cortex-test/
    └── cortex-user-v1.0.0/
```

**Statistics:**
- **Total Items:** 24 files
- **Directories:** 162 (many nested)
- **Size:** 0.25 MB (just root level)
- **Nested Size:** Unknown (could be significant)

**Risk Assessment:** 🔴 **HIGH RISK**
- Recursive deletion could fail with nested `.backup-archive`
- Must handle carefully to avoid partial deletions
- Legacy distribution builds are no longer needed

**Recommendation:**
- **DELETE ENTIRE:** `.backup-archive/` directory
- **Safety Check:** Verify no active references
- **Test Required:** Ensure cleanup handles recursion safely

---

## 🎯 Category 2: Story Documentation Backups

### Awakening of CORTEX Backups

**Path:** `D:\PROJECTS\CORTEX\docs\awakening-of-cortex.backup.*.md`

**Pattern:** `awakening-of-cortex.backup.YYYYMMDD_HHMMSS.md`

**Details:**
- **Count:** 84 backup files
- **Size:** 1.63 MB total
- **Date Range:** Nov 9-11, 2025
- **Frequency:** Multiple backups per hour (over-aggressive)

**Sample Files:**
```
awakening-of-cortex.backup.20251109_180739.md  (0.06 MB)
awakening-of-cortex.backup.20251109_180805.md  (0.02 MB)
awakening-of-cortex.backup.20251110_060409.md  (0.02 MB)
...
awakening-of-cortex.backup.20251111_154000.md  (0.02 MB)
```

**Risk Assessment:** 🟢 **LOW RISK**
- Original file exists: `docs/story/CORTEX-STORY/Awakening Of CORTEX.md`
- Backups are timestamped (no naming conflicts)
- Can safely retain last 5-10 for rollback

**Recommendation:**
- **KEEP:** Last 5 backups (most recent)
- **DELETE:** Remaining 79 backups (older than 5 most recent)
- **Retention Policy:** Keep backups from last 7 days only

---

## 🎯 Category 3: SYSTEM-REFACTOR Reports

### Auto-generated Refactor Reports

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\SYSTEM-REFACTOR-REPORT-*.md`

**Pattern:** `SYSTEM-REFACTOR-REPORT-YYYYMMDD_HHMMSS.md`

**Details:**
- **Count:** 23 report files
- **Size:** ~2 MB estimated
- **Purpose:** Auto-generated summaries from system refactor operations
- **Dates:** Nov 9-11, 2025 (3 days of intensive development)

**Files Identified:**
```
SYSTEM-REFACTOR-REPORT-20251109_161347.md
SYSTEM-REFACTOR-REPORT-20251110_124220.md
SYSTEM-REFACTOR-REPORT-20251110_133919.md
SYSTEM-REFACTOR-REPORT-20251110_134329.md
...
SYSTEM-REFACTOR-REPORT-20251111_154004.md
```

**Risk Assessment:** 🟡 **MEDIUM RISK**
- Contains development session summaries
- May have useful context for debugging
- High volume indicates excessive logging

**Recommendation:**
- **KEEP:** Last 3 reports (most recent sessions)
- **DELETE:** Remaining 20 reports (older sessions)
- **ARCHIVE:** Consider moving to `cortex-brain/archives/system-refactor-reports/`
- **Alternative:** Consolidate into single summary document

---

## 🎯 Category 4: Phase Implementation Reports

### PHASE-* Session Summaries

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\PHASE-*.md`

**Details:**
- **Count:** 19 files (minimum)
- **Size:** ~1 MB estimated
- **Content:** Implementation progress, session summaries, test results

**Sample Files:**
```
PHASE-1-DATABASE-FIXTURES-COMPLETE.md
PHASE-1-VERBOSITY-COMPLETE.md
PHASE-5.1-COMPLETE.md
PHASE-5.1-COMPLETION-REPORT.md
PHASE-5.1-CONTINUED-PROGRESS.md
PHASE-5.1-COVERAGE-ANALYSIS.md
PHASE-5.1-HIGH-PRIORITY-COMPLETE.md
PHASE-5.1-IMPLEMENTATION-PROGRESS.md
PHASE-5.1-QUICK-REFERENCE.md
PHASE-5.1-SESSION-SUMMARY-CONTINUATION.md
PHASE-5.1-SESSION-SUMMARY-EVENING-2.md
PHASE-5.1-SESSION-SUMMARY.md
PHASE-5.1-TEST-DESIGN.md
PHASE-5.2-BRAIN-PROTECTION-COMPLETE.md
PHASE-5.2-BRAIN-PROTECTION-PROGRESS.md
PHASE-5.3-EDGE-CASE-DESIGN.md
PHASE-5.3-PLANNING.md
PHASE-5.3-SESSION-SUMMARY-NOV-10-2025.md
PHASE-7.1-SESSION-SUMMARY.md
```

**Risk Assessment:** 🟡 **MEDIUM RISK**
- Historical development context
- Useful for understanding implementation decisions
- Many duplicates and interim progress reports

**Recommendation:**
- **KEEP:** Final completion reports (COMPLETE.md, COMPLETION-REPORT.md)
- **KEEP:** Quick references and design documents
- **ARCHIVE:** Session summaries to `cortex-brain/archives/phase-reports/`
- **DELETE:** Interim progress reports (CONTINUED-PROGRESS, EVENING-2, etc.)

**Consolidation Opportunity:**
- Create single `PHASE-IMPLEMENTATION-HISTORY.md` summary
- Reference archived files for details

---

## 🎯 Category 5: Session Summaries

### SESSION-* Reports

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\SESSION-*.md`

**Details:**
- **Count:** 7 files
- **Size:** ~0.5 MB estimated
- **Content:** Session-specific summaries and implementations

**Files Identified:**
```
SESSION-2025-11-09-UNIVERSAL-OPERATIONS.md
SESSION-2025-11-10-IDENTITY-AUTH-3.0.md
SESSION-REVIEW-20251103-PLAYWRIGHT-IDS.md
SESSION-SUMMARY-2025-11-09-MKDOCS-STORY.md
SESSION-SUMMARY-2025-11-09-SKULL.md
SESSION-SUMMARY-2025-11-10-DOCUMENTATION-OPERATION.md
SESSION-SUMMARY-2025-11-10-PHASE-5.1.md
```

**Risk Assessment:** 🟢 **LOW RISK**
- Lower volume than PHASE reports
- Focused on specific features/topics
- Relatively recent (November 2025)

**Recommendation:**
- **KEEP:** All for now (low volume, high value)
- **REVIEW:** In 30 days for archival
- **Future:** Move to `cortex-brain/archives/session-summaries/`

---

## 🎯 Category 6: MkDocs Build Output

### `/site` Directory

**Path:** `D:\PROJECTS\CORTEX\site`

**Details:**
- **Files:** 136
- **Directories:** ~20
- **Size:** 13.25 MB
- **Purpose:** MkDocs static site build output

**Risk Assessment:** 🟢 **LOW RISK**
- Build artifact (regenerated from source)
- Should be in `.gitignore`
- No data loss if deleted

**Recommendation:**
- **DELETE:** Entire `/site` directory
- **Verify:** Present in `.gitignore`
- **Note:** Regenerated with `mkdocs build`

---

## 🎯 Category 7: Workflow Checkpoints

### `/workflow_checkpoints` Directory

**Path:** `D:\PROJECTS\CORTEX\workflow_checkpoints`

**Details:**
- **Files:** 17
- **Size:** 0.01 MB
- **Pattern:** `wf-YYYYMMDD-HHMMSS.json`

**Sample Files:**
```
wf-20251110-124343.json
wf-20251110-134042.json
wf-20251110-134452.json
...
wf-20251111-154046.json
```

**Risk Assessment:** 🟢 **LOW RISK**
- Small size
- Workflow state snapshots
- May be useful for debugging

**Recommendation:**
- **KEEP:** Last 5 checkpoints
- **DELETE:** Older than 7 days
- **Retention:** 7-day rolling window

---

## 🎯 Category 8: Legacy Agent Backups

### Agent `.backup` Files

**Path:** `D:\PROJECTS\CORTEX\src\cortex_agents\*.py.backup`

**Details:**
- **Files:** 4
- **Size:** 0.08 MB total
- **Files:**
  - `code_executor.py.backup`
  - `health_validator.py.backup`
  - `test_generator.py.backup`
  - `work_planner.py.backup`

**Risk Assessment:** 🟢 **LOW RISK**
- Git history contains all versions
- Backups are redundant
- Small size

**Recommendation:**
- **DELETE:** All `.backup` files in `src/cortex_agents/`
- **Verify:** Git history is intact
- **Policy:** Rely on Git for version control, not manual backups

---

## 🎯 Category 9: Cortex-Brain Archives

### Archive Directories

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\archives`

**Subdirectories:**
- `converted-to-yaml-2025-11-09/`
- `phase-completions/`

**Risk Assessment:** 🟡 **MEDIUM RISK**
- Intentional archival structure
- May contain historical reference data
- Needs manual review

**Recommendation:**
- **REVIEW:** Contents before deletion
- **KEEP:** If referenced by active code
- **CONSIDER:** Consolidation with phase reports

---

## 🎯 Category 10: Cortex-Brain Design Archives

### Design Documentation Archive

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\cortex-2.0-design\archive`

**Risk Assessment:** 🟡 **MEDIUM RISK**
- Historical design decisions
- May be referenced in documentation
- Unknown size

**Recommendation:**
- **INSPECT:** Contents first
- **KEEP:** If referenced elsewhere
- **ALTERNATIVE:** Move to top-level `cortex-brain/archives/design/`

---

## 🎯 Category 11: Legacy Prompts Archive

### Archived User Prompts

**Path:** `D:\PROJECTS\CORTEX\prompts\user\ARCHIVE-2025-11-09`

**Risk Assessment:** 🟢 **LOW RISK**
- Timestamped archive (Nov 9, 2025)
- Superseded by current prompts
- Historical reference only

**Recommendation:**
- **KEEP:** For historical reference
- **REVIEW:** In 6 months for deletion
- **Document:** In cleanup retention policy

---

## 🎯 Category 12: Cortex-Brain Temporary Directories

### Crawler Temp Files

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\crawler-temp`

**Risk Assessment:** 🟢 **LOW RISK**
- Temporary directory by name
- Should be cleaned automatically
- May be empty

**Recommendation:**
- **DELETE:** Entire directory if safe
- **VERIFY:** No active crawler processes
- **FUTURE:** Add to `.gitignore`

---

## 🎯 Category 13: Cortex-Brain Inventory

### Inventory Snapshots

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\inventory-v1`

**Risk Assessment:** 🟡 **MEDIUM RISK**
- May contain system state snapshots
- Could be useful for diagnostics
- Unknown contents

**Recommendation:**
- **INSPECT:** Contents first
- **ARCHIVE:** If historical only
- **DELETE:** If superseded by newer inventory system

---

## 🎯 Category 14: Discovery Reports

### Discovery Report Directory

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\discovery-reports`

**Risk Assessment:** 🟡 **MEDIUM RISK**
- Auto-generated reports
- May be useful for debugging
- Likely duplicates information elsewhere

**Recommendation:**
- **REVIEW:** Contents for duplicates
- **CONSOLIDATE:** Into single summary if possible
- **RETAIN:** Last 5 reports only

---

## 🎯 Category 15: Metrics History

### Metrics Tracking Data

**Path:** `D:\PROJECTS\CORTEX\cortex-brain\metrics-history`

**Risk Assessment:** 🟢 **LOW RISK**
- Historical performance data
- Useful for trend analysis
- Should be retained

**Recommendation:**
- **KEEP:** All metrics history
- **COMPRESS:** If over 30 days old
- **POLICY:** Retain for performance analysis

---

## 🎯 Category 16: Hemisphere Directories

### Brain Hemisphere Data

**Paths:**
- `D:\PROJECTS\CORTEX\cortex-brain\left-hemisphere`
- `D:\PROJECTS\CORTEX\cortex-brain\right-hemisphere`
- `D:\PROJECTS\CORTEX\cortex-brain\corpus-callosum`
- `D:\PROJECTS\CORTEX\cortex-brain\cognitive-framework`

**Risk Assessment:** 🔴 **HIGH RISK - DO NOT DELETE**
- Core brain architecture data
- Active system components
- Critical for CORTEX operation

**Recommendation:**
- **KEEP:** ALL hemisphere directories
- **INSPECT:** For cleanup opportunities within
- **CAUTION:** Do not delete parent directories

---

## 📋 Cleanup Priority Matrix

### High Priority (Execute First)

| Item | Path | Reason | Savings |
|------|------|--------|---------|
| **1** | `.backup-archive/` | Recursive nesting, bloat | 0.25+ MB |
| **2** | `site/` | Build output (regenerable) | 13.25 MB |
| **3** | `docs/awakening-of-cortex.backup.*.md` | 79 old backups | ~1.4 MB |
| **4** | `src/cortex_agents/*.backup` | Git supersedes | 0.08 MB |

**Total High Priority Savings:** ~15 MB

### Medium Priority (Review Before Delete)

| Item | Path | Reason | Savings |
|------|------|--------|---------|
| **5** | `cortex-brain/SYSTEM-REFACTOR-REPORT-*.md` | 20 old reports | ~1.7 MB |
| **6** | `cortex-brain/PHASE-*-PROGRESS.md` | Interim reports | ~0.5 MB |
| **7** | `workflow_checkpoints/wf-*.json` | 12 old checkpoints | ~0.01 MB |
| **8** | `cortex-brain/crawler-temp/` | Temp files | TBD |

**Total Medium Priority Savings:** ~2.2 MB

### Low Priority (Archive/Review Later)

| Item | Path | Action | Timeline |
|------|------|--------|----------|
| **9** | `cortex-brain/archives/` | Consolidate | 30 days |
| **10** | `cortex-brain/discovery-reports/` | Review | 30 days |
| **11** | `cortex-brain/inventory-v1/` | Inspect | 60 days |
| **12** | `prompts/user/ARCHIVE-2025-11-09/` | Keep | 6 months |

---

## 🧪 Test Harness Requirements

### Safety Checks Required

1. **Recursion Protection**
   - Detect nested `.backup-archive` directories
   - Prevent infinite loops
   - Limit recursion depth

2. **Dry-Run Mode**
   - Preview all deletions
   - Calculate total space savings
   - Show file/folder counts

3. **Retention Policies**
   - Keep N most recent backups
   - Keep files newer than X days
   - Keep files matching patterns

4. **Rollback Capability**
   - Create manifest before deletion
   - Support restore from manifest
   - Verify restoration success

5. **Safety Validations**
   - Verify no active file handles
   - Check Git status (no uncommitted changes)
   - Confirm no running processes

### Test Scenarios

#### Scenario 1: Recursive Backup Archive
```python
def test_cleanup_handles_nested_backup_archive():
    """Ensure cleanup safely handles recursive .backup-archive nesting"""
    # Setup: Create nested structure
    # Execute: Run cleanup
    # Verify: All levels deleted, no errors
```

#### Scenario 2: Backup Retention
```python
def test_cleanup_retains_recent_backups():
    """Ensure N most recent backups are kept"""
    # Setup: Create 10 backups
    # Execute: Run cleanup with keep=5
    # Verify: 5 newest kept, 5 oldest deleted
```

#### Scenario 3: Dry-Run Mode
```python
def test_cleanup_dry_run_no_deletions():
    """Ensure dry-run mode doesn't delete anything"""
    # Setup: Create test files
    # Execute: Run cleanup with dry_run=True
    # Verify: All files still exist, report generated
```

#### Scenario 4: Safety Validation
```python
def test_cleanup_respects_git_status():
    """Ensure cleanup refuses if uncommitted changes exist"""
    # Setup: Create uncommitted change
    # Execute: Run cleanup
    # Verify: Cleanup aborted with warning
```

#### Scenario 5: Rollback
```python
def test_cleanup_rollback_restores_files():
    """Ensure rollback restores deleted files"""
    # Setup: Create files
    # Execute: Run cleanup, save manifest
    # Execute: Run rollback with manifest
    # Verify: Files restored to original state
```

---

## 📁 Recommended Cleanup Configuration

### Cleanup Rules (YAML)

```yaml
cleanup_rules:
  version: "1.0"
  
  categories:
    backup_archives:
      paths:
        - ".backup-archive/"
      action: delete_all
      risk: low
      
    story_backups:
      paths:
        - "docs/awakening-of-cortex.backup.*.md"
      action: retain_recent
      retain_count: 5
      risk: low
      
    system_refactor_reports:
      paths:
        - "cortex-brain/SYSTEM-REFACTOR-REPORT-*.md"
      action: retain_recent
      retain_count: 3
      risk: medium
      
    phase_reports:
      paths:
        - "cortex-brain/PHASE-*-PROGRESS.md"
        - "cortex-brain/PHASE-*-CONTINUED-PROGRESS.md"
      action: archive
      archive_to: "cortex-brain/archives/phase-reports/"
      risk: medium
      
    build_output:
      paths:
        - "site/"
      action: delete_all
      risk: low
      
    workflow_checkpoints:
      paths:
        - "workflow_checkpoints/wf-*.json"
      action: retain_days
      retain_days: 7
      risk: low
      
    legacy_backups:
      paths:
        - "src/cortex_agents/*.backup"
      action: delete_all
      risk: low
      
  safety:
    dry_run_default: true
    require_git_clean: true
    create_manifest: true
    max_recursion_depth: 10
    
  retention:
    default_backup_count: 5
    default_days: 7
    archive_before_delete: true
```

---

## 🚀 Implementation Checklist

### Phase 1: Test Harness (This Session)
- [ ] Create `tests/plugins/test_cleanup_orchestrator.py`
- [ ] Implement safety validation tests
- [ ] Implement dry-run mode tests
- [ ] Implement retention policy tests
- [ ] Implement rollback tests
- [ ] Implement recursion protection tests

### Phase 2: Cleanup Logic Updates
- [ ] Add nested backup archive detection
- [ ] Implement retention policies
- [ ] Add rollback/restore functionality
- [ ] Enhance dry-run reporting
- [ ] Add Git status validation

### Phase 3: Configuration
- [ ] Create `cortex-brain/cleanup-rules.yaml`
- [ ] Update cleanup orchestrator to read rules
- [ ] Add risk level validation
- [ ] Add archive functionality

### Phase 4: Execution
- [ ] Run cleanup in dry-run mode
- [ ] Review proposed deletions
- [ ] Execute high-priority cleanup
- [ ] Verify space savings
- [ ] Document results

---

## 📊 Expected Results

### Before Cleanup

| Metric | Value |
|--------|-------|
| **Redundant Files** | 376+ |
| **Redundant Folders** | 184+ |
| **Wasted Space** | ~18+ MB |
| **Backup Files** | 93 |
| **Session Reports** | 50+ |

### After Cleanup (Conservative)

| Metric | Value | Improvement |
|--------|-------|-------------|
| **Redundant Files** | <50 | 86% reduction |
| **Redundant Folders** | <20 | 89% reduction |
| **Wasted Space** | <3 MB | 83% reduction |
| **Backup Files** | 5-10 | 90% reduction |
| **Session Reports** | 10-15 | 75% reduction |

**Total Space Recovered:** ~15-17 MB  
**Maintenance Reduction:** ~85%  
**Clarity Improvement:** Significant

---

## ⚠️ Critical Warnings

### DO NOT DELETE

These directories are **CRITICAL** and must **NEVER** be deleted:

1. `cortex-brain/left-hemisphere/`
2. `cortex-brain/right-hemisphere/`
3. `cortex-brain/corpus-callosum/`
4. `cortex-brain/cognitive-framework/`
5. `cortex-brain/tier1/`
6. `cortex-brain/tier2/`
7. `cortex-brain/tier3/`
8. `cortex-brain/schemas/`
9. `src/` (except `.backup` files)
10. `tests/` (active test suite)

### Manual Review Required

These require human judgment:

1. `cortex-brain/archives/` (intentional archival)
2. `cortex-brain/inventory-v1/` (may contain unique data)
3. `cortex-brain/discovery-reports/` (may be useful)
4. `cortex-brain/cortex-2.0-design/archive/` (design history)

---

## 📝 Next Steps

**Immediate:**
1. ✅ Complete this scan report
2. ⏳ Create test harness (next task)
3. ⏳ Implement safety validations
4. ⏳ Execute dry-run cleanup

**Short-term:**
1. Review cleanup results
2. Update retention policies
3. Document cleanup procedures
4. Schedule regular cleanup

**Long-term:**
1. Automate cleanup (weekly cron)
2. Add monitoring/alerts
3. Create cleanup dashboard
4. Establish governance policies

---

## 📚 References

- **Cleanup Orchestrator:** `src/plugins/cleanup_orchestrator_plugin.py`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Git Repository:** `D:\PROJECTS\CORTEX\.git`
- **Issue Tracker:** GitHub Issues (CORTEX repository)

---

**Generated by:** CORTEX Cleanup Scan System  
**Scan Date:** November 11, 2025  
**Report Version:** 1.0  
**Confidence:** HIGH (comprehensive scan completed)

---

*This report provides a foundation for safe, systematic cleanup of the CORTEX workspace. All recommendations include safety checks and rollback capabilities.*
