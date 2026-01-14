# 🛠️ CORTEX SSOT Integrity Toolkit – Complete Documentation

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** 2026-01-13  
**Status:** Production Ready  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🎯 Overview

The **SSOT Integrity Toolkit** provides comprehensive tools to detect, repair, and prevent Single Source of Truth corruption in CORTEX 6.0. It implements a layered prevention strategy:

1. **Detection Layer** – Identifies corruption before it spreads
2. **Repair Layer** – Fixes issues atomically with rollback capability
3. **Prevention Layer** – Pre-commit hooks block corruption at source
4. **Validation Layer** – Post-merge reconciliation ensures consistency

---

## 📊 Components

### 1. **SSoTIntegrityValidator** (`src/tools/ssot_integrity_validator.py`)

**Purpose:** Detect and repair SSOT corruption

**Corruption Types Detected:**
- NULL AC counts in progress-tracker.json
- Orphaned ACs (in AC-INDEX but not in master-plan)
- Missing phases in progress-tracker
- Duplicate ACs across phases
- Hardcoded completion percentages
- AC-INDEX references without definitions

**Usage:**

```bash
# Validate only (read-only)
python3 src/tools/ssot_integrity_validator.py

# Repair with auto-fix
python3 src/tools/ssot_integrity_validator.py repair

# From toolkit
python3 src/mcp/toolkit_ssot_tools.py validate
python3 src/mcp/toolkit_ssot_tools.py repair --auto-fix
```

**Output:**
- Issue severity breakdown (CRITICAL, HIGH, MEDIUM, LOW)
- Auto-fixable vs. manual intervention required
- Affected items with details
- Repair report with backup locations

### 2. **ProgressTrackerManager** (`src/infrastructure/progress_tracker_manager.py`)

**Purpose:** Ensure atomic state updates with validation

**Key Methods:**

```python
# Update individual AC
manager.update_ac_completion(
    ac_id="AC-AUDIT-001",
    status="implemented",
    test_results={"passed": 5, "failed": 0, "total": 5},
    evidence_bundle={"commit": "abc123", "tests": [...]}
)

# Mark entire phase complete
manager.mark_phase_complete(
    phase_key="phase_1",
    completion_evidence={"all_acs_verified": True}
)

# Reconcile from AC-INDEX (authority)
report = manager.reconcile_from_ac_index(auto_fix=True)
```

**Guarantees:**
- ✅ Atomic writes (file locking + atomic rename)
- ✅ Pre/post validation gates
- ✅ Holistic metric recalculation (no hardcoding)
- ✅ Audit trail logging
- ✅ Rollback on validation failure

### 3. **Pre-commit Hook Guard** (`scripts/hooks/pre-commit-ssot-guard.sh`)

**Purpose:** Prevent corruption at commit time

**Checks:**
1. ❌ Block hardcoded percentages
2. ❌ Block NULL AC counts
3. ⚠️ Warn on AC removals
4. ❌ Validate YAML syntax
5. ❌ Validate JSON structure

**Installation:**

```bash
chmod +x scripts/hooks/pre-commit-ssot-guard.sh
cp scripts/hooks/pre-commit-ssot-guard.sh .git/hooks/pre-commit
```

### 4. **Post-merge Hook Reconcile** (`scripts/hooks/post-merge-ssot-reconcile.sh`)

**Purpose:** Auto-reconcile after merges

**Actions:**
1. Detect if SSOT files were modified
2. Run validation (non-blocking)
3. Alert on CRITICAL issues
4. Suggest `python3 src/tools/ssot_integrity_validator.py repair`

**Installation:**

```bash
chmod +x scripts/hooks/post-merge-ssot-reconcile.sh
cp scripts/hooks/post-merge-ssot-reconcile.sh .git/hooks/post-merge
```

### 5. **Toolkit MCP Wrapper** (`src/mcp/toolkit_ssot_tools.py`)

**Purpose:** Expose toolkit functions as MCP tools

**Implements AC-IDs:**
- `AC-TOOLKIT-SSOT-001`: SSOT Validator
- `AC-TOOLKIT-SSOT-002`: Auto-Repair
- `AC-TOOLKIT-SSOT-003`: Reconciliation
- `AC-TOOLKIT-SSOT-004`: State Validation

**MCP Tools (with @mcp_tool decorator):**

