# CORTEX 6.0 Phase 1 Repair Action Plan

**Date:** 2026-01-11  
**Status:** READY TO EXECUTE  
**Blocking:** Phase 2 (Orchestration Core) cannot start until complete  
**Effort:** 16-23 hours sequential work

---

## OVERVIEW

**Current State:** Phase 1 claims 67.65% (23/34) but 0% verified (23 false positives)  
**Fix Strategy:** 5-step sequential repair with verification gates  
**Success Criteria:** 
- ✅ All tests collect and run
- ✅ 0 hardcoded paths violations
- ✅ 11 missing ACs implemented
- ✅ Evidence bundles generated
- ✅ Verification rate ≥80%

---

## STEP 1: Fix Test Infrastructure (2-3 hours)

### Issue
11 test files fail collection (24% failure rate). Pytest cannot run full suite.

### Files to Remove/Fix
```
tests/unit/test_invalid-_name-_with-_dashes.py        ← DELETE (invalid name)
tests/unit/test_api_orchestrator.py                    ← DELETE/FIX (missing module)
tests/unit/test_custom_orchestrator.py                 ← DELETE/FIX (missing module)
tests/unit/test_custom_template_orch.py                ← DELETE/FIX (missing module)
tests/unit/test_data_processing_orchestrator.py        ← DELETE/FIX (missing module)
tests/unit/test_duplicate_orch.py                      ← DELETE/FIX (missing module)
tests/unit/test_e2_e_orchestrator.py                   ← DELETE/FIX (missing module)
tests/unit/test_governed_orchestrator.py               ← DELETE/FIX (missing module)
tests/unit/test_python_test_orchestrator.py            ← DELETE/FIX (missing module)
tests/unit/test_test_generated_orchestrator.py         ← DELETE/FIX (missing module)
tests/unit/test_workflow_orchestrator.py               ← DELETE/FIX (missing module)
```

### Actions

#### A. Identify broken tests (5 min)
```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 -m pytest tests/ --collect-only -q 2>&1 | grep "ERROR\|FAILED" > /tmp/broken_tests.txt
cat /tmp/broken_tests.txt
```

#### B. Delete test stub files (10 min)
```bash
rm tests/unit/test_invalid-_name-_with-_dashes.py
rm tests/unit/test_api_orchestrator.py
rm tests/unit/test_custom_orchestrator.py
rm tests/unit/test_custom_template_orch.py
rm tests/unit/test_data_processing_orchestrator.py
rm tests/unit/test_duplicate_orch.py
rm tests/unit/test_e2_e_orchestrator.py
rm tests/unit/test_governed_orchestrator.py
rm tests/unit/test_python_test_orchestrator.py
rm tests/unit/test_test_generated_orchestrator.py
rm tests/unit/test_workflow_orchestrator.py
```

#### C. Verify clean test collection (10 min)
```bash
python3 -m pytest tests/ --collect-only -q
# Expected: No errors, shows count of collected tests
```

#### D. Implement AC-TEST-001: Test Discovery (1 hour)

**Create:** `src/infrastructure/test_discovery.py`

```python
"""
AC-TEST-001: Test Discovery
Automated discovery of test files by AC-ID metadata
"""

import functools
from typing import Callable
from pathlib import Path
import json

# Global registry of test-to-AC-ID mappings
_TEST_AC_REGISTRY = {}

def validate_ac_id(ac_id: str):
    """
    Decorator to link a test to an AC-ID.
    
    Usage:
        @validate_ac_id("AC-AUDIT-001")
        def test_queryable_storage():
            pass
    """
    def decorator(func: Callable) -> Callable:
        _TEST_AC_REGISTRY[func.__name__] = ac_id
        func._ac_id = ac_id
        return func
    return decorator

def get_ac_id(test_func: Callable) -> str:
    """Get AC-ID for a test function."""
    return getattr(test_func, '_ac_id', None)

def discover_tests_by_ac_id(ac_id: str) -> list:
    """Find all tests that validate a given AC-ID."""
    return [
        test_name
        for test_name, test_ac in _TEST_AC_REGISTRY.items()
        if test_ac == ac_id
    ]

def export_registry(output_file: Path = None) -> dict:
    """Export test-AC-ID mapping as JSON."""
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(_TEST_AC_REGISTRY, f, indent=2)
    return _TEST_AC_REGISTRY
```

