# CORTEX 6.0 Build Epic - Session Continuation Prompt

## 📋 Quick Start

Copy this prompt at the START of each new GitHub Copilot Chat session:

---

## 🧠 CORTEX 6.0 Build - Continue Execution

Continue the CORTEX 6.0 Build Epic from the last checkpoint.

### Step 1: Load State
Read the TODO tracker to find current position:
```
.asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml
```

### Step 2: Find Current Position
Look for `current_position` section - this tells you:
- Current feature
- Current phase
- Current task
- Current status

### Step 3: Load Feature Details
Read the feature YAML for implementation instructions:
- feat01: `features/feat01-foundation/feature.yaml`
- feat02: `features/feat02-todo-orchestrator/feature.yaml`
- feat03+: `features/feat03-to-feat08/features-summary.yaml`

### Step 4: Execute Next Task
Follow these rules:
1. **Audit Logging**: Log ALL operations using `src/orchestrators/audit_logger.py`
2. **TDD**: If `tdd_required=true`, write failing tests FIRST
3. **Incremental**: Keep changes under 500 lines
4. **Validate**: Check exit criteria before marking complete

### Step 5: Update Tracker
After each task:
- Update task status (COMPLETED/FAILED)
- Update current_position
- Every 5 tasks: git commit checkpoint

### Step 6: Phase/Feature Review
At phase or feature completion:
- Review audit log trace
- Check for ERROR entries
- Remediate gaps immediately (unless ROI justifies deferral)

---

## 🚨 HANDOFF ALERT

If you complete `feat02-todo-orchestrator Phase 4 Task 4.5`:
1. Run: `pytest tests/integration/test_cortex_self_management.py -v`
2. If passes: Update `current_executor` to "CORTEX TODO Manager"
3. Log handoff completion to audit
4. CORTEX takes over for feat03+

---

## 📁 Key Files
| Purpose | Path |
|---------|------|
| TODO Tracker | `source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml` |
| Risk Registry | `source-of-truth/risk/00-RISK-REGISTRY.yaml` |
| Execution Guide | `source-of-truth/EXECUTION-GUIDE.yaml` |
| Master Source | `source-of-truth/00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml` |

---

**BEGIN EXECUTION NOW**
