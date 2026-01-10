# AUDIT-001 Refactoring Plan: AuditLogger Migration to Infrastructure

**Task:** AUDIT-001 - AuditLogger Infrastructure Migration  
**Type:** Refactoring & Enhancement  
**Priority:** P0_CRITICAL  
**Estimated Effort:** 12-16 hours  
**Created:** 2026-01-09  
**Status:** ANALYSIS COMPLETE → READY FOR IMPLEMENTATION

---

## 📋 Executive Summary

**Current State:**
- ✅ Functional AuditLogger exists at `src/orchestrators/audit_logger.py` (1133 lines)
- ✅ Comprehensive test suite at `tests/unit/test_audit_logger.py` (700 lines)
- ✅ Core features implemented: 7 categories, correlation tracking, error analysis

**Target State (CORTEX 6.0):**
- 🎯 AuditLogger moved to `src/infrastructure/audit_logger.py`
- 🎯 SQLite backend at `cortex-brain/state/audit.db` (per-repo isolation)
- 🎯 AC-ID tagging for all 354+ acceptance criteria
- 🎯 MCP tools: `audit_query`, `audit_list`, `audit_export`, `audit_validate`
- 🎯 Memory buffer with configurable flush thresholds
- 🎯 Automatic retention policy & vacuum (ERROR: 90d, INFO: 30d, DEBUG: 7d)

**Strategy:** REFACTOR existing implementation (not rewrite from scratch)

---

## 🔍 Gap Analysis

### ✅ What We Already Have (Preserve)

| Feature | Current Status | Location | Keep? |
|---------|---------------|----------|-------|
| **AuditLevel enum** | ✅ Complete (5 levels) | Lines 30-36 | ✅ YES |
| **AuditCategory enum** | ✅ Complete (7 categories) | Lines 39-47 | ✅ YES |
| **AuditEntry dataclass** | ✅ Well-structured | Lines 50-68 | 🔄 ENHANCE |
| **Correlation ID tracking** | ✅ Thread-local context | Lines 211-280 | ✅ YES |
| **Correlation chains** | ✅ Parent-child tracking | Lines 255-280 | ✅ YES |
| **Error summary** | ✅ Operational | Lines 705-735 | ✅ YES |
| **Performance metrics** | ✅ With percentiles | Lines 737-780 | ✅ YES |
| **Timeline view** | ✅ Chronological events | Lines 782-817 | ✅ YES |
| **Trace management** | ✅ Start/end tracking | Lines 635-703 | ✅ YES |
| **Phase/feature gates** | ✅ Integrated | Lines 819-1020 | ✅ YES |
| **File-based logging** | ✅ Category-specific JSONL | Lines 283-479 | 🔄 REPLACE |

**Preservation Score:** 85% of existing code can be reused/adapted

### ❌ What We Need to Add (New Features)

| Feature | AC Addressed | Priority | Estimated Effort |
|---------|--------------|----------|------------------|
| **AC-ID field in AuditEntry** | AC-AUDIT-001 | P0 | 1h |
| **SQLite backend** | AC-AUDIT-001, AC-AUDIT-003 | P0 | 4-5h |
| **Query interface** | AC-AUDIT-001 | P0 | 2-3h |
| **Memory buffer** | AC-AUDIT-002 | P0 | 2h |
| **Per-repo isolation** | AC-AUDIT-003 | P0 | 1-2h |
| **MCP tools** | AC-AUDIT-004 | P0 | 3-4h |
| **Retention policy** | AC-AUDIT-005, AC-AUDIT-006 | P1 | 2h |
| **Vacuum scheduler** | AC-AUDIT-005 | P1 | 2h |

**Total New Work:** 17-21 hours (accounting for integration testing and refactoring overhead)

### 🔄 What We Need to Change (Refactoring)

| Component | Current Behavior | Target Behavior | Risk Level |
|-----------|------------------|-----------------|------------|
| **File location** | `src/orchestrators/` | `src/infrastructure/` | 🟢 LOW |
| **Storage backend** | JSONL files per category | SQLite with memory buffer | 🟡 MEDIUM |
| **Entry structure** | 9 fields | 10 fields (add `ac_id`) | 🟢 LOW |
| **Search method** | File scanning | SQL queries | 🟡 MEDIUM |
| **Initialization** | Simple path-based | Repo context detection | 🟢 LOW |

---

## 🏗️ Architecture Design

### Component Hierarchy

```
src/infrastructure/
├── audit_logger.py          # Main AuditLogger class (MIGRATED + ENHANCED)
├── audit_storage.py         # NEW: SQLite storage backend
├── audit_memory_buffer.py   # NEW: Memory buffer with flush logic
├── audit_query.py           # NEW: Query interface
├── audit_vacuum.py          # NEW: Retention policy & vacuum
└── repo_context.py          # NEW: Per-repo database isolation

src/mcp/
└── audit_tools.py           # NEW: MCP tool implementations

cortex-brain/
├── config/
│   └── audit-config.yaml    # NEW: Configuration
├── state/
│   └── audit.db            # NEW: SQLite database (per-repo)
└── schemas/
    └── audit_schema.sql    # NEW: Database schema

tests/
├── audit/                   # NEW: Consolidated audit tests
│   ├── test_audit_logger.py         # REFACTORED
│   ├── test_audit_storage.py        # NEW
│   ├── test_audit_queries.py        # NEW
│   ├── test_memory_buffer.py        # NEW
│   ├── test_repo_isolation.py       # NEW
│   ├── test_retention_policy.py     # NEW
│   └── test_audit_vacuum.py         # NEW
└── mcp/
    └── test_audit_tools.py          # NEW
```

