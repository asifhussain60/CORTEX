# ADO Orchestrator v2 Migration Strategy

**Strategy Date:** January 2, 2026  
**Plan:** ado-v2-migration (Phase 0.4)  
**Parent Plan:** cortex-v5-holistic-refactor (Phase 6.1)  
**Duration:** 6 days (focused implementation)

---

## 🎯 Executive Summary

This document outlines the complete migration strategy for transforming ADO Orchestrator from v1 (hybrid execution model) to v2 (pure autonomous architecture). The strategy prioritizes risk mitigation, incremental delivery, and zero user impact through parallel implementation and phased activation.

**Migration Philosophy:** Build v2 alongside v1, validate thoroughly, then activate via Master Orchestrator routing.

---

## 📊 Migration Overview

### Current State (v1)
- **Implementation:** 2,105 lines (orchestrator) + 818 lines (wizard)
- **Test Coverage:** 95.7% (110/115 tests passing)
- **Architecture:** Hybrid execution (Python + natural language manifest)
- **State Management:** Ephemeral (instance variables)
- **Routing:** Manual (CORTEX.prompt.md)
- **Status:** PRODUCTION (operational but limited)

### Target State (v2)
- **Implementation:** ~2,500 lines (estimated)
- **Test Coverage:** 100% (150+ tests)
- **Architecture:** Pure autonomous (Python only, config YAML)
- **State Management:** PlanningStateDB (persistent, transactional)
- **Routing:** Master Orchestrator (pattern-based)
- **Status:** PRODUCTION-READY (full feature parity + enhancements)

### Migration Complexity: **TIER 3** (ORCHESTRATOR MIGRATION)

---

## 🏗️ Migration Phases

### Phase 1: Foundation Setup (Day 1)
**Goal:** Prepare development environment and baseline

**Tasks:**
1. ✅ Complete Phase 0 analysis (architecture, wizard, tests, strategy)
2. Create v2 directory structure (`src/orchestrators/ado/v2/`)
3. Set up v2 test suite (`tests/orchestrators/ado/v2/`)
4. Create v2 config manifest template
5. Establish CI/CD pipeline for v2 (isolated from v1)

**Deliverables:**
- Empty v2 directory structure
- v2 test scaffold (115 copied tests + 35 new tests)
- v2 config manifest skeleton
- Isolated CI/CD workflow

**Risk Mitigation:**
- v1 remains untouched (zero impact)
- v2 tests initially fail (RED phase expected)
- Parallel development environment

---

### Phase 2: Core v2 Implementation (Days 2-3)
**Goal:** Implement ADOOrchestratorV2 base class with BaseOrchestratorV4.1 compliance

**Day 2 Morning: Class Foundation (4h)**

```python
# File: src/orchestrators/ado/v2/ado_orchestrator_v2.py

from src.orchestrators.base.base_orchestrator_v4_1 import BaseOrchestratorV4_1
from src.database.planning_state_db import PlanningStateDB
from src.orchestrators.ado.ado_conversational_wizard import ADOConversationalWizard

class ADOOrchestratorV2(BaseOrchestratorV4_1):
    """Pure autonomous ADO work item generation orchestrator."""
    
    def __init__(self, config_path: str, state_db: PlanningStateDB):
        super().__init__(config_path, state_db)
        self.wizard = ADOConversationalWizard(state_db=state_db)
    
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Dual-mode execution: auto or wizard."""
        mode = kwargs.get('mode', 'auto')
        
        if mode == 'wizard':
            return self._execute_wizard_mode(kwargs)
        else:
            return self._execute_auto_mode(kwargs)
```

**Day 2 Afternoon: Phase 1-2 Implementation (4h)**
- Implement `_execute_auto_mode` scaffolding
- Port Phase 1 (DISCOVERY) from v1
- Port Phase 2 (VALIDATION) from v1
- Add database state tracking for each phase

**Day 3 Morning: Phase 3-4 Implementation (4h)**
- Implement Phase 3 (GENERATION) - **NEW LOGIC**
  - Work item hierarchy generation
  - Story point conversion
  - TDD injection
- Implement Phase 4 (APPROVAL) - **NEW LOGIC**
  - Template-based preview
  - Approval gate handling

**Day 3 Afternoon: Phase 5-6 Implementation (4h)**
- Implement Phase 5 (EXECUTION) - **NEW LOGIC**
  - ADO API integration
  - Batch work item creation
  - Parent-child linking
- Implement Phase 6 (COMPLETION) - **NEW LOGIC**
  - URL generation
  - Visual progress summary

**Deliverables:**
- Complete ADOOrchestratorV2 class (~1,500 lines)
- All 6 phases fully implemented
- Database state tracking operational
- Dual-mode support (auto + wizard)

**Risk Mitigation:**
- TDD approach (write tests first where possible)
- Incremental commits after each phase
- v1 comparison tests (ensure parity)

