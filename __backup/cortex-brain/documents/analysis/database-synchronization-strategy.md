# Database Synchronization Strategy for Multi-Machine CORTEX Deployment

**Purpose:** Resolve SQLite database sync challenges in cortex-git-commit workflow  
**Problem:** Code commits without DB state → pulling machines break due to layer desynchronization  
**Version:** 1.0.0  
**Date:** 2026-01-12  
**Author:** Asif Hussain  
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

## 🚨 Problem Statement

### Current Architecture

CORTEX 6.0 uses SQLite databases for stateful intelligence:

```
cortex-brain/database/
├── governance.db                    # Audit trail (hash chains), enforcement logs
├── tier1-working-memory.db          # Active epic, TODO queues, progress state
├── tier2-knowledge-graph.db         # Knowledge patterns, learned behaviors
├── tier3-context.db                 # Development context, session history
└── [all in .gitignore - NOT tracked]
```

### The Desynchronization Problem

**Scenario:**
1. **Machine A** implements AC-AUDIT-007 (hash chain integrity)
   - Code commits: `src/infrastructure/enhanced_audit_logger.py`
   - DB updates: `governance.db` has audit entries with correlation IDs
   - Git commit: Code pushed, DB NOT pushed (in .gitignore)

2. **Machine B** pulls latest code
   - Receives: New code expecting DB tables/entries from Machine A
   - Missing: `governance.db` state (audit entries, hash chain links)
   - **RESULT:** Runtime errors when code queries non-existent DB state

**Example Failure:**
```python
# Code on Machine B (pulled from Machine A)
def validate_audit_chain(correlation_id):
    cursor.execute("SELECT * FROM audit_log WHERE correlation_id = ?", (correlation_id,))
    # ERROR: table audit_log doesn't exist (DB schema not migrated)
    # ERROR: no entries found (Machine A's audit trail missing)
```

### Root Cause

**Code and database state have different lifecycles:**
- Code → Git-tracked, synchronized across machines
- Database → Machine-local, diverges per machine
- **Violation:** Code references DB state that doesn't exist on pulling machine

---

## 🎯 Solution Framework: 3-Tier Synchronization Strategy

### Tier 0: Schema-Driven Database (Git-Tracked Migrations)

**Principle:** Databases are **empty containers** (schema only), populated at runtime.

**Strategy:**
```
cortex-brain/database/migrations/
├── 001_create_audit_log.sql              # CREATE TABLE audit_log (...)
├── 002_create_working_memory.sql         # CREATE TABLE epic_state (...)
├── 003_create_knowledge_graph.sql        # CREATE TABLE patterns (...)
├── 004_add_correlation_id_index.sql      # CREATE INDEX idx_corr_id ON audit_log(...)
└── migration_registry.yaml               # Version tracking

.gitignore:
  cortex-brain/database/*.db              # Actual DB files NOT tracked
```

**On Machine B (after pull):**
```python
# Auto-run on startup (src/infrastructure/database_initializer.py)
def initialize_databases():
    for migration in get_pending_migrations():
        apply_migration(migration)  # Creates tables if missing
    
    # DB now has schema but is EMPTY (no Machine A data)
    # This is CORRECT - each machine builds its own audit trail
```

**Benefit:** Code expects schema (tables/columns), NOT specific data → no runtime errors.

---

### Tier 1: Exported State Snapshots (Git-Tracked YAML/JSON)

**Principle:** Critical state exported to **human-readable, git-trackable** format.

**Strategy:**
```
cortex-brain/tier1/tracking/
├── progress-tracker.json                 # Exported from tier1-working-memory.db
├── active-todos.yaml                     # Exported TODO queue
└── epic-checkpoints.yaml                 # Phase completion markers

cortex-brain/tier1/acceptance-criteria/
└── AC-INDEX.yaml                         # AC-ID registry (SSOT)

cortex-brain/tier0/governance/
└── core-rules.yaml                       # Governance rules (SSOT)
```

**Workflow:**
1. **Machine A** completes AC-AUDIT-007
2. **MasterOrchestrator** updates `tier1-working-memory.db` (local)
3. **StateManager** exports to `progress-tracker.json` (git-tracked)
4. **Git commit** includes `progress-tracker.json` (NOT the DB)
5. **Machine B** pulls `progress-tracker.json`
6. **StateManager** imports to `tier1-working-memory.db` (local rebuild)

**Code Pattern:**
```python
# src/infrastructure/state_manager.py
def sync_state_to_git():
    """Export DB state to git-tracked files."""
    db_state = load_from_db("tier1-working-memory.db")
    export_to_yaml("progress-tracker.json", db_state)
    # Git commits progress-tracker.json
    
def sync_state_from_git():
    """Import git-tracked files to DB (on pull)."""
    git_state = load_from_yaml("progress-tracker.json")
    import_to_db("tier1-working-memory.db", git_state)
    # DB now has Machine A's progress state
```