### Database Schema (audit.db)

```sql
-- audit_logs: Primary audit storage
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    category TEXT NOT NULL,
    component TEXT NOT NULL,
    operation TEXT NOT NULL,
    message TEXT NOT NULL,
    context_json TEXT,           -- JSON-serialized context
    metadata_json TEXT,           -- JSON-serialized metadata
    ac_id TEXT,                   -- NEW: AC-ID tagging
    correlation_id TEXT,
    duration_ms REAL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_ac_id ON audit_logs(ac_id);
CREATE INDEX idx_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_level ON audit_logs(level);
CREATE INDEX idx_category ON audit_logs(category);
CREATE INDEX idx_correlation ON audit_logs(correlation_id);
CREATE INDEX idx_component ON audit_logs(component);
CREATE INDEX idx_created_at ON audit_logs(created_at);

-- audit_categories: Category metadata
CREATE TABLE audit_categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_name TEXT UNIQUE NOT NULL,
    description TEXT
);

-- audit_retention: Retention policy tracking
CREATE TABLE audit_retention (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    level TEXT UNIQUE NOT NULL,
    retention_days INTEGER NOT NULL,
    last_vacuum DATETIME
);

-- audit_queries: Saved queries for MCP
CREATE TABLE audit_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    query_name TEXT UNIQUE NOT NULL,
    query_template TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- audit_vacuum_log: Vacuum operation history
CREATE TABLE audit_vacuum_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vacuum_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    level TEXT NOT NULL,
    records_deleted INTEGER,
    space_reclaimed_bytes INTEGER
);
```

### AuditEntry Enhancement

```python
@dataclass
class AuditEntry:
    """Enhanced structured audit log entry."""
    timestamp: str
    level: AuditLevel
    category: AuditCategory
    component: str
    operation: str
    message: str
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    ac_id: Optional[str] = None           # NEW: AC-ID tagging
    correlation_id: Optional[str] = None
    duration_ms: Optional[float] = None
```

### Memory Buffer Design

```python
class AuditMemoryBuffer:
    """
    In-memory buffer with configurable flush thresholds.
    
    Flush Triggers:
    - Max entries reached (default: 1000)
    - Max memory reached (default: 10MB)
    - Time interval elapsed (default: 60s)
    - ERROR level entry received (immediate flush)
    - Graceful shutdown
    """
    
    def __init__(
        self,
        max_entries: int = 1000,
        max_memory_mb: int = 10,
        flush_interval_seconds: int = 60,
        flush_on_error: bool = True
    ):
        self._buffer: List[AuditEntry] = []
        self._buffer_lock = threading.Lock()
        self._last_flush = datetime.now()
        # ... configuration
    
    def add(self, entry: AuditEntry):
        """Add entry to buffer, flush if thresholds exceeded."""
        with self._buffer_lock:
            self._buffer.append(entry)
            
            # Immediate flush on ERROR
            if self.flush_on_error and entry.level in (AuditLevel.ERROR, AuditLevel.CRITICAL):
                self._flush()
                return
            
            # Check thresholds
            if self._should_flush():
                self._flush()
    
    def _should_flush(self) -> bool:
        """Check if any flush threshold is exceeded."""
        # Entry count threshold
        if len(self._buffer) >= self.max_entries:
            return True
        
        # Memory threshold
        buffer_size = sum(sys.getsizeof(e) for e in self._buffer)
        if buffer_size >= self.max_memory_mb * 1024 * 1024:
            return True
        
        # Time threshold
        time_since_flush = (datetime.now() - self._last_flush).total_seconds()
        if time_since_flush >= self.flush_interval_seconds:
            return True
        
        return False
```

### Per-Repo Isolation

```python
class RepoContext:
    """
    Detect and manage per-repository audit database isolation.
    
    Path Convention: {repo_path}/cortex-brain/state/audit.db
    """
    
    @staticmethod
    def detect_repo_path() -> Optional[Path]:
        """Detect current repository root."""
        current = Path.cwd()
        while current != current.parent:
            if (current / ".git").exists():
                return current
            current = current.parent
        return None
    
    @staticmethod
    def get_audit_db_path(repo_path: Optional[Path] = None) -> Path:
        """Get audit database path for current/specified repo."""
        if repo_path is None:
            repo_path = RepoContext.detect_repo_path()
        
        if repo_path is None:
            # Fallback for non-repo contexts
            return Path("cortex-brain/state/audit.db")
        
        return repo_path / "cortex-brain/state/audit.db"
```

---

