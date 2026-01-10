# CORTEX 6.0 Complete Build - Continuation Prompt

**Plan ID:** plan-e763e821-4434-4189-8c90-312f13516c7d  
**Last Updated:** 2026-01-09  
**Current Status:** Stage 1 Foundation - Task 1.2 READY

---

## 🎯 How to Resume This Plan

When resuming work on this plan, use this prompt:

```
Continue CORTEX 6.0 complete build plan (plan-e763e821-4434-4189-8c90-312f13516c7d) 
from cortex-brain/documents/planning/active/cortex6/cortex6-planner/

CONTEXT:
- Master plan: 00-cortex6-complete-build.md (7 stages, 224-292 hours)
- Current stage: Stage 1 Foundation (40-48 hours)
- Current task: Task 1.2 GOV-001 - Governance Framework Migration (4-6 hours)
- Progress: 3.6% complete, 1 hour spent
- AUDIT-001: ✅ COMPLETE (29/29 tests passing)
- AC coverage: 203 acceptance criteria from v15.0.0 (target: 355+ post-remediation)
- Gap analysis: 487 issues identified (124 critical blocking)

COMPLETED:
- ✅ Task 1.1 AUDIT-001: AuditLogger Migration (100%)
  - src/infrastructure/enhanced_audit_logger.py (634 lines)
  - src/mcp/audit_tools.py (332 lines) - query, list, export, validate
  - tests/audit/test_audit_logger_enhanced.py (920 lines) - 29 tests
  - SQLite with 7 indexes, memory buffer, retention policy
  - All AC-AUDIT-001 through AC-AUDIT-006 validated

NEXT STEPS:
1. Start Task 1.2 GOV-001 - Governance Framework Migration
2. Review brain-protection-rules.yaml (61 SKULL rules)
3. Migrate governance to src/infrastructure/governance/
4. Enable AC-GOV-* criteria

PROGRESS TRACKER:
- Read: tracking/progress-tracker.json
- Update after each task completion
- Log effort in: tracking/effort-log.md
```

---

## 📊 Current State

### Stage 1: Foundation (CRITICAL PATH)
**Status:** ⚠️ IN PROGRESS  
**Completion:** 25%  
**Effort Spent:** 1 hour  
**Effort Remaining:** 39-47 hours

**Tasks:**
1. ✅ **Task 1.1: AUDIT-001** (1h actual) - COMPLETE
   - Implementation: DONE (29/29 tests passing)
   - Evidence: enhanced_audit_logger.py, audit_tools.py
   
2. ⏳ **Task 1.2: GOV-001** (4-6h) - READY (unblocked)
3. ⏳ **Task 1.3: TRACE-001** (8-10h) - READY (unblocked)
4. ⏸️ **Task 1.4: HOUSE-001** (12-16h) - PENDING (blocked by Task 1.2)

---

## 🔗 Key Documents to Review

### Before Starting Implementation
1. `00-cortex6-complete-build.md` - Master plan overview
2. `../foundation/AUDIT-001-Refactoring-Plan.md` - Complete implementation guide (550+ lines)
3. `../foundation/AUDIT-001-Quick-Reference.md` - Implementation checklist
4. `../foundation/AUDIT-001-Analysis-Summary.md` - Executive findings

### During Implementation
1. `../acceptance-criteria/CX6-acceptance-criteria.yaml` - All 355+ AC (reference)
2. `search-findings-20260109.yaml` - Gap analysis (487 issues)
3. `tracking/progress-tracker.json` - Update after each deliverable
4. `tracking/effort-log.md` - Log time spent

### Reference
1. `../../../../brain-protection-rules.yaml` - 61 SKULL rules (governance)
2. `../../../../documents/orchestrators-quick-ref.md` - Orchestrator documentation
3. `../../../../documents/cortex-architecture-quick-ref.md` - Architecture overview

---

## ⚠️ Known Blockers

### AC-ORC-012: Planning Orchestrator Persistence Bug
- **Impact:** Plans not persisted to planning.db despite success response
- **Workaround:** Manual YAML plan creation (this plan)
- **Resolution:** Stage 2, Task 2.3 (State Manager implementation)
- **Tracking:** CX6-acceptance-criteria.yaml v14.3.0

---

## 📝 Implementation Checklist

### AUDIT-001: AuditLogger Migration (Task 1.1)

**Phase 1: Preparation (1-2h)**
- [ ] Review existing implementation (src/orchestrators/audit_logger.py - 1133 lines)
- [ ] Review existing tests (tests/unit/test_audit_logger.py - 700 lines)
- [ ] Create src/infrastructure/ directory
- [ ] Design database schema (5 tables, 7 indexes)

**Phase 2: New Components (4-6h)**
- [ ] Implement SQLiteAuditBackend class
- [ ] Implement AuditRetentionPolicy class
- [ ] Implement memory buffer with 4 flush triggers
- [ ] Create database migration script

**Phase 3: Refactoring (4-5h)**
- [ ] Migrate AuditLogger to src/infrastructure/
- [ ] Add AC-ID tagging to all log methods
- [ ] Integrate SQLite backend
- [ ] Add retention policy enforcement

**Phase 4: MCP Tools (3-4h)**
- [ ] Implement mcp_audit_query
- [ ] Implement mcp_audit_list
- [ ] Implement mcp_audit_export
- [ ] Implement mcp_audit_validate

**Phase 5: Retention Policy (4h)**
- [ ] Implement automatic cleanup (cron-style)
- [ ] Implement manual vacuum trigger
- [ ] Add retention configuration

**Phase 6: Testing (2-3h)**
- [ ] Migrate existing tests (70% reusable)
- [ ] Add new tests for SQLite backend
- [ ] Add new tests for AC-ID tagging
- [ ] Add new tests for retention policy
- [ ] Add new tests for MCP tools

**Phase 7: Migration (1h)**
- [ ] Update all orchestrators to use new AuditLogger
- [ ] Remove old audit_logger.py from orchestrators/
- [ ] Update imports across codebase
- [ ] Verify all tests pass

---

## 🎯 Success Metrics for AUDIT-001

**Completion Criteria:**
- ✅ AuditLogger in src/infrastructure/ (not orchestrators/)
- ✅ SQLite backend with 5 tables, 7 indexes
- ✅ AC-ID tagging on ALL audit log entries
- ✅ Memory buffer with 4 flush triggers (size, time, level, manual)
- ✅ Retention policy (ERROR: 90d, INFO: 30d, DEBUG: 7d)
- ✅ 4 MCP tools functional (query, list, export, validate)
- ✅ Tests passing with >85% coverage
- ✅ Migration complete (old audit_logger.py removed)

**AC Enabled:** 8 AC (AC-AUDIT-001 through AC-AUDIT-008)

**Blocks Resolution:** 354+ AC now unblocked for validation

---

## 📞 Getting Help

If stuck during implementation:
1. Review SKULL rules: `../../../../brain-protection-rules.yaml`
2. Check architecture: `../../../../documents/cortex-architecture-quick-ref.md`
3. Reference orchestrators: `../../../../documents/orchestrators-quick-ref.md`
4. Read AC criteria: `../acceptance-criteria/CX6-acceptance-criteria.yaml`

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-09  
**Next Update:** After Task 1.1 completion
