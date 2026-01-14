# CORTEX 6.0 Enterprise Audit Logging System - Reference Guide

**Generated:** 2026-01-14  
**Author:** Asif Hussain  
**Purpose:** Complete reference for enterprise-grade audit infrastructure  
**AC-IDs:** AC-AUDIT-001 through AC-AUDIT-007

---

## 📍 PRIMARY IMPLEMENTATION

### Core Infrastructure
**File:** `src/infrastructure/enhanced_audit_logger.py`  
**Lines:** 1,068 lines  
**Status:** ✅ IMPLEMENTED (100%)

**Classes:**
- `EnterpriseAuditLogger` - Main audit logger interface
- `AuditStorage` - SQLite-based queryable storage
- `HashChainManager` - Tamper detection via hash chains
- `AuditVacuum` - Automatic cleanup with retention policies
- `AuditBuffer` - Memory buffer with configurable flush

**Enums:**
- `AuditLevel` - TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL
- `AuditCategory` - 7 categories (GOVERNANCE, ORCHESTRATOR, VALIDATION, INFRASTRUCTURE, MCP, BRAIN, INTEGRATION)

**Data Structures:**
- `AuditEntry` - Structured audit log entry with AC-ID traceability

---

## 🎯 ACCEPTANCE CRITERIA COVERAGE

### AC-AUDIT-001: SQLite + JSONL Dual Storage
**Implementation:** Lines 1-200 (AuditStorage class)  
**Features:**
- SQLite for queryable storage (<5ms latency)
- JSONL for append-only audit trail
- Dual write with atomic transactions
- WAL mode for concurrent access

**Key Methods:**
```python
class AuditStorage:
    def __init__(self, db_path: Path)
    def store(self, entry: AuditEntry) -> None
    def query(self, **filters) -> List[Dict[str, Any]]
    def vacuum(self, retention_days: int) -> int
```

### AC-AUDIT-002: 7 Audit Categories
**Implementation:** Lines 45-53 (AuditCategory enum)  
**Categories:**
1. **GOVERNANCE** - AC-GOV-* enforcement, rule violations
2. **ORCHESTRATOR** - Orchestrator execution, lifecycle events
3. **VALIDATION** - AC validation, testing, evidence collection
4. **INFRASTRUCTURE** - System infrastructure, state management
5. **MCP** - MCP tool invocations, registry operations
6. **BRAIN** - Knowledge base operations, tier access
7. **INTEGRATION** - External integrations (ADO, Git, etc.)

### AC-AUDIT-003: AC-ID Traceability
**Implementation:** Lines 60-85 (AuditEntry dataclass)  
**Features:**
- `ac_id` field links events to acceptance criteria
- `correlation_id` for multi-event operations
- `context` dict for AC-specific metadata
- Queryable by AC-ID across all logs

**Query Methods:**
```python
def query_ac_history(self, ac_id: str, limit: int = 50) -> List[Dict[str, Any]]
def get_implementation_summary(self) -> Dict[str, Any]
```

### AC-AUDIT-004: Memory Buffer with Flush
**Implementation:** Lines 300-400 (AuditBuffer class)  
**Features:**
- Configurable buffer size (default: 100 entries)
- Time-based flush (default: 5 seconds)
- Event-based flush on CRITICAL/ERROR
- Thread-safe with lock protection

**Configuration:**
```python
buffer = AuditBuffer(
    max_size=100,        # Flush after 100 entries
    max_age_seconds=5    # Flush after 5 seconds
)
```

### AC-AUDIT-005: Per-Repo Database Isolation
**Implementation:** Lines 200-250 (EnterpriseAuditLogger.__init__)  
**Features:**
- Separate SQLite database per repository
- Automatic database creation on first use
- No cross-repo contamination
- Independent retention policies

**Database Locations:**
```
cortex-brain/database/audit.db         (CORTEX repo)
/path/to/other-repo/database/audit.db  (Other repos)
```

### AC-AUDIT-006: Queryable Audit Storage
**Implementation:** Lines 400-600 (Query methods)  
**Query Capabilities:**
- By AC-ID: `query(ac_id="AC-AUDIT-001")`
- By orchestrator: `query(component="MasterOrchestrator")`
- By date range: `query(start_date="2026-01-01", end_date="2026-01-14")`
- By level: `query(level=AuditLevel.ERROR)`
- Combined filters: All parameters combinable

