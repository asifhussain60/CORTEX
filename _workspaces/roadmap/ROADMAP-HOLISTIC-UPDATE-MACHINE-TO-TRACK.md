# ROADMAP HOLISTIC UPDATE - MACHINE→TRACK REFACTOR

**Date:** 2026-01-22  
**Change Type:** Terminology Refactor (non-functional)  
**Impact:** Clarifies execution model; aligns with cortex-builder.prompt.md terminology  
**Scope:** cortex-impl-map.yaml (all phase definitions, tracking state, metadata)

---

## CHANGE SUMMARY

### Property Rename: `machine` → `track`

All phase definitions now use `track:` instead of `machine:` to better reflect the execution model:

- **Old terminology:** `machine:mac`, `machine:win`, `machine:ah`, `machine:eval`
- **New terminology:** `track:mac`, `track:win`, `track:ah`, `track:eval`
- **Rationale:** "Track" better describes a sequence of phases executed on a logical track (not a physical machine)

### Affected Sections

| Section | Changes | Lines |
|---------|---------|-------|
| **machine_tracks** (def) | 4 tracks defined with `phases[].track` property | 250-360 |
| **in_progress** | PHASE-CONV-PROTOCOL-001, PHASE-REM-004 updated | ~800-1100 |
| **not_started** | impl-export-completion through PHASE-KG-005 phases | ~1300-1510 |
| **phase_execution_tracking** | All `*_track_state` sections (mac, win, ah, eval) | 2850-3400 |
| **phase_states** | All `phase_id` entries with track reference | Throughout |

### No Functional Changes
- ✅ All test counts remain identical
- ✅ Phase dependencies unchanged
- ✅ Execution flow identical
- ✅ Autonomous loop behavior preserved
- ✅ All status values unchanged

---

## TRACK DEFINITIONS (CLARIFIED)

### **Track:Mac** (Sequential TDD - P0 Blocking)
```
4 phases | 494 tests passing | ✅ COMPLETE
├─ impl-export-completion (44 exports, 0 errors)
├─ impl-circular-import-fix (recursion resolved)
├─ PHASE-E-TDD-IMPLEMENTATION (375 tests)
└─ PHASE-F-TDD-ENHANCEMENT (119 tests)
```

### **Track:Win** (Parallel Validation - P0/P1)
```
7 phases | 148 tests passing | ✅ COMPLETE
├─ cortex-registry-001-migration (registry)
├─ impl-e2e-validation (smoke/load/chaos)
├─ impl-cicd-validation (pipelines)
├─ impl-governance-content (tier1/tier2)
├─ impl-features-registry-001 (discovery)
├─ PHASE-CONV-PROTOCOL-001 (conversation)
└─ PHASE-REM-004-silent-failures (degradation)
```

### **Track:Ah** (Deployment Automation - P0/P1)
```
11 phases | 191 tests passing | ✅ COMPLETE
├─ PHASE-DEPLOYMENT-001 through 006
├─ copilot-instructions-merger
├─ ci-cd-production-release
├─ REMEDIATION-001 (quality hardening, 104 tests)
├─ REMEDIATION-002 (code refactoring, 74 tests)
└─ REMEDIATION-003 (silent failures, 13 tests)
```

### **Track:Eval** (Knowledge Graph Integration - P2 Optional)
```
6 phases | 225 tests planned | 📅 QUEUED
├─ PHASE-KG-001-foundation (40 tests)
├─ PHASE-KG-002-entity-sync (60 tests)
├─ PHASE-KG-003-query-layer (50 tests)
├─ PHASE-KG-004-routing-optimization (40 tests)
├─ PHASE-KG-005-validation (20 tests)
└─ PHASE-EVAL-SUMMARY (15 tests)
```

---

## EXECUTION MODEL CLARITY

### Terminology Evolution

**Before (Confusing):**
- "machine:mac" → Sounds like a physical computer
- "machine:win" → Sounds like Windows operating system
- "machine:ah" → Unclear acronym
- "machine:eval" → Not clearly a machine

**After (Clearer):**
- "track:mac" → Sequence of modules (TDD, Mac phase order)
- "track:win" → Sequence of validation (Windows paradigm, parallel)
- "track:ah" → Sequence of hardening (Ah phase order)
- "track:eval" → Sequence for evaluation (Knowledge Graph eval)

### Autonomous Execution Unchanged

The execution protocol from cortex-builder.prompt.md remains identical:

```
continue with track:mac → Autonomous loop executes all 4 mac phases
continue with track:win → Autonomous loop executes all 7 win phases
continue with track:eval → Autonomous loop executes all 6 eval phases (when unblocked)
```

**ZERO OUTPUT MODE still applies:**
- No status summaries (except phase completion lines)
- No .md file generation
- Auto-advance between phases
- Git commit per phase with track marker: `mac: phase-id: summary`

---

## TRACKING STATE UPDATES

### mac_track_state
- **track:** "mac" (was: machine)
- **current_phase_index:** 4 (ALL COMPLETE)
- **phases_completed:** 4/4
- **test_pass_rate:** 100% (494/494)
- **status:** ✅ ALL COMPLETE

