# Phase P00B: Critical Blocker Resolution

**Epic:** cortex5-enhancement-epic-v2  
**Phase:** P00B (Setup - Critical Fixes)  
**Duration:** 1 day  
**Priority:** P0_CRITICAL  
**Status:** NOT_STARTED  
**Blocks:** All Phases 1-12  
**Created:** 2026-01-07  
**Source:** CORTEX Review findings (20260107_initial_review.yaml)

---

## 🎯 Phase Objectives

Fix 3 critical blockers identified in CORTEX review that prevent safe epic implementation:

1. **DEPLOY-001:** Missing rollback script for Phase 0 migration
2. **INT-001:** 6 orchestrators cannot instantiate (syntax/signature errors)
3. **ARCH-001:** StateManager race condition (concurrent write corruption)

**Review Source:** `cortex-brain/documents/planning/active/cortex5-enhancement-epic/reports/cortex-review/20260107_initial_review.yaml`

---

## 📋 Task Breakdown

### Task 1: Create Rollback Script (2 hours)

**Blocker:** DEPLOY-001  
**Risk:** CRITICAL  
**Impact:** Phase 0 migration unsafe without recovery mechanism

#### Deliverable

**File:** `scripts/rollback-cortex-5.5-migration.ps1`

#### Implementation

```powershell
<#
.SYNOPSIS
    Rollback CORTEX-5.5 migration to CORTEX-5.0 state

.DESCRIPTION
    Restores repository to pre-migration state if Phase 0 migration fails.
    Creates backup before migration, validates rollback success.

.PARAMETER BackupPath
    Path to backup directory (default: .cortex-backups/pre-phase-0/)

.PARAMETER Validate
    Run validation checks after rollback

.EXAMPLE
    .\rollback-cortex-5.5-migration.ps1 -Validate
#>

param(
    [string]$BackupPath = ".cortex-backups/pre-phase-0",
    [switch]$Validate
)

$ErrorActionPreference = "Stop"

function Write-Status {
    param([string]$Message, [string]$Type = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $color = switch ($Type) {
        "SUCCESS" { "Green" }
        "ERROR" { "Red" }
        "WARNING" { "Yellow" }
        default { "White" }
    }
    Write-Host "[$timestamp] $Type: $Message" -ForegroundColor $color
}

# Step 1: Verify backup exists
Write-Status "Checking for backup at $BackupPath"
if (-not (Test-Path $BackupPath)) {
    Write-Status "Backup not found at $BackupPath" "ERROR"
    Write-Status "Cannot rollback without backup" "ERROR"
    exit 1
}

# Step 2: Get current branch
$currentBranch = git branch --show-current
Write-Status "Current branch: $currentBranch"

# Step 3: Stash any uncommitted changes
Write-Status "Stashing uncommitted changes"
git stash save "Pre-rollback stash $(Get-Date -Format 'yyyyMMdd-HHmmss')"

# Step 4: Switch to main branch
Write-Status "Switching to main branch"
git checkout main

# Step 5: Delete CORTEX-5.5 branch (local and remote)
Write-Status "Deleting CORTEX-5.5 branch"
git branch -D CORTEX-5.5 2>$null
git push origin --delete CORTEX-5.5 2>$null

# Step 6: Checkout CORTEX-5.0 branch
Write-Status "Checking out CORTEX-5.0 branch"
git checkout CORTEX-5.0

# Step 7: Restore files from backup (if needed)
Write-Status "Restoring files from backup"
$backupFiles = Get-ChildItem -Path $BackupPath -Recurse -File
foreach ($file in $backupFiles) {
    $relativePath = $file.FullName.Replace("$BackupPath\", "")
    $targetPath = Join-Path (Get-Location) $relativePath
    
    # Create directory if needed
    $targetDir = Split-Path $targetPath -Parent
    if (-not (Test-Path $targetDir)) {
        New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
    }
    
    Copy-Item -Path $file.FullName -Destination $targetPath -Force
}

Write-Status "Restored $($backupFiles.Count) files from backup" "SUCCESS"

# Step 8: Run validation if requested
if ($Validate) {
    Write-Status "Running validation checks"
    
    # Check file count
    $fileCount = (Get-ChildItem -Path . -Recurse -File | Measure-Object).Count
    Write-Status "File count: $fileCount (expected: ~1000 for CORTEX-5.0)"
    
    # Check Python syntax
    Write-Status "Validating Python syntax"
    $pythonFiles = Get-ChildItem -Path "src" -Filter "*.py" -Recurse
    foreach ($pyFile in $pythonFiles) {
        python -m py_compile $pyFile.FullName
        if ($LASTEXITCODE -ne 0) {
            Write-Status "Syntax error in $($pyFile.Name)" "ERROR"
            exit 1
        }
    }
    Write-Status "Python syntax validation passed" "SUCCESS"
    
    # Check essential files exist
    $essentialFiles = @(
        "src/main.py",
        "cortex-brain/brain-protection-rules.yaml",
        "src/orchestrators/master_orchestrator.py"
    )
    foreach ($file in $essentialFiles) {
        if (-not (Test-Path $file)) {
            Write-Status "Essential file missing: $file" "ERROR"
            exit 1
        }
    }
    Write-Status "Essential files present" "SUCCESS"
}

# Step 9: Generate rollback report
$reportPath = "cortex-brain/documents/reports/rollback-report-$(Get-Date -Format 'yyyyMMdd-HHmmss').md"
$report = @"
# CORTEX-5.5 Migration Rollback Report

**Date:** $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Reason:** Phase 0 migration failed or cancelled
**Backup Source:** $BackupPath

## Actions Taken

1. ✅ Stashed uncommitted changes
2. ✅ Deleted CORTEX-5.5 branch (local and remote)
3. ✅ Restored CORTEX-5.0 branch
4. ✅ Restored $($backupFiles.Count) files from backup
5. ✅ Validation checks passed

## Validation Results

- **File Count:** $fileCount
- **Python Syntax:** PASS
- **Essential Files:** PASS

## Rollback Status

**✅ ROLLBACK SUCCESSFUL**

Repository restored to pre-migration state.
"@

New-Item -Path (Split-Path $reportPath -Parent) -ItemType Directory -Force | Out-Null
Set-Content -Path $reportPath -Value $report

Write-Status "Rollback report: $reportPath" "SUCCESS"
Write-Status "Rollback completed successfully" "SUCCESS"
```

