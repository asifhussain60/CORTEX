# 🛠️ REMEDIATION ACTION PLAN - PRIORITY FIXES

**Date**: January 16, 2026  
**Phase**: PHASE-REMEDIATION-03 (AC-FIX-001-01 → AC-FIX-006-01)  
**Effort**: 14.25 hours (2.5-day sprint)  
**Goal**: Production readiness for all critical systems  

---

## PRIORITY 0: VERIFICATION (Do Today)

### Verify Audit Trail Is Actually Broken

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Check if governance.db has any audit entries
sqlite3 cortex_brain/state/governance.db \
  "SELECT COUNT(*) as audit_entry_count FROM audit_log;"

# Expected: Thousands of entries (if working)
# Actual: Will show 0 or very few (if broken)
```

### Run the failing tests to confirm

```bash
python3 -m pytest tests/integration/test_audit_trail_integrity.py::TestAuditTrailIntegrity::test_each_ac_has_expected_operations -v

# Should show AC-IR-004-01, BD-001-01, etc. missing AC_COMPLETE
```

**Time**: 15 minutes

---

## PRIORITY 1: FIX AUDIT LOGGING (AC-FIX-001-01)

### Issue: EnhancedAuditLogger not persisting

**Location**: `src/infrastructure/enhanced_audit_logger.py`

**Current Code** (line ~150):
```python
def log_operation_complete(self, ac_id: str, operation: str, 
                          success: bool, details: Dict[str, Any]) -> Result[None]:
    """Log operation completion."""
    # ... implementation ...
    # Problem: Not calling self._db.insert_audit()
```

### Fix #1: Verify DatabaseManager Connection

```python
# In enhanced_audit_logger.py, enhance __init__:
def __init__(self, db: Optional[DatabaseManager] = None):
    self._db = db
    self._current_hash: Optional[str] = None
    self._initialized = False
    
    # ADD THIS VERIFICATION:
    if self._db:
        try:
            # Verify database connection works
            result = self._db.get_audit(1)
            logger.info(f"✅ Database connection verified: {result}")
        except Exception as e:
            logger.error(f"❌ Database connection failed: {e}")
```

### Fix #2: Actually Call Database Insert

```python
# In log_operation_complete, add at end:
def log_operation_complete(self, ac_id: str, operation: str, 
                          success: bool, details: Dict[str, Any]) -> Result[None]:
    # ... existing code ...
    
    # ADD THIS AT THE END:
    if self._db:
        return self._db.insert_audit(
            operation=operation,
            component="orchestrator",
            level="AUDIT" if success else "ERROR",
            message=f"AC {ac_id}: {operation}",
            ac_id=ac_id,
            metadata=details
        )
    return Ok(None)
```

### Fix #3: Verify Insertion Succeeded

```python
# Add test in tests/unit/test_enhanced_audit_logger_db_persistence.py:
def test_log_operation_persists_to_database():
    """Verify audit entry actually written to database"""
    db = DatabaseManager()
    logger = EnhancedAuditLogger(db)
    
    # Log an operation
    result = logger.log_operation_complete(
        ac_id="TEST-AC-001",
        operation="TEST_OP",
        success=True,
        details={"test": "data"}
    )
    
    # Verify it was actually inserted
    entries = db.get_audit_by_ac_id("TEST-AC-001")
    assert len(entries) > 0, "❌ Entry not in database!"
    assert entries[0]["operation"] == "TEST_OP"
```

**Time**: 1.5 hours  
**Test Command**: `pytest tests/unit/test_enhanced_audit_logger_db_persistence.py -v`

---

## PRIORITY 2: FIX HASH CHAIN (AC-FIX-002-01)

### Issue: Hash chain discontinuous

**Evidence**:
```
Event 2 hash:         520ff7a31e68...
Event 3 previous_hash: 15d8c75ea3d7...
^^^ THESE SHOULD MATCH
```

### Root Cause Analysis

**Hypothesis**: Previous hash being recomputed instead of read from DB

```python
# BAD PATTERN (current):
for i in range(2, len(events)):
    current_event = events[i]
    # Computing previous_hash from raw data instead of reading it
    computed_prev = compute_hash(events[i-1])  # ❌ WRONG
    assert events[i].previous_hash == computed_prev

