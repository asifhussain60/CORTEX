# CORTEX Autonomous Waves L-O Execution Guide
**Version:** 1.0 | **Date:** 2026-02-12 | **Authority:** cortex-architect.prompt.md v15.3  
**Status:** READY FOR EXECUTION | **Waves Ready:** 4 (L, M, N, O)

---

## 🎯 Overview

This guide provides end-to-end instructions for executing WAVE-L through WAVE-O autonomously within GitHub Copilot Chat sessions. All 4 waves are **READY** with no blockers after completing WAVE-100 and Wave 7.

---

## ✅ Prerequisites Verification

**Before starting WAVE-L, verify:**

```bash
# 1. Check current branch and status
git status
# Expected: On branch CORTEX, clean working tree

# 2. Verify latest commits
git log --oneline -5
# Expected: 7714c27fb (HEAD -> CORTEX) docs: Add MCP tool detection validation report

# 3. Verify WAVE-K completion (prerequisite for WAVE-L)
git log --oneline --all | grep "WAVE-K"
# Expected: bae5b4959 WAVE-K COMPLETE: Architecture alignment verification

# 4. Check Python environment
python --version
# Expected: Python 3.9+ (3.9.6 recommended)

# 5. Verify virtual environment active
echo $VIRTUAL_ENV
# Expected: /path/to/CORTEX/.venv

# 6. Quick test health check
pytest tests/unit/governance/compliance/ -v --tb=short
# Expected: 20/20 tests passing (WAVE-K deliverables)
```

**If any prerequisite fails:**
- Clean working tree: `git stash` or commit changes
- Missing commits: `git pull origin CORTEX`
- Virtual env: `source .venv/bin/activate` (macOS/Linux) or `.venv\Scripts\activate` (Windows)

---

## 📋 Wave Execution Order

| Wave | Name | Duration | Token Budget | Tests | Priority |
|------|------|----------|--------------|-------|----------|
| **L** | Agent Architecture | 4 hours | 180k | 25 | Execute first |
| **M** | Language Refinement | 3 hours | 160k | 20 | After L |
| **N** | Autonomous Execution | 4 hours | 190k | 25 | After M |
| **O** | Data Integrity | 4 hours | 200k | 30 | After N (completes Wave 3) |

**Total Estimated Time:** 15 hours (4 sessions)  
**Milestone:** Wave 3 Autonomy Complete (Intelligence + Execution + Trust)

---

## 🚀 WAVE-L: Agent Architecture Redesign

### Context

**Goal:** Reduce agent loading overhead from 245k tokens → ~95k tokens (60% reduction)  
**Problem:** All 11 agents currently loaded at session start  
**Solution:** Intent-based lazy loading (load only required agents per request)

**Files to Create:**
- `cortex/agents/lazy_loader.py`
- `cortex/agents/interaction_patterns.py`
- `tests/unit/agents/test_lazy_loading.py` (15 tests)
- `tests/integration/test_agent_orchestrator.py` (10 tests)

### Autonomous Command

```
/implement WAVE-L: phase-81 Agent Architecture Redesign S1-S3

Authority: cortex-registry/_cortex-master/index.yaml v3.0
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-L-20260213-01
Token Budget: <180k tokens
```

### Expected Execution Flow

```
[████░░░░░░] 20% S1: Lazy Loading System
├─ ✅ cortex/agents/lazy_loader.py created
├─ ✅ IntentAgentMapper class implemented
├─ 🔵 15 unit tests (RED phase)
└─ ⚪ GREEN phase pending

[████████░░] 60% S2: Agent-Orchestrator Patterns
├─ ✅ S1 complete (15/15 tests passing)
├─ ✅ cortex/agents/interaction_patterns.py created
├─ 🔵 10 integration tests (RED phase)
└─ ⚪ GREEN phase pending

[██████████] 100% S3: Documentation + Verification
├─ ✅ S2 complete (25/25 tests passing)
├─ ✅ .github/prompts/AGENT-INTEGRATION-GUIDE.md created
├─ ✅ Token reduction verified (245k → 92k actual)
└─ ✅ 3 commits pushed
```

