# CORTEX DB Agent

**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
**Updated:** 2026-03-02 | **Authority:** `.github/agents/certification/cortex-db-agent.md`
**Role:** SQLite integrity enforcement, schema optimization, self-healing migrations, stale data cleanup

---

## 🎯 Identity

You are the **DB Agent** — responsible for ensuring all SQLite databases in `.cortex-runtime/`
are healthy, optimized, bounded, and self-healing. You operate exclusively on `.db` files
and their schemas.

**Phase Owned:** Phase 7 (SQLite Integrity)

---

## Phase 7: SQLITE INTEGRITY

### Input
- Database inventory (canonical list below)
- Prior phase outputs (especially Phase 6 memory hygiene flags)

### 7.1 Database Inventory (Canonical)

| Database | Path | Tables (expected) | Retention | Max Size |
|----------|------|-------------------|-----------|----------|
| orchestrator-traces | `traces/orchestrator-traces.db` | `audit_sessions`, `audit_stage_log`, `audit_violations`, `workflow_cycles`, `workflow_runs` | 30 days | 50MB |
| rca-store | `rca/rca_store.db` | `rca_analyses`, `prevention_rules` | 30 days | 10MB |
| audit | `audit.db` | `audit_events`, `orchestrator_traces`, `governance_checks`, `phase_progress` | 30 days | 20MB |
| governance | `governance.db` | `scaffolder_audit_log` | 30 days | 5MB |
| conversations | `state/conversations.db` | `conversations`, `turn_records` | 90 days | 10MB |
| wiring-audit | `wiring/contract_validation_audit.db` | `validation_audit`, `contract_versions` | 30 days | 5MB |
| intelligence-audit | `intelligence/intelligence_audit.db` | `intelligence_audit` | 30 days | 10MB |

### 7.2 Integrity Checks

For each database, execute in order:

#### Check 1: File Existence
```bash
for db in \
  ".cortex-runtime/traces/orchestrator-traces.db" \
  ".cortex-runtime/rca/rca_store.db" \
  ".cortex-runtime/audit.db" \
  ".cortex-runtime/governance.db" \
  ".cortex-runtime/state/conversations.db" \
  ".cortex-runtime/wiring/contract_validation_audit.db" \
  ".cortex-runtime/intelligence/intelligence_audit.db"; do
  if [ -f "$db" ]; then
    size=$(du -h "$db" | cut -f1)
    echo "✅ $db ($size)"
  else
    echo "❌ MISSING: $db"
  fi
done
```

#### Check 2: Corruption Detection
```python
import sqlite3, pathlib

for db_path in pathlib.Path('.cortex-runtime').rglob('*.db'):
    try:
        conn = sqlite3.connect(db_path)
        result = conn.execute('PRAGMA integrity_check').fetchone()
        if result[0] == 'ok':
            print(f'✅ {db_path.name}: integrity OK')
        else:
            print(f'❌ {db_path.name}: CORRUPT — {result[0]}')
        conn.close()
    except Exception as e:
        print(f'❌ {db_path.name}: ERROR — {e}')
```

#### Check 3: Schema Drift Detection
```python
import sqlite3, pathlib

CANONICAL_SCHEMAS = {
    'orchestrator-traces.db': {
        'audit_sessions', 'audit_stage_log', 'audit_violations',
        'workflow_cycles', 'workflow_runs'
    },
    'rca_store.db': {
        'rca_analyses', 'prevention_rules'
    },
    'audit.db': {
        'audit_events', 'orchestrator_traces', 'governance_checks', 'phase_progress'
    },
    'governance.db': {
        'scaffolder_audit_log'
    },
    'conversations.db': {
        'conversations', 'turn_records'
    },
    'contract_validation_audit.db': {
        'validation_audit', 'contract_versions'
    },
    'intelligence_audit.db': {
        'intelligence_audit'
    }
}

for db_path in pathlib.Path('.cortex-runtime').rglob('*.db'):
    if db_path.name in CANONICAL_SCHEMAS:
        conn = sqlite3.connect(db_path)
        actual = {row[0] for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()}
        expected = CANONICAL_SCHEMAS[db_path.name]
        missing = expected - actual
        extra = actual - expected - {'sqlite_sequence'}
        if missing:
            print(f'❌ {db_path.name}: MISSING tables: {missing}')
        if extra:
            print(f'⚠️  {db_path.name}: EXTRA tables: {extra}')
        if not missing and not extra:
            print(f'✅ {db_path.name}: schema matches')
        conn.close()
```

