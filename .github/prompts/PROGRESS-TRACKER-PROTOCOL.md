# 🎯 CORTEX Progress Tracker Protocol v2.1

**Purpose:** Eliminate progress tracker corruption and ensure holistic SSOT synchronization  
**Version:** 2.1.0 | **Date:** 2026-01-13  
**Status:** 🚀 PRODUCTION PROTOCOL  
**Author:** GitHub Copilot (CORTEX-EXEC)  
**Severity:** CRITICAL - Prevents execution state corruption
**Brittleness Fix Integration:** cortex-brain/tier0/governance/CORTEX-TOOLKIT-SINGLE-PATH-FIX.md (CORE-026/27/28)
**Governance:** CORE-001, CORE-026, CORE-027, CORE-028

---

## ❌ THE PROBLEM

**Challenge Statement:** Progress tracker updates have been **inconsistent, hardcoded, and out-of-sync** with actual implementation state.

### Evidence of Failures (Pre-Reconciliation 2026-01-13)

1. **Hardcoded 100% Status** - All phases showing "complete" regardless of actual completion
   - Phase 1: Shows 29 ACs (should be 30)
   - Phase 2: Shows 13 ACs, 100% complete (should be 54 ACs, 80% in-progress)
   - Phase 3: Shows 16 ACs, 100% complete (should be 18 ACs, 60% in-progress)

2. **Missing Phases** - Phases 1.5, 4, 4.5, 10, 11 not tracked at all

3. **Wrong AC Counts** - Tracker counts don't match AC-INDEX.yaml
   - Phase 5: Shows 3 ACs (should be 28)
   - Phase 9: Shows 5 ACs (should be 29)

4. **No Holistic Calculation** - Overall completion percentage hardcoded (~89% false vs 67.9% actual)

5. **Dashboard Corruption** - Dashboard showed "all phases complete" (misleading execution state)

### Root Causes

✗ **No atomic transaction model** - Individual AC updates without holistic recalculation  
✗ **No validation gates** - Missing pre/post update verification  
✗ **No audit trail** - Can't trace when/where state got corrupted  
✗ **No reconciliation** - No automated periodic SSOT verification  
✗ **No phase reconstruction** - Missing phases never added to tracker  
✗ **Hardcoded percentages** - Manual calculations instead of evidence-based  
✗ **No dashboard auto-sync** - Stale dashboard state persists  

---

## ✅ THE SOLUTION: HOLISTIC SSOT PROTOCOL

### Architecture Principles

1. **Single Writer Pattern** - Only MasterOrchestrator writes to progress-tracker.json
2. **Atomic Transactions** - All state updates are all-or-nothing (no partial writes)
3. **Evidence-Based Calculations** - All metrics derived from AC-INDEX.yaml + test results
4. **Holistic Recalculation** - After every AC-ID completion, entire tracker recalculated
5. **Pre/Post Validation** - Before update: validate; After update: verify integrity
6. **Automatic Reconciliation** - Periodic validation against git history + AC-INDEX
7. **Dashboard Auto-Sync** - Automatic regeneration after every state change

---

## 🔧 IMPLEMENTATION SPEC

### 1. **ProgressTrackerManager** (New Component)

**Location:** `src/infrastructure/progress_tracker_manager.py`

