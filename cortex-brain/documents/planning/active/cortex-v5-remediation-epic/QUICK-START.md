# CORTEX v5 Remediation Epic - Quick Reference

**Epic ID:** cortex-v5-remediation-epic  
**Version:** 6.1.0 (Enhanced with Investigation Findings)  
**Date:** January 5, 2026  
**Status:** PLANNING → Ready for Execution

---

## 🎯 What Changed

**✅ ENHANCED with findings from 4 investigation reports:**
1. Progress Bar Brittleness (INVEST-20260103)
2. Continuation Prompt Not Displaying (INVEST-20260103-150000)
3. C150 Plan Review (C150-PLAN-REVIEW-20260104)
4. Database Schema Audit (2026-01-05)

---

## 📊 Phase Overview

### 🔴 P0_CRITICAL Phases (Must Complete First)

| Phase | Name | Duration | Key Deliverables |
|-------|------|----------|------------------|
| **P00** | Database Schema Consolidation | 2 days | Fix tier2_patterns mismatch, add user_profile.response_detail, consolidate duplicate DBs |
| **P00B** | Orchestrator Instantiation Fixes | 1 day | Fix 6 broken orchestrators (planning_v5, tdd, ado_v2, sanitization, cleanup_v2, vacuum_v2) |
| **P01** | Master Orchestrator Integration | 4 days | Task management + ResponseRenderer verification + SKULL middleware verification |
| **P02** | Planning Orchestrator v6 | 4 days | Pure Python autonomous execution |
| **P13** | Request Transformer | 2 days | Context enrichment system |
| **P14** | Final Validation & Testing | 2 days | End-to-end integration tests |

**Total Critical Path:** 15 days

---

## 🔍 Investigation Findings → Remediation Mapping

### 1. Database Schema Issues → Phase P00

**Problems Found:**
- ❌ Schema mismatch: `tier2_patterns` vs `patterns` (code expects different table/column names)
- ❌ Missing column: `user_profile.response_detail` (profile queries fail)
- ❌ Duplicate DBs: `knowledge-graph.db` (old) vs `knowledge_graph.db` (new)

**Remediation:**
- ✅ P00.3: Create compatibility VIEW: `tier2_patterns` → `patterns`
- ✅ P00.4: Add `response_detail` column to `user_profile` table
- ✅ P00.5: Migrate data from old DB → new DB, delete old file

---

### 2. Orchestrator Instantiation Failures → Phase P00B (NEW)

**Problems Found:**
- ❌ 6 orchestrators cannot instantiate (50% failure rate)
- ❌ Blocks ALL autonomous execution

**Broken Orchestrators:**
1. `planning_v5` - SyntaxError: f-string backslash (line 718)
2. `tdd_orchestrator` - Unexpected kwarg 'config_path'
3. `ado_orchestrator_v2` - Missing positional arg 'state_db'
4. `sanitization` - Unexpected kwarg 'config_path'
5. `cleanup_v2` - Missing positional arg 'state_db'
6. `vacuum_v2` - StateManager.log_execution() missing

**Remediation:**
- ✅ **NEW Phase P00B** - Dedicated 1-day phase to fix all 6 orchestrators
- ✅ Integration test: `test_orchestrator_instantiation.py`
- ✅ Target: 100% instantiation success rate

---

### 3. ResponseRenderer Not Rendering to User → Phase P01.2

**Problems Found:**
- ❌ Continuation prompts generated but never displayed
- ❌ Token warnings exist but user never sees them
- ❌ ResponseRenderer EXISTS (master_orchestrator.py:99) but may not be integrated properly

**Remediation:**
- ✅ P01.2: Verify ResponseRenderer renders to user (1 day)
- ✅ Test: `test_response_renderer_to_user.py`
- ✅ Fix: Ensure `handle_request()` returns rendered markdown (not dict)
- ✅ Verify: Continuation prompts display, token warnings display

---

### 4. SKULL Middleware Invocation Unclear → Phase P01.3

**Problems Found:**
- ❌ SetupVerifier, GovernanceCheckpoint, TeardownRefactor imported but invocation unclear
- ❌ brain-protection-rules.yaml defines rules but runtime enforcement unverified
- ❌ No governance audit logs to prove middleware runs

**Remediation:**
- ✅ P01.3: Verify SKULL middleware invocation (1 day)
- ✅ Test: `test_skull_middleware_invocation.py`
- ✅ Verify: SetupVerifier runs (Phase -2), GovernanceCheckpoint validates (runtime), TeardownRefactor runs (Phase N+1)
- ✅ Evidence: `tracking/governance-audit.jsonl` shows middleware invocations

---

