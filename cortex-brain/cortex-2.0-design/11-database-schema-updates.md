# CORTEX 2.0 Database Schema Updates

**Document:** 11-database-schema-updates.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Define the schema changes required to support CORTEX 2.0 features:
- Self-review engine (health reports, issues, auto-fixes)
- Database maintenance engine (metrics, archival, retention)
- Incremental creation (progress tracking)
- Plugin registry + hook execution history
- Conversation enrichment (task states, action logs)
- Knowledge integrity (boundary events, provenance)

This document describes: new tables, modified tables, indices, retention strategy integration, migration considerations, and rationale.

---

## 🗂️ Summary of Changes

| Area | Change Type | Object | Description |
|------|-------------|--------|-------------|
| Self-Review | New Table | `health_reports` | Stores summarized health review scores |
| Self-Review | New Table | `health_issues` | Individual issues per review with severity + fix flags |
| Maintenance | New Table | `maintenance_runs` | VACUUM/ANALYZE/REINDEX run metadata |
| Maintenance | New Table | `archival_operations` | Records archival batch stats |
| Maintenance | New Table | `retention_policy_snapshots` | Snapshot of policy evaluation |
| Incremental Creation | New Table | `creation_sessions` | Track large file creation progress |
| Incremental Creation | New Table | `creation_chunks` | Per chunk status + validation info |
| Plugins | New Table | `plugins` | Registered plugins metadata |
| Plugins | New Table | `plugin_hook_executions` | Hook execution audit trail |
| Conversation | Modify | `conversations` | Add task status, archival flags |
| Conversation | New Table | `conversation_actions` | Logged actions per turn |
| Conversation | New Table | `conversation_state_snapshots` | Full state checkpoints |
| Knowledge Integrity | New Table | `boundary_events` | Boundary guard events (allow/deny) |
| Knowledge Provenance | New Table | `provenance_links` | Source artifact relationships |
| Performance | New Index | Various | Indices for query speed (detailed below) |

---

## 📦 New Tables

### 1. `health_reports`
Stores each self-review execution summary.
```sql
CREATE TABLE health_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    overall_status TEXT NOT NULL,                -- excellent|good|fair|poor|critical
    overall_score REAL NOT NULL,                 -- 0.0 - 1.0
    database_score REAL NOT NULL,
    performance_score REAL NOT NULL,
    rule_compliance_score REAL NOT NULL,
    test_coverage_score REAL NOT NULL,
    storage_score REAL NOT NULL,
    auto_fixable_count INTEGER NOT NULL,
    fixed_count INTEGER NOT NULL
);
CREATE INDEX idx_health_reports_created_at ON health_reports(created_at DESC);
```

### 2. `health_issues`
```sql
CREATE TABLE health_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL REFERENCES health_reports(id) ON DELETE CASCADE,
    category TEXT NOT NULL,                      -- database|performance|rule_compliance|tests|storage
    severity TEXT NOT NULL,                      -- critical|high|medium|low|info
    title TEXT NOT NULL,
    description TEXT,
    auto_fixable INTEGER NOT NULL DEFAULT 0,
    fix_applied INTEGER NOT NULL DEFAULT 0,
    fix_description TEXT,
    impact TEXT,
    recommendation TEXT,
    detected_at TIMESTAMP NOT NULL,
    UNIQUE(report_id, title)
);
CREATE INDEX idx_health_issues_report ON health_issues(report_id);
CREATE INDEX idx_health_issues_severity ON health_issues(severity);
```

### 3. `maintenance_runs`
```sql
CREATE TABLE maintenance_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    tier TEXT NOT NULL,                          -- tier1|tier2|tier3
    operations TEXT NOT NULL,                    -- JSON array
    fragmentation_before REAL,
    fragmentation_after REAL,
    size_before_mb REAL,
    size_after_mb REAL,
    space_reclaimed_mb REAL,
    query_time_before_ms REAL,
    query_time_after_ms REAL,
    speedup REAL,
    status TEXT NOT NULL DEFAULT 'running',      -- running|success|failed|rolled_back
    error_message TEXT
);
CREATE INDEX idx_maintenance_runs_tier_time ON maintenance_runs(tier, started_at DESC);
```

### 4. `archival_operations`
```sql
CREATE TABLE archival_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    source_tier TEXT NOT NULL,
    destination_tier TEXT NOT NULL,
    records_archived INTEGER NOT NULL,
    space_freed_mb REAL,
    oldest_record_at TIMESTAMP,
    newest_record_at TIMESTAMP,
    compression_enabled INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'success',      -- success|failed|rolled_back
    error_message TEXT
);
CREATE INDEX idx_archival_operations_time ON archival_operations(started_at DESC);
```

