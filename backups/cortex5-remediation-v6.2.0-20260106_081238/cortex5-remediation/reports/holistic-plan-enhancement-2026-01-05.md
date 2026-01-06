# CORTEX v5 Remediation Epic - Holistic Plan Enhancement Report

**Date:** January 5, 2026  
**Author:** CORTEX Architecture Review  
**Purpose:** Integrate findings from 3 investigation reports into remediation epic  
**Status:** ✅ COMPLETE

---

## 🎯 Executive Summary

**Action:** Enhanced `epic-manifest.yaml` to holistically address architectural gaps discovered in investigation reports.

**Key Changes:**
1. ✅ **Phase P00 Enhanced** - Added specific sub-phases and deliverables from database schema audit
2. ✅ **Phase P00B Added** - New phase for 6 orchestrator instantiation fixes (P0_CRITICAL)
3. ✅ **Phase P01 Expanded** - Split into 3 sub-phases: task management, ResponseRenderer verification, SKULL middleware verification
4. ✅ **Success Criteria Enhanced** - Added measurable criteria from investigation findings
5. ✅ **Investigation Findings Tracked** - Each investigation's root cause and remediation explicitly documented

---

## 📊 Investigation Reports Analyzed

### 1. Progress Bar Brittleness Investigation (INVEST-20260103)

**Root Cause:** CORTEX master prompt lacked explicit post-orchestrator rendering instructions.

**Status:** ✅ ALREADY RESOLVED (149-line "Post-Orchestrator Progress Rendering" section added to CORTEX.prompt.md)

**Impact on Epic:** No changes needed - prompt already fixed. Verified ResponseRenderer exists in master_orchestrator.py (line 99).

**Tracking:** Added verification step in Phase P01.2 to confirm rendering works end-to-end.

---

### 2. Continuation Prompt Not Displaying Investigation (INVEST-20260103-150000)

**Root Cause:** Master Orchestrator missing ResponseRenderer integration.

**Key Finding:** ResponseRenderer EXISTS but may not be integrated into execution pipeline properly.

**Evidence:**
```python
# master_orchestrator.py line 99 - EXISTS ✅
self.response_renderer = response_renderer or ResponseRenderer()

# BUT handle_request() may not call render() ❌
def handle_request(self, user_input: str, context: dict) -> dict:
    result = self.execute_orchestrator(...)
    return {"message": result.message}  # NOT RENDERED?
```

**Impact on Epic:**
- ✅ Phase P01.2 added: "Verify ResponseRenderer renders to user"
- ✅ Deliverable: `tests/integration/test_response_renderer_to_user.py`
- ✅ Acceptance criterion: "Continuation prompts display (no longer missing)"

**Investigation Recommended Solution:** Architecture Refactor (8 hours) - ResponseRenderer + ResponseMiddleware

**Epic Implementation:**
- ResponseRenderer already exists
- ResponseMiddleware may exist (need to verify)
- Phase P01.2 verifies integration and fixes if broken

---

### 3. C150 Plan Review Investigation (C150-PLAN-REVIEW-20260104)

**Root Causes:**
1. SKULL middleware exists but invocation unclear
2. 6 orchestrators cannot instantiate (P0 blocker)
3. False completion claims (100% but many issues remain)

**Key Findings:**

#### Finding 1: SKULL Middleware Invocation Unclear
```python
# master_orchestrator.py lines 103-105 - IMPORTED ✅
self.setup_verifier = SetupVerifier(workspace_root=Path.cwd())
self.governance_checkpoint = GovernanceCheckpoint(...)
self.teardown_refactor = TeardownRefactor(workspace_root=Path.cwd())

# BUT are they CALLED during execution? ❓
```

**Impact on Epic:**
- ✅ Phase P01.3 added: "Verify SKULL middleware invocation"
- ✅ Deliverable: `tests/integration/test_skull_middleware_invocation.py`
- ✅ Deliverable: `cortex-brain/documents/investigations/skull-middleware-verification-report.md`
- ✅ Acceptance criterion: "tracking/governance-audit.jsonl shows middleware invocations"

