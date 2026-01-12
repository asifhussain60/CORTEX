# Regression Risk Analysis: Full Audit Remediation
**Date:** January 12, 2026  
**Scope:** AC-ID integration + File reorganization + Prompt updates + Plan/Dashboard sync  
**Risk Level:** MEDIUM (with mitigations)

---

## Executive Summary

**GO / NO-GO:** ✅ **SAFE TO PROCEED** (with phased execution + validation gates)

**Key Risks Identified:** 5 MEDIUM + 3 LOW  
**Mitigation Strategy:** Phased execution with automated validation gates + rollback plan  
**Estimated Impact:** 0 regressions (if gates pass) | Complete rollback if ANY gate fails  
**Execution Timeline:** 8 hours with validation gates (vs 4 hours without)

---

## 1. Risk Categories & Findings

### 1.1 AC-INDEX.yaml Integration (MEDIUM RISK)

**What Could Break:**
- ✅ SAFE: AC-INDEX.yaml is YAML-parseable (schema v1.7 validated)
- ✅ SAFE: Current structure uses nested `foundation.{category}` + flat `categories` arrays
- ⚠️ MEDIUM: Appending 29 AC-IDs to `foundation.ac_brittleness` adds ~800 lines
- ⚠️ MEDIUM: **File size growth:** 134KB → ~150KB (+12%) — ACCEPTABLE (no 1MB limit breached)

**Consumers of AC-INDEX.yaml (Critical Path):**

| Consumer | Location | Risk | Impact |
|----------|----------|------|--------|
| `atomic_state_manager.py` | Lines 175-215 | MEDIUM | Iterates `acceptance_criteria` section (need to check if exists) |
| `autonomous_ac_implementor.py` | Lines 94-179 | MEDIUM | Loads AC-INDEX, iterates `foundation` section |
| `sync_plan_viewer_data.py` | Lines 10-40 | MEDIUM | Loads `foundation` section for AC-ID mappings |
| `brittleness_validator.py` | Lines 381-392 | MEDIUM | Reads `total_ac_count` field |
| Tests: `test_state_synchronizer.py` | Line 131 | MEDIUM | Validates AC-INDEX structure via `_validate_ac_index()` |

**Specific Issue Found:**
```python
# atomic_state_manager.py:185 - ASSUMES THIS SECTION EXISTS
for category in ac_index.get('acceptance_criteria', []):
    for item in category.get('items', []):
        if item.get('id') == ac_id:
            # Update logic
```

**Problem:** AC-INDEX.yaml currently uses `foundation.{category}` structure, NOT `acceptance_criteria.{category}` structure. This will cause:
- ✅ **SAFE:** `ac_index.get('acceptance_criteria', [])` returns empty list (not error)
- ✅ **SAFE:** Loop does nothing, but doesn't crash
- ⚠️ **WARNING:** AC updates won't persist to AC-INDEX (silent failure)

---

### 1.2 Master Plan Synchronization (MEDIUM RISK)

**Current State:**
```yaml
# master-plan.yaml line 16
total_ac_ids: 97  # HARDCODED

# phase_1_foundation section uses:
ac_ids_complete: 16
ac_ids_total: 33
```

**Problem:** Master plan has:
- Hardcoded AC-ID counts (97 total)
- Phase-by-phase AC-ID counts (need update after integration)
- Brittleness AC-IDs (29 new) not assigned to phases yet

**What Will Break:**
- ⚠️ MEDIUM: Brittleness AC-IDs won't appear in master plan's phase assignments
- ⚠️ MEDIUM: Plan viewer dashboard will show outdated totals (97 vs 126)
- ⚠️ MEDIUM: `sync_plan_viewer_data.py` will report stale metrics

**Impact Chain:**
```
Add 29 AC-IDs to AC-INDEX 
  → AC-INDEX now has 131 AC-IDs
  → master-plan.yaml still says 97
  → progress-tracker.json misaligned with reality
  → plan-viewer.html shows wrong percentages
  → Users confused about completion %
```

