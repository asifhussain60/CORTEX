# Phase 2: Legacy Removal (Subtraction Batches)
## EXECUTION PLAN & PROCEDURES

**Date:** 2026-01-27  
**Phase:** 2 (Ready for Execution)  
**Status:** ✅ READY  
**Authority:** CORTEX Master Orchestrator  

---

## 🎯 EXECUTIVE SUMMARY

**Phase 2 will systematically remove legacy/duplicate/cruft files through 5 deletion batches.** Each batch includes validation gates and rollback procedures.

| Batch | Name | Files | Action | Status |
|-------|------|-------|--------|--------|
| 1 | Remove Legacy Wiring Systems | 8 | Delete | 📋 READY |
| 2 | Remove Database Files | 5+ | Delete | 📋 READY |
| 3 | Consolidate Duplicates | 2 | Delete/Rename | 📋 READY |
| 4 | Remove Cruft Documentation | Many | Delete | 📋 READY |
| 5 | Remove Archive Directories | 2 | Delete | 📋 READY |

**Total Files to Remove:** ~60 files  
**Timeline:** 3 days (Days 1-3)  
**Automation:** Fully scripted in `phase-2-execute.sh`

---

## 📋 PHASE 2 INPUTS (FROM PHASE 1)

```yaml
Phase 1 Outputs:
  total_python_files: 901
  total_lines_of_code: 230354
  test_baseline: 4134
  component_categories: 20+
  import_validity: "100%"
  broken_imports: 0
```

---

## 🔧 PHASE 2 BATCHES

### BATCH 1: REMOVE LEGACY WIRING SYSTEMS

**Purpose:** Eliminate 7 competing wiring implementations, consolidate to single YAML-based wiring.

**Files to Delete (8):**

```
cortex/orchestrators/core/database_registry.py
  - Purpose: Old database-backed registry
  - Status: Being replaced by Git-backed wiring.yaml
  
cortex/orchestrators/core/orchestrator_registry.py
  - Purpose: Competing registry implementation
  - Status: Duplicate of database_registry.py
  
cortex/orchestrators/bootstrap.py
  - Purpose: Old bootstrap mechanism
  - Status: Replaced by cortex/wiring/bootstrap.py (Phase 5)
  
cortex/orchestrators/core/db_wiring_init.py
  - Purpose: Database wiring initialization
  - Status: Replaced by Git-backed initialization
  
cortex/orchestrators/core/permanent_wiring_state.py
  - Purpose: Persistent wiring state
  - Status: No longer needed (Git is persistent)
  
cortex/orchestrators/core/autowiring_orchestrator.py
  - Purpose: Automatic orchestrator wiring
  - Status: Replaced by static YAML wiring
  
cortex/orchestrators/core/intent_router_factory.py
  - Purpose: Factory for intent router creation
  - Status: Subsumed by new bootstrap
  
cortex/infrastructure/wiring_contract_manager.py
  - Purpose: Contract-based wiring
  - Status: Replaced by YAML schema validation
  
cortex/infrastructure/wiring_drift_detector.py
  - Purpose: Detect wiring drift
  - Status: No longer needed (Git prevents drift)
```

**Validation After Deletion:**
```bash
# Check if cortex still imports
python3 -c "import cortex"

# Run orchestrator tests
pytest tests/orchestrators/ -q --tb=short -x
```

**Expected Result:**
- 8 files removed
- 0 broken imports
- Some tests may fail (expected - they may depend on removed modules)

**Rollback Procedure:**
```bash
git checkout HEAD -- cortex/orchestrators/core/
git checkout HEAD -- cortex/infrastructure/wiring*
```

---

### BATCH 2: REMOVE DATABASE FILES

**Purpose:** Eliminate all database-related code (SQLite replaced by ephemeral container DB in Docker).

**Files to Delete:**

```
cortex/migrations/
  - Purpose: Database migration scripts
  - Status: Not needed (no persistent DB in Docker)
  
cortex/infrastructure/database.py
  - Purpose: Database connection management
  - Status: Removed entirely
  
All *.db files (find cortex -name "*.db" -delete)
  - Runtime database files
  - .db, .db-journal, .db-shm, .db-wal
```

**Validation After Deletion:**
```bash
# Check if cortex still imports
python3 -c "import cortex"

# Verify no remaining .db files
find cortex -name "*.db" | wc -l  # Should output 0
```

**Expected Result:**
- 0 broken imports
- No database-related code remaining
- Clean state for Docker ephemeral DB

**Rollback Procedure:**
```bash
git checkout HEAD -- cortex/migrations/
git checkout HEAD -- cortex/infrastructure/database.py
```

---

### BATCH 3: CONSOLIDATE DUPLICATES

**Purpose:** Remove duplicate/legacy implementations, keep enhanced versions.

**Operations:**

