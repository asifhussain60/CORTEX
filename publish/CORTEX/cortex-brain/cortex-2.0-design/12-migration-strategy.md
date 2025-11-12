# CORTEX 2.0 Migration Strategy

**Document:** 12-migration-strategy.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose
Safely migrate an existing CORTEX 1.0 installation to 2.0 using a hybrid, incremental approach that:
- Preserves working conversations, patterns, and historical memory
- Introduces new schema elements without breaking existing flows
- Minimizes downtime (target: near-zero for read operations)
- Enables rollback at each critical checkpoint
- Provides verifiable post-migration health

---

## 📦 Scope
Migrates:
- Databases (Tier 1/2/3) → new tables & altered columns (see `11-database-schema-updates.md`)
- Configuration → new keys and validation (v2 format draft in doc 14)
- Plugins → registration into `plugins` table + hook audit logging
- Conversation state → add task status, archival markers
- Operational telemetry → self-review & maintenance recording

Not in scope (handled later or optional):
- Deep refactors of existing agents (done gradually)
- Data quality reclassification (patterns confidence recalculation)
- Large-scale provenance backfill (only forward from migration point)

---

## 🧭 Migration Phases Overview

```
Phase 0  Assessment & Planning
Phase 1  Snapshot & Freeze (Write Quiescence)
Phase 2  Schema Evolution (Idempotent DDL)
Phase 3  Data Backfill & Initialization
Phase 4  Verification & Health Review
Phase 5  Cutover (Enable 2.0 features progressively)
Phase 6  Post-Migration Monitoring & Rollback Window
Phase 7  Optimization & Cleanup (retention enforcement)
```

---

## 🔍 Phase 0: Assessment & Planning
Checklist:
- Identify current versions (schema hashes, CORTEX 1.0 commit SHA)
- Inventory DB sizes (Tier 1, Tier 2 FTS, Tier 3 archives)
- Count active conversations & pending tasks
- Verify test suite passing (baseline integrity)
- Confirm backup location capacity (>= 2× total DB size)

Artifacts:
- `migration-plan-{DATE}.json` containing environment fingerprint
- Dry-run time estimates (DDL execution, backfill loops)

---

## 🧊 Phase 1: Snapshot & Freeze
Goal: ensure consistent state for migration.
Steps:
1. Announce freeze (UI banner or log): new writes paused
2. Complete in-flight operations (await active tasks < threshold)
3. Export raw DB files: copy `*.db` to `backups/pre-migration/`
4. Generate logical exports (optional): `sqlite3 db .dump > logical.sql`
5. Integrity check: `PRAGMA integrity_check` == "ok" for each DB
6. Version stamp: create `MIGRATION_START` record in a migrations tracking table (create early if absent)

Resume criteria: all integrity checks pass + backups complete.

---

## 🏗️ Phase 2: Schema Evolution
Use idempotent migrations.

Pattern:
```sql
-- Example migration script segment
BEGIN TRANSACTION;
CREATE TABLE IF NOT EXISTS health_reports (...);
CREATE TABLE IF NOT EXISTS health_issues (...);
ALTER TABLE conversations ADD COLUMN task_status TEXT DEFAULT 'open';
ALTER TABLE conversations ADD COLUMN archived INTEGER DEFAULT 0;
ALTER TABLE conversations ADD COLUMN last_action_at TIMESTAMP;
CREATE INDEX IF NOT EXISTS idx_conversations_active ON conversations(archived, last_updated DESC);
COMMIT;
```

Guidelines:
- Group related DDL (self-review tables together, creation tables together)
- Commit after each logical group (limits rollback scope)
- Log start/end + checksum (SHA256 of script) in `migrations` table:
```sql
CREATE TABLE IF NOT EXISTS migrations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  applied_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  checksum TEXT NOT NULL,
  success INTEGER NOT NULL,
  error_message TEXT
);
```

Failure handling:
- On DDL failure: ROLLBACK automatically; record `success=0`
- Abort migration; restore freeze; investigate

Idempotency rules:
- Always `CREATE TABLE IF NOT EXISTS`
- `ALTER TABLE` only if column not present (checked via PRAGMA table_info)
- Index creation with `IF NOT EXISTS`

---

## 🔁 Phase 3: Data Backfill & Initialization
Initialize new tables with minimal seed data.

Tasks:
1. Insert plugin metadata into `plugins` from existing registry config.
2. Create initial baseline health report (placeholder metrics) so dashboards don't 404.
3. Backfill conversation action seeds:
   - For last N (e.g., 50) turns per active session, generate synthetic `conversation_actions` summarizing previous operations if feasible.
4. Populate `creation_sessions` only if resuming previously failed large file writes (optional; else empty).
5. Insert retention snapshot per tier using current config.
6. Add provenance link for migration event itself:
```sql
INSERT INTO provenance_links (source_type, source_ref, target_type, target_ref, relation, confidence)
VALUES ('migration','MIGRATION_START','system','schema_v2','generated',1.0);
```

Performance safeguards:
- Batch inserts (transaction size < 1000 rows for memory safety)
- Measure time; abort if single batch exceeds threshold (e.g., 5s) → review

---

## ✅ Phase 4: Verification & Health Review
Run a structured verification suite:

Categories:
1. Schema Presence
   - All expected tables exist; columns present
2. Permission/Boundary Checks
   - Boundary guard still denying forbidden paths
3. Query Performance Smoke
   - Tier 1 typical query < 100ms
   - Tier 2 pattern search < 200ms
4. Self-Review Execution
   - Run self-review → produces `health_reports` row
5. Maintenance Dry-Run
   - Schedule retrieval → returns plan (no failure)
