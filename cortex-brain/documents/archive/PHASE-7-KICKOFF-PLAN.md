# Phase 7: Operations Simplification - Kickoff Plan

**Date:** December 22, 2025  
**Author:** Asif Hussain  
**Phase:** 7 - Operations Simplification  
**Duration:** 3 weeks (Week 15-17, Days 1-15)  
**Status:** 🚀 READY TO START

---

## 🎯 Phase 7 Overview

### Mission

Simplify CORTEX operations by reducing manifest redundancy, implementing universal adapters, and enabling dependency injection auto-discovery across all 16 orchestrators.

### Key Problems to Solve

1. **Manifest Sprawl:** 14 YAML files with 60% redundancy (~8,500 lines total)
2. **Adapter Fragmentation:** 6 different adapter interfaces with inconsistent patterns
3. **Manual Wiring:** 13+ locations requiring manual dependency injection
4. **Configuration Chaos:** 8 separate config files with overlapping concerns

### Success Targets

| Metric | Current | Target | Reduction |
|--------|---------|--------|-----------|
| Manifest Files | 14 | 3 | **79%** ↓ |
| Manifest LOC | 8,500 | 2,500 | **70%** ↓ |
| Manual DI Locations | 13 | 0 | **100%** ↓ |
| Adapter Interfaces | 6 | 1 | **83%** ↓ |
| Onboarding Time | 4 hours | 2 hours | **50%** ↓ |

---

## 📅 3-Week Timeline

### Week 15: Manifest Consolidation (Days 1-5)

**Goal:** Reduce 14 manifests to 3 canonical sources

**Deliverables:**
- `cortex-brain/manifests/core-manifest.yaml` - Orchestrator registry
- `cortex-brain/manifests/config-manifest.yaml` - Runtime configuration
- `cortex-brain/manifests/integration-manifest.yaml` - External systems
- Manifest loader with validation
- 20 tests (100% passing)

**Daily Breakdown:**
- **Day 1:** Audit existing manifests, measure redundancy
- **Day 2:** Design 3-tier manifest schema, validate with stakeholders
- **Day 3:** Implement manifest loader + validator
- **Day 4:** Migrate 16 orchestrators to new manifest format
- **Day 5:** Testing + backward compatibility validation

### Week 16: Universal Adapters (Days 6-10)

**Goal:** Single adapter interface for all external systems

**Deliverables:**
- `UniversalAdapter` interface (CRUD + search)
- `AzureDevOpsAdapter` implementation
- `GitHubAdapter` implementation
- `FileSystemAdapter` implementation
- `AdapterFactory` with auto-detection
- Middleware: caching, retry, rate limiting
- 30 tests (100% passing)

**Daily Breakdown:**
- **Day 6:** Design UniversalAdapter interface
- **Day 7:** Implement AzureDevOpsAdapter + GitHub Adapter
- **Day 8:** Implement FileSystemAdapter + AdapterFactory
- **Day 9:** Add middleware (caching, retry, rate limiting)
- **Day 10:** Migrate existing adapter usages, testing

### Week 17: DI Auto-Discovery & Validation (Days 11-15)

**Goal:** Zero manual dependency wiring

**Deliverables:**
- DI container with auto-discovery
- Decorators: `@service`, `@inject`
- Lifecycle management (singleton, transient, scoped)
- Migration of 16 orchestrators
- 25 DI tests (100% passing)
- E2E validation of all orchestrators
- Performance benchmarks (<10% regression)
- Complete documentation

**Daily Breakdown:**
- **Day 11:** Design DI container architecture
- **Day 12:** Implement DI container + decorators
- **Day 13:** Migrate 16 orchestrators (8 per day)
- **Day 14:** E2E testing + performance benchmarking
- **Day 15:** Documentation + Phase 7 completion report

---

## 🏗️ Technical Architecture

### 1. 3-Tier Manifest System

```
core-manifest.yaml          ← Orchestrator metadata (registry)
     ├── orchestrator definitions
     ├── dependencies
     └── phases

config-manifest.yaml        ← Runtime configuration
     ├── defaults
     ├── per-orchestrator overrides
     └── environment-specific settings

integration-manifest.yaml   ← External systems
     ├── Azure DevOps config
     ├── GitHub config
     └── FileSystem config
```

