# Gap Analysis & Risk Assessment

**Date:** 2026-01-14  
**Scope:** SSOT Holistic Review  
**Status:** 27 Gaps Identified, 4 Critical

---

## Critical Production Blockers

### CRITICAL-001: SQLite Journal Mode

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-001 |
| **Component** | ProgressTrackerManager |
| **Impact** | Data corruption on power failure |
| **Root Cause** | SQLite journal_mode='delete' (default) |
| **Fix** | `PRAGMA journal_mode=WAL` |
| **Effort** | 15 minutes |
| **Risk Level** | 🔴 CRITICAL |

**Verification:**
```sql
-- Check current mode
PRAGMA journal_mode;
-- Expected: wal
-- If 'delete', WAL mode not enabled
```

---

### CRITICAL-002: Audit Schema Missing

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-002 |
| **Component** | EnhancedAuditLogger |
| **Impact** | Evidence validation broken |
| **Root Cause** | audit_logs table not created |
| **Fix** | Migration script + auto-init |
| **Effort** | 45 minutes |
| **Risk Level** | 🔴 CRITICAL |

**Verification:**
```sql
SELECT COUNT(*) FROM audit_logs;
-- Should not throw "no such table" error
```

---

### CRITICAL-003: Tracker Progress 0/0

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-003 |
| **Component** | ProgressTrackerManager |
| **Impact** | Phase gates unenforceable |
| **Root Cause** | progress-tracker.json shows 0/0 |
| **Fix** | Rebuild from AC-INDEX.yaml |
| **Effort** | 30 minutes |
| **Risk Level** | 🔴 CRITICAL |

**Verification:**
```python
tracker = load_json('progress-tracker.json')
assert tracker['phases']['week_1']['completed_count'] > 0
```

---

### CRITICAL-004: Pytest Collection Warnings

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-004 |
| **Component** | Test Infrastructure |
| **Impact** | Tests silently skipped |
| **Root Cause** | Dataclass names start with "Test" |
| **Fix** | Rename TestResult → ExecutionResult |
| **Effort** | 5 minutes |
| **Risk Level** | 🔴 CRITICAL |

**Verification:**
```bash
pytest --co -q 2>&1 | grep -c "warning"
# Should be 0
```

---

## High Priority Gaps

### GAP-001: Governance Enforcement 40%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-012 |
| **Current** | 10/25 rules enforced |
| **Target** | 25/25 rules enforced |
| **Impact** | Violations undetected |
| **Fix** | Wire GovernanceRegistry |
| **Effort** | 2 days |

---

### GAP-002: Evidence Generation 0%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-009 |
| **Current** | 0/100 implemented |
| **Target** | 100% AC-IDs have evidence |
| **Impact** | Cannot verify completion |
| **Fix** | Implement EvidenceBundleGenerator |
| **Effort** | 3 days |

---

### GAP-003: Verification Rate 0%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-014 |
| **Current** | 0% |
| **Target** | 80%+ |
| **Impact** | DoR assessment impossible |
| **Fix** | Evidence validation pipeline |
| **Effort** | 2 days |

---

### GAP-004: State Management 50%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-011 |
| **Current** | 50% complete |
| **Target** | 100% FSM coverage |
| **Impact** | Race conditions |
| **Fix** | Distributed locking |
| **Effort** | 1.5 days |

---

### GAP-005: Import Brittleness

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-005 |
| **Current** | Relative imports |
| **Target** | Absolute imports |
| **Impact** | Test collection fails |
| **Fix** | Convert imports |
| **Effort** | 2 hours |

---

### GAP-006: Test Collection 76%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-006 |
| **Current** | 35/46 files collect |
| **Target** | 46/46 files |
| **Impact** | Partial test execution |
| **Fix** | Fix syntax errors |
| **Effort** | 3 hours |

---

## Medium Priority Gaps

### GAP-007: Custom Template System

| Attribute | Value |
|-----------|-------|
| **Component** | TemplateResolver |
| **Current** | Not implemented |
| **Target** | Fallback chain working |
| **Impact** | Response formatting |
| **Effort** | 1.5 days |

---

### GAP-008: Cross-Platform Paths

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-010 |
| **Current** | Mixed path handling |
| **Target** | 100% pathlib |
| **Impact** | Windows failures |
| **Effort** | 2 days |