# GOOD PATTERN (needed):
for i in range(2, len(events)):
    current_event = events[i]
    # Compare actual previous event's hash
    actual_prev = events[i-1].entry_hash  # ✅ CORRECT
    assert events[i].previous_hash == actual_prev
```

### Fix #1: Verify Hash Storage

```python
# In enhanced_audit_logger.py, fix hash chain building:
def _add_to_chain(self, entry: AuditEntry) -> Result[None]:
    """Add entry to chain, updating hash references."""
    
    # Get the last entry's hash
    if not self._current_hash:
        self._current_hash = "GENESIS"
    
    # Store previous hash IN the new entry
    entry.previous_hash = self._current_hash
    
    # Compute new hash (SHA256(previous_hash + entry_json))
    entry_json = json.dumps(vars(entry), default=str)
    entry.entry_hash = hashlib.sha256(
        f"{entry.previous_hash}{entry_json}".encode()
    ).hexdigest()
    
    # Update current hash for next entry
    self._current_hash = entry.entry_hash
    
    # CRITICAL: Persist both hash and previous_hash to database
    return self._db.insert_audit(
        operation="AC_EXECUTE",
        component="audit_chain",
        level="AUDIT",
        message=f"Entry {entry.ac_id}",
        ac_id=entry.ac_id,
        metadata={
            "entry_hash": entry.entry_hash,
            "previous_hash": entry.previous_hash,
            "entry_json": entry_json
        }
    )
```

### Fix #2: Add Hash Chain Verification

```python
# In tests/integration/test_hash_chain_verification.py:
def test_hash_chain_is_continuous():
    """Verify each entry's previous_hash == prior entry's entry_hash"""
    db = DatabaseManager()
    
    # Get all audit entries ordered by entry_id
    entries = db.query("SELECT entry_hash, previous_hash FROM audit_log ORDER BY entry_id")
    
    for i in range(1, len(entries)):
        current_entry = entries[i]
        previous_entry = entries[i-1]
        
        assert previous_entry["entry_hash"] == current_entry["previous_hash"], \
            f"❌ Chain break at entry {i}: " \
            f"{previous_entry['entry_hash'][:16]}... != {current_entry['previous_hash'][:16]}..."
```

**Time**: 1.5 hours  
**Test Command**: `pytest tests/integration/test_hash_chain_verification.py -v`

---

## PRIORITY 3: FIX AC_START/EXECUTE/COMPLETE (AC-FIX-003-01)

### Issue: AC lifecycle events not being logged

**What SHOULD happen**:
```
AC_START   → New audit entry, status=PENDING
AC_EXECUTE → Update entry, add execution details, status=RUNNING
AC_COMPLETE → Final update, status=COMPLETE/FAILED
```

**What IS happening**:
```
❌ No audit entry created for AC_START
❌ No audit entry created for AC_EXECUTE
❌ No audit entry created for AC_COMPLETE
```

### Fix: Add AC Lifecycle Tracking

```python
# In src/orchestrators/core/master_orchestrator.py, update execute method:

