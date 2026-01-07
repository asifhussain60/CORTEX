# CORTEX 6.0 Build - Session Continuation

**Current Position:** feat02-todo-orchestrator, Phase 4, task-2.4.2  
**Completed:** 40 tasks | **Status:** ✅ On track | **Last:** task-2.4.1

---

## 🚀 Quick Start

1. **Load State:** Read `.asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml`
2. **Find Position:** Check `current_position` section
3. **Load Feature:** Read `features/feat02-todo-orchestrator/feature.yaml`
4. **Execute Task:** Follow task instructions
5. **Update Tracker:** Mark COMPLETED, update current_position
6. **Update This File:** Run `python3 update_continuation_prompt.py`

---

## 🛡️ Self-Healing Protocol

**Before Each Task:**
- Review audit logs: `cortex-brain/audit-logs/` (check for errors)
- Validate previous task completion
- Check test results alignment

**During Execution:**
- Log ALL operations (level, category, component, operation, correlation_id)
- TDD if `tdd_required=true` (RED → GREEN → REFACTOR)
- Keep changes <500 lines per commit

**After Task:**
- Verify exit criteria
- Update tracker AND run update script
- Checkpoint every 5 tasks

**Phase/Feature Review:**
- Audit log trace analysis (check ERROR entries)
- Test coverage validation (>80%)
- Immediate remediation if gaps found

---

## 📁 Key Files

| File | Path |
|------|------|
| Tracker | `source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml` |
| Features | `source-of-truth/features/feat02-todo-orchestrator/feature.yaml` |
| Audit | `cortex-brain/audit-logs/` |
| Risks | `source-of-truth/risk/00-RISK-REGISTRY.yaml` |
| Update | `source-of-truth/update_continuation_prompt.py` |

---

## 🎯 Next Task: task-2.4.2

Check `00-TODO-CONTINUITY-TRACKER.yaml` for:
- Task description
- Dependencies
- Estimated time
- Validation criteria

---

**Last Updated:** 2026-01-07T22:43:47.180036Z  
**Executor:** GitHub Copilot → CORTEX (after feat02 Phase 4)