### 5. `retention_policy_snapshots`
```sql
CREATE TABLE retention_policy_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    tier TEXT NOT NULL,
    policy_json TEXT NOT NULL,                   -- JSON of applied policy
    violations_count INTEGER NOT NULL,
    age_violations INTEGER NOT NULL,
    count_violations INTEGER NOT NULL,
    actions_taken TEXT                           -- JSON array of actions
);
CREATE INDEX idx_retention_policy_snapshots_tier_time ON retention_policy_snapshots(tier, created_at DESC);
```

### 6. `creation_sessions`
```sql
CREATE TABLE creation_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    file_type TEXT NOT NULL,                     -- markdown|python|json|other
    total_chunks INTEGER NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_update TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed INTEGER NOT NULL DEFAULT 0,
    failed INTEGER NOT NULL DEFAULT 0,
    UNIQUE(file_path)
);
CREATE INDEX idx_creation_sessions_status ON creation_sessions(completed, failed);
```

### 7. `creation_chunks`
```sql
CREATE TABLE creation_chunks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL REFERENCES creation_sessions(id) ON DELETE CASCADE,
    chunk_number INTEGER NOT NULL,
    chunk_type TEXT NOT NULL,                    -- header|section|code_block|list|table|footer
    line_start INTEGER NOT NULL,
    line_end INTEGER NOT NULL,
    estimated_tokens INTEGER,
    status TEXT NOT NULL DEFAULT 'pending',      -- pending|written|failed|skipped
    validation_warnings TEXT,                    -- JSON array
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, chunk_number)
);
CREATE INDEX idx_creation_chunks_session ON creation_chunks(session_id, chunk_number);
```

### 8. `plugins`
```sql
CREATE TABLE plugins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    category TEXT NOT NULL,
    priority INTEGER NOT NULL,
    description TEXT,
    author TEXT,
    dependencies TEXT,                           -- JSON array
    hooks TEXT,                                  -- JSON array
    enabled INTEGER NOT NULL DEFAULT 1,
    registered_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_plugins_category ON plugins(category, enabled);
```

### 9. `plugin_hook_executions`
```sql
CREATE TABLE plugin_hook_executions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    plugin_id TEXT NOT NULL REFERENCES plugins(plugin_id) ON DELETE CASCADE,
    hook TEXT NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    duration_ms REAL,
    status TEXT NOT NULL DEFAULT 'running',      -- running|success|failed
    error_message TEXT,
    context_json TEXT,
    result_json TEXT
);
CREATE INDEX idx_plugin_hook_exec_hook_time ON plugin_hook_executions(hook, started_at DESC);
```

### 10. `conversation_actions`
```sql
CREATE TABLE conversation_actions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    action_type TEXT NOT NULL,                   -- retrieval|generation|write|maintenance|self_review
    description TEXT NOT NULL,
    metadata_json TEXT,                          -- JSON object (paths, counts, etc.)
    success INTEGER NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_conversation_actions_session_turn ON conversation_actions(session_id, turn_number);
```

### 11. `conversation_state_snapshots`
```sql
CREATE TABLE conversation_state_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT NOT NULL,
    turn_number INTEGER NOT NULL,
    state_json TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, turn_number)
);
CREATE INDEX idx_state_snapshots_session ON conversation_state_snapshots(session_id, turn_number DESC);
```

### 12. `boundary_events`
```sql
CREATE TABLE boundary_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    occurred_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    event_type TEXT NOT NULL,                    -- read|write|scan|delete|plugin
    path TEXT NOT NULL,
    allowed INTEGER NOT NULL,                    -- 1 allowed, 0 denied
    reason TEXT,
    rule_reference TEXT,                         -- Which rule triggered decision
    plugin_id TEXT,
    session_id TEXT
);
CREATE INDEX idx_boundary_events_time ON boundary_events(occurred_at DESC);
CREATE INDEX idx_boundary_events_path ON boundary_events(path);
```

### 13. `provenance_links`
```sql
CREATE TABLE provenance_links (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_type TEXT NOT NULL,                   -- file|conversation|pattern|plugin
    source_ref TEXT NOT NULL,                    -- path or id
    target_type TEXT NOT NULL,
    target_ref TEXT NOT NULL,
    relation TEXT NOT NULL,                      -- generated|updated|referenced|archived_from
    confidence REAL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_provenance_source ON provenance_links(source_type, source_ref);
CREATE INDEX idx_provenance_target ON provenance_links(target_type, target_ref);
```

---

## ✏️ Modified Tables

### `conversations`
Add columns (if not already present):
```sql
ALTER TABLE conversations ADD COLUMN task_status TEXT DEFAULT 'open';  -- open|in_progress|blocked|done
ALTER TABLE conversations ADD COLUMN archived INTEGER DEFAULT 0;       -- moved to Tier 3
ALTER TABLE conversations ADD COLUMN last_action_at TIMESTAMP;         -- most recent agent action
```
Add index for active recent conversations:
```sql
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(archived, last_updated DESC);
```