**Benefits:**
- Single source of truth for orchestrator metadata
- Environment-specific overrides without duplication
- Easy addition of new orchestrators (5 lines vs 50 lines)

### 2. Universal Adapter Pattern

```python
UniversalAdapter (interface)
     ├── create(resource_type, data)
     ├── read(resource_type, id)
     ├── update(resource_type, id, data)
     ├── delete(resource_type, id)
     ├── search(resource_type, query)
     └── list(resource_type, parent_id)

Implementations:
     ├── AzureDevOpsAdapter
     ├── GitHubAdapter
     └── FileSystemAdapter

AdapterFactory
     └── auto_detect() → Appropriate adapter based on env
```

**Benefits:**
- Consistent error handling across platforms
- Easy testing with single mock interface
- Middleware support (caching, retry, logging)
- Platform switching without code changes

### 3. Dependency Injection Container

```python
@service(lifetime=ServiceLifetime.SINGLETON)
class KnowledgeGraph:
    pass

@service(lifetime=ServiceLifetime.TRANSIENT)
class CICDOrchestrator(BaseOrchestrator):
    def __init__(
        self,
        brain_integrator: BrainIntegrator,  # Auto-injected
        devops_orchestrator: DevOpsOrchestrator  # Auto-injected
    ):
        self.brain = brain_integrator
        self.devops = devops_orchestrator

# Usage: Zero manual wiring
orchestrator = container.resolve(CICDOrchestrator)
```

**Benefits:**
- Zero manual wiring in `__init__` methods
- Easy testing (swap dependencies in container)
- Lifecycle control (singleton prevents memory leaks)
- Circular dependency detection

---

## 🧪 Testing Strategy

### Test Coverage Targets

| Component | Tests | Coverage Target |
|-----------|-------|----------------|
| Manifest System | 20 | 90%+ |
| Universal Adapters | 30 | 85%+ |
| DI Container | 25 | 90%+ |
| E2E Orchestrators | 16 | 100% functional |

### Test Categories

**Unit Tests (75 total):**
- Manifest loading/validation (20)
- Adapter CRUD operations (30)
- DI registration/resolution (25)

**Integration Tests (16 orchestrators):**
- Per-orchestrator E2E validation
- Manifest → DI → Adapter integration
- Configuration application

**Performance Tests:**
- Manifest loading: <100ms
- Adapter overhead: <50ms
- DI resolution: <10ms per orchestrator
- Overall regression: <10%

---

## 📊 Progress Tracking

### Week 15 Milestones

- [ ] Day 1: Manifest audit complete
- [ ] Day 2: 3-tier schema designed and approved
- [ ] Day 3: Manifest loader implemented
- [ ] Day 4: All 16 orchestrators migrated
- [ ] Day 5: 20/20 tests passing

### Week 16 Milestones

- [ ] Day 6: UniversalAdapter interface designed
- [ ] Day 7: Azure DevOps + GitHub adapters implemented
- [ ] Day 8: FileSystem + Factory implemented
- [ ] Day 9: Middleware added (caching, retry)
- [ ] Day 10: 30/30 tests passing

### Week 17 Milestones

- [ ] Day 11: DI container architecture finalized
- [ ] Day 12: DI implementation complete
- [ ] Day 13: All 16 orchestrators migrated to DI
- [ ] Day 14: E2E tests + performance benchmarks complete
- [ ] Day 15: Documentation + Phase 7 report

---

## 🚨 Risk Management

### High Risk: Breaking Changes During Migration

**Risk:** Orchestrator interfaces break during DI migration

**Mitigation:**
- Incremental migration (2-3 orchestrators per day)
- Backward compatibility layer during transition
- Comprehensive E2E tests after each migration
- Git tags at each milestone for rollback

**Contingency:** Rollback to previous tag if >3 orchestrators break

### Medium Risk: Performance Regression

**Risk:** DI overhead causes >10% performance regression

**Mitigation:**
- Use singleton lifecycle for heavy services
- Lazy initialization where possible
- Benchmark at each milestone
- Optimize if regression >10%