---

### Phase 3: Wizard Integration (Day 4)
**Goal:** Integrate conversational wizard as mode selector

**Morning: Mode Selector Logic (4h)**
- Implement `_execute_wizard_mode` method
- Convert wizard output to v2 format
- Add wizard session persistence to database
- Update wizard to use PlanningStateDB

**Afternoon: Wizard Enhancements (4h)**
- Fix 5 failing wizard tests (parsing issues)
- Add wizard-specific config options
- Implement wizard → auto-mode handoff
- Add wizard state recovery

**Deliverables:**
- Wizard integration complete
- 41/41 wizard tests passing (100%)
- Wizard session persistence operational

**Risk Mitigation:**
- Wizard remains backward compatible
- v1 wizard can still be used if needed
- Session recovery prevents data loss

---

### Phase 4: Config & Templates (Day 5 Morning)
**Goal:** Create config-only manifest and Jinja2 templates

**Tasks:**
1. Create `ado-v2-config.yaml` (200 lines)
   - Routing patterns
   - Complexity thresholds
   - DoR templates
   - Validation rules
   - ADO API settings

2. Create Jinja2 templates (10 files)
   - Work item preview template
   - Approval screen template
   - Completion message template
   - Email notification template
   - DoR refinement prompt template

3. Create validation schemas (JSON Schema)
   - Work item schema
   - DoR schema
   - ADO API payload schema

**Deliverables:**
- Complete v2 config manifest
- 10 Jinja2 templates
- 3 validation schemas
- Config validation tests

**Risk Mitigation:**
- Config changes don't require code deployment
- Templates can be hot-reloaded
- Schema validation prevents bad data

---

### Phase 5: Testing & Validation (Day 5 Afternoon)
**Goal:** Achieve 100% test coverage

**Tasks:**
1. Run all 115 baseline tests → Should pass
2. Add 35 new v2-specific tests:
   - Database state tracking (8 tests)
   - Template rendering (7 tests)
   - Atomic transactions (6 tests)
   - Rollback capability (6 tests)
   - Config loading (4 tests)
   - Master Orch integration (4 tests)

3. Integration testing:
   - End-to-end workflow tests
   - Multi-user concurrency tests
   - Failure recovery tests
   - Performance benchmarks

4. Coverage report:
   - Run `pytest --cov=src/orchestrators/ado/v2`
   - Target: 100% coverage
   - Fix any gaps

**Deliverables:**
- 150/150 tests passing (100%)
- 100% code coverage report
- Integration test suite
- Performance benchmark results

**Risk Mitigation:**
- Comprehensive testing prevents regressions
- Coverage gaps identified early
- Performance validated before production

---

### Phase 6: Master Orchestrator Integration (Day 6)
**Goal:** Activate ADO v2 via Master Orchestrator routing

**Morning: Pattern Registration (2h)**

```yaml
# File: cortex-brain/config/master-orchestrator.yaml

patterns:
  - pattern: "^(ado|ado story|ado feature|ado bug).*$"
    orchestrator: ado_orchestrator_v2
    confidence: 1.0
    match_type: regex
    module: "src.orchestrators.ado.v2.ado_orchestrator_v2"
    class: "ADOOrchestratorV2"
    config: "cortex-brain/manifests/orchestrators/ado-v2-config.yaml"
```

**Morning: Orchestrator Registry Update (1h)**

```python
# File: src/mcp/registry.py

ORCHESTRATOR_REGISTRY = {
    # ... existing orchestrators ...
    "ado_orchestrator_v2": {
        "class": "ADOOrchestratorV2",
        "module": "src.orchestrators.ado.v2.ado_orchestrator_v2",
        "config": "cortex-brain/manifests/orchestrators/ado-v2-config.yaml",
        "type": "autonomous",
        "version": "2.0.0",
        "status": "active"
    }
}
```

**Afternoon: CORTEX.prompt.md Update (1h)**

```markdown
# Update Intent Router

| Intent Pattern | Route To | Type |
|----------------|----------|------|
| `ado`, `ado story`, `ado feature` | Master Orchestrator → ADO v2 | 🛡️ AUTONOMOUS |
```

**Afternoon: Testing & Validation (4h)**
1. Test routing: `"ado story X"` → Master Orch → ADO v2
2. Test wizard routing: `"ado wizard X"` → Master Orch → ADO v2 (wizard mode)
3. Verify v1 is no longer used
4. End-to-end user acceptance testing
5. Performance comparison (v1 vs v2)

**Deliverables:**
- Master Orchestrator routes ADO requests to v2
- CORTEX.prompt.md updated
- Routing tests passing
- UAT complete
- v2 ACTIVATED ✅

**Risk Mitigation:**
- Routing can be reverted instantly
- v1 code remains available (emergency fallback)
- Gradual rollout (canary testing possible)