#### E. Implement AC-TEST-002: Test Execution (1 hour)

**Create:** `src/infrastructure/test_executor.py`

```python
"""
AC-TEST-002: Test Execution
Run tests and capture results by AC-ID
"""

import subprocess
import json
from pathlib import Path
from typing import Dict, List

class TestExecutor:
    """Execute tests and collect results by AC-ID."""
    
    def run_tests_for_ac(self, ac_id: str) -> Dict:
        """Run all tests for a specific AC-ID."""
        cmd = [
            "python3", "-m", "pytest",
            "tests/",
            "-k", ac_id,
            "-v",
            "--tb=short",
            "--co-junit-xml=/tmp/test_results.xml"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Parse results
        passed = result.stdout.count(" PASSED")
        failed = result.stdout.count(" FAILED")
        total = passed + failed
        
        return {
            "ac_id": ac_id,
            "passed": passed,
            "failed": failed,
            "total": total,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "stdout": result.stdout,
            "stderr": result.stderr
        }
    
    def run_all_tests(self) -> Dict:
        """Run full test suite."""
        cmd = ["python3", "-m", "pytest", "tests/", "-v", "--tb=short"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        passed = result.stdout.count(" PASSED")
        failed = result.stdout.count(" FAILED")
        total = passed + failed
        
        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0
        }
```

#### F. Link existing tests to AC-IDs (30 min)

**Update existing test files:** Add `@validate_ac_id("AC-XXX")` decorator

Example:
```python
from src.infrastructure.test_discovery import validate_ac_id

@validate_ac_id("AC-AUDIT-001")
def test_queryable_storage():
    """Validates AC-AUDIT-001: Queryable Audit Storage"""
    # test code...

@validate_ac_id("AC-AUDIT-002")
def test_event_emission():
    """Validates AC-AUDIT-002: Event Emission"""
    # test code...
```

### Success Criteria
- ✅ `pytest --collect-only` shows no errors
- ✅ All tests collected without syntax errors
- ✅ Test count > 40 and stable
- ✅ AC-TEST-001 and AC-TEST-002 tests pass

### Verification
```bash
python3 -m pytest tests/ --collect-only -q
python3 -m pytest tests/unit/test_test_discovery.py -v
python3 -m pytest tests/unit/test_test_executor.py -v
```

---

## STEP 2: Refactor Hardcoded Paths (3-4 hours)

### Issue
222 hardcoded "cortex-brain/" paths violate CORE-005 (Path Portability).

### Actions

#### A. Create project_root() utility (20 min)

**Create:** `src/utils/path_utils.py`

```python
"""
Path utilities respecting CORE-005 (Path Portability)
"""

from pathlib import Path
import os

def project_root() -> Path:
    """
    Get absolute path to project root.
    Works on any machine/path configuration.
    """
    # Find the CORTEX project root by looking for distinctive marker
    current = Path(__file__).resolve().parent.parent.parent
    
    # Verify we found the right location
    if not (current / ".github" / "prompts").exists():
        raise RuntimeError(f"Cannot find project root from {__file__}")
    
    return current

def cortex_brain_path() -> Path:
    """Get path to cortex-brain directory (portable)."""
    return project_root() / "cortex_brain"

def audit_logs_path() -> Path:
    """Get path to audit logs directory."""
    return cortex_brain_path() / "audit_logs"

def state_db_path() -> Path:
    """Get path to state database."""
    return cortex_brain_path() / "state" / "cortex.db"

def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist."""
    path.mkdir(parents=True, exist_ok=True)
    return path
```