6. Integrity
   - `PRAGMA foreign_key_check` clean (if foreign keys used)

Example SQL bundle:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='health_reports';
SELECT COUNT(*) FROM plugins;
SELECT overall_status FROM health_reports ORDER BY created_at DESC LIMIT 1;
```

Pass criteria:
- All checks succeed
- No critical self-review issues introduced by migration

---

## 🚀 Phase 5: Cutover
Gradually enable 2.0 features rather than big-bang.

Sequence:
1. Enable plugin hook logging (low impact)
2. Enable self-review scheduling (read-heavy)
3. Enable database maintenance auto-plan (dry-run only)
4. Switch maintenance to active mode (apply changes)
5. Enable incremental creation for large doc generation
6. Expose new schema-driven telemetry in dashboards

Rollback points after each step (verify logs + metrics).

Downtime note: conversation reads remain unblocked; writes resumed after Phase 2 completion.

---

## 📈 Phase 6: Post-Migration Monitoring Window
Duration: 7 days recommended.
Monitor:
- Error rate: plugin_hook_executions failed / total
- Self-review deltas: overall_score trend vs baseline
- Fragmentation after maintenance runs
- Boundary events (unexpected denies/spikes)
- Conversation throughput vs pre-migration

Triggers:
- >5% failed plugin executions → pause new feature enablement
- Self-review drop >15 percentage points → investigate regression
- Fragmentation > threshold repeatedly → maintenance misconfiguration

---

## 🧹 Phase 7: Optimization & Cleanup
Actions:
- Enforce retention (old snapshots, hook executions >30d)
- Compress archival batches >180d (if large)
- Drop any deprecated temporary migration helper tables
- Final self-review; archive migration plan artifact

---

## 🗃️ Migration Script Organization
Proposed directory:
```
src/migrations/
  2025-11-07_001_core_tables.sql
  2025-11-07_002_self_review.sql
  2025-11-07_003_maintenance.sql
  2025-11-07_004_incremental_creation.sql
  2025-11-07_005_conversation_alter.sql
  2025-11-07_006_plugins.sql
  2025-11-07_007_post_verification.sql (optional markers)
```
Execution order = lexical.

Runner skeleton:
```python
# scripts/run_migrations.py
import sqlite3, hashlib, glob, json, time

DBS = {
  'tier1': 'path/to/tier1.db',
  'tier2': 'path/to/tier2.db',
  'tier3': 'path/to/tier3.db'
}

def apply_migration(db_path, script_path):
    with open(script_path,'r',encoding='utf-8') as f:
        sql = f.read()
    checksum = hashlib.sha256(sql.encode()).hexdigest()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS migrations (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, checksum TEXT, success INTEGER, error_message TEXT)")
    try:
        start = time.time()
        cur.executescript(sql)
        cur.execute("INSERT INTO migrations (name, checksum, success) VALUES (?,?,1)", (script_path, checksum))
        conn.commit()
        print(f"✅ {script_path} ({time.time()-start:.2f}s)")
    except Exception as e:
        conn.rollback()
        cur.execute("INSERT INTO migrations (name, checksum, success, error_message) VALUES (?,?,0,?)", (script_path, checksum, str(e)))
        conn.commit()
        print(f"❌ {script_path}: {e}")
        raise
    finally:
        conn.close()

for db_name, db_path in DBS.items():
    print(f"\n🔧 Migrating {db_name} -> {db_path}")
    for script in sorted(glob.glob('src/migrations/*.sql')):
        apply_migration(db_path, script)
```

---

## 🔄 Rollback Strategy
Rollback triggers:
- Integrity check failure
- Critical self-review health status (CRITICAL) newly introduced
- Plugin execution failure spike post-cutover

Rollback actions (tier-specific):
1. Disable new features (set flags in config)
2. Restore DB files from `backups/pre-migration/`
3. Clear in-memory caches referencing new schema objects
4. Re-run baseline verification (ensure 1.0 stability restored)

Data divergence note: any data written into new tables during rollback window will be lost unless selective merge performed—acceptable trade-off (low criticality of early telemetry).

---

## 🧪 Testing Strategy During Migration (Preview of Doc 13)
- Pre-migration: full test suite (must pass 100%)
- After Phase 2: schema smoke tests
- After Phase 3: functional tests covering plugin registration & self-review
- After Phase 5: incremental creation large-file test (controlled 600-line file)
- Daily in window: health report diff assertions (no regression beyond threshold)

---

## ⚠️ Risks & Mitigations
| Risk | Impact | Mitigation |
|------|--------|-----------|
| Long-running backfill | Extended freeze | Limit backfill scope (recent turns only) |
| Partial schema apply | Runtime errors | Transaction groups + idempotent checks |
| Hidden performance regressions | Slow response | Early benchmarks + post-migration trending |
| Rollback complexity | Data/state confusion | Clear time-boxed rollback window + snapshot tagging |
| Missed provenance continuity | Audit gap | Seed provenance link for migration event |

---

## ✅ Success Criteria
- All new tables present & populated minimally
- Baseline self-review score not worse than pre-migration by >5%
- No critical rule compliance issues introduced
- Conversation access latency within ±10% of baseline
- Rollback not needed within monitoring window

---

## 📊 Quick Verification Checklist
```
[ ] Backups present & integrity ok
[ ] All migration scripts applied successfully
[ ] New indices visible (sqlite_master)
[ ] health_reports has ≥1 row
[ ] plugins table populated
[ ] conversations still accessible
[ ] self-review passes with GOOD or better
[ ] maintenance schedule returns plan
[ ] No boundary event anomalies
```

---

**Next:** 13-testing-strategy.md (Expanded automated test coverage for new features)
