# Gap Analysis: Planning System Redesign vs. Requirements

**Date:** January 2, 2026  
**Analysis Type:** Compliance Check  
**Status:** 🔴 CRITICAL GAPS IDENTIFIED

---

## 📊 Requirements Coverage Analysis

### ✅ COVERED Requirements

| Requirement | Redesign Proposal Coverage | Location |
|-------------|---------------------------|----------|
| **Phase -1 Knowledge Library** | ✅ FULLY COVERED | Section "2. Orchestrator Self-Validation", line 398 |
| **Auto-Healing** | ✅ FULLY COVERED | Section "2. Orchestrator Self-Validation", line 477 |
| **Compliance Scoring** | ✅ FULLY COVERED | Section "4. Validation Enforcement", line 570 |
| **Invocation Bridge** | ✅ FULLY COVERED | Section "1. Invocation Bridge (NEW)", line 270 |

---

## ❌ MISSING Requirements

### 1. Maintenance-Style Autonomous Execution Format

**Requirement:** Follow `cortex-maintenance.prompt.md` execution format with constant visual progress in Copilot Chat

**Current State:**
- Redesign mentions `autonomous_execution_progress` template (line 166)
- Does NOT specify how to render progress **during** execution
- Maintenance shows progress **at each phase transition**

**Gap:**
```python
# MISSING: Real-time progress updates during plan generation
# Maintenance does this:
def execute_phase(phase_num):
    print(f"## Phase {phase_num} Starting...")
    # Do work...
    render_progress_tracker(overall_progress, phase_progress)  # ← DURING execution
    print(f"## Phase {phase_num} Complete")
    render_progress_tracker(overall_progress, phase_progress)  # ← AFTER execution

# Redesign proposal only mentions:
# "Output: Real-time progress via autonomous_execution_progress" (line 353)
# But no implementation details
```

**Required Fix:**
- Add execution loop with progress rendering at each substep
- Render progress bar after EVERY task completion (not just phase completion)
- Use maintenance template pattern: Progress → Work → Progress → Work

---

### 2. Mandatory Knowledge Library Check on EACH Turn

**Requirement:** Knowledge library consultation MUST happen on every planning turn, not just Phase -1

**Current State:**
- Redesign only mentions Phase -1 consultation (line 431-453)
- No mechanism for continuous knowledge library queries during plan refinement

**Gap:**
```python
# CURRENT: One-time check at Phase -1
def _phase_minus_one_knowledge_consultation(self, params):
    # Query knowledge library once
    pass

# REQUIRED: Check on every turn
def _execute_autonomous_mode(self, **kwargs):
    for phase in phases:
        # Before EACH phase execution
        kl_context = self._query_knowledge_library_for_phase(phase)
        phase.context.update(kl_context)
        # Execute phase
        # After phase execution
        self._extract_knowledge_to_library(phase.artifacts)
```

**Required Fix:**
- Add `_query_knowledge_library_for_phase()` method
- Add `_extract_knowledge_to_library()` method
- Integrate with Tier 2/3 brain (knowledge graph + dev context)

---

### 3. Automatic Final REFACTOR + Documentation Phase

**Requirement:** Automatically add comprehensive REFACTOR phase AND knowledge library extraction phase

**Current State:**
- Redesign mentions REFACTOR validation (line 457-473)
- Does NOT mention automatic knowledge extraction phase
- Does NOT mention feeding back to brain tiers

**Gap:**
```yaml
# CURRENT: Plan ends at Phase 10 (REFACTOR)
phases:
  - Phase -1: Knowledge Library Consultation
  - Phase 0-9: Feature Implementation
  - Phase 10: REFACTOR (≥15 tasks)

# REQUIRED: Plan ends at Phase 12
phases:
  - Phase -1: Knowledge Library Consultation
  - Phase 0-9: Feature Implementation
  - Phase 10: REFACTOR (≥15 tasks)
  - Phase 11: Knowledge Extraction & Graph Update  # ← MISSING
  - Phase 12: Documentation Library Update         # ← MISSING
```

**Required Fix:**
- Add Phase 11: Knowledge Extraction
  - Extract patterns from implementation
  - Update Tier 2 knowledge graph
  - Update Tier 3 dev context
  - Replace obsolete data
- Add Phase 12: Documentation Library Update
  - Generate lessons learned
  - Update cortex-brain/knowledge-library/
  - Create cross-references

---

### 4. Post-Implementation Brain Tier Updates

**Requirement:** Extract knowledge graphs and feed appropriate brain tiers, replacing redundant/obsolete data

**Current State:**
- Redesign does NOT mention brain tier updates
- No knowledge graph extraction
- No obsolete data detection/replacement

**Gap:**
```python
# MISSING ENTIRELY:
def _update_brain_tiers_after_plan(self, plan: PlanData):
    """
    Extract knowledge from completed plan and update brain tiers.
    
    Tier 1 Updates:
    - Update conversation-context.jsonl (plan metadata)
    - Update development-context.yaml (plan status)
    
    Tier 2 Updates:
    - Extract patterns → knowledge-graph.yaml
    - Detect obsolete patterns → replace with new ones
    - Update bidirectional links
    
    Tier 3 Updates:
    - Update module-definitions.yaml (new modules created)
    - Update file-relationships.yaml (new dependencies)
    - Update lessons-learned.yaml (what worked/didn't)
    """
    pass
```

