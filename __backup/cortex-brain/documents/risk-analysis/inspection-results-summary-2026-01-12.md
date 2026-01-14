# Risk Analysis Inspection Results Summary
**Date:** January 12, 2026  
**Status:** ✅ INSPECTION COMPLETE — Ready for User Decision

---

## Critical Findings from Automated Inspection

### Finding #1: HTML Hardcoding (HIGH RISK CONFIRMED ⚠️)
**Status:** 🔴 **CRITICAL** — Must be fixed before AC-ID integration

**Locations Found:** 3 hardcoded percentages in `cortex-plan-viewer.html`
```html
✓ Phase 1: 48% (hardcoded in badge)
✓ Phase 1.5: 85% (hardcoded in badge)  
✓ Chart labels with all phases + percentages (hardcoded array)
```

**Why It Matters:**
- After integrating 29 new AC-IDs (102→131), these percentages become **WRONG**
- Users see stale UI (48%) vs. new data (whatever actual % is)
- Undermines trust in dashboard

**Fix Required:** Remove hardcoding, use API calls to `plan-viewer-data.json`

---

### Finding #2: AC-INDEX Consumer Code Mismatch (HIGH RISK CONFIRMED ⚠️)
**Status:** 🔴 **CRITICAL** — Must be fixed before AC-INDEX integration

**Problem Found:**
- `atomic_state_manager.py` looks for AC-IDs in `acceptance_criteria` section
- `brittleness_validator.py` looks for AC-IDs in `acceptance_criteria` section
- **Current AC-INDEX has EMPTY `acceptance_criteria` section** — all real data in `foundation`

**Result:** AC status updates will **SILENTLY FAIL** (no error, no update)

**Fix Required:** Update 2 files to use `foundation` section instead

---

### Finding #3: File Path Hardcoding (MEDIUM RISK CONFIRMED ⚠️)
**Status:** 🟡 **WARNING** — Will break file organization if not fixed first

**Affected Scripts:** 4 files
```
✓ scripts/analyze_untracked_files.py
✓ scripts/capture_build_evidence.py
✓ scripts/consolidate_cx6_plan.py
✓ scripts/deep_structure_scan.py
```

**Problem:** All use hardcoded `cortex-brain/documents/reports/` path

**Result:** If we move files to `cortex-brain/documents/reports/brittleness/`, these 4 scripts break

**Fix Required:** Centralize paths in module, update 4 scripts

---

## Revised Execution Plan (Phases 0-4)

### Phase 0: Prep (30 min) — BEFORE ANY EXECUTION
1. **User decisions needed:**
   - [ ] Approve CORE-022 32-char exception for date-versioned files?
   - [ ] Assign 29 brittleness AC-IDs to Phase 1.5?
   - [ ] Proceed with full remediation?

2. **Code fixes required (BLOCKING):**
   - [ ] Fix HTML hardcoding in `cortex-plan-viewer.html` (2 badges + chart labels)
   - [ ] Fix AC-INDEX consumers in `atomic_state_manager.py` + `brittleness_validator.py`
   - [ ] Create centralized paths module for scripts

### Phase 1: File Organization (2 hours)
- Use centralized paths module
- Move/rename files
- Update 4 affected scripts
- Gate 3 validation

### Phase 2: AC-ID Integration (1.5 hours)
- Append 29 AC-IDs to AC-INDEX
- Gate 1 validation
- Update master-plan.yaml totals
- Gate 2 validation

### Phase 3: Prompt Updates (1.5 hours)
- Update 4 prompts with OUTPUT SPEC
- Gate 5 validation

### Phase 4: Dashboard Sync (1 hour)
- Run sync_plan_viewer_data.py
- Gate 4 validation

### Post-Execution: Verification (1 hour)
- Full test suite
- Manual smoke tests
- Git history review

**Total Time:** 9 hours (including 3 blocking code fixes)

---

## Key Differences from Original Plan

| Item | Original | Updated | Reason |
|------|----------|---------|--------|
| Number of issues | 3 | 5 | Inspection revealed 2 additional HIGH risks |
| Blocking fixes | 0 | 3 | HTML, consumer code, paths |
| Total time | 8 hours | 9 hours | 3 code fixes + validation overhead |
| Risk level | MEDIUM | **MEDIUM-HIGH** | HTML hardcoding is significant |
| Phase 0 | 0 min | 30 min | Must fix blockers first |
| Phase 1 | 2 hours | 2 hours | Same (but uses centralized paths) |
| Phase 1.5 | N/A | NEW | Remove HTML hardcoding |
| Phase 2 | 1 hour | 1.5 hours | +30 min for consumer code fixes |

---

## Critical Path Dependencies

```
Decision Phase (30 min)
    ↓
Fix HTML Hardcoding (1 hour)
    ↓
Fix AC-INDEX Consumers (30 min)
    ↓
Create Path Module (30 min)
    ↓ (can proceed in parallel)
┌─── Phase 1: File Organization (2 hours)
├─── Phase 2: AC-ID Integration (1.5 hours)
├─── Phase 3: Prompt Updates (1.5 hours)
└─── Phase 4: Dashboard Sync (1 hour)
    ↓
Post-Execution Verification (1 hour)
```

**Estimate:** 9 hours total (with 4 hours of prep/blocking work)

---

## What Could Still Break (Residual Risks)

Even with all mitigations, these have non-zero failure probability:

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|-----------|
| Test fixture schema mismatch | 15% | Tests fail (rollback easy) | Update fixtures before running |
| Dashboard API endpoint missing | 10% | HTML can't fetch data | Check endpoint exists in dashboard/ |
| Master plan syntax error | 5% | YAML parse fails (rollback easy) | Validate YAML before commit |
| Prompt references outdated file | 5% | Prompt broken (rollback easy) | Test prompt execution |

**Residual Risk Level:** 🟡 **LOW-MEDIUM** (all rollbackable)

---

## Go/No-Go Decision Points

**✅ SAFE TO PROCEED IF:**
1. ✅ User approves 3 decisions
2. ✅ HTML hardcoding removed + tested
3. ✅ AC-INDEX consumers updated + tested
4. ✅ Centralized paths module created + tested
5. ✅ All 5 validation gates pass

**🛑 DO NOT PROCEED IF:**
1. ❌ Any blocking fixes fail tests
2. ❌ User rejects Phase 1.5 (HTML fix)
3. ❌ Centralized paths don't resolve correctly
4. ❌ Git history has uncommitted changes (dirty state)

---

## Next Steps for User

**Option 1: Approve Full Execution** (9 hours total)
- Provide 3 decisions
- Let agent execute Phases 0-4 with gates
- Review final state before merge

**Option 2: Phased Approval** (Recommended)
- Approve Phase 0 (decisions) first
- Review blocking fixes (30 min)
- Then approve Phase 1-4 execution
- Ability to pause/adjust between phases

**Option 3: Inspect Blocking Fixes First** (Safe)
- Agent creates 3 blocking fix PRs
- User reviews + approves each
- Then execute Phases 1-4

**Recommendation:** **Option 2** — Phased approval gives visibility into blocking fixes

---

**Risk Analysis Complete**  
**Inspection Status:** ✅ DONE  
**Blocking Fixes Identified:** ✅ 3 (quantified + documented)  
**Validation Gates Ready:** ✅ 5 (ready to implement)  
**Rollback Plan:** ✅ IN PLACE (<5 min)  

**Awaiting User Decision:** 3 critical decisions + approval to proceed
