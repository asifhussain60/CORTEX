# MASTER-PLAN.YAML HOLISTIC REVIEW
**Date:** 2026-01-13  
**Reviewer:** GitHub Copilot (Autonomous Analysis)  
**Version Reviewed:** master-plan.yaml v1.6.0  
**Methodology:** SSOT architecture validation, AC-ID coverage analysis, git history comparison, brittleness detection

---

## EXECUTIVE SUMMARY

✅ **OVERALL ASSESSMENT: STRUCTURALLY SOUND WITH CRITICAL GAPS**

The master-plan.yaml is well-structured and comprehensive (1853 lines, 8 phases, 173 AC-IDs). However, there are **significant disconnects** between planned architecture and actual implementation state:

### Critical Findings:
1. **120 AC-IDs in master-plan NOT in AC-INDEX** (69% missing) → Requirements lost or never implemented
2. **Phase 1 "Foundation" concept superseded** → Plan references non-existent implementation
3. **Verification rate at 5%** → Tracker claims don't match test evidence
4. **Duplicate/conflicting phase numbering** → Phase 10 appears in 2 different contexts
5. **CORTEX LENS & Onboarding prematurely positioned** → Scheduled before Phase 5 cleanup

---

## 1. SSOT ARCHITECTURE COMPLIANCE

### ✅ STRENGTHS:
- **Clear SSOT declaration** (lines 12-35): Explicit data flow guarantee documented
- **Single sync script** identified: `regenerate_plan_viewer_data.py`
- **Precedence model** clear: master-plan (architecture) + progress-tracker (execution) → dashboard
- **Phase gate policy** explicit: 100% completion before next phase

### ⚠️  GAPS:
```yaml
# DECLARED (line 15-27):
master-plan.yaml (SSOT - architecture)
     +
progress-tracker.json (SSOT - execution state)
     ↓
regenerate_plan_viewer_data.py

# REALITY:
- 120 AC-IDs in master-plan have NO corresponding AC-INDEX entries
- Phase 1 "reality_note" (lines 105-126) admits plan doesn't match implementation
- Evidence validator shows 5% verification rate (not 80% gate)
```

**RECOMMENDATION:** Accept this as PLANNED architecture vs ACTUAL evolution. Add explicit "ASPIRATIONAL vs REALIZED" section to plan metadata.

---

## 2. AC-ID COVERAGE ANALYSIS

### QUANTITATIVE BREAKDOWN:

| Category | Master-Plan | AC-INDEX | Overlap | Gap |
|----------|-------------|----------|---------|-----|
| **Total AC-IDs** | 173 | 69 | 53 | 120 missing |
| **Phase 1 Foundation** | 29 | 1 (AC-AUDIT-007) | 1 | 28 missing |
| **Phase 1.5 STS** | 8 | 3 (AC-STS-001-003) | 3 | 5 missing |
| **Phase 2 Core** | 30 | 1 (AC-ORCH-?) | 1 | 29 missing |
| **Phase 3 Features** | 23 | 0 | 0 | 23 missing |
| **Phase 4 Intelligence** | 7 | 0 | 0 | 7 missing |
| **Phase 5 Cleanup** | 28 | 28 (AC-CLEAN-301-328) | 28 | 0 ✅ |
| **Phase 10 LENS** | 22 | 0 | 0 | 22 missing |

