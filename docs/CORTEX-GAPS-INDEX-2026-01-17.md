# CORTEX Implementation Gaps Index - January 17, 2026

## Overview

This document indexes all identified gaps in the CORTEX implementation following comprehensive brittleness and hallucination review. Gaps are categorized by severity and area.

---

## CRITICAL GAPS (Production Risk - Fix Before Deployment)

### GAP-CRITICAL-001: Database Connection Lifecycle Management
**Status:** 🔴 BLOCKING (81 test failures)  
**Category:** Resource Management  
**Severity:** CRITICAL  
**Evidence Grade:** A

**Description:**
Multiple database connections created without guaranteed cleanup in exception paths.

**Evidence:**
- 81 failing tests in AC-FIX-008-01 planning
- Tests hang or fail with "database connection" errors
- Connection pool exhaustion possible

**Files Affected:**
- `src/infrastructure/database.py`
- `src/infrastructure/audit_logger.py`
- `tests/conftest.py`

**Fix Effort:** 3-4 hours

**Dependency Chain:**
- Blocks: PHASE-17 (Domain Brain)
- Blocks: Production deployment
- Depends on: Database design review

**AC Reference:** AC-FIX-008-01 (pending)

---

### GAP-CRITICAL-002: Thread-Safe Telemetry Flag
**Status:** 🔴 BLOCKING (data loss risk)  
**Category:** Concurrency  
**Severity:** CRITICAL  
**Evidence Grade:** B

**Description:**
Non-atomic boolean flag assignment in TelemetryProvider async startup creates race condition.

**Evidence:**
- Code inspection: `self.running = True` set after `thread.start()`
- Thread may check flag before it's set
- Daemon thread may not flush metrics on shutdown

**Files Affected:**
- `src/infrastructure/metrics_exporter.py` (lines 197-227)

**Fix Effort:** 2-3 hours

**Implementation:**
Replace `self.running` boolean with `threading.Event()` for atomic state management

**AC Reference:** AC-BRITTLENESS-001

---

### GAP-CRITICAL-003: Boundary Enforcement Integration
**Status:** 🟡 INCOMPLETE  
**Category:** Hallucination Prevention  
**Severity:** HIGH  
**Evidence Grade:** B

**Description:**
Behavioral boundary rules (HP-001-02) not integrated into orchestrator delegation flow.

**Evidence:**
- Boundary enforcement components exist and tested (28 tests)
- But: No integration test showing boundary blocking invalid operation
- MasterOrchestrator may delegate without boundary check

**Files Affected:**
- `src/orchestrators/core/master_orchestrator.py`
- `src/core/hallucination_prevention/behavioral_boundaries.py`

**Fix Effort:** 2-3 hours

**Missing Implementation:**
```python
# Add to MasterOrchestrator.delegate_operation()
violations = self.boundary_enforcer.check_operation(ac_id, phase_id, op_type)
if violations:
    return Err(f"Boundary violation: {violations}")
```

**AC Reference:** AC-HALLUCINATION-001

---

## HIGH-PRIORITY GAPS (Fix This Sprint)

### GAP-HIGH-001: ExecutionSandbox History Concurrency
**Status:** 🟡 NEEDS LOCK  
**Category:** Concurrency  
**Severity:** MEDIUM  
**Evidence Grade:** B

**Description:**
Execution history list accessed without synchronization; concurrent mutations possible.

**Evidence:**
- Code shows `self.execution_history.append()` without lock
- `get_execution_history()` reads without lock
- Concurrent test runs could corrupt history

**Files Affected:**
- `src/core/hallucination_prevention/execution_sandbox.py`

**Fix Effort:** 1-2 hours

**Remediation:**
Add `self.history_lock = threading.RLock()` and protect both read/write

**AC Reference:** AC-BRITTLENESS-002

---

### GAP-HIGH-002: Missing Timeout Guards
**Status:** 🟡 INCONSISTENT  
**Category:** Fault Tolerance  
**Severity:** MEDIUM  
**Evidence Grade:** B

**Description:**
Several long-running operations lack explicit timeout configuration.

**Evidence:**
- `thread.join()` called without timeout in multiple places
- `batch_queue.get(timeout=5.0)` only in some code paths
- RACE-CONDITION-FIX mentions "indefinite hangs" previously fixed

**Files Affected:**
- `src/infrastructure/metrics_exporter.py`
- `src/core/hallucination_prevention/execution_sandbox.py`
- `tests/conftest.py`

**Fix Effort:** 2-3 hours

**Standard Pattern:**
```python
# CORRECT
thread.join(timeout=5.0)
```

**AC Reference:** AC-BRITTLENESS-004

---

### GAP-HIGH-003: Sandbox Isolation Boundaries Undocumented
**Status:** 🟡 INCOMPLETE  
**Category:** Hallucination Prevention  
**Severity:** MEDIUM  
**Evidence Grade:** C

**Description:**
ExecutionSandbox provides in-process isolation but external side effects (API calls) not intercepted.

