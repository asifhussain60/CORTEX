# CORTEX 6.0 Build - Self-Healing System Overview

**Version:** 1.0.0  
**Created:** 2026-01-07  
**Purpose:** Autonomous execution with continuous quality monitoring

---

## 🎯 Overview

The CORTEX 6.0 build system now includes comprehensive self-healing capabilities that enable autonomous execution with automatic error detection, correction, and quality assurance.

---

## 🛡️ Self-Healing Protocol

### Pre-Task Execution

**Audit Review**
- Check recent audit logs for errors
- Command: `tail -50 cortex-brain/audit-logs/*.jsonl | grep -i error`
- Frequency: Before EVERY task

**Validation Check**
- Verify previous task exit criteria met
- Method: Check `validation.result` in tracker
- Ensures continuity and correctness

**Test Alignment**
- Confirm tests match implementation
- Method: Run pytest and compare counts
- Prevents drift between code and tests

### During Execution

**Audit Logging** (MANDATORY)
- Parameters: `level`, `category`, `component`, `operation`, `correlation_id`
- Example: `AuditLevel.INFO, AuditCategory.EXECUTION, 'todo_orchestrator', 'create_todo', 'FEAT02-P2-T2.2.3'`
- Coverage: ALL operations logged

**TDD Enforcement**
- Sequence: RED (failing test) → GREEN (pass) → REFACTOR (clean)
- Applies when: `tdd_required=true`
- Validation: Test must fail first

**Incremental Commits**
- Limit: 500 lines per commit
- Rationale: Manageable review and rollback
- Method: Split large changes logically

### Post-Task Execution

**Exit Criteria Verification**
- Check: ALL criteria in `validation` section
- Mandatory: Cannot mark COMPLETED without this
- Ensures quality gates passed

**Tracker Update**
- Fields: `status`, `completed_at`, `actual_minutes`, `validation.result`, `deliverables`
- Mandatory: Preserves execution history
- Enables progress tracking

**Continuation Prompt Update**
- Script: `python3 update_continuation_prompt.py`
- Frequency: EVERY task completion
- Keeps sessions synchronized

**Checkpoint**
- Frequency: Every 5 tasks OR phase completion
- Method: Git commit with standardized message
- Format: `feat{XX}-p{Y}-t{Z}: {task_name}`

### Phase Completion Review

**Audit Trace Analysis**
- Command: `grep FEAT{XX}-P{Y} cortex-brain/audit-logs/*.jsonl`
- Check for: ERROR, CRITICAL, incomplete operations
- Coverage: 100% of phase operations

**Error Remediation**
- Requirement: Fix ALL errors immediately
- Exception: May defer if ROI justifies (MUST document)
- Documentation: Add to `risk/00-RISK-REGISTRY.yaml`

**Test Coverage**
- Minimum: 80% per phase, 85% for handoff
- Command: `pytest --cov --cov-report=term-missing`
- Action: Add missing tests if below threshold

**Balance Adjustment**
- Accuracy: Implementation matches requirements
- Efficiency: Reasonable execution time
- Adaptation: Re-plan future phases if needed

---

## 📊 Current Status

**As of 2026-01-07T16:40:00Z:**

- ✅ Audit logging: 144 entries, 0 errors
- ✅ Task completion: 30 tasks completed
- ✅ Test coverage: 10/10 tests passing (task-2.2.2)
- ✅ Git checkpoints: Regular commits maintained
- ✅ Self-healing: Implemented in all phases

**Categories:**
- state_management: 72 entries
- execution: 60 entries
- middleware: 12 entries

---

## 🔄 Automation

### Auto-Update Script

**File:** `update_continuation_prompt.py`

**Purpose:** Automatically updates `CONTINUATION-PROMPT.md` with current tracker state

**Usage:**
```bash
cd .asif/AI-Learning/cortex6/source-of-truth
python3 update_continuation_prompt.py
```

**Updates:**
- Current position (feature, phase, task)
- Completed task count
- Next task information
- Timestamp

**Integration:** Called after EVERY task completion

---

## 📁 Key Files

| File | Purpose | Update Frequency |
|------|---------|------------------|
| `00-TODO-CONTINUITY-TRACKER.yaml` | Master task tracker | Every task |
| `CONTINUATION-PROMPT.md` | Session resume instructions | Every task |
| `update_continuation_prompt.py` | Auto-update script | As needed |
| `session-audit.jsonl` | Session-level audit | Every session |
| `cortex-brain/audit-logs/*.jsonl` | Operation audit logs | Every operation |

---

## 🎓 Usage Guidelines

### For GitHub Copilot

1. **Session Start:** Read `CONTINUATION-PROMPT.md` for current position
2. **Task Execution:** Follow self-healing protocol strictly
3. **Task Completion:** Update tracker AND run update script
4. **Checkpoint:** Git commit every 5 tasks

### For CORTEX (Post-Handoff)

1. **Load tracker:** Parse YAML for current position
2. **Execute autonomously:** Use DAG for dependency management
3. **Self-monitor:** Check audit logs for own errors
4. **Self-correct:** Remediate issues automatically

---

## 🚨 Handoff Criteria

**feat02-todo-orchestrator Phase 4 Completion:**

- [ ] All 4 phases completed (100% tasks done)
- [ ] Integration test passes: `test_cortex_self_management.py`
- [ ] Audit trace clean (zero errors)
- [ ] Test coverage >85%
- [ ] CORTEX can create TODOs from YAML
- [ ] CORTEX can execute TODOs in DAG order
- [ ] CORTEX can checkpoint and resume
- [ ] CORTEX can rollback on failure

**Upon Handoff:**
1. Update `current_executor` to "CORTEX TODO Manager"
2. Log handoff to audit with correlation ID
3. GitHub Copilot transitions to advisory role
4. CORTEX manages feat03+ autonomously

---

## 📈 Benefits

### Quality Assurance
- Continuous audit trail monitoring
- Automatic error detection
- Immediate remediation triggers

### Execution Continuity
- Session resume from any point
- No context loss between sessions
- Automatic state synchronization

### Accountability
- Complete operation logging
- Traceable decision history
- Performance metrics captured

### Efficiency
- Automated routine tasks
- Reduced manual intervention
- Optimized execution flow

---

**Maintained by:** GitHub Copilot → CORTEX TODO Manager  
**Review Frequency:** Every phase completion  
**Version Control:** Git tracked with audit correlation