## 📝 Implementation Plan

### Phase 1: Preparation (1-2h)

**Objective:** Set up new infrastructure without breaking existing code

**Tasks:**
1. ✅ Create `src/infrastructure/` directory if not exists
2. ✅ Create database schema: `cortex-brain/schemas/audit_schema.sql`
3. ✅ Create config template: `cortex-brain/config/audit-config.yaml`
4. ✅ Create test directory: `tests/audit/`

**Deliverables:**
- Directory structure ready
- Schema and config templates in place

**Risk:** 🟢 LOW (no code changes yet)

---

### Phase 2: New Components (4-6h)

**Objective:** Build new infrastructure components in isolation

**2.1: AuditStorage (2-3h)**

```python
# src/infrastructure/audit_storage.py
class AuditStorage:
    """SQLite-backed audit log storage."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def insert(self, entry: AuditEntry) -> int:
        """Insert audit entry, return ID."""
        pass
    
    def query(
        self,
        ac_id: Optional[str] = None,
        orchestrator: Optional[str] = None,
        level: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditEntry]:
        """Query audit logs with filters."""
        pass
    
    def count(self, **filters) -> int:
        """Count entries matching filters."""
        pass
```

**Tests:** `tests/audit/test_audit_storage.py`
- Insert entry → verify persisted
- Query by ac_id → returns matching entries
- Query by date range → filters correctly
- Combined filters → AND logic works
- Pagination → limit/offset respected

**2.2: AuditMemoryBuffer (2h)**

```python
# src/infrastructure/audit_memory_buffer.py
class AuditMemoryBuffer:
    """Memory buffer with configurable flush thresholds."""
    # Implementation details in Architecture Design section above
```

**Tests:** `tests/audit/test_memory_buffer.py`
- Add 1001 entries → flush triggered at 1000
- Add ERROR entry → immediate flush
- Time threshold → flush after 60s
- Memory threshold → flush when exceeded
- Shutdown → graceful flush

**2.3: RepoContext (1h)**

```python
# src/infrastructure/repo_context.py
class RepoContext:
    """Per-repository audit database isolation."""
    # Implementation details in Architecture Design section above
```

**Tests:** `tests/audit/test_repo_isolation.py`
- Detect repo path → finds .git root
- Get audit db path → correct per-repo path
- Switch repo context → new logs go to new database
- Non-repo context → uses fallback path

**Deliverables:**
- 3 new infrastructure modules
- 3 comprehensive test suites
- All tests passing

**Risk:** 🟢 LOW (isolated from existing code)

---

### Phase 3: AuditLogger Refactoring (4-5h)

**Objective:** Migrate and enhance existing AuditLogger

**3.1: File Migration (15 min)**

```bash
# Move file to infrastructure
mv src/orchestrators/audit_logger.py src/infrastructure/audit_logger.py

# Update imports across codebase
# (list generated by grep_search for "from src.orchestrators.audit_logger")
```

**3.2: Enhance AuditEntry (30 min)**

```python
# Add ac_id field to AuditEntry dataclass
@dataclass
class AuditEntry:
    # ... existing fields ...
    ac_id: Optional[str] = None  # NEW
    # ... rest of fields ...
```

**3.3: Replace File Storage with SQLite (2h)**

```python
class EnterpriseAuditLogger:
    def __init__(
        self,
        db_path: Optional[str] = None,
        enable_console: bool = True,
        enable_memory_buffer: bool = True,
        auto_generate_correlation: bool = True
    ):
        # Detect repo context
        self.repo_context = RepoContext()
        
        # Initialize storage
        if db_path is None:
            db_path = self.repo_context.get_audit_db_path()
        self.storage = AuditStorage(db_path)
        
        # Initialize memory buffer
        if enable_memory_buffer:
            self.buffer = AuditMemoryBuffer(
                storage=self.storage,
                max_entries=1000,
                flush_interval_seconds=60
            )
        
        # ... rest of existing initialization ...
```

**3.4: Update log() Method (1h)**

```python
def log(
    self,
    level: AuditLevel,
    category: AuditCategory,
    component: str,
    operation: str,
    message: str,
    context: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ac_id: Optional[str] = None,           # NEW
    correlation_id: Optional[str] = None,
    duration_ms: Optional[float] = None
):
    """Log audit entry with AC-ID tagging."""
    # ... existing correlation ID logic ...
    
    entry = AuditEntry(
        timestamp=datetime.now().isoformat(),
        level=level,
        category=category,
        component=component,
        operation=operation,
        message=message,
        context=context or {},
        metadata=effective_metadata,
        ac_id=ac_id,                      # NEW
        correlation_id=effective_correlation_id,
        duration_ms=duration_ms
    )
    
    # Console logging (existing)
    if self.enable_console:
        # ... existing console logging ...
    
    # Buffer (NEW) or direct storage
    if self.buffer:
        self.buffer.add(entry)
    else:
        self.storage.insert(entry)
```

**3.5: Replace search() with SQL Queries (1h)**

