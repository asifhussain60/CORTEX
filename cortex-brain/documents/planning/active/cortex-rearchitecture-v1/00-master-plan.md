🧠 CORTEX - CORTEX Rearchitecture Master Plan
Author: Asif Hussain | GitHub: github.com/asifhussain60/CORTEX

---

# CORTEX Rearchitecture Master Plan

**Plan ID:** cortex-rearchitecture-v1  
**Date:** December 15, 2025  
**Author:** Asif Hussain  
**Status:** 📋 APPROVED → ⏳ READY FOR EXECUTION  
**Version:** 1.0.0  
**Complexity Tier:** 4 (Complex - Incremental Delivery)

---

## 🎯 Executive Summary

**User Goal:** ZERO files in folder roots across ALL CORTEX operations. Everything must be organized in semantic folders with proper lifecycle management.

**Holistic Intent:** Reorganize CORTEX architecture to follow office filing system pattern, enabling:
- Clear plan lifecycle (temp → active → completed)
- Universal subfolder structure (context/, reports/, artifacts/, tracking/)
- Visual progress tracking
- Session continuity with continuation prompts
- Historical context preservation
- All orchestrators integrated

**Scope - CORTEX Architecture ONLY:**
1. ✅ **Planning Orchestrator** - Semantic folder organization, visual tracker, continuation prompts
2. ✅ **TDD Orchestrator** - Test reports in plan folders, coverage tracking
3. ✅ **ADO Orchestrator** - ADO work items in plan structure
4. ✅ **Maintenance Orchestrator** - System maintenance plans organized
5. ✅ **Cleanup Orchestrator** - Realignment utility for existing files
6. ✅ **Brain Tier Organization** - Folder structure for Tier 1, 2, 3 captures
7. ✅ **SKULL Governance** - New rule with test harness (**COMPLETE**)
8. ✅ **Copyright Headers** - All planning documents standardized (**COMPLETE**)

**OUT OF SCOPE:**
- ❌ Cortex-Lens v3 visualization (separate plan)
- ❌ Landing page implementation
- ❌ Component extraction
- ❌ Dashboard development

---

## 📊 Visual Progress Tracker

**Overall Progress:** 2.25/14 Phases Complete (16%)

| Phase | Name | Status | Duration | Tasks | Progress |
|-------|------|--------|----------|-------|----------|
| 0 | **Governance Foundation** | ✅ COMPLETE | 4h | 3/3 | 100% |
| 1 | **Visual Tracker Migration** | ✅ COMPLETE | 1h 25m | 8/8 | 100% |
| 1.5 | Autonomous Execution Mode | ✅ COMPLETE | 4h | 7/7 | 100% |
| 1.5.7 | **Autonomous Enhancements** | ⏳ IN PROGRESS | 1.5h | 2/5 | 40% |
| 2 | Semantic Folder Organization | ⏸️ PENDING | - | 0/6 | 0% |
| 3 | Plan Lifecycle Management | ⏸️ PENDING | - | 0/7 | 0% |
| 4 | Historical Context Integration | ⏸️ PENDING | - | 0/5 | 0% |
| 5 | TDD Orchestrator Integration | ⏸️ PENDING | - | 0/4 | 0% |
| 6 | ADO Orchestrator Integration | ⏸️ PENDING | - | 0/4 | 0% |
| 7 | Maintenance Orchestrator Integration | ⏸️ PENDING | - | 0/3 | 0% |
| 8 | **File Bloat Prevention System** | 🆕 PLANNED | - | 0/5 | 0% |
| 9 | Execution Orchestrator Integration | ⏸️ PENDING | - | 0/3 | 0% |
| 10 | Cleanup Orchestrator Enhancement | ⏸️ PENDING | - | 0/4 | 0% |
| 11 | Brain Tier Organization | ⏸️ PENDING | - | 0/4 | 0% |
| 12 | Realignment Phase | ⏸️ PENDING | - | 0/5 | 0% |

**Timeline:** 26 days (14 phases × 1.9 days avg)  
**Estimated Completion:** January 10, 2026

---

## 🔄 **CONTINUATION PROMPT** (Updated: Dec 15, 6:20 PM)

