# Phase 4: Production Code Refactoring - Detailed Specification

**Phase:** 4 | **Orchestrator:** RefactoringOrchestrator | **Duration:** 40-50 hours  
**Date Started:** January 26, 2026 | **Target Date:** February 2-6, 2026  
**Scope:** Refactor IntentRouter, MasterOrchestrator, domain routing to use spec-driven execution  

---

## 🎯 Objectives

### Primary Objectives
1. **IntentRouter Refactoring** → Use routing-rules-intent.yaml instead of hardcoded keywords
2. **MasterOrchestrator Integration** → Call MasterGateway.execute() as execution path
3. **Domain Routing** → Replace string-based domain parsing with domain-transitions spec
4. **Governance Integration** → Replace error messages with GOVE_NNN codes
5. **Test Updates** → Update 50-70 existing tests for spec-driven behavior

### Secondary Objectives
- Remove all hardcoded keyword lists from production code
- Replace all elif chains with spec lookups
- Migrate all domain-specific routing to YAML-defined transitions
- Integrate structured error codes (GOVE_NNN) throughout

---

## 📊 Refactoring Targets

### Target 1: IntentRouter (cortex/orchestrators/core/intent_router.py)

**Current State:**
- Hardcoded keyword lists: IMPLEMENT_KEYWORDS, FIX_KEYWORDS, REFACTOR_KEYWORDS, FILE_CREATION_KEYWORDS
- Manual keyword matching in detect_intent() method
- ~250 lines of routing logic

**Desired State:**
- Load keyword lists from routing-rules-intent.yaml via SpecRegistry
- Use spec-driven keyword matching
- Call get_handler_for_intent() from SpecRegistry

**Changes Required:**

```python
# BEFORE (lines 133-161)
IMPLEMENT_KEYWORDS: List[str] = [
    "create", "add", "new", "implement", "develop", "build", "construct",
    "establish", "introduce", "feature", "enhancement"
]

FIX_KEYWORDS: List[str] = [
    "fix", "bug", "issue", "error", "problem", "crash", "fail", "broken",
    "resolve", "correct", "repair", "patch", "race condition"
]

REFACTOR_KEYWORDS: List[str] = [
    "refactor", "improve", "cleanup", "restructure", "simplify", "optimize",
    "clean", "modernize", "reorganize", "rewrite", "redesign", "performance"
]

FILE_CREATION_KEYWORDS: List[str] = [
    "file", "write", "output", "report", "generate", "save", "persist",
    "export", "create file", "write file", "output file", "report file"
]

# AFTER
# Remove all hardcoded lists - load from SpecRegistry
def __init__(self) -> None:
    self.spec_registry = SpecRegistry.get_registry()
    self.routing_rules = self.spec_registry.get_routing_rules()
```

**Affected Methods:**
- `__init__()` - Add SpecRegistry integration
- `detect_intent()` - Use spec-based keyword matching
- `_route_internal()` - Use spec routing rules

**Refactoring Steps:**

```
Step 1: Add SpecRegistry import and initialization
Step 2: Load routing_rules from spec_registry in __init__
Step 3: Refactor detect_intent() to use spec keywords
Step 4: Update _route_internal() to use spec handlers
Step 5: Replace all error messages with GOVE_NNN codes
Step 6: Update tests (26 tests in TestIntentRouter)
```

---

### Target 2: MasterOrchestrator (cortex/orchestrators/core/master_orchestrator.py)

**Current State:**
- Direct orchestrator invocation (no gateway)
- Manual stage orchestration
- Direct error messages (not structured codes)

**Desired State:**
- Call MasterGateway.execute() for all operations
- Use gateway result directly
- All violations use GOVE_NNN codes

**Changes Required:**

```python
# BEFORE
def execute(self, parameters: Dict[str, Any]) -> Result[Any]:
    # Stage 1: Routing
    decision = self.intent_router.route(parameters)
    # ... manual stage execution

# AFTER
def execute(self, parameters: Dict[str, Any]) -> Result[Any]:
    gateway = get_executor()
    gateway_result = gateway.execute(parameters)
    
    # Check for violations
    if not gateway_result.success:
        for violation in gateway_result.violations:
            if violation.get("severity") == "BLOCKING":
                return Err(violation.get("code"))
    
    return Ok(gateway_result.operation_output)
```

**Affected Methods:**
- `__init__()` - Add gateway initialization
- `execute()` - Route through MasterGateway
- `execute_operation()` - Use gateway
- Error handling methods - Use GOVE_NNN codes

**Refactoring Steps:**

```
Step 1: Import MasterGatewayExecutor and get_executor
Step 2: Initialize gateway in __init__
Step 3: Update execute() to call gateway.execute()
Step 4: Update error handling for GOVE_* codes
Step 5: Remove old stage-by-stage logic
Step 6: Update tests (15+ tests in TestMasterOrchestrator)
```

---

