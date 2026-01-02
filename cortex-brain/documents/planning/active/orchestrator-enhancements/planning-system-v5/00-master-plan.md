# 🧠 Planning System v5 - Enhancement Plan

**Plan ID:** `planning-system-v5-2026-01-02`  
**Parent Tracker:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**Priority:** 🔴 P1 (First orchestrator after MCP tool)  
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
| -1 | Knowledge Library Consultation | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 0 | Discovery & Requirements | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 1 | BaseOrchestrator v4.1 | `░░░░░░░░░░` | 0/8 | ⏸️ |
| 2 | Planning Orchestrator Core | `░░░░░░░░░░` | 0/12 | ⏸️ |
| 3 | Continuous Knowledge Library | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 4 | Progress Rendering | `░░░░░░░░░░` | 0/8 | ⏸️ |
| 5 | Template Integration | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 6 | Hierarchical Plan Structure | `░░░░░░░░░░` | 0/8 | ⏸️ |
| 7 | Brain Tier Updates | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 8 | Testing & Validation | `░░░░░░░░░░` | 0/10 | ⏸️ |
| 9 | REFACTOR & Cleanup | `░░░░░░░░░░` | 0/8 | ⏸️ |

**Total Tasks:** 0/83  
**Estimated Duration:** 4 days

---

## 🎯 Executive Summary

This plan enhances the **Planning System Orchestrator** to v5.0 with:

1. **MCP Tool Integration** - Invoked via `invoke_orchestrator("planning")`
2. **Continuous Knowledge Library** - Query at EVERY phase, not just Phase -1
3. **Maintenance-Style Progress** - Real-time visual progress updates
4. **Hierarchical Plans** - Master + phase sub-files with 2-way linking
5. **Brain Tier Updates** - Automatic knowledge extraction after completion

### Current Problems (v4.0)
- ❌ Orchestrator bypassed (CORTEX interprets plans manually)
- ❌ Knowledge library checked once (Phase -1 only)
- ❌ No brain tier updates after plan completion
- ❌ Monolithic plan structure

### Solutions (v5.0)
- ✅ MCP tool guarantees orchestrator execution
- ✅ Knowledge library queries at each phase
- ✅ Automatic Brain Tier 2/3 updates
- ✅ Hierarchical: master + 13 phase files

---

## 📋 Phase Details

### Phase -1: Knowledge Library Consultation
**Duration:** 15 minutes

| # | Task | Deliverable |
|---|------|-------------|
| -1.1 | Query orchestrator patterns | `context/orchestrator-patterns.md` |
| -1.2 | Query invocation mechanisms | `context/invocation-patterns.md` |
| -1.3 | Query progress rendering | `context/progress-patterns.md` |
| -1.4 | Query brain tier integration | `context/brain-tier-patterns.md` |
| -1.5 | Query hierarchical plans | `context/hierarchical-patterns.md` |

### Phase 0: Discovery & Requirements
**Duration:** 2 hours

| # | Task | Deliverable |
|---|------|-------------|
| 0.1 | Review v4.0 implementation | Analysis document |
| 0.2 | Identify integration points with MCP | Integration map |
| 0.3 | Define v5.0 API contract | `artifacts/api-contract.md` |
| 0.4 | Map knowledge library queries | Query map |
| 0.5 | Define progress events | Event schema |
| 0.6 | Create test strategy | `artifacts/test-strategy.md` |

### Phase 1: BaseOrchestrator v4.1
**Duration:** 1 day

| # | Task | Deliverable |
|---|------|-------------|
| 1.1 | Add MCP context parameter | Base class update |
| 1.2 | Add knowledge library hooks | Query hooks |
| 1.3 | Add progress event emitter | Event emission |
| 1.4 | Add brain tier update interface | Update interface |
| 1.5 | Add plan structure generator | Generator method |
| 1.6 | Update type hints | Type annotations |
| 1.7 | Write unit tests | `tests/orchestrators/test_base.py` |
| 1.8 | Documentation | Docstrings |

### Phase 2: Planning Orchestrator Core
**Duration:** 1.5 days

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Implement MCP entry point | `execute_from_mcp()` |
| 2.2 | Add context parsing | Context extraction |
| 2.3 | Implement plan folder creation | Folder structure |
| 2.4 | Implement master plan generation | `00-master-plan.md` |
| 2.5 | Implement phase file generation | Phase files |
| 2.6 | Implement 2-way linking | Links in files |
| 2.7 | Add progress tracker generation | `progress-tracker.json` |
| 2.8 | Add visual progress generation | `PROGRESS.md` |
| 2.9 | Add compliance validation | Validation logic |
| 2.10 | Add auto-healing | Fix violations |
| 2.11 | Write unit tests | Test cases |
| 2.12 | Write integration tests | E2E tests |

### Phase 3: Continuous Knowledge Library
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 3.1 | Implement phase-level queries | Query per phase |
| 3.2 | Add pattern extraction | Pattern capture |
| 3.3 | Add knowledge caching | Local cache |
| 3.4 | Add query logging | Audit log |
| 3.5 | Add metrics tracking | Query metrics |
| 3.6 | Write tests | Test cases |