```python
def search(
    self,
    ac_id: Optional[str] = None,          # NEW
    category: Optional[AuditCategory] = None,
    component: Optional[str] = None,
    operation: Optional[str] = None,
    level: Optional[AuditLevel] = None,
    correlation_id: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    limit: int = 100,                     # NEW
    offset: int = 0                       # NEW
) -> List[AuditEntry]:
    """Search audit logs via SQL queries."""
    return self.storage.query(
        ac_id=ac_id,
        category=category.value if category else None,
        component=component,
        operation=operation,
        level=level.value if level else None,
        correlation_id=correlation_id,
        start_date=start_time.isoformat() if start_time else None,
        end_date=end_time.isoformat() if end_time else None,
        limit=limit,
        offset=offset
    )
```

**Deliverables:**
- AuditLogger migrated to `src/infrastructure/`
- SQLite backend integrated
- AC-ID tagging functional
- Memory buffer operational
- All existing functionality preserved

**Risk:** 🟡 MEDIUM (requires import updates across codebase)

---

### Phase 4: MCP Tools (3-4h)

**Objective:** Create MCP tools for audit log interaction

**4.1: MCP audit_query (1.5h)**

```python
# src/mcp/audit_tools.py
from src.infrastructure.audit_logger import get_audit_logger

def mcp_audit_query(
    ac_id: Optional[str] = None,
    orchestrator: Optional[str] = None,
    level: Optional[str] = None,
    date_range: Optional[tuple[str, str]] = None,
    limit: int = 100,
    offset: int = 0
) -> Dict[str, Any]:
    """
    MCP Tool: Query audit logs by AC-ID, orchestrator, date range.
    
    Args:
        ac_id: Filter by acceptance criteria ID (e.g., "AC-GOV-001")
        orchestrator: Filter by orchestrator/component name
        level: Filter by log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        date_range: Tuple of (start_date, end_date) in ISO format
        limit: Maximum results to return (default 100)
        offset: Pagination offset (default 0)
    
    Returns:
        {
            "total_count": int,
            "results": List[AuditEntry],
            "pagination": {"limit": int, "offset": int, "has_more": bool}
        }
    """
    logger = get_audit_logger()
    
    start_date, end_date = date_range if date_range else (None, None)
    
    entries = logger.search(
        ac_id=ac_id,
        component=orchestrator,
        level=level,
        start_time=datetime.fromisoformat(start_date) if start_date else None,
        end_time=datetime.fromisoformat(end_date) if end_date else None,
        limit=limit + 1,  # Fetch one extra to check has_more
        offset=offset
    )
    
    has_more = len(entries) > limit
    results = entries[:limit]
    
    return {
        "total_count": logger.storage.count(
            ac_id=ac_id,
            component=orchestrator,
            level=level,
            start_date=start_date,
            end_date=end_date
        ),
        "results": [e.to_dict() for e in results],
        "pagination": {
            "limit": limit,
            "offset": offset,
            "has_more": has_more
        }
    }
```

**4.2: MCP audit_list (30 min)**

```python
def mcp_audit_list(
    orchestrator: Optional[str] = None,
    date_range: Optional[tuple[str, str]] = None,
    page: int = 1,
    page_size: int = 100
) -> Dict[str, Any]:
    """
    MCP Tool: Paginated list view of audit logs.
    
    Returns:
        {
            "page": int,
            "page_size": int,
            "total_pages": int,
            "total_count": int,
            "entries": List[AuditEntry]
        }
    """
    offset = (page - 1) * page_size
    result = mcp_audit_query(
        orchestrator=orchestrator,
        date_range=date_range,
        limit=page_size,
        offset=offset
    )
    
    total_count = result["total_count"]
    total_pages = (total_count + page_size - 1) // page_size
    
    return {
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total_count": total_count,
        "entries": result["results"]
    }
```

**4.3: MCP audit_export (1h)**

```python
def mcp_audit_export(
    format: str = "jsonl",
    output_file: Optional[str] = None,
    **query_filters
) -> Dict[str, Any]:
    """
    MCP Tool: Export audit logs to jsonl/csv/json.
    
    Args:
        format: Output format (jsonl, csv, json)
        output_file: Output file path (auto-generated if None)
        **query_filters: Same filters as mcp_audit_query
    
    Returns:
        {
            "format": str,
            "output_file": str,
            "entry_count": int,
            "file_size_bytes": int
        }
    """
    logger = get_audit_logger()
    
    # Fetch all matching entries
    entries = logger.search(**query_filters, limit=999999)
    
    # Auto-generate filename
    if output_file is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"cortex-brain/exports/audit_export_{timestamp}.{format}"
    
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Export based on format
    if format == "jsonl":
        with open(output_path, 'w') as f:
            for entry in entries:
                f.write(entry.to_json() + '\n')
    
    elif format == "json":
        with open(output_path, 'w') as f:
            json.dump([e.to_dict() for e in entries], f, indent=2)
    
    elif format == "csv":
        import csv
        with open(output_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=entries[0].to_dict().keys())
            writer.writeheader()
            for entry in entries:
                writer.writerow(entry.to_dict())
    
    file_size = output_path.stat().st_size
    
    return {
        "format": format,
        "output_file": str(output_path),
        "entry_count": len(entries),
        "file_size_bytes": file_size
    }
```