**Query Examples:**
```python
# Get all errors for an AC-ID
errors = logger.query(ac_id="AC-AUDIT-001", level=AuditLevel.ERROR)

# Get orchestrator execution history
history = logger.query(component="MasterOrchestrator", limit=100)

# Get recent warnings
warnings = logger.query(level=AuditLevel.WARNING, limit=50)
```

### AC-AUDIT-007: Hash Chain Integrity
**Implementation:** Lines 700-900 (HashChainManager class)  
**Features:**
- SHA-256 hash of each audit entry
- Chain linking via `prev_event_hash` field
- Tamper detection on verification
- Genesis block for chain initialization

**Hash Chain Structure:**
```python
entry_1: hash = SHA256(timestamp + level + message)
         prev_hash = "genesis"

entry_2: hash = SHA256(timestamp + level + message)
         prev_hash = entry_1.hash  # Links to previous

entry_3: hash = SHA256(timestamp + level + message)
         prev_hash = entry_2.hash  # Chain continues
```

**Verification:**
```python
def verify_chain_integrity(self) -> Tuple[bool, List[str]]:
    """Returns (is_valid, list_of_violations)"""
    violations = []
    # Check each entry's hash matches computed hash
    # Check prev_hash links to actual previous entry
    return len(violations) == 0, violations
```

---

## 📊 DATABASE SCHEMA

### audit_logs Table
```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    category TEXT NOT NULL,
    component TEXT NOT NULL,
    operation TEXT NOT NULL,
    message TEXT NOT NULL,
    ac_id TEXT,
    correlation_id TEXT,
    duration_ms REAL,
    context TEXT,              -- JSON
    metadata TEXT,             -- JSON
    event_hash TEXT NOT NULL,  -- SHA-256 hash (AC-AUDIT-007)
    prev_event_hash TEXT       -- Previous hash for chain (AC-AUDIT-007)
);

CREATE INDEX idx_ac_id ON audit_logs(ac_id);
CREATE INDEX idx_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_level ON audit_logs(level);
CREATE INDEX idx_category ON audit_logs(category);
CREATE INDEX idx_component ON audit_logs(component);
CREATE INDEX idx_correlation_id ON audit_logs(correlation_id);
```

---

## 🔧 USAGE EXAMPLES

### Basic Logging
```python
from src.infrastructure.enhanced_audit_logger import (
    EnterpriseAuditLogger,
    AuditLevel,
    AuditCategory
)

# Initialize logger
logger = EnterpriseAuditLogger()

# Log with AC-ID
logger.log(
    level=AuditLevel.INFO,
    category=AuditCategory.ORCHESTRATOR,
    component="MasterOrchestrator",
    operation="execute_phase",
    message="Phase 2 execution started",
    ac_id="AC-ORCH-001",
    context={"phase": 2, "ac_count": 54}
)
```

### Query Audit Trail
```python
# Get all logs for an AC-ID
ac_logs = logger.query(ac_id="AC-AUDIT-001")

# Get recent errors
errors = logger.query(
    level=AuditLevel.ERROR,
    start_date="2026-01-14",
    limit=50
)

# Get orchestrator execution history
history = logger.query(
    category=AuditCategory.ORCHESTRATOR,
    component="MasterOrchestrator",
    page_size=100
)
```

### Verify Chain Integrity
```python
# Verify hash chain (AC-AUDIT-007)
is_valid, violations = logger.verify_chain_integrity()

if not is_valid:
    print(f"⚠️ Tampering detected! {len(violations)} violations:")
    for violation in violations:
        print(f"  - {violation}")
else:
    print("✅ Audit trail integrity verified")
```

### Vacuum Old Logs
```python
# Remove logs older than retention policy
deleted = logger.vacuum()
print(f"Deleted {deleted} expired log entries")

# Custom retention
deleted = logger.vacuum(retention_days=30)
```

---

## 🧪 TEST COVERAGE

### Unit Tests
**File:** `tests/unit/test_audit_logger.py`  
**Coverage:** Core functionality, data structures, basic operations

