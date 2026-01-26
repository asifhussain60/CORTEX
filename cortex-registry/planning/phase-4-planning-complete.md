# Phase 4: Planning & Specifications Complete ✅

**Date:** January 26, 2026  
**Status:** ✅ Planning complete, ready for implementation  
**Branch:** feature/AC-PERMANENT-FIX-010-execution-specs  

---

## 📋 What Was Created

### 1. Phase 4 Refactoring Specification
**File:** `docs/02-architecture/phase-4-refactoring-spec.md` (350+ lines)

**Comprehensive specification covering:**
- IntentRouter refactoring (remove hardcoded keywords, use specs)
- MasterOrchestrator integration (call MasterGateway)
- Domain routing refactoring (use domain-transitions spec)
- Error code migration (use GOVE_NNN throughout)
- Test updates (50-70 tests)

**Key sections:**
- Detailed refactoring targets (4 main areas)
- Implementation strategy (4 phases, 50 hours)
- Success criteria
- Rollout plan
- Risk mitigation

### 2. Domain Transitions Specification
**File:** `cortex/execution/specs/domain-transitions.yaml` (520+ lines)

**Replaces hardcoded domain routing with declarative spec:**

**7 Domains Defined:**
1. **domain_planning** - Strategic planning/architecture (PlanningOrchestrator)
2. **domain_implementation** - Code development (TDDOrchestrator)
3. **domain_refactoring** - Code improvement (RefactoringOrchestrator)
4. **domain_deployment** - Production release (DeploymentOrchestrator)
5. **domain_analysis** - Code analysis (AnalysisOrchestrator)
6. **domain_documentation** - Code/architecture docs (DocumentationOrchestrator)
7. **domain_testing** - Test creation/validation (TestingOrchestrator)

**Each domain includes:**
- Keywords for detection
- Capabilities
- Preconditions & postconditions
- Governance rules
- Error codes (GOVE_NNN format)
- Estimated duration
- Metadata

**Domain Transitions Defined:**
- Planning → Implementation (after approval)
- Implementation → Testing (after code written)
- Testing → Refactoring (optional, if improvements identified)
- Testing → Deployment (if all tests pass)
- Any Domain → Documentation (on-demand)

**Error Recovery:**
- Implementation: retry on test fail (max 3x), on type hint fail (max 2x)
- Testing: return to implementation if coverage too low
- Deployment: rollback on health check fail (max 1x retry)

**Domain Governance:**
- Implementation requires: TDD, type hints, docstrings, no bare except, filename convention
- Testing requires: test structure, coverage minimum
- Deployment requires: approval, health check, monitoring

---

## 🎯 Phase 4 Implementation Plan

### Timeline
- **Phase 4.1:** IntentRouter Refactoring (20 hours, 2-3 days)
- **Phase 4.2:** MasterOrchestrator Integration (15 hours, 2 days)
- **Phase 4.3:** Domain Routing Refactoring (10 hours, 1.5 days)
- **Phase 4.4:** Error Code Migration (5 hours, 0.5 days)
- **Total:** 50 hours / 6 working days

### Files to Modify
1. `cortex/orchestrators/core/intent_router.py` - Remove keyword lists, use specs
2. `cortex/orchestrators/core/master_orchestrator.py` - Add gateway integration
3. `cortex/orchestrators/domain_orchestrator.py` - Use domain-transitions spec
4. Domain-specific orchestrators (5 files)
5. Test files (26+ files, 50-70 tests)

### New Files to Create
1. Refactoring helper module (optional, for transition utilities)
2. Integration test module for new spec-driven behavior

---

## ✅ Entry Criteria for Phase 4 Implementation

All criteria met:
- [x] Phase 1 complete (foundation)
- [x] Phase 2 complete (specifications)
- [x] Phase 3 complete (executor)
- [x] Phase 4 specification complete
- [x] Domain-transitions spec created
- [x] Implementation plan documented
- [x] No blocking issues identified
- [x] Branch clean and ready

---

## 📊 Phase 4 Context

### What Phase 4 Accomplishes
**Refactors production code to use spec-driven execution:**

