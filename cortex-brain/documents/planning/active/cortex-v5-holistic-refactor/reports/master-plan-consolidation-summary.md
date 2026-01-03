# 🎯 Master Plan Consolidation Summary

**Date:** January 3, 2026  
**Plan:** cortex-v5-holistic-refactor  
**Action:** Gap remediation without creating duplicate plans  
**Status:** ✅ IN PROGRESS

---

## 🎯 User Intent Clarified

**CORRECT Architecture:** Single master plan with child plans for detailed execution

```
cortex-v5-holistic-refactor/           ← MASTER PLAN (controls all work)
├── 00-MASTER-PLAN-V5.md              ← Single source of truth
├── Phase 6.1 → ado-v2-migration/     ← CHILD PLAN (referenced)
├── Phase 6.2 → vacuum-v2-migration/  ← CHILD PLAN (referenced)
├── Phase 6.3 → cleanup-v2-migration/ ← CHILD PLAN (referenced)
```

**Key Principle:** Master Orchestrator controls workflow through ONE master plan that references child plans for detailed execution.

---

## ✅ Changes Applied to Master Plan

### 1. Added Mandatory Content Blocks (✅ COMPLETE)

**Location:** After Executive Summary, before Phase 0

**Content Added:**
- ✅ Response Template Reference (`response-templates-v4.yaml:863`)
- ✅ Copilot Instructions block with:
  - Response template specification
  - TDD enforcement rules
  - REFACTOR requirements (18+ tasks minimum)
  - Governance integration
  - Applicable SKULL rules (10 rules listed)

**Gap Fixed:** PS-2.2.2, PS-2.2.4

---

### 2. Inserted Phase -1: Knowledge Library Consultation (✅ COMPLETE)

**Location:** Before Phase 0

**Duration:** 1 hour

**Tasks:**
- Task -1.1: Query Knowledge Graph (15 min)
- Task -1.2: Review Lessons Learned (15 min)
- Task -1.3: Consult TRUTH-SOURCES (15 min)
- Task -1.4: Query Brain Protection Rules (15 min)

**Deliverable:** `context/knowledge-library-findings.md`

**Gap Fixed:** PS-2.3.1 through PS-2.3.5 (SKULL: `KNOWLEDGE_LIBRARY_INTEGRATION_ENFORCEMENT`)

---

### 3. Added Acceptance Validation Tasks to Phase 6.3 (✅ COMPLETE)

**Location:** After Task 6.3 (Cleanup v2 Migration), before Task 6.4

**New Tasks Added:**
- **Task 6.3.1:** Master Orchestrator Acceptance Validation (4h)
- **Task 6.3.2:** Cross-Session Context Acceptance Validation (3h)
- **Task 6.3.3:** Plan Filename Standardization (2h)
- **Task 6.3.4:** Update Master Plan with Mandatory Content (2h) - Already complete
- **Task 6.3.5:** ADO v2 Acceptance Validation Report (2h)
- **Task 6.3.6:** Planning System v5 Acceptance Validation (1h)

**Total Duration:** 14 hours

**Gaps Fixed:** MO-1.1.*, MO-1.2.*, MO-1.3.*, PS-2.1.*, PS-2.2.*, ADO-4.1.*

---

## 🚧 Changes Pending (Need to Apply)

### 4. Phase 6.5: AST Integration (NEW - 14h)

**Insert Location:** After Task 6.4 (GUIDED Orchestrator Assessments), before Phase 7

**Goal:** Integrate AST scanning into Planning System v5 for holistic code discovery

**Tasks:**
- **Task 6.5.1:** Create AST Scanner Agent (6h)
  - File: `src/cortex_agents/ast_scanner.py` (400-500 lines)
  - Features: Call graph analysis, orphan detection, duplicate detection, complexity metrics
  
- **Task 6.5.2:** Integrate AST Scanning into Planning v5 Phase 0 (4h)
  - Modify: `src/orchestrators/planning_orchestrator_v5.py`
  - Add AST scan execution in Phase 0 (Discovery)
  - Generate: `context/ast-analysis.json` with acceptance schema
  
- **Task 6.5.3:** Generate AST Findings Report (2h)
  - Surface AST findings in plan generation
  - Template: Show orphaned functions, duplicates, complexity issues
  