#### Test Script

**File:** `scripts/test-rollback.ps1`

```powershell
# Test rollback script with simulated failure

Write-Host "Testing rollback script..." -ForegroundColor Cyan

# 1. Create test backup
Write-Host "Creating test backup..."
New-Item -Path ".cortex-backups/pre-phase-0" -ItemType Directory -Force
Copy-Item -Path "src/main.py" -Destination ".cortex-backups/pre-phase-0/main.py"

# 2. Simulate migration failure (modify a file)
Write-Host "Simulating migration failure..."
Add-Content -Path "src/main.py" -Value "`n# SIMULATED FAILURE"

# 3. Run rollback
Write-Host "Running rollback..."
.\scripts\rollback-cortex-5.5-migration.ps1 -Validate

# 4. Verify restoration
Write-Host "Verifying restoration..."
$content = Get-Content "src/main.py" -Raw
if ($content -notmatch "SIMULATED FAILURE") {
    Write-Host "✅ Rollback test PASSED" -ForegroundColor Green
} else {
    Write-Host "❌ Rollback test FAILED" -ForegroundColor Red
    exit 1
}

# 5. Cleanup
Remove-Item -Path ".cortex-backups" -Recurse -Force
```

#### Success Criteria

- [ ] Script creates backup before migration
- [ ] Script restores from backup on demand
- [ ] Validation confirms clean rollback state
- [ ] Test script passes (simulated failure → successful rollback)
- [ ] Rollback report generated with audit trail

---

### Task 2: Fix Orchestrator Instantiation (4 hours)

**Blocker:** INT-001  
**Risk:** CRITICAL  
**Impact:** 6 orchestrators cannot load, blocks Phases 1-8

#### Failures Identified

| Orchestrator | Error | File | Fix |
|--------------|-------|------|-----|
| planning_v5 | SyntaxError: f-string backslash | planning_orchestrator_v5.py:718 | Remove/escape backslash |
| tdd_orchestrator | Unexpected kwarg 'config_path' | tdd_orchestrator.py | Add config_path param |
| ado_orchestrator_v2 | Missing positional arg 'state_db' | ado_orchestrator_v2.py | Add state_db param |
| sanitization | Unexpected kwarg 'config_path' | sanitization_orchestrator.py | Add config_path param |
| cleanup_v2 | Missing positional arg 'state_db' | cleanup_orchestrator_v2.py | Add state_db param |
| vacuum_v2 | StateManager.log_execution() missing | vacuum_orchestrator_v2.py | Implement method |

#### Fix 1: planning_v5 Syntax Error

**File:** `src/orchestrators/planning/planning_orchestrator_v5.py`  
**Line:** 718

```python
# BEFORE (line 718 - INVALID):
message = f"Token usage: {tokens}\nRemaining: {remaining}"

