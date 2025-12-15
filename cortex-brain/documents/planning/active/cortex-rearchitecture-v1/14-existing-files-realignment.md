# Phase 14: Existing Files Realignment

**Phase:** 14 - Existing Files Realignment  
**Plan:** cortex-rearchitecture-v1  
**Date:** December 15, 2025  
**Status:** 📋 PLANNED

---

## 🎯 Objective

Migrate all existing plan files (master plans, sub-plans, ADO work items) to use the new unified planning architecture from Phase 13. Ensure consistency, add missing token tracking, and validate all files follow the standard format.

---

## 📊 Scope Analysis

### Files to Migrate

**1. Active Plans** (`cortex-brain/documents/planning/active/`)
```bash
# Count active master plans
find cortex-brain/documents/planning/active -name "00-master-plan.md" -o -name "master-plan.md"

# Estimate: 10-15 active plans
```

**2. Completed Plans** (`cortex-brain/documents/planning/completed/`)
```bash
# Count completed master plans
find cortex-brain/documents/planning/completed -name "*.md" | grep -E "(master|MASTER)"

# Estimate: 50+ completed plans
```

**3. ADO Plans** (`cortex-brain/documents/planning/ado/`)
```bash
# Count ADO work items
find cortex-brain/documents/planning/ado -name "*.md"

# Estimate: 20-30 work items
```

**4. Archived Plans** (`cortex-brain/documents/planning/archived/`)
```bash
# Count archived plans
find cortex-brain/documents/planning/archived -name "*.md"

# Estimate: 100+ archived plans
```

---

## 🏗️ Migration Strategy

### Priority Tiers

**Tier 1: ACTIVE PLANS** (CRITICAL)
- All plans in `active/` folder
- Currently in use
- Must have token tracking
- Must have progress trackers
- **Timeline:** Day 1-2

**Tier 2: RECENT COMPLETED** (HIGH)
- Plans completed in last 90 days
- Still referenced frequently
- Good candidates for token reduction measurement
- **Timeline:** Day 3-4

**Tier 3: ADO WORK ITEMS** (MEDIUM)
- Current ADO structure works
- Optional: Add unified format for Features/Epics
- **Timeline:** Day 5 (optional)

**Tier 4: ARCHIVED PLANS** (LOW)
- Historical reference only
- Migrate on-demand or batch process
- **Timeline:** Future/on-demand

---

## 📋 Implementation Tasks

### Task 14.1: Create Migration Utility
**File:** `scripts/migrate_existing_plans.py`

**Actions:**
- [ ] Create `PlanMigrationUtility` class
- [ ] Implement `detect_plan_format()` (identify current format)
- [ ] Implement `migrate_to_unified()` (convert to new format)
- [ ] Implement `validate_migration()` (ensure correctness)
- [ ] Add dry-run mode (preview changes without writing)
- [ ] Add batch processing support

**Migration Steps:**
```python
class PlanMigrationUtility:
    def __init__(self, unified_generator: UnifiedPlanGenerator):
        self.generator = unified_generator
        self.token_tracker = TokenReductionTracker()
    
    def migrate_plan(
        self,
        plan_path: Path,
        dry_run: bool = True
    ) -> MigrationResult:
        """
        Migrate plan to unified format.
        
        Steps:
        1. Parse existing plan
        2. Extract metadata (phases, status, durations)
        3. Generate new format using UnifiedPlanGenerator
        4. Validate structure
        5. Backup original
        6. Write new format (if not dry_run)
        """
        pass
    
    def batch_migrate(
        self,
        folder: Path,
        filter_pattern: str = "*.md",
        dry_run: bool = True
    ) -> BatchMigrationResult:
        """
        Migrate all plans in folder.
        
        Returns:
        - plans_found: 45
        - plans_migrated: 40
        - plans_skipped: 5 (already unified format)
        - errors: []
        """
        pass
```

**Tests:**
- [ ] `test_detects_old_format_correctly()`
- [ ] `test_migrates_to_new_format()`
- [ ] `test_preserves_existing_data()`
- [ ] `test_dry_run_doesnt_modify_files()`
- [ ] `test_batch_migration_handles_errors()`

**Estimated Time:** 4h

---

### Task 14.2: Add Token Baseline to Existing Plans
**File:** `scripts/measure_existing_plans_tokens.py`