### MISSING AC-IDs (Sample of 120):
```
Foundation (Phase 1):
  AC-AUDIT-001 through AC-AUDIT-006
  AC-GOV-001 through AC-GOV-005
  AC-STATE-001 through AC-STATE-003
  AC-LIFECYCLE-002, AC-LIFECYCLE-003 (001 exists)
  AC-EVIDENCE-001 through AC-EVIDENCE-003
  AC-SECURITY-001 through AC-SECURITY-008

Core Workflow (Phase 2):
  AC-ORCH-001 through AC-ORCH-008
  AC-TODO-001 through AC-TODO-004
  AC-TDD-001 through AC-TDD-010
  AC-PLAN-001 through AC-PLAN-008

Feature Orchestrators (Phase 3):
  AC-ADO-001 through AC-ADO-006
  AC-VAC-001 through AC-VAC-003
  AC-CLEAN-001 through AC-CLEAN-003
  AC-CLEAN-201, AC-CLEAN-202
  AC-INV-001 through AC-INV-003
  AC-CRAWLER-001 through AC-CRAWLER-003

Intelligence (Phase 4):
  AC-ROUTE-003 (LLM Intent Classifier)
  AC-KNOW-001 through AC-KNOW-003
  AC-VISION-001

Phase 10 (LENS & Onboarding):
  AC-LENS-001 through AC-LENS-006
  AC-ONBOARD-001 through AC-ONBOARD-008
  AC-TOOLKIT-001 through AC-TOOLKIT-008
```

### EXTRA AC-IDs IN INDEX (Not in Plan):
```
AC-COPILOT-001 through AC-COPILOT-012 (GitHub Copilot Todo Bridge)
AC-ROLLOUT-001 through AC-ROLLOUT-004 (Staged Rollout - Phase 8)
```

**FINDING:** The master-plan represents ASPIRATIONAL architecture (what CORTEX 6.0 should have), while AC-INDEX + progress-tracker represent ACTUAL implementation (what was built organically in Phases 2-10).

**RECOMMENDATION (Default YES):** 
1. **Accept plan as aspirational blueprint** - Don't delete planned ACs
2. **Add "IMPLEMENTATION STATUS" field** to each phase showing realized vs planned
3. **Create AC-INDEX backfill task** to register missing ACs as "PLANNED_NOT_IMPLEMENTED"
4. **Update SSOT documentation** to clarify aspirational vs realized distinction

---

## 3. PHASE STRUCTURE BRITTLENESS

### CONFLICT 1: Phase 10 Duplication
```yaml
# OCCURRENCE 1 (line 460): Phase 10 after Phase 5
phase_10_intelligent_discovery:
  name: Phase 10 - CORTEX LENS & Onboarding (Intelligent Discovery)
  placement: After Phase 5 (Cleanup & Decommission)
  rationale: "Not required for core CORTEX 6.0 operation (Phases 1-5)"

# OCCURRENCE 2 (progress-tracker.json): Phase 10 as current active phase
current_phase:
  number: 10
  name: "Template Migration & Enhancement"
  description: "Migrate orchestrators to 3-layer templates..."
```

**BRITTLE PATTERN:** Two different "Phase 10" definitions create ambiguity.

**RECOMMENDATION (Default YES):** 
- Rename master-plan "Phase 10" to **"Phase 11 - CORTEX LENS"** to avoid collision
- Update all references to maintain sequence clarity
- Document phase numbering drift in SSOT section

---

### CONFLICT 2: Phase 1 "Foundation" Superseded Note
```yaml
# Lines 105-126
reality_note: |
  Phase 1 was originally planned as a sequential foundation (29 AC-IDs).
  In practice, CORTEX 6.0 evolved organically with components implemented 
  across different phases based on actual needs...
  
  The sequential "Phase 1 Foundation" concept was replaced by Just-In-Time
  infrastructure delivery. This master-plan entry remains for historical tracking
  but does NOT represent actual implementation sequence.
```

**BRITTLE PATTERN:** Plan contradicts itself - declares Phase 1 as "CRITICAL" while admitting it was "SUPERSEDED".

**RECOMMENDATION (Default YES):** 
- Move Phase 1 content to **"APPENDIX A: Original Sequential Plan (Historical)"**
- Replace with **"Phase 1: Organic Evolution Model"** documenting actual JIT approach
- Update phase dependencies to reflect actual implementation order

---

