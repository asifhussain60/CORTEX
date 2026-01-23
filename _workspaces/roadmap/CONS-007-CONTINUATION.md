# CONS-007 Onboarding Consolidation - Continuation Prompt

**Date**: 2026-01-24  
**Session**: CONS-007 Phase 1 ✅ COMPLETE  
**Commit**: c5ea72eeb  
**Status**: Ready for Phase 2 Implementation

---

## Current State

✅ **Phase 1 Complete**: Architecture analysis & design  
✅ **Components Identified**: 8 onboarding implementations found  
✅ **Design Created**: `cortex/config/onboarding_unified.py` (interface)  
✅ **Documentation**: CONS-007-SESSION-PROGRESS.md with full implementation plan

---

## What's Done

1. Located all 8 onboarding components:
   - `cortex/orchestrators/onboarding/` (7 modules)
   - `cortex/orchestrators/bootstrap.py` (OrchestratorBootstrap)
   - Supporting: HealthCheck, TelemetryProvider, DependencyValidator

2. Designed UnifiedOnboarding interface with:
   - 17 core methods across all concerns
   - Composition-based pattern (proven from CONS-002-006)
   - Backward compatibility layer planned

3. Updated roadmap with CONS-007 progress

---

## Next Phase: Implementation (Phase 2)

**Estimated Time**: 90 minutes for composition handlers

### Tasks (in order)

1. **Journey Handler** (30 min)
   - Wrap OnboardingOrchestrator
   - Create_journey, start_journey, complete_activity, get_progress

2. **Setup Handler** (20 min)
   - Wrap SetupOrchestrator
   - setup_environment, validate_setup

3. **Bootstrap Handler** (20 min)
   - Wrap OrchestratorBootstrap
   - bootstrap_orchestrators, register_orchestrator

4. **Discovery Handler** (10 min)
   - Wrap ToolDiscovery + DependencyResolver
   - discover_tools, discover_dependencies

5. **Validation Handler** (10 min)
   - Wrap ToolchainValidator + DependencyValidator
   - validate_toolchain, validate_dependencies

### Implementation Pattern (Proven)

From CONS-002-006 success:
```python
def create_journey(self, ...):
    """Create journey (delegated to internal handler)."""
    if not self._journey_handler:
        self._journey_handler = OnboardingOrchestrator()  # Lazy init
    return self._journey_handler.create_journey(...)
```

---

## Testing (Phase 4: 45 min)

Create 25-40 tests covering:
- All 17 methods working correctly
- Backward compatibility verified
- Integration with existing code
- Edge cases and error handling

---

## Success Criteria

✅ **85% Consolidation Value** (target from proven pattern)  
✅ **50% Time Savings** (3h vs 6h estimate)  
✅ **100% Backward Compatible** (zero breaking changes)  
✅ **25-40 Tests, 100% Passing**  
✅ **4-5K Tokens** (within budget)

---

## Key Files

- **Architecture**: `cortex/config/onboarding_unified.py` (stub)
- **Implementation Plan**: `_workspaces/roadmap/CONS-007-SESSION-PROGRESS.md`
- **Quick Reference**: `_workspaces/roadmap/CONS-007-QUICK-START.md`
- **Roadmap Status**: `_workspaces/roadmap/cortex-roadmap.yaml` (updated)

---

## Git Commit Reference

Latest: `c5ea72eeb - AC-CONS-007-PHASE-1: Onboarding consolidation architecture complete`

---

**Continue with**: Phase 2 - Composition Handlers Implementation
**Estimated Continuation Time**: 90 minutes to complete all handlers + tests + git commit
