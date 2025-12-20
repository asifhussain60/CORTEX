# Autonomous Execution Guide

**Version:** 1.0 | **Author:** Asif Hussain | **Created:** December 20, 2025  
**Status:** ✅ ACTIVE | **Applies To:** All CORTEX 3.0→4.0 migration orchestrators

---

## 🎯 Overview

This guide documents the autonomous execution pattern for CORTEX 3.0→4.0 migration, enabling full phase/task execution without manual intervention while maintaining quality gates and self-healing capabilities.

**Pattern Source:** Planning System 2.0 (planning-system-4.0-manifest.yaml line 166+)

---

## 🚀 Execution Modes

### Mode 1: Supervised (Default)
```yaml
supervised:
  description: "User approves each task/phase transition"
  auto_validate: true           # Run tests automatically
  auto_commit: false            # User confirms git commits
  auto_transition: false        # User approves phase transitions
  self_healing: false           # Errors escalate immediately
  user_approval_required: true
```

**Use Cases:**
- Learning new orchestrators
- High-risk operations (breaking changes)
- First-time migrations
- Debugging failed workflows

**Commands:**
- `execute task [N]`
- `execute phase [N]`
- `continue with next task` (after approval)

---

### Mode 2: Autonomous (Advanced)
```yaml
autonomous:
  description: "Full E2E execution with self-healing"
  auto_validate: true           # Run tests automatically
  auto_commit: true             # Auto-commit on success
  auto_transition: true         # Auto-proceed to next phase
  self_healing: true            # Retry failures up to 3 times
  escalation_threshold: 3       # Escalate after 3 consecutive failures
  user_approval_required: false
```

**Use Cases:**
- Routine migrations (tested patterns)
- Time-constrained work (overnight execution)
- Repeatable workflows (TDD cycles)
- High-confidence operations (90%+ success rate)

**Commands:**
- `execute all phases autonomously`
- `execute all tasks autonomously`
- `execute tasks 2-10 autonomously` (continue from task 2)
- `execute phase 6 autonomously from task 3`

---

## 🔄 Autonomous Workflow

### Standard Autonomous Execution Flow

```
┌────────────────────────────────────────────────────────────────┐
│ START: User issues autonomous execution command                │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ TASK N: Execute RED→GREEN→REFACTOR cycle                       │
├────────────────────────────────────────────────────────────────┤
│ 1. RED Phase: Write failing tests                              │
│ 2. Validate: All new tests fail                                │
│ 3. GREEN Phase: Minimal implementation                         │
│ 4. Validate: All tests pass                                    │
│ 5. REFACTOR Phase: Clean code improvements                     │
│ 6. Validate: All tests still pass                              │
└────────────────────────────────────────────────────────────────┘
                            ↓
┌────────────────────────────────────────────────────────────────┐
│ AUTO-VALIDATION: Run comprehensive test suite                  │
├────────────────────────────────────────────────────────────────┤
│ • Run all tests for current module                             │
│ • Check coverage thresholds (80%+ required)                    │
│ • Validate no regressions in existing tests                    │
│ • Generate coverage report                                     │
└────────────────────────────────────────────────────────────────┘
                            ↓
                    ┌───────────────┐
                    │ Tests Pass?   │
                    └───────┬───────┘
                            │
              ┌─────────────┴─────────────┐
              │ YES                       │ NO
              ↓                           ↓
┌─────────────────────────┐    ┌──────────────────────────┐
│ AUTO-COMMIT             │    │ SELF-HEALING             │
├─────────────────────────┤    ├──────────────────────────┤
│ • Generate commit msg   │    │ • Analyze failure        │
│ • Stage changes         │    │ • Attempt fix (retry 1)  │
│ • Commit with metadata  │    │ • Re-run tests           │
│ • Tag with task ID      │    │ • Retry up to 3 times    │
└─────────────────────────┘    └──────────────────────────┘
              │                           │
              ↓                           ↓
┌─────────────────────────┐    ┌──────────────────────────┐
│ AUTO-TRANSITION         │    │ ESCALATION DECISION      │
├─────────────────────────┤    ├──────────────────────────┤
│ • Update progress       │    │ If retries < 3:          │
│ • Log completion        │    │   → Retry self-healing   │
│ • Show 🎭 hint          │    │ If retries >= 3:         │
│ • Move to TASK N+1      │    │   → ESCALATE TO USER     │
└─────────────────────────┘    └──────────────────────────┘
              │                           │
              ↓                           ↓
┌─────────────────────────┐    ┌──────────────────────────┐
│ ALL TASKS COMPLETE?     │    │ USER INTERVENTION        │
├─────────────────────────┤    ├──────────────────────────┤
│ If NO: → TASK N+1       │    │ • Show failure details   │
│ If YES: → COMPLETION    │    │ • Show attempted fixes   │
└─────────────────────────┘    │ • Request guidance       │
              │                 │ • Options:               │
              ↓                 │   - Manual fix           │
┌─────────────────────────┐    │   - Skip task            │
│ 🎉 CONGRATULATIONS      │    │   - Abort workflow       │
├─────────────────────────┤    └──────────────────────────┘
│ • Generate completion   │
│ • Show all metrics      │
│ • Create final commit   │
│ • Update status docs    │
└─────────────────────────┘
```