#### Finding 2: 6 Orchestrator Instantiation Failures

| Orchestrator | Error | File | Line |
|--------------|-------|------|------|
| planning_v5 | SyntaxError: f-string backslash | planning_orchestrator_v5.py | 718 |
| tdd_orchestrator | Unexpected kwarg 'config_path' | tdd_orchestrator.py | - |
| ado_orchestrator_v2 | Missing 'state_db' positional arg | ado_orchestrator_v2.py | - |
| sanitization | Unexpected kwarg 'config_path' | sanitization_orchestrator.py | - |
| cleanup_v2 | Missing 'state_db' positional arg | cleanup_orchestrator_v2.py | - |
| vacuum_v2 | StateManager.log_execution() missing | vacuum_orchestrator_v2.py | - |

**Impact on Epic:**
- ✅ **Phase P00B added** - Dedicated phase for these 6 fixes (P0_CRITICAL)
- ✅ Duration: 1 day
- ✅ Deliverables: All 6 orchestrators fixed + integration test
- ✅ Blocks: P01, P02, P03, P04, P05, P06, P07, P08 (nothing can proceed until these work)

---

### 4. Database Schema Audit Report (2026-01-05)

**Root Causes:**
1. Schema mismatch: `tier2_patterns` vs `patterns` (table + column names)
2. Missing column: `user_profile.response_detail`
3. Duplicate databases: `knowledge-graph.db` (old) vs `knowledge_graph.db` (new)
4. No compatibility views for backward compatibility

**Critical Issues (P0):**
- ❌ Pattern search fails (code expects `tier2_patterns.name`, DB has `patterns.title`)
- ❌ User profile queries fail (code expects `response_detail`, DB missing column)
- ❌ Data inconsistency (two knowledge graph DBs with different data)

**Impact on Epic:**
- ✅ Phase P00 sub-phases enhanced with specific details from audit
- ✅ P00.3: "Implement Database Views for Compatibility" (CREATE VIEW tier2_patterns AS SELECT...)
- ✅ P00.4: "Fix user_profile Schema (add response_detail column)"
- ✅ P00.5: "Consolidate Duplicate Databases (knowledge-graph.db → knowledge_graph.db)"
- ✅ P00.7: "Fix Code References (update pattern_search.py, unified_context_manager.py)"

---

## 📈 Epic Enhancements Summary

### New Phases Added

| Phase | Name | Priority | Duration | Addresses |
|-------|------|----------|----------|-----------|
| P00B | Critical Orchestrator Instantiation Fixes | P0_CRITICAL | 1 day | C150 Finding 2 |

### Existing Phases Enhanced

| Phase | Original | Enhanced | Justification |
|-------|----------|----------|---------------|
| P00 | Generic database consolidation | 8 specific sub-phases with deliverables from audit report | Database audit report findings |
| P01 | Basic task management | 3 sub-phases: task mgmt + ResponseRenderer verification + SKULL middleware verification | Continuation prompt + C150 investigations |

### Success Criteria Enhanced

**Before:** 5 generic criteria  
**After:** 3 categories with 16 specific measurable criteria

**Categories:**
1. **Functional** (6 criteria) - orchestrator execution, instantiation, task management, rendering, middleware
2. **Architectural** (4 criteria) - database schemas, knowledge graph, user profile, duplicates
3. **Integration** (4 criteria) - plan viewers, JSON tracking, manage_todo_list usage, governance enforcement

---

## 🔍 Investigation Findings → Epic Mapping

### Continuation Prompt Not Displaying → Phase P01.2

**Investigation Finding:**
- ResponseRenderer exists in master_orchestrator.py (line 99)
- BUT continuation prompts not displaying
- Recommended fix: Architecture refactor (ResponseRenderer + ResponseMiddleware)

