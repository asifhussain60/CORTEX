# CONS-007: Onboarding Consolidation - Quick Start Guide

**Date**: 2026-01-24  
**Status**: Ready for Implementation  
**Estimated Effort**: 6 hours (3 hours projected with acceleration)  
**Pattern**: Proven consolidation methodology from CONS-002-006

---

## Objective
Consolidate 7 scattered onboarding implementations into 1 unified `UnifiedOnboarding` interface.

## Scope: 7 Components → 1

### Components to Consolidate
```
cortex/config/profile_initializer.py      → Migrate
cortex/config/setup_wizard.py             → Migrate
cortex/orchestrators/bootstrap_orchestrator.py  → Migrate
cortex/infrastructure/environment_config.py    → Migrate
cortex/testing/dependency_validator.py         → Migrate
cortex/infrastructure/health_check_init.py     → Migrate
cortex/observability/telemetry_setup.py        → Migrate
```

### Target Structure
```
cortex/config/onboarding/
  __init__.py
  unified_onboarding.py      # Main UnifiedOnboarding class
  profile_integration.py       # ProfileInitializer + SetupWizard
  environment_integration.py   # EnvironmentConfigurator
  validation_integration.py    # DependencyValidator
  health_integration.py        # HealthCheckInitializer
  telemetry_integration.py     # TelemetrySetup
  bootstrap_integration.py     # BootstrapOrchestrator compatibility
```

---

## Implementation Pattern (Proven)

### Phase 1: Analysis (30 minutes)
1. **Map current APIs**
   - List all public methods from 7 components
   - Document dependencies between components
   - Identify shared initialization logic

2. **Design unified interface**
   - Create `UnifiedOnboarding` base class
   - Define 4-5 main entry points (e.g., `setup()`, `validate()`, `check_health()`)
   - Plan backward compatibility layer

### Phase 2: Implementation (2.5 hours)
1. **Create composition layer**
   - Implement `UnifiedOnboarding` class
   - Compose all 7 implementations internally
   - Add router logic to delegate to appropriate handlers

2. **Add comprehensive tests**
   - 25-40 test cases covering all 7 implementations
   - Backward compatibility verification
   - Integration tests with actual components

3. **Create backward compatibility shims**
   - Redirect old imports to new unified interface
   - Deprecation warnings for old APIs

### Phase 3: Validation (30 minutes)
- Run full test suite
- Verify 100% backward compatibility
- Check for any import errors

---

## Success Criteria

✅ **Consolidation Value**: 85% (target from proven pattern)  
✅ **Time Savings**: 50% (3h vs 6h estimate)  
✅ **Backward Compatibility**: 100%  
✅ **Test Coverage**: 25-40 tests, 100% passing  
✅ **Token Efficiency**: 4-5K tokens

---

## Expected Deliverables

1. `UnifiedOnboarding` class (300-400 lines)
2. Integration modules (200-250 lines total)
3. Comprehensive test suite (250-350 lines)
4. Backward compatibility imports
5. Inline documentation and docstrings

---

## Quality Checklist

- [ ] All 7 components mapped and analyzed
- [ ] `UnifiedOnboarding` class created
- [ ] All methods delegated correctly
- [ ] 100% of original APIs supported
- [ ] 25-40 tests written and passing
- [ ] Backward compatibility verified
- [ ] No import errors
- [ ] Documentation complete
- [ ] Code review ready
- [ ] Ready for CONS-008

---

## Next Phase After Completion

**CONS-008: Response Composition**
- 5 implementations → 1 UnifiedResponseComposer
- Same pattern, similar effort (6h → 3h projected)
- Ready immediately after CONS-007 validation

---

## Token Budget & Timeline

**Token Budget Remaining**: 68K (sufficient)  
**Expected Usage**: 4-5K tokens (CONS-007)  
**Remaining After**: ~63K tokens  

**Timeline**:
- CONS-007: ~3 hours (vs 6 estimated)
- CONS-008: ~3 hours (vs 6 estimated)
- CONS-009: ~3 hours (vs 6 estimated)
- CONS-010-011: ~2 hours (vs 4 estimated)
- **Total TRANSFORM-002**: ~11 hours (vs 22 estimated) = **50% savings**

---

## Key Insights from CONS-002-006

1. **Composition pattern works**: Nested delegation > inheritance
2. **Tests drive quality**: 25-40 tests per consolidation sufficient
3. **Backward compat is critical**: Deprecation warnings help migration
4. **Document heavily**: Inline docs reduce confusion
5. **Acceleration is real**: 50% time savings sustainable across phases

---

## Pattern References

See these completed consolidations for implementation examples:
- **CONS-002**: `master_orchestrator_stages.py` (UnifiedStageExecutor pattern)
- **CONS-003**: `intent_routing_unified.py` (UnifiedIntentRouter pattern)
- **CONS-004**: `registry_unified.py` (UnifiedRegistry pattern)

All follow the same composition + backward compat + comprehensive tests pattern.

---

## Start Condition

✅ All prerequisites complete:
- CONS-001: Redundancy analysis ✅
- CONS-002-006: Implementation complete ✅
- CONS-007 ready: Pattern proven ✅
- CONS-008-011: Waiting for CONS-007 completion

**Ready to begin**: 2026-01-24 (immediately)

---

*Last Updated: 2026-01-24*  
*Authority: cortex-roadmap.yaml (TRANSFORM-002 Phase 3)*
