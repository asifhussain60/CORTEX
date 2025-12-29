# Planning System Migration Discovery Analysis
**Date:** December 19, 2025  
**Author:** CORTEX Analysis Engine  
**Status:** Discovery Phase Complete

---

## 📊 Executive Summary

**Critical Finding:** The Planning System migration scope is **3.5× larger** than initially estimated in MASTER-PLAN.md.

| Metric | Initial Estimate | Actual Reality | Variance |
|--------|------------------|----------------|----------|
| **Total LOC** | 1,599 | 5,557 | +248% |
| **Methods** | ~40 (est) | 93 | +132% |
| **Classes** | 1 | 3 | +200% |
| **Dependencies** | ~10 (est) | 29 imports | +190% |
| **Test Files** | 4 (planned) | 36 (exist) | +800% |

---

## 🔍 Deep Architecture Analysis

### Core Components Identified

**1. Planning Orchestrator Core (3,200 LOC)**
- Plan validation (YAML schema)
- Plan generation (incremental + full)
- Plan execution (autonomous + supervised)
- Markdown rendering
- Session management
- Progress tracking

**2. Integration Layer (1,400 LOC)**
- Git checkpoint integration
- TDD workflow enforcement
- Threat modeling (ThreatModelerAgent)
- Test intelligence (TestIntelligence)
- Document organization (DocumentOrganizer)
- Response templates (ResponseTemplateManager)

**3. Advanced Features (900 LOC)**
- Contextual architecture review (ReviewOrchestrator)
- Task injection (TaskInjectionManager)
- Workflow recovery (OrchestrationCheckpointManager)
- Observer pattern (event subscription)
- Plan execution v2 (PlanExecutionOrchestratorV2)
- Folder management (PlanFolderManager)
- Incremental generation (IncrementalPlanGenerator)
- Streaming writer (CheckpointedPlanWriter)

**4. Validation & Compliance (1,057 LOC)**
- YAML schema validation
- Manifest compliance (ManifestValidator)
- DoR/DoD validation (ValidationFramework)
- User profile integration (UserProfileManager)
- TDD intelligence (TDDIntelligence)

---

## 🎯 Critical Dependencies

### External System Dependencies (26 total)

**Must Migrate:**
1. ✅ `SessionFactory` - Already exists
2. ✅ `PlanningSession` - Already exists
3. ✅ `PhaseManager` - Already exists in base
4. ✅ `ValidationResult` - Already exists in base
5. ❌ `ValidationFramework` - Needs migration
6. ❌ `TestIntelligence` - Needs migration
7. ❌ `TDDIntelligence` - Needs migration

**Can Defer (Optional Features):**
8. `ThreatModelerAgent` - Security analysis (nice-to-have)
9. `ReviewOrchestrator` - Architecture review (optional)
10. `TaskInjectionManager` - Mid-execution changes (advanced)
11. `OrchestrationCheckpointManager` - Recovery (advanced)
12. `PlanExecutionOrchestratorV2` - Auto-execution (can use v1)
13. `IncrementalPlanGenerator` - Token optimization (optional)
14. `CheckpointedPlanWriter` - Streaming (optional)
15. `PlanFolderManager` - Folder structure (optional)
16. `DocumentOrganizer` - Auto-organization (optional)

**Already Available:**
17. ✅ `GitCheckpointOrchestrator` - Already exists
18. ✅ `ResponseTemplateManager` - Already exists
19. ✅ `ManifestValidator` - Already exists
20. ✅ `UserProfileManager` - Already exists
21. ✅ `ProgressRenderer` - Already exists

---

## 🚨 Edge Cases Identified

### 1. **Session State Management**
**Issue:** Planning uses `PlanningSession` for multi-conversation context  
**Risk:** Sessions may be lost if not properly migrated  
**Mitigation:** Include session restoration in DoR/DoD

### 2. **Git Checkpoint Integration**
**Issue:** Planning creates checkpoints at key boundaries (approve, execute, complete)  
**Risk:** Breaking SKULL rule #22 (GIT_CHECKPOINT_ENFORCEMENT)  
**Mitigation:** Wire `GitCheckpointOrchestrator` early in migration

### 3. **Observer Pattern Subscribers**
**Issue:** Legacy code has `self.observers = []` for event subscription  
**Risk:** External systems may listen for planning events  
**Mitigation:** Document event API, maintain backward compatibility

### 4. **Manifest Compliance Validation**
**Issue:** Planning validates itself against `planning-system-4.0-manifest.yaml` on init  
**Risk:** Drift detection may fail if manifest out of sync  
**Mitigation:** Update manifest FIRST before migrating code

### 5. **Test Intelligence Integration**
**Issue:** Planning auto-detects test requirements using `TestIntelligence`  
**Risk:** Test generation may fail without this module  
**Mitigation:** Migrate `TestIntelligence` in same PR as Planning

### 6. **TDD Workflow Enforcement**
**Issue:** Planning enforces RED→GREEN→REFACTOR via `TDDIntelligence`  
**Risk:** Breaking SKULL rule #1 (TDD_ENFORCEMENT)  
**Mitigation:** Include TDD validation in migration

### 7. **Folder Structure Support**
**Issue:** Planning supports both file-based and folder-based plans  
**Risk:** Folder-based plans may break if not handled  
**Mitigation:** Test both modes explicitly

### 8. **Incremental Generation**
**Issue:** Planning can generate plans section-by-section with checkpoints  
**Risk:** Token limits may cause failures without incremental mode  
**Mitigation:** Keep incremental generation or document removal