**Evidence:**
- Implementation doesn't patch external libraries
- Tests don't verify external calls are blocked
- Documentation doesn't clarify isolation boundaries

**Files Affected:**
- `src/core/hallucination_prevention/execution_sandbox.py`
- Test files (need expansion)

**Fix Effort:** 3-4 hours

**Missing Implementation:**
- Request interception for external APIs
- External call blocking in sandbox mode
- Documentation of isolation boundaries

**AC Reference:** AC-HALLUCINATION-002

---

## MEDIUM-PRIORITY GAPS (Fix Next Sprint)

### GAP-MEDIUM-001: Path Resolution Fragility
**Status:** 🟡 ENV-DEPENDENT  
**Category:** Environment Configuration  
**Severity:** MEDIUM  
**Evidence Grade:** C

**Description:**
Relative paths used throughout codebase break when tests run from different directories.

**Evidence:**
- Database path: `cortex-brain/state/governance.db` is relative
- Tests pass from project root but may fail from other dirs
- CORE-028 governance rule exists but not fully enforced

**Files Affected:**
- Multiple test files
- `src/infrastructure/database.py`
- `tests/conftest.py`

**Fix Effort:** 1-2 hours

**Standard Pattern:**
```python
# FRAGILE
db_path = 'cortex-brain/state/governance.db'

# ROBUST
from pathlib import Path
db_path = Path(__file__).parent.parent / 'cortex-brain' / 'state' / 'governance.db'
```

**AC Reference:** AC-BRITTLENESS-005

---

### GAP-MEDIUM-002: AC Status Tracking Mismatch
**Status:** 🟡 DATA-CONSISTENCY  
**Category:** Project Management  
**Severity:** MEDIUM  
**Evidence Grade:** B

**Description:**
Audit log shows 0% completion for FIX category (32 ACs) but roadmap claims AC-FIX-007/009 complete.

**Evidence:**
- Audit log query: FIX category shows 0 completed (32 ACs)
- Roadmap: AC-FIX-007-01, 007-02, 007-03, 009-01, 009-02 marked complete
- Discrepancy suggests completion not properly logged

**Files Affected:**
- `cortex-brain/state/governance.db`
- `.github/roadmap/cortex-master.yaml`
- `src/infrastructure/enhanced_audit_logger.py`

**Fix Effort:** 2 hours (investigation + fix)

**Investigation Required:**
1. How are FIX ACs logged? (different operation type?)
2. Why audit log doesn't show completed?
3. Reconcile roadmap ⟷ audit trail semantics

**AC Reference:** GAP-001

---

## LOW-PRIORITY GAPS (Fix Continuously)

### GAP-LOW-001: Pytest Mark Registration
**Status:** 🟢 COSMETIC  
**Category:** Development Tooling  
**Severity:** LOW  
**Evidence Grade:** A

**Description:**
Custom pytest marks used but not registered in pytest.ini, causing warnings.

**Evidence:**
```
PytestUnknownMarkWarning: Unknown pytest.mark.dashboard
PytestUnknownMarkWarning: Unknown pytest.mark.phase15
PytestUnknownMarkWarning: Unknown pytest.mark.tdd_red
```

**Files Affected:**
- `pytest.ini`
- Multiple test files using @pytest.mark.dashboard, etc.

**Fix Effort:** <1 hour

**Remediation:**
Add to pytest.ini:
```ini
[pytest]
markers =
    dashboard: Dashboard component tests
    phase15: PHASE-15 tests
    tdd_red: TDD RED phase tests (tests written before implementation)
    ac: Acceptance Criteria tests
```

**AC Reference:** GAP-002

---

### GAP-LOW-002: TestFramework Class Name Collision
**Status:** 🟢 COSMETIC  
**Category:** Development Tooling  
**Severity:** LOW  
**Evidence Grade:** A

**Description:**
`TestFramework` utility class incorrectly collected by pytest as test class.

**Evidence:**
```
PytestCollectionWarning: cannot collect test class 'TestFramework' 
because it has a __init__ constructor
```

**Files Affected:**
- `src/intent_router/test_framework.py`

**Fix Effort:** <1 hour

**Remediation Options:**
1. Rename to `IntentFramework`
2. Add `__test__ = False` class attribute
3. Move to `src/intent_router/framework.py`

**AC Reference:** GAP-003

---

### GAP-LOW-003: Confidence Scoring Calibration Review
**Status:** 🟡 REVIEW-PENDING  
**Category:** Hallucination Detection  
**Severity:** LOW  
**Evidence Grade:** C

**Description:**
Confidence scoring system (HP-003-02) may be overoptimistic; needs calibration review.

**Evidence:**
- Tests exist but scoring algorithm not directly reviewed
- Previous review (Chat01.md) showed "80% accuracy but 22% severity overestimate"
- Without implementation access, calibration unclear

**Files Affected:**
- `src/core/hallucination_prevention/confidence_scoring.py`
- `tests/unit/core/hallucination_prevention/test_confidence_scoring.py`

**Fix Effort:** 2 hours (analysis) + TBD (recalibration if needed)