---

## 🚨 Risk Assessment

### High-Priority Risks

#### Risk 1: Database Schema Changes
**Impact:** HIGH | **Probability:** MEDIUM | **Mitigation:** HIGH

**Description:** PlanningStateDB schema may not support all ADO v2 needs

**Mitigation:**
- Review schema before Phase 2
- Create migration scripts if needed
- Test schema changes in isolation
- Rollback scripts prepared

**Rollback:** Revert schema migration, use v1

---

#### Risk 2: ADO API Breaking Changes
**Impact:** HIGH | **Probability:** LOW | **Mitigation:** MEDIUM

**Description:** ADO REST API changes could break work item creation

**Mitigation:**
- Pin ADO API version in config
- Add API version detection
- Comprehensive error handling
- Mock ADO API in tests

**Rollback:** Route back to v1 (working API integration)

---

#### Risk 3: Performance Degradation
**Impact:** MEDIUM | **Probability:** LOW | **Mitigation:** HIGH

**Description:** Database operations could slow down v2

**Mitigation:**
- Benchmark v1 vs v2
- Database query optimization
- Connection pooling
- Caching strategies
- Performance tests in CI/CD

**Rollback:** Route back to v1 if v2 >2x slower

---

### Medium-Priority Risks

#### Risk 4: Template Rendering Errors
**Impact:** MEDIUM | **Probability:** MEDIUM | **Mitigation:** HIGH

**Description:** Jinja2 templates could fail with edge case data

**Mitigation:**
- Template validation tests
- Default/fallback templates
- Error handling with user-friendly messages
- Template hot-reload for quick fixes

**Rollback:** Use inline string formatting (v1 style)

---

#### Risk 5: Wizard Session Loss
**Impact:** MEDIUM | **Probability:** LOW | **Mitigation:** MEDIUM

**Description:** Database crashes could lose wizard sessions

**Mitigation:**
- Session persistence to database (not memory)
- Auto-save after each stage
- Session recovery on restart
- Transaction boundaries

**Rollback:** Sessions lost, user restarts (acceptable trade-off)

---

### Low-Priority Risks

#### Risk 6: Config Schema Changes
**Impact:** LOW | **Probability:** LOW | **Mitigation:** HIGH

**Description:** Config format changes break existing deployments

**Mitigation:**
- Config versioning
- Schema validation on load
- Migration scripts for config
- Backward compatibility checks

**Rollback:** Use default config

---

## 🔄 Rollback Procedures

### Emergency Rollback (Immediate - <5 min)

**Trigger:** Critical production failure in v2

**Steps:**
1. Update `master-orchestrator.yaml`:
   ```yaml
   # DISABLE v2, route to v1
   - pattern: "^(ado|ado story).*$"
     orchestrator: ado_orchestrator  # v1
     confidence: 1.0
   ```

2. Restart Master Orchestrator (if needed)
3. Verify routing: `"ado story test"` → v1
4. Monitor logs for v1 health

**Impact:** Zero downtime, instant revert

---

### Partial Rollback (Selective - 15 min)

**Trigger:** Specific v2 feature failing

**Steps:**
1. Disable failing mode in config:
   ```yaml
   ado_v2:
     wizard_enabled: false  # Disable wizard, keep auto mode
   ```

2. Update routing for wizard:
   ```yaml
   - pattern: "^ado wizard.*$"
     orchestrator: ado_orchestrator  # v1 wizard
   ```

3. Keep auto-mode in v2
4. Fix issue, re-enable

**Impact:** Partial feature loss, core functionality preserved

---

### Database Rollback (Structural - 1 hour)

**Trigger:** Database schema migration failure

**Steps:**
1. Stop all ADO operations
2. Run database rollback script:
   ```bash
   /usr/bin/python3 -m src.database.migrations.rollback_ado_v2
   ```

3. Verify schema reverted
4. Route to v1
5. Restart operations

**Impact:** Temporary downtime, data preserved

---

## 📈 Success Metrics

### Technical Metrics

| Metric | Target | Validation Method |
|--------|--------|------------------|
| **Test Coverage** | 100% | pytest --cov |
| **Test Pass Rate** | 100% (150/150) | pytest |
| **Performance** | <2x v1 time | Benchmark tests |
| **Database Queries** | <10 per execution | Query profiler |
| **Memory Usage** | <100MB | Resource monitor |
| **Error Rate** | <0.1% | Production logs |

### Functional Metrics

| Metric | Target | Validation Method |
|--------|--------|------------------|
| **v1 Feature Parity** | 100% | Feature comparison |
| **Wizard Success Rate** | >95% | Session completion |
| **Work Item Creation** | 100% success | ADO API logs |
| **Rollback Time** | <5 min | Rollback drill |
| **User Impact** | Zero | User feedback |

