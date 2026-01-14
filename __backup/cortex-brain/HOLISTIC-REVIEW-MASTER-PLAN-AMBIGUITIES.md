# 🔍 HOLISTIC REVIEW: Master-Plan.yaml Ambiguities & Root Cause Analysis

**Status:** CRITICAL - Circular dependency problem identified  
**Date:** 2026-01-13  
**Author:** GitHub Copilot  
**Severity:** BLOCKER - Causing infinite loops and hallucinations

---

## 📋 EXECUTIVE SUMMARY

The master-plan.yaml has **9 CRITICAL AMBIGUITIES** causing circular implementation attempts and hallucinations:

1. **Missing Phases 6-9:** 4 phases completely undefined (should have ~100+ ACs)
2. **Invalid Phase Names:** 1.5, 4.5 are intermediate phases (non-standard, confusing)
3. **AC Count Mismatch:** 110 ACs in AC-INDEX but only 110 in master-plan (looks complete but 6-9 missing)
4. **Phase 3 Content:** Only 1 AC-ID (evidence bucket), should have 30+ ACs for feature orchestrators
5. **Phase 4-5 Skeleton:** Only 1 AC-ID each (evidence buckets), no actual implementation ACs
6. **Completed Count Zero:** All phases show `completed_ac_count: 0` (stale data)
7. **Target Dates Invalid:** All phases have same target: "2026-02-01" (unrealistic)
8. **SSOT Contradiction:** Progress-tracker shows 100% complete but master-plan shows all 0%
9. **Phase Sequencing Broken:** Actual execution is CORTEX-1 through CORTEX-5.5 legacy code; CORTEX-6 plan is incomplete

---

## 🔗 ROOT CAUSE: HALLUCINATION CYCLE

```
User asks "implement Phase 3" 
  ↓
Copilot reads master-plan.yaml 
  ↓
Finds Phase 3 has only 1 AC-ID (evidence bucket) + no feature orchestrator ACs
  ↓
Copilot HALLUCINATES Phase 3 should have ADO, Vacuum, Crawler ACs
  ↓
Generates fake progress (100% complete on missing phases)
  ↓
Progress-tracker corrupted with false data
  ↓
Next user query sees contradiction: "Phase 3 says 100% but also 'not started'"
  ↓
Copilot attempts to REPAIR by regenerating tracker
  ↓
Cycle repeats → INFINITE LOOP
```

---

## 📊 DETAILED AMBIGUITY ANALYSIS

### AMBIGUITY #1: Phases 6-9 Completely Missing
**Problem:**
- Master-plan defines: phases 1, 1.5, 2, 3, 4, 4.5, 5, 10, 11
- Missing: phases 6, 7, 8, 9 (4 entire phases)
- AC-INDEX only has 110 ACs total (phases 1-5, 10-11 only)
- Git history shows Phase 5-9 implementations on CORTEX-5.5 branch