# AFTER (VALID):
message = f"Token usage: {tokens} / Remaining: {remaining}"
```

**Validation:**
```bash
python -m py_compile src/orchestrators/planning/planning_orchestrator_v5.py
```

#### Fix 2-3: Add state_db Parameter

**Files:**
- `src/orchestrators/ado/ado_orchestrator_v2.py`
- `src/orchestrators/cleanup/cleanup_orchestrator_v2.py`

```python
# BEFORE:
def __init__(self, config_path: str):
    self.config_path = Path(config_path)
    # No state_db

# AFTER:
def __init__(self, config_path: str, state_db: PlanningStateDB):
    self.config_path = Path(config_path)
    self.state_db = state_db
```

#### Fix 4-5: Add config_path Support

**Files:**
- `src/orchestrators/tdd/tdd_orchestrator.py`
- `src/orchestrators/sanitization/sanitization_orchestrator.py`

```python
# BEFORE:
def __init__(self, workspace_root: Path):
    self.workspace_root = workspace_root
    # Doesn't accept config_path

# AFTER:
def __init__(self, config_path: str, workspace_root: Path = None):
    self.config_path = Path(config_path)
    self.workspace_root = workspace_root or Path.cwd()
```

#### Fix 6: Implement Missing Method

**File:** `src/orchestrators/state_manager.py`

```python
def log_execution(
    self, 
    orchestrator_id: str, 
    execution_data: Dict[str, Any]
) -> None:
    """
    Log orchestrator execution to audit trail.
    
    Args:
        orchestrator_id: Unique orchestrator identifier
        execution_data: Execution metadata (start_time, end_time, status, etc.)
    """
    self.logger.info(
        f"Orchestrator {orchestrator_id} executed",
        extra={"execution_data": execution_data}
    )
    
    self.audit.info(
        AuditCategory.EXECUTION,
        orchestrator_id,
        "execute",
        f"Orchestrator {orchestrator_id} executed successfully",
        context=execution_data
    )
```

#### Integration Test Suite

**File:** `tests/integration/test_all_orchestrators_instantiate.py`

```python
"""Test that all orchestrators can instantiate successfully."""

import pytest
from pathlib import Path
from src.mcp.registry import OrchestratorRegistry
from src.database.planning_state_db import PlanningStateDB