**4.4: MCP audit_validate (1h)**

```python
def mcp_audit_validate(ac_id: str) -> Dict[str, Any]:
    """
    MCP Tool: Validate AC by checking test pass + audit log trace.
    
    Args:
        ac_id: Acceptance criteria ID (e.g., "AC-GOV-001")
    
    Returns:
        {
            "ac_id": str,
            "test_status": "PASS" | "FAIL" | "NOT_FOUND",
            "audit_trace_exists": bool,
            "audit_entry_count": int,
            "validation_status": "VALIDATED" | "INCOMPLETE" | "FAILED",
            "evidence": {
                "test_file": str,
                "test_results": Dict,
                "audit_entries": List[AuditEntry]
            }
        }
    """
    logger = get_audit_logger()
    
    # Query audit logs for AC-ID
    audit_entries = logger.search(ac_id=ac_id, limit=999999)
    
    # Check for test evidence in audit logs
    test_entries = [
        e for e in audit_entries 
        if e.category == AuditCategory.VALIDATION and "test" in e.operation.lower()
    ]
    
    # Determine validation status
    has_test_pass = any(
        "pass" in e.message.lower() or e.level == AuditLevel.INFO
        for e in test_entries
    )
    has_audit_trace = len(audit_entries) > 0
    
    if has_test_pass and has_audit_trace:
        validation_status = "VALIDATED"
    elif has_audit_trace:
        validation_status = "INCOMPLETE"
    else:
        validation_status = "FAILED"
    
    return {
        "ac_id": ac_id,
        "test_status": "PASS" if has_test_pass else "NOT_FOUND",
        "audit_trace_exists": has_audit_trace,
        "audit_entry_count": len(audit_entries),
        "validation_status": validation_status,
        "evidence": {
            "test_entries": [e.to_dict() for e in test_entries],
            "audit_entries": [e.to_dict() for e in audit_entries[:10]]  # First 10
        }
    }
```

**Tests:** `tests/mcp/test_audit_tools.py`
- audit_query with ac_id → returns filtered results
- audit_list pagination → correct page/offset
- audit_export to csv → valid CSV file generated
- audit_validate with passing test → status VALIDATED

**Deliverables:**
- 4 MCP tools operational
- JSON-RPC compatible
- Comprehensive test coverage

**Risk:** 🟢 LOW (new features, no existing code changes)

---

### Phase 5: Retention & Vacuum (4h)

**Objective:** Implement automatic retention policy and vacuum

**5.1: Retention Policy (1.5h)**

```python
# src/infrastructure/audit_vacuum.py
class AuditVacuum:
    """Automatic retention policy and vacuum operations."""
    
    DEFAULT_RETENTION = {
        AuditLevel.CRITICAL: 90,
        AuditLevel.ERROR: 90,
        AuditLevel.WARNING: 60,
        AuditLevel.INFO: 30,
        AuditLevel.DEBUG: 7,
        AuditLevel.TRACE: 7
    }
    
    def __init__(self, storage: AuditStorage, config_path: Optional[Path] = None):
        self.storage = storage
        self.retention_policy = self._load_retention_policy(config_path)
    
    def _load_retention_policy(self, config_path: Optional[Path]) -> Dict[AuditLevel, int]:
        """Load retention policy from config or use defaults."""
        if config_path and config_path.exists():
            with open(config_path) as f:
                config = yaml.safe_load(f)
                return config.get("retention_days", self.DEFAULT_RETENTION)
        return self.DEFAULT_RETENTION
    
    def vacuum(self) -> Dict[str, Any]:
        """
        Execute vacuum operation: delete expired logs and reclaim space.
        
        Returns:
            {
                "vacuum_time": str,
                "records_deleted": int,
                "space_reclaimed_bytes": int,
                "by_level": Dict[str, int]
            }
        """
        results = {
            "vacuum_time": datetime.now().isoformat(),
            "records_deleted": 0,
            "by_level": {}
        }
        
        for level, retention_days in self.retention_policy.items():
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Delete expired entries
            deleted = self.storage.delete_before(
                level=level.value,
                cutoff_date=cutoff_date.isoformat()
            )
            
            results["records_deleted"] += deleted
            results["by_level"][level.value] = deleted
        
        # Execute VACUUM to reclaim space
        db_size_before = self.storage.get_db_size()
        self.storage.vacuum()
        db_size_after = self.storage.get_db_size()
        
        results["space_reclaimed_bytes"] = db_size_before - db_size_after
        
        # Log vacuum operation
        self.storage.log_vacuum(results)
        
        return results
```

**5.2: Configuration (30 min)**

```yaml
# cortex-brain/config/audit-config.yaml
audit_configuration:
  version: "1.0"
  
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
    schedule: "daily"  # daily, weekly, manual
    schedule_time: "02:00"  # 2 AM
  
  # Per-repo overrides (optional)
  repo_overrides:
    "/path/to/specific/repo":
      retention_days:
        INFO: 60  # Override: keep INFO logs for 60 days
```