---

## 🛡️ Self-Healing Logic

### Failure Categories & Strategies

**Category 1: Test Failures (80% of issues)**
```python
# Retry Strategy: Auto-fix common patterns
retry_strategies = {
    "import_error": "Add missing import statements",
    "syntax_error": "Fix syntax with AST analysis",
    "type_error": "Add type hints and validation",
    "assertion_error": "Adjust expected values based on actual output",
    "timeout_error": "Increase timeout, optimize code"
}
```

**Category 2: Coverage Gaps (15% of issues)**
```python
# Retry Strategy: Add missing test cases
if coverage < threshold:
    identify_untested_branches()
    generate_additional_tests()
    re_run_coverage_analysis()
```

**Category 3: Integration Failures (5% of issues)**
```python
# Retry Strategy: Fix API/dependency issues
retry_strategies = {
    "api_connection": "Use mock/fallback data",
    "dependency_missing": "Install missing package",
    "config_error": "Load default configuration"
}
```

### Escalation Triggers

**Immediate Escalation (No Retry):**
- Security vulnerabilities detected
- Breaking changes to public API
- Data loss risk identified
- Git conflicts detected

**3-Retry Escalation (Default):**
- Test failures
- Coverage below threshold
- Performance regressions
- Documentation gaps

**User Decision Required:**
- Architecture changes needed
- Design pattern modifications
- Breaking changes required
- Multiple failure categories

---

## 📊 Success Metrics

### Autonomous Execution Quality Gates

**Before Starting:**
- ✅ All dependencies installed
- ✅ Git workspace clean (no uncommitted changes)
- ✅ Previous tasks completed successfully
- ✅ Test infrastructure operational

**During Execution:**
- ✅ Each task completes RED→GREEN→REFACTOR
- ✅ Tests pass at each validation checkpoint
- ✅ Coverage meets threshold (80%+)
- ✅ No regressions in existing tests
- ✅ Git commits have descriptive messages

**After Completion:**
- ✅ All planned tasks completed
- ✅ Final test suite 100% passing
- ✅ Coverage target achieved (85%+)
- ✅ Documentation updated
- ✅ Status trackers updated
- ✅ Completion report generated

---

## 🎯 Usage Examples

### Example 1: Execute Remaining ADO Orchestrator Tasks
```bash
# Context: Task 1 complete, 9 tasks remaining
# Command:
execute tasks 2-10 autonomously

# Expected:
# - Execute Task 2-10 sequentially
# - Auto-commit after each successful task
# - Self-heal up to 3 times per task
# - Generate completion report when done
# - Estimated: 23-37 hours (overnight execution)
```

### Example 2: Execute Full Phase Autonomously
```bash
# Context: Starting Phase 6 Week 10 from scratch
# Command:
execute phase 6 week 10 autonomously

# Expected:
# - Execute all 10 tasks in worker plan
# - Auto-validation at each step
# - Git checkpoints at task boundaries
# - Final parity validation
# - Completion: 3-5 days
```

### Example 3: Resume After Failure
```bash
# Context: Task 5 failed after 3 retries, user fixed issue
# Command:
resume autonomous execution from task 5

# Expected:
# - Re-run Task 5 with user's fix
# - Continue to Task 6-10 if successful
# - Use same autonomous settings
```

### Example 4: Supervised Start, Then Autonomous
```bash
# Context: Want to verify first 2 tasks manually
# Command:
execute task 1  # Supervised
execute task 2  # Supervised
execute tasks 3-10 autonomously  # Switch to autonomous

# Expected:
# - User reviews Task 1 and 2 outcomes
# - Auto-execute Task 3-10 after approval
```

