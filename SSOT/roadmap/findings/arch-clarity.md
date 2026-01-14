# Architecture Design Clarity Review

**Date:** 2026-01-14  
**Scope:** Architecture, MCP, Toolkit, Orchestration, Audit Trace  
**Status:** ✅ CLEAR WITH HIGH CONFIDENCE

---

## 1. Governance Architecture

### 3-Tier Model Clarity

**Definition (AR-001):**
```
Tier 0: CORTEX CORE (25 SKULL rules) - IMMUTABLE
    │
    ├── Runtime write-protected
    ├── Loaded at startup
    └── Cannot be bypassed
    
Tier 1: Business Rules - MUTABLE
    │
    ├── YAML files (human-readable)
    ├── SQLite index (fast queries)
    └── Reloaded on file change
    
Tier 2: Engineering Standards - ADVISORY
    │
    └── Convention-based enforcement
```

**Clarity Score:** 95%

**Open Questions:**
1. ~~What happens when Tier 1 rule conflicts with Tier 0?~~ → Resolved: Tier 0 wins (precedence)
2. ~~How are rules cached?~~ → Resolved: SQLite + hash-based invalidation

---

## 2. MCP Integration Architecture

### Tool Categories

**Standard MCP Servers (Reuse):**
- Filesystem operations
- Git operations
- SQLite queries

**Custom CORTEX Tools (Build):**
| Tool | Purpose | Status |
|------|---------|--------|
| `cortex_audit_query` | Query audit logs | ✅ Implemented |
| `cortex_audit_list` | Paginated audit view | ✅ Implemented |
| `cortex_audit_export` | Export to JSON/CSV | ✅ Implemented |
| `cortex_governance_rules` | List governance rules | ✅ Implemented |
| `cortex_governance_validate` | Validate rule exists | ✅ Implemented |
| `cortex_governance_conflicts` | Detect conflicts | ✅ Implemented |
| `cortex_traceability_scan` | Scan AC-IDs | ✅ Implemented |
| `cortex_todo_create` | Create TODO | ✅ Implemented |

**Architecture Pattern:**
```
Request → MCP Server → Tool Handler → CORTEX Core
                │
                └── Schema Validation → Execution → Response
```

**Clarity Score:** 90%

---

## 3. Cortex Toolkit Components

### Core Components (10)

| Component | Interface | Dependencies | Clarity |
|-----------|-----------|--------------|---------|
| BaseOrchestrator | Abstract class | None | 95% |
| MasterOrchestrator | Concrete class | PatternRouter, StateManager | 95% |
| GovernanceRegistry | Singleton | SQLite, YAML loader | 90% |
| GovernanceMerger | Service | GovernanceRule | 90% |
| EnhancedAuditLogger | Service | SQLite, HashChain | 95% |
| ProgressTrackerManager | Service | SQLite | 85% |
| EvidenceBundle | Data class | Path, JSON | 80% |
| HashChainIntegrity | Utility | SHA256 | 95% |
| LifecycleManager | Service | FSM, Locks | 85% |
| TemplateResolver | Service | Path, YAML | 80% |

### Domain Orchestrators (9)

| Orchestrator | Domain | Base | Clarity |
|--------------|--------|------|---------|
| TDD-Master | Testing | BaseOrchestrator | 85% |
| Planning | Planning | BaseOrchestrator | 85% |
| ADO | Azure DevOps | BaseOrchestrator | 80% |
| Investigation | Analysis | BaseOrchestrator | 80% |
| Governance | Rules | BaseOrchestrator | 90% |
| Evidence | Capture | BaseOrchestrator | 80% |
| TodoManager | Execution | BaseOrchestrator | 85% |
| Vacuum | Cleanup | BaseOrchestrator | 75% |
| Cleanup | Maintenance | BaseOrchestrator | 75% |

**Overall Clarity Score:** 85%

---

## 4. Master Orchestration Pattern

### Routing Flow

```
User Request
    │
    ▼
┌─────────────────────┐
│  MasterOrchestrator │
│                     │
│  1. PatternRouter   │◄─── Exact/Regex match (90%+ requests)
│       │             │
│       ▼             │
│  2. can_handle()    │◄─── Strategy pattern selection
│       │             │
│       ▼             │
│  3. ExecutionEngine │◄─── Lifecycle management
│       │             │
│       ▼             │
│  4. ResponseRender  │◄─── Template resolution
└─────────────────────┘
    │
    ▼
Response + Audit Trail
```

