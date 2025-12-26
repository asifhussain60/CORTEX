# Task 13.5: Dynamic Registry System Implementation Plan

**Phase:** 13 (Post-GA Refinement)  
**Task:** 13.5 - Dynamic Orchestrator/Agent Registration  
**Priority:** HIGH  
**Estimated Effort:** 12 hours (Days 5-6)  
**Author:** CORTEX Phase 13 Planning  
**Created:** December 25, 2025

---

## 🎯 Objective

Implement dynamic orchestrator/agent registration to replace hardcoded imports with a plugin-style discovery system, improving maintainability and extensibility.

---

## 📊 Current State Analysis

### Discovery Audit Results (Completed)

**Hardcoded Import Locations:**
1. **Entry Point:** `src/operations/modules/routing/unified_entry_point_utility.py` (lines 160, 168, 176)
   - CodeReviewOrchestrator
   - ADOWorkItemOrchestrator
   - PlanningOrchestrator

2. **Orchestrator Cross-References:** 31 matches across `src/orchestrators/**/*.py`
   - Base orchestrator imports (internal dependencies - OK)
   - Cross-orchestrator calls (needs registry)

3. **Operations Modules:** 50+ matches in `src/operations/**/*.py`
   - Dynamic imports scattered throughout
   - Inconsistent error handling
   - No centralized registry

### Failing Tests to Fix (22 tests)

**Group 1: TDD Workflow Integration (13 tests)**
- `test_red_green_refactor_phases_in_plan` - FAILED
- `test_tdd_mandatory_for_high_complexity` - FAILED
- `test_test_first_enforcement_in_dor` - FAILED
- `test_test_coverage_in_dod` - FAILED
- `test_tdd_intelligence_layer_integration` - FAILED
- `test_test_quality_validation_enabled` - FAILED
- `test_tdd_checkpoint_after_each_cycle` - FAILED
- `test_tdd_metrics_collected` - FAILED
- 5 more TDD-related tests

**Group 2: DoR/DoD Validation (9 tests)**
- `test_dor_validation_before_phase_execution` - FAILED
- `test_dor_missing_criteria_fails` - FAILED
- `test_dod_validation_after_phase_execution` - FAILED
- `test_dod_incomplete_criteria_fails` - FAILED
- `test_dor_dod_logged_at_phase_boundaries` - FAILED
- `test_dor_blocks_phase_execution_if_fails` - FAILED
- `test_failed_dod_triggers_rollback` - FAILED
- `test_dor_dod_criteria_loaded_from_manifest` - FAILED
- `test_custom_dor_dod_can_override_defaults` - FAILED

---

## 🏗️ Implementation Phases

### Phase 1: Core Registry Implementation (4 hours)

**Deliverable:** `src/core/orchestrator_registry.py` + tests

**Components:**

1. **OrchestratorRegistry Class**
   ```python
   class OrchestratorRegistry:
       """Central registry for all orchestrators with dynamic discovery."""
       
       def __init__(self):
           self._orchestrators: Dict[str, Type[BaseOrchestrator]] = {}
           self._instances: Dict[str, BaseOrchestrator] = {}
       
       def register(self, name: str, orchestrator_class: Type[BaseOrchestrator]):
           """Register an orchestrator class."""
       
       def get(self, name: str) -> Optional[BaseOrchestrator]:
           """Get orchestrator instance (lazy initialization)."""
       
       def discover(self, search_paths: List[Path]) -> int:
           """Auto-discover orchestrators in given paths."""
       
       def is_available(self, name: str) -> bool:
           """Check if orchestrator is available."""
   ```

2. **Auto-Discovery System**
   - Scan `src/orchestrators/` for classes inheriting from `BaseOrchestrator`
   - Extract metadata from docstrings (name, version, capabilities)
   - Handle import errors gracefully (optional dependencies)

3. **Plugin Interface**
   ```python
   @orchestrator_plugin("planning", version="4.0.0")
   class PlanningOrchestrator(BaseOrchestrator):
       """Planning System orchestrator."""
       pass
   ```

4. **Tests** (18 tests)
   - Registry initialization
   - Manual registration
   - Auto-discovery
   - Lazy loading
   - Error handling (missing orchestrators)
   - Thread safety

### Phase 2: TDD Workflow Integration (4 hours)

**Objective:** Fix 13 failing TDD integration tests

**Implementation:**

1. **TDD Manifest Integration** (`src/orchestrators/planning/tdd_integration.py`)
   ```python
   class TDDWorkflowIntegrator:
       """Integrates TDD workflow into planning system."""
       
       def inject_tdd_phases(self, plan: Dict) -> Dict:
           """Add RED→GREEN→REFACTOR phases to plan."""
       
       def enforce_test_first(self, phase: Dict) -> bool:
           """Validate test-first enforcement in DoR."""
       
       def validate_test_coverage(self, phase: Dict) -> bool:
           """Validate test coverage in DoD."""
   ```

2. **Complexity-Based TDD Requirements**
   - HIGH complexity: Mandatory TDD (all phases)
   - MEDIUM complexity: Conditional TDD (key phases)
   - LOW complexity: Optional TDD (skeleton only)

3. **DoR Integration**
   - Add "Tests written (RED phase)" to DoR criteria
   - Validate test files exist before implementation
   - Block phase execution if tests missing

4. **DoD Integration**
   - Add "Tests passing (GREEN phase)" to DoD criteria
   - Validate test coverage meets threshold
   - Trigger rollback if tests fail