### Phase 4: Progress Rendering
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 4.1 | Implement progress bar generator | Progress bars |
| 4.2 | Add phase status tracking | Status updates |
| 4.3 | Add task completion events | Event emission |
| 4.4 | Add real-time rendering | Live updates |
| 4.5 | Match maintenance style | Consistent UX |
| 4.6 | Add burndown chart | Visual chart |
| 4.7 | Add timeline view | Timeline |
| 4.8 | Write tests | Test cases |

### Phase 5: Template Integration
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 5.1 | Fix `autonomous_execution_progress` | Template fix |
| 5.2 | Add template variables | Variable binding |
| 5.3 | Add execution context | Context injection |
| 5.4 | Add Copilot instructions block | Instructions |
| 5.5 | Validate template rendering | Validation |
| 5.6 | Write tests | Test cases |

### Phase 6: Hierarchical Plan Structure
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 6.1 | Define folder structure | Structure spec |
| 6.2 | Generate master plan | `00-master-plan.md` |
| 6.3 | Generate phase files | `phases/*.md` |
| 6.4 | Generate context folder | `context/*.md` |
| 6.5 | Generate artifacts folder | `artifacts/*.md` |
| 6.6 | Generate tracking folder | `tracking/*` |
| 6.7 | Add navigation breadcrumbs | Navigation |
| 6.8 | Write tests | Test cases |

### Phase 7: Brain Tier Updates
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 7.1 | Implement Tier 1 updates | Working memory |
| 7.2 | Implement Tier 2 updates | Knowledge graph |
| 7.3 | Implement Tier 3 updates | Dev context |
| 7.4 | Add obsolete pattern detection | Detection |
| 7.5 | Add pattern replacement | Replacement |
| 7.6 | Write tests | Test cases |

### Phase 8: Testing & Validation
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 8.1 | Unit test coverage | ≥80% coverage |
| 8.2 | Integration test: full flow | E2E test |
| 8.3 | Integration test: MCP invocation | MCP test |
| 8.4 | Integration test: progress | Progress test |
| 8.5 | Integration test: brain updates | Tier test |
| 8.6 | Performance test: <5s generation | Perf test |
| 8.7 | Compliance test: score ≥8.0 | Compliance test |
| 8.8 | UAT: manual validation | UAT |
| 8.9 | Fix failing tests | Bug fixes |
| 8.10 | Final validation | Sign-off |

### Phase 9: REFACTOR & Cleanup
**Duration:** 2 hours

| # | Task | Deliverable |
|---|------|-------------|
| 9.1 | Remove orphaned code | Clean code |
| 9.2 | Eliminate duplication | DRY code |
| 9.3 | Fix unused imports | Import cleanup |
| 9.4 | Fix code smells | Refactored code |
| 9.5 | Standardize formatting | Formatted code |
| 9.6 | Add missing docstrings | Documentation |
| 9.7 | Update type hints | Type annotations |
| 9.8 | Final code review | Review complete |

---

## 📐 Architecture

### Current (v4.0)
```
planning_orchestrator.py
├── execute()              # Never called
├── generate_plan()        # Never called
└── validate_compliance()  # Never called
```

### Target (v5.0)
```
planning_orchestrator.py
├── execute_from_mcp(context)     # Entry from MCP tool
├── query_knowledge_library()     # Every phase
├── generate_hierarchical_plan()  # Master + phases
├── emit_progress_event()         # Real-time updates
├── update_brain_tiers()          # After completion
└── validate_and_heal()           # Auto-fix violations
```

---

## 🔗 Dependencies

### Upstream
- [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md) (MUST complete first)

### Downstream
- None (other orchestrators can follow this pattern)

### Shared Components
- `BaseOrchestrator` - Updated in Phase 1
- `KnowledgeLibrary` - Used in Phase 3
- `ProgressRenderer` - Implemented in Phase 4
- `BrainTierManager` - Used in Phase 7

---

## ✅ Definition of Done

- [ ] MCP tool invokes orchestrator successfully
- [ ] Continuous knowledge library queries working
- [ ] Hierarchical plan structure generated
- [ ] 2-way linking functional
- [ ] Progress rendering matches maintenance style
- [ ] Brain tier updates automated
- [ ] Compliance score ≥8.0 enforced
- [ ] Auto-healing working for 90% of violations
- [ ] Performance <5s plan generation
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests passing
- [ ] REFACTOR phase complete
- [ ] Documentation updated

---

## 📞 Copilot Instructions

```yaml
plan_id: planning-system-v5-2026-01-02
priority: P1
depends_on: mcp-tool-infrastructure
tdd_enforcement: mandatory
deliverable: src/orchestrators/planning_orchestrator.py
test_coverage_target: 80%
performance_target: <5s
compliance_target: 8.0
```

---

**⬆️ Back to:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**⬅️ Depends on:** [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md)  
**➡️ Next:** [ADO Operations v2](../ado-operations-v2/00-master-plan.md)
