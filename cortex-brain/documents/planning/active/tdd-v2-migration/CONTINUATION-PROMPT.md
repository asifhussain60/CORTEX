# Phase 6.5 Continuation Prompt: TDD Orchestrator v2 Migration

**Date:** January 3, 2026  
**Plan:** `tdd-v2-migration`  
**Status:** NOT STARTED  
**Next Action:** Begin Day 1 - Core TDDOrchestratorV2 + TestRunnerAbstraction

---

## 🎯 Where We Are

**Phase 6.5 Status:** Plan created, ready to begin implementation

**Context:**
- Phase 6.4 (GUIDED Orchestrators Assessment) completed January 2, 2026
- TDD Orchestrator scored 8.85/10 → AUTONOMOUS migration APPROVED
- Decision based on: Complex state machine (10/10), reusable components (9/10), integration dependencies (10/10)
- 4-day migration plan created
- Week 1 of 3-week migration roadmap (TDD → Debug → Sanitization)

---

## 📋 What's Next

### Immediate: Day 1 - Core TDDOrchestratorV2 + TestRunnerAbstraction (8 hours)

**Morning Tasks (4h):**
1. Create `src/orchestrators/tdd/` directory structure
2. Implement `TDDOrchestratorV2` class extending `BaseOrchestrator v4.1`
3. Define phase enum (`RED`, `GREEN`, `REFACTOR`, `CHECKPOINT`, `COMPLETE`)
4. Implement `execute()` method with state machine dispatcher
5. Connect to Planning State DB

**Afternoon Tasks (4h):**
6. Create `TestRunnerAbstraction` base class
7. Implement `PytestAdapter` (primary framework)
8. Implement `UnittestAdapter` (secondary framework)
9. Test discovery logic (file patterns, naming conventions)
10. Basic test execution (run, capture output, parse results)
11. Write unit tests for adapters (50+ tests)

**Deliverables:**
- `src/orchestrators/tdd/tdd_orchestrator_v2.py` (~200 lines)
- `src/orchestrators/tdd/test_runner_abstraction.py` (~300 lines)
- `tests/orchestrators/tdd/test_test_runner_abstraction.py` (50+ tests)

**Success Criteria:**
- TDDOrchestratorV2 instantiates successfully
- TestRunnerAbstraction can execute pytest/unittest tests
- State DB connection established

---

## 📚 Key Context Files

### Planning Documents
- **Master Plan:** `cortex-brain/documents/planning/active/tdd-v2-migration/00-MASTER-PLAN.md`
- **Progress Tracker:** `cortex-brain/documents/planning/active/tdd-v2-migration/tracking/progress.json`
- **Phase 6.4 Assessment:** `cortex-brain/documents/planning/active/guided-orchestrators-assessment/artifacts/strategic-recommendations.md` (lines 65-150)

### Reference Code
- **BaseOrchestrator v4.1:** `src/orchestrators/base/base_orchestrator_v4_1.py` (685 lines)
- **Existing TDD Manifest:** `cortex-brain/manifests/orchestrators/tdd-orchestrator-v4-manifest.yaml`
- **Planning State DB:** `cortex-brain/database/planning_state.db`

### Architecture Reference
- **MCP Server Config:** `cortex-brain/config/mcp-server.yaml` (register TDDOrchestratorV2 here on Day 4)
- **Master Orchestrator:** `src/orchestrators/master_orchestrator.py` (update routing on Day 4)
- **CLI Bridge:** `scripts/cortex-cli.py` (test invocation on Day 4)

---

## 🎨 Design Decisions (From Phase 6.4)

### Why AUTONOMOUS?
1. **Complex State Machine:** RED→GREEN→REFACTOR cycle requires transactional state (10/10)
2. **Reusable Components:** TestRunnerAbstraction benefits 3+ orchestrators (9/10)
3. **Integration Dependencies:** Master Orchestrator, Git Checkpoint, State DB (10/10)
4. **Multi-Phase State:** Requires rollback, checkpointing, session persistence (10/10)

### Key Features
- **Test Framework Abstraction:** Unified interface for pytest, unittest, nose
- **Atomic Rollback:** REFACTOR failure triggers automatic rollback to GREEN state
- **Git Checkpointing:** Automatic commits on GREEN/REFACTOR success
- **Session Persistence:** Multi-session support via Planning State DB
- **Master Orchestrator Integration:** Routes `start tdd`, `run tests`, `continue tdd`

---

## 🛡️ SKULL Rules to Enforce

### TDD_ENFORCEMENT
- Tests must fail before implementation (RED phase validation)
- Tests must pass before refactoring (GREEN phase gate)
- Atomic rollback enforced on REFACTOR failure

### HOLISTIC_DISCOVERY
- Test file discovery before creation (prevent duplication)
- Search for existing test patterns
- Reuse TestRunnerAbstraction across orchestrators

### REFACTOR_CLEANUP
- REFACTOR phase removes unused imports, dead code
- Quality checks enforce code standards
- Whole-file cleanup on completion

---

## 🚀 How to Continue

### Option 1: Begin Day 1 (Recommended)
Say: **"begin day 1"** or **"start tdd migration day 1"**

CORTEX will:
1. Create `src/orchestrators/tdd/` directory
2. Implement TDDOrchestratorV2 scaffolding
3. Implement TestRunnerAbstraction with pytest/unittest adapters
4. Write unit tests (50+)
5. Update progress tracker

### Option 2: Review Plan
Say: **"review tdd migration plan"** or **"show master plan"**

CORTEX will display:
- Full 4-day implementation breakdown
- Success criteria
- Integration points
- Risk mitigation

### Option 3: Context Questions
Ask: **"what is TestRunnerAbstraction?"** or **"why autonomous instead of guided?"**

CORTEX will explain design decisions from Phase 6.4 assessment.

---

## 📊 Progress Tracking

**Current State:**
- Day 1: 0% (not started)
- Day 2: 0% (not started)
- Day 3: 0% (not started)
- Day 4: 0% (not started)
- Overall: 0%

**After Day 1 Completion:**
- Day 1: 100% (TDDOrchestratorV2 scaffolding + TestRunnerAbstraction complete)
- Overall: 25%

---

## ⏭️ Subsequent Days (Preview)

### Day 2: RED Phase Automation
- Implement `execute_red_phase()` method
- Test failure detection and categorization
- Baseline recording in State DB
- 30+ unit tests

### Day 3: GREEN Phase Automation
- Implement `execute_green_phase()` method
- Test pass verification
- Git checkpoint creation
- Coverage tracking
- 30+ unit tests

### Day 4: REFACTOR Phase + Integration
- Implement `execute_refactor_phase()` method
- Code quality checks (pylint, mypy)
- Atomic rollback
- MCP registration
- Master Orchestrator routing
- CLI bridge testing
- Integration tests (end-to-end)

---

## 🎯 Success at End of Day 1

You'll know Day 1 is complete when:
- ✅ TDDOrchestratorV2 class exists and extends BaseOrchestrator v4.1
- ✅ Phase enum defined (`RED`, `GREEN`, `REFACTOR`, etc.)
- ✅ TestRunnerAbstraction base class implemented
- ✅ PytestAdapter and UnittestAdapter functional
- ✅ Test discovery logic working
- ✅ 50+ unit tests passing
- ✅ State DB connection established

---

**Ready to begin Day 1? Say "begin day 1" to start!**

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
