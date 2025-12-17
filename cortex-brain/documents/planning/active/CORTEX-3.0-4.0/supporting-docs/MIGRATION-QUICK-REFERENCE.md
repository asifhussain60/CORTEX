# CORTEX 3.0 → 4.0 Migration Quick Reference

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 17, 2025

---

## 📋 Quick Overview

**Timeline:** 16 weeks (4 months)  
**Risk:** 🟡 MEDIUM  
**Complexity:** HIGH  
**Team Size:** 1-2 developers  
**Test Coverage Target:** 85%+

---

## 🎯 Key Changes

| Component | Current (3.0) | Target (4.0) | Benefit |
|-----------|---------------|--------------|---------|
| **Orchestrators** | 28 scattered | 12 consolidated | 57% reduction |
| **Manifest Config** | 6,760 lines | 500 lines | 93% bloat reduction |
| **Tool Integration** | 2-4 weeks | <1 day | MCP architecture |
| **Brain Storage** | Per-repo SQLite | Hybrid (shared Tier 2) | Cross-repo learning |
| **Test Co-location** | 0% | 100% | Improved maintainability |
| **Test Coverage** | ~60% | 85%+ | Higher quality |
| **Wiring** | Manifest files | DI Container | Permanent code-based wiring |

---

## 📅 5-Phase Timeline

### Phase 1: Foundation (Weeks 1-3)
**Goal:** MCP Gateway + Dependency Injection Container

**Deliverables:**
- ✅ MCP Gateway with JSON-RPC 2.0
- ✅ Dev Tools MCP Server (Git, Docker, pytest)
- ✅ Dependency Injection Container (CortexContainer)
- ✅ @orchestrator decorator for auto-discovery
- ✅ Backward compatibility layer

**Tests:** 40+ tests for MCP, auth, circuit breaker, DI

---

### Phase 2: Brain Enhancement (Weeks 4-6)
**Goal:** Hybrid centralization (shared Tier 2 + templates)

**Deliverables:**
- ✅ `~/.cortex/shared/` directory structure
- ✅ Centralized response templates
- ✅ Tier 2 knowledge graph with namespace isolation
- ✅ Cross-repo pattern discovery API
- ✅ Migration tool with rollback capability

**Tests:** 35+ tests for namespace isolation, privacy, migration

---

### Phase 3: Orchestrator Consolidation (Weeks 7-11)
**Goal:** 28 → 12 orchestrators with co-located tests

#### Week 7: Core
1. **ExecutionOrchestrator** - Foundation for all execution
2. **TDDOrchestrator** - RED→GREEN→REFACTOR enforcement

#### Week 8: Planning
3. **PlanningOrchestrator** - Feature planning (split 1,599 LOC → 4 modules)
4. **ScaffoldingOrchestrator** - Project structure generation

#### Week 9: Domain-Specific
5. **ADOOrchestrator** - Consolidate all ADO operations
6. **DocumentationOrchestrator** - Merge 2 implementations

#### Week 10: Operations
7. **MaintenanceOrchestrator** - Merge cleanup + optimization (5→1)
8. **QAOrchestrator** - Code quality + review (3→1)
9. **DevOpsOrchestrator** - CI/CD automation (3→1)

#### Week 11: Supporting
10. **ObservabilityOrchestrator** - Monitoring + profiling
11. **IntelligenceOrchestrator** - Pattern learning
12. **OnboardingOrchestrator** - Onboarding + demos (2→1)

**Tests:** 85%+ coverage per orchestrator, co-located tests

---

### Phase 4: Operations Simplification (Weeks 12-14)
**Goal:** Eliminate manifest bloat via DI auto-discovery

**Deliverables:**
- ✅ @orchestrator decorator with metadata
- ✅ Auto-discovery system (scan src/orchestrators/)
- ✅ cortex-operations.yaml reduced to 500 lines (metadata only)
- ✅ Dynamic routing via DI container
- ✅ Natural language aliases
- ✅ Backward compatibility (all old commands work)

**Tests:** 30+ tests for auto-discovery, routing, aliases

---

### Phase 5: Testing & Validation (Weeks 15-16)
**Goal:** Production-ready validation

**Activities:**
- ✅ Run full test suite (500+ tests)
- ✅ Measure coverage (pytest --cov)
- ✅ Fix coverage gaps (target 85%+)
- ✅ 10 integration tests (critical workflows)
- ✅ Performance benchmarks (<10% regression)
- ✅ Load testing (100 concurrent ops)
- ✅ UAT on 3 repositories
- ✅ Migration validation report
- ✅ Go/No-Go decision