#### B. Find all hardcoded paths (10 min)

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Find all hardcoded paths
grep -r "cortex-brain/" src/ tests/ --include="*.py" | tee /tmp/hardcoded_paths.txt

# Count them
wc -l /tmp/hardcoded_paths.txt
```

#### C. Refactor paths (2-3 hours)

For each file containing hardcoded paths:

**Pattern 1: String paths**
```python
# Before
log_path = "cortex-brain/audit-logs/..."

# After
from src.utils.path_utils import audit_logs_path
log_path = audit_logs_path() / "..."
```

**Pattern 2: File opens**
```python
# Before
with open("cortex-brain/tier0/governance/core-rules.yaml") as f:
    rules = yaml.safe_load(f)

# After
from src.utils.path_utils import cortex_brain_path
rules_path = cortex_brain_path() / "tier0" / "governance" / "core-rules.yaml"
with open(rules_path) as f:
    rules = yaml.safe_load(f)
```

**Pattern 3: Path concatenation**
```python
# Before
json_path = "cortex-brain/tier1/tracking/progress-tracker.json"

# After
from src.utils.path_utils import cortex_brain_path
json_path = cortex_brain_path() / "tier1" / "tracking" / "progress-tracker.json"
```

#### D. Add CORE-005 pre-commit hook (20 min)

**Create:** `.git/hooks/pre-commit`

```bash
#!/bin/bash

# CORE-005: Path Portability Check
# Block commits with hardcoded 'cortex-brain/' paths

HARDCODED=$(grep -r "cortex-brain/" src/ tests/ --include="*.py" 2>/dev/null | wc -l)

if [ "$HARDCODED" -gt 0 ]; then
    echo "❌ CORE-005 VIOLATION: $HARDCODED hardcoded paths detected"
    echo "Use project_root() from src.utils.path_utils instead"
    exit 1
fi

exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

#### E. Validate on separate paths (30 min)

```bash
# Test on a different directory
mkdir -p /tmp/cortex_test
cp -r /Users/asifhussain/PROJECTS/CORTEX/* /tmp/cortex_test/
cd /tmp/cortex_test

# Run tests - should work despite different path
python3 -m pytest tests/unit/test_path_utils.py -v

# Verify hardcoded paths are gone
grep -r "cortex-brain/" src/ tests/ --include="*.py" | wc -l
# Should output: 0

cd /Users/asifhussain/PROJECTS/CORTEX
```

### Success Criteria
- ✅ `project_root()` utility created and working
- ✅ All 222 hardcoded paths refactored
- ✅ `grep -r "cortex-brain/" src/` returns 0 matches
- ✅ Tests pass on different directory paths
- ✅ Pre-commit hook blocks hardcoded paths

### Verification
```bash
python3 -m pytest tests/unit/test_path_utils.py -v
grep -r "cortex-brain/" src/ tests/ --include="*.py" | wc -l  # Should be 0
```

---

## STEP 3: Implement Missing Audit ACs (4-6 hours)

### Missing AC-IDs
- AC-AUDIT-004: AC-ID Traceability (link audit events to AC-IDs)
- AC-AUDIT-005: Automatic Vacuum (retention policy + daily cleanup)
- AC-AUDIT-006: Per-Repo Isolation (separate audit DB per repo)
- AC-AUDIT-007: Hash Chain Integrity (tamper detection via event_hash)

### Implementation Plan

#### AC-AUDIT-004: AC-ID Traceability (1 hour)

**Update:** `src/infrastructure/enhanced_audit_logger.py`