- **Task 6.5.4:** Test AST Integration (2h)
  - Test suite: `tests/orchestrators/planning/test_ast_integration.py`
  - Validate: PS-2.4.1 through PS-2.4.5

**Deliverables:**
- AST Scanner agent (400-500 lines, 100% coverage)
- Planning v5 Phase 0 includes AST scan
- `context/ast-analysis.json` per acceptance schema
- AST findings in plan generation
- Test suite passing

**Gaps Fixed:** PS-2.4.1 through PS-2.4.5 (SKULL: `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`)

---

### 5. Phase 7.1: Orchestrator Lifecycle Hooks (NEW - 14h)

**Insert Location:** After current Phase 7, before Phase 8

**Goal:** Implement standardized lifecycle hooks for all orchestrators

**Tasks:**
- **Task 7.1.1:** Pre-Execution Workspace Validation Hook (3h)
  - File: `src/orchestrators/hooks/pre_execution.py`
  - Checks: Git repo, clean state, disk space, Python environment
  - Integration: BaseOrchestrator v4.1
  
- **Task 7.1.2:** Post-Execution Git Checkpoint Hook (4h)
  - File: `src/orchestrators/hooks/post_execution.py`
  - Creates: Git commit + tag after each phase
  - Format: `checkpoint-{orchestrator}-{phase}-{timestamp}`
  
- **Task 7.1.3:** Error Cleanup Hook (3h)
  - File: `src/orchestrators/hooks/error_cleanup.py`
  - Actions: Remove partial artifacts, rollback DB, log error
  
- **Task 7.1.4:** Test Lifecycle Hooks (4h)
  - Test suite: `tests/orchestrators/hooks/test_lifecycle_hooks.py`
  - Validate: All hooks integrated with BaseOrchestrator v4.1

**Deliverables:**
- 3 hook implementations (pre-execution, post-execution, error cleanup)
- BaseOrchestrator v4.1 integration complete
- Test suite passing (100% coverage)
- Documentation updated

**Gaps Fixed:** MO-1.2.1, MO-1.2.2, MO-1.2.3 (SKULL: `GIT_CHECKPOINT_ENFORCEMENT`)

---

### 6. Phase 10 Expansion: REFACTOR Automation (18+ tasks)

**Location:** Existing Phase 10 needs expansion

**Current State:** Phase 10 exists but lacks detail

**Required Changes:** Add 18+ automated cleanup tasks

**Tasks to Add:**
1. **Task 10.1:** Automated Orphaned Function Detection & Removal (6h)
2. **Task 10.2:** Automated Duplicate Code Detection & Consolidation (8h)
3. **Task 10.3:** Unused Import Removal (2h)
4. **Task 10.4:** Code Smell Detection & Refactoring (8h)
5. **Task 10.5:** Complexity Reduction (cyclomatic ≤10) (6h)
6. **Task 10.6:** Extract Magic Numbers to Constants (4h)
7. **Task 10.7:** Type Hint Validation & Addition (4h)
8. **Task 10.8:** Docstring Completeness Check (3h)
9. **Task 10.9:** Code Formatting (Black, isort) (2h)
10. **Task 10.10:** Security Audit (bandit) (3h)
11. **Task 10.11:** Dependency Audit (safety) (2h)
12. **Task 10.12:** Remove Debug Print Statements (1h)
13. **Task 10.13:** Simplify Nested Conditionals (4h)
14. **Task 10.14:** Apply SOLID Principles (6h)
15. **Task 10.15:** Consolidate Similar Classes (4h)
16. **Task 10.16:** Extract Repeated Logic to Helpers (4h)
17. **Task 10.17:** Optimize Inefficient Loops (3h)
18. **Task 10.18:** Final Acceptance Criteria Validation (6h)

**Total Duration:** 32 hours (2 days → 4 days)

**Gaps Fixed:** TDD-3.3.1 through TDD-3.3.5, PS-2.2.5 (SKULL: `REFACTOR_CODE_CLEANUP_ENFORCEMENT`)

---

### 7. Update Visual Progress Tracker

**Location:** Top of master plan (after header)