---

## 🏗️ Architecture Changes

### MCP Server Architecture

**Before (3.0):**
```
CORTEX → 100+ hardcoded tool wrappers
         (git_wrapper.py, docker_wrapper.py, ...)
```

**After (4.0):**
```
CORTEX → MCP Gateway → MCP Servers → Tools
         (Auth, Circuit Breaker, Load Balancer)
         
         Dev Tools MCP ─→ Git, Docker, pytest
         ADO MCP ────────→ Boards, Pipelines
         Enterprise MCP ─→ Jira, Confluence
```

**Benefit:** Add new tool in <1 day (just config)

---

### Brain Centralization

**Before (3.0):**
```
RepoA/cortex-brain/       RepoB/cortex-brain/       RepoC/cortex-brain/
├── Tier 0 (rules)        ├── Tier 0 (rules)        ├── Tier 0 (rules)
├── Tier 1 (conv)         ├── Tier 1 (conv)         ├── Tier 1 (conv)
├── Tier 2 (patterns) 50MB├── Tier 2 (patterns) 50MB├── Tier 2 (patterns) 50MB
├── Tier 3 (git)          ├── Tier 3 (git)          ├── Tier 3 (git)
└── Templates (dupl)      └── Templates (dupl)      └── Templates (dupl)
```

**After (4.0):**
```
~/.cortex/shared/                     # CENTRALIZED
├── Tier 0 (SKULL rules)              # Shared governance
├── Tier 2 (knowledge_graph.db)       # Namespace-isolated patterns
└── response-templates.yaml           # Single source of truth

RepoA/cortex-brain/  RepoB/cortex-brain/  RepoC/cortex-brain/
├── Tier 1 (conv)    ├── Tier 1 (conv)    ├── Tier 1 (conv)  # Isolated
└── Tier 3 (git)     └── Tier 3 (git)     └── Tier 3 (git)   # Isolated
```

**Benefits:**
- Cross-repo pattern learning
- 33% storage reduction
- Unified templates

---

### Dependency Injection (Bloat Reduction)

**Before (3.0):**
```yaml
# cortex-operations.yaml - 6,760 lines
operations:
  refine:
    modules: [refinement_orchestrator_v1]
    profiles:
      standard: {...}
      discovery_only: {...}
    implementation_status: {...}
    # ... hundreds more lines
```

**After (4.0):**
```python
# src/di/container.py - Code-based wiring
from dependency_injector import containers, providers

class CortexContainer(containers.DeclarativeContainer):
    config = providers.Configuration()
    
    mcp_gateway = providers.Singleton(MCPGateway)
    
    # Auto-discovered via @orchestrator decorator
    planning_orchestrator = providers.Factory(PlanningOrchestrator)
    tdd_orchestrator = providers.Factory(TDDOrchestrator)
    # ...
```

```yaml
# cortex-operations.yaml - 500 lines (metadata only)
operations:
  refine:
    description: "Holistic system refinement"
    examples:
      - "refine"
      - "improve cortex"
    # NO wiring config (handled by DI)
```

**Benefit:** 93% config reduction

---

## 📦 Orchestrator Consolidation

| New (4.0) | Consolidates (3.0) | Reduction |
|-----------|-------------------|-----------|
| MaintenanceOrchestrator | cleanup, holistic_cleanup, user_cleanup, optimize_cortex, optimize_system | 5→1 |
| DocumentationOrchestrator | documentation, documentation_generation | 2→1 |
| ADOOrchestrator | ado_agent, ado work items, ado_planning | 3→1 |
| QAOrchestrator | qa, code_quality, holistic_review | 3→1 |
| DevOpsOrchestrator | devops, deployment, integration_testing | 3→1 |
| OnboardingOrchestrator | onboarding, demo | 2→1 |

**Total:** 28 orchestrators → 12 (57% reduction)

---

## 🧪 Test Strategy

### Co-Located Tests

**Before (3.0):**
```
src/orchestrators/planning/planning_orchestrator.py
tests/orchestrators/test_planning_orchestrator_v3_1.py  ← Far away!
tests/orchestrators/test_planning_orchestrator_phase6.py
tests/orchestrators/test_planning_orchestrator_observer.py
```