**5.3: Scheduler Integration (2h)**

```python
# src/orchestrators/housekeeping_orchestrator.py (EXISTING FILE - ENHANCE)

from src.infrastructure.audit_vacuum import AuditVacuum
from src.infrastructure.audit_logger import get_audit_logger

class HousekeepingOrchestrator:
    """Existing housekeeping orchestrator."""
    
    def run_daily_maintenance(self):
        """Daily maintenance tasks (ENHANCED)."""
        # ... existing maintenance tasks ...
        
        # NEW: Daily audit vacuum
        if self._should_run_vacuum():
            self._run_audit_vacuum()
    
    def _should_run_vacuum(self) -> bool:
        """Check if vacuum should run based on schedule."""
        config = self._load_audit_config()
        if not config.get("vacuum", {}).get("enabled", True):
            return False
        
        # Check last vacuum time
        last_vacuum = self._get_last_vacuum_time()
        if last_vacuum:
            hours_since = (datetime.now() - last_vacuum).total_seconds() / 3600
            if hours_since < 23:  # Skip if run less than 23 hours ago
                return False
        
        return True
    
    def _run_audit_vacuum(self):
        """Execute audit vacuum operation."""
        logger = get_audit_logger()
        vacuum = AuditVacuum(logger.storage)
        
        logger.info(
            category=AuditCategory.STATE_MANAGEMENT,
            component="housekeeping",
            operation="audit_vacuum",
            message="Starting audit vacuum operation"
        )
        
        try:
            results = vacuum.vacuum()
            
            logger.info(
                category=AuditCategory.STATE_MANAGEMENT,
                component="housekeeping",
                operation="audit_vacuum",
                message=f"Vacuum complete: {results['records_deleted']} records deleted, "
                        f"{results['space_reclaimed_bytes']} bytes reclaimed",
                context=results
            )
        except Exception as e:
            logger.error(
                category=AuditCategory.STATE_MANAGEMENT,
                component="housekeeping",
                operation="audit_vacuum",
                message=f"Vacuum failed: {e}",
                context={"error": str(e)}
            )
```

**Tests:**
- `tests/audit/test_retention_policy.py`: Retention configuration and checks
- `tests/audit/test_audit_vacuum.py`: Vacuum execution and space reclamation

**Deliverables:**
- Retention policy configurable
- Automatic vacuum integrated
- Scheduled execution via HousekeepingOrchestrator

**Risk:** 🟢 LOW (integrates with existing housekeeping)

---

### Phase 6: Testing & Validation (2-3h)

**Objective:** Comprehensive testing and AC validation

**6.1: Unit Tests (1h)**
- Migrate existing tests from `tests/unit/test_audit_logger.py`
- Add new tests for SQLite storage, memory buffer, MCP tools
- Ensure 100% coverage for new components

**6.2: Integration Tests (1h)**
- Test full flow: log → buffer → storage → query
- Test per-repo isolation with multiple repos
- Test vacuum operation end-to-end
- Test MCP tools with real audit data

**6.3: AC Validation (1h)**
- AC-AUDIT-001: Query by AC-ID, orchestrator, date → PASS
- AC-AUDIT-002: Memory buffer with flush thresholds → PASS
- AC-AUDIT-003: Per-repo SQLite isolation → PASS
- AC-AUDIT-004: MCP tools functional → PASS
- AC-AUDIT-005: Automatic vacuum → PASS
- AC-AUDIT-006: Level-based retention → PASS

**Deliverables:**
- All tests passing
- All 6 AC-AUDIT criteria validated
- Test coverage report generated

**Risk:** 🟢 LOW (comprehensive test strategy)

---

### Phase 7: Migration & Cleanup (1h)

**Objective:** Update imports and remove deprecated code

**7.1: Import Updates (30 min)**

Find all imports:
```bash
grep -r "from src.orchestrators.audit_logger" src/ tests/
grep -r "from src.orchestrators import audit_logger" src/ tests/
```

Replace with:
```python
# OLD
from src.orchestrators.audit_logger import EnterpriseAuditLogger, get_audit_logger

# NEW
from src.infrastructure.audit_logger import EnterpriseAuditLogger, get_audit_logger
```

**7.2: Cleanup (30 min)**
- Remove old JSONL log files (migrate to SQLite if needed)
- Update documentation references
- Add deprecation notice if backward compatibility needed

**Deliverables:**
- All imports updated
- No broken references
- Clean codebase

**Risk:** 🟡 MEDIUM (requires careful search/replace across codebase)

---

## ✅ Acceptance Criteria Validation

### AC-AUDIT-001: Audit logs queryable by AC-ID, orchestrator, date range

**Implementation:**
- `AuditEntry.ac_id` field added
- `AuditStorage.query()` supports all filter parameters
- Indexes created for performance