**Epic Implementation:**
```yaml
sub_phases:
  - "P01.2: Verify ResponseRenderer renders to user (continuation prompt fix) (1 day)"

deliverables:
  - "tests/integration/test_response_renderer_to_user.py"
  - "Fixed: master_orchestrator.py handle_request() returns rendered markdown"
  - "Verified: continuation prompts display to user"
  - "cortex-brain/documents/investigations/response-renderer-verification-report.md"

acceptance_criteria:
  - "✅ ResponseRenderer confirmed rendering to GitHub Copilot Chat"
  - "✅ Continuation prompts display (no longer missing)"
  - "✅ Token warnings display to user"
```

---

### C150 SKULL Middleware Unclear → Phase P01.3

**Investigation Finding:**
- SetupVerifier, GovernanceCheckpoint, TeardownRefactor imported (lines 103-105)
- BUT invocation during execution unclear
- brain-protection-rules.yaml defines SETUP_VERIFICATION, TEARDOWN_REFACTOR rules
- No evidence middleware hooks actually called

**Epic Implementation:**
```yaml
sub_phases:
  - "P01.3: Verify SKULL middleware invocation (1 day)"

deliverables:
  - "tests/integration/test_skull_middleware_invocation.py"
  - "Verified: SetupVerifier runs before orchestrator execution (Phase -2)"
  - "Verified: GovernanceCheckpoint validates during execution"
  - "Verified: TeardownRefactor runs after execution (Phase N+1)"
  - "Fixed: middleware hooks integrated into execution_engine.py if missing"

acceptance_criteria:
  - "✅ SetupVerifier executes before every orchestrator (Phase -2 logged)"
  - "✅ GovernanceCheckpoint validates during execution (checkpoints logged)"
  - "✅ TeardownRefactor executes after every orchestrator (Phase N+1 logged)"
  - "✅ tracking/governance-audit.jsonl shows middleware invocations"
```

---

### C150 Orchestrator Instantiation Failures → Phase P00B

**Investigation Finding:**
- 6 orchestrators cannot instantiate (comprehensive brittleness audit)
- Blocks all autonomous execution
- Each orchestrator has specific error (f-string, kwargs, args, missing methods)

**Epic Implementation:**
```yaml
phase_id: "P00B"
name: "Critical Orchestrator Instantiation Fixes"
priority: P0_CRITICAL
duration: "1 day"
status: planning

issues_to_fix:
  - orchestrator: "planning_v5"
    error: "SyntaxError: f-string backslash"
    line: 718
  - orchestrator: "tdd_orchestrator"
    error: "unexpected kwarg 'config_path'"
  - orchestrator: "ado_orchestrator_v2"
    error: "missing positional arg 'state_db'"
  - orchestrator: "sanitization"
    error: "unexpected kwarg 'config_path'"
  - orchestrator: "cleanup_v2"
    error: "missing positional arg 'state_db'"
  - orchestrator: "vacuum_v2"
    error: "StateManager.log_execution() missing"

blocks: ["P01", "P02", "P03", "P04", "P05", "P06", "P07", "P08"]
```

---

### Database Schema Audit → Phase P00 Enhancement

**Investigation Finding:**
- 7 critical issues, 4 high priority, 3 moderate
- Schema mismatches blocking tier2 pattern search
- Duplicate databases causing confusion
- Missing compatibility views

**Epic Implementation:**
```yaml
sub_phases:
  - "P00.1: Schema Audit & Analysis (✅ COMPLETED - 623-line report)"
  - "P00.3: Implement Database Views for Compatibility (CREATE VIEW tier2_patterns...)"
  - "P00.4: Fix user_profile Schema (add response_detail column)"
  - "P00.5: Consolidate Duplicate Databases (knowledge-graph.db → knowledge_graph.db)"
  - "P00.7: Fix Code References (update pattern_search.py, unified_context_manager.py)"

deliverables:
  - "src/database/migrations/001_add_compatibility_views.sql"
  - "src/database/migrations/002_fix_user_profile_schema.sql"
  - "src/database/migrations/003_consolidate_knowledge_graphs.sql"
```

---

## 📊 Metrics & KPIs Enhanced