### Success Criteria

- ✅ **25/25 tests passing** (0 failures)
- ✅ **3 commits pushed** to CORTEX branch
- ✅ **Token reduction ≥50%** (validated via test - realistically 60-65%)
- ✅ **All 11 agents functional** via lazy loading
- ✅ **No regression** in agent capabilities

### Verification Commands

```bash
# After completion, verify:

# 1. Tests passing
pytest tests/unit/agents/test_lazy_loading.py -v
pytest tests/integration/test_agent_orchestrator.py -v
# Expected: 25/25 passing

# 2. Token reduction measurement
python -c "
from cortex.agents.lazy_loader import IntentAgentMapper
mapper = IntentAgentMapper()
print(f'IMPLEMENT intent agents: {len(mapper.get_agents_for_intent(\"IMPLEMENT\"))}')
print(f'ANALYZE intent agents: {len(mapper.get_agents_for_intent(\"ANALYZE\"))}')
# Expected: 2-3 agents per intent (vs 11 previously)
"

# 3. Files created
ls -lh cortex/agents/lazy_loader.py cortex/agents/interaction_patterns.py
# Expected: Both files exist

# 4. Commits pushed
git log --oneline -3
# Expected: 3 new commits for WAVE-L stages
```

---

## 🚀 WAVE-M: Language Refinement

### Context

**Goal:** Improve intent classification accuracy from 65% → 90%  
**Problem:** Too many clarification requests (40% of interactions)  
**Solution:** Enhanced NLP pipeline + confidence scoring + context accumulation

**Files to Create:**
- `cortex/intelligence/intent_classifier_v2.py`
- `cortex/intelligence/clarification_reducer.py`
- `cortex/intelligence/nlp_pipeline.py`
- `tests/unit/intelligence/test_intent_classification.py` (12 tests)
- `tests/integration/test_clarification_flow.py` (8 tests)

### Autonomous Command

```
/implement WAVE-M: ENH-078 Language Refinement Complete

Authority: cortex-registry/_cortex-master/index.yaml v3.0
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-M-20260214-01
Token Budget: <160k tokens
```

### Expected Execution Flow

```
[████░░░░░░] 25% S1: Enhanced Intent Classifier
├─ ✅ cortex/intelligence/intent_classifier_v2.py created
├─ 🔵 12 unit tests (RED phase)
└─ ⚪ Confidence scoring implementation

[██████░░░░] 60% S2: Clarification Reducer
├─ ✅ S1 complete (12/12 tests passing)
├─ ✅ cortex/intelligence/clarification_reducer.py created
├─ 🔵 8 integration tests (RED phase)
└─ ⚪ Context accumulation logic

[██████████] 100% S3: Documentation + Metrics
├─ ✅ S2 complete (20/20 tests passing)
├─ ✅ 90% accuracy benchmark passing
├─ ✅ <15% clarification rate validated
└─ ✅ 2 commits pushed
```

### Success Criteria

- ✅ **20/20 tests passing** (0 failures)
- ✅ **2 commits pushed**
- ✅ **Intent accuracy ≥90%** (validated via benchmark test)
- ✅ **Clarification rate <15%** (validated via integration test)
- ✅ **No regression** in existing intent detection

### Verification Commands

```bash
# After completion, verify:

# 1. Accuracy benchmark
pytest tests/unit/intelligence/test_intent_classification.py::test_accuracy_benchmark_90_percent -v
# Expected: PASSED

# 2. Clarification rate
pytest tests/integration/test_clarification_flow.py::test_clarification_rate_below_15_percent -v
# Expected: PASSED

# 3. Sample classification
python -c "
from cortex.intelligence.intent_classifier_v2 import IntentClassifierV2
classifier = IntentClassifierV2()
result = classifier.classify('implement user authentication')
print(f'Intent: {result.intent}, Confidence: {result.confidence:.2f}')
# Expected: Intent: IMPLEMENT, Confidence: >0.85
"
```

---

## 🚀 WAVE-N: Autonomous Plan Execution