**Benefit:** Machines share progress state WITHOUT committing binary DB files.

---

### Tier 2: Audit Trail Preservation (Append-Only Export)

**Principle:** Audit logs are **append-only, immutable** → export incrementally, never overwrite.

**Strategy:**
```
cortex-brain/audit-logs/
├── 2026-01-12-session-a7f3b21c.jsonl     # Machine A's audit entries
├── 2026-01-12-session-b9e4c32d.jsonl     # Machine B's audit entries
└── audit-index.yaml                      # Correlation ID registry

Format: JSONL (one JSON object per line, append-only)
```

**Workflow:**
1. **Machine A** completes work session
2. **AuditLogger** exports to `audit-logs/{date}-session-{correlation_id}.jsonl`
3. **Git commit** includes audit export (NOT governance.db)
4. **Machine B** pulls audit exports
5. **AuditLogger** merges exports into local `governance.db` (on startup)

**Code Pattern:**
```python
# src/infrastructure/enhanced_audit_logger.py
def export_session_audit(correlation_id):
    """Export audit entries for session to JSONL."""
    entries = db.query("SELECT * FROM audit_log WHERE correlation_id = ?", (correlation_id,))
    with open(f"audit-logs/{date}-session-{correlation_id}.jsonl", "a") as f:
        for entry in entries:
            f.write(json.dumps(entry) + "\n")
    # Git commits JSONL file

def import_audit_exports():
    """Import all JSONL files into local governance.db."""
    for jsonl_file in glob("audit-logs/*.jsonl"):
        with open(jsonl_file) as f:
            for line in f:
                entry = json.loads(line)
                db.insert("audit_log", entry, on_conflict="ignore")
    # DB now has audit trail from all machines
```

**Benefit:** Complete audit trail across machines WITHOUT binary DB files in git.

---

### Tier 3: Knowledge Patterns (Git-Tracked YAML)

**Principle:** Learned patterns are **git-trackable metadata**, not operational state.

**Strategy:**
```
cortex-brain/tier3/patterns/
├── git-operations.yaml                   # Learned conflict resolution patterns
├── tdd-workflows.yaml                    # Learned TDD best practices
└── governance-violations.yaml            # Common violation patterns

# tier3-context.db used for RUNTIME queries only, populated from YAML on startup
```

**Workflow:**
1. **Machine A** learns new pattern (e.g., "React imports cause merge conflicts")
2. **Tier3Manager** stores in `tier3-context.db` (local)
3. **Tier3Manager** exports to `tier3/patterns/git-operations.yaml`
4. **Git commit** includes YAML pattern file
5. **Machine B** pulls pattern YAML
6. **Tier3Manager** imports to `tier3-context.db` (local rebuild)

**Benefit:** Shared intelligence across machines WITHOUT binary DB sync.

---

## 📋 Updated cortex-git-commit Workflow

### Stage 4.5: Pre-Commit State Export (NEW)

**Added after Stage 4 (Validate Working Tree), before Stage 5 (Commit):**

```yaml
Operation: Export Database State to Git-Tracked Files

Steps:
  1. Export working memory:
     Command: python3 -m src.infrastructure.state_manager export
     Output: progress-tracker.json, active-todos.yaml
  
  2. Export audit session:
     Command: python3 -m src.infrastructure.enhanced_audit_logger export_session
     Output: audit-logs/{date}-session-{correlation_id}.jsonl
  
  3. Export learned patterns:
     Command: python3 -m src.infrastructure.tier3_manager export_patterns
     Output: tier3/patterns/*.yaml
  
  4. Stage exported files:
     Command: git add cortex-brain/tier1/tracking/*.{json,yaml}
     Command: git add cortex-brain/audit-logs/*.jsonl
     Command: git add cortex-brain/tier3/patterns/*.yaml
  
  5. Log to audit:
     Event: STATE_EXPORTED_FOR_GIT
     Data: {files_exported, export_size_bytes, correlation_id}

Success Criteria:
  - All state files exported
  - Files staged for commit
  - Audit entry written

Failure Mode: Export fails → ABORT commit (state not synchronized)
```

### Stage 2.5: Post-Pull State Import (NEW)

**Added to Machine Alignment Protocol (Section: Pull and Synchronization):**