**After (4.0):**
```
src/orchestrators/planning/
├── planning_orchestrator.py
├── complexity_analyzer.py
├── dor_validator.py
├── plan_generator.py
└── tests/                      ← CO-LOCATED!
    ├── test_planning_orchestrator.py
    ├── test_complexity_analyzer.py
    ├── test_dor_validator.py
    └── test_plan_generator.py
```

### Coverage Targets

| Component | Target | Rationale |
|-----------|--------|-----------|
| Core Orchestrators | 90% | Critical path |
| Domain Orchestrators | 85% | Important features |
| Supporting Orchestrators | 75% | Lower risk |
| MCP Gateway | 90% | Infrastructure |
| DI Container | 95% | Foundation |
| Brain Tiers | 80% | Data integrity |

### TDD Enforcement

**Every orchestrator enhancement:**
1. ✅ Write failing test (RED)
2. ✅ Implement minimal code (GREEN)
3. ✅ Refactor and optimize (REFACTOR)
4. ✅ Verify 85%+ coverage

---

## 🛡️ Safety & Rollback

### Phase-Specific Safety

**Phase 1:** Compatibility layer (old wrappers → MCP)  
**Phase 2:** Opt-in migration (user runs script)  
**Phase 3:** One-by-one orchestrator migration  
**Phase 4:** Backward compatible routing  
**Phase 5:** Comprehensive validation before release

### Emergency Rollback

```bash
# If migration fails
git checkout CORTEX-3.0
git branch -D CORTEX-4.0-migration-failed

# Restore brain data
cp ~/.cortex/backup/brain.db.backup cortex-brain/brain.db

# Document failure
echo "$(date): Migration failed - [reason]" >> migration-failures.log
```

---

## 📊 Success Metrics

### Must-Have Criteria

- ✅ All 12 orchestrators migrated and tested
- ✅ 85%+ test coverage achieved
- ✅ <10% performance regression
- ✅ Backward compatibility verified (all 27 operations work)
- ✅ 0 critical bugs
- ✅ Bloat reduction: 6,760 → 500 lines (93%)

### Quality Gates

**Go Criteria:**
- All tests passing (500+ tests)
- Coverage ≥85%
- Performance benchmarks pass
- UAT successful (3 repos)
- Migration validation report approved

**No-Go Criteria:**
- Critical bugs found
- >10% performance regression
- Backward compatibility broken
- Data loss during migration

---

## 🚀 Getting Started

### Prerequisites

1. Backup all brain data: `python scripts/backup_brain.py --all-repos`
2. Create branch: `git checkout -b CORTEX-4.0`
3. Set milestones in GitHub (5 phases)
4. Review all dependencies: `pip list`

### Phase 1 Kickoff

```bash
# Create MCP structure
mkdir -p src/mcp/{gateway,servers,registry,protocol}

# Create DI structure
mkdir -p src/di

# Install dependencies
pip install dependency-injector

# Start implementation
# 1. src/mcp/protocol/mcp_protocol.py
# 2. src/mcp/gateway/mcp_gateway.py
# 3. src/di/container.py
# 4. src/di/decorators.py
```

---

## 📞 Questions Before Starting

1. **Timeline:** Is 16 weeks acceptable?
2. **Testing:** Agree with 85%+ coverage target?
3. **Brain Centralization:** Approve hybrid model (shared Tier 2)?
4. **MCP Priority:** Prioritize specific MCP servers beyond Dev Tools?
5. **Bloat Reduction:** Approve DI container over manifest?
6. **Backward Compatibility:** Must ALL old operations work?
7. **Rollback Trigger:** >10% perf regression = rollback?
8. **Documentation:** Who reviews updated docs?

---

## 📚 Related Documents

- **Full Plan:** `CORTEX-3-TO-4-MIGRATION-MASTER-PLAN.md`
- **Visual Roadmap:** `MIGRATION-VISUAL-ROADMAP.md`
- **MCP Architecture:** `06-mcp-server-architecture.md`
- **Brain Storage:** `17-brain-architecture-storage-options.md`
- **CORTEX 4.0 Roadmap:** `CORTEX-4.0-ROADMAP.md`

---

## ✅ Next Step

**User Action Required:** Review and approve to begin Phase 1 implementation! 🚀

---

**Author:** Asif Hussain  
**Contact:** github.com/asifhussain60/CORTEX  
**Date:** December 17, 2025