```python
@mcp_tool
def validate_ssot() -> Dict:
    """Validate SSOT integrity"""

@mcp_tool
def repair_ssot(auto_fix_only: bool = True) -> Dict:
    """Repair SSOT corruption"""

@mcp_tool
def reconcile_tracker(auto_fix: bool = False) -> Dict:
    """Reconcile progress-tracker from AC-INDEX"""

@mcp_tool
def update_ac_completion(ac_id: str, status: str, ...) -> Dict:
    """Update AC completion with validation"""

@mcp_tool
def mark_phase_complete(phase_key: str) -> Dict:
    """Mark phase complete after validation"""
```

---

## 🛡️ Prevention Architecture

### Layer 1: Pre-Commit (Blocks at source)
```
User commits SSOT file changes
    ↓
Pre-commit hook runs
    ├─ Check for hardcoded percentages (BLOCK)
    ├─ Check for NULL counts (BLOCK)
    ├─ Validate YAML syntax (BLOCK)
    └─ Warn on AC removals (WARN)
    ↓
If all pass: Allow commit
If any fail: Abort commit (user must fix)
```

### Layer 2: Pre-Push (MasterOrchestrator validation)
```
Before state update
    ↓
MasterOrchestrator calls ProgressTrackerManager
    ├─ Pre-validation: AC exists, phase valid
    ├─ Load current state
    ├─ Apply update with calculated metrics
    ├─ Post-validation: State integrity check
    └─ Atomic write (file lock + rename)
    ↓
If validation fails: Abort update, rollback
If passes: Persist with audit trail
```

### Layer 3: Post-Merge (Reconciliation)
```
After merge
    ↓
Post-merge hook runs
    ├─ Detect SSOT file changes
    ├─ Run validator (non-blocking)
    └─ Alert on CRITICAL issues
    ↓
If issues found: User can run repair
```

### Layer 4: Runtime (Continuous validation)
```
Every MasterOrchestrator state change
    ↓
ProgressTrackerManager.reconcile_from_ac_index()
    ├─ Count implemented ACs per phase (from AC-INDEX)
    ├─ Compare to tracker
    ├─ Recalculate holistically
    └─ Report discrepancies
    ↓
If issues detected: Log and alert
```

---

## 🔧 How to Use

### Scenario 1: Detect Corruption (Read-Only)

```bash
# Quick validation
python3 src/tools/ssot_integrity_validator.py

# Via toolkit
python3 src/mcp/toolkit_ssot_tools.py validate
```

**Output:**
- ✅ GREEN: No issues
- 🟡 YELLOW: Manual review needed
- 🔴 RED: Critical issues requiring immediate repair

### Scenario 2: Auto-Repair (Write Operation)

```bash
# Create backups, then repair
python3 src/tools/ssot_integrity_validator.py repair

# Via toolkit with explicit flag
python3 src/mcp/toolkit_ssot_tools.py repair --auto-fix
```

**Safety:**
- Backups saved to: `cortex-brain/backups/ssot-integrity/`
- Timestamp: `{filename}.backup.{YYYYMMDD_HHMMSS}`
- Rollback: Copy from backup if issues

### Scenario 3: Update AC Status

```python
from src.infrastructure.progress_tracker_manager import ProgressTrackerManager

manager = ProgressTrackerManager(
    tracker_path="cortex-brain/tier1/tracking/progress-tracker.json",
    ac_index_path="cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml",
    master_plan_path="cortex-brain/cx6-plan/master-plan.yaml"
)

# Update single AC (with validation)
success = manager.update_ac_completion(
    ac_id="AC-AUDIT-001",
    status="implemented",
    test_results={"passed": 5, "failed": 0, "total": 5}
)

if success:
    print("✅ AC-AUDIT-001 updated and validated")
else:
    print("❌ Update failed - state rolled back")
```

### Scenario 4: Mark Phase Complete

```python
# Validate and mark phase as complete
success = manager.mark_phase_complete(
    phase_key="phase_1",
    completion_evidence={"all_acs_verified": True, "tests": 30}
)

if success:
    print("✅ Phase 1 complete, Phase 2 queued")
```

### Scenario 5: Reconcile After Merge

```bash
# Check for merge conflicts in SSOT
python3 src/mcp/toolkit_ssot_tools.py reconcile

# Auto-apply fixes
python3 src/mcp/toolkit_ssot_tools.py reconcile --auto-fix
```

---

## 📋 Integration with MasterOrchestrator

**Current Status:** Ready for integration  
**Reference:** `src/orchestrators/core/master_orchestrator.py`

**How to Wire:**