**Contingency:** Selective DI usage (heavy services stay manual)

### Low Risk: Adapter Interface Gaps

**Risk:** Universal interface doesn't cover all use cases

**Mitigation:**
- Design review with actual usage patterns
- Extension points in interface
- Platform-specific methods as needed

**Contingency:** Extend interface incrementally based on needs

---

## 📈 Success Metrics

### Quantitative Metrics

1. **Manifest Reduction:** 14 → 3 files (79% reduction)
2. **LOC Reduction:** 8,500 → 2,500 lines (70% reduction)
3. **Manual DI Locations:** 13 → 0 (100% elimination)
4. **Adapter Interfaces:** 6 → 1 (83% consolidation)
5. **Test Pass Rate:** 100% (75 new tests)
6. **Performance Regression:** <10%

### Qualitative Metrics

1. **Developer Experience:** Onboarding time 4h → 2h
2. **Code Quality:** Reduced duplication, lower complexity
3. **Maintainability:** Single source of truth for config
4. **Extensibility:** Easy to add new orchestrators/adapters

---

## 🎯 Phase 7 Day 1 Action Items

### Immediate Tasks (Monday, December 23, 2025)

1. **Manifest Audit (2 hours)**
   - Analyze all 14 existing manifest files
   - Identify redundant sections (estimate 60%)
   - Document unique orchestrator metadata
   - Create redundancy report

2. **Schema Design (4 hours)**
   - Design core-manifest.yaml structure
   - Design config-manifest.yaml structure
   - Design integration-manifest.yaml structure
   - Validate schema with Phase 6 orchestrators
   - Get stakeholder approval

3. **Test Fixture Setup (2 hours)**
   - Create test fixtures for 16 orchestrators
   - Set up pytest infrastructure
   - Define manifest validation test cases

**End of Day 1 Deliverable:** Manifest audit report + 3-tier schema design

---

## 📚 Resources & References

### Documentation

- **Phase 7 Full Plan:** `phases/phase-07-operations-simplification.md`
- **Phase 6 Reference:** `phases/phase-06-orchestrator-consolidation.md`
- **Master Plan:** `00-MASTER-PLAN.md`

### Technical References

- **Dependency Injection:** Martin Fowler's DI patterns
- **Adapter Pattern:** Gang of Four design patterns
- **YAML Schemas:** JSON Schema for YAML validation

### Code Locations

- **Manifests:** `cortex-brain/manifests/` (to be created)
- **Adapters:** `src/orchestration_4_0/adapters/` (to be created)
- **DI Container:** `src/orchestration_4_0/di/` (to be created)
- **Tests:** `tests/orchestration_4_0/phase_7/` (to be created)

---

## ✅ Phase 7 Completion Criteria

Phase 7 is complete when ALL criteria met:

1. ✅ Manifest consolidation: 14 → 3 files (70% reduction)
2. ✅ Universal adapter: Single interface for Azure DevOps, GitHub, FileSystem
3. ✅ DI auto-discovery: Zero manual wiring in 16 orchestrators
4. ✅ Tests: 75 new tests (100% passing)
5. ✅ E2E validation: All 16 orchestrators tested
6. ✅ Performance: <10% regression
7. ✅ Documentation: Migration guides + API docs complete

---

## 🎉 Expected Impact

**Before Phase 7:**
- 14 manifest files with 60% redundancy
- 6 different adapter interfaces
- 13+ manual DI locations
- 4 hour onboarding time

**After Phase 7:**
- 3 canonical manifests (79% reduction)
- 1 universal adapter interface (83% consolidation)
- 0 manual DI locations (100% auto-discovery)
- 2 hour onboarding time (50% faster)

**Developer Benefits:**
- Faster orchestrator development
- Easier testing and debugging
- Consistent patterns across codebase
- Simplified configuration management

---

**Phase 7 Status:** 🚀 READY TO START

**Next Action:** Begin Day 1 - Manifest audit and schema design

**Target Completion:** January 9, 2026 (3 weeks from kickoff)

---

**Prepared By:** Asif Hussain  
**Date:** December 22, 2025  
**Approved:** Ready for execution