**STATUS:** Phase 1.5.7 (Autonomous Enhancements) - 2/5 tasks complete (40%). Git checkpoints ✅ + Master plan minimization ✅. SKULL protection BLOCKED (need Phase 8 first).

**NEXT ACTION:** Skip to Phase 8 (File Bloat Prevention) to unblock Task 1.5.7.3, OR continue with Task 1.5.7.4 (Token Optimization).

**CONTEXT:**
- ✅ Task 1.5.7.1: Git checkpoint integration complete (12/12 tests)
- ✅ Task 1.5.7.2: Master plan minimization complete (11/11 tests)
- 🔴 Task 1.5.7.3: BLOCKED by brain-protection-rules.yaml bloat (4,385 lines)
- Sub-plan: `01-5-7-autonomous-enhancements.md`
- Related files:
  - `src/operations/modules/orchestration/temporary_plan_manager.py` (minimized master plan generator)
  - `tests/orchestrators/test_minimal_master_plan.py` (11 tests passing)
  - `cortex-brain/documents/reports/master-plan-generator-minimization-report.md`

**INSTRUCTIONS FOR CORTEX:**
```
You are continuing work on cortex-rearchitecture-v1. Phase 1.5.7 is 40% complete (2/5 tasks).

OPTION A (Recommended): Execute Phase 8 (File Bloat Prevention) to unblock SKULL protection:
1. Read 08-file-bloat-prevention-system.md
2. Refactor brain-protection-rules.yaml (4,385 → 1,500 lines)
3. Extract 75 inline rationales to markdown files
4. Fix YAML syntax errors blocking Task 1.5.7.3
5. Return to complete Task 1.5.7.3-1.5.7.5

OPTION B: Continue with Task 1.5.7.4 (Token Optimization):
1. Read 01-5-7-autonomous-enhancements.md (Task 4)
2. Create TokenOptimizer class
3. Track tokens per phase
4. Add budget warnings
5. Update progress tracker after completion

Choose option based on priority. Follow TDD workflow (RED→GREEN→REFACTOR).
```

---

## 📋 Implementation Phases

### Phase 0: Governance Foundation ✅ **COMPLETE**
**Duration:** 4 hours  
**Status:** All tasks complete, all tests passing

**Deliverables:**
- ✅ STRICT_FOLDER_ORGANIZATION_ENFORCEMENT rule in brain-protection-rules.yaml
- ✅ Semantic naming quality enforcement (intent-based folder names)
- ✅ 16 SKULL tests in tests/tier0/test_skull_strict_folder_organization.py
- ✅ BulkCopyrightUpdater utility in src/operations/utilities/bulk_operations/copyright_updater.py
- ✅ Plan folder structure created: cortex-rearchitecture-v1 with universal subfolders

**Completion Report:** `reports/governance-completion-summary.md`

---

### Phase 1: Visual Tracker Migration ✅ **COMPLETE**
**Duration:** 1 hour 25 minutes  
**Sub-plan:** `01-visual-tracker-migration.md`  
**Status:** All tasks complete, all tests passing

**Deliverables:**
- ✅ Pre-planning discovery (9/9 unit tests passing)
- ✅ PlanningSession integration with visual tracker
- ✅ Progress table rendering in user responses
- ✅ Master plan generation with embedded tracker
- ✅ 6/6 integration tests passing
- ✅ Planning System 3.0 manifest updated

**Completion Report:** `reports/phase-1-completion-report.md`

---

### Phase 1.5: Autonomous Execution Mode ✅ **COMPLETE**
**Duration:** 4 hours  
**Sub-plan:** Created dynamically during execution  
**Status:** All 7 tasks complete, 50/50 tests passing

**Deliverables:**
- ✅ Auto-progression logic with safety checks (16 tests)
- ✅ Execution mode detection (keyword-based)
- ✅ Incremental progress summaries with branding (18 tests)
- ✅ Phase transition logging
- ✅ Integration tests for autonomous flow (16 tests)
- ✅ All 50 unit tests passing (100%)

**Completion:** December 15, 2025

---