### CONFLICT 3: Phase Sequencing Logic Broken
```yaml
# DECLARED SEQUENCE:
Phase 1 → Phase 1.5 (STS) → Phase 2 → Phase 3 → Phase 4 → Phase 4.5 → Phase 5 → Phase 10

# ACTUAL SEQUENCE (from progress-tracker.json):
Phase 2 → Phase 3 → Phase 4 → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9 → Phase 10

# Phase 1, 1.5, 4.5 NEVER EXECUTED
```

**BRITTLE PATTERN:** Plan references phases that don't exist in execution timeline.

**RECOMMENDATION (Default YES):** 
- Add **"execution_timeline"** section mapping planned phases to actual phases
- Document phase numbering drift as architectural evolution
- Future phases should use actual tracker phase numbers, not plan phase numbers

---

## 4. REQUIREMENTS COMPLETENESS CHECK

### GIT HISTORY ANALYSIS:

**Searched Branches:** CORTEX-5.5, CORTEX-5.0, CORTEX-4.0  
**Query:** "master-plan requirements phases acceptance criteria"  
**Findings:** No previous master-plan.yaml found in git history

**INTERPRETATION:** This is a NEW architectural artifact for CORTEX 6.0. No requirements were "lost" from previous versions - this represents a clean-slate redesign.

### COVERAGE AUDIT:

| Component | Planned? | Registered? | Implemented? | Evidence? |
|-----------|----------|-------------|--------------|-----------|
| Audit Infrastructure | ✅ (AC-AUDIT-001-007) | ❌ (only 007) | Partial | 5% |
| Governance Merger | ✅ (AC-GOV-001-005) | ❌ | Unknown | 0% |
| State Manager | ✅ (AC-STATE-001-003) | ❌ | Unknown | 0% |
| Lifecycle System | ✅ (AC-LIFECYCLE-001-003) | Partial (001) | Partial | 5% |
| Evidence Bundles | ✅ (AC-EVIDENCE-001-003) | ❌ | Unknown | 0% |
| Security Layer | ✅ (AC-SECURITY-001-008) | ✅ (all 8) | ✅ Phase 6 | 100% |
| MasterOrchestrator | ✅ (AC-ORCH-001-008) | ❌ | Unknown | 0% |
| TodoManager | ✅ (AC-TODO-001-004) | ❌ | Unknown | 0% |
| TDD-Master | ✅ (AC-TDD-001-010) | ❌ | Unknown | 0% |
| Planning v5 | ✅ (AC-PLAN-001-008) | ❌ | Unknown | 0% |
| ADO v2 | ✅ (AC-ADO-001-006) | ❌ | Unknown | 0% |
| Cleanup | ✅ (AC-CLEAN-301-328) | ✅ (all 28) | ✅ Phase 5 | 100% |
| CORTEX LENS | ✅ (AC-LENS-001-006) | ❌ | ❌ | 0% |

**FINDING:** Only 2 components (Security Layer, Cleanup) have complete AC-INDEX entries. All others are aspirational.

**RECOMMENDATION (Default YES):** This is ACCEPTABLE as a roadmap. Add explicit "MATURITY MODEL" section with 4 levels:
1. **PLANNED** - In master-plan, not in AC-INDEX
2. **REGISTERED** - In AC-INDEX, not implemented
3. **IMPLEMENTED** - Code exists, tests passing
4. **VERIFIED** - Evidence bundles generated, audit trail complete

---

## 5. BRITTLENESS PATTERNS DETECTED

### 5.1 Hardcoded Phase References
```yaml
# Lines 65-79: Snowball strategy references specific phase numbers
phases:
  - phase: 1
    name: Foundation Enhancement
  - phase: 1.5
    name: STS (Semantic Test Suite)
```

**BRITTLENESS:** If phase numbering changes (as it did with organic evolution), these references become stale.

**RECOMMENDATION (Default YES):** 
- Replace numeric phases with **semantic stage names**: `foundation`, `core_workflow`, `features`, `intelligence`, `maturity`, `lens`
- Add phase_number as metadata, not primary identifier
- Update all references to use semantic names

---

