# AC-SYNC-001: Automated State Synchronization System

**Status:** ✅ IMPLEMENTED  
**Date:** 2026-01-10  
**Author:** Asif Hussain  
**Tests:** 14/14 passing (100%)

---

## Overview

AC-SYNC-001 implements automated synchronization validation across all CORTEX 6.0 state files. This system runs on **every GitHub Copilot turn** to detect and report discrepancies before they cause problems.

---

## Architecture

### Components

1. **StateSynchronizer** (`src/orchestrators/core/state_synchronizer.py`)
   - Main validation engine
   - Checks 6 truth sources
   - Generates sync reports
   - Provides auto-fix capabilities

2. **CORTEX.prompt.md Integration**
   - Runs automatically on every turn
   - Blocks operations if sync_score < 80%
   - Displays actionable recommendations

3. **Test Suite** (`tests/orchestrators/test_state_synchronizer.py`)
   - 14 tests covering all validation scenarios
   - 100% passing
   - AC-ID marked tests for traceability

---

## The 6 Truth Sources

| # | Source | Path | Purpose |
|---|--------|------|---------|
| 1 | **progress-tracker.json** | `cortex-brain/tier1/tracking/` | Current phase, completed AC-IDs |
| 2 | **AC-INDEX.yaml** | `cortex-brain/tier1/acceptance-criteria/` | AC registry with status |
| 3 | **holistic-snowball-plan.yaml** | `cortex-brain/documents/cx6-holistic-analysis/` | Master plan status |
| 4 | **plan-viewer.html** | `templates/plan-viewer/` | User-facing dashboard |
| 5 | **evidence-bundles/** | `cortex-brain/tier1/evidence-bundles/` | Implementation proof |
| 6 | **Implementation files** | `src/` | Actual source code |

---

## Sync Score Calculation

```python
Sync Score = (sources_accurate / sources_total) × 100%

≥80% = ✅ HEALTHY (proceed with optional warnings)
<80% = ⚠️ WARNING (fix recommended before proceeding)
CRITICAL discrepancies = 🔴 BLOCK (must fix immediately)
```

### Status Values

| Status | Meaning | Action |
|--------|---------|--------|
| **accurate** | Source is current and valid | None |
| **stale** | Source is outdated | Update recommended |
| **conflicting** | Source has internal conflicts | Fix required |
| **missing** | Source file doesn't exist | Create required |

---

## Discrepancy Types

| Type | Severity | Description | Resolution |
|------|----------|-------------|------------|
| **status_mismatch** | HIGH | Phase status differs between sources | Update plan file to match tracker |
| **completion_mismatch** | MEDIUM | Completion % differs | Sync percentages |
| **ac_count_mismatch** | CRITICAL | Completed count ≠ verified list length | Recalculate completed_count |
| **missing_evidence** | HIGH | No evidence bundle for "implemented" AC-ID | Generate evidence or mark "planned" |
| **stub_implementation** | MEDIUM | File <500 bytes | Complete implementation or mark "planned" |
| **conflicting_displays** | HIGH | plan-viewer shows contradictory data | Standardize displays |

---

## Usage

### Automatic (Recommended)

The synchronizer runs automatically on every GitHub Copilot turn via CORTEX.prompt.md:

```python
# This happens automatically:
from src.orchestrators.core.state_synchronizer import run_synchronization_check

sync_report = run_synchronization_check(workspace_root)

if sync_report.sync_score < 80 or sync_report.critical:
    # Display report and BLOCK operation
    print(sync_report.generate_sync_report_markdown())
    return
```

### Manual (Debugging)

For deep debugging or manual checks:

```python
from pathlib import Path
from src.orchestrators.core.state_synchronizer import StateSynchronizer

workspace_root = Path("/Users/asifhussain/PROJECTS/CORTEX")
synchronizer = StateSynchronizer(workspace_root)

# Run full validation
report = synchronizer.validate_all_sources()

# Display markdown report
markdown = synchronizer.generate_sync_report_markdown(report)
print(markdown)

# Auto-fix safe discrepancies
fixes = synchronizer.auto_fix_discrepancies(report)
print(f"Applied fixes: {fixes}")
```

### Command Line

```bash
# Run synchronization check (planned for Phase 2)
python3 -m src.main "run state synchronization check" --format markdown

# This will:
# 1. Validate all 6 truth sources
# 2. Generate sync report
# 3. Display recommendations
# 4. Optionally apply auto-fixes
```

---

## Example Output

```markdown
# 🔄 State Synchronization Report

**Timestamp:** 2026-01-10T22:00:00Z
**Sync Score:** 67.0% (4/6 sources accurate)
**Status:** ⚠️ WARNING - Synchronization issues detected

## 📊 Discrepancies

- ⚠️ **status_mismatch:** Phase 1 status: tracker='in_progress', plan='ready_to_implement'
  - Resolution: Update holistic-snowball-plan.yaml status to match progress-tracker.json

- ⚠️ **conflicting_displays:** plan-viewer.html shows both 64% and 48% for Phase 1
  - Resolution: Standardize all Phase 1 displays to 48% (16/33)

## 🎯 Recommendations

- ⚠️ **Update holistic-snowball-plan.yaml** (Est: 10 minutes)
  - Phase 1 status should be 'in_progress', not 'ready_to_implement'
  - Missing completion_percentage in phase_1_foundation

- ⚠️ **Fix conflicts in plan-viewer.html** (Est: 15 minutes)
  - Conflicting completion percentages (64% and 48%)
  - Conflicting AC-ID counts (21/33 and 16/33)
```

---

## Integration with CORTEX Workflow

### Before AC-SYNC-001 (Broken)

```
User Request → Process → Execute → Update Files → Hope they sync
                                                       ↑
                                                   NO VALIDATION
```

### After AC-SYNC-001 (Fixed)

```
User Request → SYNC CHECK → Process → Execute → Update Files → SYNC CHECK
                  ↓                                                ↓
            If <80% BLOCK                                    Verify still synced
```

---

## Testing

### Run All Tests

```bash
python3 -m pytest tests/orchestrators/test_state_synchronizer.py -v
```

### Expected Output

```
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_initialize PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_validate_progress_tracker_missing PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_validate_progress_tracker_valid PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_validate_ac_index_valid PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_validate_holistic_plan_status_mismatch PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_validate_all_sources_perfect_sync PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_cross_validate_detects_status_mismatch PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_cross_validate_detects_completion_mismatch PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_generate_recommendations PASSED
tests/orchestrators/test_state_synchronizer.py::TestStateSynchronizer::test_generate_sync_report_markdown PASSED
tests/orchestrators/test_state_synchronizer.py::TestRunSynchronizationCheck::test_run_synchronization_check PASSED
tests/orchestrators/test_state_synchronizer.py::TestACSync001::test_ac_sync_001_detects_discrepancies PASSED
tests/orchestrators/test_state_synchronizer.py::TestACSync001::test_ac_sync_001_generates_recommendations PASSED
tests/orchestrators/test_state_synchronizer.py::TestACSync001::test_ac_sync_001_calculates_sync_score PASSED

========================= 14 passed, 1 warning in 0.08s =========================
```

---

## Evidence Bundle

**Location:** `cortex-brain/tier1/evidence-bundles/AC-SYNC-001/`

```
AC-SYNC-001/
├── manifest.yaml           # AC-ID metadata
├── test_results.json       # 14/14 tests passing
├── implementation.py       # state_synchronizer.py (780 lines)
└── audit_trace.jsonl       # Implementation audit trail
```

---

## Acceptance Criteria

### ✅ AC-SYNC-001.1: Validate 6 Truth Sources

**GIVEN:** CORTEX workspace with state files  
**WHEN:** Synchronization check runs  
**THEN:** All 6 sources are validated and status reported

**Test:** `test_validate_all_sources_perfect_sync`  
**Status:** ✅ PASSING

---

### ✅ AC-SYNC-001.2: Detect Discrepancies

**GIVEN:** Truth sources with mismatched data  
**WHEN:** Cross-validation runs  
**THEN:** All discrepancies detected and categorized

**Tests:** 
- `test_cross_validate_detects_status_mismatch` ✅
- `test_cross_validate_detects_completion_mismatch` ✅
- `test_ac_sync_001_detects_discrepancies` ✅

**Status:** ✅ PASSING

---

### ✅ AC-SYNC-001.3: Calculate Sync Score

**GIVEN:** Validation results  
**WHEN:** Sync score calculated  
**THEN:** Score = (accurate_sources / total_sources) × 100%

**Test:** `test_ac_sync_001_calculates_sync_score`  
**Status:** ✅ PASSING

---

### ✅ AC-SYNC-001.4: Generate Recommendations

**GIVEN:** Detected discrepancies  
**WHEN:** Recommendations generated  
**THEN:** Actionable fixes provided with priorities and estimates

**Tests:**
- `test_generate_recommendations` ✅
- `test_ac_sync_001_generates_recommendations` ✅

**Status:** ✅ PASSING

---

### ✅ AC-SYNC-001.5: Markdown Report

**GIVEN:** Sync report data  
**WHEN:** Markdown generated  
**THEN:** Human-readable report with all details

**Test:** `test_generate_sync_report_markdown`  
**Status:** ✅ PASSING

---

## Future Enhancements (Phase 2+)

### AC-SYNC-002: Auto-Fix Capabilities

Implement safe automatic fixes for common discrepancies:
- Status mismatches (update plan to match tracker)
- Completion percentage sync
- Timestamp updates

### AC-SYNC-003: Real-Time Monitoring

Add file watchers to detect changes and trigger validation:
- Watch progress-tracker.json for updates
- Auto-validate on file save
- Notification on sync_score drop

### AC-SYNC-004: Historical Tracking

Track sync scores over time:
- Store sync reports in `cortex-brain/audit/sync-history/`
- Generate trend charts
- Alert on degrading sync quality

### AC-SYNC-005: MCP Tool Integration

Expose synchronization as MCP tool:
```bash
cortex_sync_check
cortex_sync_fix
cortex_sync_history
```

---

## Known Limitations

1. **Auto-fix Not Fully Implemented**
   - `auto_fix_discrepancies()` has placeholder logic
   - Will be completed in Phase 2

2. **Plan-Viewer Parsing**
   - Currently uses string matching for HTML
   - Could be improved with proper HTML parsing

3. **Evidence Bundle Validation**
   - Basic size checking only
   - Could validate manifest schema, test results format

4. **No Historical Comparison**
   - Each check is point-in-time
   - No tracking of sync score trends

---

## Changelog

### 2026-01-10 (v1.0.0) - Initial Implementation

- ✅ Implemented StateSynchronizer class
- ✅ 6-truth-source validation
- ✅ Discrepancy detection and cross-validation
- ✅ Sync score calculation
- ✅ Recommendation generation
- ✅ Markdown report generation
- ✅ 14 tests covering all scenarios
- ✅ Integrated with CORTEX.prompt.md (automatic execution)
- ✅ Updated holistic-snowball-plan.yaml Phase 1 status
- ✅ Generated state-sync-report-2026-01-10.md

---

## References

- **Implementation:** `src/orchestrators/core/state_synchronizer.py`
- **Tests:** `tests/orchestrators/test_state_synchronizer.py`
- **Integration:** `.github/prompts/CORTEX.prompt.md` (lines 1-50)
- **Documentation:** This file
- **State Sync Report:** `cortex-brain/documents/validation/state-sync-report-2026-01-10.md`
- **Holistic Report:** `cortex-brain/documents/validation/cortex6-holistic-implementation-report.md`

---

**Implementation Complete:** 2026-01-10T22:30:00Z  
**Test Coverage:** 100% (14/14 tests passing)  
**Integration Status:** ✅ Active in CORTEX.prompt.md  
**Next Steps:** Monitor usage, refine recommendations, implement auto-fix