### Target 3: Domain Routing (cortex/orchestrators/domain_brain/)

**Current State:**
- Multiple domain-specific routers
- String-based domain transitions
- Domain-specific if/elif chains

**Desired State:**
- Load domain transitions from domain-transitions spec (in exec-flow.yaml)
- Use unified routing via SpecRegistry
- All transitions spec-driven

**Files to Refactor:**
- `domain_orchestrator.py` - Use domain-transitions spec
- `planning_orchestrator.py` - Use spec-driven flow
- `refactoring_orchestrator.py` - Use spec-driven flow

**Example Change:**

```python
# BEFORE (in DomainOrchestrator)
if domain == "planning":
    return self.planning_orchestrator.execute()
elif domain == "refactoring":
    return self.refactoring_orchestrator.execute()
elif domain == "implementation":
    return self.execution_orchestrator.execute()

# AFTER
domain_spec = self.spec_registry.get_domain_transition(domain)
if domain_spec:
    handler = domain_spec.get("handler")
    return self._invoke_handler(handler, parameters)
```

**Refactoring Steps:**

```
Step 1: Create domain-transitions.yaml spec (if not exists)
Step 2: Load spec in __init__()
Step 3: Replace all if/elif chains with spec lookups
Step 4: Use GOVE_NNN codes for domain errors
Step 5: Update 20+ domain routing tests
```

---

### Target 4: Error Code Migration

**Current State:**
```python
return Err("Intent could not be classified")
return Err("Handler not found")
return Err("Domain routing failed")
```

**Desired State:**
```python
return Err("GOVE_INTENT_UNCLASSIFIED")  # From routing-rules
return Err("GOVE_HANDLER_NOT_FOUND")   # From orchestrator spec
return Err("GOVE_DOMAIN_ROUTING_FAIL")  # From domain spec
```

