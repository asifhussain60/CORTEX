# 🎯 C50-03: Phase -1 Knowledge Library + Runtime Governance Implementation

**Sub-Plan ID:** C50-03  
**Order:** 03  
**Type:** Feature + Gap Remediation  
**Priority:** HIGH  
**Duration:** 3-4 days  
**Status:** 🔒 BLOCKED (awaiting C50-00C completion)

---

## 📊 Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏳ NOT STARTED

| Phase | Status | Duration | Progress |
|-------|--------|----------|----------|
| **Phase -2:** Setup Verification | ⏳ Not Started | 10min | `░░░░░░░░░░` 0% |
| **Phase 0:** Knowledge Library | ⏳ Not Started | 1d | `░░░░░░░░░░` 0% |
| **Phase 1:** Runtime Governance Middleware | ⏳ Not Started | 1.5d | `░░░░░░░░░░` 0% |
| **Phase 2:** Integration + Testing | ⏳ Not Started | 1d | `░░░░░░░░░░` 0% |
| **Phase 999:** Teardown + REFACTOR + Commit | ⏳ Not Started | 20min | `░░░░░░░░░░` 0% |

---

## 🎯 Objectives

### Primary Objective
Implement Phase -1 Knowledge Library for pre-planning knowledge discovery with AST scanning, pattern detection, and duplication analysis.

### Gap Remediation Objective (Gap 2)
**Gap 2: Runtime Governance Enforcement**  
Implement continuous governance validation (not just Phase -1) with `governance_checkpoint.py` middleware integrated into Master Orchestrator lifecycle.

---

## 📋 Phase Details

### Phase -2: Setup Verification (NEW - CORTEX v5 Universal Pattern)

**Duration:** 10 minutes  
**Purpose:** Verify dependencies are ACTUALLY complete, not just present

**Tasks:**
1. ✅ **Run Setup Verifier** (`setup_verification.py`)
   - Validate C50-00C completion (test coverage ≥80%)
   - Implementation test: Import `planning_orchestrator_v5.py` successfully
   - Check VSCode cache state (clear if >30 days old or brittle)
   - Validate governance compliance

2. ✅ **False Positive Detection**
   - Verify C50-00C tests ACTUALLY pass (not just exist)
   - Run: `pytest tests/orchestrators/planning/ -v`
   - Expected: 100% pass rate

3. ✅ **Cache Check**
   - Check `.vscode/cache/` age
   - Clear cache if:
     - Age > 30 days
     - Test failures detected
     - Size > 100MB

**Exit Criteria:**
- Setup verification report generated (`analysis/setup-verification-report.md`)
- All dependencies validated as functional
- No false positives detected
- Cache state optimal

---

### Phase 0: Knowledge Library Implementation

**Duration:** 1 day  
**Purpose:** Pre-planning knowledge discovery

**Tasks:**
1. **AST Scanning Integration**
   - Create `src/cortex_agents/knowledge_library.py`
   - Implement `scan_workspace()` method
   - Extract classes, functions, imports, patterns

2. **Pattern Detection**
   - Detect duplicate code
   - Detect architectural patterns
   - Detect potential refactoring opportunities

3. **Knowledge Graph Integration**
   - Query Tier 2 (`cortex-brain/knowledge-graph.yaml`)
   - Enrich context with historical patterns
   - Risk analysis from `lessons-learned.yaml`

**Exit Criteria:**
- Knowledge library operational
- AST scanning tested on 10+ files
- Pattern detection accuracy >80%

---

### Phase 1: Runtime Governance Middleware (🔴 GAP 2 REMEDIATION)

**Duration:** 1.5 days  
**Purpose:** Implement continuous governance validation

**Tasks:**
1. **Create Governance Checkpoint Module**
   ```
   File: src/orchestrators/middleware/governance_checkpoint.py
   ```
   - Load SKULL rules from `brain-protection-rules.yaml`
   - Implement `checkpoint_phase_start(phase_number)` method
   - Implement `checkpoint_phase_operations(operation_name)` method
   - Implement `checkpoint_phase_complete(phase_number)` method

2. **Governance Audit Trail**
   ```
   File: tracking/governance-audit.jsonl
   Schema:
   {
     "timestamp": "2026-01-04T12:00:00",
     "orchestrator": "planning_v5",
     "phase": 2,
     "checkpoint_type": "phase_start",
     "rules_validated": ["TDD_ENFORCEMENT", "PLANNING_ISOLATION"],
     "violations": [],
     "status": "PASSED"
   }
   ```

3. **Master Orchestrator Integration**
   - Update `master-orchestrator.yaml` lifecycle hooks (✅ ALREADY DONE)
   - Integrate `governance_checkpoint` into pre_execution (priority 20)
   - Integrate `governance_checkpoint` into post_execution (priority 20)