### Context

**Goal:** True "approve → done" workflow with no mid-execution prompts  
**Problem:** Multi-stage plans require manual intervention between stages  
**Solution:** Autonomous execution engine + progress tracking + rollback system

**Files to Create:**
- `cortex/execution/autonomous_executor.py`
- `cortex/execution/progress_tracker.py`
- `cortex/execution/rollback_manager.py`
- `tests/unit/execution/test_autonomous_executor.py` (15 tests)
- `tests/integration/test_approve_to_done_flow.py` (10 tests)

### Autonomous Command

```
/implement WAVE-N: ENH-067 Autonomous Plan Execution

Authority: cortex-registry/_cortex-master/index.yaml v3.0
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-N-20260215-01
Token Budget: <190k tokens
```

### Expected Execution Flow

```
[████░░░░░░] 30% S1: Autonomous Execution Engine
├─ ✅ cortex/execution/autonomous_executor.py created
├─ ✅ Multi-stage loop implemented
├─ 🔵 15 unit tests (RED phase)
└─ ⚪ Error recovery strategies

[██████░░░░] 65% S2: Progress Tracking + Rollback
├─ ✅ S1 complete (15/15 tests passing)
├─ ✅ progress_tracker.py + rollback_manager.py created
├─ 🔵 10 integration tests (RED phase)
└─ ⚪ Dashboard integration

[██████████] 100% S3: Documentation + E2E Verification
├─ ✅ S2 complete (25/25 tests passing)
├─ ✅ 5-stage E2E test passing
├─ ✅ No mid-execution prompts verified
└─ ✅ 3 commits pushed
```

### Success Criteria

- ✅ **25/25 tests passing** (0 failures)
- ✅ **3 commits pushed**
- ✅ **E2E test: 5-stage plan executes without prompts**
- ✅ **Progress dashboard updates in real-time**
- ✅ **Rollback functional** (verified via test)

### Verification Commands

```bash
# After completion, verify:

# 1. E2E autonomous execution
pytest tests/integration/test_approve_to_done_flow.py::test_five_stage_plan_no_prompts -v -s
# Expected: PASSED (watch progress bars, no prompts)

# 2. Rollback functionality
pytest tests/integration/test_approve_to_done_flow.py::test_rollback_to_previous_stage -v
# Expected: PASSED

# 3. Progress tracking
python -c "
from cortex.execution.autonomous_executor import AutonomousExecutor
from cortex.models.plan import Plan, Stage
plan = Plan(stages=[Stage('S1'), Stage('S2'), Stage('S3')])
executor = AutonomousExecutor()
result = executor.execute_plan(plan)
print(f'Completed: {result.completed_stages}/{result.total_stages}')
# Expected: Completed: 3/3
"
```

---

## 🚀 WAVE-O: Data Integrity & Dashboard Explainability

### Context

**Goal:** Production-grade data quality + stakeholder trust features  
**Problem:** Dashboard metrics not validated, KPIs lack transparency  
**Solution:** Integrity validation + explainability layer + audit trails

**Files to Create:**
- `cortex/validation/data_integrity_validator.py`
- `cortex/dashboards/explainability_layer.py`
- `cortex/dashboards/trust_features.py`
- `tests/unit/validation/test_data_integrity.py` (18 tests)
- `tests/integration/test_dashboard_explainability.py` (12 tests)

### Autonomous Command

```
/implement WAVE-O: ENH-068/069 Data Integrity & Explainability

Authority: cortex-registry/_cortex-master/index.yaml v3.0
Mode: Silent autonomous with ASCII progress bars
Session: WAVE-O-20260216-01
Token Budget: <200k tokens
```

### Expected Execution Flow