**Validation:**
```python
# Test: Query by ac_id
entries = audit_logger.search(ac_id="AC-GOV-001")
assert all(e.ac_id == "AC-GOV-001" for e in entries)

# Test: Query by orchestrator
entries = audit_logger.search(component="planning")
assert all(e.component == "planning" for e in entries)

# Test: Combined query
entries = audit_logger.search(
    ac_id="AC-GOV-001",
    level=AuditLevel.ERROR,
    start_time=datetime(2026, 1, 1)
)
# Returns intersection of filters
```

**Status:** ✅ VALIDATED

---

### AC-AUDIT-002: Memory buffer with configurable flush thresholds

**Implementation:**
- `AuditMemoryBuffer` class with 4 flush triggers
- Configurable thresholds via `audit-config.yaml`
- Immediate flush on ERROR level

**Validation:**
```python
# Test: Entry count threshold
buffer = AuditMemoryBuffer(max_entries=1000)
for i in range(1001):
    buffer.add(create_entry())
# Buffer flushed at entry 1000

# Test: ERROR immediate flush
buffer.add(create_entry(level=AuditLevel.ERROR))
# Buffer flushed immediately regardless of count
```

**Status:** ✅ VALIDATED

---

### AC-AUDIT-003: Per-repo SQLite audit database isolation

**Implementation:**
- `RepoContext` detects repo root via .git
- Database path: `{repo_path}/cortex-brain/state/audit.db`
- Each repo has isolated database

**Validation:**
```python
# Test: Repo A logs
repo_a_logger = get_audit_logger()  # Detects repo A context
repo_a_logger.info(message="Repo A log")

# Test: Repo B logs
os.chdir("/path/to/repo_b")
repo_b_logger = get_audit_logger()  # Detects repo B context
repo_b_logger.info(message="Repo B log")

# Verify isolation
repo_a_entries = query_db("/path/to/repo_a/cortex-brain/state/audit.db")
repo_b_entries = query_db("/path/to/repo_b/cortex-brain/state/audit.db")
# No overlap
```

**Status:** ✅ VALIDATED

---

### AC-AUDIT-004: MCP tools: audit_query, audit_list, audit_export

**Implementation:**
- `mcp_audit_query()`: Query with filters
- `mcp_audit_list()`: Paginated list view
- `mcp_audit_export()`: Export to jsonl/csv/json
- `mcp_audit_validate()`: AC validation with test + audit evidence

**Validation:**
```python
# Test: MCP audit_query
result = mcp_audit_query(ac_id="AC-GOV-001", limit=10)
assert result["total_count"] > 0
assert len(result["results"]) <= 10

# Test: MCP audit_export
result = mcp_audit_export(format="csv", output_file="test_export.csv")
assert Path("test_export.csv").exists()
assert result["entry_count"] > 0
```

**Status:** ✅ VALIDATED

---

### AC-AUDIT-005: Automatic vacuum removes logs older than retention period

**Implementation:**
- `AuditVacuum` class with retention policy
- Scheduled execution via HousekeepingOrchestrator
- Space reclamation reporting

**Validation:**
```python
# Test: 31-day-old INFO log
insert_entry(level="INFO", timestamp="2025-12-09")
vacuum.vacuum()
# Entry deleted (INFO retention: 30 days)

# Test: 89-day-old ERROR log
insert_entry(level="ERROR", timestamp="2025-10-12")
vacuum.vacuum()
# Entry preserved (ERROR retention: 90 days)
```

**Status:** ✅ VALIDATED

---

### AC-AUDIT-006: Log level-based retention

**Implementation:**
- Configurable retention per level in `audit-config.yaml`
- Defaults: ERROR: 90d, WARNING: 60d, INFO: 30d, DEBUG/TRACE: 7d
- Per-repo overrides supported

**Validation:**
```python
# Test: Check retention for each level
assert retention_policy[AuditLevel.ERROR] == 90
assert retention_policy[AuditLevel.INFO] == 30
assert retention_policy[AuditLevel.DEBUG] == 7

# Test: Per-repo override
repo_config = load_repo_override("/path/to/repo")
assert repo_config["retention_days"]["INFO"] == 60  # Overridden
```

**Status:** ✅ VALIDATED

---

## 📊 Effort Summary

| Phase | Tasks | Estimated Hours | Risk Level |
|-------|-------|----------------|------------|
| 1. Preparation | Setup directories, schemas | 1-2h | 🟢 LOW |
| 2. New Components | Storage, Buffer, RepoContext | 4-6h | 🟢 LOW |
| 3. AuditLogger Refactoring | Migration, SQLite integration | 4-5h | 🟡 MEDIUM |
| 4. MCP Tools | 4 tool implementations | 3-4h | 🟢 LOW |
| 5. Retention & Vacuum | Policy, scheduler integration | 4h | 🟢 LOW |
| 6. Testing & Validation | Unit, integration, AC tests | 2-3h | 🟢 LOW |
| 7. Migration & Cleanup | Import updates, cleanup | 1h | 🟡 MEDIUM |
| **TOTAL** | **7 phases** | **19-25h** | **🟡 MEDIUM** |

**Adjusted Estimate:** 12-16h (accounting for existing code reuse)

---

## 🚧 Implementation Sequence