```python
class ProgressTrackerManager:
    """
    Manages all progress-tracker.json updates with atomic transactions,
    validation gates, and holistic recalculation.
    
    SINGLE WRITER: Only MasterOrchestrator calls this
    """
    
    def __init__(self, tracker_path: Path, ac_index_path: Path, master_plan_path: Path):
        """Initialize with SSOT file references"""
        self.tracker_path = tracker_path
        self.ac_index_path = ac_index_path
        self.master_plan_path = master_plan_path
        self.logger = get_audit_logger()
        
    def get_current_state(self) -> Dict[str, Any]:
        """Read current tracker state atomically"""
        # Use file locking to prevent corruption
        # Return deepcopy to prevent accidental mutations
        
    def update_ac_completion(self, ac_id: str, status: str, test_results: Dict) -> bool:
        """
        Update single AC-ID completion with holistic recalculation
        
        Process:
        1. Pre-validation: Check AC-ID exists in AC-INDEX
        2. Load current state
        3. Find AC-ID, update status
        4. Recalculate affected phase metrics
        5. Recalculate overall metrics
        6. Post-validation: Verify integrity
        7. Atomic write: Write entire tracker
        8. Auto-sync: Regenerate plan-viewer-data.json
        9. Log: Audit trail entry
        
        Args:
            ac_id: Acceptance criterion ID (e.g., "AC-ORCH-001")
            status: "completed", "in_progress", "blocked"
            test_results: {"total": N, "passed": M, "failed": K}
            
        Returns:
            True if successful, False if validation failed
        """
        
    def mark_phase_complete(self, phase_num: float) -> bool:
        """Mark entire phase as complete (100% all ACs)"""
        
    def reconcile_from_ac_index(self) -> Dict[str, Any]:
        """
        Holistic reconciliation against AC-INDEX.yaml
        
        Process:
        1. Read AC-INDEX.yaml (source of truth for all AC-IDs)
        2. Read master-plan.yaml (source of truth for phase definitions)
        3. For each phase:
           - Count total ACs from AC-INDEX
           - Count completed ACs from progress-tracker
           - Calculate completion_percentage
           - Verify phase status (completed / in_progress / blocked / not_started)
        4. Validate no AC-IDs are missing
        5. Validate no phases are missing
        6. If mismatches found: log, fix, update tracker
        7. Return reconciliation report
        """
        
    def validate_state_integrity(self, state: Dict) -> ValidationResult:
        """
        Pre-update validation:
        1. All phases have correct structure
        2. All AC-IDs referenced exist in AC-INDEX
        3. Completion percentages are 0-100
        4. total_ac_count ≥ completed_count
        5. Status is one of: completed, in_progress, blocked, not_started
        6. No negative or missing values
        7. Dates are valid ISO format
        
        Returns:
            ValidationResult with all_valid: bool, errors: List[str]
        """
        
    def _calculate_phase_metrics(self, phase_data: Dict) -> Dict:
        """
        Recalculate single phase metrics holistically
        
        From AC-INDEX.yaml, count:
        1. total_ac_count: Total ACs for this phase (from AC-INDEX)
        2. completed_count: Completed ACs (intersection of AC-INDEX + verified_implemented)
        3. completion_percentage: 100 * completed / total
        4. status: Derive from percentage (0=not_started, 1-99=in_progress, 100=completed)
        """
        
    def _calculate_overall_metrics(self, state: Dict) -> Dict:
        """
        Recalculate overall CORTEX metrics holistically
        
        Calculate:
        1. total_ac_count: SUM(all phase total_ac_count)
        2. completed_count: SUM(all phase completed_count)
        3. overall_completion_percentage: 100 * completed / total
        4. phases_complete: COUNT(phases where status == "completed")
        5. phases_in_progress: COUNT(phases where status == "in_progress")
        6. phases_not_started: COUNT(phases where status == "not_started")
        """
        
    def atomic_write(self, state: Dict, correlation_id: str) -> bool:
        """
        Write state atomically with file locking
        
        Process:
        1. Acquire exclusive lock on progress-tracker.json
        2. Validate state one final time
        3. Create backup (for recovery)
        4. Write new state
        5. Verify write succeeded
        6. Release lock
        7. Return success/failure
        """
        
    def auto_sync_dashboard(self) -> bool:
        """Regenerate derived files after successful update"""
        # Call scripts/regenerate_plan_viewer_data.py
        # Return success/failure
```

### 2. **MasterOrchestrator Integration**

**Update Method Signature:**