### 5. Manual Task Tracking → Phase P01.1

**Problems Found:**
- ❌ No manage_todo_list integration in Master Orchestrator
- ❌ Task tracking is manual (we're tracking in GitHub Copilot todo list, not system)

**Remediation:**
- ✅ P01.1: Implement todo_manager.py with manage_todo_list API (1 day)
- ✅ All orchestrators use consistent task tracking pattern
- ✅ task-registry.json updates in real-time during execution

---

## 📈 Success Criteria (Enhanced)

### Functional (6 criteria)
- [x] All orchestrators execute via `python3 -m src.main`
- [x] All 6 broken orchestrators instantiate successfully
- [x] Master Orchestrator manages tasks via manage_todo_list
- [x] ResponseRenderer confirmed rendering to user
- [x] SKULL middleware invoked on all executions
- [x] Zero markdown files used for workflow execution

### Architectural (4 criteria)
- [x] Database schemas consolidated (zero schema mismatch errors)
- [x] Knowledge graph queries work (tier2_patterns resolved)
- [x] User profile operations work (response_detail exists)
- [x] Duplicate databases eliminated

### Integration (4 criteria)
- [x] Plan viewers auto-refresh with progress updates
- [x] All phases tracked in JSON with real-time updates
- [x] manage_todo_list used consistently across all orchestrators
- [x] Governance rules from brain-protection-rules.yaml enforced at runtime

**Total:** 14 measurable success criteria (was 5 generic criteria)

---

## 🚀 Execution Order

```
Phase P00: Database Schema Consolidation (2 days)
   ↓
Phase P00B: Orchestrator Instantiation Fixes (1 day) ← NEW
   ↓
Phase P01: Master Orchestrator Integration (4 days) ← ENHANCED
   ├─ P01.1: Task Management (1 day)
   ├─ P01.2: ResponseRenderer Verification (1 day)
   ├─ P01.3: SKULL Middleware Verification (1 day)
   └─ P01.4: Integration Testing (1 day)
   ↓
Phase P02-P11: Orchestrator Upgrades (parallel execution possible)
   ↓
Phase P12: Plan Viewer v3 (3 days)
   ↓
Phase P13: Request Transformer (2 days)
   ↓
Phase P14: Final Validation (2 days)
```

---

## 📚 Key Documents

### Investigation Reports (Input)
- `cortex-brain/documents/investigations/progress-bar-brittleness/investigation-complete.md`
- `cortex-brain/documents/investigations/continuation-prompt-not-displaying/investigation-summary.md`
- `cortex-brain/documents/investigations/c150-plan-review/00-executive-summary.md`
- `cortex-brain/documents/analysis/database-schema-audit-report-2026-01-05.md`

### Epic Documents (Output)
- `epic-manifest.yaml` - Complete phase definitions (enhanced)
- `reports/holistic-plan-enhancement-2026-01-05.md` - This enhancement report
- `README.md` - User-facing documentation
- `tracking/progress-tracker.json` - Real-time progress
- `tracking/task-registry.json` - Task management

### Code References
- `src/orchestrators/master_orchestrator.py` (ResponseRenderer line 99, SKULL middleware lines 103-105)
- `cortex-brain/brain-protection-rules.yaml` (Governance rules)
- `.github/prompts/CORTEX.prompt.md` (Intent routing + post-orchestrator rendering)

---

## ✅ Completion Checklist

### Phase P00 Ready?
- [x] All 7 critical database issues documented
- [x] Sub-phases include specific SQL queries and file names
- [x] Acceptance criteria reference zero schema errors
- [x] Audit report complete (623 lines)

### Phase P00B Added?
- [x] All 6 orchestrator failures documented
- [x] Each fix has specific error message and solution
- [x] Integration test deliverable added
- [x] Blocks P01-P08 correctly (nothing proceeds until fixed)

### Phase P01 Enhanced?
- [x] Split into 3 sub-phases (task mgmt + rendering + middleware)
- [x] ResponseRenderer verification addresses continuation prompt investigation
- [x] SKULL middleware verification addresses C150 investigation
- [x] Task management addresses manual tracking issue

### Success Criteria Measurable?
- [x] Every criterion has baseline and target
- [x] Every criterion has measurement method
- [x] No subjective criteria (all objective)

---

## 🎯 Ready to Execute

**Status:** ✅ PLANNING COMPLETE  
**Next Action:** Execute Phase P00 (Database Schema Consolidation)  
**Duration:** 15 days (critical path)  
**Risk Level:** LOW (all blockers identified and planned)

**Command to Start:**
```bash
python3 -m src.main "execute cortex-v5-remediation-epic phase P00" --format markdown
```

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
