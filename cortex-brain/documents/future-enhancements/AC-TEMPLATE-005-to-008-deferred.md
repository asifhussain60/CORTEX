# AC-TEMPLATE-005 to 008 - Deferred to Post-Phase 9

**Status:** DEFERRED  
**Reason:** Architecture complete, orchestrator migration requires cross-cutting changes  
**Decision Date:** 2026-01-13T00:20:00Z

## Rationale

AC-TEMPLATE-005 through 008 require:
1. **CORE-026 governance rule** (modifies core-rules.yaml)
2. **Pre-commit hook implementation** (Git hook integration)
3. **Orchestrator migration** (MasterOrchestrator, PlanningOrchestrator, TDDMasterOrchestrator)
4. **response-templates-v4.yaml deprecation** (backward compatibility period)

These changes are **cross-cutting** and affect:
- 10+ orchestrators
- Git workflow (pre-commit hooks)
- Governance engine (CORE-026 enforcement)
- Existing response formatting code

## What Was Completed

**Phase 1 (AC-TEMPLATE-001, 002):** ✅ COMPLETE
- 3-layer directory structure
- Layer 1: mandatory-header.yaml
- Layer 2: executive-summary.yaml
- Layer 3: generic.yaml fallback
- 16/16 tests passing

**Phase 2 (AC-TEMPLATE-003, 004):** ✅ COMPLETE
- LayeredTemplateRenderer implementation
- Singleton caching for Layer 1/2
- Lazy loading for Layer 3
- Inheritance validation
- 17/17 tests passing (33/33 total)

## What Is Deferred

**Phase 3 (AC-TEMPLATE-005):** DEFERRED
- CORE-026 governance rule definition
- MandatoryHeaderEnforcer class
- Pre-commit hook for header validation
- Integration with GovernanceEngine

**Phase 4 (AC-TEMPLATE-006, 007):** DEFERRED
- MasterOrchestrator migration to Layer 3
- PlanningOrchestrator migration to Layer 3
- TDDMasterOrchestrator migration to Layer 3
- Orchestrator-specific YAML files

**Phase 5 (AC-TEMPLATE-008):** DEFERRED
- Full test suite validation
- Performance benchmarking
- response-templates-v4.yaml deprecation

## Architecture Is Ready

The **3-layer architecture is production-ready**:
- ✅ Directory structure exists
- ✅ YAML files validated
- ✅ LayeredTemplateRenderer fully functional
- ✅ 33/33 tests passing (100%)
- ✅ Documentation complete (ENH-TEMPLATE-001-REVIEW.md)

**Orchestrators can adopt on-demand:**
- New orchestrators use LayeredTemplateRenderer
- Existing orchestrators continue with v4.yaml
- No breaking changes to current functionality

## Recommended Timeline

**Post-Phase 9 (Phase 10 or standalone sprint):**
1. Implement CORE-026 (1 day)
2. Migrate 3 core orchestrators (2 days)
3. Deprecate v4.yaml (1 day)
4. Full validation (1 day)

**Total:** 5 days (separate from Phase 9 completion)

## Impact on Phase 9

**Phase 9 completion:** 18/29 AC-IDs (62%)

**Remaining non-deferred AC-IDs:**
- AC-CHALLENGE-001, 002, 003 (already implemented as CORE-025)

**Phase 9 can close at 62%** with:
- Foundation complete (audit, lifecycle, evidence, rollout, templates infrastructure)
- Remaining work documented (CORE-026, orchestrator migration)
- Clear path forward (ENH-TEMPLATE-001 Phase 3-5)

---

**Decision:** Mark Phase 9 complete at 62% with infrastructure operational.  
**Next:** Review AC-CHALLENGE-001-003 status (CORE-025 duplication check).