**Actions:**
- [ ] Extend `measure_prompt_tokens.py` to work per-plan
- [ ] Measure tokens for each active plan folder
- [ ] Record baselines in `cortex-brain/metrics/plan-baselines/`
- [ ] Update master plans with baseline metrics
- [ ] Generate comparison report

**Output:**
```json
{
  "plan_id": "cortex-rearchitecture-v1",
  "baseline_date": "2025-12-15",
  "total_tokens": 45000,
  "files": [
    {"file": "00-master-plan.md", "tokens": 2500},
    {"file": "01-visual-tracker-migration.md", "tokens": 8500},
    ...
  ],
  "reduction_target": 6750,
  "target_percentage": 15
}
```

**Tests:**
- [ ] `test_measures_plan_tokens_correctly()`
- [ ] `test_stores_baseline_json()`
- [ ] `test_calculates_reduction_target()`

**Estimated Time:** 2h

---

### Task 14.3: Migrate Active Plans (cortex-rearchitecture-v1)
**Target:** `cortex-brain/documents/planning/active/cortex-rearchitecture-v1/`

**Actions:**
- [ ] Run migration utility on `00-master-plan.md`
- [ ] Add token baseline (already have: 6.7M tokens)
- [ ] Verify progress tracker format matches unified standard
- [ ] Update all sub-plan headers
- [ ] Validate phase links work
- [ ] Run end-to-end test

**Manual Review:**
- [ ] Check visual progress tracker rendering
- [ ] Verify token reduction metric shows correctly
- [ ] Confirm continuation prompt is copy-paste ready
- [ ] Test phase status updates work

**Estimated Time:** 2h

---

### Task 14.4: Migrate Cortex-Lens-v3 Plan
**Target:** `cortex-brain/documents/planning/active/cortex-lens-v3/`

**Actions:**
- [ ] Migrate `00-master-plan.md`
- [ ] Migrate `00-implementation-plan.md`
- [ ] Update all 11 sub-plan files
- [ ] Establish token baseline for this plan
- [ ] Validate all phase links

**Estimated Time:** 3h

---

### Task 14.5: Migrate Dashboard Consolidation Plan
**Target:** `cortex-brain/documents/planning/active/dashboard-consolidation/`

**Actions:**
- [ ] Migrate `MASTER-PLAN.md`
- [ ] Update progress tracker
- [ ] Add token tracking
- [ ] Validate structure

**Estimated Time:** 2h

---

### Task 14.6: Batch Migrate Remaining Active Plans
**Target:** All other plans in `active/`

**Actions:**
- [ ] List all active plans
- [ ] Run batch migration utility
- [ ] Review dry-run report
- [ ] Execute migration
- [ ] Spot-check 5 random plans for quality

**Estimated Time:** 3h

---

### Task 14.7: Migrate Recent Completed Plans
**Target:** `cortex-brain/documents/planning/completed/` (last 90 days)

**Actions:**
- [ ] Identify plans completed after Sept 15, 2025
- [ ] Run batch migration
- [ ] Add completion metrics (if missing)
- [ ] Archive original formats in `.backup/`

**Estimated Time:** 3h

---

### Task 14.8: Create Migration Report
**File:** `cortex-brain/documents/reports/planning-migration-report-2025-12-15.md`

**Actions:**
- [ ] Generate comprehensive migration report
- [ ] Include before/after statistics
- [ ] List all migrated files
- [ ] Document any issues encountered
- [ ] Provide rollback instructions (if needed)

**Report Structure:**
```markdown
# Planning Architecture Migration Report

**Date:** December 15, 2025  
**Phase:** 14 - Existing Files Realignment

## Executive Summary
- **Plans Migrated:** 45/50
- **Token Baselines Established:** 45
- **Format Violations Fixed:** 23
- **Errors:** 0

## Active Plans (15 migrated)
- cortex-rearchitecture-v1 ✅
- cortex-lens-v3 ✅
- dashboard-consolidation ✅
- ...

## Completed Plans (20 migrated)
- ...

## Skipped Plans (5)
- Reason: Already in unified format
- ...

## Token Metrics
- **Total Baseline:** 145M tokens
- **Reduction Target:** 22M tokens (15%)
- **Measurement Date:** 2025-12-15

## Next Steps
- Monitor token reduction in next 30 days
- Archive original formats after 7 days
- Update documentation links
```

**Estimated Time:** 2h

---

### Task 14.9: Update Documentation Links
**Files:** Multiple references across `cortex-brain/documents/`