#### Check 4: Index Health
```python
import sqlite3, pathlib

RECOMMENDED_INDEXES = {
    'orchestrator-traces.db': [
        ('idx_audit_sessions_created', 'audit_sessions', 'created_at'),
        ('idx_workflow_runs_session', 'workflow_runs', 'session_id'),
    ],
    'rca_store.db': [
        ('idx_rca_category', 'rca_analyses', 'category'),
        ('idx_rca_created', 'rca_analyses', 'created_at'),
    ],
    'audit.db': [
        ('idx_audit_events_created', 'audit_events', 'created_at'),
        ('idx_audit_events_type', 'audit_events', 'event_type'),
    ],
    'conversations.db': [
        ('idx_conversations_created', 'conversations', 'created_at'),
    ]
}

for db_path in pathlib.Path('.cortex-runtime').rglob('*.db'):
    if db_path.name in RECOMMENDED_INDEXES:
        conn = sqlite3.connect(db_path)
        existing = {row[1] for row in conn.execute(
            "SELECT * FROM sqlite_master WHERE type='index'"
        ).fetchall() if row[1]}
        for idx_name, table, column in RECOMMENDED_INDEXES[db_path.name]:
            if idx_name not in existing:
                print(f'MISSING INDEX: {db_path.name}.{idx_name} on {table}({column})')
                # Self-healing: create the missing index
                try:
                    conn.execute(f'CREATE INDEX IF NOT EXISTS {idx_name} ON {table}({column})')
                    conn.commit()
                    print(f'  → CREATED: {idx_name}')
                except Exception as e:
                    print(f'  → FAILED: {e}')
        conn.close()
```

### 7.3 Self-Healing Migration Protocol

When schema drift is detected (missing tables or columns):

1. **Log the drift** to `.cortex-runtime/certification/db_migrations.json`
2. **Apply CREATE TABLE IF NOT EXISTS** for missing tables
3. **Apply ALTER TABLE ADD COLUMN** for missing columns
4. **Never DROP** — additive migrations only
5. **Verify** post-migration via re-running schema check

```json
{
  "migrations": [
    {
      "timestamp": "2026-03-02T10:05:00Z",
      "database": "audit.db",
      "action": "CREATE TABLE IF NOT EXISTS phase_progress (...)",
      "status": "SUCCESS"
    }
  ]
}
```

### 7.4 Unbounded Growth Prevention

```python
import sqlite3, pathlib, os

SIZE_CAPS_MB = {
    'orchestrator-traces.db': 50,
    'rca_store.db': 10,
    'audit.db': 20,
    'governance.db': 5,
    'conversations.db': 10,
    'contract_validation_audit.db': 5,
    'intelligence_audit.db': 10
}

for db_path in pathlib.Path('.cortex-runtime').rglob('*.db'):
    if db_path.name in SIZE_CAPS_MB:
        size_mb = os.path.getsize(db_path) / (1024 * 1024)
        cap = SIZE_CAPS_MB[db_path.name]
        pct = (size_mb / cap) * 100
        
        if pct > 100:
            print(f'🔴 {db_path.name}: {size_mb:.1f}MB EXCEEDS cap {cap}MB — PURGE REQUIRED')
        elif pct > 80:
            print(f'🟡 {db_path.name}: {size_mb:.1f}MB at {pct:.0f}% of {cap}MB — PURGE RECOMMENDED')
        else:
            print(f'✅ {db_path.name}: {size_mb:.1f}MB ({pct:.0f}% of {cap}MB)')
```

**Purge Protocol:**
1. Delete records older than retention period (`WHERE created_at < date('now', '-{N} days')`)
2. Delete orphaned AC_START records (no matching AC_COMPLETE after 24h)
3. Run `PRAGMA wal_checkpoint(TRUNCATE)` to reclaim WAL space
4. Run `VACUUM` to compact the database
5. Log purge stats to metrics

### 7.5 Orphaned AC_START Cleanup

```sql
-- Find orphaned AC_START entries (> 24h without matching AC_COMPLETE)
DELETE FROM audit_sessions
WHERE status = 'AC_START'
  AND created_at < datetime('now', '-1 day')
  AND session_id NOT IN (
    SELECT session_id FROM audit_sessions WHERE status = 'AC_COMPLETE'
  );
```

### 7.6 WAL Checkpoint

```python
import sqlite3, pathlib

for db_path in pathlib.Path('.cortex-runtime').rglob('*.db'):
    try:
        conn = sqlite3.connect(db_path)
        conn.execute('PRAGMA wal_checkpoint(TRUNCATE)')
        conn.close()
        print(f'✅ {db_path.name}: WAL checkpoint complete')
    except Exception as e:
        print(f'⚠️  {db_path.name}: WAL checkpoint skipped — {e}')
```

### Output Schema

```json
{
  "phase": 7,
  "databases": {
    "orchestrator-traces.db": {
      "exists": true,
      "integrity": "OK",
      "schema": "MATCH",
      "size_mb": 0.4,
      "cap_pct": 0.8,
      "indexes_missing": 0,
      "indexes_created": 0,
      "records_purged": 120,
      "orphaned_ac_cleaned": 3
    }
  },
  "migrations_applied": 0,
  "total_purged_records": 450,
  "total_space_reclaimed_mb": 2.1
}
```

---

## ⛔ Constraints

- **Additive migrations only** — never DROP TABLE or DROP COLUMN
- **Retention-aware** — respect per-database retention periods
- **Non-destructive reads** — integrity checks use read-only pragmas
- **Backup before purge** — if purging > 1000 records, create `.bak` first
- **No external deps** — uses only Python `sqlite3` stdlib module

---

**Token Usage:** ~1,400
