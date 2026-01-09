# AUDIT-001 Implementation Workflow

**Visual Guide for CORTEX 6.0 Stage 1 Foundation**

---

## 🗺️ Overall Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUDIT-001 REFACTORING                        │
│                                                                 │
│  Current: src/orchestrators/audit_logger.py (1133 lines)      │
│           ↓ REFACTOR (not rewrite)                            │
│  Target:  src/infrastructure/ + SQLite + MCP                   │
│                                                                 │
│  Preservation: 85% of existing code                            │
│  New Work: SQLite, AC-ID, MCP, Retention                       │
│  Effort: 12-16 hours                                           │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 7-Phase Implementation

```
┌──────────────┐
│  PHASE 1     │  Preparation (1-2h)
│  Setup       │  • Create directories
└──────┬───────┘  • Create schemas
       │          • Create config
       ↓
┌──────────────┐
│  PHASE 2     │  New Components (4-6h)
│  Build       │  • AuditStorage (SQLite)
└──────┬───────┘  • AuditMemoryBuffer
       │          • RepoContext
       │          • Tests for each
       ↓
┌──────────────┐
│  PHASE 3     │  AuditLogger Refactoring (4-5h)
│  Migrate     │  • Move to infrastructure/
└──────┬───────┘  • Add ac_id field
       │          • Replace JSONL with SQLite
       │          • Integrate memory buffer
       │          • Update search() method
       ↓
┌──────────────┐
│  PHASE 4     │  MCP Tools (3-4h)
│  Extend      │  • mcp_audit_query
└──────┬───────┘  • mcp_audit_list
       │          • mcp_audit_export
       │          • mcp_audit_validate
       ↓
┌──────────────┐
│  PHASE 5     │  Retention & Vacuum (4h)
│  Automate    │  • AuditVacuum class
└──────┬───────┘  • Retention policy
       │          • Scheduler integration
       ↓
┌──────────────┐
│  PHASE 6     │  Testing & Validation (2-3h)
│  Validate    │  • Unit tests (8 files)
└──────┬───────┘  • Integration tests
       │          • AC validation
       ↓
┌──────────────┐
│  PHASE 7     │  Migration & Cleanup (1h)
│  Finalize    │  • Update imports
└──────┬───────┘  • Remove old JSONL files
       │          • Update docs
       ↓
  ┌────────┐
  │ DONE ✅ │  All 6 AC-AUDIT validated
  └────────┘  354+ AC now validatable
```

---

## 🏗️ Architecture Transformation

### Before (Current State)

```
┌─────────────────────────────────────────────┐
│  src/orchestrators/audit_logger.py          │
│  ┌─────────────────────────────────────┐   │
│  │ EnterpriseAuditLogger               │   │
│  │ • log() → writes to JSONL files     │   │
│  │ • search() → scans JSONL files      │   │
│  │ • correlation tracking              │   │
│  │ • error analysis                    │   │
│  │ • performance metrics               │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────┐
│  cortex-brain/audit-logs/                   │
│  • state_management.jsonl                   │
│  • execution.jsonl                          │
│  • middleware.jsonl                         │
│  • ... (7 category files)                   │
└─────────────────────────────────────────────┘
```

### After (Target State)