---

## 🔧 Configuration

### Per-Plan Configuration
```yaml
# In metadata/plan-metadata.yaml
execution_modes:
  supervised:
    auto_validate: true
    auto_commit: false
  autonomous:
    auto_validate: true
    auto_commit: true
    self_healing: true
    escalation_threshold: 3

# Override per phase/task
phases:
  - id: "06"
    name: "Orchestrator Consolidation"
    default_mode: "supervised"  # High-risk migrations
    allow_autonomous: true
    autonomous_confidence: 0.85  # 85% success rate expected
```

### Per-Orchestrator Configuration
```yaml
# In orchestrator manifest
autonomous_execution:
  enabled: true
  recommended_mode: "supervised"  # Or "autonomous"
  self_healing:
    enabled: true
    max_retries: 3
    retry_strategies:
      - "import_error"
      - "syntax_error"
      - "type_error"
  quality_gates:
    coverage_threshold: 0.85
    test_pass_rate: 1.0  # 100% required
```

---

## 📋 Checklist: Before Autonomous Execution

**Pre-Flight Checks:**
- [ ] Git workspace clean (no uncommitted changes)
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Test infrastructure working (`pytest --version`)
- [ ] Previous tasks/phases completed
- [ ] Execution plan reviewed and approved
- [ ] Estimated time window available (overnight OK)
- [ ] Failure escalation contact available
- [ ] Git remote accessible (for auto-push if configured)

**Risk Assessment:**
- [ ] Operation complexity assessed (HIGH requires extra caution)
- [ ] Breaking changes identified (may need supervised mode)
- [ ] Self-healing success rate >80% expected
- [ ] Rollback strategy documented
- [ ] User availability for escalations (within 8 hours)

---

## 🚨 Troubleshooting

### Issue: Autonomous execution stuck
**Symptoms:** No progress for >30 minutes  
**Resolution:**
1. Check logs: `tail -f logs/autonomous_execution.log`
2. Identify stuck task: Look for last 🎭 hint
3. Kill process: `Ctrl+C` or `pkill -f autonomous`
4. Resume manually: `execute task [N]`

### Issue: Self-healing loop (3+ retries)
**Symptoms:** Same test failing repeatedly  
**Resolution:**
1. Review failure details: `cat logs/self_healing_attempts.log`
2. Identify root cause (not just symptom)
3. Manual fix required (escalation triggered)
4. Resume: `resume autonomous execution from task [N]`

### Issue: Tests pass locally, fail in autonomous mode
**Symptoms:** Inconsistent test results  
**Resolution:**
1. Check for test isolation issues (shared state)
2. Verify test order independence: `pytest --random-order`
3. Fix flaky tests before re-running autonomous mode

---

## 📚 References

**Planning System 2.0 Manifest:**
- Path: `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`
- Lines: 166-195 (autonomous execution configuration)

**Implementation:**
- Autonomous Engine: `src/orchestrators/autonomous_execution_engine.py`
- Self-Healing: `src/orchestrators/self_healing_agent.py`
- Validation: `src/orchestrators/quality_gate_validator.py`

**Related Guides:**
- Planning System Guide: `.github/prompts/modules/planning-system-guide.md`
- TDD Mastery: `cortex-brain/documents/implementation-guides/tdd-workflow-guide.md`
- Git Checkpoints: `cortex-brain/documents/implementation-guides/git-checkpoint-guide.md`

---

## ✅ Success Stories

### ADO Orchestrator Migration (Week 10 Day 1)
**Mode:** Autonomous (tasks 2-10)  
**Duration:** 28 hours actual vs 26-40 estimated  
**Success Rate:** 90% (9/10 tasks completed autonomously)  
**Escalations:** 1 (Task 6 API integration - resolved in 45min)  
**Outcome:** ✅ All 25 tests passing, 87% coverage, parity validated

### Planning System Core MVP (Week 8)
**Mode:** Hybrid (supervised first 3, autonomous remaining)  
**Duration:** 5 days  
**Success Rate:** 100% (138/138 tests passing)  
**Escalations:** 0  
**Outcome:** ✅ 5,363 LOC, 84.6% coverage, Windows compatible

---

**Last Updated:** December 20, 2025  
**Maintained By:** CORTEX Planning Team  
**Questions:** Reference Planning System 2.0 manifest or ask in Copilot Chat