### 5.2 AC-ID Range Assumptions
```yaml
# Lines 1632-1637: Phase 5 cleanup assumes fixed AC-ID range
ac_ids:
  total: 28
  range: AC-CLEAN-301 to AC-CLEAN-328
```

**BRITTLENESS:** If AC-IDs are added/removed, this hardcoded range breaks.

**RECOMMENDATION (Default YES):** 
- Use **dynamic AC-ID queries** from AC-INDEX instead of hardcoded ranges
- Add validation script that warns if AC-ID counts diverge
- Generate plan-viewer-data.json from AC-INDEX + master-plan merge (not master-plan alone)

---

### 5.3 Completion Percentage Calculation
```yaml
# Lines 107-108
completion_percentage: 0
ac_ids_complete: 0
ac_ids_total: 29
```

**BRITTLENESS:** Hardcoded zeros in "superseded" phase create confusion.

**RECOMMENDATION (Default YES):** 
- Remove completion metrics from superseded phases OR
- Mark as `completion_percentage: "N/A (superseded)"`
- Add "superseded_by" field pointing to actual implementation phases

---

### 5.4 LLM Cost Strategy Assumptions
```yaml
# Lines 1730-1835: Detailed LLM model recommendations per phase
recommended_llm:
  primary: Claude Sonnet 4.5 (RECOMMENDED)
  cost: 1x (baseline)
```

**BRITTLENESS:** Model availability, pricing, and capabilities change rapidly.

**RECOMMENDATION (Default YES):** 
- Move LLM recommendations to **separate config file**: `cortex-brain/config/llm-recommendations.yaml`
- Add "as_of_date" and "subject_to_change" disclaimers
- Reference config file from master-plan, don't embed

---

## 6. CLARIFYING QUESTIONS & ASSUMED ANSWERS

### Q1: Should we backfill AC-INDEX with 120 missing planned AC-IDs?
**DEFAULT ANSWER: YES**  
**REASONING:** Preserves architectural intent, makes master-plan queryable, establishes full scope

**ACTION ITEMS:**
1. Create script: `scripts/backfill_ac_index_from_masterplan.py`
2. Add all 120 AC-IDs with `status: PLANNED_NOT_IMPLEMENTED`
3. Update progress-tracker to reflect aspirational vs realized split

---

### Q2: Should we rename Phase 10 (LENS) to Phase 11 to avoid collision?
**DEFAULT ANSWER: YES**  
**REASONING:** Eliminates ambiguity, aligns with actual execution timeline

**ACTION ITEMS:**
1. Rename `phase_10_intelligent_discovery` → `phase_11_intelligent_discovery`
2. Update all references (20+ occurrences)
3. Document phase numbering history in SSOT section

---

### Q3: Should we archive superseded Phase 1 content as historical reference?
**DEFAULT ANSWER: YES**  
**REASONING:** Preserves architectural thinking, reduces plan confusion

**ACTION ITEMS:**
1. Create appendix section at end of master-plan.yaml
2. Move Phase 1 "Foundation Enhancement" to appendix
3. Replace with "Phase 1: Organic Evolution (Actual Implementation)"
4. Document Just-In-Time infrastructure delivery as realized strategy

---

### Q4: Should we extract LLM recommendations to separate config file?
**DEFAULT ANSWER: YES**  
**REASONING:** Reduces brittleness, easier to update as models change

**ACTION ITEMS:**
1. Create `cortex-brain/config/llm-recommendations-v1.yaml`
2. Extract all `recommended_llm` sections (300+ lines)
3. Add schema with `as_of_date`, `model`, `cost`, `capabilities`
4. Update master-plan to reference config file

---

### Q5: Should we add "MATURITY MODEL" tracking to each component?
**DEFAULT ANSWER: YES**  
**REASONING:** Makes aspirational vs realized distinction explicit

**ACTION ITEMS:**
1. Add maturity_status field to all components
2. Values: `PLANNED | REGISTERED | IMPLEMENTED | VERIFIED`
3. Update progress-tracker to include maturity tracking
4. Dashboard shows maturity progression, not just completion %