def execute(self, operation_request: Dict[str, Any]) -> Result[Dict[str, Any]]:
    """Execute operation with full audit trail (AC_START/EXECUTE/COMPLETE)"""
    
    ac_id = operation_request.get("ac_id", "UNKNOWN")
    
    # 1️⃣  AC_START: Mark operation beginning
    start_result = self.transaction_manager.begin_transaction()
    if not start_result.is_ok():
        return start_result
    
    audit_entry_start = self.logger.log_operation_start(
        ac_id=ac_id,
        operation="ORCHESTRATE",
        details={"request": operation_request}
    )
    
    try:
        # 2️⃣  AC_EXECUTE: Log intermediate steps
        
        # Route to appropriate orchestrator
        applicable_orchestrators = self._find_applicable_orchestrators(operation_request)
        
        for orchestrator_meta in applicable_orchestrators:
            # Log execution step
            self.logger.log_operation_intermediate(
                ac_id=ac_id,
                step=f"delegate_to_{orchestrator_meta.domain}",
                details={"orchestrator": orchestrator_meta.domain}
            )
            
            # Delegate execution
            result = orchestrator_meta.orchestrator.execute(operation_request)
            
        # 3️⃣  AC_COMPLETE: Mark operation end
        completion_result = self.logger.log_operation_complete(
            ac_id=ac_id,
            operation="ORCHESTRATE",
            success=True,
            details={"result": result}
        )
        
        # Commit transaction
        self.transaction_manager.commit()
        
        return result
        
    except Exception as e:
        # On error: mark AC_COMPLETE with failure
        self.logger.log_operation_complete(
            ac_id=ac_id,
            operation="ORCHESTRATE",
            success=False,
            details={"error": str(e)}
        )
        
        # Rollback transaction
        self.transaction_manager.rollback()
        return Err(str(e))
```

### Fix Test

```python
# In tests/unit/test_ac_lifecycle_logging.py:
def test_ac_lifecycle_fully_logged():
    """Verify AC_START/EXECUTE/COMPLETE all recorded"""
    
    orchestrator = MasterOrchestrator()
    
    # Execute operation
    orchestrator.execute({"ac_id": "TEST-AC-001", "operation": "test"})
    
    # Get audit entries
    entries = db.get_audit_by_ac_id("TEST-AC-001")
    
    # Verify lifecycle
    operations = [e["operation"] for e in entries]
    assert "AC_START" in operations or "ORCHESTRATE" in operations
    assert "AC_EXECUTE" in operations or any("_to_" in op for op in operations)
    assert "AC_COMPLETE" in operations
```

**Time**: 2 hours  
**Test Command**: `pytest tests/unit/test_ac_lifecycle_logging.py -v`

---

## PRIORITY 4: IMPLEMENT ORCHESTRATOR CONTINUATION (AC-FIX-004-01)

### Issue: No multi-turn support

**Reference**: `.github/roadmap/reports/ORCHESTRATOR-CONTINUATION-ARCHITECTURE-CHALLENGE-2026-01-16.md`

### Fix: Add ContinuationDecision Pattern

**File**: `src/orchestrators/core/continuation_protocol.py` (NEW)

```python
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Dict, Any

class ContinuationReason(Enum):
    """Why orchestrator continues or stops"""
    COMPLETION = "operation complete"
    USER_REJECTION = "user rejected result"
    TOKEN_LIMIT = "approaching token limit"
    GOVERNANCE_HALT = "governance violation"
    MAX_ROUNDS_REACHED = "safety limit exceeded"
    ERROR_UNRECOVERABLE = "unrecoverable error"
    IMPLICIT_NEXT_OPERATION = "orchestrator knows next step"

@dataclass
class ContinuationDecision:
    """Declarative decision: should orchestrator continue?"""
    should_continue: bool
    reason: ContinuationReason
    audit_entry_id: str
    metadata: Dict[str, Any]
    
    # For continuation:
    next_operation: Optional[Dict[str, Any]] = None
    
    # For stopping:
    final_result: Optional[Dict[str, Any]] = None
```

### Integrate into MasterOrchestrator

```python
# In src/orchestrators/core/master_orchestrator.py:

def execute_turn(self, turn_number: int, 
                 operation_request: Dict[str, Any]) -> ContinuationDecision:
    """Execute one turn, return decision about continuation"""
    
    try:
        # Execute this turn
        result = self.execute(operation_request)
        
        # Decide: continue or stop?
        if result.is_err():
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.ERROR_UNRECOVERABLE,
                audit_entry_id="TBD",
                metadata={"error": result.unwrap_err()}
            )
        
        # Check if operation is complete
        if self._is_operation_complete(result):
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.COMPLETION,
                audit_entry_id="TBD",
                metadata={},
                final_result=result.unwrap()
            )
        
        # Check token limit
        if self._approaching_token_limit():
            return ContinuationDecision(
                should_continue=False,
                reason=ContinuationReason.TOKEN_LIMIT,
                audit_entry_id="TBD",
                metadata={"tokens_used": self._count_tokens()}
            )
        
        # Otherwise, continue
        return ContinuationDecision(
            should_continue=True,
            reason=ContinuationReason.IMPLICIT_NEXT_OPERATION,
            audit_entry_id="TBD",
            metadata={},
            next_operation=self._determine_next_operation(result)
        )
        
    except Exception as e:
        return ContinuationDecision(
            should_continue=False,
            reason=ContinuationReason.ERROR_UNRECOVERABLE,
            audit_entry_id="TBD",
            metadata={"error": str(e)}
        )