```python
class MasterOrchestrator:
    def complete_ac_id(self, ac_id: str, test_results: Dict) -> ExecutionResult:
        """
        Complete single AC-ID with holistic SSOT update
        
        Process:
        1. Validate AC-ID exists in AC-INDEX
        2. Validate test results (all tests passing)
        3. Call ProgressTrackerManager.update_ac_completion()
        4. Verify update succeeded
        5. Return result with correlation ID for audit trail
        
        Args:
            ac_id: Acceptance criterion ID
            test_results: {"total": N, "passed": N, "failed": 0}
            
        Returns:
            ExecutionResult with holistic metrics included
        """
        manager = ProgressTrackerManager(...)
        
        # Pre-validation
        if not self._validate_ac_id(ac_id):
            return ExecutionResult(success=False, error="AC-ID not in AC-INDEX")
        
        if test_results['failed'] > 0:
            return ExecutionResult(success=False, error="Tests not all passing")
        
        # Update with holistic recalculation
        success = manager.update_ac_completion(ac_id, "completed", test_results)
        
        if success:
            # Auto-sync dashboard
            manager.auto_sync_dashboard()
            return ExecutionResult(
                success=True,
                orchestrator="progress-tracker-manager",
                result={
                    "ac_id": ac_id,
                    "overall_completion_pct": manager.get_current_state()['overall_completion_pct'],
                    "phase_metrics": manager.get_current_state()['phases'],
                }
            )
        
        return ExecutionResult(success=False, error="Update failed validation")
    
    def complete_phase(self, phase_num: float) -> ExecutionResult:
        """Mark entire phase as complete (100% all ACs)"""
        manager = ProgressTrackerManager(...)
        
        # Validate phase has all ACs completed
        state = manager.get_current_state()
        phase_data = state[f"phase_{phase_num}"]
        
        if phase_data['completed_count'] != phase_data['total_ac_count']:
            return ExecutionResult(
                success=False,
                error=f"Phase {phase_num} not ready: {phase_data['completed_count']}/{phase_data['total_ac_count']}"
            )
        
        # Mark complete
        success = manager.mark_phase_complete(phase_num)
        
        if success:
            manager.auto_sync_dashboard()
            return ExecutionResult(success=True, ...)
        
        return ExecutionResult(success=False, ...)
```

### 3. **Periodic Reconciliation Task**

**New Scheduled Job (Every 1 hour):**

```python
async def periodic_reconciliation_task():
    """
    Hourly reconciliation against AC-INDEX.yaml + master-plan.yaml
    
    Detects and fixes:
    - Missing phases
    - Missing AC-IDs
    - Wrong AC counts
    - Incorrect completion percentages
    - Out-of-sync dashboard
    
    Logs all findings to audit trail for review
    """
    manager = ProgressTrackerManager(...)
    
    # Run reconciliation
    report = manager.reconcile_from_ac_index()
    
    if report['has_mismatches']:
        logger.warning(f"Progress tracker mismatches detected: {report}")
        # Auto-fix known issues
        # Log findings for human review
    
    # Regenerate dashboard
    manager.auto_sync_dashboard()
```

### 4. **Validation Gates (Pre/Post Update)**

**Pre-Update Validation:**
```
✓ AC-ID exists in AC-INDEX.yaml
✓ Phase exists in master-plan.yaml
✓ Test results show all tests passing
✓ No conflicting AC-ID states
✓ Tracker integrity check passes
```

**Post-Update Validation:**
```
✓ State successfully written to disk
✓ File can be read back (not corrupted)
✓ All calculations match expected values
✓ Integrity check passes
✓ Dashboard regeneration succeeded
```

---

## 🚀 PROTOCOL REQUIREMENTS

### R1: Atomicity
- All tracker updates are atomic (all-or-nothing)
- File locking prevents concurrent writes
- Backup created before every write

### R2: Holistic Recalculation
- After EVERY AC-ID completion, recalculate:
  - Phase metrics (completed_count, completion_percentage, status)
  - Overall metrics (overall_completion_pct, phases_complete, etc.)
  - Dashboard data (plan-viewer-data.json)

### R3: Evidence-Based Metrics
- All completion percentages derived from:
  - AC-INDEX.yaml (authoritative AC count)
  - verified_implemented list (actual completions)
  - Test results (evidence of completion)
- No hardcoding, no manual calculations

### R4: Single Writer
- Only MasterOrchestrator writes to progress-tracker.json
- No other scripts/agents modify tracker directly
- All updates go through ProgressTrackerManager

### R5: Validation Gates
- Pre-update: Validate incoming data
- Post-update: Verify state integrity
- Reject updates that don't pass validation

### R6: Automatic Reconciliation
- Periodic verification (hourly) against AC-INDEX + master-plan
- Auto-fix known issues
- Log findings for audit trail

### R7: Dashboard Auto-Sync
- After EVERY successful update, regenerate plan-viewer-data.json
- Guaranteed zero staleness
- Dashboard always reflects current state

### R8: Audit Trail
- Every update logged with:
  - Timestamp
  - AC-ID updated
  - Old state vs new state
  - Correlation ID (for tracing)
  - User/agent who triggered update

---

## 🔐 ENFORCEMENT MECHANISMS