### Phase 1.5.7: Autonomous Enhancements
**Duration:** 8.5 hours estimated (1.5h complete)  
**Sub-plan:** `01-5-7-autonomous-enhancements.md`  
**Status:** ⏳ IN PROGRESS (2/5 tasks complete)

**User Requests Integration:**
1. ✅ **Git Checkpoint Integration** - COMPLETE (12/12 tests passing)
2. ✅ **Master Plan Generator Minimization** - COMPLETE (11/11 tests passing)
3. ⏳ **SKULL Protection** - BLOCKED (YAML syntax errors, need Phase 8 first)
4. ⏸️ **Token Optimization** - PENDING
5. ⏸️ **Response Template Standardization** - PENDING

**Task 1.5.7.1: Git Checkpoints** ✅ COMPLETE (30 minutes)
- ✅ `_create_phase_checkpoint()` method (47 lines)
- ✅ Checkpoint called BEFORE phase work
- ✅ Graceful degradation on git unavailability
- ✅ Metadata: phase_name, plan_id, execution_mode, version
- ✅ 12/12 unit tests passing

**Task 1.5.7.2: Master Plan Generator Minimization** ✅ COMPLETE (1 hour)
- ✅ Refactored `_generate_master_plan()` method (75% size reduction)
- ✅ ASCII progress bar with phase links to sub-plans
- ✅ Automatic continuation prompt updates after EVERY phase
- ✅ Token-conscious format (< 100 lines vs 200-300 lines)
- ✅ Single-paragraph continuation prompts (< 400 chars)
- ✅ 11/11 unit tests passing (100% coverage)
- ✅ Implementation report: `reports/master-plan-generator-minimization-report.md`

**Task 1.5.7.3: SKULL Protection** ⏳ BLOCKED
- 🔴 **BLOCKER:** brain-protection-rules.yaml has YAML syntax errors (4,385 lines, 204KB)
- ⏸️ Need to execute Phase 8 (File Bloat Prevention) FIRST
- ✅ 4 new SKULL rules designed (not yet committed)
- ✅ 19 SKULL tests created in `test_skull_protection_autonomous.py`
- ⏳ 10/18 tests passing (parse errors block 8 tests)

**Task 1.5.7.4: Token Optimization** ⏸️ PENDING (3 hours estimated)
- Create `TokenOptimizer` class
- Track tokens per phase
- Add budget warnings
- Integrate with progress summaries

**Task 1.5.7.5: Response Template** ⏸️ PENDING (2 hours estimated)
- Standardize autonomous phase completion template
- User-preferred format from Phase 1.5.4
- YAML-driven template with variables

**Key Files:**
- `src/operations/modules/orchestration/planning_orchestrator.py` (git checkpoints added)
- `src/operations/modules/orchestration/temporary_plan_manager.py` (master plan minimization)
- `tests/unit/test_git_checkpoint_integration.py` (12 tests ✅)
- `tests/orchestrators/test_minimal_master_plan.py` (11 tests ✅)
- `tests/unit/test_skull_protection_autonomous.py` (19 tests, 10 passing ⏳)
- `cortex-brain/brain-protection-rules.yaml` (needs refactoring - Phase 8)

**Expected Outcomes:**
- ✅ Git checkpoints before each phase
- ☐ SKULL protection for autonomous functionality
- ☐ Token usage tracked and optimized
- ☐ Standardized autonomous response template

**Continuation:** Execute Phase 8 (File Bloat Prevention) before completing Task 1.5.7.2

---

### Phase 2: Semantic Folder Organization
**Duration:** 2 days  
**Sub-plan:** `02-semantic-folder-organization.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Replace _generate_plan_path() with semantic folder logic
2. Add auto-versioning (v1, v2, v3)
3. Create universal subfolders (context/, reports/, artifacts/, tracking/)
4. Initialize progress tracker automatically
5. Implement tier-based routing (temp-plans/ vs active/)
6. Add _detect_next_version() method

**Key Files:**
- `src/operations/modules/orchestration/planning_orchestrator.py` (_generate_plan_path method)
- Tests: `tests/orchestrators/test_planning_orchestrator.py`

**Expected Outcomes:**
- ✅ Temp plans (tier 1-2) in temp-plans/{plan-id}/
- ✅ Active plans (tier 3-4) in active/{feature-name-v1}/
- ✅ Auto-versioning working correctly
- ✅ Universal subfolders created automatically

---

### Phase 3: Plan Lifecycle Management
**Duration:** 2 days  
**Sub-plan:** `03-plan-lifecycle-management.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Implement approve_temporary_plan() method
2. Parse phases from temporary plan
3. Generate master plan with visual tracker
4. Generate sub-plans (01-, 02-, etc.)
5. Move temp-plans/ → active/ on approval
6. Initialize continuation prompt system
7. Delete temporary plan after conversion