```
┌─────────────────────────────────────────────────────────────────┐
│  src/infrastructure/                                            │
│  ┌────────────────────────────────────────────────────────┐   │
│  │ audit_logger.py (MIGRATED + ENHANCED)                  │   │
│  │ • log() → writes to memory buffer                      │   │
│  │ • search() → SQL queries                               │   │
│  │ • correlation tracking (preserved)                     │   │
│  │ • error analysis (preserved)                           │   │
│  │ • performance metrics (preserved)                      │   │
│  │ • AC-ID tagging (NEW)                                  │   │
│  └────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌────────────────┐  ┌────────────────┐  ┌─────────────────┐ │
│  │ audit_storage  │  │ audit_memory   │  │ repo_context    │ │
│  │ (SQLite)       │  │ _buffer        │  │ (per-repo)      │ │
│  └────────────────┘  └────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  cortex-brain/state/audit.db (per repository)                   │
│  ┌────────────┬──────────────┬──────────────┬────────────────┐ │
│  │ audit_logs │ audit_       │ audit_       │ audit_vacuum_  │ │
│  │            │ categories   │ retention    │ log            │ │
│  └────────────┴──────────────┴──────────────┴────────────────┘ │
│                                                                 │
│  • Indexed by: ac_id, timestamp, level, category, correlation  │
│  • Queryable: filters, pagination, ordering                    │
│  • Isolated: one database per repository                       │
└─────────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│  src/mcp/audit_tools.py (NEW)                                   │
│  ┌──────────────┬─────────────┬──────────────┬──────────────┐ │
│  │ audit_query  │ audit_list  │ audit_export │ audit_       │ │
│  │              │             │              │ validate     │ │
│  └──────────────┴─────────────┴──────────────┴──────────────┘ │
│                                                                 │
│  • JSON-RPC compatible                                          │
│  • AC validation with evidence                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔀 Data Flow Transformation

### Current Flow (JSONL)

```
┌──────────────┐
│ Orchestrator │
└──────┬───────┘
       │ log(level, category, component, operation, message)
       ↓
┌──────────────────────┐
│ EnterpriseAuditLogger│
│ • Generate entry     │
│ • Console output     │
└──────┬───────────────┘
       │ write_to_file()
       ↓
┌───────────────────────┐
│ category_file.jsonl   │
│ • Append JSON line    │
│ • No indexes          │
│ • Linear scan search  │
└───────────────────────┘
```

### Target Flow (SQLite + Buffer)

```
┌──────────────┐
│ Orchestrator │
└──────┬───────┘
       │ log(level, category, component, operation, message, ac_id)
       │                                                      ↑ NEW
       ↓
┌───────────────────────────────────────────────────────┐
│ EnterpriseAuditLogger                                 │
│ • Generate entry (with ac_id)                         │
│ • Console output                                      │
│ • Detect repo context                                 │
└──────┬────────────────────────────────────────────────┘
       │ buffer.add()
       ↓
┌──────────────────────────┐     Flush Triggers:
│ AuditMemoryBuffer        │     • Count (1000)
│ • In-memory queue        │     • Memory (10MB)
│ • Check thresholds       │ ────• Time (60s)
│ • Immediate on ERROR     │     • ERROR level
└──────┬───────────────────┘
       │ storage.insert_batch()
       ↓
┌────────────────────────────────────────────────────┐
│ AuditStorage (SQLite)                              │
│ • INSERT with transaction                          │
│ • 7 indexes for fast queries                       │
│ • Per-repo isolation                               │
└──────┬─────────────────────────────────────────────┘
       │
       ↓