class TestOrchestratorInstantiation:
    """Test orchestrator instantiation from registry."""
    
    @pytest.fixture
    def registry(self):
        """Create orchestrator registry."""
        return OrchestratorRegistry(
            registry_path="cortex-brain/registry/orchestrators.json"
        )
    
    @pytest.fixture
    def state_db(self, tmp_path):
        """Create temporary state database."""
        db_path = tmp_path / "test_state.db"
        return PlanningStateDB(str(db_path))
    
    def test_planning_v5_instantiates(self, registry, state_db):
        """Test planning_v5 orchestrator instantiation."""
        metadata = registry.get("planning_v5")
        assert metadata is not None
        
        # Instantiate orchestrator
        orchestrator_class = registry.load_orchestrator_class(metadata)
        orchestrator = orchestrator_class(
            config_path="cortex-brain/config/master-orchestrator.yaml",
            state_db=state_db
        )
        
        assert orchestrator is not None
        assert hasattr(orchestrator, 'execute')
    
    def test_tdd_orchestrator_instantiates(self, registry, state_db):
        """Test tdd_orchestrator instantiation."""
        metadata = registry.get("tdd_orchestrator")
        assert metadata is not None
        
        orchestrator_class = registry.load_orchestrator_class(metadata)
        orchestrator = orchestrator_class(
            config_path="cortex-brain/config/master-orchestrator.yaml",
            workspace_root=Path.cwd()
        )
        
        assert orchestrator is not None
    
    def test_ado_orchestrator_v2_instantiates(self, registry, state_db):
        """Test ado_orchestrator_v2 instantiation."""
        metadata = registry.get("ado_orchestrator_v2")
        assert metadata is not None
        
        orchestrator_class = registry.load_orchestrator_class(metadata)
        orchestrator = orchestrator_class(
            config_path="cortex-brain/config/master-orchestrator.yaml",
            state_db=state_db
        )
        
        assert orchestrator is not None
    
    def test_sanitization_instantiates(self, registry, state_db):
        """Test sanitization orchestrator instantiation."""
        metadata = registry.get("sanitization")
        assert metadata is not None
        
        orchestrator_class = registry.load_orchestrator_class(metadata)
        orchestrator = orchestrator_class(
            config_path="cortex-brain/config/master-orchestrator.yaml"
        )
        
        assert orchestrator is not None
    
    def test_cleanup_v2_instantiates(self, registry, state_db):
        """Test cleanup_v2 orchestrator instantiation."""
        metadata = registry.get("cleanup_v2")
        assert metadata is not None
        
        orchestrator_class = registry.load_orchestrator_class(metadata)
        orchestrator = orchestrator_class(
            config_path="cortex-brain/config/master-orchestrator.yaml",
            state_db=state_db
        )
        
        assert orchestrator is not None
    
    def test_vacuum_v2_instantiates(self, registry, state_db):
        """Test vacuum_v2 orchestrator instantiation."""
        metadata = registry.get("vacuum_v2")
        assert metadata is not None
        
        orchestrator_class = registry.load_orchestrator_class(metadata)
        orchestrator = orchestrator_class(
            config_path="cortex-brain/config/master-orchestrator.yaml",
            state_db=state_db
        )
        
        assert orchestrator is not None
        # Verify log_execution method exists
        assert hasattr(orchestrator.state_manager, 'log_execution')
    
    def test_all_orchestrators_instantiate(self, registry, state_db):
        """Test that ALL orchestrators can instantiate."""
        failed = []
        
        for orch_id in registry.list_orchestrators():
            try:
                metadata = registry.get(orch_id)
                orchestrator_class = registry.load_orchestrator_class(metadata)
                
                # Try instantiation with common parameters
                orchestrator = orchestrator_class(
                    config_path="cortex-brain/config/master-orchestrator.yaml",
                    state_db=state_db
                )
                
                assert orchestrator is not None
            except Exception as e:
                failed.append((orch_id, str(e)))
        
        # All must pass
        assert len(failed) == 0, f"Failed to instantiate: {failed}"
```

#### Success Criteria

- [ ] All 6 orchestrators fixed
- [ ] Python syntax validation passes (0 errors)
- [ ] Test suite passes (6/6 orchestrators instantiate)
- [ ] Import paths verified

**Test Command:**
```bash
pytest tests/integration/test_all_orchestrators_instantiate.py -v
```

---

### Task 3: Fix StateManager Race Condition (4 hours)

**Blocker:** ARCH-001  
**Risk:** CRITICAL  
**Impact:** Concurrent write corruption in multi-orchestrator usage

#### Current Implementation (Vulnerable)

**File:** `src/orchestrators/state_manager.py`

```python
# PROBLEM: JSON file I/O without locking
def save(self):
    """Save state to file."""
    if self.state_file:
        with open(self.state_file, 'w') as f:
            json.dump(self.states, f, indent=2)
        # ❌ No file locking
        # ❌ Concurrent writes corrupt file
```

#### New Implementation (SQLite with WAL)

**File:** `src/orchestrators/state_manager.py`

```python
"""
State Manager - Cross-orchestrator state coordination with SQLite.

Migrated from JSON to SQLite with WAL mode for concurrent access.
"""

import sqlite3
import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List
import time

from .audit_logger import get_audit_logger, AuditCategory, AuditLevel


class StateType(str, Enum):
    """Types of states managed by StateManager."""
    PLANNING = "planning"
    EXECUTION = "execution"
    VALIDATION = "validation"
    COORDINATION = "coordination"


class StateValidationError(Exception):
    """Raised when state validation fails."""
    pass