### 9. **Template Integration**
**Issue:** Planning reads flags from `response-templates.yaml` for session restoration  
**Risk:** Config changes may break planning behavior  
**Mitigation:** Document template dependencies

### 10. **Threat Modeling**
**Issue:** Planning optionally runs security threat analysis before execution  
**Risk:** Security features silently disabled if `ThreatModelerAgent` missing  
**Mitigation:** Make threat modeling explicitly optional with warning logs

---

## 📋 Phased Migration Strategy (Revised)

### Phase 1: Core Planning (Week 8 Days 1-3) - MVP
**Scope:** 1,800 LOC  
**Deliverables:**
- `planning_orchestrator.py` (800 LOC) - Main orchestrator
- `plan_validator.py` (300 LOC) - YAML schema validation
- `plan_generator.py` (400 LOC) - Plan creation
- `markdown_renderer.py` (300 LOC) - Markdown export

**Tests:** 20 core tests (create, validate, render, load, save)

### Phase 2: Execution Engine (Week 8 Days 4-5)
**Scope:** 1,200 LOC  
**Deliverables:**
- `plan_executor.py` (500 LOC) - Autonomous execution
- `phase_manager_integration.py` (300 LOC) - Wire PhaseManager
- `git_checkpoint_integration.py` (200 LOC) - Checkpoint wiring
- `session_manager.py` (200 LOC) - Session restoration

**Tests:** 15 execution tests (phases, checkpoints, sessions)

### Phase 3: Intelligence Integrations (Week 9 Days 1-3)
**Scope:** 1,400 LOC  
**Deliverables:**
- `test_intelligence_adapter.py` (400 LOC) - TestIntelligence wiring
- `tdd_intelligence_adapter.py` (300 LOC) - TDDIntelligence wiring
- `validation_framework_adapter.py` (400 LOC) - ValidationFramework wiring
- `manifest_compliance.py` (300 LOC) - Compliance validation

**Tests:** 25 integration tests (intelligence modules)

### Phase 4: Advanced Features (Week 9 Days 4-5) - OPTIONAL
**Scope:** 1,157 LOC (DEFERRED to post-Phase 5)  
**Reason:** These features require Phase 2.5 Agentic AI enhancements  
**Deliverables (Deferred):**
- Threat modeling integration
- Contextual architecture review
- Task injection
- Orchestration checkpoints
- Incremental generation
- Folder-based plans

---

## 📊 Test Migration Plan

**36 existing test files** need triage:

**Keep & Migrate (15 files):**
- `test_planning_orchestrator.py` - Core orchestrator
- `test_planning_system_e2e.py` - End-to-end
- `test_planning_integration.py` - Integration suite
- `test_pre_planning_discovery.py` - Discovery phase
- `test_planning_status_transitions.py` - Lifecycle
- `test_planning_git_checkpoint_integration.py` - Git wiring
- `test_planning_tdd_e2e.py` - TDD workflow
- `test_planning_production_validation.py` - Validation
- + 7 more critical tests

**Archive (10 files):**
- Legacy v3.0 tests
- Deprecated feature tests
- Duplicate test files

**Consolidate (11 files):**
- Merge similar test suites
- Remove redundant tests

---

## 🎯 Updated Scope Estimates

### Week 8: Core Planning System Migration
**Days 1-2:** Discovery + Core MVP (1,800 LOC)  
**Day 3:** Execution Engine (1,200 LOC)  
**Day 4:** Integration & Validation  
**Day 5:** Documentation + Commit + Push

**Total:** 3,000 LOC (54% of total)  
**Coverage Target:** 85%+  
**Tests:** 35+ (consolidated from 36 existing)

### Week 9: Intelligence Integrations + Completion
**Days 1-2:** Intelligence Adapters (1,400 LOC)  
**Days 3-4:** Full Integration Testing  
**Day 5:** Final Documentation + Release

**Total:** 1,400 LOC (25% of total)  
**Coverage Target:** 85%+  
**Tests:** 50+ (full suite)

### Post-Phase 5: Advanced Features (Week 11)
**Scope:** 1,157 LOC (21% of total - deferred)  
**Reason:** Requires agentic AI enhancements from Phase 2.5

---

## ✅ Recommendations

1. **Update MASTER-PLAN Week 8:**
   - Change "1,599 LOC" → "3,000 LOC (Core MVP)"
   - Split into 2 weeks: Week 8 (Core) + Week 9 (Intelligence)
   - Defer advanced features to Week 11 (post-Phase 5)

2. **Update Module Split:**
   - Week 8: 4 modules → 3,000 LOC (not 1,599)
   - Week 9: 4 adapters → 1,400 LOC (new)
   - Week 11: 8 advanced features → 1,157 LOC (deferred)

3. **Test Strategy:**
   - Consolidate 36 tests → 35 core + 15 integration = 50 total
   - Archive 10 obsolete tests
   - Achieve 85%+ coverage

4. **Git Strategy:**
   - Commit after Week 8 (Core MVP)
   - Commit after Week 9 (Intelligence Integrations)
   - Final commit after Week 11 (Advanced Features)

---

## 🚦 Ready to Proceed

**Discovery Phase:** ✅ COMPLETE  
**Edge Cases:** ✅ IDENTIFIED (10 documented)  
**Migration Strategy:** ✅ REVISED (3 phases)  
**MASTER-PLAN Update:** ⏳ READY TO APPLY

**Next Step:** Update MASTER-PLAN.md with revised scope and phasing.