```yaml
Operation: Import Git-Tracked State to Database

Steps:
  1. Detect pulled state files:
     Command: git diff HEAD@{1} HEAD --name-only | grep "progress-tracker.json\|audit-logs/\|tier3/patterns/"
  
  2. Import working memory:
     Command: python3 -m src.infrastructure.state_manager import
     Input: progress-tracker.json, active-todos.yaml
     Output: tier1-working-memory.db updated
  
  3. Import audit exports:
     Command: python3 -m src.infrastructure.enhanced_audit_logger import_exports
     Input: audit-logs/*.jsonl
     Output: governance.db updated (append-only)
  
  4. Import learned patterns:
     Command: python3 -m src.infrastructure.tier3_manager import_patterns
     Input: tier3/patterns/*.yaml
     Output: tier3-context.db updated
  
  5. Validate DB integrity:
     Command: python3 -m src.infrastructure.database_validator check_all
     Checks: Schema version, foreign key constraints, index coverage
  
  6. Log to audit:
     Event: STATE_IMPORTED_FROM_GIT
     Data: {files_imported, db_version, correlation_id}

Success Criteria:
  - All state files imported
  - DB schema up-to-date
  - No foreign key violations
  - Audit entry written

Failure Mode: Import fails → ALERT (manual remediation), but don't block pull
```

---

## 🔧 Implementation Checklist

### Phase 1: Database Migration System (Week 1)

- [ ] Create `cortex-brain/database/migrations/` directory
- [ ] Extract schema from existing DBs to SQL migration files
- [ ] Implement `DatabaseMigrator` class (apply migrations, track versions)
- [ ] Add migration check to startup (auto-apply pending migrations)
- [ ] Test: Fresh machine applies all migrations, DB schema matches

### Phase 2: State Export/Import (Week 2)

- [ ] Implement `StateManager.export()` (DB → progress-tracker.json)
- [ ] Implement `StateManager.import()` (progress-tracker.json → DB)
- [ ] Implement `AuditLogger.export_session()` (DB → JSONL)
- [ ] Implement `AuditLogger.import_exports()` (JSONL → DB)
- [ ] Implement `Tier3Manager.export_patterns()` (DB → YAML)
- [ ] Implement `Tier3Manager.import_patterns()` (YAML → DB)
- [ ] Test: Export on Machine A, import on Machine B, verify state matches

### Phase 3: Git Workflow Integration (Week 3)

- [ ] Add Stage 4.5 (Pre-Commit State Export) to `vacuum_orchestrator.py`
- [ ] Add post-pull import to Machine Alignment Protocol
- [ ] Update `.gitignore` (databases excluded, exports included)
- [ ] Add pre-commit hook (verify state exported)
- [ ] Add post-merge hook (auto-import state)
- [ ] Test: Full workflow (commit on A, pull on B, verify no runtime errors)

### Phase 4: Documentation & Validation (Week 4)

- [ ] Update `cortex-git-commit.prompt.md` with new stages
- [ ] Update `machine-alignment-guide.md` with import commands
- [ ] Create runbook: "Troubleshooting State Sync Issues"
- [ ] Add validation script: `verify_state_sync.py`
- [ ] Integrate into deployment gate (Gate 50: State Sync Verification)
- [ ] Test: Onboard new machine, verify full functionality

---

## 🎯 Benefits of This Strategy

### Benefit 1: No Binary Files in Git
- ✅ SQLite databases stay in `.gitignore`
- ✅ Only human-readable YAML/JSON/JSONL in git
- ✅ Smaller repo size, faster pulls
- ✅ Easier code review (diffs are readable)

### Benefit 2: Zero Runtime Failures on Pull
- ✅ Schema migrations auto-apply (tables exist)
- ✅ State imports auto-run (data synchronized)
- ✅ Code never references missing DB state
- ✅ Each machine has complete operational context

### Benefit 3: Complete Audit Trail
- ✅ Audit exports from ALL machines in git
- ✅ Full traceability across sessions
- ✅ Hash chain integrity maintained
- ✅ Compliance-ready (SOC 2, GDPR)

### Benefit 4: Shared Intelligence
- ✅ Learned patterns propagate across machines
- ✅ Knowledge graph unified
- ✅ Best practices automatically adopted
- ✅ No "lost learning" when switching machines

### Benefit 5: Graceful Degradation
- ✅ If import fails, machine still functional (just missing remote state)
- ✅ Alert generated, but doesn't block work
- ✅ Manual remediation possible (re-export/re-import)
- ✅ No catastrophic failures

---

## ⚠️ Trade-offs & Risks

### Trade-off 1: Commit Size Increase
- **Impact:** Commits include state exports (JSON/YAML/JSONL)
- **Mitigation:** Compress exports, rotate old audit logs (>30 days)
- **Acceptable:** Text files compress well, repo stays manageable