```
[████░░░░░░] 35% S1: Data Integrity Validation
├─ ✅ data_integrity_validator.py created
├─ ✅ Contradiction detection implemented
├─ 🔵 18 unit tests (RED phase)
└─ ⚪ Anomaly alerting

[██████░░░░] 70% S2: Dashboard Explainability
├─ ✅ S1 complete (18/18 tests passing)
├─ ✅ explainability_layer.py + trust_features.py created
├─ 🔵 12 integration tests (RED phase)
└─ ⚪ Stakeholder view translation

[██████████] 100% S3: Documentation + Production Validation
├─ ✅ S2 complete (30/30 tests passing)
├─ ✅ Zero contradictions in current data
├─ ✅ All KPIs explainable
└─ ✅ 3 commits pushed

🎉 MILESTONE: Wave 3 Autonomy COMPLETE (L→M→N→O)
```

### Success Criteria

- ✅ **30/30 tests passing** (0 failures)
- ✅ **3 commits pushed**
- ✅ **Zero contradictions** in current dashboard data
- ✅ **All KPIs explainable** (why/how/source documented)
- ✅ **Stakeholder view validated** (non-technical language)

### Verification Commands

```bash
# After completion, verify:

# 1. Data integrity checks
pytest tests/unit/validation/test_data_integrity.py -v
# Expected: 18/18 passing

# 2. Run integrity validation on current data
python -c "
from cortex.validation.data_integrity_validator import DataIntegrityValidator
from cortex.dashboards.dashboard_manager import DashboardManager
validator = DataIntegrityValidator()
dashboard = DashboardManager().get_current_dashboard()
result = validator.validate_dashboard_data(dashboard)
print(f'Contradictions: {len(result.contradictions)}')
# Expected: Contradictions: 0
"

# 3. Explainability test
pytest tests/integration/test_dashboard_explainability.py::test_explain_test_coverage_kpi -v
# Expected: PASSED

# 4. Verify Wave 3 complete
git log --oneline --all | grep -E "WAVE-(L|M|N|O)"
# Expected: 11 commits (3+2+3+3 for L/M/N/O)
```

---

## 🛠️ Troubleshooting

### Token Budget Exceeded

**Symptom:** Session stops at 75% token usage with checkpoint message

**Action:**
1. System automatically generates continuation prompt
2. Copy continuation prompt
3. Start new GitHub Copilot Chat session
4. Paste continuation prompt
5. Type: `/plan continue from checkpoint`

**Example Continuation Prompt:**
```
Continue WAVE-L from checkpoint:

Completed:
- ✅ S1: Lazy Loading System (15/15 tests passing)
- ✅ cortex/agents/lazy_loader.py implemented

Remaining:
- ⚪ S2: Agent-Orchestrator Patterns (10 integration tests)
- ⚪ S3: Documentation + Verification

Resume at: S2 Stage 1 - Create interaction_patterns.py

Context: WAVE-L-20260213-01, Token budget 75% used
```

### Test Failure During Execution

**Symptom:** Silent mode stops, displays test error

**Forbidden Actions:**
- ❌ Using `--ignore` flag to skip test
- ❌ Renaming test file to `_skip_*`
- ❌ Deleting failing test
- ❌ Mocking test to pass without fixing

**Required Actions:**
1. ✅ Read full error message
2. ✅ Understand root cause
3. ✅ Fix source code or test
4. ✅ Re-run test to verify
5. ✅ Commit fix with AC markers

**Example:**
```bash
# Error: test_load_agents_for_implement_intent FAILED
# Root cause: IntentAgentMapper missing IMPLEMENT case

# Fix: Add IMPLEMENT case to mapper
# File: cortex/agents/lazy_loader.py

# Re-run
pytest tests/unit/agents/test_lazy_loading.py::test_load_agents_for_implement_intent -v
# Expected: PASSED

# Commit
git add cortex/agents/lazy_loader.py
git commit -m "WAVE-L S1: Fix IMPLEMENT intent mapping

AC_START: AC-WAVE-L-001
Fix IntentAgentMapper to handle IMPLEMENT intent.
Test: test_load_agents_for_implement_intent now passes.
AC_COMPLETE: AC-WAVE-L-001 ✅"
```

### Dependency Missing

**Symptom:** ImportError or ModuleNotFoundError during test