---

### GAP-009: AC Completeness 68%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-008 |
| **Current** | 11 missing implementations |
| **Target** | 100% implemented |
| **Impact** | Phase incomplete |
| **Effort** | 5 days |

---

### GAP-010: Test-AC Linking 0%

| Attribute | Value |
|-----------|-------|
| **ID** | AC-BRITTLE-013 |
| **Current** | 0% organized by AC |
| **Target** | 100% tests tagged |
| **Impact** | Cannot link results |
| **Effort** | 2 hours |

---

## Low Priority Gaps

| ID | Gap | Target | Effort |
|----|-----|--------|--------|
| GAP-011 | Hallucination prevention | Phase 2 | +3.5 days |
| GAP-012 | Cross-file coherence | Phase 4 | +5.25 days |
| GAP-013 | OpenTelemetry | Week 3 | 1 day |
| GAP-014 | Load testing | Week 4 | 2 days |
| GAP-015 | HIPAA compliance | Week 4 | 1 day |

---

## Risk Matrix

```
Impact ↑
  │
  │  ┌─────────┐     ┌─────────┐
  │  │CRITICAL │     │  HIGH   │
  │  │ 001-004 │     │ 001-006 │
  │  └─────────┘     └─────────┘
  │
  │  ┌─────────┐     ┌─────────┐
  │  │ MEDIUM  │     │   LOW   │
  │  │ 007-010 │     │ 011-015 │
  │  └─────────┘     └─────────┘
  │
  └────────────────────────────▶ Likelihood
```

---

## Mitigation Timeline

### Day 0 (Pre-Implementation)

| Task | Duration | Blocks |
|------|----------|--------|
| WAL mode | 15 min | Week 1 |
| Audit schema | 45 min | Week 1 |
| Tracker rebuild | 30 min | Week 1 |
| Pytest fix | 5 min | Week 1 |
| **Total** | **~2 hours** | |

### Week 1

| Task | Duration | Dependencies |
|------|----------|--------------|
| Governance wiring | 2 days | Day 0 complete |
| Import fixes | 2 hours | None |
| Test collection | 3 hours | Import fixes |

### Week 2

| Task | Duration | Dependencies |
|------|----------|--------------|
| Evidence generation | 3 days | Week 1 |
| State management | 1.5 days | Week 1 |
| Custom templates | 1.5 days | None |

### Week 3-4

| Task | Duration | Dependencies |
|------|----------|--------------|
| Verification rate | 2 days | Evidence |
| Cross-platform | 2 days | None |
| Observability | 3 days | None |

---

## Success Criteria

| Metric | Current | Target | Gate |
|--------|---------|--------|------|
| Critical gaps | 4 | 0 | Day 0 |
| Rules enforced | 40% | 100% | Week 1 |
| Evidence coverage | 0% | 100% | Week 2 |
| Verification rate | 0% | 80% | Week 3 |
| Test collection | 76% | 100% | Week 1 |
| Platform support | WIN only | WIN/MAC/Linux | Week 3 |

---

## Approval Status

**Critical Fixes:** ⚠️ MUST EXECUTE BEFORE WEEK 1

**High Priority:** ✅ PLANNED FOR WEEK 1-2

**Medium Priority:** ✅ PLANNED FOR WEEK 2-3

**Low Priority:** ✅ SCHEDULED FOR WEEK 3-4 + FUTURE

---

## SOLID/DRY Production Brittleness

**Reference:** `findings/solid-dry-review.md`

### Concrete Failures Identified

| Issue | Will Cause | Detection |
|-------|------------|-----------|
| Hardcoded `/Users/asifhussain` paths | FileNotFoundError on Windows | First run |
| Duplicate YAML loaders | Inconsistent validation | Schema change |
| No unified tool entry | State corruption | Concurrent use |
| Missing error propagation | Silent pipeline failure | Bad data |
| Unix-only file locking | Data corruption | Windows deploy |

### Mitigation Required Before Production

1. Search-replace hardcoded paths → portable resolution
2. Extract shared utilities into `src/core/`
3. Implement `Result[T]` error pattern
4. Add cross-platform locking with `filelock` library
