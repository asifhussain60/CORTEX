# PHASE-17 IMPLEMENTATION: OPTIMIZED AUDIT-FIRST TEST EXECUTION

## Comprehensive Developer Guide for Test Validation via Audit Trace Logs

**Target Audience**: Development Team (Implementation, QA, DevOps)  
**Date**: 2026-01-16  
**Scope**: How to execute PHASE-17 tests with complete audit trail validation  

---

## 📖 TABLE OF CONTENTS

1. [Quick Start](#quick-start)
2. [Test Execution Framework](#test-execution-framework)
3. [Audit Trail Integration Patterns](#audit-trail-integration-patterns)
4. [Weekly Checkpoint Procedure](#weekly-checkpoint-procedure)
5. [Monitoring & Troubleshooting](#monitoring--troubleshooting)
6. [Performance Optimization Tips](#performance-optimization-tips)
7. [Rollback Procedures](#rollback-procedures)

---

## 🚀 QUICK START

### Prerequisites

```bash
# 1. Install dependencies
pip install pytest pytest-cov pytest-xdist sqlite3 PyYAML

# 2. Initialize audit database
python init_db.py --audit-schema-only

# 3. Verify schema
sqlite3 cortex_brain/state/governance.db ".schema audit_entries"
```

### First Test with Audit Logging

```bash
# 1. Run single AC with audit trace
pytest tests/unit/governance/test_phase_17_ac_db_001_01.py -v \
  --audit-trace \
  --audit-log cortex_brain/state/governance.db

# Expected output:
# test_query_existing_domain PASSED
# [AUDIT] AC-DB-001-01: AC_START (entry_1044)
# [AUDIT] AC-DB-001-01: AC_EXECUTE (hash_valid=true)
# [AUDIT] AC-DB-001-01: AC_COMPLETE (result=PASS)
```

### Run All PHASE-17 Tests

```bash
# Sequential execution (preserves audit chain ordering)
pytest tests/unit/governance/test_phase_17_*.py \
  --audit-trace \
  --audit-log cortex_brain/state/governance.db \
  --collect-only | grep "test_" | wc -l
# Expected: 338+ tests

# Parallel execution (by AC, with audit coordination)
pytest tests/unit/governance/test_phase_17_*.py \
  --audit-trace \
  --audit-log cortex_brain/state/governance.db \
  -n auto \  # Use all CPU cores
  --dist loadgroup  # Group by AC to maintain audit ordering
```

---

## 🔧 TEST EXECUTION FRAMEWORK

### Audit Logger Class (Core Infrastructure)

```python
# src/governance/audit_logger.py

from datetime import datetime
from hashlib import sha256
import sqlite3
import json
from pathlib import Path

class AuditLogger:
    """
    Central audit logging for PHASE-17 tests.
    Implements CORE-027: AC_START → AC_EXECUTE → AC_COMPLETE with hash chain.
    """
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.previous_hash = self._get_last_hash()
    
    def start_ac_test(self, ac_id: str, test_name: str, component: str) -> str:
        """
        Begin AC test. Returns audit_id for tracking through execution.
        
        Args:
            ac_id: e.g., "AC-DB-001-01"
            test_name: e.g., "test_query_existing_domain"
            component: e.g., "DomainBrainAPI"
        
        Returns:
            audit_id: Unique identifier for this test run
        """
        audit_id = f"{ac_id}_{test_name}_{datetime.now().isoformat()}"
        
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "ac_id": ac_id,
            "phase_id": "PHASE-17",
            "event_type": "AC_START",
            "test_name": test_name,
            "component": component,
            "audit_id": audit_id,
            "result": None,
            "duration_ms": 0
        }
        
        # Calculate hash with previous hash
        entry_json = json.dumps(entry, sort_keys=True)
        current_hash = sha256(
            (self.previous_hash + entry_json).encode()
        ).hexdigest()
        entry["previous_hash"] = self.previous_hash
        entry["current_hash"] = current_hash
        
        # Persist to database
        self._insert_audit_entry(entry)
        self.previous_hash = current_hash
        
        return audit_id
    
    def log_execution(self, audit_id: str, step: str, result: Any, 
                     duration_ms: int) -> None:
        """Log progress during test execution."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "AC_EXECUTE",
            "audit_id": audit_id,
            "step": step,
            "result": str(result)[:500],  # Truncate long results
            "duration_ms": duration_ms
        }
        
        entry_json = json.dumps(entry, sort_keys=True)
        current_hash = sha256(
            (self.previous_hash + entry_json).encode()
        ).hexdigest()
        entry["previous_hash"] = self.previous_hash
        entry["current_hash"] = current_hash
        
        self._insert_audit_entry(entry)
        self.previous_hash = current_hash
    
    def complete_ac_test(self, audit_id: str, result: str, 
                        error: str = None) -> None:
        """Mark test completion with final result."""
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event_type": "AC_COMPLETE",
            "audit_id": audit_id,
            "result": result,  # PASS, FAIL, SKIP
            "error": error
        }
        
        entry_json = json.dumps(entry, sort_keys=True)
        current_hash = sha256(
            (self.previous_hash + entry_json).encode()
        ).hexdigest()
        entry["previous_hash"] = self.previous_hash
        entry["current_hash"] = current_hash
        
        self._insert_audit_entry(entry)
        self.previous_hash = current_hash
    
    def verify_hash_chain(self, ac_id: str = None, 
                         start_date: datetime = None) -> bool:
        """
        Verify hash chain integrity for audit trail.
        
        Args:
            ac_id: Optional filter (e.g., "AC-DB-001-01")
            start_date: Optional start date for verification window
        
        Returns:
            True if all hashes valid, False if tampering detected
        """
        query = "SELECT * FROM audit_entries WHERE 1=1"
        params = []
        
        if ac_id:
            query += " AND ac_id = ?"
            params.append(ac_id)
        
        if start_date:
            query += " AND timestamp >= ?"
            params.append(start_date.isoformat())
        
        query += " ORDER BY timestamp ASC"
        
        self.cursor.execute(query, params)
        entries = self.cursor.fetchall()
        
        previous_hash = "0" * 64  # Genesis block hash
        
        for entry in entries:
            current_hash = entry["current_hash"]
            previous_hash_in_entry = entry["previous_hash"]
            
            # Verify chain continuity
            if previous_hash_in_entry != previous_hash:
                print(f"❌ Hash chain broken at {entry['timestamp']}")
                return False
            
            # Verify hash calculation
            entry_json = json.dumps(
                {k: v for k, v in entry.items() 
                 if k not in ["current_hash", "previous_hash"]},
                sort_keys=True
            )
            recalculated_hash = sha256(
                (previous_hash + entry_json).encode()
            ).hexdigest()
            
            if recalculated_hash != current_hash:
                print(f"❌ Hash mismatch at {entry['timestamp']}")
                return False
            
            previous_hash = current_hash
        
        print(f"✓ Hash chain verified ({len(entries)} entries)")
        return True
    
    def _insert_audit_entry(self, entry: dict) -> None:
        """Insert entry into database."""
        keys = ", ".join(entry.keys())
        placeholders = ", ".join(["?"] * len(entry))
        
        sql = f"INSERT INTO audit_entries ({keys}) VALUES ({placeholders})"
        self.cursor.execute(sql, tuple(entry.values()))
        self.conn.commit()
    
    def _get_last_hash(self) -> str:
        """Get hash of last audit entry (for chain continuity)."""
        query = "SELECT current_hash FROM audit_entries ORDER BY timestamp DESC LIMIT 1"
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0] if result else "0" * 64
```

### Test Base Class with Audit Integration

```python
# tests/conftest.py - Pytest configuration

import pytest
from src.governance.audit_logger import AuditLogger
from pathlib import Path

@pytest.fixture
def audit_logger():
    """Audit logger instance for each test."""
    db_path = Path(__file__).parent.parent / "cortex_brain" / "state" / "governance.db"
    return AuditLogger(str(db_path))

class AuditedTestCase:
    """Base class for all PHASE-17 tests with audit trail."""
    
    def __init__(self, audit_logger):
        self.audit_logger = audit_logger
        self.audit_id = None
    
    def start_test(self, ac_id: str, test_name: str, component: str):
        """Begin test with audit logging."""
        self.audit_id = self.audit_logger.start_ac_test(
            ac_id=ac_id,
            test_name=test_name,
            component=component
        )
    
    def execute(self, step: str, result: Any, duration_ms: int):
        """Log execution step."""
        if self.audit_id:
            self.audit_logger.log_execution(
                audit_id=self.audit_id,
                step=step,
                result=result,
                duration_ms=duration_ms
            )
    
    def complete(self, result: str, error: str = None):
        """Mark test complete."""
        if self.audit_id:
            self.audit_logger.complete_ac_test(
                audit_id=self.audit_id,
                result=result,
                error=error
            )
```

---

## 🔌 AUDIT TRAIL INTEGRATION PATTERNS

### Pattern 1: Simple Unit Test

```python
# tests/unit/governance/test_phase_17_ac_db_001_01.py

import pytest
from src.domain_brain.api import DomainBrainAPI
from src.governance.audit_logger import AuditLogger

class TestDomainBrainFoundation:
    """AC-DB-001-01: Domain Brain Foundation"""
    
    @pytest.fixture(autouse=True)
    def setup(self, audit_logger):
        self.api = DomainBrainAPI()
        self.audit = audit_logger
    
    def test_query_existing_domain(self):
        """
        Test: DomainBrainAPI.query_domain() returns correct domain
        
        Audit Trail:
        - AC_START: Test beginning
        - AC_EXECUTE: Query executed
        - AC_COMPLETE: Assertions passed
        """
        # 1. AC_START
        audit_id = self.audit.start_ac_test(
            ac_id="AC-DB-001-01",
            test_name="test_query_existing_domain",
            component="DomainBrainAPI"
        )
        
        try:
            # 2. Query execution
            start_time = time.time()
            domain = self.api.query_domain("user-auth-domain")
            duration_ms = (time.time() - start_time) * 1000
            
            # 3. Log execution
            self.audit.log_execution(
                audit_id=audit_id,
                step="query_complete",
                result={"domain_id": domain.id, "entities": len(domain.entities)},
                duration_ms=int(duration_ms)
            )
            
            # 4. Assertions
            assert domain is not None
            assert domain.id == "user-auth-domain"
            assert len(domain.entities) >= 3
            
            # 5. AC_COMPLETE - success
            self.audit.complete_ac_test(
                audit_id=audit_id,
                result="PASS"
            )
            
        except Exception as e:
            # 5. AC_COMPLETE - failure
            self.audit.complete_ac_test(
                audit_id=audit_id,
                result="FAIL",
                error=str(e)
            )
            raise
    
    def test_list_domains(self):
        """Test: DomainBrainAPI.list_domains() returns all domains"""
        audit_id = self.audit.start_ac_test(
            ac_id="AC-DB-001-01",
            test_name="test_list_domains",
            component="DomainBrainAPI"
        )
        
        try:
            domains = self.api.list_domains()
            
            self.audit.log_execution(
                audit_id=audit_id,
                step="list_complete",
                result={"count": len(domains)},
                duration_ms=50
            )
            
            assert len(domains) >= 5  # Should have test domains
            
            self.audit.complete_ac_test(audit_id=audit_id, result="PASS")
            
        except Exception as e:
            self.audit.complete_ac_test(
                audit_id=audit_id,
                result="FAIL",
                error=str(e)
            )
            raise
```

### Pattern 2: Integration Test (Multi-Component)

```python
# tests/integration/test_phase_17_ac_db_002_01.py

class TestSourceAdapters:
    """AC-DB-002-01: Source Adapters Integration"""
    
    def test_git_adapter_integration(self, audit_logger):
        """
        Integration: GitAdapter → ConsistencyValidator → AuditLogger
        
        Multiple components, multiple EXECUTE events
        """
        audit_id = audit_logger.start_ac_test(
            ac_id="AC-DB-002-01",
            test_name="test_git_adapter_integration",
            component="GitAdapter+ConsistencyValidator+AuditLogger"
        )
        
        try:
            # Component 1: GitAdapter
            adapter = GitAdapter()
            git_data = adapter.fetch_history("src/core/")
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="git_adapter_fetch_complete",
                result={"commits": len(git_data)},
                duration_ms=120
            )
            
            # Component 2: ConsistencyValidator
            validator = ConsistencyValidator()
            validation_result = validator.validate(git_data)
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="consistency_validation_complete",
                result={"valid": validation_result.is_valid},
                duration_ms=85
            )
            
            assert validation_result.is_valid
            
            # Component 3: AuditLogger
            domain_brain = DomainBrainAPI()
            domain_brain.audit_log.append(git_data)
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="audit_log_append_complete",
                result={"entries": len(domain_brain.audit_log)},
                duration_ms=25
            )
            
            audit_logger.complete_ac_test(audit_id=audit_id, result="PASS")
            
        except Exception as e:
            audit_logger.complete_ac_test(
                audit_id=audit_id,
                result="FAIL",
                error=str(e)
            )
            raise
```

### Pattern 3: Edge Case Test with Multi-Step Audit

```python
# tests/unit/governance/test_phase_17_ac_db_e01.py

class TestDuplicateDetection:
    """AC-DB-E01: Duplicate Upload Detection"""
    
    def test_duplicate_upload_detection(self, audit_logger):
        """
        Test: Hash-based deduplication prevents duplicate uploads
        
        Multi-step verification:
        1. Upload v1
        2. Attempt upload v2 (identical)
        3. Verify deduplication
        4. Verify audit trail
        """
        audit_id = audit_logger.start_ac_test(
            ac_id="AC-DB-E01",
            test_name="test_duplicate_upload_detection",
            component="DuplicationDetector"
        )
        
        try:
            detector = DuplicationDetector()
            
            # Step 1: Upload v1
            domain_v1 = create_test_domain("auth-service")
            domain_v1_hash = detector.compute_domain_hash(domain_v1)
            result_v1 = detector.upload_domain(domain_v1)
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="upload_v1_complete",
                result={"hash": domain_v1_hash, "success": result_v1.success},
                duration_ms=45
            )
            
            assert result_v1.success
            
            # Step 2: Attempt upload v2 (identical)
            domain_v2 = copy.deepcopy(domain_v1)  # Identical
            domain_v2_hash = detector.compute_domain_hash(domain_v2)
            result_v2 = detector.upload_domain(domain_v2)
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="upload_v2_attempt_complete",
                result={"hash": domain_v2_hash, "dedup_triggered": result_v2.dedup_triggered},
                duration_ms=30
            )
            
            # Step 3: Verify deduplication
            assert domain_v1_hash == domain_v2_hash, "Hashes must match"
            assert result_v2.dedup_triggered, "Deduplication should trigger"
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="deduplication_verified",
                result={"matching_hashes": True, "dedup_active": True},
                duration_ms=10
            )
            
            # Step 4: Verify audit trail shows both attempts
            audit_trail = detector.get_audit_trail(domain_v1.id)
            
            audit_logger.log_execution(
                audit_id=audit_id,
                step="audit_trail_verification_complete",
                result={"audit_entries": len(audit_trail)},
                duration_ms=20
            )
            
            assert len(audit_trail) >= 2, "Both attempts should be in audit"
            assert audit_trail[-1].event_type == "DUPLICATE_DETECTED"
            
            audit_logger.complete_ac_test(audit_id=audit_id, result="PASS")
            
        except Exception as e:
            audit_logger.complete_ac_test(
                audit_id=audit_id,
                result="FAIL",
                error=str(e)
            )
            raise
```

---

## 📅 WEEKLY CHECKPOINT PROCEDURE

### Checkpoint Execution Checklist

```bash
#!/bin/bash
# scripts/phase_17_weekly_checkpoint.sh

set -e

PHASE="PHASE-17"
DB_PATH="cortex_brain/state/governance.db"
WEEK=$1

echo "📍 PHASE-17 Weekly Checkpoint: Week $WEEK"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# 1. Verify all tests passed
echo "✓ Step 1: Verifying test results"
python -c "
import sqlite3
conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()

cursor.execute('''
    SELECT COUNT(*), SUM(CASE WHEN result='PASS' THEN 1 ELSE 0 END)
    FROM audit_entries 
    WHERE event_type='AC_COMPLETE' AND phase_id='$PHASE'
''')

total, passed = cursor.fetchone()
print(f'Tests: {passed}/{total} passed')
if passed < total:
    print('❌ Some tests failed - cannot proceed to checkpoint')
    exit(1)
"

# 2. Verify hash chain integrity
echo "✓ Step 2: Verifying hash chain integrity"
python << 'EOF'
from src.governance.audit_logger import AuditLogger

logger = AuditLogger('cortex_brain/state/governance.db')
if not logger.verify_hash_chain(ac_id=None):
    exit(1)
EOF

# 3. Calculate checkpoint hash
echo "✓ Step 3: Calculating checkpoint hash"
CHECKPOINT_HASH=$(python -c "
import sqlite3
from hashlib import sha256

conn = sqlite3.connect('$DB_PATH')
cursor = conn.cursor()

cursor.execute('''
    SELECT current_hash FROM audit_entries 
    WHERE phase_id='$PHASE'
    ORDER BY timestamp DESC LIMIT 1
''')

last_hash = cursor.fetchone()
print(last_hash[0] if last_hash else 'N/A')
")

echo "Checkpoint Hash: $CHECKPOINT_HASH"

# 4. Store checkpoint
echo "✓ Step 4: Storing checkpoint"
sqlite3 "$DB_PATH" <<EOF_SQL
INSERT INTO phase_checkpoints (phase_id, week, checkpoint_hash, verified_at)
VALUES ('$PHASE', $WEEK, '$CHECKPOINT_HASH', datetime('now'));
EOF_SQL

# 5. Generate checkpoint report
echo "✓ Step 5: Generating checkpoint report"
python scripts/phase_17_checkpoint_report.py --week $WEEK

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Week $WEEK Checkpoint Complete"
```

### Checkpoint Report Template

```python
# scripts/phase_17_checkpoint_report.py

import sqlite3
from datetime import datetime
import json

def generate_checkpoint_report(week: int):
    """Generate comprehensive checkpoint report."""
    
    db = sqlite3.connect('cortex_brain/state/governance.db')
    cursor = db.cursor()
    
    # Aggregate stats
    cursor.execute('''
        SELECT 
            COUNT(*) as total_entries,
            COUNT(DISTINCT ac_id) as ac_ids_tested,
            SUM(CASE WHEN result='PASS' THEN 1 ELSE 0 END) as tests_passed,
            SUM(CASE WHEN result='FAIL' THEN 1 ELSE 0 END) as tests_failed,
            AVG(duration_ms) as avg_duration_ms,
            MAX(timestamp) as last_test_time
        FROM audit_entries 
        WHERE phase_id='PHASE-17'
    ''')
    
    stats = cursor.fetchone()
    
    report = {
        "week": week,
        "timestamp": datetime.utcnow().isoformat(),
        "phase": "PHASE-17",
        "statistics": {
            "total_audit_entries": stats[0],
            "ac_ids_tested": stats[1],
            "tests_passed": stats[2],
            "tests_failed": stats[3],
            "avg_duration_ms": stats[4],
            "pass_rate": f"{stats[2] / (stats[2] + stats[3]) * 100:.1f}%"
        },
        "status": "✅ CHECKPOINT VERIFIED" if stats[3] == 0 else "❌ FAILURES DETECTED"
    }
    
    print(json.dumps(report, indent=2))
    return report
```

---

## 🔍 MONITORING & TROUBLESHOOTING

### Common Issues & Solutions

#### Issue 1: Hash Chain Broken

```
❌ Error: Hash chain broken at 2026-01-23T14:30:45.123Z
```

**Solution**:
```python
# Identify break point and investigate
python -c "
import sqlite3
from src.governance.audit_logger import AuditLogger

db = sqlite3.connect('cortex_brain/state/governance.db')
cursor = db.cursor()

# Find entry before break
cursor.execute('''
    SELECT timestamp, ac_id, event_type, current_hash 
    FROM audit_entries 
    WHERE timestamp < '2026-01-23T14:30:45.123Z'
    ORDER BY timestamp DESC LIMIT 1
''')
print('Last valid entry:', cursor.fetchone())

# Find first broken entry
cursor.execute('''
    SELECT timestamp, ac_id, event_type, current_hash, previous_hash
    FROM audit_entries 
    WHERE timestamp >= '2026-01-23T14:30:45.123Z'
    ORDER BY timestamp ASC LIMIT 1
''')
print('First broken entry:', cursor.fetchone())
"

# Option: Rollback to last known good checkpoint
git checkout phase_17_week_3_checkpoint
python init_db.py --restore-checkpoint phase_17_week_3_checkpoint
```

#### Issue 2: Missing Audit Entries

```
❌ Error: Test completed but no audit entries found for AC-DB-001-01
```

**Solution**:
```python
# Check if test actually ran
pytest tests/unit/governance/test_phase_17_ac_db_001_01.py -v --tb=short

# Verify database connection
python -c "
import sqlite3
db = sqlite3.connect('cortex_brain/state/governance.db')
cursor = db.cursor()
cursor.execute('SELECT COUNT(*) FROM audit_entries')
print(f'Total audit entries: {cursor.fetchone()[0]}')
"

# Re-run with explicit logging
pytest tests/unit/governance/test_phase_17_ac_db_001_01.py \
  -v -s --audit-trace --log-cli-level=DEBUG
```

#### Issue 3: Performance Degradation

```
❌ Warning: Tests running slow (>5 seconds, expected <3 seconds)
```

**Solution**:
```bash
# 1. Check database size
du -h cortex_brain/state/governance.db

# 2. Optimize indexes
sqlite3 cortex_brain/state/governance.db "ANALYZE"
sqlite3 cortex_brain/state/governance.db "VACUUM"

# 3. Check for slow queries
python -c "
import sqlite3
db = sqlite3.connect('cortex_brain/state/governance.db')
cursor = db.cursor()

# Recent entries (should be <5ms with TTL cache)
import time
start = time.time()
cursor.execute('SELECT * FROM audit_entries WHERE timestamp > datetime(\"now\", \"-1 day\")')
elapsed = (time.time() - start) * 1000
print(f'Recent entries query: {elapsed:.1f}ms')

# By AC-ID (should be <10ms with index)
start = time.time()
cursor.execute('SELECT * FROM audit_entries WHERE ac_id = \"AC-DB-001-01\"')
elapsed = (time.time() - start) * 1000
print(f'AC-ID lookup: {elapsed:.1f}ms')
"

# 4. Check index usage
sqlite3 cortex_brain/state/governance.db "PRAGMA index_list(audit_entries);"
```

---

## ⚡ PERFORMANCE OPTIMIZATION TIPS

### 1. Batch Audit Entries

```python
# Instead of logging every assertion:
# ❌ NOT RECOMMENDED
for i in range(100):
    result = api.query_domain(f"domain-{i}")
    audit_logger.log_execution(...)  # 100 database writes!

# ✅ RECOMMENDED
results = []
for i in range(100):
    result = api.query_domain(f"domain-{i}")
    results.append(result)

audit_logger.log_execution(
    ...,
    result={"count": len(results), "sample": results[:5]}
)
```

### 2. Use TTL Cache for Recent Entries

```python
# src/governance/audit_logger.py with caching

from functools import lru_cache
from datetime import datetime, timedelta

class AuditLoggerOptimized(AuditLogger):
    def __init__(self, db_path):
        super().__init__(db_path)
        self.recent_entries_cache = []
        self.cache_ttl = timedelta(hours=1)
        self.cache_timestamp = datetime.utcnow()
    
    def get_recent_entries(self, hours: int = 24):
        """Get recent entries from cache when possible."""
        # If cache is fresh, return cached entries
        if datetime.utcnow() - self.cache_timestamp < self.cache_ttl:
            return self.recent_entries_cache
        
        # Otherwise query database
        query = '''
            SELECT * FROM audit_entries 
            WHERE timestamp > datetime("now", "-{} hours")
            ORDER BY timestamp DESC
        '''.format(hours)
        
        self.cursor.execute(query)
        entries = self.cursor.fetchall()
        
        # Update cache
        self.recent_entries_cache = entries
        self.cache_timestamp = datetime.utcnow()
        
        return entries
```

### 3. Parallel Test Execution

```bash
# Run tests in parallel within same AC (independent tests)
# Across ACs maintain sequence (dependencies)

pytest tests/unit/governance/test_phase_17_*.py \
  -n 4 \  # Use 4 processes
  --dist loadgroup \  # Group by AC
  -v --audit-trace \
  2>&1 | tee phase_17_test_run.log

# Expected speedup: 4x (on 4-core system)
# Example: 3 minutes → 45 seconds
```

### 4. Weekly Checkpoint Optimization

```python
# Don't verify every entry, verify checkpoint hash

class FastCheckpointVerification:
    """Verify only checkpoint hashes, not every entry."""
    
    def verify_week(self, week: int) -> bool:
        """Verify week checkpoint (fast)."""
        db = sqlite3.connect('cortex_brain/state/governance.db')
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT checkpoint_hash FROM phase_checkpoints 
            WHERE phase_id='PHASE-17' AND week=?
        ''', (week,))
        
        stored_hash = cursor.fetchone()
        if not stored_hash:
            return False
        
        # Get current chain tail hash
        cursor.execute('''
            SELECT current_hash FROM audit_entries 
            WHERE phase_id='PHASE-17'
            ORDER BY timestamp DESC LIMIT 1
        ''')
        
        tail_hash = cursor.fetchone()[0]
        
        # Quick comparison
        return tail_hash == stored_hash[0]
```

---

## 🔄 ROLLBACK PROCEDURES

### Full Phase Rollback

```bash
#!/bin/bash
# scripts/phase_17_full_rollback.sh

CHECKPOINT=$1  # e.g., "week_2"

echo "⚠️ Rolling back PHASE-17 to checkpoint: $CHECKPOINT"

# 1. Get checkpoint info
CHECKPOINT_HASH=$(sqlite3 cortex_brain/state/governance.db \
  "SELECT checkpoint_hash FROM phase_checkpoints WHERE phase_id='PHASE-17' AND checkpoint='$CHECKPOINT'")

# 2. Delete all entries after checkpoint
sqlite3 cortex_brain/state/governance.db <<EOF
DELETE FROM audit_entries 
WHERE phase_id='PHASE-17' AND timestamp > (
    SELECT verified_at FROM phase_checkpoints 
    WHERE checkpoint='$CHECKPOINT'
);
EOF

# 3. Verify integrity
python -c "
from src.governance.audit_logger import AuditLogger
logger = AuditLogger('cortex_brain/state/governance.db')
if logger.verify_hash_chain(ac_id=None):
    print('✅ Rollback successful')
else:
    print('❌ Rollback failed - hash chain broken')
    exit(1)
"

# 4. Restore code to checkpoint
git checkout refs/tags/phase_17_${CHECKPOINT}

echo "✅ PHASE-17 rolled back to $CHECKPOINT"
```

### Selective AC Rollback

```python
# Rollback single AC without affecting others

def rollback_ac(ac_id: str, to_timestamp: str = None):
    """Roll back specific AC to checkpoint."""
    db = sqlite3.connect('cortex_brain/state/governance.db')
    cursor = db.cursor()
    
    # Find last AC_START before timestamp
    if not to_timestamp:
        cursor.execute('''
            SELECT timestamp FROM audit_entries 
            WHERE ac_id=? AND event_type='AC_START'
            ORDER BY timestamp DESC LIMIT 1 OFFSET 1
        ''', (ac_id,))
        to_timestamp = cursor.fetchone()[0]
    
    # Delete all entries for this AC after rollback point
    cursor.execute('''
        DELETE FROM audit_entries 
        WHERE ac_id=? AND timestamp > ?
    ''', (ac_id, to_timestamp))
    
    db.commit()
    print(f"✅ Rolled back AC {ac_id} to {to_timestamp}")
```

---

## 📋 SUMMARY CHECKLIST

- [ ] Audit logger implemented and tested
- [ ] Database schema includes audit_entries table with hash chain
- [ ] All tests updated to use AuditedTestCase base class
- [ ] AC_START/EXECUTE/COMPLETE events logged for every test
- [ ] Hash chain verification working (no tampering)
- [ ] Weekly checkpoints created with automated procedure
- [ ] Performance benchmarks established (<5% audit overhead)
- [ ] Monitoring dashboard updated with audit metrics
- [ ] Rollback procedures tested end-to-end
- [ ] Documentation provided to dev team
- [ ] Phase lock readiness confirmed

---

**Questions?** Contact the Architecture Team for clarification on audit trail validation strategy.

**Next Steps**: Execute PHASE-17 Week 1 with full audit trail validation enabled.