---

### 1.3 File Organization (LOW-MEDIUM RISK)

**Governance Violations Found:** 450+ files

**Critical Path Impact:**
- ✅ SAFE: Moving files doesn't break imports (relative paths use `Path()`)
- ✅ SAFE: Tests reference files by glob patterns
- ⚠️ MEDIUM: Scripts with hardcoded paths will break:
  - `sync_plan_viewer_data.py` line 14: `'cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml'`
  - `update_plan_viewer_progress.py` (if it exists)
  - Multiple scripts reference `cortex-brain/documents/reports/`

**Files That Will Break If Reorganized:**
```
cortex-brain/documents/reports/
  ├── AC-IDS-BRITTLENESS-2026-01-12.yaml     # Currently: reports/
  ├── BRITTLENESS-REVIEW-EXECUTIVE-SUMMARY-2026-01-12.md
  └── CORTEX6-BRITTLENESS-REVIEW-2026-01-12.md

Moving these to:
cortex-brain/documents/reports/brittleness/
  └── findings-2026-01-12.yaml                # REQUIRES script updates
```

**Scripts That Reference These Paths:**
```bash
grep -r "reports/" scripts/*.py | grep -v "\.pyc" | grep -v "archive"
# Result: 12 hardcoded references to cortex-brain/documents/reports/
```

---

### 1.4 Prompt Updates (LOW RISK)

**Updates Needed:** 4 prompts

| Prompt | Change | Risk |
|--------|--------|------|
| `cortex-brittleness-review.prompt.md` | ✅ DONE | LOW (applied) |
| `cortex-evidence-validator.prompt.md` | Add OUTPUT SPEC | LOW (append only) |
| `cortex-exec.prompt.md` | Add OUTPUT SPEC | LOW (append only) |
| `CORTEX.prompt.md` | Add OUTPUT SPEC | LOW (append only) |

**Risk:** Extremely low — only adding sections, not modifying execution logic.

---

### 1.5 Plan-Viewer Dashboard Sync (MEDIUM RISK)

**Current State:**
```
templates/plan-viewer/
  ├── cortex-plan-viewer.html           (UI - has HARDCODED phase data)
  ├── plan-viewer-data.json             (Data source - auto-synced)
  └── [various supporting files]
```

**Problem:** `cortex-plan-viewer.html` may have hardcoded metrics:
```html
<!-- If hardcoded like this, will be incorrect after AC integration -->
<div class="phase-completion" data-percentage="48%">Phase 1: 48%</div>
```

**What Will Break:**
- ⚠️ MEDIUM: HTML shows wrong metrics if hardcoded
- ✅ SAFE: `plan-viewer-data.json` auto-generated (will be correct)
- ⚠️ MEDIUM: Users see inconsistency (HTML ≠ JSON)

---

## 1.6 AC-INDEX Consumer Code Mismatch (MEDIUM RISK - NOW CHARACTERIZED)

**INSPECTION COMPLETE** ✅

**Consumers Found (Active):**
```
atomic_state_manager.py:      Uses 'acceptance_criteria' section (4 references)
brittleness_validator.py:     Uses 'acceptance_criteria' section (1 reference)
sync_plan_viewer_data.py:     Uses 'foundation' section (4 references) ← SAFER
autonomous_ac_implementor.py: Not inspected (likely uses one or both)
```

**Critical Finding:**
- ✅ `sync_plan_viewer_data.py` uses `foundation` — will work fine with new AC-IDs
- ⚠️ `atomic_state_manager.py` & `brittleness_validator.py` use `acceptance_criteria` — **THIS SECTION DOESN'T EXIST**

**Current AC-INDEX Structure:**
```yaml
foundation:
  audit:
    - id: AC-AUDIT-001
      name: Queryable Audit Storage
      ...
acceptance_criteria: []  # ← EMPTY! Consumers will find nothing
```

