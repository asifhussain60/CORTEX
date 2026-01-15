# CORTEX Multi-Machine Development Strategy
## State Synchronization & Developer Onboarding Protocol

**Date:** January 15, 2026  
**Status:** PROPOSED  
**Scope:** Database sync, audit portability, edge case handling

---

## Executive Summary

### The Problem
CORTEX uses SQLite (`governance.db`) for runtime state (audit logs, phase locks, AC index). This creates challenges:

1. **Binary merge conflicts** - SQLite files can't be merged by git
2. **WAL file pollution** - `-shm` and `-wal` are runtime artifacts
3. **State divergence** - Each developer's local audit log differs
4. **Onboarding friction** - New machines need database initialization

### The Solution: "Source as Truth, Database as Cache"

The YAML files in `cortex-brain/` and `.github/roadmap/` are the **source of truth**. The SQLite database is a **derived cache** for fast runtime queries. This is already the design - we just need to formalize the sync protocol.

---

## Strategy: Minimal Changes, Maximum Compatibility

### Principle 1: YAML is Truth, SQLite is Derived

| Layer | Files | Git Tracked | Purpose |
|-------|-------|-------------|---------|
| **Source of Truth** | `cortex-master.yaml`, `*.yaml` | ✅ Yes | Authoritative state |
| **Derived Cache** | `governance.db` | ✅ Yes* | Fast queries |
| **Runtime Artifacts** | `*.db-shm`, `*.db-wal` | ❌ No | Transient |

*Database tracked for convenience, but can be regenerated from YAML.

### Principle 2: Idempotent Initialization

The `init_db.py` script already exists. Enhance it to be idempotent:
- Safe to run multiple times
- Merges new data without losing existing
- Exports audit logs before reset (if needed)

### Principle 3: Audit Logs are Local Context

Audit logs in SQLite track **local operations** (what this machine did). They don't need to sync across machines because:
- The YAML files capture **what was decided** (source of truth)
- The audit logs capture **how it was executed** (local context)
- Hash chain integrity is verified **locally**

---

## Implementation Plan

### Step 1: Gitignore Runtime Artifacts (Immediate)

Add to `.gitignore`:
```
# SQLite runtime artifacts (NOT the database itself)
cortex-brain/state/*.db-shm
cortex-brain/state/*.db-wal
```

**Rationale:** The `-shm` (shared memory) and `-wal` (write-ahead log) files are transient. They cause merge issues and contain uncommitted transactions.

### Step 2: Enhance init_db.py (Immediate)

Create idempotent initialization that:
1. Preserves existing audit logs (don't truncate)
2. Syncs AC index from `cortex-master.yaml`
3. Syncs phase locks from `phase_tracker`
4. Reports what was updated

```python
# Enhanced init_db.py behavior
def sync_from_yaml():
    """Sync database state from YAML sources."""
    # 1. Read cortex-master.yaml phase_tracker
    # 2. Update phase_locks table (upsert)
    # 3. Update ac_index table (upsert)
    # 4. DO NOT touch audit_log (local context)
    # 5. Return sync report
```

### Step 3: Add Post-Pull Hook (Optional - PHASE-09)

Git hook that runs after `git pull`:
```bash
#!/bin/bash
# .git/hooks/post-merge
python scripts/init_db.py --sync-only
```

This ensures database is always in sync with YAML after pull.

### Step 4: Export Audit Summary (Optional - PHASE-13)

For audit compliance, export summary to JSON:
```
cortex-brain/audit-logs/
├── rollback-history.json     # Existing ✓
├── audit-summary-{date}.json # New: Daily summary export
└── .gitkeep
```

---

## Edge Cases Addressed

### Edge Case 1: Fresh Clone
**Scenario:** Developer clones repo for the first time.
**Solution:** Run `python scripts/init_db.py`
- Creates `governance.db` if missing
- Populates from YAML sources
- Ready to develop

### Edge Case 2: Pull After Others Made Changes
**Scenario:** Developer pulls after phase was locked by another.
**Solution:** 
- Database file updates via git (binary, but deterministic)
- If conflicts: delete local db, run `init_db.py`
- YAML is source of truth, so no data loss

### Edge Case 3: Concurrent Development (Same Phase)
**Scenario:** Two developers working on same phase.
**Solution:**
- Each has local audit log (different entries, both valid)
- Phase lock is controlled by YAML (single source)
- On merge: YAML wins, databases regenerate

### Edge Case 4: Database Corruption
**Scenario:** SQLite file becomes corrupted.
**Solution:**
- Delete `governance.db`, `governance.db-shm`, `governance.db-wal`
- Run `python scripts/init_db.py`
- All state recovered from YAML

### Edge Case 5: Offline Development
**Scenario:** Developer works offline, then syncs.
**Solution:**
- Local audit log captures all operations
- On sync: YAML changes merged via git
- Run `init_db.py --sync-only` to update db

### Edge Case 6: CI/CD Pipeline
**Scenario:** Automated testing needs database.
**Solution:**
- CI runs `python scripts/init_db.py` at start
- Tests use fresh database each run
- No state carried between runs

---

## Decision Matrix

| Approach | Complexity | Risk | Compatibility |
|----------|------------|------|---------------|
| ❌ Stop tracking db | Low | Medium | Breaks existing |
| ❌ JSON-only audit | High | Low | Major rewrite |
| ✅ **Track db, ignore WAL** | **Low** | **Low** | **100%** |
| ❌ DB sync protocol | High | Medium | Complex |

**Recommendation:** Option 3 - Track database, gitignore WAL files, enhance init_db.py

---

## Implementation Checklist

### Immediate (No Code Changes)
- [ ] Add `.db-shm` and `.db-wal` to `.gitignore`
- [ ] Document in README: "Run `python scripts/init_db.py` after clone"

### Short-term (Minor Enhancement)
- [ ] Enhance `init_db.py` with `--sync-only` flag
- [ ] Add sync logic to read from `cortex-master.yaml`
- [ ] Make initialization idempotent (safe to re-run)

### Medium-term (PHASE-09: Developer Governance Tooling)
- [ ] Add post-merge git hook
- [ ] Create `cortex-governance sync` CLI command
- [ ] IDE integration for state awareness

### Long-term (PHASE-13: Production Rollout)
- [ ] Audit summary export for compliance
- [ ] Multi-team state federation (if needed)
- [ ] Dashboard showing cross-machine state

---

## Integration with Existing Roadmap

This strategy aligns with:

1. **PHASE-09-ADAPTIVE-EXECUTION** (GV-003-01: Pre-commit Hook)
   - Extend to post-merge hook for db sync

2. **PHASE-08-GOVERNANCE-TOOLS** (GV-001-01: CLI Query Interface)
   - Add `cortex-governance sync` command

3. **PHASE-13-PRODUCTION-MIGRATION** (PR-001: Operational Readiness)
   - Multi-machine audit federation

---

## Summary

**No major modifications needed.** The existing design is sound:

1. ✅ YAML is already source of truth
2. ✅ Database is already derivable from YAML
3. ✅ `init_db.py` already exists

**Minimal changes:**
1. Gitignore WAL files (2 lines)
2. Enhance `init_db.py` (idempotent sync)
3. Document the protocol (this file)

**Result:** Any machine can:
1. Clone repo
2. Run `pip install -r requirements.txt`
3. Run `python scripts/init_db.py`
4. Start developing

The audit logs are **local context** - they don't need to sync. What matters (phase locks, AC status) is in YAML and **does** sync.
