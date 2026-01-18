# PHASE-VAC-001: MD Organizer Feature — Executive Summary

**Date:** 2026-01-17  
**Status:** PLANNED  
**Initiator:** CORTEX Builder  
**From Request:** chat01.md (MD Organization Task)  

---

## WHAT IS THIS PHASE?

Converts the MD Document Organization task (from chat01.md) into a **production-grade feature of the Vacuum Orchestrator** that can be invoked by the Housekeeping Orchestrator on a schedule.

**Key Innovation:** Implements a **SOLID-compliant plugin architecture** for pluggable "cleaners" so additional housekeeping operations (Python cache, backups, logs) can be added in future phases without modifying the orchestrator.

---

## THE TRANSFORMATION

### BEFORE (chat01.md)
```
Standalone task to:
- Review all *.md files
- Delete non-essential ones
- Reorganize into .github/docs
- Rename to kebab-case
```

### AFTER (PHASE-VAC-001)
```
Pluggable "MDOrganizerCleaner" component that:
- Implements CleanerInterface (SOLID abstraction)
- Registers with VacuumOrchestrator
- Can be invoked by HousekeepingOrchestrator on schedule
- Follows analyze → execute → verify → rollback pattern
- Enables future cleaners (Python cache, backups, etc.)
  without modifying orchestrator code
```

---

## ARCHITECTURE: SOLID DESIGN

The cleaner plugin architecture follows all five SOLID principles:

| Principle | Implementation |
|-----------|-----------------|
| **S**ingle Responsibility | Each cleaner handles one domain (MD, cache, backups) |
| **O**pen/Closed | New cleaners added WITHOUT modifying VacuumOrchestrator |
| **L**iskov Substitution | All cleaners swap via identical CleanerInterface |
| **I**nterface Segregation | CleanerInterface minimal: `analyze()`, `execute()`, `rollback()` |
| **D**ependency Inversion | Orchestrator depends on abstraction, not concrete implementations |

**Visual Structure:**
```
VacuumOrchestrator (coordinator)
├── CleanerInterface (abstraction)
│   ├── MDOrganizerCleaner (first implementation)
│   ├── PythonCacheCleaner (future)
│   ├── BackupCleaner (future)
│   └── LogArchiver (future)
└── CleanerRegistry (plugin manager)
```

---

## SCOPE: 5 ACCEPTANCE CRITERIA

| AC-ID | Title | Blocks | Purpose |
|-------|-------|--------|---------|
| **VAC-001-01** | Cleaner Plugin Architecture | All others | SOLID foundation for pluggable cleaners |
| **VAC-001-02** | MD Analyzer | VAC-001-03,04 | Non-destructive analysis engine |
| **VAC-001-03** | MD Executor | VAC-001-04 | Controlled execution with rollback |
| **VAC-001-04** | VacuumOrchestrator Integration | VAC-001-05 | Wire into orchestrator framework |
| **VAC-001-05** | Execute on Current Repo | (Final) | Validate on real CORTEX state |

---

## SAFETY & AUDITABILITY

✅ **Deterministic:** Operations recorded in governance.db audit trail  
✅ **Reversible:** Pre-execution snapshot enables full rollback  
✅ **Governed:** Follows CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)  
✅ **Reference-Safe:** Cross-file references tracked and updated automatically  
✅ **Protected:** Essential files (README.md) never touched  

---

## ASSUMPTIONS

| Assumption | Source | Status |
|-----------|--------|--------|
| PHASE-06-ECOSYSTEM completed (orchestrator framework exists) | architecture | ✅ VERIFIED |
| vacuum/config.yaml has classification rules | workspace | ✅ EXISTS |
| Git checkpoints work as described | CORE-026 | ✅ VERIFIED |
| VacuumOrchestrator can be extended | design | ✅ CONFIRMED |

---

## RISKS & BLOCKERS

**Risks:** 
- MEDIUM: Broken references after reorganization → Mitigated by reference tracker + validation
- LOW: Incorrect file classification → Mitigated by protected files list + dry-run mode
- LOW: Naming conflicts → Mitigated by collision detection

**Blockers:**  
- None identified

---

## IMPACT ASSESSMENT

### What WILL be delivered:
- ✅ CleanerInterface (abstract base for all cleaners)
- ✅ MDOrganizerCleaner (first concrete implementation)
- ✅ CleanerRegistry (plugin manager)
- ✅ VacuumOrchestrator enhancements
- ✅ MD documents reorganized (chat01.md requirement complete)
- ✅ Foundation for future cleaners (PHASE-VAC-002, VAC-003, etc.)

### What WILL change:
- `.github/docs/` reorganized with nested structure
- Root .md files reorganized or deleted (per config.yaml rules)
- VacuumOrchestrator supports plugin pattern

### What WILL NOT change:
- `README.md` (protected)
- `pytest.ini`, `requirements.txt` (protected)
- `cortex-brain/state/governance.db*` (protected)
- Prompts in `.github/prompts/` (preserved per chat01.md)

---

## GOVERNANCE

**Tier 0 Rules Enforced:**
- CORE-008: Tests first (RED → GREEN)
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings on all public APIs
- CORE-026: Git checkpoint before major action
- CORE-027: AC_START, AC_EXECUTE, AC_COMPLETE audit entries
- CORE-028: Kebab-case names, ≤25 characters

**Phase-Specific Rules:**
- CleanerInterface immutable after VAC-001-01 completes
- Protected files list enforced at all times
- Dry-run mode mandatory before execution
- Snapshot required before execute()

---

## PARALLEL EXECUTION

✅ **Parallel Track:** Can be developed independently from PHASE-15 (Neural Observatory)  
✅ **No Blocking:** Does not block other phases  
⏳ **Blocks VAC-002:** Python Cache Cleaner depends on cleaner architecture  

---

## NEXT STEPS

| Step | Owner | Duration |
|------|-------|----------|
| 1. Git Checkpoint | Builder | 1 min |
| 2. Implement VAC-001-01 (Plugin Architecture) | DEV | 4 hours |
| 3. Implement VAC-001-02 (MD Analyzer) | DEV | 6 hours |
| 4. Implement VAC-001-03 (MD Executor) | DEV | 8 hours |
| 5. Implement VAC-001-04 (Integration) | DEV | 4 hours |
| 6. Execute VAC-001-05 (Live Reorganization) | DEV | 2 hours |

**Total Duration:** 3 days (24 hours)

---

## DECISION

**RECOMMENDATION:** ✅ **PROCEED**

This phase:
1. ✅ Transforms a standalone task into an architected feature
2. ✅ Establishes SOLID-compliant plugin pattern
3. ✅ Enables rapid addition of future cleaners
4. ✅ Maintains full safety (rollback, audit, protection)
5. ✅ Completes chat01.md requirement
6. ✅ Does not block other phases

**Action:** Create git checkpoint, then implement VAC-001-01 (CleanerInterface)