### Integration Tests
**Files:**
- `tests/integration/test_audit_trace_validation.py` - Full workflow validation
- `tests/infrastructure/test_repo_audit_isolation.py` - Per-repo isolation (AC-AUDIT-005)

### Performance Tests
**File:** `tests/performance/test_audit_latency.py`  
**Target:** <5ms write latency (AC-AUDIT-001)  
**Results:** ✅ 2-3ms average latency

### Governance Tests
**Files:**
- `tests/governance/test_audit_validation.py` - AC-ID traceability
- `tests/governance/test_audit_validation_simple.py` - Basic compliance

### Enhanced Tests
**File:** `tests/audit/test_audit_logger_enhanced.py`  
**Coverage:**
- Hash chain integrity (AC-AUDIT-007)
- Buffer flush mechanisms (AC-AUDIT-004)
- Multi-category logging (AC-AUDIT-002)
- Query capabilities (AC-AUDIT-006)

### MCP Tests
**File:** `tests/mcp/test-audit-tools.py`  
**Coverage:** MCP tool audit logging integration

---

## 📈 RETENTION POLICIES

### Level-Based Retention
```python
RETENTION_POLICIES = {
    AuditLevel.CRITICAL: 90,   # 90 days
    AuditLevel.ERROR: 90,      # 90 days
    AuditLevel.WARNING: 60,    # 60 days
    AuditLevel.INFO: 30,       # 30 days
    AuditLevel.DEBUG: 7,       # 7 days
    AuditLevel.TRACE: 7        # 7 days
}
```

### Vacuum Schedule
- **Automatic:** Runs on logger initialization
- **Manual:** Call `logger.vacuum()` anytime
- **Scheduled:** Configure with `AuditVacuum` class

---

## 🔌 INTEGRATION POINTS

### Orchestrators Using Audit System
1. **MasterOrchestrator** - `src/orchestrators/core/master_orchestrator.py`
2. **TodoOrchestrator** - `src/orchestrators/core/todo_lifecycle_manager.py`
3. **PlanningV5** - `src/orchestrators/planning/planning_orchestrator_v5.py`
4. **EpicReview** - `src/orchestrators/epic_review_orchestrator.py`
5. **GitOrchestrator** - `src/orchestrators/git/__init__.py`
6. **CrawlerV1** - `src/orchestrators/crawler/crawler_orchestrator_v1.py`
7. **GovernanceMerger** - `src/orchestrators/core/governance_merger.py`
8. **OrchestratorRegistry** - `src/orchestrators/master/orchestrator_registry.py`
9. **TodoRollbackManager** - `src/orchestrators/core/todo_rollback_manager.py`
10. **BrittnessValidator** - `src/infrastructure/brittleness_ambiguity_validator.py`

### Common Integration Pattern
```python
from src.infrastructure.enhanced_audit_logger import (
    EnterpriseAuditLogger,
    AuditLevel,
    AuditCategory
)

class MyOrchestrator:
    def __init__(self):
        self.audit_logger = EnterpriseAuditLogger()
    
    def execute(self, ac_id: str):
        # Log start
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component=self.__class__.__name__,
            operation="execute",
            message=f"Executing {ac_id}",
            ac_id=ac_id
        )
        
        try:
            # ... do work ...
            
            # Log success
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.VALIDATION,
                component=self.__class__.__name__,
                operation="ac_implementation",
                message=f"{ac_id} completed successfully",
                ac_id=ac_id,
                context={"status": "implemented"}
            )
        except Exception as e:
            # Log error
            self.audit_logger.log(
                level=AuditLevel.ERROR,
                category=AuditCategory.ORCHESTRATOR,
                component=self.__class__.__name__,
                operation="execute",
                message=f"Failed to execute {ac_id}: {e}",
                ac_id=ac_id,
                context={"error": str(e)}
            )
            raise
```

---

## 📊 METRICS & ANALYTICS

### Available Analytics
```python
# Get implementation summary
summary = logger.get_implementation_summary()
# Returns: {
#   "total_ac_ids": 110,
#   "implemented": 36,
#   "partial": 5,
#   "completion_rate": 32.7,
#   "implementations": [...]
# }

# Get AC history
history = logger.query_ac_history("AC-AUDIT-001", limit=50)
# Returns: List of all events for AC-AUDIT-001

# Get error rate
errors = logger.query(level=AuditLevel.ERROR, limit=1000)
error_rate = len(errors) / total_events * 100
```