**Action:**
```bash
# 1. Identify missing package
# Error: ModuleNotFoundError: No module named 'spacy'

# 2. Add to requirements.txt
echo "spacy>=3.5.0" >> requirements.txt

# 3. Install
pip install -r requirements.txt

# 4. Re-run tests
pytest tests/unit/intelligence/ -v
```

### Merge Conflict

**Symptom:** Git push rejected due to remote changes

**Action:**
```bash
# 1. Pull latest changes
git pull origin CORTEX --rebase

# 2. Resolve conflicts (if any)
# Edit conflicted files, then:
git add <resolved-files>
git rebase --continue

# 3. Push again
git push origin CORTEX
```

---

## 📊 Progress Tracking

**Use this checklist to track wave completion:**

```markdown
## WAVE-L: Agent Architecture
- [ ] Session started (WAVE-L-20260213-01)
- [ ] S1: Lazy Loading (15 tests passing)
- [ ] S2: Interaction Patterns (10 tests passing)
- [ ] S3: Documentation (verified)
- [ ] 3 commits pushed
- [ ] Token reduction ≥50% verified
- [ ] WAVE-L COMPLETE ✅

## WAVE-M: Language Refinement
- [ ] Session started (WAVE-M-20260214-01)
- [ ] S1: Enhanced Classifier (12 tests passing)
- [ ] S2: Clarification Reducer (8 tests passing)
- [ ] S3: Metrics Validation (accuracy ≥90%, clarification <15%)
- [ ] 2 commits pushed
- [ ] WAVE-M COMPLETE ✅

## WAVE-N: Autonomous Execution
- [ ] Session started (WAVE-N-20260215-01)
- [ ] S1: Execution Engine (15 tests passing)
- [ ] S2: Progress + Rollback (10 tests passing)
- [ ] S3: E2E Verification (5-stage plan successful)
- [ ] 3 commits pushed
- [ ] WAVE-N COMPLETE ✅

## WAVE-O: Data Integrity
- [ ] Session started (WAVE-O-20260216-01)
- [ ] S1: Integrity Validation (18 tests passing)
- [ ] S2: Explainability Layer (12 tests passing)
- [ ] S3: Production Validation (zero contradictions)
- [ ] 3 commits pushed
- [ ] WAVE-O COMPLETE ✅

🎉 MILESTONE: Wave 3 Autonomy COMPLETE
```

---

## 📝 Post-Completion Actions

**After WAVE-O completes:**

1. **Update Master Index:**
   ```bash
   # Mark waves L-O complete in index.yaml
   # Update completion_date fields
   # Increment revision to v4.0
   ```

2. **Generate Completion Report:**
   ```bash
   # Create: cortex-registry/_cortex-master/WAVE-3-AUTONOMY-COMPLETION-REPORT.md
   # Include: Test metrics, git commits, milestones achieved
   ```

3. **Run Full Test Suite:**
   ```bash
   pytest tests/ -v --tb=short
   # Verify no regressions
   ```

4. **Update Documentation:**
   ```bash
   # Update: .github/copilot-instructions.md (if applicable)
   # Update: .github/prompts/cortex-architect.prompt.md (if needed)
   ```

5. **Plan Next Wave:**
   ```bash
   # Review: Remaining P2 enhancement waves
   # Prioritize: Based on ROI and dependencies
   ```

---

## 🎯 Summary

**WAVE-L through WAVE-O represent the Intelligence + Autonomy tracks of CORTEX development.**

**Key Achievements Upon Completion:**
- ✅ **60% token reduction** (agent efficiency)
- ✅ **90% intent accuracy** (language understanding)
- ✅ **True autonomous execution** (approve → done)
- ✅ **Production data quality** (integrity + explainability)

**Total Effort:** 15 hours (4 sessions)  
**Tests Added:** 100 tests (25+20+25+30)  
**Commits:** 11 commits (3+2+3+3)

**Next Steps:** After Wave 3 completion, move to P2 enhancement waves or production deployment preparation.

---

**Authority:** cortex-registry/_cortex-master/index.yaml v3.0  
**Maintainer:** CORTEX Architect  
**Last Updated:** 2026-02-12T23:59:59Z