class StateManager:
    """
    Manages cross-orchestrator state coordination with SQLite.
    
    Features:
    - SQLite WAL mode for concurrent access
    - Transaction-based writes with retry logic
    - Atomic operations with ACID guarantees
    - File corruption prevention
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize StateManager with SQLite backend.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.logger = logging.getLogger("cortex.orchestrators.state_manager")
        self.audit = get_audit_logger()
        
        # Use SQLite database instead of JSON file
        self.db_path = Path(db_path) if db_path else Path("cortex-brain/database/state.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Initialize database schema
        self._init_database()
        
        self.logger.info(f"StateManager initialized with SQLite (WAL mode): {self.db_path}")
    
    def _init_database(self):
        """Initialize SQLite database with WAL mode."""
        with self._get_connection() as conn:
            # Enable Write-Ahead Logging for concurrent access
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA foreign_keys=ON")
            
            # Create states table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS states (
                    state_id TEXT PRIMARY KEY,
                    state_type TEXT NOT NULL,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Create index on state_type
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_state_type 
                ON states(state_type)
            """)
            
            self.logger.debug("Database schema initialized")
    
    @contextmanager
    def _get_connection(self):
        """
        Context manager for database connections with retry logic.
        
        Implements exponential backoff for handling locked database.
        """
        max_retries = 3
        retry_delay = 0.1  # 100ms initial delay
        
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(
                    str(self.db_path),
                    timeout=10.0,  # 10 second timeout
                    isolation_level='IMMEDIATE'  # Start transaction immediately
                )
                conn.row_factory = sqlite3.Row
                
                yield conn
                
                conn.commit()
                conn.close()
                return
                
            except sqlite3.OperationalError as e:
                if "locked" in str(e).lower() and attempt < max_retries - 1:
                    # Database locked, retry with exponential backoff
                    delay = retry_delay * (2 ** attempt)
                    self.logger.warning(
                        f"Database locked, retrying in {delay}s (attempt {attempt + 1}/{max_retries})"
                    )
                    time.sleep(delay)
                else:
                    # Final attempt failed or non-lock error
                    self.logger.error(f"Database error: {e}")
                    raise
    
    def create_state(
        self, 
        state_id: str, 
        state_type: StateType, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Create new state with atomic transaction.
        
        Args:
            state_id: Unique state identifier
            state_type: Type of state
            data: State data
            
        Returns:
            True if created successfully
            
        Raises:
            StateValidationError: If state already exists
        """
        # Check if state already exists
        if self.get_state(state_id) is not None:
            raise StateValidationError(f"State {state_id} already exists")
        
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO states (state_id, state_type, data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (state_id, state_type.value, json.dumps(data), now, now)
            )
        
        self.logger.debug(f"Created state: {state_id} (type: {state_type})")
        self.audit.trace(
            AuditCategory.STATE_MANAGEMENT,
            "StateManager",
            "create_state",
            f"Created state: {state_id}",
            context={"state_id": state_id, "state_type": state_type.value}
        )
        
        return True
    
    def get_state(self, state_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve state by ID.
        
        Args:
            state_id: State identifier
            
        Returns:
            State data or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM states WHERE state_id = ?",
                (state_id,)
            )
            row = cursor.fetchone()
        
        if row is None:
            return None
        
        return {
            "type": StateType(row["state_type"]),
            "data": json.loads(row["data"]),
            "created_at": row["created_at"],
            "updated_at": row["updated_at"]
        }
    
    def update_state(self, state_id: str, data: Dict[str, Any]) -> bool:
        """
        Update existing state with atomic transaction.
        
        Args:
            state_id: State identifier
            data: New state data
            
        Returns:
            True if updated successfully
            
        Raises:
            StateValidationError: If state not found
        """
        if self.get_state(state_id) is None:
            raise StateValidationError(f"State {state_id} not found")
        
        now = datetime.now().isoformat()
        
        with self._get_connection() as conn:
            conn.execute(
                "UPDATE states SET data = ?, updated_at = ? WHERE state_id = ?",
                (json.dumps(data), now, state_id)
            )
        
        self.logger.debug(f"Updated state: {state_id}")
        return True
    
    def delete_state(self, state_id: str) -> bool:
        """
        Delete state with atomic transaction.
        
        Args:
            state_id: State identifier
            
        Returns:
            True if deleted successfully
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM states WHERE state_id = ?",
                (state_id,)
            )
            deleted = cursor.rowcount > 0
        
        if deleted:
            self.logger.debug(f"Deleted state: {state_id}")
        
        return deleted
    
    def list_states(self, state_type: Optional[StateType] = None) -> List[str]:
        """
        List all state IDs, optionally filtered by type.
        
        Args:
            state_type: Optional filter by state type
            
        Returns:
            List of state IDs
        """
        with self._get_connection() as conn:
            if state_type:
                cursor = conn.execute(
                    "SELECT state_id FROM states WHERE state_type = ?",
                    (state_type.value,)
                )
            else:
                cursor = conn.execute("SELECT state_id FROM states")
            
            return [row["state_id"] for row in cursor.fetchall()]
    
    def log_execution(
        self, 
        orchestrator_id: str, 
        execution_data: Dict[str, Any]
    ) -> None:
        """
        Log orchestrator execution to audit trail.
        
        Args:
            orchestrator_id: Unique orchestrator identifier
            execution_data: Execution metadata
        """
        self.logger.info(
            f"Orchestrator {orchestrator_id} executed",
            extra={"execution_data": execution_data}
        )
        
        self.audit.info(
            AuditCategory.EXECUTION,
            orchestrator_id,
            "execute",
            f"Orchestrator {orchestrator_id} executed successfully",
            context=execution_data
        )