---

## 🚀 Indices & Performance Optimizations

| Table | Index | Purpose |
|-------|-------|---------|
| health_reports | created_at DESC | Recent reviews dashboard |
| health_issues | (severity) | Filter critical/high issues fast |
| maintenance_runs | (tier, started_at DESC) | Latest maintenance per tier |
| archival_operations | (started_at DESC) | Auditing batches |
| creation_sessions | (completed, failed) | Query incomplete sessions |
| creation_chunks | (session_id, chunk_number) | Resume incremental creation |
| plugin_hook_executions | (hook, started_at DESC) | Hook performance analysis |
| conversation_actions | (session_id, turn_number) | Turn-level audit trail |
| conversation_state_snapshots | (session_id, turn_number DESC) | Quick latest snapshot retrieve |
| boundary_events | (occurred_at DESC) | Recent security events |
| provenance_links | (target_type, target_ref) | Trace lineage |

---

## ♻️ Retention & Archival Strategy Integration

| Table | Retention Policy | Action |
|-------|------------------|--------|
| health_reports | Keep 180 days | Delete older rows (cascade handles issues) |
| health_issues | Cascade w/ reports | No direct retention needed |
| maintenance_runs | 90 days | Aggregate stats beyond 90d, drop detail |
| archival_operations | 180 days | Keep for audit; compress JSON exports if needed |
| retention_policy_snapshots | 90 days | Only recent evaluation context needed |
| creation_sessions | Complete & >30d | Delete with chunks cascade |
| creation_chunks | Cascade | No direct action |
| plugin_hook_executions | 30 days | Summarize performance metrics in rollup table (future) |
| conversation_actions | 60 days (Tier 1) | Archive to Tier 3 if linked to long-term sessions |
| conversation_state_snapshots | Last 5 per session | Delete older snapshots |
| boundary_events | 90 days | Export denied events to cold storage before purge |
| provenance_links | 1 year | Needed for audit; archive older |

---

## 🔄 Migration Approach (High-Level)

1. Snapshot & Backup
   - Export existing Tier DBs (`.db` copies + JSON diffs)
   - Verify integrity (`PRAGMA integrity_check`)
2. Apply Schema Evolutions
   - Use idempotent migrations (CREATE TABLE IF NOT EXISTS, conditional ALTER)
   - Wrap in transaction per logical group
3. Backfill / Initialize
   - Insert initial plugin metadata from current registry
   - Create initial self-review baseline row (all perfect or null metrics)
   - Initialize retention snapshots using current config
4. Verification Phase
   - Run smoke self-review → generates `health_reports` + `health_issues`
   - Trigger incremental creation dry-run to populate `creation_sessions`
5. Rollback Plan
   - If any migration fails: restore DB copies, abort start
6. Logging
   - Record migration ID, applied_at, checksum (future `migrations` table already likely exists or will be defined in doc 12)

---

## 🧪 Validation Queries

```sql
-- Confirm new tables
SELECT name FROM sqlite_master WHERE type='table' AND name IN (
  'health_reports','maintenance_runs','creation_sessions','plugins'
);

-- Recent failed plugin executions
SELECT plugin_id, hook, error_message, started_at
FROM plugin_hook_executions
WHERE status='failed'
ORDER BY started_at DESC
LIMIT 10;

-- Incomplete creation sessions
SELECT file_path, total_chunks, completed, failed, started_at
FROM creation_sessions
WHERE completed=0
ORDER BY started_at DESC;
```

---

## ✅ Rationale

- Separate `health_reports` + `health_issues`: fast dashboard queries, cascade cleanup
- Explicit `creation_sessions/chunks`: deterministic resume + analytics (mean chunk size, retries)
- Plugin execution logging: observability + future adaptive prioritization
- Boundary + provenance tables: auditability and compliance foundation
- Retention snapshots: historical shape of policy decisions (explain why deletion happened)

---

## ⚠️ Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|-----------|
| Table bloat (execution logs) | Slow queries | Aggressive retention + rollups |
| Migration interruption | Partial schema | Wrap groups in transactions + idempotent checks |
| Index overhead | Slower writes | Only create indices tied to query patterns |
| Provenance growth | Storage increase | Archive >12 months to cold storage |
| Cascade deletes misused | Data loss | Restrict cascades to safe child tables only |

---

## 🧩 Next Steps

- Implement migrations (Doc 12)
- Update ORM / data access layer abstractions
- Integrate self-review writes → `health_reports` / `health_issues`
- Wire maintenance engine metrics → `maintenance_runs`
- Add creation engine persistence layer (currently in-memory in doc 09 example)
- Add retention worker to enforce table-specific policies

---

**Next:** 12-migration-strategy.md (Applying these changes safely from 1.0 → 2.0)