**Key Files:**
- `src/operations/modules/orchestration/planning_orchestrator.py`
- Tests: `tests/orchestrators/test_planning_orchestrator.py`

**Expected Outcomes:**
- ✅ Temp → Active workflow automated
- ✅ Master + sub-plans generated
- ✅ Continuation prompts initialized
- ✅ Visual tracker embedded in master plan

---

### Phase 4: Historical Context Integration
**Duration:** 2 days  
**Sub-plan:** `04-historical-context-integration.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Integrate git history gathering
2. Integrate AST analysis
3. Extract comments and TODOs
4. Generate code dependency graph
5. Store all context in context/ subfolder

**Key Files:**
- `src/operations/modules/orchestration/planning_orchestrator.py`
- `src/tier3/` (git, AST analysis modules)
- Tests: `tests/orchestrators/test_planning_orchestrator.py`

**Expected Outcomes:**
- ✅ Git history in context/git-history.yaml
- ✅ AST analysis in context/ast-analysis.yaml
- ✅ Comments in context/comments.yaml
- ✅ Code graph in context/code-graph.json

---

### Phase 5: TDD Orchestrator Integration
**Duration:** 2 days  
**Sub-plan:** `05-tdd-orchestrator-integration.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Store test execution reports in plan-folder/reports/
2. Track coverage in plan-folder/tracking/tdd-coverage.json
3. Link test results to phase tracking
4. Update progress tracker after test runs

**Key Files:**
- `src/operations/modules/orchestration/tdd_orchestrator.py`
- Tests: `tests/orchestrators/test_tdd_orchestrator.py`

**Expected Outcomes:**
- ✅ Test reports in plan reports/ folder
- ✅ Coverage tracked per phase
- ✅ Progress tracker updated with test status

---

### Phase 6: ADO Orchestrator Integration
**Duration:** 2 days  
**Sub-plan:** `06-ado-orchestrator-integration.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Apply same folder organization as planning_orchestrator
2. Store ADO summaries in reports/
3. Track ADO item IDs in tracking/
4. Generate ADO-formatted work items from plans

**Key Files:**
- `src/operations/modules/orchestration/ado_planning_orchestrator.py`
- Tests: `tests/orchestrators/test_ado_orchestrator.py`

**Expected Outcomes:**
- ✅ ADO plans follow same structure
- ✅ ADO summaries in reports/
- ✅ ADO item IDs tracked

---

### Phase 7: Maintenance Orchestrator Integration
**Duration:** 1 day  
**Sub-plan:** `07-maintenance-orchestrator-integration.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Create maintenance plans in planning/system-maintenance-v{N}/
2. Track maintenance metrics in tracking/maintenance-metrics.json
3. Generate maintenance reports

**Key Files:**
- `src/operations/modules/orchestration/maintenance_orchestrator_v3.py`
- Tests: `tests/orchestrators/test_maintenance_orchestrator.py`

**Expected Outcomes:**
- ✅ Maintenance plans organized
- ✅ Metrics tracked per maintenance run

---

### Phase 8: File Bloat Prevention System
**Duration:** 7 days  
**Sub-plan:** `08-file-bloat-prevention-system.md`  
**Status:** 🆕 PLANNED (blocking Phase 1.5.7 Task 2)

**Problem Statement:**
- `brain-protection-rules.yaml`: 4,385 lines (204KB) - 75 inline rationales
- `planning_orchestrator.py`: 1,800+ lines (70KB)
- `response-templates.yaml`: 50KB+
- Multiple large JSON analysis files (50KB+)