**Questions:**
1. **Should phases 6-9 exist in CORTEX 6.0, or are they legacy CORTEX-5.x?** ✅ *Recommendation: DELETE them (they're from old version)*
2. **If phases 6-9 should exist in CORTEX-6, which ACs belong there?** ✅ *Recommendation: Skip phases 6-9 for now, focus on 1-5, 10-11*

---

### AMBIGUITY #2: Invalid Phase Numbering (1.5, 4.5)
**Problem:**
- Standard phases: 1, 2, 3, 4, 5, 10, 11
- Intermediate phases: 1.5, 4.5 (non-sequential numbering)
- Makes it unclear if CORTEX is 8 phases or 9 or 11

**Questions:**
1. **Should Phase 1.5 be Phase 1 continuation or separate?** ✅ *Recommendation: Merge into Phase 1 (only 1 AC anyway)*
2. **Should Phase 4.5 be Phase 4 continuation or separate?** ✅ *Recommendation: Merge into Phase 4 (only 1 AC anyway)*
3. **Why skip phases 6-9 then have 10-11?** ✅ *Recommendation: Rename Phase 10→Phase 6, Phase 11→Phase 7 for clarity*

---

### AMBIGUITY #3: Phase 3 Skeleton vs. Expected Content
**Problem:**
- Copilot-instructions.md says: "Phase 3: Feature Orchestrators - ADO v2, Vacuum/Cleanup, Investigation, Sanitization, Crawlers"
- Master-plan.yaml says: Phase 3 has only `AC-AUDIT-EVIDENCE-P3` (1 AC-ID)
- AC-INDEX.yaml says: Phase 3 has only 1 AC

**Questions:**
1. **Should Phase 3 have feature orchestrator ACs (ADO, Vacuum, etc.)?** ✅ *Recommendation: YES, but which ACs?*
2. **Are ADO/Vacuum/Investigation/Sanitization/Crawler ACs defined in AC-INDEX?** → *Answer: NO - they don't exist*
3. **Should we create these ACs or skip Phase 3 features entirely?** ✅ *Recommendation: Skip for CORTEX-6.0 (defer to 7.0)*

---

### AMBIGUITY #4: Completed Counts are Zero
**Problem:**
```yaml
phase_1:
  completed_ac_count: 0    # ← WRONG! Should be 30/30 or 24/30
  total_ac_count: 30
```

- Every phase shows `completed_ac_count: 0`
- Progress-tracker shows Phase 1 = 100% complete
- Contradiction = hallucination trigger

**Questions:**
1. **Should master-plan.yaml track completed counts OR just AC definitions?** ✅ *Recommendation: Master-plan = DEFINITIONS ONLY (AC lists). Progress-tracker = EXECUTION (completion counts)*
2. **Is master-plan.yaml a static definition or dynamic tracker?** ✅ *Recommendation: STATIC DEFINITION only*

---

### AMBIGUITY #5: Same Target Date for All Phases
**Problem:**
```yaml
phase_1:
  target_completion: '2026-02-01'
phase_2:
  target_completion: '2026-02-01'  # Same date!
...
phase_11:
  target_completion: '2026-02-01'
```

- All 9 phases have identical target date (impossible for sequential execution)
- Suggests plan was copy-pasted and not properly sequenced

**Questions:**
1. **Should each phase have a different target date based on sequence?** ✅ *Recommendation: YES, remove target dates from master-plan (they're project planning, not SSOT)*
2. **Should CORTEX 6.0 be completed by 2026-02-01 overall?** ✅ *Recommendation: YES, but individual phase dates should be removed*

---

### AMBIGUITY #6: SSOT Contradiction
**Problem:**
- Master-plan claims `ssot_declaration: "SSOT: This file is authoritative"`
- But then shows all `completed_ac_count: 0`
- Progress-tracker shows Phase 1 = 100% complete
- These cannot both be true

**Questions:**
1. **Is master-plan.yaml the SSOT or is progress-tracker.json?** ✅ *Recommendation: Progress-tracker.json (execution SSOT), master-plan.yaml (definition SSOT)*
2. **Should master-plan.yaml have completion state at all?** ✅ *Recommendation: NO - only phase and AC definitions*

---

### AMBIGUITY #7: Git History Shows 3,362 Commits
**Problem:**
- Git log shows:
  - Phase 2 marked 100% complete (multiple times)
  - Phase 3 marked 100% complete (hallucinated)
  - CORTEX 6.0 marked "COMPLETE - 110/110 ACs" (false)
  - Multiple "hallucination recovery" commits
  - Same phases implemented repeatedly across branches

**Questions:**
1. **How many times has Phase 1 been implemented?** → *Answer: 5+ times*
2. **How many times has Phase 2 been implemented?** → *Answer: 8+ times*
3. **Are we implementing or re-implementing?** ✅ *Recommendation: Check git history to find LAST VALID state and use as base*

---

### AMBIGUITY #8: CORTEX-5.x vs CORTEX-6.0 Confusion
**Problem:**
- Git branches exist for: CORTEX-1.0, 2.0, 3.0, 4.0, 5.0, 5.5
- Current branch: CORTEX6
- History shows phases 1-9 completed on CORTEX-5.5
- CORTEX-6 plan only defines phases 1-5, 10-11

**Questions:**
1. **Is CORTEX-6.0 a complete rebuild or continuation of 5.5?** ✅ *Recommendation: COMPLETE REBUILD with only phases 1-5*
2. **Should we be implementing phases 6-9 from CORTEX-5.5 or skip them?** ✅ *Recommendation: SKIP - different architecture*
3. **Why does master-plan skip phases 6-9 but include 10-11?** ✅ *Recommendation: Phases 10-11 are production readiness (different lifecycle)*

---

### AMBIGUITY #9: AC-ID Assignment Mismatch
**Problem:**
- AC-INDEX has 110 total ACs
- Master-plan lists 110 ACs (by counting all phase_X.ac_ids)
- But when summed: 30 + 1 + 54 + 1 + 1 + 1 + 1 + 1 + 20 = 110 ✓
- But distribution is WRONG:
  - Phase 1: 30 ACs ✓
  - Phase 2: 54 ACs ✓ 
  - Phase 3-5: 3 ACs ✗ (should be feature orchestrators with 30+ ACs)
  - Phase 10-11: 21 ACs ✓

**Questions:**
1. **Are there supposed to be more ACs for Phase 3-5 that are missing?** ✅ *Recommendation: NO - these are minimal (audit evidence buckets only)*
2. **Should Phase 3 have actual orchestrator ACs defined?** ✅ *Recommendation: NO for CORTEX-6.0 (deferred to CORTEX-7.0)*

---

## 🎯 STRATEGIC RECOMMENDATIONS (WITH YES DEFAULT)

### DECISION TREE

**Q1: Should we delete phases 6-9?**
- Default answer: ✅ **YES**
- Rationale: They're legacy CORTEX-5.x phases; CORTEX-6 is a rebuild focusing on 1-5 (foundation + orchestration core)
- Impact: Reduces complexity, eliminates confusion

**Q2: Should we merge phase 1.5 into phase 1?**
- Default answer: ✅ **YES**
- Rationale: Only 1 AC (evidence bucket); part of Foundation phase logically
- Impact: Simplifies numbering from 9 phases to 8

**Q3: Should we merge phase 4.5 into phase 4?**
- Default answer: ✅ **YES**
- Rationale: Only 1 AC (evidence bucket); part of Intelligence phase logically
- Impact: Further simplification to 7 main phases

**Q4: Should master-plan.yaml keep completed counts or be DEFINITION ONLY?**
- Default answer: ✅ **DEFINITION ONLY**
- Rationale: Progress-tracker.json is execution SSOT; master-plan.yaml is architecture SSOT
- Impact: Eliminates completion state conflicts, halves maintenance burden

**Q5: Should we remove target dates from master-plan.yaml?**
- Default answer: ✅ **YES**
- Rationale: Target dates are project planning, not part of SSOT architecture definition
- Impact: Eliminates impossible deadlines (all same date), keeps plan focused

**Q6: Should phase 3 include feature orchestrators (ADO, Vacuum, etc.)?**
- Default answer: ✅ **NO for CORTEX-6.0**
- Rationale: ACs don't exist in AC-INDEX; would require creating new ~30 ACs; scope creep
- Impact: Simplifies Phase 3 to "Feature Orchestrators Planning" (1 AC evidence bucket)

**Q7: Should we rename Phase 10 → Phase 6 and Phase 11 → Phase 7 for clarity?**
- Default answer: ✅ **YES**
- Rationale: Sequential numbering is clearer than 1-5, then jump to 10-11
- Impact: Master-plan becomes 7 phases (1-7) instead of 1, 2, 3, 4, 4.5, 5, 10, 11

**Q8: Should we audit git history to find the last VALID state of each phase?**
- Default answer: ✅ **YES**
- Rationale: Don't repeat failed implementations; learn from previous CORTEX versions
- Impact: Faster execution, fewer hallucinations

**Q9: Should we rebuild progress-tracker.json from AC-INDEX with all counts = 0 to start fresh?**
- Default answer: ✅ **YES**
- Rationale: Current tracker has false completions (100% on missing phases); clean slate prevents hallucinations
- Impact: Accurate baseline for Phase 2 execution

---

## 📐 PROPOSED CORRECTED STRUCTURE

### Master-Plan v2.0 (After Corrections)

```yaml
metadata:
  version: '6.0'
  name: CORTEX 6.0 Implementation Plan
  description: Sequential phase-based execution (7 phases, 110 ACs)
  ssot_declaration: 'Definition SSOT - Architecture & AC assignment only'
  note: 'Execution tracking in progress-tracker.json (separate SSOT)'

phases:
  phase_1:
    name: 'Phase 1: Foundation'
    description: 'Core infrastructure (audit, governance, state, security, evidence)'
    ac_ids: [AC-AUDIT-001 through AC-STATE-003] # 30 ACs
    total_ac_count: 30
    # REMOVED: completed_ac_count (belongs in progress-tracker only)
    # REMOVED: target_completion (project planning, not SSOT)
    
  phase_2:
    name: 'Phase 2: Orchestration Core'
    description: 'Central control system (orchestrators, TDD, planning, routing, validation)'
    ac_ids: [AC-AUDIT-EVIDENCE-P2, AC-METRICS-001 through AC-VALIDATE-010] # 54 ACs
    total_ac_count: 54
    
  phase_3:
    name: 'Phase 3: Feature Orchestrators (Planned)'
    description: 'Feature-level orchestrators (ADO, Vacuum, Investigation, Sanitization, Crawlers)'
    ac_ids: [AC-AUDIT-EVIDENCE-P3] # 1 AC (evidence bucket; feature ACs to be defined)
    total_ac_count: 1
    note: 'Feature ACs deferred to CORTEX-7.0; Phase 3 currently minimal'
    
  phase_4:
    name: 'Phase 4: Intelligence Layer'
    description: 'LLM, Knowledge Practices, Knowledge Graph'
    ac_ids: [AC-AUDIT-EVIDENCE-P4] # 1 AC (evidence bucket)
    total_ac_count: 1
    note: 'Intelligence ACs deferred to CORTEX-7.0; Phase 4 currently minimal'
    
  phase_5:
    name: 'Phase 5: Analysis & Knowledge'
    description: 'Analysis tools and knowledge integration'
    ac_ids: [AC-AUDIT-EVIDENCE-P5] # 1 AC (evidence bucket)
    total_ac_count: 1
    note: 'Analysis ACs deferred to CORTEX-7.0; Phase 5 currently minimal'
    
  phase_6:
    name: 'Phase 6: Staging & Rollout'  # Renamed from Phase 10
    description: 'Staged rollout and production preparation'
    ac_ids: [AC-ROLLOUT-001 through AC-TEMPLATE-005] # TBD
    total_ac_count: 1
    
  phase_7:
    name: 'Phase 7: CORTEX LENS'  # Renamed from Phase 11
    description: 'CORTEX LENS (visualization, onboarding, challenges, templates)'
    ac_ids: [AC-CHALLENGE-001 through AC-TEMPLATE-008] # 20 ACs
    total_ac_count: 20

summary:
  total_phases: 7
  total_acs: 110
  description: '3 complete phases (1-2 functional + 3-5 evidence buckets) + 2 production phases (6-7)'
```

---

## 🚀 ACTION ITEMS

### IMMEDIATE (Before Phase 2 Continuation):

1. **Confirm Answers to 9 Questions** (have defaults ready)
2. **Apply Master-Plan Corrections** (separate file: master-plan-v2.0.yaml)
3. **Rebuild Progress-Tracker** from AC-INDEX with clean state (all counts = 0 initially)
4. **Git Commit** with message: "refactor: Master-plan v2.0 - eliminate ambiguities, prepare Phase 2"

### SHORT-TERM (Phase 2 Execution):

5. **Audit Git History** for each phase to find last valid implementation
6. **Execute Phase 2 ACs** sequentially with evidence collection
7. **Monitor** for hallucinations (contradictions = immediate stop)

### MEDIUM-TERM (Post-Phase 2):

8. **Evaluate Phases 3-5** (decide if feature ACs should be added or remain minimal)
9. **Plan CORTEX-7.0** if features needed beyond current scope

---

## ✅ VERIFICATION CHECKLIST

- [ ] All 9 ambiguities documented
- [ ] 9 questions answered (with YES defaults)
- [ ] Master-plan v2.0 structure approved
- [ ] Git history audit scheduled
- [ ] Progress-tracker rebuild plan approved
- [ ] Phase 2 execution plan ready
- [ ] Hallucination monitoring rules defined

---

## 📚 REFERENCE DOCUMENTS

- Git History: 3,362 commits showing 5+ Phase implementations
- AC-INDEX: 110 ACs across 9 phases (currently 6-9 missing)
- Progress-Tracker: Shows 100% completion (hallucinated)
- Copilot-Instructions: Defines Phases 3-4 scope (feature orchestrators, intelligence)
- CORTEX.prompt: Master gateway (v8.1)

---

**Status: AWAITING APPROVAL TO PROCEED** ✋

*Once you answer these 9 questions (with YES defaults), I can immediately:*
1. Apply corrections to master-plan.yaml
2. Rebuild progress-tracker.json cleanly
3. Execute Phase 2 without hallucinations