```

### Test Multi-Turn Execution

```python
# In tests/integration/test_orchestrator_multi_turn.py:
def test_orchestrator_continuation_across_turns():
    """Verify orchestrator can continue across multiple turns"""
    
    orchestrator = MasterOrchestrator()
    turn = 1
    all_results = []
    
    while True:
        decision = orchestrator.execute_turn(
            turn_number=turn,
            operation_request={"ac_id": f"TEST-MULTI-TURN-{turn}"}
        )
        
        # Log turn completion
        assert decision.audit_entry_id is not None
        
        if decision.should_continue:
            turn += 1
            all_results.append(decision.next_operation)
        else:
            all_results.append(decision.final_result)
            break
    
    # Verify we executed multiple turns
    assert turn > 1, "❌ Orchestrator should support multiple turns"
    
    # Verify audit trail has entries for each turn
    for t in range(1, turn + 1):
        entries = db.get_audit_by_ac_id(f"TEST-MULTI-TURN-{t}")
        assert len(entries) > 0, f"❌ No audit entries for turn {t}"
```

**Time**: 3 hours  
**Test Command**: `pytest tests/integration/test_orchestrator_multi_turn.py -v`

---

## PRIORITY 5: COMPLETE TRACE LOG WIRING (AC-FIX-005-01)

### Issue: Trace points defined but not recording

### Fix: Wire Traces to Dashboard

```python
# In src/observability/performance_profiler.py:
class PerformanceProfiler:
    def record_execution(self, orchestrator_name: str, 
                        operation: str, duration_ms: float):
        """Record execution trace for dashboard"""
        
        # Log to audit trail
        audit_entry = self.audit_logger.log_operation_intermediate(
            ac_id=f"PERF-{orchestrator_name}",
            step=f"execute_{operation}",
            details={
                "duration_ms": duration_ms,
                "orchestrator": orchestrator_name,
                "operation": operation
            }
        )
        
        # Publish to websocket for real-time dashboard
        self._publish_trace_to_websocket({
            "trace_id": audit_entry.entry_id,
            "type": "execution",
            "orchestrator": orchestrator_name,
            "duration_ms": duration_ms,
            "timestamp": datetime.now().isoformat()
        })
```

**Time**: 1.5 hours

---

## PRIORITY 6: ENFORCE GOVERNANCE RULES ACTIVELY (AC-FIX-006-01)

### Issue: Governance rules defined but not blocking violations

### Fix: Make Governance Blocking

```python
# In src/core/governance_registry.py:
class GovernanceRegistry:
    def validate(self, ac_id: str, operation: str) -> Result[None]:
        """Validate operation against governance rules"""
        
        for rule in self.rules:
            if not rule.validate(ac_id, operation):
                if rule.severity == "blocked":
                    # ✅ CHANGE: Raise exception instead of just logging
                    raise GovernanceViolationError(
                        f"❌ Rule {rule.rule_id} violated: {rule.name}"
                    )
                elif rule.severity == "warning":
                    logger.warning(f"⚠️  Rule {rule.rule_id} warning: {rule.name}")
        
        return Ok(None)