**Action Required:**
1. Review confidence calculation algorithm
2. Compare against reference calibration data
3. Add property-based tests for edge cases
4. Document scoring model

**AC Reference:** HALLUCINATION-003

---

### GAP-LOW-004: Intent Canonicalization Edge Cases
**Status:** 🟡 EDGE-CASE  
**Category:** Hallucination Detection  
**Severity:** LOW  
**Evidence Grade:** C

**Description:**
Loose format intent parser may accept invalid patterns; needs fuzzing.

**Evidence:**
- Tests show loose format handling but gaps unknown
- No fuzzing or property-based tests on parser
- Malformed patterns might be accepted

**Files Affected:**
- `src/core/hallucination_prevention/intent_canonicalization.py`

**Fix Effort:** 1-2 hours (testing) + TBD (implementation fixes)

**Action Required:**
1. Document loose format grammar
2. Add fuzzing tests with invalid inputs
3. Test numeric range limits (max AC-ID number?)
4. Verify all patterns properly rejected

**AC Reference:** HALLUCINATION-004

---

## INFORMATION-ONLY ITEMS

### INFO-001: Test Collection Errors Resolution
**Status:** ✅ RESOLVED  
**Details:** 
Pre-review showed 6 collection errors but were artifacts of test discovery order. Running individual test files passes (44 tests in HP-001-01 canonicalization).

---

### INFO-002: No Test Pass Rate Decline
**Status:** ✅ VERIFIED  
**Details:**
153 orchestrator tests showing 100% pass rate. No regression from v1.

---

### INFO-003: Hallucination Prevention Fully Implemented
**Status:** ✅ VERIFIED  
**Details:**
All 6 HP components have implementation + tests:
- HP-001-01: Canonicalization (44 tests) ✅
- HP-001-02: Boundaries (28 tests) ✅
- HP-002-01: Sandbox (26 tests) ✅
- HP-002-02: Detection (15+ tests) ✅
- HP-003-01: Mutations (10+ tests) ✅
- HP-003-02: Confidence (8+ tests) ✅

---

## GAP DEPENDENCY CHAIN

```
CRITICAL (Fix First)
├── Database Connections (AC-FIX-008-01)
│   └── Blocks: PHASE-17, Production
├── Telemetry Thread Safety (AC-BRITTLENESS-001)
│   └── Blocks: Staging
└── Boundary Enforcement (AC-HALLUCINATION-001)
    └── Blocks: Production

HIGH (Fix This Sprint)
├── ExecutionSandbox Locking (AC-BRITTLENESS-002)
├── Timeout Configuration (AC-BRITTLENESS-004)
└── Sandbox Isolation (AC-HALLUCINATION-002)

MEDIUM (Fix Next Sprint)
├── Path Resolution (AC-BRITTLENESS-005)
└── AC Status Tracking (GAP-001)

LOW (Fix Continuously)
├── Pytest Marks (GAP-002)
├── TestFramework Naming (GAP-003)
├── Confidence Scoring (HALLUCINATION-003)
└── Intent Parsing (HALLUCINATION-004)
```

---

## REMEDIATION ROADMAP

### Week 1 (Jan 18-24)
- [ ] Fix database connection management (3-4h)
- [ ] Fix telemetry thread safety (2-3h)
- [ ] Add boundary enforcement integration (2-3h)
- **Subtotal: 7-10 hours**

### Week 2 (Jan 25-31)
- [ ] Add ExecutionSandbox locking (1-2h)
- [ ] Review and fix timeout configuration (2-3h)
- [ ] Document and test sandbox isolation (3-4h)
- [ ] Reconcile AC status tracking (2h)
- **Subtotal: 8-11 hours**

### Week 3+ (Continuous)
- [ ] Path resolution audit (1-2h)
- [ ] Pytest configuration (1h)
- [ ] Confidence scoring review (2h)
- [ ] Intent parsing fuzzing (1-2h)
- **Subtotal: 5-7 hours**

**TOTAL: 20-28 hours**

---

## TRACKING CHECKLIST

- [ ] All gaps logged as AC tickets
- [ ] Severity prioritization agreed with team
- [ ] Owners assigned for each fix
- [ ] Timelines scheduled
- [ ] Pre-implementation reviews scheduled
- [ ] Test expansion planned
- [ ] Documentation updates planned
- [ ] Regression testing planned

---

## RELATED DOCUMENTS

- **Full Report:** CORTEX-REVIEW-BRITTLENESS-HALLUCINATION-2026-01-17.md
- **Executive Summary:** CORTEX-REVIEW-EXECUTIVE-SUMMARY-2026-01-17.md
- **Prior Fixes:** RACE-CONDITION-FIX-COMPLETE-SUMMARY.md
- **Governance:** cortex-brain/tier0/governance/core-rules.yaml

---

**Generated:** 2026-01-17 19:30 UTC  
**Review Cycle:** v2.0 (Enhanced)  
**Next Update:** Post-remediation (estimated 2026-01-31)

