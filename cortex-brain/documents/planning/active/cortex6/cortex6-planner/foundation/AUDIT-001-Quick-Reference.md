# AUDIT-001 Quick Reference Card

**Task:** AuditLogger Infrastructure Migration  
**Status:** ✅ READY FOR IMPLEMENTATION  
**Estimate:** 12-16 hours  
**Priority:** P0_CRITICAL (Blocks ALL 354+ AC validation)

---

## 🎯 What We're Doing

**Strategy:** REFACTOR existing AuditLogger (not rewrite)  
**Why:** 85% of needed functionality already exists at `src/orchestrators/audit_logger.py`

---

## 📋 Implementation Checklist

### Phase 1: Preparation (1-2h)
- [ ] Create `src/infrastructure/` directory
- [ ] Create `cortex-brain/schemas/audit_schema.sql`
- [ ] Create `cortex-brain/config/audit-config.yaml`
- [ ] Create `tests/audit/` directory

### Phase 2: New Components (4-6h)
- [ ] Implement `src/infrastructure/audit_storage.py` (SQLite backend)
- [ ] Implement `src/infrastructure/audit_memory_buffer.py` (flush logic)
- [ ] Implement `src/infrastructure/repo_context.py` (per-repo isolation)
- [ ] Write tests: `test_audit_storage.py`, `test_memory_buffer.py`, `test_repo_isolation.py`

### Phase 3: AuditLogger Refactoring (4-5h)
- [ ] Move `src/orchestrators/audit_logger.py` → `src/infrastructure/audit_logger.py`
- [ ] Add `ac_id` field to `AuditEntry` dataclass
- [ ] Replace file storage with SQLite backend
- [ ] Integrate memory buffer
- [ ] Update `log()` method to accept `ac_id` parameter
- [ ] Replace `search()` with SQL queries

### Phase 4: MCP Tools (3-4h)
- [ ] Implement `src/mcp/audit_tools.py`
  - [ ] `mcp_audit_query()` - Query with filters
  - [ ] `mcp_audit_list()` - Paginated list view
  - [ ] `mcp_audit_export()` - Export to jsonl/csv/json
  - [ ] `mcp_audit_validate()` - AC validation with evidence
- [ ] Write tests: `test_audit_tools.py`

### Phase 5: Retention & Vacuum (4h)
- [ ] Implement `src/infrastructure/audit_vacuum.py` (retention policy)
- [ ] Update `src/orchestrators/housekeeping_orchestrator.py` (scheduler)
- [ ] Write tests: `test_retention_policy.py`, `test_audit_vacuum.py`

### Phase 6: Testing & Validation (2-3h)
- [ ] Migrate `tests/unit/test_audit_logger.py` → `tests/audit/test_audit_logger.py`
- [ ] Run all audit tests and ensure 100% pass rate
- [ ] Validate all 6 AC-AUDIT criteria
- [ ] Generate test coverage report

### Phase 7: Migration & Cleanup (1h)
- [ ] Update all imports: `src.orchestrators.audit_logger` → `src.infrastructure.audit_logger`
- [ ] Remove deprecated JSONL log files (migrate to SQLite)
- [ ] Update documentation references
- [ ] Final validation

---

## 🗂️ File Structure

```
src/
├── infrastructure/          # NEW: Infrastructure layer
│   ├── audit_logger.py      # MIGRATED from orchestrators
│   ├── audit_storage.py     # NEW: SQLite backend
│   ├── audit_memory_buffer.py  # NEW: Memory buffer
│   ├── audit_query.py       # NEW: Query interface
│   ├── audit_vacuum.py      # NEW: Retention policy
│   └── repo_context.py      # NEW: Per-repo detection
├── mcp/
│   └── audit_tools.py       # NEW: MCP tool implementations
└── orchestrators/
    └── housekeeping_orchestrator.py  # ENHANCED: Vacuum scheduler

cortex-brain/
├── config/
│   └── audit-config.yaml    # NEW: Configuration
├── schemas/
│   └── audit_schema.sql     # NEW: Database schema
└── state/
    └── audit.db            # NEW: SQLite database (per-repo)

tests/
├── audit/                   # NEW: Consolidated audit tests
│   ├── test_audit_logger.py
│   ├── test_audit_storage.py
│   ├── test_audit_queries.py
│   ├── test_memory_buffer.py
│   ├── test_repo_isolation.py
│   ├── test_retention_policy.py
│   └── test_audit_vacuum.py
└── mcp/
    └── test_audit_tools.py
```

---

## 🔑 Key Changes

### AuditEntry Enhancement
```python
# BEFORE
@dataclass
class AuditEntry:
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    component: str
    operation: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None
    duration_ms: Optional[float] = None

# AFTER (add ac_id field)
@dataclass
class AuditEntry:
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    component: str
    operation: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    ac_id: Optional[str] = None  # NEW
    correlation_id: Optional[str] = None
    duration_ms: Optional[float] = None
```

### log() Method Enhancement
```python
# BEFORE
def log(
    self,
    level: AuditLevel,
    category: AuditCategory,
    component: str,
    operation: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    correlation_id: Optional[str] = None,
    duration_ms: Optional[float] = None
):
    # ... writes to JSONL file ...

# AFTER
def log(
    self,
    level: AuditLevel,
    category: AuditCategory,
    component: str,
    operation: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ac_id: Optional[str] = None,  # NEW
    correlation_id: Optional[str] = None,
    duration_ms: Optional[float] = None
):
    # ... writes to memory buffer → SQLite ...
```