**Required Fix:**
- Implement brain tier update pipeline
- Add obsolete data detection (compare old vs. new patterns)
- Add replacement logic (atomic updates, no orphaned references)

---

### 5. Hierarchical Plan Structure (Master + Sub-Files)

**Requirement:** Create plan under `planning/active/` with master file + linked sub-files for each phase with 2-way links

**Current State:**
- Redesign mentions folder structure (line 176-184):
  ```
  cortex-brain/documents/planning/active/{PLAN_NAME}/
  ├── 00-master-plan.md
  ├── context/
  ├── reports/
  ├── artifacts/
  └── tracking/
  ```
- But does NOT specify sub-files for EACH PHASE
- No 2-way linking strategy

**Gap:**
```markdown
# CURRENT: Monolithic master plan
00-master-plan.md (contains ALL phases inline)

# REQUIRED: Hierarchical structure
planning/active/user-authentication-2026-01-02/
├── 00-MASTER-PLAN.md           # Hub with links to phase files
├── phases/
│   ├── phase-minus-1-knowledge-library.md
│   ├── phase-00-discovery.md
│   ├── phase-01-requirements.md
│   ├── ...
│   ├── phase-10-refactor.md
│   ├── phase-11-knowledge-extraction.md
│   └── phase-12-documentation-update.md
├── context/
│   ├── knowledge-library-context.md
│   ├── existing-implementations.md
│   └── threat-model.md
├── artifacts/
│   ├── api-spec.yaml
│   ├── data-model.sql
│   └── test-cases.json
└── tracking/
    ├── progress-tracker.json
    └── compliance-report.json

# 2-Way Links:
# 00-MASTER-PLAN.md:
## Phase 1: Requirements
[View Phase Details](phases/phase-01-requirements.md)

# phases/phase-01-requirements.md:
[← Back to Master Plan](../00-MASTER-PLAN.md)
```

**Required Fix:**
- Generate phase sub-files during plan creation
- Implement 2-way linking (master → phase, phase → master)
- Add navigation breadcrumbs

---

## 📋 Enhanced Requirements Summary

| # | Requirement | Redesign Coverage | Status | Priority |
|---|-------------|-------------------|--------|----------|
| 1 | Phase -1 Knowledge Library (one-time) | ✅ COVERED | Complete | HIGH |
| 2 | **Continuous Knowledge Library Checks** | ❌ MISSING | New requirement | CRITICAL |
| 3 | Invocation Bridge (MCP tool) | ✅ COVERED | Complete | CRITICAL |
| 4 | Auto-Healing Violations | ✅ COVERED | Complete | HIGH |
| 5 | Compliance Scoring | ✅ COVERED | Complete | HIGH |
| 6 | **Maintenance-Style Progress Rendering** | ❌ MISSING | Partial spec | CRITICAL |
| 7 | **Automatic Phase 11 (Knowledge Extraction)** | ❌ MISSING | Not mentioned | CRITICAL |
| 8 | **Automatic Phase 12 (Documentation Update)** | ❌ MISSING | Not mentioned | CRITICAL |
| 9 | **Brain Tier Updates (Post-Implementation)** | ❌ MISSING | Not mentioned | HIGH |
| 10 | **Hierarchical Plan Structure (Master + Subs)** | ⚠️ PARTIAL | Folder structure only | HIGH |
| 11 | **2-Way Linking (Master ↔ Phase)** | ❌ MISSING | Not mentioned | MEDIUM |
| 12 | **Obsolete Data Replacement** | ❌ MISSING | Not mentioned | MEDIUM |

**Coverage Score:** 4/12 (33%) → **67% MISSING**

---

## 🎯 Critical Action Items

### Immediate (Week 1-2)
1. ✅ Specify maintenance-style progress rendering pattern
2. ✅ Add continuous knowledge library query mechanism
3. ✅ Design Phase 11 (Knowledge Extraction) implementation
4. ✅ Design Phase 12 (Documentation Update) implementation

### Short-Term (Week 3-4)
5. ✅ Implement hierarchical plan structure (master + phase sub-files)
6. ✅ Implement 2-way linking system
7. ✅ Design brain tier update pipeline
8. ✅ Add obsolete data detection/replacement logic

### Medium-Term (Week 5-6)
9. ✅ Test continuous knowledge library integration
10. ✅ Test brain tier updates with real plans
11. ✅ Validate hierarchical structure rendering
12. ✅ Performance testing (with sub-file loading)

---

## 🚀 Next Steps

**FOR USER:**
1. Review this gap analysis
2. Confirm requirements priorities
3. Approve enhanced scope (12 requirements vs. original 4)

**FOR IMPLEMENTATION:**
1. Update redesign proposal with missing requirements
2. Create detailed specifications for missing components
3. Create example plan structure showing hierarchical layout
4. Begin Phase 1 implementation with enhanced scope

---

**End of Gap Analysis**