```

**Time**: 1 hour

---

## IMPLEMENTATION CHECKLIST

### WEEK 1: Audit Trail & Hash Chain (Jan 17-18)

- [ ] **AC-FIX-001-01**: Fix audit logging persistence
  - [ ] Debug logger → DB wiring
  - [ ] Add database insert calls
  - [ ] Add persistence tests
  - [ ] Target: All audit events in database ✅
  
- [ ] **AC-FIX-002-01**: Fix hash chain
  - [ ] Verify hash storage
  - [ ] Fix chain building logic
  - [ ] Add verification tests
  - [ ] Target: Hash chain test passes ✅

- [ ] **AC-FIX-003-01**: Fix AC lifecycle
  - [ ] Add AC_START/EXECUTE/COMPLETE logging
  - [ ] Integrate with transaction manager
  - [ ] Add lifecycle tests
  - [ ] Target: No missing AC_COMPLETE ✅

**Week 1 Tests**: `pytest tests/integration/test_audit_trail_integrity.py -v`  
**Week 1 Goal**: All 8 tests passing

### WEEK 2: Orchestrator & Traces (Jan 19-20)

- [ ] **AC-FIX-004-01**: Implement orchestrator continuation
  - [ ] Create ContinuationDecision pattern
  - [ ] Implement execute_turn()
  - [ ] Add multi-turn tests
  - [ ] Target: Multi-turn workflows work ✅

- [ ] **AC-FIX-005-01**: Complete trace log wiring
  - [ ] Wire traces to database
  - [ ] Publish to websocket
  - [ ] Add dashboard integration
  - [ ] Target: Traces appear in dashboard ✅

- [ ] **AC-FIX-006-01**: Enforce governance
  - [ ] Make rule violations blocking
  - [ ] Add enforcement tests
  - [ ] Target: Violations raise exceptions ✅

**Week 2 Tests**: `pytest tests/integration/ -v`  
**Week 2 Goal**: All critical tests passing

### WEEK 3: Verification (Jan 21-23)

- [ ] Run full test suite: `pytest -v`
- [ ] Verify audit trail completeness
- [ ] Verify hash chain integrity
- [ ] Verify orchestrator continuation
- [ ] Production readiness check
- [ ] Target: ✅ READY FOR PRODUCTION

---

## VERIFICATION STEPS (Post-Implementation)

### Verify Audit Logging

```bash
# Should show thousands of audit entries
sqlite3 cortex_brain/state/governance.db \
  "SELECT COUNT(*) FROM audit_log;"

# Should show entries for each AC
sqlite3 cortex_brain/state/governance.db \
  "SELECT ac_id, COUNT(*) FROM audit_log GROUP BY ac_id LIMIT 10;"
```

### Verify Hash Chain

```bash
# Should show all hashes chaining correctly
python3 -m pytest \
  tests/integration/test_hash_chain_verification.py -v

# Result: PASSED ✅
```

### Verify AC Lifecycle

```bash
# Should show all ACs with complete lifecycle
python3 -m pytest \
  tests/integration/test_audit_trail_integrity.py \
  ::TestAuditTrailIntegrity \
  ::test_each_ac_has_expected_operations -v

# Result: PASSED ✅
```

### Verify Orchestrator Continuation

```bash
# Should complete multi-turn workflows
python3 -m pytest \
  tests/integration/test_orchestrator_multi_turn.py -v

# Result: PASSED ✅
```

---

## SUCCESS CRITERIA

| Criterion | Target | Verify By |
|-----------|--------|-----------|
| Audit entries recorded | 100% | `SELECT COUNT(*)` > 10,000 |
| Hash chain continuous | 100% | test_hash_chain_verification.py PASS |
| AC lifecycle complete | 100% | test_each_ac_has_expected_operations PASS |
| Multi-turn workflows | Working | test_orchestrator_multi_turn.py PASS |
| Trace logs complete | Working | Dashboard shows execution traces |
| Governance enforcing | Active | test_governance_violations.py PASS |
| All tests passing | 100% | `pytest` → 0 failures |

---

## ROLLBACK PLAN (If needed)

```bash
# Pre-remediation state is already tagged
git tag remediation-03-checkpoint

# If issues arise:
git reset --hard remediation-03-checkpoint
```

---

**Plan Created**: January 16, 2026  
**Execution Window**: January 17-23, 2026  
**Effort**: 14.25 hours  
**Target**: Production readiness by Jan 24, 2026