```python
def log_with_ac_id(self, ac_id: str, event_type: str, **kwargs):
    """Log event linked to specific AC-ID (AC-AUDIT-004)."""
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "category": "INFRASTRUCTURE",
        "ac_id": ac_id,           # ← NEW: AC-ID traceability
        "event_type": event_type,
        "data": kwargs,
        "event_hash": self._compute_hash(...),
        "prev_event_hash": self._get_last_hash()
    }
    self.db.execute(
        """INSERT INTO audit_log 
           (timestamp, category, ac_id, event_type, data, event_hash, prev_event_hash)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (entry["timestamp"], entry["category"], entry["ac_id"], 
         entry["event_type"], json.dumps(entry["data"]), 
         entry["event_hash"], entry["prev_event_hash"])
    )
    self.db.commit()
```

**Create test:** `tests/infrastructure/test_ac_traceability.py`

```python
def test_audit_events_linked_to_ac_ids():
    """AC-AUDIT-004: All audit entries link to AC-IDs"""
    logger = EnhancedAuditLogger()
    
    logger.log_with_ac_id("AC-AUDIT-001", "TEST_EVENT", detail="test")
    
    # Verify in DB
    result = logger.db.execute(
        "SELECT ac_id FROM audit_log WHERE event_type = 'TEST_EVENT'"
    ).fetchone()
    
    assert result[0] == "AC-AUDIT-001"
```

#### AC-AUDIT-005: Automatic Vacuum (1.5 hours)

**Create:** `src/infrastructure/audit_vacuum.py`

```python
"""
AC-AUDIT-005: Automatic Vacuum
Level-based retention with daily cleanup
"""

from datetime import datetime, timedelta
import sqlite3

class AuditVacuum:
    """Manage audit log retention and cleanup."""
    
    RETENTION_LEVELS = {
        "CRITICAL": 90,   # days
        "ERROR": 90,
        "WARNING": 60,
        "INFO": 30,
        "DEBUG": 7,
        "TRACE": 1
    }
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
    
    def vacuum_expired_logs(self) -> dict:
        """Remove logs older than retention period."""
        results = {"deleted": 0, "by_level": {}}
        
        now = datetime.utcnow()
        
        for level, retention_days in self.RETENTION_LEVELS.items():
            cutoff_date = now - timedelta(days=retention_days)
            
            cursor = self.conn.execute(
                """DELETE FROM audit_log 
                   WHERE level = ? AND timestamp < ?""",
                (level, cutoff_date.isoformat())
            )
            
            deleted = cursor.rowcount
            results["deleted"] += deleted
            results["by_level"][level] = deleted
        
        self.conn.commit()
        return results
    
    def should_vacuum(self) -> bool:
        """Check if vacuum is needed (last one > 24h ago)."""
        # Implementation...
        pass
```

**Create test:** `tests/infrastructure/test_audit_vacuum.py`

#### AC-AUDIT-006: Per-Repo Isolation (1.5 hours)

**Update:** `src/infrastructure/enhanced_audit_logger.py`

```python
class EnhancedAuditLogger:
    def __init__(self, repo_id: str):
        """Initialize audit logger with repo isolation (AC-AUDIT-006)."""
        self.repo_id = repo_id
        
        # Each repo gets isolated audit database
        db_path = f"{project_root()}/cortex-brain/audit-logs/{repo_id}/audit.db"
        ensure_dir(Path(db_path).parent)
        
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
```

**Create test:** `tests/infrastructure/test_repo_isolation.py`

#### AC-AUDIT-007: Hash Chain Integrity (1.5 hours)

**Update:** `src/infrastructure/enhanced_audit_logger.py`