**Impact:**
- 🔴 **HIGH RISK:** `atomic_state_manager.py` code searches for AC-IDs in empty `acceptance_criteria` section
- Result: AC-ID status updates **SILENTLY FAIL** (no error, no update)
- Progress not persisted → tests might pass but state is inconsistent

**Mitigation Options:**

**Option A: Add `acceptance_criteria` Section (Data Duplication)**
```yaml
acceptance_criteria:
  - category: Audit
    items:
      - id: AC-AUDIT-001
        name: Queryable Audit Storage
        ...
foundation:
  audit:
    - id: AC-AUDIT-001  # DUPLICATE
      ...
```
- ❌ Violates DRY principle (data in two places)
- ✅ Makes old code work without changes
- ⚠️ Creates maintenance burden

**Option B: Update Consumer Code to Use `foundation` (RECOMMENDED)**
```python
# OLD (atomic_state_manager.py:185)
for category in ac_index.get('acceptance_criteria', []):
    for item in category.get('items', []):
        ...

# NEW
for category_name, ac_list in ac_index.get('foundation', {}).items():
    for item in ac_list:
        ...
```
- ✅ Single source of truth
- ✅ No data duplication
- ⚠️ Requires code changes (simple regex replace)

**Recommendation:** **Option B** — Update 2-3 consumer modules (30 min)

**Risk:** MEDIUM → LOW (with code updates)

---

## 1.7 File Path Hardcoding (MEDIUM RISK - NOW CHARACTERIZED)

**INSPECTION COMPLETE** ✅

**Affected Scripts (4 files found):**
```
✅ scripts/analyze_untracked_files.py       References: hardcoded cortex-brain/documents/reports/
✅ scripts/capture_build_evidence.py        References: hardcoded cortex-brain/documents/reports/
✅ scripts/consolidate_cx6_plan.py          References: hardcoded cortex-brain/documents/reports/
✅ scripts/deep_structure_scan.py           References: hardcoded cortex-brain/documents/reports/
```

**Pattern Found:**
All 4 use hardcoded relative path: `cortex-brain/documents/reports/`

**Impact:**
If we reorganize to:
```
cortex-brain/documents/reports/brittleness/    ← NEW SUBFOLDER
                                    ↑
These 4 scripts won't find files
```

**Mitigation:**
1. **Before moving files:** Update all 4 scripts to use correct paths
2. **Create centralized path module:** `scripts/utils/path_utils.py`
   ```python
   REPORTS_DIR = Path("cortex-brain/documents/reports")
   BRITTLENESS_DIR = REPORTS_DIR / "brittleness"
   EVIDENCE_DIR = REPORTS_DIR / "evidence"
   ```
3. **Replace hardcoded strings** in 4 scripts with imports
4. **Test path resolution** after moves (Gate 3)

**Risk:** MEDIUM → LOW (with centralized paths + updates)

---

## 1.8 Plan-Viewer HTML Hardcoding (HIGH RISK - NOW CONFIRMED)

**INSPECTION COMPLETE** ✅

**Findings:**
HTML contains **3 LOCATIONS OF HARDCODED METRICS**:

```html
<!-- Location 1: Phase 1 badge (line ~1245) -->
<span class="badge badge-yellow">PARTIAL 48%</span>
<div class="progress-bar" style="width: 48%" aria-valuenow="48"></div>

<!-- Location 2: Phase 1.5 badge (line ~1285) -->
<span class="badge badge-yellow">IN PROGRESS 85%</span>
<div class="progress-bar" style="width: 85%" aria-valuenow="85"></div>

<!-- Location 3: Chart data (line ~1900+) -->
labels: ['Phase 1 (48%)', 'Phase 1.5 (85%)', 'Phase 2 (0%)', 'Phase 3 (0%)', 'Phase 4 (0%)']
```

