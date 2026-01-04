# Plan Orchestrator Quick Reference

**Version:** 2.0 (Infrastructure-Integrated)  
**Date:** January 3, 2026  
**Status:** ✅ Production Ready

---

## 🚀 Quick Start

```bash
cd cortex-brain/documents/planning/active/CORTEX-5.0
python plan_orchestrator.py         # Auto-execute next task
python plan_orchestrator.py status  # Show current status
```

---

## 📋 Commands

| Command | Description | Example |
|---------|-------------|---------|
| `python plan_orchestrator.py` | Auto-execute next available sub-plan | Default mode |
| `python plan_orchestrator.py status` | Show full status dashboard | Read-only |

---

## 🎯 Current Status (January 4, 2026)

```
📊 Overall Progress: 0%
   Completed: 0/11 sub-plans
   Current Sub-Plan: 00 - Test Coverage Sprint

📋 Sub-Plans:
00   Test Coverage Sprint                🔄 in_progress    0%  2-3 weeks
01   Refinement Orchestrator             ⏸️ blocked        0%     1 week
02   Debug Orchestrator                  ⏸️ blocked        0%     1 week
03   Phase -1 Knowledge Library          ⏸️ blocked        0%   3-4 days
04   AST Scanning Integration            ⏸️ blocked        0%   3-4 days
05   Context Middleware Enhancement      ⏸️ blocked        0%   2-3 days
06   Visual Progress Generation          ⏸️ blocked        0%     2 days
07   REFACTOR Task Enforcement           ⏸️ blocked        0%     2 days
08   Orchestrator Migrations             ⏸️ blocked        0%  1-2 weeks
09   Final Validation & DoD              ⏸️ blocked        0%   3-4 days
10   Acceptance Validation System        ⏸️ blocked        0%     1 week
```

---

## 🏗️ Infrastructure

**Powered By:**
- ✅ PlanningStateDB (880 lines) - ACID-compliant state management
- ✅ StateManager (396 lines) - Execution lifecycle tracking
- ✅ OrchestratorRegistry (437 lines) - Dynamic orchestrator discovery

**Total Infrastructure:** 1,713 lines of battle-tested code

---

## 📊 Status Icons

| Icon | Status | Meaning |
|------|--------|---------|
| 🔄 | in_progress | Currently being worked on |
| ⏳ | not_started | Ready to start (dependencies met) |
| ⏸️ | blocked | Waiting on dependencies |
| ✅ | complete | Finished successfully |
| ❌ | failed | Encountered error |

---

## 🔗 Dependencies

**Sub-Plan Dependency Chain:**

```
00 (Test Coverage Sprint)
├── Blocks: 01, 02, 05, 10
│
01 (Refinement Orchestrator) + 02 (Debug Orchestrator)
├── Blocks: 08
│
03 (Knowledge Library) + 04 (AST Scanning)
├── Blocks: 05
│
05 (Context Middleware)
├── Blocks: 06, 07
│
06 (Visual Progress) + 07 (REFACTOR Enforcement)
├── Blocks: 08
│
08 (Orchestrator Migrations)
├── Blocks: 09
│
10 (Acceptance Validation System)
├── Replaces manual gap analysis in 09
│
09 (Final Validation & DoD)
├── Uses automated L3 validation from 10
└── END
```

---

## 🎯 Milestones

| Milestone | Target Date | Criteria |
|-----------|-------------|----------|
| Gate 1: 50% Test Coverage | 2026-01-17 | 65+ of 130 criteria tested |
| Gate 2: 80% Test Coverage | 2026-01-24 | 104+ of 130 criteria tested |
| All Orchestrators Complete | 2026-02-07 | Refinement + Debug functional |
| All Core Features Complete | 2026-02-14 | Knowledge, AST, Context, etc. |
| Production Ready | 2026-02-28 | All 130 criteria pass, 80%+ coverage |

---

## 📁 File Structure

```
CORTEX-5.0/
├── plan_orchestrator.py              # Main orchestrator (441 lines)
├── README-ORCHESTRATOR.md            # Full documentation
├── ORCHESTRATOR-QUICK-REFERENCE.md   # This file
│
├── 00-test-coverage-sprint/          # Current sub-plan
├── 01-refinement-orchestrator/
├── 02-debug-orchestrator/
├── 03-knowledge-library-phase/
├── 04-ast-scanning-planning/
├── 05-context-middleware/
├── 06-visual-progress/
├── 07-refactor-enforcement/
├── 08-orchestrator-migrations/
└── 09-final-validation/
```

---

## 🔍 Troubleshooting

### Orchestrator Won't Start
```bash
# Ensure PYTHONPATH is set
export PYTHONPATH=/Users/asifhussain/PROJECTS/CORTEX
python3 plan_orchestrator.py
```

### Check Database State
```bash
sqlite3 cortex-brain/database/planning_state.db
sqlite> SELECT * FROM plans;
sqlite> .quit
```

### View Logs
```bash
# Execution logs stored in database
python3 -c "
from src.database.planning_state_db import PlanningStateDB
db = PlanningStateDB('cortex-brain/database/planning_state.db')
logs = db.get_execution_logs()
for log in logs:
    print(log)
"
```

---

## 📚 Documentation

**Full Documentation:**
- `README-ORCHESTRATOR.md` - Complete usage guide
- `cortex-brain/documents/implementation-guides/plan-orchestrator-integration-complete-2026-01-03.md` - Technical details
- `cortex-brain/documents/analysis/plan-orchestrator-brittleness-analysis-2026-01-03.md` - Problem analysis

**Infrastructure:**
- `src/database/planning_state_db.py` - Database operations
- `src/orchestrators/state_manager.py` - Execution tracking
- `src/core/orchestrator_registry.py` - Orchestrator discovery

---

## 🎯 Next Actions

1. **Continue Sub-Plan 00** (Test Coverage Sprint)
   - Follow phases in `00-test-coverage-sprint/00-test-coverage-sprint.md`
   - Write tests for brain protection rules
   - Target: 50% coverage (Gate 1)

2. **Track Progress** (Future Enhancement)
   - Update progress as phases complete
   - Mark milestones as achieved

3. **Unblock Sub-Plans**
   - When Sub-Plan 00 reaches 50% coverage
   - Sub-Plans 01, 02, 05 will automatically unblock

---

**Last Updated:** January 3, 2026  
**Status:** Production Ready ✅  
**Current Focus:** Sub-Plan 00 - Test Coverage Sprint