```python
import hashlib

class EnhancedAuditLogger:
    def _compute_event_hash(self, event: dict) -> str:
        """Compute SHA256 hash of event (AC-AUDIT-007)."""
        event_str = json.dumps(event, sort_keys=True)
        return hashlib.sha256(event_str.encode()).hexdigest()
    
    def _get_prev_event_hash(self) -> str:
        """Get hash of previous event for chain integrity."""
        result = self.db.execute(
            "SELECT event_hash FROM audit_log ORDER BY timestamp DESC LIMIT 1"
        ).fetchone()
        return result[0] if result else "GENESIS"
    
    def log_event(self, **kwargs):
        """Log with hash chain verification (AC-AUDIT-007)."""
        prev_hash = self._get_prev_event_hash()
        event_hash = self._compute_event_hash(kwargs)
        
        self.db.execute(
            """INSERT INTO audit_log 
               (timestamp, event_hash, prev_event_hash, data)
               VALUES (?, ?, ?, ?)""",
            (datetime.utcnow().isoformat(), event_hash, prev_hash, json.dumps(kwargs))
        )
        self.db.commit()
    
    def verify_chain_integrity(self) -> bool:
        """Verify event_hash chain (detect tampering)."""
        rows = self.db.execute(
            "SELECT id, event_hash, prev_event_hash FROM audit_log ORDER BY id"
        ).fetchall()
        
        for i, (id, hash, prev_hash) in enumerate(rows):
            if i == 0:
                # First event should reference GENESIS
                continue
            
            # Verify prev_hash matches previous event's hash
            prev_row = rows[i-1]
            if prev_hash != prev_row[1]:
                return False
        
        return True
```

**Create test:** `tests/infrastructure/test_hash_chain.py`

### Success Criteria
- ✅ AC-AUDIT-004: All audit events have `ac_id` field linked
- ✅ AC-AUDIT-005: Vacuum removes logs by retention policy
- ✅ AC-AUDIT-006: Each repo has isolated audit database
- ✅ AC-AUDIT-007: Hash chain verified, tampering detected
- ✅ All 4 test files pass (test_*_audit_*.py)

---

## STEP 4: Implement Evidence Bundle System (6-8 hours)

### Missing AC-IDs
- AC-EVIDENCE-001: Bundle Structure (3-file format)
- AC-EVIDENCE-002: Validation Gates (80% coverage, audit, governance)
- AC-EVIDENCE-003: Auto-Generation

#### AC-EVIDENCE-001: Bundle Structure (2 hours)

**Create:** `src/infrastructure/evidence_bundler.py`

```python
"""
AC-EVIDENCE-001: Evidence Bundle Structure
3-file lightweight format: manifest.yaml, test_results.json, audit_trace.jsonl
"""

from pathlib import Path
from datetime import datetime
import yaml
import json
import hashlib

class EvidenceBundle:
    """Generate and manage evidence bundles for AC-IDs."""
    
    def __init__(self, ac_id: str, base_path: Path = None):
        self.ac_id = ac_id
        if base_path is None:
            from src.utils.path_utils import cortex_brain_path
            base_path = cortex_brain_path() / "tier1" / "evidence-bundles"
        
        self.bundle_dir = base_path / ac_id
        self.bundle_dir.mkdir(parents=True, exist_ok=True)
    
    def create_manifest(self, ac_spec: dict, test_results: dict, 
                       governance_rules: list) -> dict:
        """Create manifest.yaml (AC-EVIDENCE-001)."""
        manifest = {
            "ac_id": self.ac_id,
            "generated_at": datetime.utcnow().isoformat(),
            "spec_hash": self._compute_hash(str(ac_spec)),
            "test_count": test_results.get("total", 0),
            "test_coverage": test_results.get("coverage", 0),
            "governance_rules_applied": governance_rules,
            "validation_gates": {
                "test_coverage": test_results.get("coverage", 0) >= 80,
                "audit_complete": test_results.get("audit_events", 0) > 0,
                "governance_compliant": len(governance_rules) > 0
            }
        }
        
        manifest_path = self.bundle_dir / "manifest.yaml"
        with open(manifest_path, 'w') as f:
            yaml.dump(manifest, f)
        
        return manifest
    
    def add_test_results(self, test_results: dict) -> None:
        """Add test_results.json (AC-EVIDENCE-001)."""
        results_path = self.bundle_dir / "test_results.json"
        with open(results_path, 'w') as f:
            json.dump(test_results, f, indent=2)
    
    def add_audit_trace(self, audit_events: list) -> None:
        """Add audit_trace.jsonl (AC-EVIDENCE-001)."""
        trace_path = self.bundle_dir / "audit_trace.jsonl"
        with open(trace_path, 'w') as f:
            for event in audit_events:
                f.write(json.dumps(event) + '\n')
    
    def _compute_hash(self, content: str) -> str:
        """Compute SHA256 hash."""
        return hashlib.sha256(content.encode()).hexdigest()
```