```
Keep enhanced_refactoring_orchestrator.py, remove refactoring_orchestrator.py
  From: cortex/orchestrators/domain/
  Reason: Enhanced version is superset
  
Keep enhanced_planning_orchestrator.py, remove planning_orchestrator.py
  From: cortex/orchestrators/domain/
  Reason: Enhanced version is superset
  
Delete: cortex/infrastructure/pre_op_enforcer.py
  Reason: Superseded by new infrastructure
  
Delete: cortex/infrastructure/core035_compliance_check.py
  Reason: Compliance integrated into main code
```

**Validation After Deletion:**
```bash
python3 -c "import cortex; from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator"
```

**Expected Result:**
- 2 original versions removed (keeping enhanced)
- 2 compliance files removed
- Simpler orchestrator structure

---

### BATCH 4: REMOVE CRUFT DOCUMENTATION

**Purpose:** Clean up excessive documentation files left from earlier phases.

**Files to Delete:**

```
Pattern: AC-*.md (all files matching)
  - Example: AC-PERMANENT-FIX-001.md, AC-FR-WIRING-001.md
  - These are archived acceptance criteria, kept in version control
  
Pattern: *-COMPLETION-REPORT*.md (except Phase-specific)
  - Example: CORTEX-NUMBERED-OPTIONS-COMPLETION-CERTIFICATE.md
  - Archived reports from earlier phases
  - KEEP: PHASE-*-COMPLETION-REPORT*.md (phase tracking)
  
Pattern: *-COMPLETION-CERTIFICATE*.md
  - Example: CORTEX-NUMBERED-OPTIONS-DEMO.md
  - Archived completion documentation
  
Pattern: PHASE_*_COMPLETION*.md
  - Old phase completion files (using underscore naming)
  - New format uses hyphens
```

**Files to KEEP:**
```
docs/00-README.md
docs/ROOT-README.md
_workspaces/docker-plan/PHASE-*-COMPLETION-REPORT.md (current phase tracking)
```

**Expected Result:**
- ~30-40 .md files removed
- Cleaner root directory
- Phase tracking preserved in docker-plan folder

---

### BATCH 5: REMOVE ARCHIVE DIRECTORIES

**Purpose:** Remove legacy archive directories containing old code/scripts.

**Directories to Delete:**

```
cortex/scripts-root-archive/ (46 Python files)
  - Purpose: Legacy scripts archived during earlier refactoring
  - Status: Not referenced anywhere
  - Size: ~15 MB
  
_backups/ (if created during migration prep)
  - Purpose: Pre-migration backup
  - Status: Not needed after successful Phase 1
  - Note: Separate backup maintained outside _backups folder
```

**Validation After Deletion:**
```bash
# Verify directories removed
[ ! -d "cortex/scripts-root-archive" ] && echo "✓ Archive removed"
[ ! -d "_backups" ] && echo "✓ Backup removed"
```

**Expected Result:**
- 46 legacy script files removed
- ~15 MB disk space freed
- Clean directory structure

---

## 📊 PHASE 2 EXPECTED OUTCOMES

### File Count

```
BEFORE Phase 2:
  Total Python Files: 901
  Breakdown:
    - orchestrators: 178
    - brain: 145
    - infrastructure: 52
    - core: 96
    - mcp: 40
    - scripts-root-archive: 46 (to delete)
    - other: 344

AFTER Phase 2:
  Total Python Files: ~850
  Removed: ~51 files
  Breakdown:
    - orchestrators: 170 (removed legacy: -8)
    - brain: 145 (no change)
    - infrastructure: 50 (removed DB/wiring: -2)
    - core: 96 (no change)
    - mcp: 40 (no change)
    - scripts-root-archive: 0 (DELETED: -46)
    - other: 299
```

### Test Count

```
BEFORE Phase 2: 4,134 tests collected
AFTER Phase 2: ~4,000-4,050 tests (some may be orphaned)
  
Some test failures expected:
  - Tests that import deleted modules
  - Phase 3 will resolve these dependencies
```

### Code Quality

```
BEFORE Phase 2:
  - 7 competing wiring systems (PROBLEM)
  - SQLite database code (to be replaced)
  - Duplicate orchestrator implementations
  - Legacy script archive included
  
AFTER Phase 2:
  - 0 wiring systems (ready for Phase 5 creation)
  - 0 database code
  - Single implementation per orchestrator
  - Archive removed (cleanup)
```

---

## 🔄 EXECUTION PROCEDURES

### Pre-Execution Checklist

- [ ] Git working tree is clean (`git status`)
- [ ] All commits are pushed (`git push`)
- [ ] Phase 1 completion report reviewed
- [ ] Current branch is `CORTEX` or `CORTEX-docker`
- [ ] Test baseline captured (4,134 tests)

### Execution Steps

**Option A: Automated Execution (Recommended)**