**Objectives:**
1. **Bloat Detection System** - Automated scanning with thresholds
2. **YAML Refactoring** - Extract 75 inline rationales to markdown files
3. **Python Module Decomposition** - Break planning_orchestrator into 7 modules
4. **Pre-Commit Hook** - Prevent future bloat automatically
5. **JSON Cleanup** - Archive duplicate analysis files

**Key Deliverables:**
- `src/operations/modules/quality/bloat_detector.py` (automated detection)
- `cortex-brain/documents/rationales/*.md` (75 extracted rationales)
- `src/operations/modules/orchestration/planning/*.py` (7 decomposed modules)
- `.git/hooks/pre-commit` (bloat prevention hook)
- New SKULL rule: `FILE_BLOAT_PREVENTION_ENFORCEMENT`

**Success Metrics:**
- brain-protection-rules.yaml: 4,385 → 1,500 lines (65% reduction)
- planning_orchestrator.py: 1,800 → 500 lines (72% reduction)
- All rationales use `#file:` references (DRY principle)
- Pre-commit hook prevents files > thresholds

**Priority:** HIGH (blocks Phase 1.5.7 Task 2 - SKULL protection)

**Key Files:**
- `cortex-brain/brain-protection-rules.yaml` (refactor target)
- `src/operations/modules/orchestration/planning_orchestrator.py` (decompose target)
- Tests: `tests/quality/test_bloat_detector.py`

**Expected Outcomes:**
- ✅ Files decomposed and maintainable
- ✅ YAML parsing faster (< 100ms vs current ~200ms)
- ✅ Automated bloat detection in CI/CD
- ✅ No module > 1,000 lines

---

### Phase 9: Execution Orchestrator Integration
**Duration:** 1 day  
**Sub-plan:** `08-execution-orchestrator-integration.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Store execution reports in plan-folder/reports/
2. Track execution progress in tracking/
3. Update continuation prompts after each phase

**Key Files:**
- `src/operations/modules/orchestration/execution_orchestrator.py`
- Tests: `tests/orchestrators/test_execution_orchestrator.py`

**Expected Outcomes:**
- ✅ Execution reports per phase
- ✅ Progress tracker updated in real-time

---

### Phase 9: Execution Orchestrator Integration
**Duration:** 1 day  
**Sub-plan:** `09-execution-orchestrator-integration.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Store execution reports in plan-folder/reports/
2. Track execution progress in tracking/
3. Update continuation prompts after each phase

**Key Files:**
- `src/operations/modules/orchestration/execution_orchestrator.py`
- Tests: `tests/orchestrators/test_execution_orchestrator.py`

**Expected Outcomes:**
- ✅ Execution reports per phase
- ✅ Progress tracker updated in real-time

---

### Phase 10: Cleanup Orchestrator Enhancement
**Duration:** 2 days  
**Sub-plan:** `09-cleanup-orchestrator-enhancement.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Rename to StrictFolderRealignmentOrchestrator
2. Realign existing files to strict folder organization
3. Generate cleanup reports
4. Delete obsolete files

**Key Files:**
- `src/operations/modules/orchestration/cleanup_orchestrator.py`
- Tests: `tests/orchestrators/test_cleanup_orchestrator.py`

**Expected Outcomes:**
- ✅ Existing files realigned
- ✅ Cleanup reports generated
- ✅ No orphaned files

---

### Phase 10: Cleanup Orchestrator Enhancement
**Duration:** 2 days  
**Sub-plan:** `10-cleanup-orchestrator-enhancement.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Rename to StrictFolderRealignmentOrchestrator
2. Realign existing files to strict folder organization
3. Generate cleanup reports
4. Delete obsolete files

**Key Files:**
- `src/operations/modules/orchestration/cleanup_orchestrator.py`
- Tests: `tests/orchestrators/test_cleanup_orchestrator.py`

**Expected Outcomes:**
- ✅ Existing files realigned
- ✅ Cleanup reports generated
- ✅ No orphaned files

---