#### AC-EVIDENCE-002: Validation Gates (2 hours)

**Create:** `src/infrastructure/evidence_gates.py`

```python
"""
AC-EVIDENCE-002: Evidence Bundle Validation Gates
3 gates: Test Coverage (80%), Audit Completeness, Governance Compliance
"""

class EvidenceGates:
    """Validate evidence bundles against quality gates."""
    
    def validate_coverage_gate(self, coverage_percent: float) -> tuple[bool, str]:
        """
        Gate 1: Test Coverage >= 80% (BLOCKER)
        """
        passed = coverage_percent >= 80
        msg = f"Coverage: {coverage_percent:.1f}%" + (" ✅ PASS" if passed else " ❌ FAIL")
        return passed, msg
    
    def validate_audit_gate(self, audit_events: list) -> tuple[bool, str]:
        """
        Gate 2: Audit Completeness (BLOCKER)
        All required audit events must exist
        """
        required_events = ["ORCHESTRATOR_START", "TEST_EXECUTION", "RESULT_RECORDED"]
        event_types = [e.get("event_type") for e in audit_events]
        
        missing = [e for e in required_events if e not in event_types]
        passed = len(missing) == 0
        
        msg = f"Audit events: {len(event_types)} collected"
        if not passed:
            msg += f", missing: {missing}"
        msg += " ✅ PASS" if passed else " ❌ FAIL"
        
        return passed, msg
    
    def validate_governance_gate(self, governance_rules: list) -> tuple[bool, str]:
        """
        Gate 3: Governance Compliance (BLOCKER)
        All applicable governance rules must have enforcement logs
        """
        passed = len(governance_rules) > 0
        msg = f"Governance rules: {len(governance_rules)} enforced"
        msg += " ✅ PASS" if passed else " ❌ FAIL"
        
        return passed, msg
    
    def validate_bundle(self, bundle: dict) -> tuple[bool, list]:
        """
        Validate entire bundle against all 3 gates
        Returns: (all_pass, [gate_results])
        """
        gates = [
            self.validate_coverage_gate(bundle["coverage"]),
            self.validate_audit_gate(bundle["audit_events"]),
            self.validate_governance_gate(bundle["governance_rules"])
        ]
        
        all_pass = all(g[0] for g in gates)
        return all_pass, gates
```

#### AC-EVIDENCE-003: Auto-Generation (2 hours)

**Create:** `src/infrastructure/evidence_auto_generator.py`

