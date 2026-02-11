# WAVE 7 TRACK 4: SUPPORT ELIMINATION - DECISION POINT

**Date:** 2026-02-11 | **Token Budget:** Approaching limit | **Status:** Planning checkpoint

---

## 📊 Wave 7 Status After Track 3

| Metric | Value | Target |
|--------|-------|--------|
| **Tests** | 168/275 (61%) | 275 (100%) |
| **Tests/Day** | 7-8 tests/day | 10-12 tests/day |
| **Estimated Total Days** | 28-40 days | 20-25 days |
| **Commits** | 10 commits | 15-18 commits |
| **Code Quality** | 100% governance | 100% governance ✅ |

---

## 🎯 Track 4 Three Options

### **OPTION A: Full Track 4 - Comprehensive (Recommended)**
**Duration:** 3-5 days | **Tests:** +20-25 | **Orchestrators:** 26 → 15 (42% reduction) ✅

**Scope:**
1. **Phase 1:** Deprecation mapping (identify 7-8 targets)
2. **Phase 2:** Create deprecation wrappers with import redirects
3. **Phase 3:** Update wiring contract + deprecation registry
4. **Phase 4:** Comprehensive deprecation tests + validation

**Targets for Deprecation:**
- `CodeReviewOrchestrator` → Merge into QualityAssuranceOrchestrator
- `SecurityReviewEngine` → Merge into QualityAssuranceOrchestrator
- `RefactoringOrchestrator` → Merge into TDDOrchestrator
- `MetaAuditOrchestrator` → Remove wrapper layer
- `ChallengeEngine` → Remove wrapper layer
- `RecommendationGate` → Remove wrapper layer
- `LegacyAnalysisOrchestrator` → Mark deprecated
- (1 additional candidate TBD)

**Success Criteria:**
- ✅ All 7-8 deprecated orchestrators have redirects
- ✅ No breaking changes (backward compatible)
- ✅ 20-25 new tests (deprecation coverage)
- ✅ Full test suite passes (Track 1-4 combined)
- ✅ Wiring updated (26 → 15 shown)

**Impact:**
- Wave 7: 168 → 193-218 tests (70-79% complete)
- Orchestrator consolidation: 15% → 42% reduction achieved
- Ready for Track 5 immediately

---

### **OPTION B: Minimal Track 4 - Focused (Time-Boxed)**
**Duration:** 1 day | **Tests:** +10-12 | **Orchestrators:** 26 → 20 (23% reduction)

**Scope:**
- Deprecation mapping only (no full implementation)
- Create deprecation wrappers for top 3-4 high-impact orchestrators
- Minimal test coverage (redirect tests only)
- Deferred wiring update (can do later)

**Targets:**
- `LegacyAnalysisOrchestrator` → `UnifiedAnalysisOrchestrator`
- `RefactoringOrchestrator` → `TDDOrchestrator`
- `MetaAuditOrchestrator` → `QualityAssuranceOrchestrator`

**Impact:**
- Wave 7: 168 → 178-180 tests (65% complete)
- Quick progress, can extend later if needed

---

### **OPTION C: Skip Track 4 - Fast-Track to Track 5**
**Duration:** 0 days | **Tests:** +0 | **Orchestrators:** stays 22 (15% reduction)

**Rationale:**
- Track 3 consolidation complete (67/67 tests passing)
- Move directly to Track 5 (LENS Physical Tests - 50-75 new tests)
- Return to Track 4 after Track 5 if time permits
- Wave 7 focus on depth (test coverage) vs. breadth (orchestrator count)

**Impact:**
- Wave 7: 168 → 218-243 tests (79-88% complete)
- Skips deprecation maintenance, focuses on new features
- Defers 42% orchestrator target, but achieves 70%+ test coverage

---

## 📈 Wave 7 Timeline Impact

| Option | Track 4 Time | Total Wave 7 Time | Final Tests | Orchestrators |
|--------|-------------|------------------|-------------|----------------|
| **A** | 3-5 days | 31-45 days | 193-218 | 15/26 ✅ |
| **B** | 1 day | 27-41 days | 178-203 | 20/26 |
| **C** | 0 days | 24-40 days | 218-243 | 22/26 |

---

## 🎯 Recommendation Matrix

**Choose OPTION A if:**
- ✅ You want to achieve 42% orchestrator reduction (Wave 7 PRIMARY goal)
- ✅ You have 3-5 additional days available
- ✅ Quality + infrastructure consolidation is priority
- ✅ You want clean wiring contract post-Track-4

**Choose OPTION B if:**
- ✅ You have limited time (1-2 days max)
- ✅ Quick progress needed for momentum
- ✅ Can return to deprecation later
- ✅ Minimal disruption preferred

**Choose OPTION C if:**
- ✅ Maximum test coverage is priority (218-243 tests)
- ✅ Orchestrator count is secondary concern
- ✅ Want to complete full test suite quickly
- ✅ Deprecation can be handled post-Wave-7

---

## 🎪 Technical Debt Assessment

**If Track 4 Skipped:**
- Deferred: Deprecation wrapper cleanup (5-10 tests)
- Deferred: Wiring contract consolidation (1 commit)
- Benefit: 50-75 new LENS tests in Track 5
- Risk: May need to revisit orchestrator cleanup later

**If Track 4 Completed (Option A):**
- Cleaned: 7-8 deprecated orchestrators properly flagged
- Wiring: Contract updated and validated
- Tests: 20-25 new deprecation tests
- Maintenance: Clear migration path for dependent code

---

## ⚠️ Token Budget Alert

**Current Status:** Session approaching token limit
**Recommendation:** 
1. Choose option (A/B/C)
2. Commit checkpoint
3. Provide continuation prompt for next session if needed

**Tokens Available:** ~90k remaining (sufficient for Track 4 Phase 1)

---

## 🔄 Next Steps

**If OPTION A chosen:**
```bash
1. Run Track 4 Phase 1: Deprecation mapping + candidate identification
2. Create deprecation wrapper files (cortex/orchestrators/deprecated/)
3. Update imports and redirect tests
4. Execute full test suite
```

**If OPTION B chosen:**
```bash
1. Focus on top 3 highest-impact orchestrators
2. Create redirect tests only
3. Validate no breaking changes
4. Commit and move to Track 5
```

**If OPTION C chosen:**
```bash
1. Skip to Track 5 immediately
2. Execute LENS Physical Tests (50-75 tests)
3. Return to Track 4 deprecation if time remains
4. Focus on test coverage % (goal: 80%+)
```

---

## 📋 Checkpoint Saved

This document serves as a continuation checkpoint. When resuming:
1. Load this decision document
2. Choose preferred option
3. Begin Track 4 Phase 1 or skip directly to Track 5

**Files Created:**
- ✅ `/tmp/wave7_track4_strategic_plan.md` (full Track 4 strategy)
- ✅ `docs/WAVE-7-TRACK-4-DECISION.md` (this file - decision point)

**Last Session State:**
- Track 3: ✅ 67/67 tests PASSED (100%)
- Wave 7: 168/275 tests (61% complete)
- Ready for Track 4 Phase 1 execution

---

**Decision Needed:** Which option (A/B/C) should Wave 7 pursue?