### Quality Metrics

| Metric | Target | Validation Method |
|--------|--------|------------------|
| **Code Quality** | A grade | SonarQube |
| **Documentation** | 100% | Doc coverage |
| **Type Hints** | 100% | mypy |
| **Linting** | Zero issues | pylint/black |

---

## 🎯 Phase Completion Criteria

### Phase 0: Foundation & Analysis ✅
- [x] ADO v1 architecture documented
- [x] Conversational wizard design documented
- [x] Baseline tests executed (110/115 passing)
- [x] Migration strategy created

### Phase 1: Foundation Setup
- [ ] v2 directory structure created
- [ ] v2 test suite scaffold ready
- [ ] v2 config manifest template created
- [ ] Isolated CI/CD pipeline operational

### Phase 2: Core v2 Implementation
- [ ] ADOOrchestratorV2 class complete
- [ ] All 6 phases implemented (DISCOVERY → COMPLETION)
- [ ] Database state tracking operational
- [ ] Dual-mode support functional

### Phase 3: Wizard Integration
- [ ] Wizard mode selector implemented
- [ ] Wizard session persistence added
- [ ] 41/41 wizard tests passing
- [ ] Wizard → auto-mode handoff working

### Phase 4: Config & Templates
- [ ] ado-v2-config.yaml complete
- [ ] 10 Jinja2 templates created
- [ ] 3 validation schemas defined
- [ ] Config validation tests passing

### Phase 5: Testing & Validation
- [ ] 150/150 tests passing (100%)
- [ ] 100% code coverage achieved
- [ ] Integration tests complete
- [ ] Performance benchmarks passing

### Phase 6: Master Orchestrator Integration
- [ ] Pattern registration complete
- [ ] Orchestrator registry updated
- [ ] CORTEX.prompt.md updated
- [ ] Routing tests passing
- [ ] v2 ACTIVATED ✅

---

## 📅 Execution Timeline

| Day | Phase | Duration | Deliverables |
|-----|-------|----------|--------------|
| 1 | Foundation Setup | 8h | v2 structure, test scaffold, config template |
| 2 | Core Implementation (Phase 1-2) | 8h | Discovery + Validation implemented |
| 3 | Core Implementation (Phase 3-6) | 8h | Generation + Approval + Execution + Completion |
| 4 | Wizard Integration | 8h | Wizard mode selector, session persistence |
| 5 AM | Config & Templates | 4h | Config YAML, Jinja2 templates, schemas |
| 5 PM | Testing & Validation | 4h | 150 tests, 100% coverage |
| 6 AM | Master Orch Integration | 4h | Routing, registry, activation |
| 6 PM | Validation & UAT | 4h | End-to-end testing, performance validation |

**Total:** 6 days (48 hours)

---

## 🚀 Go-Live Checklist

### Pre-Launch (Day 5)
- [ ] All 150 tests passing
- [ ] 100% code coverage
- [ ] Performance benchmarks passing
- [ ] Database migrations tested
- [ ] Rollback procedures tested
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Security review passed

### Launch (Day 6 Morning)
- [ ] Master Orchestrator updated
- [ ] Orchestrator registry updated
- [ ] CORTEX.prompt.md updated
- [ ] Config deployed
- [ ] Templates deployed
- [ ] Monitoring enabled

### Post-Launch (Day 6 Afternoon)
- [ ] Routing verified (ado story → v2)
- [ ] First work item created successfully
- [ ] Wizard session completed successfully
- [ ] No errors in logs (first 100 requests)
- [ ] Performance within targets
- [ ] User feedback collected

### Day 7+ (Monitoring)
- [ ] 24-hour stability check
- [ ] Error rate <0.1%
- [ ] Performance stable
- [ ] User satisfaction >90%
- [ ] v1 can be deprecated

---

## 📝 Communication Plan

### Stakeholder Updates

**Daily Standups:**
- Progress update
- Blockers identified
- Next day plan

**Milestone Updates:**
- Phase completion reports
- Test results
- Risk status

**Go-Live Communication:**
- Pre-launch notification (1 day before)
- Launch announcement
- Post-launch report

---

## 🎯 Next Steps

1. ✅ **Complete Phase 0.4:** Migration strategy (this document)
2. ⏸️ **Begin Phase 1:** Foundation setup (Day 1)
3. ⏸️ **Execute Phases 2-6:** Implementation + testing (Days 2-6)
4. ⏸️ **Monitor:** Post-launch stability (Days 7+)

---

**Strategy Finalized:** January 2, 2026  
**Reviewed By:** Asif Hussain  
**Status:** ✅ READY FOR EXECUTION  
**Confidence Level:** HIGH (comprehensive analysis, clear risks, solid mitigation)

**Authorization:** APPROVED - Begin Phase 1 implementation.