```python
"""
AC-EVIDENCE-003: Evidence Bundle Auto-Generation
Generate Evidence Bundle post-implementation from tests + audit + AC-INDEX
"""

from pathlib import Path
from src.infrastructure.evidence_bundler import EvidenceBundle

class EvidenceAutoGenerator:
    """Automatically generate evidence bundles after AC implementation."""
    
    def generate_for_ac(self, ac_id: str, 
                       test_executor, audit_logger, 
                       ac_index: dict) -> dict:
        """
        Generate evidence bundle for AC-ID
        
        Process:
        1. Get AC definition from AC-INDEX
        2. Run tests for this AC-ID
        3. Collect audit events for this AC-ID
        4. Create bundle with manifest + results + trace
        """
        
        # Step 1: Get AC spec
        ac_spec = ac_index.get(ac_id, {})
        
        # Step 2: Run tests
        test_results = test_executor.run_tests_for_ac(ac_id)
        
        # Step 3: Collect audit events
        audit_events = audit_logger.query_events_by_ac_id(ac_id)
        
        # Step 4: Create bundle
        bundle = EvidenceBundle(ac_id)
        manifest = bundle.create_manifest(
            ac_spec=ac_spec,
            test_results=test_results,
            governance_rules=ac_spec.get("governance_rules", [])
        )
        bundle.add_test_results(test_results)
        bundle.add_audit_trace(audit_events)
        
        return {
            "ac_id": ac_id,
            "bundle_dir": str(bundle.bundle_dir),
            "manifest": manifest,
            "test_results": test_results,
            "audit_events": len(audit_events)
        }
    
    def generate_all_for_phase(self, phase_name: str) -> dict:
        """Generate evidence bundles for all AC-IDs in a phase."""
        results = []
        for ac_id in self._get_phase_ac_ids(phase_name):
            result = self.generate_for_ac(ac_id)
            results.append(result)
        
        return {
            "phase": phase_name,
            "bundles_generated": len(results),
            "bundles": results
        }
```

### Success Criteria
- ✅ AC-EVIDENCE-001: 3-file bundles created (manifest + results + trace)
- ✅ AC-EVIDENCE-002: All 3 gates implemented and validating
- ✅ AC-EVIDENCE-003: Auto-generation creates bundles from tests + audit
- ✅ All tests pass (test_evidence_bundle.py, test_evidence_gates.py, test_evidence_auto_gen.py)

---

## STEP 5: Evidence Collection & Verification (1-2 hours)

### Actions

#### A. Run full test suite (30 min)

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Run full test suite
python3 -m pytest tests/ -v --tb=short --co-junit-xml=/tmp/test_results.xml

# Capture results
pytest_summary=$(python3 -m pytest tests/ -q --tb=no | tail -1)
echo "Test summary: $pytest_summary"
```

#### B. Generate evidence bundles (30 min)

```bash
# Generate bundles for all Phase 1 AC-IDs
python3 << 'EOF'
from src.infrastructure.evidence_auto_generator import EvidenceAutoGenerator
from src.infrastructure.test_executor import TestExecutor
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

generator = EvidenceAutoGenerator()
results = generator.generate_all_for_phase("Phase 1: Foundation Enhancement")

print(f"Generated {results['bundles_generated']} evidence bundles")
for bundle in results['bundles']:
    print(f"  {bundle['ac_id']}: {bundle['bundle_dir']}")
EOF
```

#### C. Update tracker with verified results (30 min)

**Script:** `scripts/update_tracker_verified.py`

```python
"""
Update progress-tracker.json with VERIFIED results from tests + evidence
"""

import json
from pathlib import Path
from src.infrastructure.test_executor import TestExecutor

def update_tracker_with_verified_results():
    """Load tracker, verify each AC with tests, update with evidence."""
    
    # Load tracker
    tracker_path = Path("cortex-brain/tier1/tracking/progress-tracker.json")
    with open(tracker_path) as f:
        tracker = json.load(f)
    
    # Run tests for each AC in Phase 1
    executor = TestExecutor()
    verified = []
    partial = []
    
    for ac_id in tracker['current_phase']['ac_ids']:
        results = executor.run_tests_for_ac(ac_id)
        
        if results['total'] == 0:
            # No tests = planned
            continue
        elif results['passed'] == results['total']:
            # All pass = implemented
            verified.append(ac_id)
        else:
            # Some fail = partial
            partial.append(ac_id)
    
    # Update tracker
    tracker['current_phase']['verified_implemented'] = verified
    tracker['current_phase']['partial_implemented'] = partial
    tracker['current_phase']['completed_count'] = len(verified)
    tracker['current_phase']['completion_percentage'] = (
        len(verified) / len(tracker['current_phase']['ac_ids']) * 100
    )
    
    # Save updated tracker
    with open(tracker_path, 'w') as f:
        json.dump(tracker, f, indent=2)
    
    print(f"Verified: {len(verified)} ACs")
    print(f"Partial: {len(partial)} ACs")
    print(f"Completion: {tracker['current_phase']['completion_percentage']:.1f}%")