┌────────────────────────────────────────────────────┐
│ {repo_path}/cortex-brain/state/audit.db            │
│                                                    │
│ SELECT * FROM audit_logs                           │
│ WHERE ac_id = 'AC-GOV-001'                         │
│   AND level = 'ERROR'                              │
│   AND timestamp BETWEEN '2026-01-01' AND '2026-01-09' │
│ ORDER BY timestamp DESC                            │
│ LIMIT 100 OFFSET 0;                                │
│                                                    │
│ [Uses indexes for fast query]                      │
└────────────────────────────────────────────────────┘
```

---

## 🎯 AC-ID Tagging Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Test Execution (any orchestrator)                          │
└──────┬──────────────────────────────────────────────────────┘
       │
       │ test_planning_validation()
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│  Audit Logger Called                                         │
│  audit_logger.log(                                           │
│      category=AuditCategory.VALIDATION,                      │
│      component="test_runner",                                │
│      operation="test_pass",                                  │
│      message="AC-GOV-001 validation test passed",            │
│      ac_id="AC-GOV-001"  ← AC-ID tagged                      │
│  )                                                           │
└──────┬──────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│  Stored in SQLite with ac_id='AC-GOV-001'                   │
└──────┬──────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│  Later: Query all evidence for AC-GOV-001                   │
│                                                              │
│  entries = audit_logger.search(ac_id="AC-GOV-001")          │
│  # Returns ALL audit entries tagged with AC-GOV-001:        │
│  #   - Test executions                                      │
│  #   - Planning operations                                  │
│  #   - Validation checks                                    │
│  #   - Error traces                                         │
└─────────────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│  AC Validation with Evidence                                │
│                                                              │
│  result = mcp_audit_validate(ac_id="AC-GOV-001")            │
│  # Returns:                                                 │
│  # {                                                        │
│  #   "validation_status": "VALIDATED",                      │
│  #   "test_status": "PASS",                                 │
│  #   "audit_trace_exists": true,                            │
│  #   "evidence": {...}                                      │
│  # }                                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## 🗄️ Per-Repo Isolation

```
┌────────────────────────────────────────────────────────────┐
│  Multi-Repository Deployment                               │
└────────────────────────────────────────────────────────────┘

Repository A:                    Repository B:
/path/to/repo-a/                /path/to/repo-b/
├── .git/                       ├── .git/
├── cortex-brain/               ├── cortex-brain/
│   └── state/                  │   └── state/
│       └── audit.db ───────────┼──X──── audit.db
│                               │       ↑
│   [Isolated Database A]       │   [Isolated Database B]
│                               │
│   • Logs from repo A only     │   • Logs from repo B only
│   • No cross-contamination    │   • Independent retention
└───────────────────────────────┴───────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│  RepoContext Detection                                      │
│                                                             │
│  1. AuditLogger.__init__()                                  │
│  2. RepoContext.detect_repo_path()                          │
│     → Walks up directories looking for .git/               │
│  3. RepoContext.get_audit_db_path(repo_path)                │
│     → Returns: {repo_path}/cortex-brain/state/audit.db     │
│  4. AuditStorage(db_path)                                   │
│     → Opens/creates database for THIS repo only            │
└─────────────────────────────────────────────────────────────┘

Admin Query Capability (optional):
┌─────────────────────────────────────────────────────────────┐
│  Cross-Repo Audit Query (Admin Tools Only)                 │
│                                                             │
│  admin_audit_query(                                         │
│      repos=["/path/to/repo-a", "/path/to/repo-b"],         │
│      ac_id="AC-GOV-001"                                     │
│  )                                                          │
│  → Opens multiple databases and aggregates results         │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔄 Memory Buffer Flush Logic

```
┌─────────────────────────────────────────────────────────────┐
│  AuditMemoryBuffer State Machine                           │
└─────────────────────────────────────────────────────────────┘

┌──────────┐
│  EMPTY   │
└────┬─────┘
     │ add(entry)
     ↓
┌──────────┐         Check Thresholds:
│ BUFFERING│ ────┐   1. entries >= max_entries (1000)?
└────┬─────┘     │   2. memory >= max_memory_mb (10MB)?
     │           │   3. time >= flush_interval (60s)?
     │ add(entry)│   4. entry.level == ERROR?
     ↓           │
┌──────────┐     │   Any TRUE?
│ BUFFERING│ ────┘      ↓ YES
└────┬─────┘            │
     │                  │
     ↓ NO               ↓
     │           ┌──────────┐
     │           │ FLUSHING │
     │           └────┬─────┘
     │                │
     │                │ storage.insert_batch()
     │                │
     │                ↓
     │           ┌──────────┐
     │           │  EMPTY   │
     │           └──────────┘
     │                ↑
     └────────────────┘

Special Case: ERROR Level
┌──────────┐
│  entry   │
│ level=   │
│  ERROR   │
└────┬─────┘
     │ IMMEDIATE FLUSH (bypass buffer)
     ↓
┌──────────────┐
│ storage.     │
│ insert()     │
└──────────────┘
```