```bash
cd /Users/asifhussain/PROJECTS/CORTEX/_workspaces/docker-plan

# Make script executable
chmod +x phase-2-execute.sh

# Run automated Phase 2
./phase-2-execute.sh 2>&1 | tee phase2-execution.log

# Review execution log
cat phase2-execution.log
```

**Option B: Manual Execution (Batch-by-Batch)**

```bash
# Batch 1: Remove legacy wiring
rm -f cortex/orchestrators/core/database_registry.py
# ... (repeat for all 8 files)
git commit -m "chore(phase2): batch 1 - remove legacy wiring"

# Batch 2: Remove databases
rm -rf cortex/migrations
# ... (repeat for database files)
git commit -m "chore(phase2): batch 2 - remove database files"

# ... (repeat for batches 3-5)
```

### Validation After Each Batch

```bash
# Test import
python3 -c "import cortex" || echo "IMPORT FAILED"

# Quick test run
pytest tests/ -q --tb=no -x 2>&1 | head -10

# Review commits
git log --oneline -10
```

### Rollback Procedure (If Needed)

**Full Phase 2 Rollback:**
```bash
git reset --hard HEAD~5  # Undo last 5 commits (assumes 1 per batch)
git log --oneline -1
```

**Selective Rollback (Single Batch):**
```bash
git revert <commit-hash>
```

---

## 📋 ACCEPTANCE CRITERIA FOR PHASE 2

### AC-2.1: Batch 1 Complete (Legacy Wiring Removed)
- ✅ 8 wiring files deleted
- ✅ Cortex still importable
- ✅ Batch committed to git

### AC-2.2: Batch 2 Complete (Database Files Removed)
- ✅ 0 .db files remaining
- ✅ migrations/ directory deleted
- ✅ database.py deleted
- ✅ Batch committed to git

### AC-2.3: Batch 3 Complete (Duplicates Consolidated)
- ✅ Duplicate implementations removed
- ✅ Enhanced versions retained
- ✅ Batch committed to git

### AC-2.4: Batch 4 Complete (Cruft Documentation Removed)
- ✅ AC-*.md files removed
- ✅ *-COMPLETION-*.md files removed
- ✅ Phase tracking docs preserved
- ✅ Batch committed to git

### AC-2.5: Batch 5 Complete (Archive Removed)
- ✅ scripts-root-archive/ deleted
- ✅ _backups/ directory deleted (if created)
- ✅ Batch committed to git

### AC-2.6: All Imports Still Resolvable
- ✅ `import cortex` succeeds
- ✅ Core imports work (`from cortex.orchestrators import MasterOrchestrator`)
- ✅ 0 broken imports

### AC-2.7: Test Suite Baseline Captured
- ✅ Test count recorded (before ~4,134, after TBD)
- ✅ Test failures documented (expected for Phase 3)

---

## 🚦 PHASE 2 GATES

### Entry Gate (Phase 1 → Phase 2)
- ✅ Phase 1 complete (component analysis done)
- ✅ Git state clean
- ✅ Test baseline captured
- ✅ **STATUS: OPEN**

### Exit Gate (Phase 2 → Phase 3)
- ⏳ All 5 batches complete
- ⏳ All 7 acceptance criteria passed
- ⏳ All commits reviewed
- ⏳ Ready for dependency resolution

---

## 📊 PHASE 2 METRICS

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| Python Files | 901 | ~850 | -51 (-5.7%) |
| Lines of Code | 230K+ | ~220K | -10K |
| Wiring Systems | 7 | 0 | -7 ✅ |
| Database Files | 5+ | 0 | -5+ ✅ |
| Test Count | 4,134 | ~4,050 | -84 |
| Archive Files | 46 | 0 | -46 ✅ |
| Cruft Docs | 30+ | 0 | -30+ ✅ |

---

## ✅ READY FOR EXECUTION

**Phase 2 is ready to execute.**

### Next Steps

1. **Review this document** - Understand all batches
2. **Run Phase 2 automation:**
   ```bash
   cd _workspaces/docker-plan
   chmod +x phase-2-execute.sh
   ./phase-2-execute.sh
   ```
3. **Validate all acceptance criteria** - Confirm 7/7 passed
4. **Commit completion report** - Document results
5. **Proceed to Phase 3** - Dependency resolution

---

## 📞 SUPPORT

**If batch fails:**
1. Check execution log: `cat phase2-execution.log`
2. Review error message
3. Roll back: `git reset --hard HEAD~1`
4. Fix issue manually
5. Re-run batch

**If tests fail:**
1. Run specific failing tests: `pytest tests/orchestrators/ -v`
2. Identify import issues
3. Phase 3 handles dependency resolution

---

**Created:** 2026-01-27  
**Authority:** CORTEX Master Orchestrator  
**Status:** ✅ READY FOR EXECUTION

**→ Proceed to Phase 2 when ready**