### search() Method Enhancement
```python
# BEFORE
def search(
    self,
    category: Optional[AuditCategory] = None,
    component: Optional[str] = None,
    operation: Optional[str] = None,
    level: Optional[AuditLevel] = None,
    correlation_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None
) -> List[AuditEntry]:
    # ... scans JSONL files ...

# AFTER
def search(
    self,
    ac_id: Optional[str] = None,  # NEW
    category: Optional[AuditCategory] = None,
    component: Optional[str] = None,
    operation: Optional[str] = None,
    level: Optional[AuditLevel] = None,
    correlation_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,  # NEW
    offset: int = 0    # NEW
) -> List[AuditEntry]:
    # ... queries SQLite database ...
```

---

## 🗄️ Database Schema

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    category TEXT NOT NULL,
    component TEXT NOT NULL,
    operation TEXT NOT NULL,
    message TEXT NOT NULL,
    context_json TEXT,
    metadata_json TEXT,
    ac_id TEXT,              -- NEW: AC-ID tagging
    correlation_id TEXT,
    duration_ms REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Performance indexes
CREATE INDEX idx_ac_id ON audit_logs(ac_id);
CREATE INDEX idx_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_level ON audit_logs(level);
CREATE INDEX idx_category ON audit_logs(category);
CREATE INDEX idx_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_component ON audit_logs(component);
CREATE INDEX idx_created_at ON audit_logs(created_at);
```

---

## 🛠️ MCP Tools API

### audit_query
```python
result = mcp_audit_query(
    ac_id="AC-GOV-001",
    level="ERROR",
    date_range=("2026-01-01", "2026-01-09"),
    limit=100
)
# Returns: {"total_count": int, "results": List[dict], "pagination": {...}}
```

### audit_list
```python
result = mcp_audit_list(
    orchestrator="planning",
    page=1,
    page_size=50
)
# Returns: {"page": 1, "total_pages": int, "entries": List[dict]}
```

### audit_export
```python
result = mcp_audit_export(
    format="csv",
    ac_id="AC-GOV-001",
    output_file="exports/audit_export.csv"
)
# Returns: {"format": "csv", "output_file": str, "entry_count": int}
```

### audit_validate
```python
result = mcp_audit_validate(ac_id="AC-GOV-001")
# Returns: {
#     "ac_id": "AC-GOV-001",
#     "validation_status": "VALIDATED" | "INCOMPLETE" | "FAILED",
#     "audit_trace_exists": bool,
#     "evidence": {...}
# }
```

---

## ⚙️ Configuration

### audit-config.yaml
```yaml
audit_configuration:
  # Retention policy (days)
  retention_days:
    CRITICAL: 90
    ERROR: 90
    WARNING: 60
    INFO: 30
    DEBUG: 7
    TRACE: 7
  
  # Memory buffer settings
  memory_buffer:
    enabled: true
    max_entries: 1000
    max_memory_mb: 10
    flush_interval_seconds: 60
    flush_on_error: true
  
  # Vacuum schedule
  vacuum:
    enabled: true
    schedule: "daily"
    schedule_time: "02:00"
```

---

## ✅ Acceptance Criteria

### AC-AUDIT-001: Queryable by AC-ID, orchestrator, date range
**Test:**
```python
entries = audit_logger.search(ac_id="AC-GOV-001")
assert all(e.ac_id == "AC-GOV-001" for e in entries)
```

### AC-AUDIT-002: Memory buffer with flush thresholds
**Test:**
```python
# Add 1001 entries → flush triggered at 1000
# Add ERROR entry → immediate flush
```

### AC-AUDIT-003: Per-repo SQLite isolation
**Test:**
```python
# Log from repo A → only in repo A's audit.db
# Switch to repo B → logs go to repo B's audit.db
```

### AC-AUDIT-004: MCP tools operational
**Test:**
```python
result = mcp_audit_query(ac_id="AC-GOV-001")
assert result["total_count"] > 0
```

### AC-AUDIT-005: Automatic vacuum
**Test:**
```python
# 31-day-old INFO log → deleted by vacuum
# 89-day-old ERROR log → preserved by vacuum
```

### AC-AUDIT-006: Level-based retention
**Test:**
```python
assert retention_policy[AuditLevel.ERROR] == 90
assert retention_policy[AuditLevel.INFO] == 30
```

---

## 📚 Related Documents

- **Detailed Plan:** `implementation-guides/AUDIT-001-Refactoring-Plan.md` (550+ lines)
- **Analysis Summary:** `analysis/AUDIT-001-Analysis-Summary.md`
- **AC Specifications:** `acceptance-criteria/CX6-acceptance-criteria.yaml` (AC-AUDIT-001 to AC-AUDIT-006)
- **Existing Code:** `src/orchestrators/audit_logger.py` (1133 lines)
- **Existing Tests:** `tests/unit/test_audit_logger.py` (700 lines)

---

## 🚀 Quick Start

```bash
# 1. Review the comprehensive plan
open cortex-brain/documents/planning/active/cortex6/implementation-guides/AUDIT-001-Refactoring-Plan.md

# 2. Start Phase 1 (Preparation)
mkdir -p src/infrastructure
mkdir -p tests/audit
mkdir -p cortex-brain/schemas
mkdir -p cortex-brain/config

# 3. Create schema file
touch cortex-brain/schemas/audit_schema.sql

# 4. Create config file
touch cortex-brain/config/audit-config.yaml

# 5. Begin implementation following 7-phase plan
# (See detailed plan for code examples and test cases)
```

---

**Created:** 2026-01-09  
**Estimate:** 12-16 hours  
**Blocks:** ALL 354+ AC validation  
**Status:** ✅ READY FOR IMPLEMENTATION

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