**Affected Files:**
- cortex/orchestrators/core/intent_router.py (26 occurrences)
- cortex/orchestrators/core/master_orchestrator.py (15 occurrences)
- cortex/orchestrators/domain_orchestrator.py (20+ occurrences)
- cortex/orchestrators/domain_brain/*.py (50+ occurrences)

---

## 🧪 Test Updates

### Tests to Update (50-70 total)

#### IntentRouter Tests (26 tests)
```
tests/unit/orchestrators/test_intent_orchestrator_routing.py
tests/integration/orchestrators/test_intent_router.py
tests/integration/domain_brain/test_intent_router.py
```

**Changes:**
- Mock SpecRegistry instead of direct keyword lists
- Verify spec-based routing
- Verify GOVE_NNN error codes

#### MasterOrchestrator Tests (15+ tests)
```
tests/unit/orchestrators/test_master_orchestrator.py
tests/integration/orchestrators/test_master_orchestrator.py
```

**Changes:**
- Verify gateway integration
- Test violations handling
- Test handler selection

#### Domain Routing Tests (20+ tests)
```
tests/integration/domain_brain/test_domain_orchestrator.py
tests/integration/domain_brain/test_planning_orchestrator.py
tests/integration/domain_brain/test_refactoring_orchestrator.py
```

**Changes:**
- Mock domain-transitions spec
- Verify spec-based transitions
- Test error codes

---

## 📁 Files to Create/Modify

### Files to Create (6 new)
1. `cortex/orchestrators/intent-router-spec.py` - Spec-driven IntentRouter refactoring
2. `cortex/orchestrators/master-gateway-int.py` - MasterOrchestrator + gateway integration
3. `cortex/orchestrators/domain-transitions.yaml` - Domain transition specification
4. `tests/test-intent-router-refac.py` - IntentRouter refactoring tests
5. `tests/test-master-orchestra-int.py` - MasterOrchestrator integration tests
6. `docs/02-architecture/phase-4-refac-guide.md` - Phase 4 implementation guide

### Files to Modify (10+ existing)
- `cortex/orchestrators/core/intent_router.py` - Remove hardcoded keywords, use specs
- `cortex/orchestrators/core/master_orchestrator.py` - Add gateway integration
- `cortex/orchestrators/domain_orchestrator.py` - Use domain-transitions spec
- `cortex/orchestrators/domain_brain/planning_orchestrator.py` - Use spec-driven flow
- `cortex/orchestrators/domain_brain/refactoring_orchestrator.py` - Use spec-driven flow
- Multiple test files (26+ tests)

---

## ⚙️ Implementation Strategy

### Phase 4.1: IntentRouter Refactoring (20 hours)
1. **Analysis** (2 hours)
   - Document all hardcoded keyword lists
   - Identify all routing logic
   - Map current behavior to specs

2. **Implementation** (15 hours)
   - Add SpecRegistry integration
   - Refactor detect_intent() to use specs
   - Update _route_internal() for spec-based handlers
   - Replace error messages with GOVE_NNN codes

3. **Testing** (3 hours)
   - Update 26 IntentRouter tests
   - Add spec-based routing tests
   - Verify error codes

### Phase 4.2: MasterOrchestrator Integration (15 hours)
1. **Analysis** (1 hour)
   - Document current stage orchestration
   - Identify gateway integration points

2. **Implementation** (12 hours)
   - Import MasterGatewayExecutor
   - Update execute() to call gateway
   - Update error handling
   - Remove old stage logic

3. **Testing** (2 hours)
   - Update 15+ MasterOrchestrator tests
   - Verify gateway integration
   - Test violation handling

### Phase 4.3: Domain Routing Refactoring (10 hours)
1. **Analysis** (2 hours)
   - Document domain-specific routing
   - Create domain-transitions spec

2. **Implementation** (6 hours)
   - Refactor domain orchestrators
   - Replace if/elif with spec lookups
   - Update error codes

3. **Testing** (2 hours)
   - Update 20+ domain tests
   - Verify spec transitions

### Phase 4.4: Error Code Migration (5 hours)
- Audit all error messages (1 hour)
- Replace with GOVE_NNN codes (3 hours)
- Verify no English text in errors (1 hour)

---

## ✅ Success Criteria

### Code Quality
- [ ] All hardcoded keyword lists removed
- [ ] All elif chains replaced with spec lookups
- [ ] 100% type hints maintained (CORE-011)
- [ ] 100% docstrings maintained (CORE-012)
- [ ] All error messages use GOVE_NNN codes
- [ ] Zero breaking changes

### Testing
- [ ] 50-70 existing tests updated
- [ ] 100% of updated tests passing
- [ ] Zero regression failures
- [ ] New spec-based test coverage

### Integration
- [ ] IntentRouter uses routing-rules-intent.yaml
- [ ] MasterOrchestrator calls MasterGateway
- [ ] Domain orchestrators use domain-transitions
- [ ] All violations structured (GOVE_NNN)

### Backward Compatibility
- [ ] Old code paths still work (fallback)
- [ ] Existing API unchanged
- [ ] No external breaking changes

---

## 🚀 Rollout Plan

### Pre-Refactoring
1. Create feature branch: `feature/AC-PERMANENT-FIX-010-phase-4`
2. Document all hardcoded patterns
3. Create specification for domain transitions
4. Set up test environment

### During Refactoring
1. Implement IntentRouter changes
2. Add comprehensive tests
3. Implement MasterOrchestrator integration
4. Refactor domain routers
5. Migrate error codes

### Post-Refactoring
1. Run full test suite
2. Verify backward compatibility
3. Git checkpoint commit
4. Documentation update
5. Ready for Phase 5

---

## 📈 Expected Impact

### Code Metrics
- **Lines Removed:** ~200 (hardcoded lists, if/elif chains)
- **Lines Added:** ~300 (spec integration, error handling)
- **Net Change:** ~100 lines
- **Files Modified:** 10-15
- **Test Updates:** 50-70 tests

### Quality Metrics
- **Type Safety:** 100% maintained
- **Documentation:** 100% maintained
- **Error Handling:** Improved (structured codes)
- **Maintainability:** Improved (spec-driven)

### Performance
- **Lookup Performance:** Same (SpecRegistry cached)
- **Startup Time:** Slightly faster (specs cached)
- **Runtime:** No change

---

## 🎓 Key Learnings from Phase 3

### Applied to Phase 4
1. ✅ Use FilenameFactory for all new files
2. ✅ Write tests first (CORE-008)
3. ✅ Maintain 100% type hints (CORE-011)
4. ✅ Keep docstrings complete (CORE-012)
5. ✅ Use git checkpoints after major sections
6. ✅ Document all changes thoroughly

### Risk Mitigation
1. **Regression Risk:** Update all existing tests
2. **Backward Compat:** Keep old code paths functional
3. **Integration Risk:** Test MasterOrchestrator + gateway together
4. **Domain Risk:** Validate domain transitions work for all domains

---

## 📋 Checklist

### Before Starting Phase 4
- [ ] Phase 3 tests passing (65/65)
- [ ] Documentation reviewed
- [ ] Team approval obtained
- [ ] Feature branch created

### During Phase 4
- [ ] IntentRouter refactored
- [ ] All IntentRouter tests updated
- [ ] MasterOrchestrator integrated
- [ ] MasterOrchestrator tests updated
- [ ] Domain routers refactored
- [ ] Domain tests updated
- [ ] Error codes migrated
- [ ] Full test suite passes
- [ ] Backward compatibility verified
- [ ] Git checkpoint created

### After Phase 4
- [ ] Documentation updated
- [ ] Phase 4 completion summary created
- [ ] Ready for Phase 5
- [ ] All metrics collected

---

**Authority:** CORTEX Master Orchestrator  
**Mandate:** AC-PERMANENT-FIX-010 Phase 4  
**Status:** Planning Complete, Ready for Implementation  
**Date:** January 26, 2026