### Phase 11: Brain Tier Organization
**Duration:** 2 days  
**Sub-plan:** `10-brain-tier-organization.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Create folder structure for Tier 1, 2, 3 captures
2. Organize tier-specific documents
3. Update tier README files
4. Migrate existing tier documents

**Key Files:**
- `cortex-brain/tier1/`, `tier2/`, `tier3/`
- Tests: `tests/tier1/`, `tests/tier2/`, `tests/tier3/`

**Expected Outcomes:**
- ✅ Tier folders organized
- ✅ Documents properly categorized
- ✅ README files updated

---

### Phase 11: Brain Tier Organization
**Duration:** 2 days  
**Sub-plan:** `11-brain-tier-organization.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Create folder structure for Tier 1, 2, 3 captures
2. Organize tier-specific documents
3. Update tier README files
4. Migrate existing tier documents

**Key Files:**
- `cortex-brain/tier1/`, `tier2/`, `tier3/`
- Tests: `tests/tier1/`, `tests/tier2/`, `tests/tier3/`

**Expected Outcomes:**
- ✅ Tier folders organized
- ✅ Documents properly categorized
- ✅ README files updated

---

### Phase 12: Realignment Phase
**Duration:** 2 days  
**Sub-plan:** `11-realignment-phase.md`  
**Status:** ⏸️ PENDING

**Objectives:**
1. Scan cortex-brain/documents/ recursively
2. Realign ALL existing files to new structure
3. Add copyright headers where missing
4. Delete obsolete/orphaned files
5. Generate realignment report

**Key Files:**
- `src/operations/utilities/bulk_operations/copyright_updater.py` (already exists)
- Tests: `tests/utilities/test_copyright_updater.py`

**Expected Outcomes:**
- ✅ All files in proper folders
- ✅ Copyright headers added
- ✅ No root-level files (except README, schemas)
- ✅ Realignment report generated

---

## 📁 Folder Structure

```
cortex-rearchitecture-v1/
├── 00-master-plan.md (this file)
├── 01-visual-tracker-migration.md
├── 02-semantic-folder-organization.md
├── 03-plan-lifecycle-management.md
├── 04-historical-context-integration.md
├── 05-tdd-orchestrator-integration.md
├── 06-ado-orchestrator-integration.md
├── 07-maintenance-orchestrator-integration.md
├── 08-execution-orchestrator-integration.md
├── 09-cleanup-orchestrator-enhancement.md
├── 10-brain-tier-organization.md
├── 11-realignment-phase.md
├── context/
│   ├── governance-completion-summary.md (Phase 0 outcomes)
│   └── README.md (context artifacts index)
├── reports/
│   └── (execution reports will be generated here)
├── artifacts/
│   └── (implementation artifacts will be stored here)
└── tracking/
    └── progress-tracker.json (real-time progress)
```

---

## 🔗 Related Documentation

- **Original Plan:** `cortex-brain/documents/reports/STRICT-FOLDER-ORGANIZATION-ENFORCEMENT-PLAN-2025-12-15.md`
- **SKULL Rule:** `cortex-brain/brain-protection-rules.yaml` (STRICT_FOLDER_ORGANIZATION_ENFORCEMENT)
- **SKULL Tests:** `tests/tier0/test_skull_strict_folder_organization.py`
- **Copyright Utility:** `src/operations/utilities/bulk_operations/copyright_updater.py`
- **Planning System 2.0 Manifest:** `cortex-brain/orchestrator-manifests/planning-system-2.0-manifest.yaml`

---

## 📝 Notes

**Implementation Strategy:**
- Follow incremental delivery (complexity tier 4)
- Each phase produces working code with tests
- TDD workflow mandatory (RED→GREEN→REFACTOR)
- Update continuation prompt after each phase
- Generate execution report after each phase

**Success Criteria:**
- ✅ All SKULL tests passing (16/16)
- ✅ Zero files in planning/ root (except README, schemas)
- ✅ All orchestrators integrated
- ✅ Visual tracker functional
- ✅ Continuation prompts working
- ✅ Historical context preserved

**Risk Mitigation:**
- Git checkpoints after each phase
- Rollback plan if tests fail
- Incremental deployment to avoid big-bang issues

---

**Last Updated:** December 15, 2025, 3:00 PM  
**Next Update:** After Phase 1 completion