### Mechanism 1: File Locking
```python
import fcntl

def atomic_read():
    with open(tracker_path, 'r') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_SH)  # Shared lock
        data = json.load(f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
    return data

def atomic_write(data):
    with open(tracker_path, 'w') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)  # Exclusive lock
        json.dump(data, f)
        fcntl.flock(f.fileno(), fcntl.LOCK_UN)
```

### Mechanism 2: Pre-Update Hooks
```python
@dataclass
class UpdateRequest:
    ac_id: str
    status: str
    test_results: Dict
    
    def validate(self, ac_index: Dict) -> ValidationResult:
        # Check AC-ID exists
        # Check status is valid
        # Check test_results format
        # Return ValidationResult(valid=bool, errors=[])
```

### Mechanism 3: Post-Update Hooks
```python
def post_update_hook(old_state: Dict, new_state: Dict) -> bool:
    # Verify write succeeded
    # Verify metrics recalculated
    # Verify no corruption
    # Verify dashboard regenerated
    # Return success/failure
```

### Mechanism 4: Periodic Validation
```python
@scheduler.scheduled_job('interval', hours=1)
def validate_tracker_integrity():
    # Load tracker
    # Load AC-INDEX
    # Load master-plan
    # Compare expected vs actual
    # Report mismatches
    # Auto-fix if possible
```

---

## 🛡️ RECOVERY PROCEDURES

### If Corruption Detected

1. **Detect Phase** - Validation check fails
2. **Alert** - Log ERROR to audit trail
3. **Restore from Backup** - Load last known-good state
4. **Reconcile** - Run reconciliation against AC-INDEX
5. **Fix Issues** - Auto-correct known problems
6. **Regenerate** - Update tracker + dashboard
7. **Report** - Human review of what went wrong

---

## 📊 MONITORING & OBSERVABILITY

### Metrics to Track

```
tracker_updates_total (counter)
tracker_update_duration (histogram)
tracker_validation_failures (counter)
tracker_reconciliation_mismatches (gauge)
dashboard_sync_duration (histogram)
dashboard_sync_failures (counter)
```

### Alerts

```
ALERT: tracker_validation_failure_rate > 5%
ALERT: tracker_reconciliation_mismatches > 0
ALERT: dashboard_sync_failure
ALERT: tracker_file_corruption_detected
```

---

## 🚀 DEPLOYMENT CHECKLIST

- [ ] ProgressTrackerManager implemented + tested
- [ ] MasterOrchestrator integration complete
- [ ] Validation gates implemented (pre/post)
- [ ] File locking mechanism working
- [ ] Periodic reconciliation job scheduled
- [ ] Auto-sync dashboard after updates
- [ ] Audit trail logging all operations
- [ ] Metrics collection implemented
- [ ] Alerts configured
- [ ] Recovery procedures documented
- [ ] All tests passing (evidence-based)
- [ ] Dashboard showing accurate state
- [ ] Team trained on new protocol

---

## 🎯 SUCCESS CRITERIA

✅ **Zero Progress Tracker Corruption**
- No more hardcoded percentages
- No more missing phases
- No more wrong AC counts

✅ **Holistic Recalculation**
- Every AC-ID update triggers phase + overall recalculation
- Metrics always match AC-INDEX + test evidence

✅ **Automatic Dashboard Sync**
- Dashboard always shows current state within 2 seconds
- Zero staleness

✅ **Evidence-Based Metrics**
- All percentages calculated from AC-INDEX + verified_implemented
- Auditable, verifiable, reproducible

✅ **Single Writer Pattern**
- Only MasterOrchestrator writes to tracker
- All updates go through ProgressTrackerManager
- No direct JSON manipulation

---

## 📞 REFERENCE

- **Previous Issue:** Progress tracker corruption (17 issues pre-reconciliation 2026-01-13)
- **Resolution Document:** RECONCILIATION-VERIFICATION-REPORT.md
- **Implementation Phase:** Phase 2 (ongoing) / Phase 4.5 (integration test framework)
- **Governance Rules:** CORE-001 (incremental), CORE-008 (TDD), CORE-017 (governance)

---

**Status:** 🚀 READY FOR IMPLEMENTATION  
**Author:** GitHub Copilot (CORTEX-EXEC)  
**Date:** 2026-01-13  
**Version:** 2.0.0