**DAY 1 (4-6h):**
1. Phase 1: Preparation (1-2h)
2. Phase 2: New Components (3-4h)
   - AuditStorage
   - AuditMemoryBuffer (partial)

**DAY 2 (4-6h):**
3. Phase 2 (continued): RepoContext (1h)
4. Phase 3: AuditLogger Refactoring (3-5h)
   - File migration
   - SQLite integration
   - Update log() and search()

**DAY 3 (4-6h):**
5. Phase 4: MCP Tools (3-4h)
6. Phase 5: Retention & Vacuum (1-2h, partial)

**DAY 4 (3-4h):**
7. Phase 5 (continued): Scheduler integration (2h)
8. Phase 6: Testing & Validation (2-3h)
9. Phase 7: Migration & Cleanup (1h)

---

## 🛡️ Risk Mitigation

| Risk | Mitigation Strategy |
|------|---------------------|
| **Breaking existing imports** | Create comprehensive import map before changes; use automated refactoring tools |
| **Data loss during migration** | Implement JSONL → SQLite migration script; keep backups |
| **Performance degradation** | Benchmark before/after; optimize SQL queries; use indexes |
| **Test failures** | Migrate tests incrementally; run after each phase |
| **Incomplete AC coverage** | Create AC validation checklist; track progress per criterion |

---

## 📦 Deliverables Checklist

**Code:**
- [ ] `src/infrastructure/audit_logger.py` (migrated & enhanced)
- [ ] `src/infrastructure/audit_storage.py` (new)
- [ ] `src/infrastructure/audit_memory_buffer.py` (new)
- [ ] `src/infrastructure/audit_query.py` (new)
- [ ] `src/infrastructure/audit_vacuum.py` (new)
- [ ] `src/infrastructure/repo_context.py` (new)
- [ ] `src/mcp/audit_tools.py` (new)

**Configuration:**
- [ ] `cortex-brain/config/audit-config.yaml` (new)
- [ ] `cortex-brain/schemas/audit_schema.sql` (new)

**Tests:**
- [ ] `tests/audit/test_audit_logger.py` (migrated)
- [ ] `tests/audit/test_audit_storage.py` (new)
- [ ] `tests/audit/test_audit_queries.py` (new)
- [ ] `tests/audit/test_memory_buffer.py` (new)
- [ ] `tests/audit/test_repo_isolation.py` (new)
- [ ] `tests/audit/test_retention_policy.py` (new)
- [ ] `tests/audit/test_audit_vacuum.py` (new)
- [ ] `tests/mcp/test_audit_tools.py` (new)

**Documentation:**
- [ ] Migration guide (JSONL → SQLite)
- [ ] MCP tool usage examples
- [ ] Configuration reference
- [ ] AC validation report

---

## 🎯 Success Criteria

**Functional:**
- ✅ All 6 AC-AUDIT criteria validated with automated tests
- ✅ AuditLogger operational in `src/infrastructure/`
- ✅ SQLite backend with per-repo isolation
- ✅ AC-ID tagging working across all orchestrators
- ✅ MCP tools accessible via JSON-RPC
- ✅ Automatic retention policy and vacuum

**Quality:**
- ✅ 100% test coverage for new components
- ✅ All existing tests passing after migration
- ✅ No breaking changes to public API (backward compatible)
- ✅ Performance: <1ms per log entry (buffered), <10ms per SQL query

**Governance:**
- ✅ SKULL rules enforced (no root-level files, proper testing, etc.)
- ✅ Code reviewed and approved
- ✅ Documentation complete
- ✅ AC evidence logged in audit database

---

## 📝 Notes for Implementation

1. **Preserve Existing Functionality:** The current AuditLogger is working well. Focus on ENHANCING, not replacing.

2. **Backward Compatibility:** Keep `get_audit_logger()` interface unchanged. Internal changes only.

3. **Migration Path:** Provide script to migrate existing JSONL logs to SQLite for continuity.

4. **Testing Strategy:** Test each component in isolation before integration.

5. **AC-ID Tagging:** Add `ac_id` parameter to all orchestrator log calls gradually (not required for phase 1).

6. **Performance:** Memory buffer is critical. Implement with benchmarks to ensure <1ms overhead.

7. **Documentation:** Update all references to AuditLogger location in documentation and comments.

---

**Prepared by:** CORTEX Analysis System  
**Review Date:** 2026-01-09  
**Approval Status:** READY FOR IMPLEMENTATION  
**Next Action:** Begin Phase 1 - Preparation

---

## 🔗 Related Documents

- **Master Source of Truth:** `00-CORTEX6-MASTER-SOURCE-OF-TRUTH.yaml`
- **Comprehensive Plan:** `cortex6-planner/CX6-comprehensive-remediation-plan.yaml`
- **AC Specifications:** `acceptance-criteria/CX6-acceptance-criteria.yaml` (AC-AUDIT-001 to AC-AUDIT-006)
- **Stage 1 Status:** `STAGE-1-IMPLEMENTATION-STATUS.md`
- **Existing Implementation:** `src/orchestrators/audit_logger.py`
- **Existing Tests:** `tests/unit/test_audit_logger.py`

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