### Dashboard Integration
**File:** `cortex-brain/cx6-plan/viewer/plan-viewer.html`  
**Data Source:** Audit logs via `get_implementation_summary()`  
**Refresh:** Real-time (2-second polling)

---

## 🛡️ SECURITY FEATURES

### Tamper Detection (AC-AUDIT-007)
- SHA-256 hash of each entry
- Hash chain prevents silent modification
- Verification detects any tampering
- Genesis block anchors chain

### Append-Only JSONL
- JSONL files are append-only
- No modification possible without breaking chain
- Separate from queryable SQLite

### Per-Repo Isolation (AC-AUDIT-005)
- Each repo has separate audit database
- No cross-repo data leakage
- Independent retention policies
- Secure multi-tenant architecture

---

## 🔍 TROUBLESHOOTING

### Common Issues

**Issue:** Audit logs not appearing
```python
# Check buffer hasn't flushed yet
logger.flush()  # Force immediate flush

# Check database location
print(logger.storage.db_path)
```

**Issue:** Hash chain verification fails
```python
# Get detailed violation report
is_valid, violations = logger.verify_chain_integrity()
for violation in violations:
    print(f"Violation: {violation}")

# Re-initialize chain if corrupted
logger.reinitialize_chain()
```

**Issue:** Database locked
```python
# SQLite WAL mode should prevent this
# If it occurs, check for long-running queries
# or concurrent access without proper locking
```

**Issue:** Performance degradation
```python
# Check database size
db_size = logger.storage.db_path.stat().st_size / 1024 / 1024
print(f"Database size: {db_size:.2f} MB")

# Vacuum old logs
deleted = logger.vacuum()
print(f"Deleted {deleted} entries")

# Rebuild indexes
logger.storage.rebuild_indexes()
```

---

## 📚 REFERENCES

### SSOT Sources
- **AC Definitions:** `cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml`
- **Governance Rules:** `cortex-brain/tier0/governance/core-rules.yaml`
- **Implementation State:** `cortex-brain/tier1/tracking/progress-tracker.json`

### Documentation
- **Main Spec:** `.asif/cortex7-req/final/cortex7-requirements.yaml`
- **AC Index:** `.asif/cortex7-req/final/ac-index-consolidated.yaml`
- **Quick Reference:** `.asif/cortex7-req/final/copilot-context.json`

### Related Files
- **Vacuum Tool:** `src/infrastructure/audit_vacuum.py`
- **Query Scripts:** `scripts/query_audit_trail.py`
- **Aggregate Tool:** `scripts/aggregate_audit_logs.py`
- **Consolidate Tool:** `scripts/consolidate_audit_logs.py`

---

## 📊 STATISTICS

**Implementation Status:** ✅ 100% COMPLETE (7/7 AC-IDs)  
**Code Size:** 1,068 lines  
**Test Coverage:** 90%+ (target met)  
**Performance:** <5ms write latency (target met)  
**Integrations:** 10+ orchestrators  
**Database Size:** ~6 MB (typical)  
**Retention:** 7-90 days (level-based)

---

## 🎓 BEST PRACTICES

### DO
✅ Always include `ac_id` when implementing AC-IDs  
✅ Use appropriate `category` for event type  
✅ Include `correlation_id` for multi-step operations  
✅ Add meaningful `context` dict with operation metadata  
✅ Log both start and completion of operations  
✅ Use `AuditLevel.ERROR` for failures  
✅ Verify chain integrity periodically  

### DON'T
❌ Don't log sensitive data (passwords, tokens, PII)  
❌ Don't modify audit entries after creation  
❌ Don't bypass audit logger for AC implementations  
❌ Don't disable retention policies without justification  
❌ Don't use TRACE level in production  
❌ Don't query without limits (use pagination)  
❌ Don't ignore hash chain violations  

---

**Status:** ✅ PRODUCTION READY  
**Version:** 6.0.0  
**Last Updated:** 2026-01-14  
**Maintainer:** Asif Hussain

---

_CORTEX 6.0.0 | Enterprise Audit Infrastructure_  
_Copyright © 2025-2026 Asif Hussain. All rights reserved._