```python
# In MasterOrchestrator.__init__()
from src.infrastructure.progress_tracker_manager import ProgressTrackerManager

self.tracker_manager = ProgressTrackerManager(
    tracker_path="cortex-brain/tier1/tracking/progress-tracker.json",
    ac_index_path="cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml",
    master_plan_path="cortex-brain/cx6-plan/master-plan.yaml"
)

# When completing an AC
success = self.tracker_manager.update_ac_completion(
    ac_id=ac_id,
    status="implemented",
    test_results=test_results
)

if not success:
    # Block phase progression
    return ExecutionResult(
        success=False,
        error="State update validation failed"
    )
```

---

## ⚠️ Corruption Prevention Rules (New CORE Rules)

### CORE-029: Atomic State Updates
**Rule:** All progress-tracker.json updates MUST use ProgressTrackerManager  
**Enforcement:** Pre-commit hook + runtime validation  
**Violation:** Write fails atomically, no partial state  

### CORE-030: No Hardcoded Metrics
**Rule:** completion_percentage, overall_progress MUST be calculated from AC counts  
**Enforcement:** Pre-commit hook blocks, ProgressTrackerManager recalculates  
**Violation:** Commit blocked if hardcoded percentages detected  

### CORE-031: Holistic Recalculation
**Rule:** Every state change triggers holistic recalculation of ALL phases  
**Enforcement:** ProgressTrackerManager._recalculate_all_phases()  
**Violation:** Inconsistent state detected in validation, update fails  

### CORE-032: SSOT Sync Gates
**Rule:** Phase gates only progress if SSOT integrity passes  
**Enforcement:** MasterOrchestrator checks before phase transition  
**Violation:** Phase cannot start with corrupted state  

---

## 🧪 Testing

### Unit Tests (TDD)

```bash
pytest tests/test_ssot_integrity.py -v
pytest tests/test_progress_tracker_manager.py -v
```

### Integration Tests (with CORTEX)

```bash
# Validate + repair cycle
python3 src/tools/ssot_integrity_validator.py
python3 src/tools/ssot_integrity_validator.py repair

# Verify state is healthy
python3 src/tools/ssot_integrity_validator.py
# Should show: ✅ No issues found
```

### Manual Testing

```bash
# 1. Introduce corruption
echo 'null' >> cortex-brain/tier1/tracking/progress-tracker.json

# 2. Detect
python3 src/tools/ssot_integrity_validator.py
# Should show: 🔴 CRITICAL: NULL AC counts

# 3. Repair
python3 src/tools/ssot_integrity_validator.py repair
# Should show: ✅ REPAIR COMPLETE

# 4. Verify
python3 src/tools/ssot_integrity_validator.py
# Should show: ✅ No issues found
```

---

## 📖 Reference

### Backup Locations
- **Automated backups:** `cortex-brain/backups/ssot-integrity/`
- **Format:** `{filename}.backup.{YYYYMMDD_HHMMSS}`
- **Retention:** Keep indefinitely (low disk impact)

### Audit Trail
- **Location:** `cortex-brain/audit-logs/`
- **Events:** All state updates logged with correlation ID
- **Query:** `python3 -m src.main "audit query --category ORCHESTRATOR --ac-id {ac_id}"`

### Configuration
- **SSOT Files:** (Read `cortex-exec.prompt.md`)
  - `cortex-brain/tier1/tracking/progress-tracker.json`
  - `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
  - `cortex-brain/cx6-plan/master-plan.yaml`
  - `cortex-brain/tier0/governance/core-rules.yaml`

---

## 🚀 Next Steps

1. ✅ **IMMEDIATE**: Wire ProgressTrackerManager into MasterOrchestrator
2. ✅ **IMMEDIATE**: Install pre-commit hooks (blocking corruption)
3. ✅ **This Sprint**: Register toolkit MCP tools (@mcp_tool decorators)
4. ✅ **This Sprint**: Add CORE-029/30/31/32 enforcement
5. ⏳ **Phase 2**: Integration tests with evidence validation
6. ⏳ **Phase 3**: Dashboard displays SSOT health status

---

## 📞 Support

**For issues:**
- Check backup status: `ls -lh cortex-brain/backups/ssot-integrity/`
- Run full validation: `python3 src/tools/ssot_integrity_validator.py`
- View recent changes: `git log --oneline cortex-brain/tier1/tracking/`

**For questions:**
- Read: `cortex-exec.prompt.md` (SSOT architecture)
- Reference: `master-plan.yaml → ssot_declaration`
- Audit trail: `python3 -m src.main "audit query --category ORCHESTRATOR"`