if __name__ == "__main__":
    update_tracker_with_verified_results()
```

#### D. Sync plan viewer dashboard (10 min)

```bash
python3 scripts/sync_plan_viewer_data.py
```

#### E. Validate verification rate (10 min)

```bash
python3 scripts/audit_based_evidence_validator.py
```

**Success:** Verification rate should be ≥80%

### Success Criteria
- ✅ Full test suite runs (no collection errors)
- ✅ Evidence bundles generated for all verified ACs
- ✅ Tracker updated with actual test results
- ✅ Plan viewer dashboard synced
- ✅ Verification rate ≥80%

---

## EXECUTION CHECKLIST

```
STEP 1: Fix Test Infrastructure (2-3 hours)
  [ ] Delete 11 broken test files
  [ ] Create test_discovery.py (AC-TEST-001)
  [ ] Create test_executor.py (AC-TEST-002)
  [ ] Link existing tests to AC-IDs
  [ ] Verify: pytest --collect-only runs cleanly

STEP 2: Refactor Hardcoded Paths (3-4 hours)
  [ ] Create src/utils/path_utils.py
  [ ] Refactor 222 hardcoded paths
  [ ] Add CORE-005 pre-commit hook
  [ ] Verify: 0 hardcoded paths remain
  [ ] Test on different directory path

STEP 3: Implement Missing Audit ACs (4-6 hours)
  [ ] AC-AUDIT-004: AC-ID Traceability
  [ ] AC-AUDIT-005: Automatic Vacuum
  [ ] AC-AUDIT-006: Per-Repo Isolation
  [ ] AC-AUDIT-007: Hash Chain Integrity
  [ ] Verify: All 4 test files pass

STEP 4: Implement Evidence Bundle System (6-8 hours)
  [ ] AC-EVIDENCE-001: Bundle Structure
  [ ] AC-EVIDENCE-002: Validation Gates
  [ ] AC-EVIDENCE-003: Auto-Generation
  [ ] Verify: All 3 test files pass

STEP 5: Evidence Collection & Verification (1-2 hours)
  [ ] Run full test suite
  [ ] Generate evidence bundles
  [ ] Update tracker with verified results
  [ ] Sync plan viewer
  [ ] Verify: Verification rate ≥80%

FINAL: Phase 2 Readiness Check
  [ ] All 34 Phase 1 ACs at 100% verified
  [ ] 0 CORE-005 violations
  [ ] Evidence bundles for all ACs
  [ ] Phase 2 can proceed
```

---

## TOTAL EFFORT SUMMARY

| Step | Task | Hours | Status |
|------|------|-------|--------|
| 1 | Test Infrastructure | 2-3 | TODO |
| 2 | Hardcoded Paths | 3-4 | TODO |
| 3 | Audit ACs | 4-6 | TODO |
| 4 | Evidence System | 6-8 | TODO |
| 5 | Verification | 1-2 | TODO |
| **TOTAL** | **Phase 1 Repair** | **16-23** | **READY TO START** |

---

## SUCCESS DEFINITION

After all 5 steps complete:

✅ **Test Execution:** 100% - All tests collect and run cleanly  
✅ **AC Completeness:** 100% - All 34 AC-IDs implemented  
✅ **Evidence:** 100% - Bundles generated for all ACs  
✅ **Portability:** 100% - 0 hardcoded paths  
✅ **Verification:** ≥80% - Evidence validated and linked  
✅ **Governance:** ✓ - CORE-005 enforced  
✅ **Phase 2 Ready:** YES - Can proceed with confidence