5. **Tests** (13 tests)
   - All TDD workflow integration tests passing
   - Test coverage validation
   - Checkpoint integration
   - Metrics collection

### Phase 3: DoR/DoD Validation System (3 hours)

**Objective:** Fix 9 failing DoR/DoD validation tests

**Implementation:**

1. **Manifest Loader** (`src/orchestrators/planning/manifest_loader.py`)
   ```python
   class ManifestLoader:
       """Load DoR/DoD criteria from manifest files."""
       
       def load_manifest(self, plan_type: str) -> Dict:
           """Load manifest for given plan type."""
       
       def get_dor_criteria(self) -> List[str]:
           """Get Definition of Ready criteria."""
       
       def get_dod_criteria(self) -> List[str]:
           """Get Definition of Done criteria."""
   ```

2. **DoR/DoD Validator** (`src/orchestrators/planning/dor_dod_validator.py`)
   ```python
   class DoRDoDValidator:
       """Validate DoR before phase, DoD after phase."""
       
       def validate_dor(self, phase: Dict, context: Dict) -> ValidationResult:
           """Validate Definition of Ready."""
       
       def validate_dod(self, phase: Dict, context: Dict) -> ValidationResult:
           """Validate Definition of Done."""
       
       def log_validation(self, result: ValidationResult):
           """Log validation results at phase boundaries."""
   ```

3. **Rollback Integration**
   - Trigger git checkpoint before phase execution
   - Rollback to checkpoint if DoD fails
   - Log rollback reason

4. **Tests** (9 tests)
   - All DoR/DoD validation tests passing
   - Manifest loading
   - Custom criteria overrides
   - Rollback on DoD failure

### Phase 4: Entry Point Integration (1 hour)

**Objective:** Replace hardcoded imports in unified_entry_point_utility.py

**Implementation:**

1. **Update `initialize_orchestrators()`**
   ```python
   def initialize_orchestrators(cortex_root: Path) -> OrchestratorRegistry:
       """Initialize orchestrators using dynamic registry."""
       registry = OrchestratorRegistry()
       
       # Auto-discover all orchestrators
       discovered = registry.discover([
           cortex_root / "src" / "orchestrators",
           cortex_root / "src" / "operations" / "modules"
       ])
       
       logger.info(f"✅ Discovered {discovered} orchestrators")
       return registry
   ```

2. **Update Routing Functions**
   - Replace `from src.orchestrators.X import Y` with `registry.get("Y")`
   - Add fallback handling for missing orchestrators
   - Maintain backward compatibility

3. **Tests** (5 tests)
   - Registry initialization
   - Orchestrator discovery
   - Routing with registry
   - Error handling

---

## 📊 Success Metrics

**Test Pass Rate:**
- **Before:** 2,944/2,977 (98.9%)
- **Target:** 2,966+/2,977 (99.6%+)
- **Improvement:** +22 tests fixed

**Code Quality:**
- Zero hardcoded orchestrator imports in entry point
- Consistent error handling across all dynamic loads
- Comprehensive test coverage for registry system

**Maintainability:**
- Plugin-style registration for new orchestrators
- Auto-discovery reduces maintenance overhead
- Centralized orchestrator management

---

## 🔄 TDD Workflow

**Phase 1: RED (2h)**
- Write 45 failing tests (18 registry + 13 TDD + 9 DoR/DoD + 5 integration)
- All tests fail as expected
- Test coverage plan documented

**Phase 2: GREEN (6h)**
- Implement registry system (4h)
- Implement TDD integration (4h)
- Implement DoR/DoD validation (3h)
- Update entry point (1h)
- All 45 tests passing

**Phase 3: REFACTOR (4h)**
- Optimize registry performance
- Improve error messages
- Add comprehensive logging
- Update documentation

---

## 📝 Deliverables

1. **Code:**
   - `src/core/orchestrator_registry.py` (300 LOC)
   - `src/orchestrators/planning/tdd_integration.py` (250 LOC)
   - `src/orchestrators/planning/dor_dod_validator.py` (200 LOC)
   - `src/orchestrators/planning/manifest_loader.py` (150 LOC)

2. **Tests:**
   - `tests/core/test_orchestrator_registry.py` (18 tests)
   - `tests/orchestrators/planning/test_tdd_integration.py` (13 tests)
   - `tests/orchestrators/planning/test_dor_dod_validator.py` (9 tests)
   - `tests/operations/test_routing_with_registry.py` (5 tests)

3. **Documentation:**
   - Task 13.5 completion report
   - Registry API documentation
   - Migration guide for custom orchestrators

---

## 🚀 Execution Timeline

| Phase | Duration | Deliverables | Tests |
|-------|----------|--------------|-------|
| 1. Core Registry | 4h | Registry + auto-discovery | 18 |
| 2. TDD Integration | 4h | TDD workflow integration | 13 |
| 3. DoR/DoD Validation | 3h | Validation system | 9 |
| 4. Entry Point | 1h | Routing updates | 5 |
| **Total** | **12h** | **4 modules + tests** | **45** |

**Days:** 5-6 (2 days @ 6 hours/day)

---

## 🔍 Next Steps

**Immediate:**
1. Create RED phase tests (45 tests, all failing)
2. Implement `OrchestratorRegistry` core class
3. Add auto-discovery system

**Post-Completion:**
- Task 13.6: Registry consolidation
- Task 13.7: MEDIUM-priority documentation
- Update CORTEX4-STATUS.md with Task 13.5 completion

---

**Status:** ⏳ READY - Awaiting approval to start RED phase