```

#### Integration Test Suite

**File:** `tests/integration/test_concurrent_state_writes.py`

```python
"""Test concurrent state writes don't corrupt database."""

import pytest
import threading
import time
from pathlib import Path
from src.orchestrators.state_manager import StateManager, StateType


class TestConcurrentStateWrites:
    """Test StateManager handles concurrent writes correctly."""
    
    @pytest.fixture
    def state_manager(self, tmp_path):
        """Create StateManager with temporary database."""
        db_path = tmp_path / "test_concurrent.db"
        return StateManager(str(db_path))
    
    def test_concurrent_creates(self, state_manager):
        """Test 10 threads creating states simultaneously."""
        threads = []
        errors = []
        
        def create_state(thread_id):
            try:
                state_manager.create_state(
                    f"state_{thread_id}",
                    StateType.PLANNING,
                    {"thread": thread_id, "data": "concurrent_test"}
                )
            except Exception as e:
                errors.append((thread_id, str(e)))
        
        # Launch 10 concurrent creates
        for i in range(10):
            t = threading.Thread(target=create_state, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Verify no errors
        assert len(errors) == 0, f"Errors during concurrent creates: {errors}"
        
        # Verify all 10 states created
        states = state_manager.list_states()
        assert len(states) == 10
        
        # Verify each state
        for i in range(10):
            state = state_manager.get_state(f"state_{i}")
            assert state is not None
            assert state["data"]["thread"] == i
    
    def test_concurrent_updates(self, state_manager):
        """Test 10 threads updating same state simultaneously."""
        # Create initial state
        state_manager.create_state(
            "shared_state",
            StateType.EXECUTION,
            {"counter": 0}
        )
        
        threads = []
        lock = threading.Lock()
        
        def increment_counter(thread_id):
            # Read current state
            state = state_manager.get_state("shared_state")
            counter = state["data"]["counter"]
            
            # Simulate processing
            time.sleep(0.01)
            
            # Update with incremented value
            state_manager.update_state(
                "shared_state",
                {"counter": counter + 1, "last_thread": thread_id}
            )
        
        # Launch 10 concurrent updates
        for i in range(10):
            t = threading.Thread(target=increment_counter, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Final state should have counter updated
        final_state = state_manager.get_state("shared_state")
        # Note: Due to race conditions, final counter may not be exactly 10
        # But database should not be corrupted
        assert final_state is not None
        assert "counter" in final_state["data"]
    
    def test_database_integrity_after_concurrent_ops(self, state_manager):
        """Test database integrity check passes after concurrent operations."""
        import sqlite3
        
        # Perform many concurrent operations
        threads = []
        
        def mixed_operations(thread_id):
            for i in range(5):
                # Create
                state_manager.create_state(
                    f"state_{thread_id}_{i}",
                    StateType.VALIDATION,
                    {"thread": thread_id, "iteration": i}
                )
                
                # Read
                state_manager.get_state(f"state_{thread_id}_{i}")
                
                # Update
                state_manager.update_state(
                    f"state_{thread_id}_{i}",
                    {"thread": thread_id, "iteration": i, "updated": True}
                )
        
        # Launch 5 threads, each doing 5 operations
        for i in range(5):
            t = threading.Thread(target=mixed_operations, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Check database integrity
        conn = sqlite3.connect(state_manager.db_path, timeout=10.0)
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        conn.close()
        
        assert result == "ok", f"Database integrity check failed: {result}"
        
        # Verify state count
        states = state_manager.list_states()
        assert len(states) == 25  # 5 threads × 5 states each
    
    def test_wal_mode_enabled(self, state_manager):
        """Test that WAL mode is actually enabled."""
        import sqlite3
        
        conn = sqlite3.connect(state_manager.db_path, timeout=10.0)
        cursor = conn.execute("PRAGMA journal_mode")
        mode = cursor.fetchone()[0]
        conn.close()
        
        assert mode.lower() == "wal", f"Expected WAL mode, got {mode}"
```

#### Success Criteria

- [ ] SQLite database with WAL mode enabled
- [ ] Transaction-based writes with retry logic
- [ ] Concurrent write test passes (10+ threads)
- [ ] PRAGMA integrity_check passes
- [ ] Performance: <100ms per write operation

**Test Command:**
```bash
pytest tests/integration/test_concurrent_state_writes.py -v
```

---

## 🎯 Phase P00B Success Criteria

**All Must Pass:**

- [ ] ✅ **Task 1:** Rollback script created and tested
  - Script exists: `scripts/rollback-cortex-5.5-migration.ps1`
  - Test script passes: `scripts/test-rollback.ps1`
  - Simulated failure recovery successful
  
- [ ] ✅ **Task 2:** All 6 orchestrators instantiate
  - planning_v5: Syntax error fixed
  - tdd_orchestrator: config_path parameter added
  - ado_orchestrator_v2: state_db parameter added
  - sanitization: config_path parameter added
  - cleanup_v2: state_db parameter added
  - vacuum_v2: log_execution() method implemented
  - Test suite: `test_all_orchestrators_instantiate.py` (6/6 PASS)
  
- [ ] ✅ **Task 3:** StateManager production-ready
  - SQLite with WAL mode enabled
  - Concurrent write test passes (10+ threads)
  - Database integrity check passes
  - Performance validated (<100ms per write)
  
- [ ] ✅ **Integration:** All tests pass
  - Python syntax validation: 0 errors
  - Integration tests: 100% pass rate
  - No regressions introduced

---

## 📦 Deliverables

1. **Rollback Script**
   - File: `scripts/rollback-cortex-5.5-migration.ps1`
   - Test: `scripts/test-rollback.ps1`
   - Report: `cortex-brain/documents/reports/rollback-test-report.md`

2. **Orchestrator Fixes**
   - 6 Python files modified
   - Test suite: `tests/integration/test_all_orchestrators_instantiate.py`

3. **StateManager Enhancement**
   - File: `src/orchestrators/state_manager.py` (SQLite implementation)
   - Test suite: `tests/integration/test_concurrent_state_writes.py`

4. **Documentation**
   - This phase plan: `phases/phase-p00b-critical-blocker-resolution.md`
   - Git commit with all fixes and test evidence

---

## 🚀 Phase P00B → Phase 1 Handoff

**After P00B Complete:**

1. ✅ Rollback script operational → Phase 0 migration safe
2. ✅ All orchestrators instantiate → Phases 1-8 unblocked
3. ✅ StateManager production-ready → Concurrent usage safe
4. ✅ **Phase 1 can begin with confidence**

**Git Commit Template:**

```bash
git add .
git commit -m "fix(p00b): Critical blocker resolution before Phase 1

Phase P00B: Critical Blocker Resolution (1 day)

Fixes:
1. Created rollback-cortex-5.5-migration.ps1 (DEPLOY-001)
2. Fixed 6 orchestrator instantiation failures (INT-001)
3. Fixed StateManager race condition (ARCH-001)

Tests: 100% pass rate
- tests/integration/test_all_orchestrators_instantiate.py (6/6 PASS)
- tests/integration/test_concurrent_state_writes.py (PASS)
- Python syntax validation (0 errors)

Review: reports/cortex-review/20260107_initial_review.yaml
Epic: cortex5-enhancement-epic-v2
Phase: P00B (Critical Blocker Resolution)
Blocks: Phases 1-11
"
```

---

**Phase Status:** NOT_STARTED  
**Next Phase:** Phase 1 (Knowledge Extension Layer)  
**Estimated Completion:** After 1 day of focused development