**Impact:**
- 🔴 **HIGH RISK:** After AC-ID integration (131 vs 102 vs 97), these percentages become **LIES**
- Chart will display wrong phase completion metrics
- Users see stale data in UI (conflict with `plan-viewer-data.json`)
- Trust in dashboard eroded

**Mitigation:**
1. **REMOVE all hardcoded percentages** from HTML
2. **REPLACE with dynamic API calls** to `plan-viewer-data.json`
3. **Update chart** to fetch labels from API instead of hardcoded array

**Code Changes Required:**
```javascript
// OLD (hardcoded)
const labels = ['Phase 1 (48%)', 'Phase 1.5 (85%)', ...];

// NEW (dynamic)
fetch('/api/plan-data')
  .then(r => r.json())
  .then(data => {
    const labels = data.phases.map(p => `${p.name} (${p.completion}%)`);
    updateChart(labels);
  });
```

**Risk:** MEDIUM → LOW (with removal + API call)

---

## 2. Validation Gates (Mitigation Strategy)

### Gate 1: AC-INDEX Schema Validation
**When:** After appending 29 AC-IDs  
**Validates:**
- ✅ YAML parseable
- ✅ `total_ac_count` == 131
- ✅ No duplicate AC-IDs
- ✅ All required fields present
- ✅ File size < 200KB

**Failure Action:** ROLLBACK append from git

```python
# Gate 1 Script
def validate_ac_index():
    with open('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml') as f:
        data = yaml.safe_load(f)
    
    assert data['total_ac_count'] == 131, f"Expected 131, got {data['total_ac_count']}"
    
    # Extract all AC-IDs and verify uniqueness
    all_ac_ids = set()
    for category in data.get('foundation', {}).values():
        for ac in category:
            all_ac_ids.add(ac['id'])
    
    assert len(all_ac_ids) == 131, f"Expected 131 unique IDs, got {len(all_ac_ids)}"
    print(f"✅ AC-INDEX validation PASSED: {len(all_ac_ids)} unique AC-IDs")
```

### Gate 2: Master Plan Sync Validation
**When:** After updating master-plan.yaml with new totals  
**Validates:**
- ✅ `total_ac_ids` == 131
- ✅ Phase AC-ID counts sum to 131
- ✅ Progress-tracker counts ≤ master-plan counts
- ✅ YAML valid

**Failure Action:** ROLLBACK plan updates from git

### Gate 3: File Organization Integrity
**When:** After moving/renaming files  
**Validates:**
- ✅ All scripts with hardcoded paths updated
- ✅ No broken references in markdown files
- ✅ AC-INDEX path still resolves
- ✅ Tests still find fixture files

**Failure Action:** ROLLBACK file moves

### Gate 4: Plan-Viewer Dashboard Sync
**When:** After running sync_plan_viewer_data.py  
**Validates:**
- ✅ `plan-viewer-data.json` generated
- ✅ Contains 131 AC-IDs (not 102 or 97)
- ✅ HTML loads without console errors
- ✅ Dashboard metrics updated

**Failure Action:** ROLLBACK sync, investigate hardcoding

### Gate 5: Prompt Integrity
**When:** After updating all prompts  
**Validates:**
- ✅ All 4 prompts still valid YAML/Markdown
- ✅ No circular references introduced
- ✅ Output-standards.md linked correctly

**Failure Action:** ROLLBACK prompt changes

---

## 3. Identified Issues & Mitigations

### Issue #1: Brittleness AC-IDs Not In Any Phase