### Orchestrator Health Metrics (New)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Orchestrators broken | 6 (50%) | 0 (0%) | Integration test |
| Instantiation success rate | 50% | 100% | Registry scan |

### Integration Metrics (New)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Task tracking adoption | 0% (manual only) | 100% | Code review |
| Continuation prompt display | 0% (never) | 100% (always) | Integration test |
| SKULL middleware invocation | Unknown | 100% (every exec) | governance-audit.jsonl |

### Database Metrics (Enhanced)

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Schema consistency score | 45% | 100% | Schema validator |
| Database errors | 100% (blocking) | 0% | Log analysis |
| Duplicate tables | 6 | 0 | Schema audit |

---

## ✅ Verification Checklist

### Phase P00 Completeness
- [x] All 7 critical issues from audit report captured
- [x] Sub-phases include specific file names and SQL queries
- [x] Acceptance criteria reference zero schema errors
- [x] Deliverables include ERD diagram and documentation

### Phase P00B Addition
- [x] All 6 orchestrator failures documented with error messages
- [x] Each orchestrator has specific fix description
- [x] Integration test deliverable added
- [x] Blocks notation correct (prevents P01-P08 until fixed)

### Phase P01 Enhancement
- [x] Sub-phases split: task mgmt + rendering + middleware
- [x] ResponseRenderer verification includes test deliverable
- [x] SKULL middleware verification includes governance audit log
- [x] Investigation findings section maps each report to remediation

### Success Criteria Enhancement
- [x] Functional criteria include all 6 orchestrators working
- [x] Architectural criteria include zero database errors
- [x] Integration criteria include manage_todo_list adoption
- [x] All criteria are measurable (not subjective)

---

## 🚀 Next Steps

### Immediate (Today)
1. ✅ Review epic-manifest.yaml enhancements
2. ✅ Update progress-tracker.json with new phase P00B
3. ✅ Regenerate plan-viewer.html to show enhanced phases

### Phase P00 (2 days)
1. Execute database schema migration (P00.2-P00.8)
2. Verify zero schema errors after migration
3. Update ERD diagram and documentation

### Phase P00B (1 day)
1. Fix all 6 orchestrator instantiation failures
2. Run integration test: `pytest tests/integration/test_orchestrator_instantiation.py`
3. Verify 100% instantiation success rate

### Phase P01 (4 days)
1. P01.1: Implement todo_manager.py with manage_todo_list API
2. P01.2: Verify ResponseRenderer renders to user (fix continuation prompts)
3. P01.3: Verify SKULL middleware invocation (add hooks if missing)
4. P01.4: Integration testing (all 3 subsystems together)

---

## 📚 References

**Investigation Reports:**
- `cortex-brain/documents/investigations/progress-bar-brittleness/investigation-complete.md`
- `cortex-brain/documents/investigations/continuation-prompt-not-displaying/investigation-summary.md`
- `cortex-brain/documents/investigations/c150-plan-review/00-executive-summary.md`

**Database Audit:**
- `cortex-brain/documents/analysis/database-schema-audit-report-2026-01-05.md`

**Brain Protection Rules:**
- `cortex-brain/brain-protection-rules.yaml`

**Master Orchestrator:**
- `src/orchestrators/master_orchestrator.py` (lines 99, 103-105)

**Epic Manifest:**
- `cortex-brain/documents/planning/active/cortex5-remediation/epic-manifest.yaml`

---

## 🎉 Impact Summary

**Before Enhancement:**
- Generic phases with unclear deliverables
- No connection to investigation findings
- Success criteria not measurable
- 6 orchestrators broken with no fix plan

**After Enhancement:**
- Specific sub-phases with exact file names
- Every investigation finding mapped to remediation phase
- Success criteria measurable with baselines and targets
- Phase P00B added with specific fixes for each orchestrator

**Result:** Plan is now **holistic** and **actionable** with clear traceability from investigation reports to remediation phases.

---

**Status:** ✅ COMPLETE  
**Next Action:** Proceed with Phase P00 database schema consolidation

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
