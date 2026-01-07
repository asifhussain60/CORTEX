# 🧹 Vacuum v2 - Enhancement Plan

**Plan ID:** `vacuum-v2-2026-01-02`  
**Parent Tracker:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**Priority:** 🟡 P2  
**Created:** January 2, 2026  
**Status:** ⏸️ NOT STARTED  
**Blocked By:** [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md)

---

## 📊 Progress Tracker

```
░░░░░░░░░░░░░░░░░░░░  0% Complete
```

| Phase | Name | Progress | Tasks | Status |
|-------|------|----------|-------|--------|
| -1 | Knowledge Library Consultation | `░░░░░░░░░░` | 0/3 | ⏸️ |
| 0 | Discovery & Requirements | `░░░░░░░░░░` | 0/4 | ⏸️ |
| 1 | MCP Integration | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 2 | Filesystem Scanner | `░░░░░░░░░░` | 0/8 | ⏸️ |
| 3 | Cleanup Engine | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 4 | Reorganization Logic | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 5 | Safety & Validation | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 6 | Testing & Validation | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 7 | REFACTOR & Cleanup | `░░░░░░░░░░` | 0/4 | ⏸️ |

**Total Tasks:** 0/47  
**Estimated Duration:** 2 days

---

## 🎯 Executive Summary

This plan enhances the **Vacuum Orchestrator** to v2.0 with:

1. **MCP Tool Integration** - Invoked via `invoke_orchestrator("vacuum")`
2. **Deep Filesystem Scanner** - Recursive scanning with pattern matching
3. **Smart Cleanup Engine** - Remove orphaned, temporary, duplicate files
4. **Reorganization Logic** - Move files to correct locations
5. **Safety Mechanisms** - Dry-run, backup, undo capability

### Current Problems (v1.0)
- ❌ Orchestrator bypassed (never invoked)
- ❌ Limited file detection
- ❌ No dry-run capability
- ❌ No undo/rollback

### Solutions (v2.0)
- ✅ MCP tool guarantees orchestrator execution
- ✅ Deep recursive scanning
- ✅ Dry-run mode by default
- ✅ Full backup and undo capability

---

## 📋 Phase Details

### Phase -1: Knowledge Library Consultation
**Duration:** 10 minutes

| # | Task | Deliverable |
|---|------|-------------|
| -1.1 | Query cleanup patterns | `context/cleanup-patterns.md` |
| -1.2 | Query filesystem operations | `context/filesystem-ops.md` |
| -1.3 | Query safety patterns | `context/safety-patterns.md` |

### Phase 0: Discovery & Requirements
**Duration:** 1 hour

| # | Task | Deliverable |
|---|------|-------------|
| 0.1 | Review current vacuum logic | Analysis document |
| 0.2 | Define v2.0 API contract | `artifacts/api-contract.md` |
| 0.3 | Map file categories | Category mapping |
| 0.4 | Create test strategy | `artifacts/test-strategy.md` |

### Phase 1: MCP Integration
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 1.1 | Implement MCP entry point | `execute_from_mcp()` |
| 1.2 | Add context parsing | Context extraction |
| 1.3 | Add path parameter handling | Path validation |
| 1.4 | Add registry entry | Registry update |
| 1.5 | Write unit tests | Test cases |
| 1.6 | Documentation | Docstrings |

### Phase 2: Filesystem Scanner
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Implement recursive scanner | Scanner class |
| 2.2 | Add pattern matching | Glob patterns |
| 2.3 | Add file categorization | Categories |
| 2.4 | Detect orphaned files | Detection |
| 2.5 | Detect duplicate files | Hash comparison |
| 2.6 | Detect temp files | Temp detection |
| 2.7 | Generate scan report | Report |
| 2.8 | Write tests | Test cases |

### Phase 3: Cleanup Engine
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 3.1 | Implement dry-run mode | Dry-run logic |
| 3.2 | Implement file deletion | Delete logic |
| 3.3 | Implement backup creation | Backup logic |
| 3.4 | Add progress tracking | Progress |
| 3.5 | Generate cleanup report | Report |
| 3.6 | Write tests | Test cases |

### Phase 4: Reorganization Logic
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 4.1 | Define target locations | Location mapping |
| 4.2 | Implement file movement | Move logic |
| 4.3 | Update references | Reference updates |
| 4.4 | Generate move report | Report |
| 4.5 | Write tests | Test cases |

### Phase 5: Safety & Validation
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 5.1 | Implement undo capability | Undo logic |
| 5.2 | Add confirmation prompts | User prompts |
| 5.3 | Add protected paths | Path protection |
| 5.4 | Add size limits | Limits |
| 5.5 | Validate operations | Validation |
| 5.6 | Write tests | Test cases |

### Phase 6: Testing & Validation
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 6.1 | Unit test coverage | ≥80% coverage |
| 6.2 | Integration test: full flow | E2E test |
| 6.3 | Integration test: MCP invocation | MCP test |
| 6.4 | Fix failing tests | Bug fixes |
| 6.5 | Final validation | Sign-off |

### Phase 7: REFACTOR & Cleanup
**Duration:** 1 hour

| # | Task | Deliverable |
|---|------|-------------|
| 7.1 | Remove orphaned code | Clean code |
| 7.2 | Fix code smells | Refactored code |
| 7.3 | Add documentation | Docstrings |
| 7.4 | Update type hints | Type annotations |

---

## 📐 Architecture

### Current (v1.0)
```
vacuum (system orchestrator)
└── Basic file cleanup (limited)
```

### Target (v2.0)
```
vacuum_orchestrator.py
├── execute_from_mcp(context)     # Entry from MCP tool
├── scan_filesystem(path)         # Deep recursive scan
├── categorize_files()            # Categorization
├── detect_orphaned()             # Orphan detection
├── detect_duplicates()           # Duplicate detection
├── cleanup_files(dry_run=True)   # Safe cleanup
├── reorganize_files()            # Move to correct locations
├── create_backup()               # Backup before cleanup
└── undo_operations()             # Rollback capability
```

---

## 🔗 Dependencies

### Upstream
- [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md) (MUST complete first)

### Downstream
- None

### Shared Components
- File system utilities
- Backup manager

---

## ✅ Definition of Done

- [ ] MCP tool invokes orchestrator successfully
- [ ] Filesystem scanner detects all file types
- [ ] Dry-run mode works correctly
- [ ] Backup created before cleanup
- [ ] Undo capability functional
- [ ] Protected paths respected
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests passing
- [ ] REFACTOR phase complete

---

## 📞 Copilot Instructions

```yaml
plan_id: vacuum-v2-2026-01-02
priority: P2
depends_on: mcp-tool-infrastructure
tdd_enforcement: mandatory
deliverable: src/orchestrators/vacuum_orchestrator.py
test_coverage_target: 80%
safety_first: true
dry_run_default: true
```

---

**⬆️ Back to:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**⬅️ Depends on:** [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md)  
**➡️ Parallel:** [ADO Operations v2](../ado-operations-v2/00-master-plan.md)