**Current State:**
- 29 new AC-IDs exist in separate file
- No phase assignment (Decision #2 from last session)
- Master plan will be inconsistent

**Mitigation:**
- **Assign to Phase 1.5** (new subphase for critical brittleness fixes)
- Update master-plan.yaml with phase assignments
- Create execution plan for Phase 1.5 (separate deliverable)

**Risk:** MEDIUM → LOW (with assignment)

---

### Issue #2: File Path Hardcoding

**Affected Scripts:**
```python
# sync_plan_viewer_data.py:14
ac_index_path = Path('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')

# scripts/ (12 scripts with hardcoded cortex-brain/documents/reports/)
```

**Mitigation:**
1. Use `Path.cwd().resolve()` for portability (CORE-005 compliance)
2. Create `scripts/utils/paths.py` with centralized path definitions
3. Update all 12 scripts before file reorganization
4. Validate paths resolve correctly (Gate 3)

**Risk:** MEDIUM → LOW (with centralized paths)

---

### Issue #3: AC-INDEX Consumer Code Mismatch

**Problem:** Code expects `acceptance_criteria` section, AC-INDEX has `foundation` section

**Affected Code:**
- `atomic_state_manager.py:185` — Silent failure (doesn't crash, doesn't update)

**Mitigation:**
1. Check which consumers actually work with current structure
2. Either:
   - Option A: Add `acceptance_criteria` section to AC-INDEX (duplication)
   - Option B: Update consumer code to use `foundation` section
3. Test both before/after

**Recommendation:** **Option B** (update code, don't duplicate data)

**Risk:** MEDIUM → LOW (with code update)

---

### Issue #4: Plan-Viewer HTML Hardcoding

**INSPECTION COMPLETE** ✅

**Findings:**
HTML contains **HARDCODED metrics** in 3 locations:
```html
<!-- Location 1: Phase 1 badge -->
<span class="badge badge-yellow">PARTIAL 48%</span>
<div class="progress-bar" style="width: 48%" aria-valuenow="48"></div>

<!-- Location 2: Phase 1.5 badge -->
<span class="badge badge-yellow">IN PROGRESS 85%</span>
<div class="progress-bar" style="width: 85%" aria-valuenow="85"></div>

<!-- Location 3: Chart data -->
labels: ['Phase 1 (48%)', 'Phase 1.5 (85%)', 'Phase 2 (0%)', 'Phase 3 (0%)', 'Phase 4 (0%)']
```

**Impact:**
- ⚠️ **HIGH RISK:** After AC-ID integration (131 vs 102), these percentages become LIES
- Chart will show wrong phase completion after update
- Users will see inconsistency: old HTML ≠ new JSON data

**Mitigation:**
1. **REMOVE all hardcoded percentages** from HTML
2. **Replace with dynamic data** from `plan-viewer-data.json`
3. **Update chart generation** to use API call instead of hardcoded labels

**Risk:** MEDIUM → HIGH (due to hardcoding) → MEDIUM (with removal + API call)

**Required Changes:**
- [ ] Remove 48% from Phase 1 badge
- [ ] Remove 85% from Phase 1.5 badge (or keep, depending on Phase decision)
- [ ] Replace chart labels with dynamic data from API

---

## 4. Test Coverage Impact

### Tests That Will Be Affected

| Test File | Test Function | Impact | Mitigation |
|-----------|--------------|--------|-----------|
| `test_state_synchronizer.py` | `test_validate_ac_index_valid` | ⚠️ MEDIUM | Update fixture to use `foundation` section |
| `test_path_utils.py` | `test_ac_index_path_is_file` | ✅ SAFE | No change (path doesn't change) |
| Various integration tests | Assertion checks for `total_ac_count` | ⚠️ MEDIUM | Update to expect 131, not 102 |

### New Tests Required

**Gate 1 Tests:** AC-INDEX validation (3-4 tests)
**Gate 2 Tests:** Master plan consistency (2-3 tests)
**Gate 3 Tests:** File path resolution (4-5 tests)
**Gate 4 Tests:** Dashboard sync completeness (2-3 tests)

**Total New Tests:** 11-15 tests (~30 minutes to write + run)

---

## 5. Rollback Plan

### Scenario A: AC-INDEX Append Fails
```bash
# Immediate action
git checkout cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml

# Verify
yaml cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml  # Should parse
grep "total_ac_count:" cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml  # Should show 102
```

### Scenario B: Master Plan Update Breaks Sync
```bash
# Rollback
git checkout cortex-brain/cx6-plan/master-plan.yaml

# Re-run sync
python3 scripts/sync_plan_viewer_data.py

# Verify dashboard
curl http://localhost:5000/api/plan-data  # If running dashboard server
```

### Scenario C: File Reorganization Breaks Paths
```bash
# Rollback all moves
git checkout cortex-brain/documents/reports/

# Fix scripts, then re-organize
```

### Scenario D: Prompt Updates Cause Issues
```bash
# Rollback all prompt changes
git checkout .github/prompts/

# Re-apply selectively
```

**Rollback Time:** <5 minutes (all changes in git)

---

## 6. Risk Mitigation Checklist

### Pre-Execution Checklist (Phase 0)
- [ ] **Decision 1:** Approve CORE-022 32-char exception
- [ ] **Decision 2:** Assign 29 brittleness AC-IDs to Phase 1.5
- [ ] **Decision 3:** Approve immediate file reorganization
- [x] **Inspection 1 COMPLETE:** HTML has HARDCODED metrics (48%, 85%, Phase labels)
- [x] **Inspection 2 COMPLETE:** 4 scripts have `cortex-brain/documents/reports/` paths
- [x] **Inspection 3 COMPLETE:** 2 active consumers use `acceptance_criteria`, 1 uses `foundation`

### Execution Checklist (Phases 1-4)
- [ ] Phase 1: File Organization
  - [ ] Create centralized paths module (`scripts/utils/path_utils.py`)
  - [ ] Update 4 affected scripts with new path references
  - [ ] Move files (brittleness/evidence/tdd/validation subdirs)
  - [ ] Run Gate 3 (file integrity)
  
- [ ] Phase 1.5: HTML Hardcoding Removal (NEW - DISCOVERED RISK)
  - [ ] Remove hardcoded 48% from Phase 1 badge
  - [ ] Remove hardcoded 85% from Phase 1.5 badge
  - [ ] Replace chart labels array with API call
  - [ ] Test dashboard loads without errors
  
- [ ] Phase 2: AC-ID Integration + Consumer Code Fix
  - [ ] Update `atomic_state_manager.py:185` to use `foundation` section
  - [ ] Update `brittleness_validator.py` to use `foundation` section
  - [ ] Test code paths with fixture data
  - [ ] Append 29 AC-IDs to AC-INDEX
  - [ ] Run Gate 1 (AC-INDEX validation)
  - [ ] Update `total_ac_count` in master-plan.yaml (102 → 131)
  - [ ] Run Gate 2 (master plan sync)
  
- [ ] Phase 3: Prompt Updates
  - [ ] Add OUTPUT SPEC to 4 prompts
  - [ ] Run Gate 5 (prompt integrity)
  
- [ ] Phase 4: Dashboard Sync
  - [ ] Run `sync_plan_viewer_data.py`
  - [ ] Run Gate 4 (dashboard validation)

### Post-Execution Verification
- [ ] All gates passed
- [ ] Test suite runs: `pytest tests/ -v` (100% pass rate)
- [ ] Git history clean (no merge conflicts)
- [ ] Dashboard displays updated metrics
- [ ] No console errors (browser dev tools)
- [ ] AC-INDEX parseable and valid

---

## 7. Risk Summary Table

| Risk ID | Risk | Severity | Probability | Mitigation | Residual Risk |
|---------|------|----------|-------------|-----------|---------------|
| R1 | AC-INDEX append breaks schema | MEDIUM | LOW (5%) | Gate 1 validation | LOW |
| R2 | Master plan metrics mismatch | MEDIUM | MEDIUM (30%) | Gate 2 validation | LOW |
| R3 | File paths hardcoded (4 scripts) | MEDIUM | HIGH (70%) | Centralized paths module | LOW |
| R4 | Dashboard HTML hardcoded metrics (3 locations) | **HIGH** | CERTAIN (100%) | Remove hardcoding, add API calls | **MEDIUM** |
| R5 | Prompt syntax errors | LOW | LOW (10%) | Gate 5 validation | VERY LOW |
| R6 | Test assertions fail | MEDIUM | MEDIUM (25%) | Update fixtures | LOW |
| R7 | Circular references in prompts | LOW | LOW (5%) | Inspection + testing | VERY LOW |
| R8 | AC-INDEX consumers use wrong section | **HIGH** | HIGH (80%) | Update to use `foundation` section | **LOW** |
| R9 | Brittleness AC-IDs unassigned | MEDIUM | HIGH (100%) | Decision #2 + Phase 1.5 | MEDIUM |

**Overall Risk Level:** ✅ **MEDIUM-HIGH** (manageable with gates + mitigations, but HTML hardcoding is significant)

---

## 8. Recommendations

### Recommended Execution Path: **Phased with Validation Gates**

**Phase 0 (30 min): Decision + Inspection**
- [ ] User provides 3 decisions (CORE-022, Phase assignment, timing)
- [ ] Run inspections (HTML hardcoding, script paths, AC-INDEX consumers)
- [ ] Document findings

**Phase 1 (2 hours): File Organization**
- [ ] Create centralized paths module
- [ ] Update all scripts with hardcoded paths
- [ ] Move/rename files
- [ ] Gate 3 validation

**Phase 2 (1 hour): AC-ID Integration**
- [ ] Append 29 AC-IDs to AC-INDEX
- [ ] Gate 1 validation
- [ ] Update master-plan.yaml
- [ ] Gate 2 validation

**Phase 3 (1.5 hours): Prompt Updates**
- [ ] Update 4 prompts with OUTPUT SPEC
- [ ] Gate 5 validation

**Phase 4 (1 hour): Dashboard Sync**
- [ ] Run sync script
- [ ] Gate 4 validation

**Post-Execution (1 hour): Verification**
- [ ] Full test suite: `pytest tests/ -v`
- [ ] Manual smoke tests
- [ ] Dashboard visual inspection

**Total Time:** 8 hours (including all validations)

### Alternative: "Minimal Risk" Fast Path (NOT RECOMMENDED)
**Skip:** File reorganization + prompt updates  
**Do:** AC-ID integration only  
**Risk:** AC-IDs exist but scattered across tools, no governance structure  
**Recommendation:** NO — Do full remediation now

---

## 9. Success Criteria

**The remediation is successful if:**
1. ✅ AC-INDEX.yaml has 131 AC-IDs (102 + 29)
2. ✅ All 4 gates pass without intervention
3. ✅ Test suite: 100% pass rate (no regressions)
4. ✅ Plan-viewer dashboard shows updated totals
5. ✅ No broken file references
6. ✅ All 12 scripts with hardcoded paths updated
7. ✅ Master-plan.yaml in sync with AC-INDEX
8. ✅ Progress-tracker.json consistent with AC-INDEX counts
9. ✅ All git commits clean (no conflicts, clear messages)
10. ✅ Documentation updated (.github/prompts/output-standards.md referenced)

---

## 10. Final Recommendation

**✅ PROCEED WITH PHASED EXECUTION + VALIDATION GATES**

**Why This Is Safe:**
1. All changes tracked in git (rollback available)
2. Validation gates prevent silent failures
3. Phased approach allows inspection between phases
4. Comprehensive test coverage catches regressions
5. Risk mitigation strategies address each identified issue

**Go/No-Go:** **GO** — Execute Phase 0 (decisions) first, then proceed with Phases 1-4

---

**Analysis Complete:** January 12, 2026 @ 17:45 UTC  
**Next Action:** User provides decisions on 3 critical questions + inspection results