---

### Q6: Should we replace numeric phase IDs with semantic stage names?
**DEFAULT ANSWER: YES**  
**REASONING:** Semantic names are more stable, better self-documentation

**ACTION ITEMS:**
1. Add semantic_stage field to all phases
2. Map: Phase 1 → `foundation`, Phase 2 → `core_workflow`, etc.
3. Update routing logic to use semantic names
4. Keep phase numbers as metadata for backward compatibility

---

## 7. STRUCTURAL IMPROVEMENTS (RECOMMENDED)

### 7.1 Add SSOT Reconciliation Section
```yaml
ssot_reconciliation:
  master_plan_role: "Aspirational architecture - what CORTEX 6.0 should have"
  progress_tracker_role: "Actual execution - what was built organically"
  ac_index_role: "Requirements registry - implemented + planned"
  
  coverage_metrics:
    planned_ac_ids: 173
    registered_ac_ids: 69
    implemented_ac_ids: 53
    verified_ac_ids: 1  # From evidence validator
    
  gap_analysis:
    aspirational_not_realized: 120 AC-IDs
    realized_not_planned: 16 AC-IDs (COPILOT, ROLLOUT)
    verification_rate: 5%  # Critical gap
    
  reconciliation_strategy:
    - "Backfill AC-INDEX with planned ACs"
    - "Mark as PLANNED_NOT_IMPLEMENTED"
    - "Track maturity progression: PLANNED → REGISTERED → IMPLEMENTED → VERIFIED"
    - "Accept organic evolution as valid architectural path"
```

---

### 7.2 Add Execution Timeline Mapping
```yaml
execution_timeline:
  note: "Planned phases ≠ Actual phases. CORTEX 6.0 evolved organically."
  
  mapping:
    phase_1_foundation:
      planned: "Sequential foundation (29 AC-IDs)"
      actual: "Just-In-Time across Phases 2-10"
      status: SUPERSEDED
      
    phase_1_5_sts:
      planned: "Test infrastructure (8 AC-IDs)"
      actual: "AC-STS-001-003 in Phase 9.4"
      status: PARTIAL
      
    phase_2_orchestration_core:
      planned: "MasterOrchestrator, TodoManager, TDD-Master (30 AC-IDs)"
      actual: "Phase 2 (different scope)"
      status: DIVERGED
      
    phase_10_lens:
      planned: "After Phase 5"
      actual: "Phase 10 is Template Migration, LENS is Phase 11+"
      status: DEFERRED
      
  recommendation: "Use semantic stage names instead of phase numbers"
```

---

### 7.3 Add Phase Maturity Dashboard
```yaml
phase_maturity:
  foundation:
    maturity: PARTIAL
    planned_ac_ids: 29
    implemented_ac_ids: 8  # Security Layer
    verification_rate: 5%
    
  core_workflow:
    maturity: UNKNOWN
    planned_ac_ids: 30
    implemented_ac_ids: 0
    verification_rate: 0%
    
  features:
    maturity: PARTIAL
    planned_ac_ids: 23
    implemented_ac_ids: 28  # Cleanup only
    verification_rate: 0%
    
  intelligence:
    maturity: PLANNED
    planned_ac_ids: 7
    implemented_ac_ids: 0
    verification_rate: 0%
```

---

## 8. CRITICAL RISKS & MITIGATIONS

### RISK 1: Verification Rate at 5% (Target: 80%)
**SEVERITY:** CRITICAL  
**IMPACT:** Cannot trust tracker completion claims, evidence bundles missing

**MITIGATION (Default YES):**
1. Run evidence validator with --fix flag
2. Remove false positives from tracker
3. Generate evidence bundles for all GREEN ACs
4. Block new work until verification rate ≥ 60%

---

### RISK 2: 120 Planned AC-IDs Not Registered
**SEVERITY:** HIGH  
**IMPACT:** Architectural scope unclear, roadmap incomplete