Before Phase 4:
```python
# IntentRouter (hardcoded keywords)
IMPLEMENT_KEYWORDS = ["create", "add", "new", ...]
FIX_KEYWORDS = ["fix", "bug", "issue", ...]

# MasterOrchestrator (no gateway integration)
decision = self.intent_router.route()
# manual stage orchestration

# Domain routing (hardcoded if/elif)
if domain == "planning":
    return planning_orchestrator.execute()
elif domain == "implementation":
    return implementation_orchestrator.execute()
```

After Phase 4:
```python
# IntentRouter (spec-driven)
routing_rules = self.spec_registry.get_routing_rules()
keywords = routing_rules[intent_id]["keywords"]  # From YAML

# MasterOrchestrator (gateway-integrated)
gateway = get_executor()
result = gateway.execute(parameters)

# Domain routing (spec-driven)
domain_spec = self.spec_registry.get_domain_transition(domain)
handler = domain_spec.get("handler")
result = self._invoke_handler(handler, parameters)
```

### Key Benefits
1. **Spec-driven execution** - All routing from YAML, not hardcoded
2. **Gateway integration** - Single entry point for all operations
3. **Structured error codes** - GOVE_NNN throughout
4. **Maintainability** - Changes in YAML, not code
5. **Testability** - Spec changes = test changes, not code changes

---

## 🚀 Next Steps

### For User
1. Review Phase 4 specification: `/docs/02-architecture/phase-4-refactoring-spec.md`
2. Review domain-transitions spec: `/cortex/execution/specs/domain-transitions.yaml`
3. Approve to proceed: **"proceed to Phase 4 implementation"** OR **"continue Phase 4"**

### For Agent
Upon user approval:
1. Create feature branch (if not exists)
2. Implement IntentRouter refactoring (Phase 4.1)
3. Add test updates for IntentRouter
4. Implement MasterOrchestrator integration (Phase 4.2)
5. Refactor domain routers (Phase 4.3)
6. Migrate all error codes (Phase 4.4)
7. Run full test suite (target: 100% pass)
8. Git checkpoint commit
9. Create Phase 4 completion summary

---

## 📈 Success Metrics

### Code Quality
- ✅ All hardcoded lists removed (BEFORE Phase 4)
- ✅ All elif chains replaced (BEFORE Phase 4)
- ✅ 100% type hints maintained (CORE-011)
- ✅ 100% docstrings maintained (CORE-012)
- ✅ All errors use GOVE_NNN codes (CORE-040-003)

### Testing
- ✅ 50-70 existing tests updated
- ✅ 100% passing (target)
- ✅ Zero regression failures
- ✅ Spec-based tests added

### Integration
- ✅ IntentRouter uses routing-rules-intent.yaml
- ✅ MasterOrchestrator calls MasterGateway
- ✅ Domain orchestrators use domain-transitions.yaml
- ✅ All violations use GOVE_NNN codes

### Backward Compatibility
- ✅ No breaking API changes
- ✅ Old code paths still functional
- ✅ Existing tests still passing
- ✅ Graceful fallbacks

---

**Status:** ✅ **Phase 4 Ready for Implementation**  
**Authority:** CORTEX Master Orchestrator + CORE-040  
**Date:** January 26, 2026

---

### Files Created Today (Phase 4 Planning)

1. **docs/02-architecture/phase-4-refactoring-spec.md** (350 lines)
   - Comprehensive refactoring specification
   - 4 main refactoring targets (IntentRouter, MasterOrchestrator, Domain Routing, Error Codes)
   - Implementation strategy (50 hours, 4 phases)
   - Success criteria and rollout plan

2. **cortex/execution/specs/domain-transitions.yaml** (520 lines)
   - 7 domains fully specified
   - 6 domain transitions defined
   - Error recovery strategies
   - Domain governance requirements
   - CORE-040 compliant (all spec-driven)

### Next: Phase 4 Implementation

Upon user approval ("continue Phase 4" or "proceed to Phase 4 implementation"):
- Refactor IntentRouter (remove keyword lists, use specs)
- Integrate MasterOrchestrator with MasterGateway
- Update domain orchestrators to use spec-driven routing
- Migrate all error codes to GOVE_NNN format
- Update 50-70 existing tests
- Git checkpoint and completion summary