### Trade-off 2: Import Latency on Pull
- **Impact:** Post-pull import adds ~5-10 seconds
- **Mitigation:** Background import (async), show progress spinner
- **Acceptable:** One-time cost per pull, prevents runtime errors

### Trade-off 3: Merge Conflicts on State Files
- **Impact:** If two machines update progress-tracker.json simultaneously
- **Mitigation:** Value-based conflict resolution (use newer timestamp)
- **Acceptable:** Rare (most work is sequential), auto-resolvable

### Risk 1: Export Failure → Incomplete State
- **Scenario:** StateManager fails to export, commit proceeds anyway
- **Prevention:** Pre-commit hook BLOCKS if export fails
- **Recovery:** Re-run export manually, amend commit

### Risk 2: Import Failure → Stale State
- **Scenario:** Machine B fails to import, uses old DB state
- **Prevention:** Validation gate checks DB version matches git state
- **Recovery:** Alert user, provide manual import command

---

## 📊 Success Metrics

Track these KPIs to validate strategy effectiveness:

- **State Sync Success Rate:** Target >99% (import succeeds on pull)
- **Runtime Error Rate:** Target 0% (no DB-related failures after pull)
- **Commit Size Growth:** Target <5% increase (compressed exports)
- **Import Latency:** Target <10 seconds (background import)
- **Merge Conflict Rate:** Target <2% on state files (auto-resolvable)

---

## 🔄 Migration Path (Existing Deployments)

For machines already running CORTEX 6.0 without this strategy:

### Step 1: Backup Existing Databases
```bash
cp cortex-brain/database/*.db cortex-brain/database/backup/
```

### Step 2: Export Current State
```bash
python3 -m src.infrastructure.state_manager export --force
python3 -m src.infrastructure.enhanced_audit_logger export_all_sessions
python3 -m src.infrastructure.tier3_manager export_patterns
```

### Step 3: Commit Exports
```bash
git add cortex-brain/tier1/tracking/*.{json,yaml}
git add cortex-brain/audit-logs/*.jsonl
git add cortex-brain/tier3/patterns/*.yaml
git commit -m "chore: export database state for git-tracked sync"
```

### Step 4: Pull on Other Machines
```bash
git pull origin CORTEX6
python3 -m src.infrastructure.state_manager import
python3 -m src.infrastructure.enhanced_audit_logger import_exports
python3 -m src.infrastructure.tier3_manager import_patterns
```

### Step 5: Validate Sync
```bash
python3 scripts/verify_state_sync.py
```

---

## 📚 Related AC-IDs

- **AC-GIT-006:** Database state export/import for multi-machine sync
- **AC-STATE-004:** StateManager export to git-tracked files
- **AC-AUDIT-009:** Audit trail export to JSONL (append-only)
- **AC-TIER3-005:** Knowledge pattern export to YAML

---

## 🆘 Troubleshooting

### Issue: Import fails with "schema version mismatch"

**Cause:** Machine B has older schema than exported state expects

**Solution:**
```bash
# Apply pending migrations
python3 -m src.infrastructure.database_migrator apply_all

# Retry import
python3 -m src.infrastructure.state_manager import
```

### Issue: Merge conflict in progress-tracker.json

**Cause:** Two machines updated tracker simultaneously

**Solution:**
```bash
# Use value-based resolution (newer timestamp wins)
python3 -m src.tools.git_operations resolve_state_conflict progress-tracker.json --strategy newest

# Or manual: Keep version with more recent "last_updated" timestamp
```

### Issue: Audit logs missing after pull

**Cause:** Export didn't include session JSONL files

**Solution:**
```bash
# On pushing machine (Machine A): Re-export session
python3 -m src.infrastructure.enhanced_audit_logger export_session --correlation-id {correlation_id}

# On pulling machine (Machine B): Pull again, then import
git pull origin CORTEX6
python3 -m src.infrastructure.enhanced_audit_logger import_exports
```

---

## 📖 References

- `cortex-brain/documents/operations/machine-alignment-guide.md` (Section: Pull and Synchronization)
- `.github/prompts/archive/cortex-git-commit.prompt.md` (Updated workflow)
- `src/infrastructure/state_manager.py` (Export/import implementation)
- `src/infrastructure/enhanced_audit_logger.py` (Audit export/import)
- `cortex-brain/database/migrations/README.md` (Migration system docs)

---

**Version:** 1.0.0  
**Status:** Approved for implementation (Phase 1-4 roadmap defined)  
**Next Steps:** Implement Phase 1 (Database Migration System)  
**Review Date:** 2026-02-01

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**  
This document is part of the CORTEX 6.0 Production-Grade AI Orchestration System.