**Changes Required:**
- Add Phase -1 to progress tracker (1h duration)
- Update Phase 6 to include Tasks 6.3.1-6.3.6 (+14h)
- Add Phase 6.5 (AST Integration, 14h)
- Renumber current Phase 7 → Phase 7 (keep name)
- Add new Phase 7.1 (Lifecycle Hooks, 14h)
- Update Phase 10 duration (16h → 32h)
- **New Timeline:** 40.5 days → 42.5 days (+2 days)

**Progress Bar Updates:**
```
Phase -1  | Knowledge Library    | 1h   | Not Started
Phase 6   | Execute Migrations   | 24d+14h → 25d | In Progress
Phase 6.5 | AST Integration      | 14h  | Not Started
Phase 7.1 | Lifecycle Hooks      | 14h  | Not Started  
Phase 10  | REFACTOR & Cleanup   | 2d → 4d | Not Started
```

---

### 8. Update FINAL-ACCEPTANCE-CRITERIA.md

**Location:** `cortex-brain/documents/planning/FINAL-ACCEPTANCE-CRITERIA.md`

**Sections to Add:**

**Section 2.4:** AST Scanning During Planning (PS-2.4.*)
- PS-2.4.1: AST scan executes in Phase 0
- PS-2.4.2: Scan results include function/class/import counts
- PS-2.4.3: Duplicate code detection runs
- PS-2.4.4: Orphaned code detection runs
- PS-2.4.5: AST findings saved to context/ast-analysis.json

**Section 1.2 (Update):** Orchestrator Lifecycle Management (MO-1.2.*)
- MO-1.2.1: Pre-execution hooks validate workspace (UPDATE)
- MO-1.2.2: Post-execution hooks create git checkpoints (UPDATE)
- MO-1.2.3: Error hooks cleanup partial artifacts (UPDATE)

**Section 3.3 (Update):** REFACTOR Phase Code Cleanup (TDD-3.3.*)
- Add 18+ task requirements
- Add automation expectations
- Add tool specifications (Pylint, Flake8, Black, bandit, etc.)

---

## 📊 Timeline Impact

| Component | Original | Updated | Change |
|-----------|----------|---------|--------|
| **Phase -1** (NEW) | 0h | 1h | +1h |
| **Phase 6.3** | Complete | +14h | +14h |
| **Phase 6.5** (NEW) | 0h | 14h | +14h |
| **Phase 7.1** (NEW) | 0h | 14h | +14h |
| **Phase 10** | 16h | 32h | +16h |
| **Total Duration** | 40.5 days | **42.5 days** | **+2 days** |

**Justification:** Necessary for 100% acceptance criteria compliance and SKULL rule adherence.

---

## 🎯 Next Actions

### Immediate (Remaining in This Session)
1. ✅ Add mandatory content blocks (DONE)
2. ✅ Insert Phase -1 (DONE)
3. ✅ Add acceptance validation tasks to Phase 6.3 (DONE)
4. ⏭️ Insert Phase 6.5 (AST Integration) in master plan
5. ⏭️ Insert Phase 7.1 (Lifecycle Hooks) in master plan
6. ⏭️ Expand Phase 10 with 18+ REFACTOR tasks
7. ⏭️ Update visual progress tracker
8. ⏭️ Update FINAL-ACCEPTANCE-CRITERIA.md

### Validation
9. ⏭️ Verify master plan structure (single master, child plans referenced)
10. ⏭️ Verify no duplicate plan documents created
11. ⏭️ Verify all gaps from brittleness analysis addressed

---

## ✅ Architecture Confirmation

**✅ CORRECT:** Master plan references child plans
**✅ CORRECT:** No deletion of child plan folders
**✅ CORRECT:** Master Orchestrator controls workflow via master plan
**✅ CORRECT:** All gaps added to MASTER plan, not scattered

**Child Plans Remain:**
- `ado-v2-migration/` (referenced by Phase 6.1)
- `vacuum-v2-migration/` (referenced by Phase 6.2)
- `cleanup-v2-migration/` (referenced by Phase 6.3)
- `guided-orchestrators-assessment/` (referenced by Phase 6.4)

These child plans provide detailed execution steps while master plan orchestrates at high level.

---

**Status:** 3 of 8 changes complete, 5 remaining  
**Next:** Insert Phase 6.5 and Phase 7.1 into master plan