4. **SKULL Rules Enforcement**
   - Validate 6 core rules at runtime:
     - `TDD_ENFORCEMENT`
     - `PLANNING_ISOLATION`
     - `GIT_ISOLATION`
     - `HOLISTIC_DISCOVERY`
     - `SETUP_VERIFICATION`
     - `TEARDOWN_REFACTOR`

**Exit Criteria:**
- `governance_checkpoint.py` created with 3 methods
- Governance audit trail operational (`governance-audit.jsonl`)
- Master Orchestrator integrated
- Unit tests: 100% coverage for governance middleware
- Runtime governance validated in 1 orchestrator execution

---

### Phase 2: Integration + Testing

**Duration:** 1 day  
**Purpose:** Integrate knowledge library with planning system, test end-to-end

**Tasks:**
1. **Planning v5 Integration**
   - Add Phase -1 to `planning-system-5.0-manifest.yaml` (✅ CONFIG DONE)
   - Implement Phase -1 logic in `planning_orchestrator_v5.py`
   - Knowledge library runs BEFORE Phase 0 (Context Discovery)

2. **End-to-End Testing**
   - Create plan with Phase -1 enabled
   - Verify knowledge library discovers patterns
   - Verify governance checkpoints fire at phase boundaries
   - Verify audit trail logs all governance decisions

3. **Documentation**
   - Update `CORTEX.prompt.md` with Phase -1 guidance
   - Update brain-protection-rules.yaml with new rules

**Exit Criteria:**
- Phase -1 operational in Planning v5
- Runtime governance tested in full orchestrator execution
- Documentation complete

---

### Phase 999: Teardown + REFACTOR + Commit (NEW - CORTEX v5 Universal Pattern)

**Duration:** 20 minutes  
**Purpose:** Whole-file cleanup and git commit

**Tasks:**
1. ✅ **REFACTOR Cycle**
   - Run `teardown_refactor.py` on all modified files:
     - `src/orchestrators/middleware/governance_checkpoint.py`
     - `src/cortex_agents/knowledge_library.py`
     - `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
   - Remove unused imports
   - Remove orphaned code
   - Consolidate duplicate logic
   - Format code (black)

2. ✅ **Git Commit** (`/cortex-git-commit` pattern)
   ```
   Message Template:
   
   C50-03: Knowledge Library + Runtime Governance Middleware
   
   Phase -1 knowledge library with AST scanning operational.
   Runtime governance middleware (Gap 2 remediation) complete.
   
   Files modified: 5
   Tests added: 25
   Coverage: +15% (governance middleware)
   
   Gap 2 remediation:
   - governance_checkpoint.py created
   - 3 checkpoint methods implemented
   - Governance audit trail operational
   - SKULL rules enforced at runtime
   
   Co-authored-by: CORTEX v5 <cortex@asifhussain.dev>
   ```

3. ✅ **Teardown Report**
   - Generate `reports/teardown-report.md`
   - Summary of refactor changes
   - Git commit SHA

**Exit Criteria:**
- All files refactored and cleaned
- Git commit successful with Phase N+1 pattern
- Teardown report generated

---

## 🎯 Acceptance Criteria (DoD)

### Knowledge Library
- ✅ AST scanning operational
- ✅ Pattern detection accuracy >80%
- ✅ Integration with Tier 2 knowledge graph

### Gap 2 Remediation
- ✅ `governance_checkpoint.py` created with 3 methods
- ✅ Runtime governance integrated into Master Orchestrator lifecycle
- ✅ Governance audit trail operational (`governance-audit.jsonl`)
- ✅ SKULL rules enforced at phase start/operations/completion
- ✅ Unit tests: 100% coverage for governance middleware

### Setup/Teardown
- ✅ Phase -2 setup verification passed
- ✅ Phase 999 teardown + REFACTOR completed
- ✅ Git commit with /cortex-git-commit pattern

### Quality
- ✅ Test coverage: 100% for new code
- ✅ All tests passing
- ✅ Documentation complete

---

## 📚 References

**Gap Analysis:**
- `cortex-brain/documents/analysis/c50-master-orchestrator-gaps.md` (Gap 2 section)

**CORTEX-5.0 Backup:**
- `cortex-brain/documents/planning/backups/CORTEX-5.0-acceptance-criteria-backup-20260104/03-knowledge-library-phase/implementation-guide.md`

**Manifests:**
- `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml` (governance config)
- `cortex-brain/config/master-orchestrator.yaml` (lifecycle hooks)

**Brain Protection:**
- `cortex-brain/brain-protection-rules.yaml` (SKULL rules)

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