**Actions:**
- [ ] Find all links to migrated plans
- [ ] Update paths if changed
- [ ] Verify links still work
- [ ] Update quick reference guides

**Search Pattern:**
```bash
grep -r "cortex-brain/documents/planning" cortex-brain/documents/ | grep -v ".backup"
```

**Estimated Time:** 2h

---

### Task 14.10: Validation Testing
**File:** `tests/integration/test_plan_migration_validation.py`

**Actions:**
- [ ] Create validation test suite
- [ ] Test all migrated active plans load correctly
- [ ] Test progress trackers render properly
- [ ] Test token metrics display correctly
- [ ] Test continuation prompts work
- [ ] Test phase lifecycle updates work

**Tests:**
- [ ] `test_all_active_plans_valid()`
- [ ] `test_progress_trackers_render()`
- [ ] `test_token_metrics_calculated()`
- [ ] `test_continuation_prompts_copyable()`
- [ ] `test_phase_updates_work()`

**Estimated Time:** 3h

---

## 🎯 Success Metrics

**Migration Completeness:**
- ✅ 100% of active plans migrated
- ✅ 80%+ of recent completed plans migrated
- ✅ Token baselines established for all active plans
- ✅ All migrated plans pass validation

**Quality:**
- ✅ No broken links
- ✅ No format violations
- ✅ Consistent visual appearance
- ✅ All tests passing

**Documentation:**
- ✅ Migration report published
- ✅ Rollback instructions available
- ✅ Updated quick reference guides

**Token Efficiency:**
- ✅ Baselines recorded for future comparison
- ✅ Reduction targets set (15% target)
- ✅ Measurement system ready for tracking

---

## 📊 Before/After Comparison

### Before Phase 14

**Active Plans:**
- ❌ Inconsistent formats (3-4 different templates)
- ❌ No token tracking
- ❌ Incomplete progress trackers
- ❌ Manual continuation prompts
- ❌ No percentage-based metrics

**Completed Plans:**
- ❌ Legacy formats
- ❌ No token metrics
- ❌ Difficult to compare

### After Phase 14

**Active Plans:**
- ✅ Unified format (single template)
- ✅ Token tracking with baselines
- ✅ Complete progress trackers
- ✅ Auto-generated continuation prompts
- ✅ Percentage-based metrics

**Completed Plans:**
- ✅ Migrated to unified format
- ✅ Token baselines recorded
- ✅ Easy cross-plan comparison

---

## 🚨 Risk Mitigation

**Risk:** Data loss during migration
- **Mitigation:** Automatic backups before migration, dry-run mode

**Risk:** Breaking existing workflows
- **Mitigation:** Gradual rollout, validation testing

**Risk:** Token measurement errors
- **Mitigation:** Multiple validation checks, manual spot-checks

**Risk:** Migration script bugs
- **Mitigation:** TDD approach, comprehensive test suite

---

## 🔗 Dependencies

**Requires:**
- Phase 13: Planning Architecture Unification (MUST complete first)
  - UnifiedPlanGenerator
  - TokenReductionTracker
  - PhaseLifecycleManager

**Blocks:**
- Future token optimization work (needs baselines from this phase)
- Cross-plan analytics (needs consistent format)

---

## 📅 Estimated Duration

**Total Time:** 26 hours (3-4 days)

**Task Breakdown:**
- Task 14.1: Migration Utility (4h)
- Task 14.2: Token Baseline Measurement (2h)
- Task 14.3: Migrate cortex-rearchitecture-v1 (2h)
- Task 14.4: Migrate cortex-lens-v3 (3h)
- Task 14.5: Migrate dashboard-consolidation (2h)
- Task 14.6: Batch Migrate Active Plans (3h)
- Task 14.7: Migrate Completed Plans (3h)
- Task 14.8: Migration Report (2h)
- Task 14.9: Update Documentation Links (2h)
- Task 14.10: Validation Testing (3h)

---

## 📝 Notes

- **Backup Strategy:** All originals backed up to `.backup/` folder
- **Rollback:** Keep backups for 30 days, then archive
- **Monitoring:** Track token reduction over next 30 days
- **Documentation:** Update all references to new format

**Estimated Duration:** 26h (3-4 days)  
**Risk Level:** MEDIUM (bulk file operations)  
**Priority:** HIGH (ensures consistency across all plans)
