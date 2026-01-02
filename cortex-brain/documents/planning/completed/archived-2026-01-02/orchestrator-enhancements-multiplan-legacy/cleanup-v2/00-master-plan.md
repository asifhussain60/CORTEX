# 🗑️ Cleanup v2 - Enhancement Plan

**Plan ID:** `cleanup-v2-2026-01-02`  
**Parent Tracker:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**Priority:** 🟢 P3 (Last)  
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
| -1 | Knowledge Library Consultation | `░░░░░░░░░░` | 0/2 | ⏸️ |
| 0 | Discovery & Requirements | `░░░░░░░░░░` | 0/3 | ⏸️ |
| 1 | MCP Integration | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 2 | Cache Management | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 3 | Temp File Cleanup | `░░░░░░░░░░` | 0/4 | ⏸️ |
| 4 | Bloat Detection | `░░░░░░░░░░` | 0/4 | ⏸️ |
| 5 | Testing & Validation | `░░░░░░░░░░` | 0/4 | ⏸️ |
| 6 | REFACTOR & Cleanup | `░░░░░░░░░░` | 0/3 | ⏸️ |

**Total Tasks:** 0/30  
**Estimated Duration:** 1 day

---

## 🎯 Executive Summary

This plan enhances the **Cleanup Orchestrator** to v2.0 with:

1. **MCP Tool Integration** - Invoked via `invoke_orchestrator("cleanup")`
2. **Cache Management** - Clear Python, npm, pip caches
3. **Temp File Cleanup** - Remove temporary files
4. **Bloat Detection** - Identify and remove code bloat

### Current Problems (v1.0)
- ❌ Orchestrator bypassed (never invoked)
- ❌ Limited cache types supported
- ❌ No bloat detection
- ❌ Runs via maintenance only

### Solutions (v2.0)
- ✅ MCP tool guarantees orchestrator execution
- ✅ Full cache management (Python, npm, pip, etc.)
- ✅ Bloat detection and removal
- ✅ Standalone orchestrator (not maintenance-only)

---

## 📋 Phase Details

### Phase -1: Knowledge Library Consultation
**Duration:** 5 minutes

| # | Task | Deliverable |
|---|------|-------------|
| -1.1 | Query cache cleanup patterns | `context/cache-patterns.md` |
| -1.2 | Query bloat detection | `context/bloat-patterns.md` |

### Phase 0: Discovery & Requirements
**Duration:** 30 minutes

| # | Task | Deliverable |
|---|------|-------------|
| 0.1 | Review current cleanup logic | Analysis document |
| 0.2 | Define v2.0 API contract | `artifacts/api-contract.md` |
| 0.3 | Create test strategy | `artifacts/test-strategy.md` |

### Phase 1: MCP Integration
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 1.1 | Implement MCP entry point | `execute_from_mcp()` |
| 1.2 | Add context parsing | Context extraction |
| 1.3 | Add cleanup type parameter | Type handling |
| 1.4 | Add registry entry | Registry update |
| 1.5 | Write unit tests | Test cases |

### Phase 2: Cache Management
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Implement Python cache cleanup | `__pycache__`, `.pyc` |
| 2.2 | Implement pip cache cleanup | pip cache |
| 2.3 | Implement npm cache cleanup | npm cache |
| 2.4 | Generate cache report | Report |
| 2.5 | Write tests | Test cases |

### Phase 3: Temp File Cleanup
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 3.1 | Detect temp files | Detection |
| 3.2 | Detect log files (old) | Log detection |
| 3.3 | Safe removal | Removal logic |
| 3.4 | Write tests | Test cases |

### Phase 4: Bloat Detection
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 4.1 | Detect unused dependencies | Dependency analysis |
| 4.2 | Detect dead code | Dead code analysis |
| 4.3 | Generate bloat report | Report |
| 4.4 | Write tests | Test cases |

### Phase 5: Testing & Validation
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 5.1 | Unit test coverage | ≥80% coverage |
| 5.2 | Integration test: full flow | E2E test |
| 5.3 | Fix failing tests | Bug fixes |
| 5.4 | Final validation | Sign-off |

### Phase 6: REFACTOR & Cleanup
**Duration:** 30 minutes

| # | Task | Deliverable |
|---|------|-------------|
| 6.1 | Remove orphaned code | Clean code |
| 6.2 | Fix code smells | Refactored code |
| 6.3 | Add documentation | Docstrings |

---

## 📐 Architecture

### Current (v1.0)
```
cleanup (via maintenance Phase 2)
└── Basic cache clearing
```

### Target (v2.0)
```
cleanup_orchestrator.py
├── execute_from_mcp(context)    # Entry from MCP tool
├── cleanup_python_cache()       # __pycache__, .pyc
├── cleanup_pip_cache()          # pip cache
├── cleanup_npm_cache()          # npm cache
├── cleanup_temp_files()         # Temp files
├── cleanup_old_logs()           # Old log files
├── detect_bloat()               # Bloat detection
└── generate_report()            # Cleanup report
```

---

## 🔗 Dependencies

### Upstream
- [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md) (MUST complete first)

### Downstream
- None

### Related
- Maintenance Phase 2 (will use this orchestrator)

---

## ✅ Definition of Done

- [ ] MCP tool invokes orchestrator successfully
- [ ] All cache types cleared correctly
- [ ] Temp files removed safely
- [ ] Bloat detection working
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests passing
- [ ] REFACTOR phase complete

---

## 📞 Copilot Instructions

```yaml
plan_id: cleanup-v2-2026-01-02
priority: P3
depends_on: mcp-tool-infrastructure
tdd_enforcement: mandatory
deliverable: src/orchestrators/cleanup_orchestrator.py
test_coverage_target: 80%
```

---

**⬆️ Back to:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**⬅️ Depends on:** [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md)  
**✅ Final orchestrator in enhancement sequence**