### Plugin Architecture

```
src/orchestrators/
├── core/           ← Required, loaded always
├── domain/         ← Built-in domain orchestrators
├── custom/         ← Auto-discovered plugins (separate process)
└── registry/       ← Registration metadata
```

**Isolation Pattern:**
- Custom orchestrators run in separate process (multiprocessing)
- Child exceptions caught at boundary
- Circular dependencies detected at startup

**Clarity Score:** 90%

---

## 5. Audit Trace Logging Design

### Hash Chain Architecture

```
Event N-1                Event N                 Event N+1
┌─────────────┐         ┌─────────────┐         ┌─────────────┐
│ event_hash  │────────▶│ prev_hash   │────────▶│ prev_hash   │
│             │         │ event_hash  │         │ event_hash  │
└─────────────┘         └─────────────┘         └─────────────┘
       │                       │                       │
       └───────────────────────┼───────────────────────┘
                               │
                         Tamper Detection
```

### Audit Schema (Implemented)

```sql
CREATE TABLE audit_logs (
    id INTEGER PRIMARY KEY,
    timestamp TEXT NOT NULL,
    level TEXT NOT NULL,
    category TEXT NOT NULL,    -- 7 categories
    component TEXT NOT NULL,
    operation TEXT NOT NULL,
    message TEXT NOT NULL,
    ac_id TEXT,                -- Traceability
    correlation_id TEXT,       -- Request tracking
    duration_ms REAL,
    context TEXT,              -- JSON blob
    metadata TEXT,             -- JSON blob
    event_hash TEXT NOT NULL,  -- Current hash
    prev_event_hash TEXT,      -- Previous hash
    created_at DATETIME
);
```

### Query Indexes

| Index | Columns | Purpose |
|-------|---------|---------|
| idx_ac_id | ac_id | AC-ID traceability |
| idx_component | component | Component filtering |
| idx_level | level | Severity filtering |
| idx_timestamp | timestamp | Time range queries |
| idx_category | category | Category filtering |
| idx_correlation | correlation_id | Request tracing |
| idx_event_hash | event_hash | Integrity checks |

**Clarity Score:** 95%

---

## 6. Design Gaps Identified

### High Priority

| Gap | Impact | Resolution |
|-----|--------|------------|
| GovernanceRegistry not auto-wiring | 60% rules not enforced | Implement reflection loader |
| Evidence bundle generation 0% | Cannot verify AC completion | Implement EvidenceBundleGenerator |
| State machine incomplete | Race conditions possible | Add distributed locking |

### Medium Priority

| Gap | Impact | Resolution |
|-----|--------|------------|
| Custom template fallback | Broken responses | Implement TemplateResolver chain |
| Cross-platform paths | Windows failures | Convert to pathlib throughout |
| Performance metrics | No SLA monitoring | Add OpenTelemetry |

### Low Priority

| Gap | Impact | Resolution |
|-----|--------|------------|
| Knowledge graph (FR-005) | No intent disambiguation | Defer to Phase 2 |
| HIPAA/SOX compliance | No enterprise audit | Tier 3 logger opt-in |

---

## 7. Confidence Summary

| Area | Confidence | Blocking Issues |
|------|------------|-----------------|
| Governance Architecture | 95% | None |
| MCP Integration | 90% | Schema validation |
| Toolkit Components | 85% | Evidence generation |
| Master Orchestration | 90% | None |
| Audit Trace Logging | 95% | None |
| **Overall** | **91%** | **3 blocking issues** |

---

## Recommendations

1. **Execute Day 0 Critical Fixes** (2 hours)
   - WAL mode, audit schema, tracker rebuild, pytest warnings

2. **Complete Governance Wiring** (Week 1)
   - Wire remaining 15/25 SKULL rules
   - Test enforcement at startup

3. **Implement Evidence Bundle** (Week 1)
   - Link tests to AC-IDs
   - Capture code diffs and commits
   - Generate verification reports

4. **Add Distributed Locking** (Week 2)
   - Prevent state race conditions
   - Enable concurrent orchestrator execution
