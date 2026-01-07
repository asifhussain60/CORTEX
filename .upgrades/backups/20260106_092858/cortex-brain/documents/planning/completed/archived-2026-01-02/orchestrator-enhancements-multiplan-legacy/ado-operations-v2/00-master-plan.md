# 📋 ADO Operations v2 - Enhancement Plan

**Plan ID:** `ado-operations-v2-2026-01-02`  
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
| 2 | Work Item Generation | `░░░░░░░░░░` | 0/8 | ⏸️ |
| 3 | Acceptance Criteria | `░░░░░░░░░░` | 0/5 | ⏸️ |
| 4 | Estimation Engine | `░░░░░░░░░░` | 0/4 | ⏸️ |
| 5 | Testing & Validation | `░░░░░░░░░░` | 0/6 | ⏸️ |
| 6 | REFACTOR & Cleanup | `░░░░░░░░░░` | 0/4 | ⏸️ |

**Total Tasks:** 0/40  
**Estimated Duration:** 2 days

---

## 🎯 Executive Summary

This plan enhances the **ADO (Azure DevOps) Operations Orchestrator** to v2.0 with:

1. **MCP Tool Integration** - Invoked via `invoke_orchestrator("ado")`
2. **Improved Work Item Generation** - Structured stories, features, tasks
3. **Enhanced Acceptance Criteria** - Clear, testable criteria
4. **Estimation Engine** - Story points based on complexity analysis

### Current Problems (v1.0)
- ❌ Orchestrator bypassed (never invoked)
- ❌ Work items lack structure
- ❌ Acceptance criteria inconsistent
- ❌ No automated estimation

### Solutions (v2.0)
- ✅ MCP tool guarantees orchestrator execution
- ✅ Structured work item templates
- ✅ Consistent acceptance criteria format
- ✅ AI-powered estimation

---

## 📋 Phase Details

### Phase -1: Knowledge Library Consultation
**Duration:** 10 minutes

| # | Task | Deliverable |
|---|------|-------------|
| -1.1 | Query ADO patterns | `context/ado-patterns.md` |
| -1.2 | Query work item templates | `context/work-item-templates.md` |
| -1.3 | Query estimation patterns | `context/estimation-patterns.md` |

### Phase 0: Discovery & Requirements
**Duration:** 1 hour

| # | Task | Deliverable |
|---|------|-------------|
| 0.1 | Review v1.0 implementation | Analysis document |
| 0.2 | Define v2.0 API contract | `artifacts/api-contract.md` |
| 0.3 | Map work item types | Type mapping |
| 0.4 | Create test strategy | `artifacts/test-strategy.md` |

### Phase 1: MCP Integration
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 1.1 | Implement MCP entry point | `execute_from_mcp()` |
| 1.2 | Add context parsing | Context extraction |
| 1.3 | Add registry entry | Registry update |
| 1.4 | Add progress events | Event emission |
| 1.5 | Write unit tests | Test cases |
| 1.6 | Documentation | Docstrings |

### Phase 2: Work Item Generation
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 2.1 | Implement Feature generation | Feature template |
| 2.2 | Implement Story generation | Story template |
| 2.3 | Implement Task generation | Task template |
| 2.4 | Implement Bug generation | Bug template |
| 2.5 | Add hierarchy linking | Parent-child links |
| 2.6 | Add tagging system | Tags |
| 2.7 | Add iteration assignment | Sprint assignment |
| 2.8 | Write tests | Test cases |

### Phase 3: Acceptance Criteria
**Duration:** 0.5 day

| # | Task | Deliverable |
|---|------|-------------|
| 3.1 | Define AC format | Given-When-Then |
| 3.2 | Implement AC generator | AC generation |
| 3.3 | Add testability validation | Validation |
| 3.4 | Add AC templates | Templates |
| 3.5 | Write tests | Test cases |

### Phase 4: Estimation Engine
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 4.1 | Implement complexity analysis | Analysis |
| 4.2 | Implement story point calculation | Calculation |
| 4.3 | Add confidence scoring | Confidence |
| 4.4 | Write tests | Test cases |

### Phase 5: Testing & Validation
**Duration:** 0.25 day

| # | Task | Deliverable |
|---|------|-------------|
| 5.1 | Unit test coverage | ≥80% coverage |
| 5.2 | Integration test: full flow | E2E test |
| 5.3 | Integration test: MCP invocation | MCP test |
| 5.4 | Integration test: ADO API | API test |
| 5.5 | Fix failing tests | Bug fixes |
| 5.6 | Final validation | Sign-off |

### Phase 6: REFACTOR & Cleanup
**Duration:** 1 hour

| # | Task | Deliverable |
|---|------|-------------|
| 6.1 | Remove orphaned code | Clean code |
| 6.2 | Fix code smells | Refactored code |
| 6.3 | Add documentation | Docstrings |
| 6.4 | Update type hints | Type annotations |

---

## 📐 Architecture

### Current (v1.0)
```
ado_orchestrator.py
├── execute()              # Never called
├── generate_story()       # Never called
└── create_work_item()     # Never called
```

### Target (v2.0)
```
ado_orchestrator.py
├── execute_from_mcp(context)    # Entry from MCP tool
├── generate_feature()           # Feature work item
├── generate_story()             # Story work item
├── generate_task()              # Task work item
├── generate_acceptance_criteria() # AC generation
├── estimate_story_points()      # Estimation
└── push_to_ado()               # ADO API integration
```

---

## 🔗 Dependencies

### Upstream
- [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md) (MUST complete first)

### Downstream
- None

### External
- Azure DevOps API

---

## ✅ Definition of Done

- [ ] MCP tool invokes orchestrator successfully
- [ ] Work items generated with correct structure
- [ ] Acceptance criteria in Given-When-Then format
- [ ] Story points estimated with confidence score
- [ ] Unit tests ≥80% coverage
- [ ] Integration tests passing
- [ ] REFACTOR phase complete

---

## 📞 Copilot Instructions

```yaml
plan_id: ado-operations-v2-2026-01-02
priority: P2
depends_on: mcp-tool-infrastructure
tdd_enforcement: mandatory
deliverable: src/orchestrators/ado_orchestrator.py
test_coverage_target: 80%
```

---

**⬆️ Back to:** [Orchestrator Enhancement Master](../00-ORCHESTRATOR-MASTER.md)  
**⬅️ Depends on:** [MCP Tool Infrastructure](../mcp-tool-infrastructure/00-master-plan.md)  
**➡️ Parallel:** [Vacuum v2](../vacuum-v2/00-master-plan.md)