---

## 🔧 MCP Tools Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  MCP Tools Layer                                            │
│  (JSON-RPC 2.0 Compatible)                                  │
└─────────────────────────────────────────────────────────────┘

┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐
│ mcp_audit_    │  │ mcp_audit_    │  │ mcp_audit_    │  │ mcp_audit_    │
│ query         │  │ list          │  │ export        │  │ validate      │
│               │  │               │  │               │  │               │
│ • Filters     │  │ • Pagination  │  │ • Format:     │  │ • Test check  │
│ • Pagination  │  │ • Date range  │  │   jsonl/csv/  │  │ • Audit check │
│ • Ordering    │  │ • Orchestrator│  │   json        │  │ • Evidence    │
└───────┬───────┘  └───────┬───────┘  └───────┬───────┘  └───────┬───────┘
        │                  │                  │                  │
        └──────────────────┴──────────────────┴──────────────────┘
                                   ↓
        ┌──────────────────────────────────────────────────────┐
        │  EnterpriseAuditLogger                               │
        │  • search()                                          │
        │  • get_trace()                                       │
        │  • export_session()                                  │
        └────────────────────────┬─────────────────────────────┘
                                 ↓
        ┌──────────────────────────────────────────────────────┐
        │  AuditStorage (SQLite)                               │
        │  • query()                                           │
        │  • count()                                           │
        │  • export()                                          │
        └──────────────────────────────────────────────────────┘

Usage Example:
┌─────────────────────────────────────────────────────────────┐
│ # Query via MCP                                             │
│ {                                                           │
│   "jsonrpc": "2.0",                                         │
│   "method": "mcp_audit_query",                              │
│   "params": {                                               │
│     "ac_id": "AC-GOV-001",                                  │
│     "level": "ERROR",                                       │
│     "date_range": ["2026-01-01", "2026-01-09"],             │
│     "limit": 100                                            │
│   },                                                        │
│   "id": 1                                                   │
│ }                                                           │
│                                                             │
│ # Response                                                  │
│ {                                                           │
│   "jsonrpc": "2.0",                                         │
│   "result": {                                               │
│     "total_count": 47,                                      │
│     "results": [...],                                       │
│     "pagination": {"limit": 100, "offset": 0, "has_more": false} │
│   },                                                        │
│   "id": 1                                                   │
│ }                                                           │
└─────────────────────────────────────────────────────────────┘
```

---

## 🧹 Retention & Vacuum Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Housekeeping Orchestrator (Daily Scheduled)               │
└──────┬──────────────────────────────────────────────────────┘
       │ 02:00 AM (configurable)
       ↓
┌─────────────────────────────────────────────────────────────┐
│  AuditVacuum.vacuum()                                       │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─→ For each log level:
       │   ┌────────────────────────────────────────┐
       │   │ Level: ERROR (retention: 90 days)      │
       │   │ Cutoff: 2025-10-11                     │
       │   │ DELETE FROM audit_logs                 │
       │   │ WHERE level='ERROR'                    │
       │   │   AND created_at < '2025-10-11'        │
       │   └────────────────────────────────────────┘
       │
       ├─→ ┌────────────────────────────────────────┐
       │   │ Level: INFO (retention: 30 days)       │
       │   │ Cutoff: 2025-12-10                     │
       │   │ DELETE FROM audit_logs                 │
       │   │ WHERE level='INFO'                     │
       │   │   AND created_at < '2025-12-10'        │
       │   └────────────────────────────────────────┘
       │
       ├─→ ┌────────────────────────────────────────┐
       │   │ Level: DEBUG (retention: 7 days)       │
       │   │ Cutoff: 2026-01-02                     │
       │   │ DELETE FROM audit_logs                 │
       │   │ WHERE level='DEBUG'                    │
       │   │   AND created_at < '2026-01-02'        │
       │   └────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│  VACUUM Command (reclaim space)                             │
│  • DB size before: 150 MB                                   │
│  • Records deleted: 47,832                                  │
│  • DB size after: 98 MB                                     │
│  • Space reclaimed: 52 MB                                   │
└──────┬──────────────────────────────────────────────────────┘
       │
       ↓
┌─────────────────────────────────────────────────────────────┐
│  Log Vacuum Operation (audit the audit)                     │
│  INSERT INTO audit_vacuum_log (                             │
│      vacuum_time, level, records_deleted, space_reclaimed   │
│  )                                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## ✅ Success Verification Flow

```
┌─────────────────────────────────────────────────────────────┐
│  Implementation Complete                                    │
└──────┬──────────────────────────────────────────────────────┘
       │
       ├─→ AC-AUDIT-001: Query by AC-ID
       │   │ TEST: search(ac_id="AC-GOV-001")
       │   └─→ ✅ Returns matching entries only
       │
       ├─→ AC-AUDIT-002: Memory buffer
       │   │ TEST: Add 1001 entries
       │   └─→ ✅ Flush triggered at 1000
       │
       ├─→ AC-AUDIT-003: Per-repo isolation
       │   │ TEST: Log from repo A, check repo B
       │   └─→ ✅ No cross-contamination
       │
       ├─→ AC-AUDIT-004: MCP tools
       │   │ TEST: mcp_audit_query(ac_id="AC-GOV-001")
       │   └─→ ✅ Returns filtered results
       │
       ├─→ AC-AUDIT-005: Automatic vacuum
       │   │ TEST: 31-day-old INFO log
       │   └─→ ✅ Deleted by vacuum
       │
       └─→ AC-AUDIT-006: Level-based retention
           │ TEST: Check retention periods
           └─→ ✅ ERROR: 90d, INFO: 30d, DEBUG: 7d