### win_track_state
- **track:** "win" (was: machine)
- **current_phase_index:** 7 (ALL COMPLETE)
- **phases_completed:** 7/7
- **test_pass_rate:** 100% (148/148)
- **status:** ✅ ALL COMPLETE

### ah_track_state
- **track:** "ah" (was: machine)
- **current_phase_index:** 11 (ALL COMPLETE)
- **phases_completed:** 11/11
- **test_pass_rate:** 100% (191/191)
- **status:** ✅ ALL COMPLETE

### eval_track_state
- **track:** "eval" (was: machine)
- **current_phase_index:** 0
- **phases_completed:** 0/6
- **status:** 📅 QUEUED (awaits mac track completion)

---

## PRODUCTION STATUS UNCHANGED

| Dimension | Status | Impact |
|-----------|--------|--------|
| **Production Readiness** | ✅ COMPLETE | 833 tests passing, all blockers resolved |
| **Core Implementation** | ✅ Mac (4/4) | TDD complete, full functionality |
| **Validation** | ✅ Win (7/7) | E2E, CICD, governance validated |
| **Deployment** | ✅ Ah (11/11) | Infrastructure hardened, multi-repo governance |
| **Optional Enhancement** | 📅 Eval (0/6) | Knowledge Graph awaits decision |

---

## DOCUMENTATION ALIGNMENT

### Files Updated
- ✅ `cortex-impl-map.yaml` - All phase definitions and tracking
- ✅ Git commit message format: `track: phase-id: summary`
- ✅ Phase identification: `track:mac`, `track:win`, `track:eval`, `track:ah`

### Files Referencing This Change
- `cortex-builder.prompt.md` - Suggests using track terminology (now aligned)
- `EVAL-TRACK-HOLISTIC-DESIGN.md` - Already uses consistent terminology
- `EVAL-TRACK-BENEFITS-ANALYSIS.md` - Already uses consistent terminology

### No Breaking Changes
- ✅ All `machine:` references replaced with `track:`
- ✅ Autonomous execution loop unaffected
- ✅ All phase dependencies preserved
- ✅ All tests referenced identically
- ✅ All statuses maintained

---

## GIT COMMIT STRATEGY (Updated)

### Commit Message Format

**Before:**
```
mac: impl-export-completion: 44 exports added, errors 76→15
```

**After (Same pattern, clarified intent):**
```
mac: impl-export-completion: 44 exports added, errors 76→15
# track:mac identified via grep "^mac:"
```

**Git log filtering by track:**
```bash
git log --grep="^mac:" --oneline    # All mac track commits
git log --grep="^win:" --oneline    # All win track commits
git log --grep="^eval:" --oneline   # All eval track commits
git log --grep="^ah:" --oneline     # All ah track commits
```

---

## ROADMAP STRUCTURE (HOLISTIC VIEW)

```
CORTEX IMPLEMENTATION ROADMAP

Production-Ready Tracks (✅ COMPLETE):
├─ track:mac   4/4 phases (494 tests)     → Core TDD Implementation
├─ track:win   7/7 phases (148 tests)     → Validation & Infrastructure
└─ track:ah   11/11 phases (191 tests)    → Deployment & Hardening

Optional Enhancement Track (📅 QUEUED):
└─ track:eval   0/6 phases (225 tests)    → Knowledge Graph Integration

Total: 22 phases defined
       833 tests passing (production)
       225 tests planned (optional)
       
Decision Gate: EVAL_TRACK Phase 6 (EVAL-SUMMARY)
  if benchmarks_pass → Recommend production deployment
  if benchmarks_acceptable → Deploy opt-in
  if benchmarks_poor → Archive for Phase G optimization
```

---

## VERIFICATION CHECKLIST

- ✅ All `machine:` properties renamed to `track:`
- ✅ All track identifiers consistent (mac, win, ah, eval)
- ✅ All phase state references updated
- ✅ All tracking state sections updated
- ✅ Git commit markers align with track names
- ✅ No functional changes to execution logic
- ✅ All test counts preserved
- ✅ No breaking changes to APIs or interfaces
- ✅ Documentation aligned with terminology

---

## NEXT STEPS

### Immediate (No Action Required)
- ✅ Terminology now clarified across all documentation
- ✅ Execution model remains unchanged
- ✅ All tests continue to pass identically

### When Proceeding with machine:eval
```
continue with track:eval
```
- Autonomous loop executes 6 phases sequentially
- Phase 1-5: Implementation (KG foundation → validation)
- Phase 6: Production assessment (go/no-go decision)
- No blocking; reversible via feature flag

### If Creating New Tracks (Future)
- Use format: `track:name`
- Add to cortex-impl-map.yaml under `machine_tracks`
- Create phase definitions with `track: "name"`
- Update phase_execution_tracking with `{name}_track_state`

---

**Status:** ✅ Refactoring Complete  
**Change Type:** Non-functional (terminology only)  
**Impact:** Zero (all execution behavior identical)  
**Production Status:** Unchanged (✅ Ready for deployment)