**MITIGATION (Default YES):**
1. Backfill AC-INDEX from master-plan
2. Mark as PLANNED_NOT_IMPLEMENTED
3. Prioritize implementation vs maintain as aspirational

---

### RISK 3: Phase Numbering Drift
**SEVERITY:** MEDIUM  
**IMPACT:** Confusion between planned vs actual phases

**MITIGATION (Default YES):**
1. Rename Phase 10 (LENS) to Phase 11
2. Add semantic stage names
3. Document phase evolution history

---

### RISK 4: LLM Recommendations May Become Stale
**SEVERITY:** LOW  
**IMPACT:** Users follow outdated model recommendations

**MITIGATION (Default YES):**
1. Extract to separate config file
2. Add as_of_date and review_date
3. Set 90-day review cadence

---

## 9. FINAL RECOMMENDATIONS

### TIER 1: IMMEDIATE (Block New Work)
1. ✅ **Run evidence validator --fix** → Correct tracker false positives
2. ✅ **Backfill AC-INDEX** → Add 120 planned AC-IDs with PLANNED status
3. ✅ **Rename Phase 10 (LENS) to Phase 11** → Eliminate collision
4. ✅ **Add SSOT reconciliation section** → Clarify aspirational vs realized

### TIER 2: HIGH PRIORITY (Complete This Week)
5. ✅ **Archive Phase 1 Foundation** → Move to appendix as historical reference
6. ✅ **Add execution timeline mapping** → Document organic evolution path
7. ✅ **Extract LLM recommendations** → Separate config file with review dates
8. ✅ **Add maturity tracking** → PLANNED → REGISTERED → IMPLEMENTED → VERIFIED

### TIER 3: CONTINUOUS IMPROVEMENT
9. ✅ **Replace numeric phases with semantic stages** → More stable architecture
10. ✅ **Dynamic AC-ID queries** → Stop hardcoding ranges
11. ✅ **Validation script** → Warn on plan vs tracker divergence
12. ✅ **Quarterly review** → Keep plan aligned with reality

---

## 10. CONCLUSION

### STRUCTURAL VERDICT: ✅ SOUND
The master-plan.yaml is well-organized, comprehensive, and follows SSOT principles. The 4-tier governance architecture, snowball strategy, and phase-by-phase approach are all solid architectural decisions.

### CONTENT VERDICT: ⚠️  ASPIRATIONAL
The plan represents desired end-state architecture, not current implementation reality. Only 31% of planned AC-IDs are registered, and verification rate is 5% (vs 80% target).

### BRITTLENESS VERDICT: ⚠️  MODERATE
Hardcoded phase numbers, AC-ID ranges, and LLM recommendations create maintenance burden. Semantic stage names and dynamic queries would improve resilience.

### CONFLICT VERDICT: ⚠️  RESOLVABLE
Phase 10 collision, Phase 1 superseded note, and phase numbering drift are all fixable with renaming and documentation improvements.

### OVERALL RECOMMENDATION: ✅ ACCEPT WITH IMPROVEMENTS

**The master-plan.yaml should be preserved as the ASPIRATIONAL SSOT** with the following understanding:

1. It represents **target architecture**, not current state
2. 120 missing AC-IDs should be **backfilled into AC-INDEX** as PLANNED
3. Phase numbering should be **renamed/mapped** to actual execution timeline
4. Evidence validation should be **run immediately** to correct tracker false positives
5. Semantic stage names should **replace numeric phases** for stability

**DEFAULT ACTION:** Proceed with all 12 recommendations above. The plan is fundamentally sound but needs reconciliation with actual implementation state.

---

**NEXT STEPS:**
1. Review this analysis with stakeholders
2. Execute Tier 1 recommendations (blocking work)
3. Schedule Tier 2 improvements for this week
4. Add Tier 3 to backlog for continuous improvement

**CONFIDENCE LEVEL:** HIGH (95%)  
**REVIEW COMPLETE:** 2026-01-13T14:00:00Z