```

---

## 📊 Progress Tracking

```
PHASE 1: Preparation
├── [ ] Create src/infrastructure/
├── [ ] Create cortex-brain/schemas/audit_schema.sql
├── [ ] Create cortex-brain/config/audit-config.yaml
└── [ ] Create tests/audit/

PHASE 2: New Components
├── [ ] Implement AuditStorage
│   ├── [ ] __init__, insert, query methods
│   └── [ ] Tests: test_audit_storage.py
├── [ ] Implement AuditMemoryBuffer
│   ├── [ ] __init__, add, flush methods
│   └── [ ] Tests: test_memory_buffer.py
└── [ ] Implement RepoContext
    ├── [ ] detect_repo_path, get_audit_db_path
    └── [ ] Tests: test_repo_isolation.py

PHASE 3: AuditLogger Refactoring
├── [ ] Move file to infrastructure/
├── [ ] Add ac_id field to AuditEntry
├── [ ] Replace file storage with SQLite
├── [ ] Integrate memory buffer
└── [ ] Update search() method

PHASE 4: MCP Tools
├── [ ] Implement mcp_audit_query
├── [ ] Implement mcp_audit_list
├── [ ] Implement mcp_audit_export
├── [ ] Implement mcp_audit_validate
└── [ ] Tests: test_audit_tools.py

PHASE 5: Retention & Vacuum
├── [ ] Implement AuditVacuum
├── [ ] Update HousekeepingOrchestrator
└── [ ] Tests: test_retention_policy.py, test_audit_vacuum.py

PHASE 6: Testing & Validation
├── [ ] Migrate existing tests
├── [ ] Run all audit tests
└── [ ] Validate all 6 AC-AUDIT criteria

PHASE 7: Migration & Cleanup
├── [ ] Update imports across codebase
├── [ ] Remove deprecated JSONL files
└── [ ] Update documentation

═══════════════════════════════════════════════════
COMPLETION: All 6 AC-AUDIT validated ✅
           354+ AC now validatable ✅
```

---

**Created:** January 9, 2026  
**Status:** Implementation Guide  
**Estimate:** 12-16 hours  
**Priority:** P0_CRITICAL

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
